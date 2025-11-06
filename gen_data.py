from faker import Faker
import pandas as pd
import numpy as np
import random
from datetime import timedelta

faker = Faker()

def generate_brands(n):
    return pd.DataFrame({
        'brand_id': np.arange(1, n+1),
        'brand_name': [faker.random_element(elements=(
            "Samsung","Apple","Xiaomi","Huawei","Sony","LG","Dell","HP","Lenovo","Asus",
            "Acer","Microsoft","Google","Panasonic","Bose","JBL","Canon","Nikon","Philips","Garmin"
        )) for _ in range(n)],
        'country': [faker.country() for _ in range(n)],
        'created_at': [faker.date_time_this_decade() for _ in range(n)],
    })

def generate_categories():
    main_categories = ["Electronics","Fashion","Home Appliances","Sports & Outdoors","Books & Media"]
    sub_to_main = {
        "Smartphones":"Electronics",
        "Laptops":"Electronics",
        "Wearables & Smart Watches":"Fashion",
        "Small Kitchen Appliances":"Home Appliances",
        "Gaming Consoles & Accessories":"Electronics"
    }
    rows = []
    cat_id = 1
    for mc in main_categories:
        rows.append({
            "category_id": cat_id,
            "category_name": mc,
            "parent_category_id": None,
            "level": 1,
            "created_at": faker.date_time_this_year()
        })
        cat_id += 1
    for sub, parent in sub_to_main.items():
        parent_id = main_categories.index(parent)
        rows.append({
            "category_id": cat_id,
            "category_name": sub,
            "parent_category_id": parent_id,
            "level": 2,
            "created_at": faker.date_time_this_year()
        })
        cat_id += 1
    return pd.DataFrame(rows)

def generate_sellers(n):
    seller_type_choices = [
        "official_store", "authorized_distributor", "brand_partner", "flagship_store",
        "premium_retailer", "certified_reseller", "local_seller", "overseas_seller",
        "marketplace_merchant", "wholesaler", "direct_manufacturer", "franchise_store",
        "outlet_store", "handmade_artisan", "dropship_supplier", "print_on_demand_seller",
        "liquidation_surplus_store"
    ]
    return pd.DataFrame({
        'seller_id': np.arange(1, n+1),
        'seller_name': [faker.company() for _ in range(n)],
        'join_date': [faker.date_between(start_date='-1y', end_date='today') for _ in range(n)],
        'seller_type': [random.choice(seller_type_choices) for _ in range(n)],
        'rating': [round(random.uniform(3.0,5.0),1) for _ in range(n)],
        'country': ['Vietnam'] * n
    })

def generate_products(n, categories_df, brands_df, sellers_df):
    product_ids = np.arange(1, n+1)
    cat_ids = categories_df['category_id'].tolist()
    brand_ids = brands_df['brand_id'].tolist()
    seller_ids = sellers_df['seller_id'].tolist()
    prices = np.round(np.random.uniform(100000, 50000000, size=n), 2)
    discount_factors = np.random.uniform(0.7, 1.0, size=n)
    discount_prices = np.round(prices * discount_factors, 2)
    return pd.DataFrame({
        'product_id': product_ids,
        'product_name': [faker.catch_phrase() for _ in range(n)],
        'category_id': np.random.choice(cat_ids, size=n),
        'brand_id': np.random.choice(brand_ids, size=n),
        'seller_id': np.random.choice(seller_ids, size=n),
        'price': prices,
        'discount_price': discount_prices,
        'stock_qty': np.random.randint(0, 501, size=n),
        'rating': np.round(np.random.uniform(3.0,5.0, size=n),1),
        'created_at': [faker.date_between(start_date='-3y', end_date='today') for _ in range(n)],
        'is_active': [faker.boolean(chance_of_getting_true=85) for _ in range(n)]
    })

def generate_orders(n, sellers_df):
    status_choices = ["PAID", "CANCELLED", "RETURNED"]
    weights = [0.8, 0.1, 0.1]
    seller_ids = sellers_df['seller_id'].tolist()
    return pd.DataFrame({
        'order_id': np.arange(1, n+1),
        'order_date': [faker.date_time_this_year() for _ in range(n)],
        'seller_id': np.random.choice(seller_ids, size=n),
        'status': random.choices(status_choices, weights=weights, k=n),
        'total_amount': np.round(np.random.uniform(50000, 50000000, size=n),2),
        'created_at': [faker.date_time_this_year() for _ in range(n)]
    })

def generate_order_items(orders_df, products_df):
    records = []
    prod_df = products_df.set_index('product_id')
    for _, order in orders_df.iterrows():
        num_items = random.randint(1,5)
        chosen_ids = products_df.sample(num_items)['product_id'].tolist()
        for pid in chosen_ids:
            quantity = random.randint(1,5)
            unit_price = float(prod_df.loc[pid,'discount_price'])
            subtotal = round(quantity * unit_price,2)
            records.append({
                'order_item_id': None,  # will set after
                'order_id': order['order_id'],
                'product_id': pid,
                'quantity': quantity,
                'unit_price': unit_price,
                'subtotal': subtotal
            })
    oi = pd.DataFrame(records)
    oi = oi.reset_index(drop=True)
    oi['order_item_id'] = oi.index + 1
    return oi

def generate_promotions(n):
    promotion_types = [
        "product","category","seller","flash_sale","voucher","clearance","bundle_offer","seasonal_campaign"
    ]
    discount_types = ["percentage","fixed_amount"]
    rows = []
    for pid in range(1, n+1):
        d_type = random.choice(discount_types)
        value = random.choice([5,10,15,20,25,30] if d_type=="percentage" else [20000,50000,100000,200000,300000])
        start = faker.date_between(start_date='-6m', end_date='today')
        end = start + timedelta(days=random.randint(3,30))
        rows.append({
            "promotion_id": pid,
            "promotion_name": f"{faker.catch_phrase()} Promo",
            "promotion_type": random.choice(promotion_types),
            "discount_type": d_type,
            "discount_value": value,
            "start_date": start,
            "end_date": end
        })
    return pd.DataFrame(rows)

def generate_promotion_products(promotions_df, products_df, min_products=3, max_products=10):
    records = []
    promo_ids = promotions_df['promotion_id'].tolist()
    prod_ids = products_df['product_id'].tolist()
    pid_ctr = 1
    for promo_id in promo_ids:
        num_links = random.randint(min_products, max_products)
        selected = random.sample(prod_ids, num_links)
        for pid in selected:
            records.append({
                "promo_product_id": pid_ctr,
                "promotion_id": promo_id,
                "product_id": pid,
                "created_at": faker.date_time_this_year()
            })
            pid_ctr += 1
    return pd.DataFrame(records)


# —————————————————————————————
# Execution & export
brands_df = generate_brands(20)
categories_df = generate_categories()
sellers_df = generate_sellers(25)
products_df = generate_products(200, categories_df, brands_df, sellers_df)
orders_df = generate_orders(100000, sellers_df)
order_items_df = generate_order_items(orders_df, products_df)
promotions_df = generate_promotions(10)
promotion_products_df = generate_promotion_products(promotions_df, products_df)

# Export CSV
brands_df.to_csv("brands_table.csv", index=False)
categories_df.to_csv("categories_table.csv", index=False)
sellers_df.to_csv("sellers_table.csv", index=False)
products_df.to_csv("products_table.csv", index=False)
orders_df.to_csv("orders_table.csv", index=False)
order_items_df.to_csv("order_items_table.csv", index=False)
promotions_df.to_csv("promotions_table.csv", index=False)
promotion_products_df.to_csv("promotion_products_table.csv", index=False)