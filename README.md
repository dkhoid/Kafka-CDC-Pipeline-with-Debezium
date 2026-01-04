# Kafka CDC Lab - Quick Start Guide

## 📋 Prerequisites

- Docker & Docker Compose installed
- Python 3.8+ installed
- At least 4GB RAM available

## 🚀 Quick Start

### 1. Setup Project Structure

```bash
mkdir kafka-cdc-lab
cd kafka-cdc-lab

# Create necessary files (copy from artifacts)
touch docker-compose.yml
touch init.sql
touch debezium-connector.json
touch data_generator.py
touch consumer.py
touch requirements.txt
touch setup.sh

# Make setup script executable
chmod +x setup.sh
```

### 2. Start Infrastructure

```bash
# Start all services
docker-compose up -d

# Wait for services (30-60 seconds)
docker-compose ps
```

### 3. Deploy Debezium Connector

```bash
# Deploy connector
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" \
  localhost:8083/connectors/ \
  -d @debezium-connector.json

# Check connector status
curl http://localhost:8083/connectors/postgres-connector/status | jq
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Lab

**Terminal 1 - Data Generator:**
```bash
python data_generator.py
```

**Terminal 2 - Consumer:**
```bash
python consumer.py
```

**Terminal 3 - Monitor:**
```bash
# Open Kafka UI
open http://localhost:8080
```

## 🎯 What You'll See

### Data Generator Output:
```
✓ Inserted user: john_doe (ID: 5)
✓ Inserted order: Laptop x1 (ID: 10)
✓ Updated order 8 to status: shipped
✗ Deleted order 3
```

### Consumer Output:
```
================================================================================
Operation: ➕ CREATE
Table: orders
Timestamp: 2026-01-04 15:30:45

📄 Data:
  id: 10
  user_id: 5
  product_name: Laptop
  quantity: 1
  price: 999.99
  status: pending
================================================================================
```

## 📊 Monitoring

### Kafka UI (http://localhost:8080)
- View topics: `cdc.public.users`, `cdc.public.orders`
- Monitor consumer lag
- Inspect messages

### Check Topics
```bash
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

### Check Messages
```bash
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic cdc.public.orders \
  --from-beginning \
  --max-messages 5
```

## 🧪 Testing Scenarios

### 1. Test INSERT
```sql
docker exec -it postgres psql -U postgres-cdc -d testdb
INSERT INTO users (username, email) VALUES ('test_user', 'test@example.com');
```

### 2. Test UPDATE
```sql
UPDATE orders SET status = 'completed' WHERE id = 1;
```

### 3. Test DELETE
```sql
DELETE FROM orders WHERE id = 2;
```

### 4. Verify in Consumer
Check that your consumer shows the corresponding CDC events.

## 🔍 Troubleshooting

### Services not starting?
```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

### Connector not working?
```bash
# Check connector status
curl http://localhost:8083/connectors/postgres-connector/status

# Delete and recreate
curl -X DELETE http://localhost:8083/connectors/postgres-connector
curl -X POST -H "Content-Type:application/json" \
  --data @debezium-connector.json \
  http://localhost:8083/connectors
```

### No messages in Kafka?
```bash
# Check if topics exist
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Check PostgreSQL replication
docker exec postgres psql -U postgres -d testdb \
  -c "SELECT * FROM pg_replication_slots;"
```

### Consumer not receiving messages?
```bash
# Check consumer group
docker exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group cdc-consumer-group
```

## 🛑 Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Remove everything including images
docker-compose down -v --rmi all
```

## 📚 Understanding CDC Events

### Event Structure
```json
{
  "before": { /* previous values for UPDATE/DELETE */ },
  "after": { /* new values for CREATE/UPDATE */ },
  "source": {
    "db": "testdb",
    "table": "orders",
    "ts_ms": 1704398445123
  },
  "op": "c",  // c=create, u=update, d=delete, r=read
  "ts_ms": 1704398445456
}
```

### Operations
- **c** (create): New record inserted
- **u** (update): Existing record modified
- **d** (delete): Record deleted
- **r** (read): Initial snapshot

## 🎓 Learning Objectives

✅ Deploy Kafka cluster with Docker
✅ Configure PostgreSQL for CDC
✅ Setup Debezium connector
✅ Stream database changes to Kafka
✅ Consume and process CDC events
✅ Monitor data pipeline

## 📖 Next Steps

1. Add more tables to capture
2. Implement data transformations
3. Add error handling and retry logic
4. Setup alerting for pipeline issues
5. Explore Kafka Streams for processing
6. Implement downstream applications

## 🆘 Need Help?

- Check Kafka UI: http://localhost:8080
- View logs: `docker-compose logs -f [service-name]`
- Debezium docs: https://debezium.io/documentation/
- Kafka docs: https://kafka.apache.org/documentation/

---

**Happy Learning! 🚀**