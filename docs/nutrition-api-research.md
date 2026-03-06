# Nutrition API Research
*Created: 2026-03-06 | For: scan.py fallback enrichment*

## Why This Matters
OpenFoodFacts (OFF) is the current sole data source for nutrition in scan.py. Many products have null fields for protein, fat, calories, etc. Multiple fallback APIs would improve data coverage significantly.

---

## API Comparison

### 1. USDA FoodData Central (FDC)
- **URL:** https://fdc.nal.usda.gov / https://api.nal.usda.gov/fdc/v1/
- **Barcode lookup:** ✅ Yes — search by `gtinUpc` in the Branded Foods dataset (monthly updated)
- **Nutrition coverage:** ⭐⭐⭐⭐⭐ Best — lab-validated data; calories, protein, fat, carbs, fiber, sugar, sodium, vitamins, minerals
- **Rate limits:** No enforced rate limit with API key (free, unlimited). Need to register for API key at https://fdc.nal.usda.gov/api-guide.html
- **Cost:** 100% free, public domain (CC0 1.0)
- **Database size:** ~250K foods; Branded Foods dataset updated monthly (v13.0 as of April 2025)
- **Data source:** US government lab tests + GDSN (Global Data Sync Network)
- **Notes:** Best accuracy for US products. UPC barcode → search for `?query=<upc>&dataType=Branded`. Returns multiple results; pick first.

### 2. Nutritionix
- **URL:** https://www.nutritionix.com/business/api
- **Barcode lookup:** ✅ Yes — `/v2/search/instant?upc=<barcode>`
- **Nutrition coverage:** ⭐⭐⭐⭐ Very good — calories, macros, micronutrients, restaurant data
- **Rate limits:** Free tier: 500 req/day. Paid plans available.
- **Cost:** Free tier available; requires sign-up for API key
- **Database size:** 900K+ foods including restaurants
- **Notes:** Strong for branded grocery items. NLP query support is a bonus. Good complement to USDA.

### 3. Edamam Food & Grocery Database API
- **URL:** https://developer.edamam.com/food-database-api
- **Barcode lookup:** ✅ Yes — explicit UPC support; 680K+ UPCs indexed
- **Nutrition coverage:** ⭐⭐⭐⭐ Good — macros + micronutrients, diet labels (vegan, keto, etc.)
- **Rate limits:** Free tier: limited (need to check current free plan; has historically been 400 req/month)
- **Cost:** Free tier very limited; $29-$99/month for meaningful usage
- **Notes:** 680K UPCs is impressive. Best for recipe integration. Diet/allergy tagging is unique. **Rate limits make it a poor fallback unless paid plan**.

### 4. CalorieNinja (calorieninjas.com)
- **URL:** https://calorieninjas.com/api
- **Barcode lookup:** ✅ Claimed — but API is name-based primarily; barcode support unclear
- **Nutrition coverage:** ⭐⭐⭐ Moderate — basic macros; less detail than USDA
- **Rate limits:** Free tier available; exact limits undocumented (check dashboard after signup)
- **Cost:** Free tier; paid for higher limits
- **Notes:** Easy setup but coverage and barcode lookup reliability uncertain. Not recommended as primary fallback.

### 5. Spoonacular
- **URL:** https://spoonacular.com/food-api
- **Barcode lookup:** ✅ Yes — `/food/products/upc/{upc}` endpoint
- **Nutrition coverage:** ⭐⭐⭐⭐ Good — macros + full nutrient list + product info (image, brand, servings)
- **Rate limits:** Free tier: 150 req/day (1 point per request; 150 points/day free)
- **Cost:** Free tier exists; $29-$99/month for more
- **Notes:** Has a dedicated barcode/UPC endpoint. Returns product image, brand, full nutrition, ingredients. Solid choice but free rate limits are low.

---

## Summary Table

| API | Barcode Lookup | Nutrition Coverage | Free Limit | Cost |
|-----|---------------|-------------------|------------|------|
| USDA FoodData Central | ✅ | ⭐⭐⭐⭐⭐ | Unlimited | Free |
| Nutritionix | ✅ | ⭐⭐⭐⭐ | 500/day | Free tier |
| Edamam | ✅ | ⭐⭐⭐⭐ | ~400/month | Paid for more |
| CalorieNinja | ⚠️ Unclear | ⭐⭐⭐ | Unknown | Free tier |
| Spoonacular | ✅ | ⭐⭐⭐⭐ | 150/day | Free tier |
| OpenFoodFacts (current) | ✅ | ⭐⭐⭐ | Unlimited | Free |

---

## Recommendation for scan.py

**Add as fallback sources in this priority order:**

1. **OpenFoodFacts** (current, keep as primary) — barcode-first, community data, good international coverage
2. **USDA FoodData Central** (add as fallback #1) — best data quality, truly free unlimited, US-focused. Query by UPC via `https://api.nal.usda.gov/fdc/v1/foods/search?query={barcode}&dataType=Branded,Foundation&api_key={key}`. API key is free at fdc.nal.usda.gov.
3. **Spoonacular** (add as fallback #2) — clean barcode endpoint, returns product image too, 150/day free is sufficient for household scan volume (we scan maybe 1-5 new products/week)

**Skip Edamam** (too restrictive on free tier) and **CalorieNinja** (barcode support unverified).

### Implementation sketch for scan.py:
```python
def fetch_nutrition(barcode):
    # Try OFF first
    data = fetch_openfoodfacts(barcode)
    if has_sufficient_nutrition(data):
        return data
    
    # Fallback to USDA
    data = fetch_usda_fdc(barcode)
    if has_sufficient_nutrition(data):
        return data
    
    # Fallback to Spoonacular
    data = fetch_spoonacular(barcode)
    return data

def has_sufficient_nutrition(data):
    """Return True if we have at least calories + protein"""
    n = data.get('nutrition', {})
    return n.get('calories_per_100g') and n.get('protein_per_100g')
```

*This is research only. Implementation goes in Phase 4 or later.*
