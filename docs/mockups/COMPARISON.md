# Pantry Dashboard v2 — Design Mockup Comparison

*Created: 2026-03-06 · Evaluator: Sage (UI/UX Design Subagent)*

---

## The 3 Concepts

### Concept A — "Warm Kitchen"
**Aesthetic:** Cream/sage palette, soft rounded cards, organic recipe-app feel.  
**Desktop:** Left sidebar (280px) with category list + color bars, stats mini-cards in 2×2 grid.  
**Category filter:** Pill bar with colored `--cat-*` backgrounds, inline on mobile.  
**Card category badge:** Colored dot + emoji + name in a pill, right after brand.

### Concept B — "Clean Market"
**Aesthetic:** Near-monochromatic, structured, grocery-store-shelf logic.  
**Desktop:** Full-width header with location dropdown + sort pills, NO sidebar. Content grouped by category sections with collapsible dividers.  
**Category filter:** 5×2 emoji icon grid on mobile; dropdown selects on desktop.  
**Card style:** List rows, not grid cards. Bold category section headers divide items.

### Concept C — "Dashboard Pro"
**Aesthetic:** Dark sidebar (`#1E2330`), light content area, SaaS analytics feel.  
**Desktop:** Dark left sidebar with collapsible filter groups (location, multi-select category checkboxes, expiry status, sort). Main area shows a data table (row view) on desktop, cards on mobile. Stats bar = 4 summary cards with mini sparkline bars.  
**Category filter:** Multi-select checkboxes in sidebar (desktop); horizontal pill scroll (mobile).  
**Card style:** Compact data-table rows on desktop (5-column: name, category, location, expiry, qty).

---

## Scoring Matrix

| Criterion | Concept A | Concept B | Concept C |
|---|:---:|:---:|:---:|
| **Aesthetic quality** | 9 | 7 | 8 |
| **Information density** | 6 | 8 | 10 |
| **Mobile usability** | 9 | 8 | 8 |
| **Desktop efficiency** | 8 | 7 | 10 |
| **Alignment with v1 aesthetic** | 10 | 6 | 5 |
| **Innovation** | 6 | 8 | 10 |
| **TOTAL** | **48** | **44** | **51** |

---

## Detailed Analysis

### Concept A — Warm Kitchen ⭐ Mobile Best / Aesthetic Winner

**Strengths:**
- Closest to v1 — same cream bg, sage green primary, warm card feel. Zero regression risk.
- The colored `--cat-*` pill badges are immediately readable and beautiful.
- Sidebar category list with color bars is elegant and easy to scan.
- Stats as mini 2×2 cards in sidebar is much better than the v1 muted dots.
- Mobile pill scroll is exactly right — comfortable thumb zone, high contrast.

**Weaknesses:**
- Desktop isn't radically different from a stretched mobile layout — still card-heavy.
- Lowest information density of the three — one card per row feels spacious but shallow.
- Sort as a vertical list in sidebar is less discoverable than inline pills.
- Least innovative — a beautiful execution of the obvious path.

**Risk:** Low. This is the safest implementation.

---

### Concept B — Clean Market

**Strengths:**
- Category icon grid on mobile is delightful — emoji + count, grid layout, feels like a grocery app.
- Collapsible category sections are excellent UX for power users who know their mental model (dairy, produce, etc.).
- Stats strip with large numbers across the top is clean and scannable.
- List-style rows are more information-dense than cards.

**Weaknesses:**
- Desktop top bar with dropdowns for both Location and Category feels cramped on smaller desktops.
- No sidebar means filters always take up prime real estate in the header.
- The monochromatic aesthetic is a departure from v1's warmth — could feel cold/clinical.
- Category section grouping means items aren't sorted uniformly — you can only sort within a category.
- If "All" is selected, sections with 1-2 items waste a lot of vertical space on section headers.

**Risk:** Medium. The grouped-by-category view is a strong concept but conflicts with user's expectation of a unified sorted list.

---

### Concept C — Dashboard Pro ⭐ Desktop Best / Feature Winner

**Strengths:**
- Dark sidebar is beautiful and immediately signals "serious tool" — fits Cyrus's SaaS-oriented aesthetic taste.
- Multi-select category filters are the most powerful UX — select Dairy + Produce + Meat, see only those.
- Sparkline bars in sidebar KPIs are a distinctive touch — no other pantry app does this.
- Desktop table view (5-column rows) is the most efficient at showing 58 items — 20+ visible at once vs. ~6 in card view.
- Filter chips in topbar show active filters at a glance, with easy ×-removal.
- View toggle (cards ↔ list) gives users agency.

**Weaknesses:**
- Dark sidebar is a significant aesthetic departure from v1's warm cream palette. Could feel jarring.
- Dark sidebar adds implementation complexity (two distinct color systems).
- Table view requires careful column sizing on 1024-1100px viewports.
- KPI sparklines are decorative — the trend data doesn't exist yet (would need historical tracking).

**Risk:** Medium-High on aesthetics. Low on functionality.

---

## 🏆 Recommendation

### Implement: **A + C Hybrid** ("Warm Dashboard")

Take Concept A's aesthetics and Concept C's functional innovations:

**From Concept A (keep):**
- Warm cream background + sage green primary
- Rounded card style for mobile
- Colored category pill badges on cards
- Mobile horizontal pill scroll for categories

**From Concept C (add):**
- **Sidebar on desktop** — but in `--sidebar-bg: #F8F4EC` (warm, not dark)
- **Multi-select category checkboxes** in sidebar (huge UX win, minimal extra code)
- **Summary cards with counts** replacing muted stat dots
- **Sort direction indicators (▲/▼)** on active sort option
- **Active filter chips** in desktop topbar
- **List/card view toggle** on desktop (compact rows = much more efficient)

**From Concept B (one thing):**
- **Category section grouping** as an optional view mode (toggle between "by category" and "unified sort")

### Why not pure C?
The dark sidebar is too jarring for a kitchen/food app. The spec explicitly says "warm, food-appropriate color palette." A dark sidebar would feel like opening a stock trading terminal in the kitchen. The `--sidebar-bg: #F8F4EC` from the spec keeps it warm while gaining all the structural benefits.

### Why not pure A?
Concept A misses the biggest wins: multi-select, list view on desktop, and the active-filter chip pattern. These are table stakes for a v2 upgrade.

### Implementation order for Builder:
1. Start with Concept A HTML structure (closest to v1, lowest migration risk)
2. Add sidebar at >1024px using Concept C's sidebar CSS patterns (adapted to warm palette)
3. Add multi-select category checkboxes in sidebar (Concept C pattern)
4. Add list/compact-row view toggle for desktop (Concept C table pattern)
5. Add filter chips in topbar (Concept C pattern)
6. Add category icon grid on mobile as alternative to pills (Concept B pattern, optional)

---

## Screenshots

All 6 screenshots saved to `screenshots/` directory:
- `concept-a-mobile.png` — 420px viewport
- `concept-a-desktop.png` — 1200px viewport
- `concept-b-mobile.png` — 420px viewport
- `concept-b-desktop.png` — 1200px viewport
- `concept-c-mobile.png` — 420px viewport
- `concept-c-desktop.png` — 1200px viewport

---

*Design evaluation by Sage · Pantry Dashboard v2 · 2026-03-06*
