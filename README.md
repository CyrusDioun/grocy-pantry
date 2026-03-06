# grocy-pantry

Barcode scanner + smart pantry dashboard for home inventory management. Built for Sage (Linux Omen), integrated with Grocy and served via the Sage Mission Control dashboard.

---

## Features (v2)

### Inventory Management
- **Barcode scanning** via USB scanner → auto-lookup via Open Food Facts API
- **Add / edit / delete** products with quantity, location, expiry, and notes
- **Out of stock tracking** — zero-quantity items flagged separately
- **Inventory persisted** in `~/grocy/inventory.json` (Dropbox-synced)

### Smart Categorization
- **10 product categories**: Produce, Dairy & Eggs, Meat & Seafood, Bakery & Bread, Pantry Staples, Snacks & Sweets, Beverages, Frozen, Household, Other
- **Auto-categorized** from Open Food Facts taxonomy on scan
- **User override** — tap category badge on any card to reassign
- Category source tracked (`api` vs `user`) for override persistence

### Dashboard UI
- **Triple filtering**: location × category × search text
- **Location tabs** with counts: All, Pantry, Fridge, Freezer
- **Category filter pill bar** — horizontal scroll on mobile
- **Sort**: Name, Quantity, Expiry — with ascending/descending toggle
- **Stats bar** — Total / Low Stock / Expiring Soon / Out of Stock, each clickable as a filter
- **Skeleton loading states**, error state with retry, empty state with CTA

### Responsive Layout
- **Mobile (≤ 1024px)**: card grid, horizontal pill scroll, bottom sheet detail panel
- **Desktop (≥ 1025px)**: fixed sidebar with filters + stats, constrained content max-width (1920px)

### Location Picker
- **Dropdown selector** on product cards (replaces blind cycle tap)
- Inline update via `PATCH /api/pantry/<barcode>`

---

## Architecture

```
USB Barcode Scanner
      │
      ▼
  scan.py  ──── Open Food Facts API (name, category)
      │
      ▼
inventory.json  (~/grocy/inventory.json, Dropbox-synced)
      │
      ▼
server.py  (Python HTTP server, port 9002)
      │
      ├── GET  /api/pantry         → full product list
      ├── PATCH /api/pantry/<id>   → update fields
      ├── POST  /api/pantry        → add product
      └── DELETE /api/pantry/<id> → remove product
      │
      ▼
pantry-dashboard.html  (single-page HTML+JS, no framework)
```

The dashboard is served as a static page within the Sage Mission Control multi-page dashboard at `http://localhost:9002/pages/pantry-dashboard.html`.

---

## Setup

### Prerequisites
- Python 3.10+
- USB barcode scanner (HID keyboard mode)
- Dropbox (optional, for cross-device sync)

### 1. Clone
```bash
git clone git@github.com:CyrusDioun/grocy-pantry.git ~/projects/grocy-pantry
```

### 2. Inventory file
```bash
mkdir -p ~/grocy
echo '{"products":[]}' > ~/grocy/inventory.json
# Or restore from Dropbox backup
```

### 3. Dashboard server (sage-tools)
The server lives in `~/projects/sage-tools/dashboard/`. It's managed by a systemd user service:
```bash
systemctl --user status dashboard
systemctl --user start dashboard
```

The dashboard page is served from:
```
~/projects/sage-tools/dashboard/pages/pantry-dashboard.html
```
This file is kept in sync with `dashboard.html` in this repo.

### 4. Scanner service
```bash
# Run scan.py directly (reads from /dev/input or stdin)
python3 ~/projects/grocy-pantry/scan.py
# Or enable as systemd service (grocy-scanner)
systemctl --user start grocy-scanner
```

### 5. Dropbox sync (optional)
Point Dropbox to sync `~/grocy/` for cross-device inventory access. The Mac and Omen both read/write the same `inventory.json`.

---

## Changelog

### v1 — 2026-03-05 · `b8fa590`
Initial release.
- USB barcode scanner (`scan.py`) with Open Food Facts lookup
- Basic pantry dashboard (`dashboard.html`) — list view, add/edit/delete
- Inventory stored in `~/grocy/inventory.json`

### v2 — 2026-03-06

#### Phase 1: Category Backend · `a090a08` · fix `41a301b`
- Added `categorize.py` — maps Open Food Facts taxonomy to 10 product groups
- Backfilled all 58 existing products with auto-categories
- Updated `scan.py` to auto-categorize on every scan
- Updated `server.py` PATCH to handle `user_category` + `category_source` fields
- Fixed timestamp format and removed dead code in scanner

#### Phase 2: Category Filter UI · `1d07d24`
- Category filter pill bar below location tabs (horizontal scroll on mobile)
- Triple filtering: location × category × search
- Category badge on product cards with dropdown picker on tap
- Category field added to Add Item modal

#### Phase 3: Desktop Sidebar Layout · `40748b1` · fix `bbeff4f`
- Responsive sidebar at ≥ 1025px with filters + stats
- Card grid adjusts for sidebar offset
- Content max-width constrained to 1920px
- All breakpoints tested 320px → 1920px

#### Phase 4: Polish · `e72eadb`
- Skeleton loading cards, centered error state with retry button, empty state with CTA
- Location dropdown replaces blind cycle-tap
- Sort direction toggle with ▲/▼ indicator
- Stats bar items clickable as filters (active state highlighted)
- "Out of stock" label for qty=0 products
- Null field handling in detail panel (no broken `undefined` display)

#### Phase 5: Deploy · 2026-03-06
- Verified `dashboard.html` ↔ `pantry-dashboard.html` in sync (identical)
- Confirmed live dashboard loads at `http://localhost:9002/pages/pantry-dashboard.html`
- Screenshots taken at 420px and 1200px
- README written with full changelog
- Pushed to `origin main`
