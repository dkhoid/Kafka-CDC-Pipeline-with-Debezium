#!/bin/bash

echo "🚀 Kafka CDC Lab Setup Script"
echo "=============================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Start all services
echo -e "\n${YELLOW}Step 1: Starting Docker services...${NC}"
docker-compose up -d

echo -e "${GREEN}✓ Services started${NC}"
echo "Waiting for services to be ready (30 seconds)..."
sleep 30

# Step 2: Check service health
echo -e "\n${YELLOW}Step 2: Checking service health...${NC}"

echo "Checking Kafka..."
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Kafka is ready${NC}"
else
    echo -e "${RED}✗ Kafka is not ready${NC}"
fi

echo "Checking PostgreSQL..."
docker exec postgres psql -U postgres -d testdb -c "SELECT 1" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not ready${NC}"
fi

echo "Checking Kafka Connect..."
curl -s http://localhost:8083/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Kafka Connect is ready${NC}"
else
    echo -e "${RED}✗ Kafka Connect is not ready${NC}"
    echo "Waiting additional 20 seconds..."
    sleep 20
fi

# Step 3: Deploy Debezium Connector
echo -e "\n${YELLOW}Step 3: Deploying Debezium PostgreSQL Connector...${NC}"

curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" \
  localhost:8083/connectors/ \
  -d @debezium-connector.json

sleep 5

# Check connector status
echo -e "\n${YELLOW}Checking connector status...${NC}"
curl -s http://localhost:8083/connectors/postgres-connector/status | python3 -m json.tool

echo -e "\n${GREEN}✓ Setup complete!${NC}"

# Step 4: Display access information
echo -e "\n${YELLOW}=============================="
echo "Access Information"
echo -e "==============================${NC}"
echo "Kafka UI:          http://localhost:8080"
echo "Kafka Connect:     http://localhost:8083"
echo "Schema Registry:   http://localhost:8081"
echo "PostgreSQL:        localhost:5432 (user: postgres, pass: postgres)"
echo ""

echo -e "${YELLOW}Available Kafka Topics:${NC}"
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

echo -e "\n${YELLOW}=============================="
echo "Next Steps"
echo -e "==============================${NC}"
echo "1. Install Python dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "2. Start the data generator:"
echo "   python data_generator.py"
echo ""
echo "3. In another terminal, start the consumer:"
echo "   python consumer.py"
echo ""
echo "4. Monitor in Kafka UI:"
echo "   Open http://localhost:8080 in your browser"
echo ""

echo -e "${GREEN}Happy streaming! 🎉${NC}"