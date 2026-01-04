import psycopg2
import time
import random
from datetime import datetime
from faker import Faker

fake = Faker()


# Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="testdb",
        user="postgres",
        password="postgres"
    )


def insert_user(cursor):
    """Insert a new user"""
    username = fake.user_name()
    email = fake.email()
    cursor.execute(
        "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id",
        (username, email)
    )
    user_id = cursor.fetchone()[0]
    print(f"✓ Inserted user: {username} (ID: {user_id})")
    return user_id


def insert_order(cursor):
    """Insert a new order"""
    cursor.execute("SELECT id FROM users ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    if not result:
        return

    user_id = result[0]
    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'Webcam']
    product = random.choice(products)
    quantity = random.randint(1, 5)
    price = round(random.uniform(10, 1000), 2)

    cursor.execute(
        """INSERT INTO orders (user_id, product_name, quantity, price, status)
           VALUES (%s, %s, %s, %s, %s) RETURNING id""",
        (user_id, product, quantity, price, 'pending')
    )
    order_id = cursor.fetchone()[0]
    print(f"✓ Inserted order: {product} x{quantity} (ID: {order_id})")
    return order_id


def update_order(cursor):
    """Update an existing order status"""
    cursor.execute("SELECT id FROM orders WHERE status = 'pending' ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    if not result:
        return

    order_id = result[0]
    new_status = random.choice(['processing', 'shipped', 'completed'])
    cursor.execute(
        "UPDATE orders SET status = %s, updated_at = %s WHERE id = %s",
        (new_status, datetime.now(), order_id)
    )
    print(f"✓ Updated order {order_id} to status: {new_status}")


def delete_order(cursor):
    """Delete a completed order"""
    cursor.execute("SELECT id FROM orders WHERE status = 'completed' ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    if not result:
        return

    order_id = result[0]
    cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    print(f"✗ Deleted order {order_id}")


def main():
    print("🚀 Starting continuous data generator...")
    print("Press Ctrl+C to stop\n")

    conn = get_db_connection()
    cursor = conn.cursor()

    operations = [
        ('INSERT USER', insert_user, 0.2),
        ('INSERT ORDER', insert_order, 0.5),
        ('UPDATE ORDER', update_order, 0.2),
        ('DELETE ORDER', delete_order, 0.1)
    ]

    try:
        counter = 0
        while True:
            counter += 1

            # Choose random operation based on weights
            op_name, operation, _ = random.choices(
                operations,
                weights=[op[2] for op in operations]
            )[0]

            try:
                operation(cursor)
                conn.commit()
            except Exception as e:
                print(f"✗ Error in {op_name}: {e}")
                conn.rollback()

            # Random delay between operations
            delay = random.uniform(0.5, 2.0)
            time.sleep(delay)

            if counter % 10 == 0:
                print(f"\n--- {counter} operations completed ---\n")

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping data generator...")
    finally:
        cursor.close()
        conn.close()
        print("✓ Database connection closed")


if __name__ == "__main__":
    main()