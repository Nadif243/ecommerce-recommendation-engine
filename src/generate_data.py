import random
import sqlite3
from db import get_db_connection, init_db

# Event weights for implicit feedback
EVENT_WEIGHTS = {
    "view": 1.0,
    "cart": 3.0,
    "buy": 5.0
}

def generate_seed_data(num_users=100, num_items=50, num_events=2000):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM events")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM items")
    cursor.execute("DELETE FROM recommendations")

    # Seed Users
    users = [i for i in range(1, num_users + 1)]
    cursor.executemany("INSERT INTO users (user_id) VALUES (?)", [(u,) for u in users])

    # Seed Items with categories
    categories = ["Electronics", "Apparel"]
    items = []
    for item_id in range(1, num_items + 1):
        category = "Electronics" if item_id <= (num_items // 2) else "Apparel"
        items.append((item_id, category))
    cursor.executemany("INSERT INTO items (item_id, category) VALUES (?, ?)", items)

    # Seed Non-Random Event Stream
    # Users 1-50 prefer Electronics (Items 1-25)
    # Users 51-100 prefer Apparel (Items 26-50)
    events = []
    event_types = ["view", "cart", "buy"]
    event_probabilities = [0.6, 0.25, 0.15]  # Views are most common, buys are rare

    for _ in range(num_events):
        user_id = random.choice(users)

        # 80% chance user picks from preferred cluster, 20% random noise
        if random.random() < 0.8:
            if user_id <= (num_users // 2):
                item_id = random.randint(1, num_items // 2)  # Electronics
            else:
                item_id = random.randint((num_items // 2) + 1, num_items)  # Apparel
        else:
            item_id = random.randint(1, num_items)

        event_type = random.choices(event_types, weights=event_probabilities)[0]
        weight = EVENT_WEIGHTS[event_type]
        events.append((user_id, item_id, event_type, weight))

    cursor.executemany("""
        INSERT INTO events (user_id, item_id, event_type, weight)
        VALUES (?, ?, ?, ?)
    """, events)

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Generated {num_users} users, {num_items} items, and {num_events} interaction events.")

if __name__ == "__main__":
    generate_seed_data()
