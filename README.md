# Grocy Barcode Scanner → Food Inventory

## How It Works

1. **Take a photo** of a barcode on your phone
2. **Drop it into** `~/Dropbox/Grocy-Scan/` (via Dropbox sync from any device)
3. **Scanner detects** the new file (inotify — zero CPU when idle)
4. **Reads barcode** using zbarimg (with enhanced image retry via PIL)
5. **Looks up product** across 3 databases in order:
   - [Open Food Facts](https://world.openfoodfacts.org) — best data, includes nutrition
   - [UPC Item DB](https://www.upcitemdb.com) — good coverage, free trial tier
   - [Go-UPC](https://go-upc.com) — web scrape fallback
6. **Saves to inventory** at `~/grocy/inventory.json`
7. **Moves photo** to `processed/` subfolder

## Commands

```bash
python3 scan.py watch     # Watch folder for new photos (inotify, runs as service)
python3 scan.py scan      # Process any photos in folder now
python3 scan.py list      # Show current inventory
python3 scan.py resolve   # Re-lookup all unknown barcodes against all databases
```

## Files

| File | Purpose |
|---|---|
| `scan.py` | Main scanner script |
| `inventory.json` | Product database (JSON) |
| `scan.log` | Processing log |
| `docker-compose.yml` | Grocy web UI (Docker) |
| `~/Dropbox/Grocy-Scan/` | Drop barcode photos here |
| `~/Dropbox/Grocy-Scan/processed/` | Photos move here after scanning |

## Service

```bash
# Systemd user service (auto-starts on boot)
systemctl --user status grocy-scanner
systemctl --user restart grocy-scanner
```

## Features

- **Dropbox dedup** — automatically skips `(1)` conflict copies
- **Multi-source lookup** — 3 databases for maximum product coverage
- **IPv4 forced** — avoids IPv6 connectivity issues
- **Image enhancement** — auto-enhances blurry/dark photos for better barcode reads
- **Source tracking** — each product records which database it came from
- **Quantity tracking** — scanning same barcode increments quantity
- **Zero CPU idle** — uses inotify, only wakes when files arrive

## Dependencies

```bash
# System
apt install zbar-tools

# Python
pip install requests inotify_simple Pillow
```

## Expanding to Other Inventory

This same pattern (photo → barcode → lookup → JSON) can be adapted for:
- **Tools** — scan UPC codes on power tools, hand tools
- **Clothes** — scan tags (though many clothes lack UPC)
- **HomeBox** — planned self-hosted general inventory system (Docker)

For non-barcoded items, consider HomeBox for manual cataloging with photos.
