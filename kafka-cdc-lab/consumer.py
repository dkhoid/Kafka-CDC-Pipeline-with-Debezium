from kafka import KafkaConsumer
import json
from datetime import datetime


def format_timestamp(ts):
    """Convert epoch milliseconds to readable format"""
    if ts:
        return datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return 'N/A'


def process_message(msg):
    """Process and display CDC message"""
    try:
        data = json.loads(msg.value.decode('utf-8'))

        # Extract metadata
        operation = data.get('op', 'unknown')
        table = data.get('source', {}).get('table', 'unknown')
        ts = data.get('ts_ms', None)

        op_symbols = {
            'c': '➕ CREATE',
            'u': '🔄 UPDATE',
            'd': '🗑️  DELETE',
            'r': '📸 READ (snapshot)'
        }

        op_display = op_symbols.get(operation, f'❓ {operation}')

        print(f"\n{'=' * 80}")
        print(f"Operation: {op_display}")
        print(f"Table: {table}")
        print(f"Timestamp: {format_timestamp(ts)}")
        print(f"Topic: {msg.topic}")
        print(f"Partition: {msg.partition} | Offset: {msg.offset}")

        # Display before/after data
        if operation == 'c' or operation == 'r':
            # Create or Read - show 'after' data
            after = data.get('after', {})
            print(f"\n📄 Data:")
            for key, value in after.items():
                print(f"  {key}: {value}")

        elif operation == 'u':
            # Update - show before and after
            before = data.get('before', {})
            after = data.get('after', {})

            print(f"\n📄 Before:")
            for key, value in before.items():
                print(f"  {key}: {value}")

            print(f"\n📄 After:")
            for key, value in after.items():
                if before.get(key) != value:
                    print(f"  {key}: {value} ⬅️ CHANGED")
                else:
                    print(f"  {key}: {value}")

        elif operation == 'd':
            # Delete - show 'before' data
            before = data.get('before', {})
            print(f"\n📄 Deleted Data:")
            for key, value in before.items():
                print(f"  {key}: {value}")

        print(f"{'=' * 80}")

    except Exception as e:
        print(f"Error processing message: {e}")
        print(f"Raw message: {msg.value}")


def main():
    print("🎧 Starting Kafka CDC Consumer...")
    print("Listening for change events...\n")

    # Subscribe to all CDC topics
    topics = ['cdc.public.users', 'cdc.public.orders']

    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='cdc-consumer-group',
        value_deserializer=lambda x: x
    )

    print(f"✓ Connected to Kafka")
    print(f"✓ Subscribed to topics: {', '.join(topics)}\n")

    try:
        message_count = 0
        for message in consumer:
            message_count += 1
            process_message(message)

            if message_count % 10 == 0:
                print(f"\n📊 Total messages processed: {message_count}\n")

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping consumer...")
    finally:
        consumer.close()
        print("✓ Consumer closed")


if __name__ == "__main__":
    main()