"""Synthetic e-commerce data generator for the demo-ecommerce Elasticsearch index."""

import json
import random
import uuid
from datetime import datetime, timedelta, timezone

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from faker import Faker

fake = Faker()

INDEX_NAME = "demo-ecommerce"

INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "order_id":            {"type": "keyword"},
            "customer_id":         {"type": "keyword"},
            "customer_name":       {"type": "text"},
            "customer_region":     {"type": "keyword"},
            "order_date":          {"type": "date"},
            "status":              {"type": "keyword"},
            "product_category":    {"type": "keyword"},
            "product_name":        {"type": "text"},
            "product_description": {"type": "semantic_text"},
            "unit_price":          {"type": "float"},
            "quantity":            {"type": "integer"},
            "total_amount":        {"type": "float"},
            "payment_method":      {"type": "keyword"},
        }
    }
}

_REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]

_STATUSES = ["placed", "shipped", "delivered", "returned"]
_STATUS_WEIGHTS = [0.15, 0.20, 0.60, 0.05]

_PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "bank_transfer"]

_CATEGORIES = {
    "Electronics":    (49.99,  899.99),
    "Clothing":       (12.99,  149.99),
    "Home & Garden":  (9.99,   299.99),
    "Sports":         (14.99,  499.99),
    "Books":          (5.99,   49.99),
    "Beauty":         (7.99,   89.99),
}

_PRODUCTS = {
    "Electronics":   ["Wireless Headphones", "Smart Speaker", "USB-C Hub", "Laptop Stand",
                      "Mechanical Keyboard", "Webcam HD", "Monitor Arm", "Portable Charger"],
    "Clothing":      ["Running Shoes", "Denim Jacket", "Yoga Pants", "Cotton T-Shirt",
                      "Wool Sweater", "Rain Jacket", "Casual Sneakers", "Linen Shorts"],
    "Home & Garden": ["Coffee Maker", "Air Purifier", "Throw Pillow", "Bamboo Cutting Board",
                      "Scented Candle", "Plant Pot", "Desk Lamp", "Storage Basket"],
    "Sports":        ["Foam Roller", "Resistance Bands", "Jump Rope", "Yoga Mat",
                      "Water Bottle", "Gym Gloves", "Dumbbell Set", "Fitness Tracker"],
    "Books":         ["Python Crash Course", "Clean Code", "Designing Data-Intensive Applications",
                      "Atomic Habits", "The Pragmatic Programmer", "Deep Work", "Refactoring"],
    "Beauty":        ["Face Moisturizer", "Vitamin C Serum", "Lip Balm", "Shampoo Bar",
                      "Eye Cream", "Sunscreen SPF50", "Charcoal Mask", "Hair Oil"],
}

# Descriptions are crafted for semantic richness: cross-category themes (home office,
# fitness/recovery, eco-friendly, travel) surface naturally in semantic queries even when
# product_category or product_name don't contain the search terms.
_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "Electronics": {
        "Wireless Headphones": (
            "Premium wireless headphones with active noise cancellation deliver studio-quality "
            "sound for deep focus work sessions and immersive listening. Designed for remote "
            "workers and commuters who need to eliminate background distractions."
        ),
        "Smart Speaker": (
            "Voice-controlled smart speaker with room-filling audio brings music, podcasts, and "
            "calendar reminders to life hands-free. A central hub for the connected smart home "
            "that responds to natural voice commands throughout the day."
        ),
        "USB-C Hub": (
            "Slim USB-C hub expands a laptop to seven ports including HDMI, SD card reader, and "
            "USB-A for a complete home office workstation setup. Compatible with all major "
            "operating systems and ideal for portable productivity."
        ),
        "Laptop Stand": (
            "Adjustable aluminum laptop stand elevates the screen to eye level, reducing neck and "
            "shoulder strain during long remote work sessions. Folds flat for commuting and fits "
            "neatly in a laptop bag."
        ),
        "Mechanical Keyboard": (
            "Compact mechanical keyboard with satisfying tactile switches built for programmers "
            "and writers who spend hours typing. Wireless connectivity and low-profile design keep "
            "any home office desk clean and clutter-free."
        ),
        "Webcam HD": (
            "1080p wide-angle webcam with automatic light correction delivers crisp, professional "
            "video quality for remote meetings and online presentations. Built-in dual microphone "
            "with noise cancellation reduces background sound."
        ),
        "Monitor Arm": (
            "Fully articulating dual monitor arm allows precise screen positioning for ergonomic "
            "home office setups and multi-screen coding workstations. Integrated cable management "
            "routes power and data cables cleanly behind the desk."
        ),
        "Portable Charger": (
            "High-capacity 20,000mAh portable charger with fast-charging output keeps smartphones, "
            "tablets, and wireless earbuds powered during travel, hiking, and outdoor adventures. "
            "Compact enough for carry-on bags."
        ),
    },
    "Clothing": {
        "Running Shoes": (
            "Lightweight road running shoes with responsive cushioning and a breathable mesh upper "
            "designed for daily training runs and marathon preparation. Slip-resistant outsole "
            "provides traction on wet pavement and light trails."
        ),
        "Denim Jacket": (
            "Classic denim jacket with a relaxed fit and reinforced stitching that layers over "
            "t-shirts or acts as a light shell in cool weather. Fades naturally with wear for "
            "a vintage look suited to casual outdoor outings."
        ),
        "Yoga Pants": (
            "High-waist yoga pants with four-way stretch fabric and a hidden waistband pocket "
            "designed for yoga, pilates, barre, and low-impact fitness workouts. Moisture-wicking "
            "material keeps you cool and comfortable through any flow."
        ),
        "Cotton T-Shirt": (
            "Organic cotton crewneck t-shirt in a relaxed unisex fit that works as a base layer "
            "for outdoor activities or a casual everyday wardrobe staple. Pre-washed to prevent "
            "shrinking and made from sustainably sourced fibers."
        ),
        "Wool Sweater": (
            "Soft merino wool sweater with natural temperature-regulating properties perfect for "
            "hiking, outdoor adventures, and urban commuting in variable weather. Naturally "
            "odor-resistant, machine washable, and a durable sustainable choice."
        ),
        "Rain Jacket": (
            "Waterproof, breathable rain jacket with taped seams and an adjustable hood designed "
            "for cycling commutes, trail running, and all-day outdoor festivals. Packs into its "
            "own chest pocket for compact travel storage."
        ),
        "Casual Sneakers": (
            "Versatile canvas sneakers with memory foam insoles and a vulcanized rubber sole "
            "offering all-day comfort for city walking, travel, and everyday casual wear. "
            "Available in minimal, clean colorways that go with anything."
        ),
        "Linen Shorts": (
            "Relaxed-fit linen shorts with an elastic waistband and deep side pockets ideal for "
            "beach vacations, summer travel, and warm-weather outdoor gatherings. Natural linen "
            "fabric is breathable, quick-drying, and eco-friendly."
        ),
    },
    "Home & Garden": {
        "Coffee Maker": (
            "Programmable drip coffee maker with a built-in burr grinder and thermal carafe brews "
            "fresh, aromatic coffee on a schedule so your morning cup is ready when you wake up. "
            "Perfect for home baristas and remote workers who need reliable fuel for focused work."
        ),
        "Air Purifier": (
            "True HEPA air purifier removes 99.97% of dust, pollen, pet dander, and smoke "
            "particles from bedroom and living room air. Whisper-quiet sleep mode runs throughout "
            "the night for cleaner, healthier breathing and better rest."
        ),
        "Throw Pillow": (
            "Handwoven throw pillow with a removable, washable cover adds texture and warmth to "
            "living room sofas and bedroom headboards. Filled with recycled polyester for a "
            "sustainable and cozy home aesthetic."
        ),
        "Bamboo Cutting Board": (
            "Large bamboo cutting board with deep juice grooves and a built-in handle is gentle "
            "on knife blades and naturally antimicrobial for food safety. An eco-friendly "
            "sustainable alternative to plastic kitchen boards."
        ),
        "Scented Candle": (
            "Hand-poured soy wax candle with calming lavender and eucalyptus essential oils "
            "creates a spa-like atmosphere for relaxation, meditation, and self-care routines. "
            "Clean burn with no toxic paraffin or artificial fragrances."
        ),
        "Plant Pot": (
            "Minimalist ceramic plant pot with a drainage hole and matching saucer, sized for "
            "succulents, herbs, and small tropical houseplants that brighten any indoor space. "
            "Glazed finish is easy to wipe clean and pairs with modern or bohemian home decor."
        ),
        "Desk Lamp": (
            "LED desk lamp with tunable color temperature from warm to cool white and stepless "
            "dimming for reading, studying, and focused home office work. A built-in USB charging "
            "port in the base keeps devices topped up without extra adapters."
        ),
        "Storage Basket": (
            "Handwoven seagrass storage basket with rope handles for organizing blankets, throw "
            "pillows, toys, and bathroom essentials with a natural, bohemian aesthetic. A "
            "sustainable and stylish alternative to plastic storage bins."
        ),
    },
    "Sports": {
        "Foam Roller": (
            "High-density EVA foam roller with a textured surface for deep-tissue myofascial "
            "release, post-workout muscle recovery, and relief from tightness in the IT band, "
            "back, and calves. An essential tool for athletes and anyone managing chronic tension."
        ),
        "Resistance Bands": (
            "Set of five looped resistance bands with progressive tension levels for glute "
            "activation, physical therapy rehabilitation, warm-up routines, and full-body "
            "strength training at home or in the gym without heavy equipment."
        ),
        "Jump Rope": (
            "Lightweight speed jump rope with precision ball-bearing handles and an adjustable "
            "cable for double-unders, high-intensity cardio conditioning, and boxing training "
            "workouts that build endurance and coordination."
        ),
        "Yoga Mat": (
            "6mm thick non-slip yoga mat with alignment lines and a closed-cell surface that is "
            "sweat-resistant and easy to wipe clean after hot yoga, pilates, and stretching "
            "sessions. Supports mindful movement and recovery practice at home or the studio."
        ),
        "Water Bottle": (
            "Double-wall vacuum-insulated stainless steel water bottle keeps drinks cold for "
            "24 hours and hot for 12 hours, perfect for gym sessions, hiking, trail running, "
            "and daily hydration goals throughout the workday."
        ),
        "Gym Gloves": (
            "Leather-palm gym gloves with integrated wrist wraps and padded grip zones designed "
            "for weightlifting, pull-ups, and cross-training exercises to prevent calluses and "
            "improve grip on barbells and pull-up bars."
        ),
        "Dumbbell Set": (
            "Adjustable cast-iron dumbbell set with a quick-change weight selector system "
            "replaces a full rack of dumbbells for compact home gym strength and hypertrophy "
            "training. Saves floor space while covering a full range of resistance loads."
        ),
        "Fitness Tracker": (
            "Slim fitness tracker with continuous heart rate monitoring, sleep quality scoring, "
            "GPS route tracking, and a seven-day battery life for running, cycling, strength "
            "training, and daily activity and recovery goals."
        ),
    },
    "Books": {
        "Python Crash Course": (
            "Hands-on introduction to Python programming with projects covering web scraping, "
            "data visualization, and game development for beginners and self-taught developers. "
            "Clear, project-driven approach that gets readers building real things quickly."
        ),
        "Clean Code": (
            "Practical guide to writing readable, maintainable, and well-structured code through "
            "naming conventions, small functions, and continuous refactoring for professional "
            "software engineers. Widely considered a foundational text for software craftsmanship."
        ),
        "Designing Data-Intensive Applications": (
            "Deep technical exploration of how modern data systems are built: databases, "
            "distributed computing, stream processing, and the trade-offs behind reliability and "
            "scalability. Essential reading for backend engineers and data engineers at scale."
        ),
        "Atomic Habits": (
            "Behavioral science framework for building lasting good habits and breaking bad ones "
            "through tiny one-percent daily improvements that compound into remarkable long-term "
            "results. Practical strategies grounded in psychology and neuroscience research."
        ),
        "The Pragmatic Programmer": (
            "Timeless career guide for software developers on writing adaptable, future-proof code, "
            "managing complexity, and growing as a craftsman throughout a long engineering career. "
            "Covers everything from source control to personal responsibility."
        ),
        "Deep Work": (
            "Research-backed productivity philosophy for achieving intense, focused concentration "
            "on cognitively demanding tasks in an age of constant digital distraction and shallow "
            "work. Essential for remote workers, writers, and knowledge professionals."
        ),
        "Refactoring": (
            "Step-by-step catalog of techniques for restructuring existing code to improve its "
            "internal design, readability, and maintainability without changing its observable "
            "external behavior. Includes worked examples in multiple programming languages."
        ),
    },
    "Beauty": {
        "Face Moisturizer": (
            "Lightweight daily face moisturizer with hyaluronic acid, niacinamide, and SPF 30 "
            "hydrates, brightens, and protects skin from UV damage as part of a morning skincare "
            "routine. Suitable for all skin types including sensitive and acne-prone skin."
        ),
        "Vitamin C Serum": (
            "10% L-ascorbic acid vitamin C serum with ferulic acid fades hyperpigmentation, "
            "evens skin tone, and provides antioxidant protection against environmental stressors "
            "with consistent daily use in a morning skincare regimen."
        ),
        "Lip Balm": (
            "Nourishing lip balm with shea butter, vitamin E, and beeswax soothes and heals dry, "
            "chapped lips and provides a protective barrier against cold, wind, and dry indoor air. "
            "A travel essential for outdoor activities and long flights."
        ),
        "Shampoo Bar": (
            "Zero-waste solid shampoo bar with rosemary and biotin cleanses and strengthens hair "
            "while eliminating single-use plastic bottles from your bathroom routine. Lasts three "
            "times longer than a standard liquid shampoo bottle."
        ),
        "Eye Cream": (
            "Firming eye cream with retinol, peptides, and caffeine visibly reduces fine lines, "
            "dark circles, and morning puffiness around the eyes with consistent use in a nightly "
            "skincare self-care regimen."
        ),
        "Sunscreen SPF50": (
            "Mineral broad-spectrum SPF 50 sunscreen with zinc oxide provides reef-safe, "
            "non-greasy daily UV protection suitable for sensitive skin, outdoor sports, "
            "beach activities, and high-altitude hiking."
        ),
        "Charcoal Mask": (
            "Deep-cleansing activated charcoal face mask with kaolin clay draws out blackheads, "
            "excess oil, and pore-clogging impurities for clearer, smoother skin in a weekly "
            "self-care and skincare treatment."
        ),
        "Hair Oil": (
            "Lightweight blend of argan, jojoba, and rosehip oils tames frizz, adds mirror shine, "
            "and nourishes dry ends without weighing hair down after washing or heat styling. "
            "A finishing treatment for all hair types."
        ),
    },
}


def _random_date(days_back: int = 180) -> str:
    now = datetime.now(tz=timezone.utc)
    delta = timedelta(seconds=random.randint(0, days_back * 86400))
    return (now - delta).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_documents(count: int = 5000) -> list[dict]:
    """Return a list of synthetic e-commerce order documents."""
    docs = []
    for _ in range(count):
        category = random.choice(list(_CATEGORIES))
        low, high = _CATEGORIES[category]
        unit_price = round(random.uniform(low, high), 2)
        quantity = random.randint(1, 5)
        product_name = random.choice(_PRODUCTS[category])
        doc = {
            "order_id":            str(uuid.uuid4()),
            "customer_id":         str(uuid.uuid4()),
            "customer_name":       fake.name(),
            "customer_region":     random.choice(_REGIONS),
            "order_date":          _random_date(),
            "status":              random.choices(_STATUSES, weights=_STATUS_WEIGHTS)[0],
            "product_category":    category,
            "product_name":        product_name,
            "product_description": _DESCRIPTIONS[category][product_name],
            "unit_price":          unit_price,
            "quantity":            quantity,
            "total_amount":        round(unit_price * quantity, 2),
            "payment_method":      random.choice(_PAYMENT_METHODS),
        }
        docs.append(doc)
    return docs


def create_index(es: Elasticsearch, index_name: str = INDEX_NAME) -> None:
    """Create the index with explicit mapping, deleting any existing index first."""
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Deleted existing index '{index_name}'")
    es.indices.create(index=index_name, body=INDEX_MAPPING)
    print(f"Created index '{index_name}' with explicit mapping")


def index_documents(
    es: Elasticsearch,
    documents: list[dict],
    index_name: str = INDEX_NAME,
    chunk_size: int = 500,
) -> tuple[int, int]:
    """Bulk-index documents. Returns (success_count, error_count)."""
    actions = ({"_index": index_name, "_source": doc} for doc in documents)
    success, errors = bulk(es, actions, chunk_size=chunk_size, raise_on_error=False)
    if errors:
        print(f"  {len(errors)} indexing error(s)")
    es.indices.refresh(index=index_name)
    return success, len(errors) if isinstance(errors, list) else 0

def verify_index(es: Elasticsearch, index_name: str = INDEX_NAME) -> None:
    """Return doc count and a sample document from the index."""
    count_resp = es.count(index=index_name)
    doc_count = count_resp["count"]

    sample_resp = es.search(index=index_name, body={"size": 1, "query": {"match_all": {}}})
    sample = sample_resp["hits"]["hits"][0]["_source"] if sample_resp["hits"]["hits"] else {}

    print(f"Total documents: {doc_count:,}")
    print("Sample document:")
    print(json.dumps(sample, indent=2))


def run(
    es: Elasticsearch,
    index_name: str = INDEX_NAME,
    count: int = 5000,
) -> dict:
    """Create index, generate and index documents, then verify."""
    print(f"Generating {count} synthetic e-commerce documents...")
    docs = generate_documents(count)

    create_index(es, index_name)

    print(f"Indexing {len(docs)} documents into '{index_name}'...")
    success, errors = index_documents(es, docs, index_name)
    print(f"  Indexed {success} documents ({errors} errors)")
    print("  Note: embeddings for product_description are generated asynchronously.")
    print("  Wait ~60s before running semantic queries to allow inference to complete.")

    verify_index(es, index_name)
