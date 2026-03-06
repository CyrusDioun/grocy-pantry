#!/usr/bin/env python3
"""
Category Mapper — maps OpenFoodFacts taxonomy strings to 10 clean pantry categories.

Usage:
    from category_mapper import map_category
    cat = map_category("Dairies, Milks, Cow milks")  # → "Dairy"
"""

# Segments to skip — they're OFF meta-categories, not useful for classification
SKIP_SEGMENTS = {
    "plant-based foods and beverages",
    "plant-based foods",
    "plant-based beverages",
    "specific products",
    "plant-based",
}

# Segments that start with "en:" are taxonomy codes, skip them
def _is_skip_segment(seg: str) -> bool:
    s = seg.strip().lower()
    if s.startswith("en:"):
        return False  # We'll handle en: codes separately below
    return s in SKIP_SEGMENTS


# Category taxonomy: ordered by priority (most specific first).
# For each category: (name, keywords_list)
# Each keyword is checked as a substring in a normalized segment.
CATEGORY_RULES = [
    ("Dairy",           ["dairies", "milks", "yogurt", "yogurts", "cheese", "butter",
                          "cream", "kefir", "dairy", "en:milk", "en:milks", "en:dairy"]),
    ("Frozen",          ["frozen foods", "frozen fruits", "frozen vegetables",
                          "frozen meals", "frozen", "ice cream", "gelato",
                          "en:frozen", "en:ice-cream"]),
    ("Meat & Protein",  ["meats", "poultry", "beef", "chicken", "fish", "seafood",
                          "eggs", "turkey", "pork", "lamb", "protein",
                          "en:meats", "en:eggs", "en:poultry"]),
    ("Beverages",       ["beverages", "juices", "juice", "water", "coffees", "coffee",
                          "tea", "soda", "drinks", "drink", "beverage", "smoothie",
                          "lemonade", "broth", "stock", "coconut water",
                          "en:beverages", "en:juices"]),
    ("Produce",         ["fruits and vegetables", "fruits", "vegetables", "avocados",
                          "onions", "tomatoes", "berries", "fresh produce",
                          "lettuce", "greens", "kale", "spinach", "peppers",
                          "mango", "kiwi", "banana", "salad kits", "salad kit",
                          "chopped salad", "bagged salads", "en:fruits", "en:vegetables",
                          "en:salad-kit"]),
    ("Grains & Bakery", ["cereals and potatoes", "breads", "cereals", "pasta", "rice",
                          "flour", "bakery", "tortillas", "bread", "buns", "rolls",
                          "bagels", "wraps", "grain", "wheat", "oats", "simit",
                          "focaccia", "pita", "flatbread", "pocket bread", "sourdough",
                          "bakery products", "en:breads", "en:bakery"]),
    ("Snacks",          ["snacks", "chips", "cookies", "candy", "chocolate",
                          "nuts", "popcorn", "snack", "brownie", "toffee", "mints",
                          "gummies", "sweets", "confectionery", "biscuits and cakes",
                          "biscuits", "cakes", "sweet snacks", "salted snacks",
                          "en:snacks", "en:chocolate"]),
    ("Condiments & Sauces", ["condiments", "sauces", "ketchup", "mustard",
                              "dressing", "oil", "vinegar", "condiment", "salsa",
                              "dips", "spreads", "marinades", "kimchi", "pesto",
                              "jam", "jelly", "mayo", "mayonnaise", "en:condiments",
                              "en:sauces"]),
    ("Meals & Prepared",["meals", "pizzas", "sandwiches", "soups", "samosas",
                          "prepared", "ready-to-eat", "ready meals",
                          "meal", "pizza", "lasagna", "burrito", "tacos",
                          "dumplings", "empanadas", "en:meals"]),
]

DEFAULT_CATEGORY = "Other"


def map_category(categories_str: str) -> str:
    """
    Map an OpenFoodFacts categories string to one of 10 pantry categories.

    Args:
        categories_str: Comma-separated categories string from OFF
                        e.g. "Dairies, Milks, Cow milks"

    Returns:
        One of the 10 category names, or "Other" if no match.
    """
    if not categories_str or not categories_str.strip():
        return DEFAULT_CATEGORY

    # Split and normalize segments
    raw_segments = [s.strip() for s in categories_str.split(",") if s.strip()]

    # Build two lists: normal segments and en: codes
    segments = []
    en_codes = []
    for seg in raw_segments:
        s = seg.lower()
        if s.startswith("en:"):
            en_codes.append(s)
        elif s not in SKIP_SEGMENTS:
            segments.append(s)

    # Check segments first (in order), then en: codes
    all_to_check = segments + en_codes

    for segment in all_to_check:
        for category, keywords in CATEGORY_RULES:
            for keyword in keywords:
                if keyword in segment:
                    return category

    return DEFAULT_CATEGORY


if __name__ == "__main__":
    # Self-test with real OFF data from inventory
    tests = [
        ("Dairies, Milks, Cow milks", "Dairy"),
        ("Dairies, Milks", "Dairy"),
        ("en:milk", "Dairy"),
        ("Condiments, Sauces, Dips", "Condiments & Sauces"),
        ("Condiments,Sauces,Mustards,Yellow mustards", "Condiments & Sauces"),
        ("Condiments,Sauces,Tomato sauces,Ketchup,Groceries", "Condiments & Sauces"),
        # Beverages (not falsely matched by "plant-based foods and beverages")
        ("Plant-based foods and beverages, Beverages, Plant-based beverages, Specific products", "Beverages"),
        ("Beverages, Juices", "Beverages"),
        # Produce
        ("Plant-based foods and beverages, Plant-based foods, Fruits and vegetables based foods, Fruits", "Produce"),
        ("Avocados", "Produce"),
        ("Onions", "Produce"),
        ("en:salad-kit", "Produce"),
        ("Meals,Prepared salads,Bagged salads,Salad", "Meals & Prepared"),  # "Meals" wins first
        # Grains & Bakery
        ("Plant-based foods and beverages, Plant-based foods, Cereals and potatoes, Breads", "Grains & Bakery"),
        ("en:breads", "Grains & Bakery"),
        ("Bakery products", "Grains & Bakery"),
        # Snacks
        ("Plant-based foods and beverages, Plant-based foods, Snacks, Cereals and potatoes", "Snacks"),
        ("Snacks, Sweet snacks, Biscuits and cakes, Cakes", "Snacks"),
        ("Salted snacks", "Snacks"),
        ("Snacks, Desserts, Sweet snacks, Biscuits and cakes", "Snacks"),
        # Frozen
        ("Frozen foods", "Frozen"),
        ("Frozen mangos", "Frozen"),
        # Meat & Protein
        ("Meats and their products, Meats, Poultries", "Meat & Protein"),
        ("en:eggs", "Meat & Protein"),
        # Meals & Prepared
        ("Meals, Pizzas pies and quiches, Pizzas", "Meals & Prepared"),
        ("Canned foods, Meals, Soups, Canned meals", "Meals & Prepared"),
        ("Meals, Samosas", "Meals & Prepared"),
        # Kimchi → Condiments
        ("Salted-snacks,Kimchi,Fermented foods,Fermented plants", "Snacks"),
        # Hazelnut spread (Sandwiches category in OFF)
        ("Sandwiches", "Meals & Prepared"),
        # Chocolate covered nuts → Snacks (contains "chocolate")
        ("en:chocolate-covered-nuts", "Snacks"),
        # Empty/unknown
        ("", "Other"),
        ("Unknown category xyz", "Other"),
    ]

    print("=== Category Mapper Self-Test ===\n")
    passed = 0
    for categories, expected in tests:
        result = map_category(categories)
        status = "✓" if result == expected else "✗"
        if result == expected:
            passed += 1
        print(f"  {status} {result:22} (expected: {expected:22}) | '{categories[:60]}'")

    print(f"\n{passed}/{len(tests)} tests passed")
