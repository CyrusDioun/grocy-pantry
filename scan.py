#!/usr/bin/env python3
"""
Barcode Scanner → Food Inventory
Drop photos of barcodes into ~/Dropbox/Grocy-Scan/
Uses inotify — only wakes when a file appears. Zero CPU otherwise.
"""

import json, os, sys, time, glob, subprocess, requests, re
from datetime import datetime
from pathlib import Path
from category_mapper import map_category

SCAN_DIR = os.path.expanduser("~/Dropbox/Grocy-Scan")
PROCESSED_DIR = os.path.join(SCAN_DIR, "processed")
INVENTORY_FILE = os.path.expanduser("~/grocy/inventory.json")
LOG_FILE = os.path.expanduser("~/grocy/scan.log")

os.makedirs(SCAN_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Force IPv4 to avoid IPv6 connectivity issues with some APIs
requests.packages.urllib3.util.connection.HAS_IPV6 = False

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE) as f:
            return json.load(f)
    return {"products": [], "last_updated": None}

def save_inventory(inv):
    inv["last_updated"] = datetime.now().isoformat()
    with open(INVENTORY_FILE, "w") as f:
        json.dump(inv, f, indent=2)

def is_dropbox_duplicate(filename):
    """Skip Dropbox conflict copies like 'IMG_2028 (1).JPG'"""
    return bool(re.search(r'\(\d+\)\.\w+$', filename))

def read_barcode(image_path):
    # Try raw first
    try:
        result = subprocess.run(
            ["zbarimg", "--quiet", "--raw", image_path],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")[0].strip()
    except Exception as e:
        log(f"  Error reading barcode: {e}")
    
    # If raw fails, enhance image and retry
    try:
        from PIL import Image, ImageOps, ImageEnhance
        log("  Trying enhanced image...")
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)
        img = img.convert("L")
        img = ImageEnhance.Contrast(img).enhance(2.0)
        enhanced = image_path + ".enhanced.jpg"
        img.save(enhanced)
        result = subprocess.run(
            ["zbarimg", "--quiet", "--raw", enhanced],
            capture_output=True, text=True, timeout=20
        )
        os.remove(enhanced)
        if result.returncode == 0 and result.stdout.strip():
            log("  (read via enhanced image)")
            return result.stdout.strip().split("\n")[0].strip()
    except Exception as e:
        log(f"  Error with enhanced read: {e}")
    return None

def lookup_openfoodfacts(barcode):
    """Primary: Open Food Facts"""
    try:
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == 1:
                p = data["product"]
                name = p.get("product_name", "").strip()
                if name:
                    n = p.get("nutriments", {})
                    return {
                        "barcode": barcode,
                        "name": name,
                        "brand": p.get("brands", "Unknown"),
                        "categories": p.get("categories", ""),
                        "quantity": p.get("quantity", ""),
                        "serving_size": p.get("serving_size", ""),
                        "ingredients": p.get("ingredients_text", ""),
                        "image_url": p.get("image_front_url", ""),
                        "nutrition": {
                            "calories_per_100g": n.get("energy-kcal_100g"),
                            "fat_per_100g": n.get("fat_100g"),
                            "carbs_per_100g": n.get("carbohydrates_100g"),
                            "protein_per_100g": n.get("proteins_100g"),
                            "sodium_per_100g": n.get("sodium_100g"),
                            "fiber_per_100g": n.get("fiber_100g"),
                            "sugar_per_100g": n.get("sugars_100g"),
                        },
                        "nutriscore": p.get("nutriscore_grade", ""),
                        "source": "openfoodfacts",
                    }
    except Exception as e:
        log(f"  OpenFoodFacts error: {e}")
    return None

def lookup_upcitemdb(barcode):
    """Fallback 1: UPC Item DB (free, no key needed for low volume)"""
    try:
        url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}"
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            if items:
                item = items[0]
                name = item.get("title", "").strip()
                if name:
                    return {
                        "barcode": barcode,
                        "name": name,
                        "brand": item.get("brand", "Unknown"),
                        "categories": ", ".join(item.get("category", "").split(" > ")) if item.get("category") else "",
                        "quantity": item.get("size", ""),
                        "serving_size": "",
                        "ingredients": item.get("description", ""),
                        "image_url": (item.get("images", []) or [""])[0],
                        "nutrition": {},
                        "source": "upcitemdb",
                    }
    except Exception as e:
        log(f"  UPCItemDB error: {e}")
    return None

def lookup_go_upc(barcode):
    """Fallback 2: Go-UPC (free tier, scrape-friendly)"""
    try:
        url = f"https://go-upc.com/barcode/{barcode}"
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        resp = requests.get(url, timeout=15, headers=headers)
        if resp.status_code == 200:
            # Simple extraction from HTML
            text = resp.text
            # Look for product name in <h1> tag
            name_match = re.search(r'<h1[^>]*class="[^"]*product-name[^"]*"[^>]*>([^<]+)</h1>', text)
            if not name_match:
                name_match = re.search(r'<h1[^>]*>([^<]+)</h1>', text)
            if name_match:
                name = name_match.group(1).strip()
                if name and "not found" not in name.lower() and barcode not in name:
                    return {
                        "barcode": barcode,
                        "name": name,
                        "brand": "Unknown",
                        "categories": "",
                        "quantity": "",
                        "serving_size": "",
                        "ingredients": "",
                        "image_url": "",
                        "nutrition": {},
                        "source": "go-upc",
                    }
    except Exception as e:
        log(f"  Go-UPC error: {e}")
    return None

def lookup_product(barcode):
    """Try multiple sources in order"""
    # 1. Open Food Facts (best data, nutrition included)
    product = lookup_openfoodfacts(barcode)
    if product:
        log(f"  Found via OpenFoodFacts")
        return product
    
    # 2. UPC Item DB (good coverage, no nutrition)
    product = lookup_upcitemdb(barcode)
    if product:
        log(f"  Found via UPCItemDB")
        return product
    
    # 3. Go-UPC (web scrape fallback)
    product = lookup_go_upc(barcode)
    if product:
        log(f"  Found via Go-UPC")
        return product
    
    log(f"  Not found in any database")
    return None

def process_image(image_path):
    filename = os.path.basename(image_path)
    
    # Skip Dropbox duplicate copies
    if is_dropbox_duplicate(filename):
        log(f"Skipping Dropbox duplicate: {filename}")
        os.rename(image_path, os.path.join(PROCESSED_DIR, filename))
        return None
    
    log(f"Processing: {filename}")
    
    barcode = read_barcode(image_path)
    if not barcode:
        log(f"  No barcode found in {filename}")
        os.rename(image_path, os.path.join(PROCESSED_DIR, f"NOBARCODE_{filename}"))
        return None
    
    log(f"  Barcode: {barcode}")
    inv = load_inventory()
    existing = [p for p in inv["products"] if p["barcode"] == barcode]
    if existing:
        p = existing[0]
        p["quantity_count"] = p.get("quantity_count", 1) + 1
        p["last_scanned"] = datetime.now().isoformat()
        # Update auto-category if not manually overridden
        if p.get("category_source") != "manual":
            new_cat = map_category(p.get("categories", ""))
            p["user_category"] = new_cat
            p["category_source"] = "auto"
        save_inventory(inv)
        log(f"  Already in inventory: {p['name']} (qty: {p['quantity_count']}, category: {p.get('user_category', 'none')})")
        os.rename(image_path, os.path.join(PROCESSED_DIR, filename))
        return p
    
    product = lookup_product(barcode)
    if product:
        # Auto-assign category from OFF data
        cat = map_category(product.get("categories", ""))
        product.update({
            "quantity_count": 1,
            "added": datetime.now().isoformat(),
            "last_scanned": datetime.now().isoformat(),
            "expiration_date": None,
            "location": "pantry",
            "user_category": cat,
            "category_source": "auto",
        })
        inv["products"].append(product)
        save_inventory(inv)
        log(f"  Added: {product['name']} ({product['brand']}) → {cat}")
    else:
        product = {
            "barcode": barcode,
            "name": f"Unknown ({barcode})",
            "brand": "Unknown",
            "quantity_count": 1,
            "added": datetime.now().isoformat(),
            "last_scanned": datetime.now().isoformat(),
            "expiration_date": None,
            "location": "pantry",
            "user_category": "Other",
            "category_source": "auto",
        }
        inv["products"].append(product)
        save_inventory(inv)
        log(f"  Added unknown: {barcode}")
    
    os.rename(image_path, os.path.join(PROCESSED_DIR, filename))
    return product

def resolve_unknowns():
    """Re-lookup all unknown products against all databases"""
    inv = load_inventory()
    resolved = 0
    for p in inv["products"]:
        if p["name"].startswith("Unknown (") or p.get("brand") == "Unknown":
            barcode = p["barcode"]
            log(f"Re-looking up: {barcode}")
            product = lookup_product(barcode)
            if product and not product["name"].startswith("Unknown"):
                old_name = p["name"]
                p.update({k: v for k, v in product.items() if v})
                p["name"] = product["name"]
                p["brand"] = product.get("brand", p.get("brand", "Unknown"))
                # Update category if not manually set
                if p.get("category_source") != "manual":
                    p["user_category"] = map_category(product.get("categories", ""))
                    p["category_source"] = "auto"
                log(f"  Resolved: {old_name} → {product['name']} ({product.get('brand', '?')}) → {p['user_category']}")
                resolved += 1
            else:
                log(f"  Still unknown: {barcode}")
    if resolved:
        save_inventory(inv)
    log(f"Resolved {resolved} unknowns")
    return resolved

def scan_all():
    extensions = ["*.jpg", "*.jpeg", "*.png", "*.heic", "*.HEIC", "*.JPG", "*.JPEG", "*.PNG"]
    images = []
    for ext in extensions:
        images.extend(glob.glob(os.path.join(SCAN_DIR, ext)))
    results = []
    for img in sorted(images):
        r = process_image(img)
        if r:
            results.append(r)
    return results

def watch_mode():
    from inotify_simple import INotify, flags
    inotify = INotify()
    watch_flags = flags.CLOSE_WRITE | flags.MOVED_TO
    inotify.add_watch(SCAN_DIR, watch_flags)
    
    log(f"Watching (inotify): {SCAN_DIR}")
    log("Zero CPU until a file arrives.\n")
    
    # Process any existing files first
    scan_all()
    
    while True:
        events = inotify.read(timeout=None)  # Blocks until file event
        time.sleep(1)  # Brief pause for Dropbox to finish writing
        scan_all()

def show_inventory():
    inv = load_inventory()
    if not inv["products"]:
        print("Empty. Drop barcode photos in ~/Dropbox/Grocy-Scan/")
        return
    print(f"\n{'='*60}")
    print(f"PANTRY INVENTORY — {len(inv['products'])} items")
    print(f"{'='*60}\n")
    unknowns = 0
    for p in sorted(inv["products"], key=lambda x: x.get("name", "")):
        qty = p.get("quantity_count", 1)
        exp = p.get("expiration_date") or "not set"
        src = p.get("source", "openfoodfacts")
        is_unknown = p["name"].startswith("Unknown (")
        if is_unknown:
            unknowns += 1
        print(f"  [{qty}x] {p['name']}")
        if p.get("brand", "Unknown") != "Unknown":
            print(f"       Brand: {p['brand']}")
        if p.get("quantity"):
            print(f"       Size: {p['quantity']}")
        print(f"       Expires: {exp} | Barcode: {p['barcode']} | Source: {src}")
        print()
    if unknowns:
        print(f"  ⚠️  {unknowns} unknown items. Run: python3 scan.py resolve")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "watch": watch_mode()
    elif cmd == "list": show_inventory()
    elif cmd == "scan": scan_all() or print("No images to process")
    elif cmd == "resolve": resolve_unknowns()
    else:
        print("Usage: python3 scan.py watch|scan|list|resolve")
        print(f"Drop barcode photos in: {SCAN_DIR}")
        print("  watch   — Watch folder for new photos (inotify)")
        print("  scan    — Process any photos in folder now")
        print("  list    — Show current inventory")
        print("  resolve — Re-lookup all unknown barcodes")
