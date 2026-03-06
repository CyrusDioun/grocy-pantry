#!/usr/bin/env python3
"""
Backfill Script — assigns user_category + category_source to all existing products.

Respects existing manual overrides (category_source = "manual").
Run once to normalize all 58 products.

Usage: python3 backfill_categories.py [--dry-run]
"""

import json
import sys
import shutil
from datetime import datetime
from pathlib import Path
from collections import Counter
from category_mapper import map_category

INVENTORY_FILE = Path.home() / "grocy" / "inventory.json"


def main(dry_run=False):
    # Load inventory
    with open(INVENTORY_FILE) as f:
        data = json.load(f)

    products = data.get("products", [])
    print(f"Loaded {len(products)} products from {INVENTORY_FILE}\n")

    stats = Counter()
    changes = []

    for p in products:
        name = p.get("name", "?")
        categories_str = p.get("categories", "")
        existing_source = p.get("category_source")
        existing_cat = p.get("user_category")

        # Skip manual overrides
        if existing_source == "manual":
            print(f"  SKIP (manual): {name[:40]} → {existing_cat}")
            stats["skipped_manual"] += 1
            continue

        # Map category
        new_cat = map_category(categories_str)
        stats[new_cat] += 1

        if not dry_run:
            p["user_category"] = new_cat
            p["category_source"] = "auto"

        changed = existing_cat != new_cat
        changes.append((name, existing_cat, new_cat, changed))
        marker = "NEW" if existing_cat is None else ("CHG" if changed else "OK ")
        print(f"  {marker}: {name[:40]:40} → {new_cat}")

    print(f"\n{'='*60}")
    print(f"Category Distribution:")
    for cat, count in sorted(stats.items(), key=lambda x: -x[1]):
        if cat != "skipped_manual":
            bar = "█" * count
            print(f"  {cat:25} {count:2}  {bar}")
    print(f"\n  Skipped (manual overrides): {stats['skipped_manual']}")
    print(f"  Total processed: {len(products) - stats['skipped_manual']}")

    if dry_run:
        print("\n[DRY RUN — no changes written]")
        return

    # Save
    data["last_updated"] = datetime.now().isoformat()
    with open(INVENTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n✓ Saved to {INVENTORY_FILE}")

    # Verify
    with open(INVENTORY_FILE) as f:
        verify = json.load(f)
    missing = [p["name"] for p in verify["products"] if not p.get("user_category")]
    if missing:
        print(f"\n⚠️  WARNING: {len(missing)} products still missing user_category:")
        for n in missing:
            print(f"  - {n}")
    else:
        print(f"✓ Verification passed: all {len(verify['products'])} products have user_category")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("=== Backfill (DRY RUN) ===\n")
    else:
        print("=== Backfill Categories ===\n")
    main(dry_run)
