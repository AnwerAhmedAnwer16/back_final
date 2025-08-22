#!/bin/bash

# PayMob Integration Test Script
# This script tests the complete PayMob payment flow

BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/accounts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test data
TEST_EMAIL="testuser@example.com"
TEST_PASSWORD="TestPassword123!"
TEST_USERNAME="testuser"

echo -e "${BLUE}=== PayMob Integration Test Suite ===${NC}"
echo "Base URL: $BASE_URL"
echo "API Base: $API_BASE"
echo ""

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

# Function to extract JSON value
extract_json_value() {
    echo $1 | grep -o "\"$2\":[^,}]*" | cut -d':' -f2 | tr -d '"' | tr -d ' '
}

echo -e "${YELLOW}Step 1: Setup - Creating subscription plans${NC}"
python manage.py create_subscription_plans
print_result $? "Created subscription plans"

echo ""
echo -e "${YELLOW}Step 2: User Registration${NC}"

# Register a test user
REGISTER_RESPONSE=$(curl -s -X POST "${API_BASE}/register/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"username\": \"$TEST_USERNAME\",
    \"password\": \"$TEST_PASSWORD\",
    \"password_confirm\": \"$TEST_PASSWORD\"
  }")

echo "Registration Response: $REGISTER_RESPONSE"
print_result $? "User registration"

echo ""
echo -e "${YELLOW}Step 3: User Login${NC}"

# Login to get JWT token
LOGIN_RESPONSE=$(curl -s -X POST "${API_BASE}/login/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

echo "Login Response: $LOGIN_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(extract_json_value "$LOGIN_RESPONSE" "access")
if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}Failed to get access token${NC}"
    exit 1
fi

print_result 0 "User login and token extraction"
echo "Access Token: ${ACCESS_TOKEN:0:50}..."

echo ""
echo -e "${YELLOW}Step 4: Get Subscription Plans${NC}"

# Get available subscription plans
PLANS_RESPONSE=$(curl -s -X GET "${API_BASE}/subscription-plans/" \
  -H "Content-Type: application/json")

echo "Subscription Plans: $PLANS_RESPONSE"
print_result $? "Retrieved subscription plans"

# Extract first plan ID
PLAN_ID=$(echo "$PLANS_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
if [ -z "$PLAN_ID" ]; then
    echo -e "${RED}No subscription plans found${NC}"
    exit 1
fi

echo "Using Plan ID: $PLAN_ID"

echo ""
echo -e "${YELLOW}Step 5: Test Successful Payment Flow${NC}"

# Create subscription (this should return PayMob payment URL)
SUBSCRIPTION_RESPONSE=$(curl -s -X POST "${API_BASE}/create-subscription/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"subscription_plan_id\": $PLAN_ID
  }")

echo "Subscription Creation Response: $SUBSCRIPTION_RESPONSE"
print_result $? "Subscription creation"

# Extract payment details
PAYMENT_ID=$(extract_json_value "$SUBSCRIPTION_RESPONSE" "payment_id")
ORDER_ID=$(extract_json_value "$SUBSCRIPTION_RESPONSE" "order_id")
IFRAME_URL=$(extract_json_value "$SUBSCRIPTION_RESPONSE" "iframe_url")

echo "Payment ID: $PAYMENT_ID"
echo "Order ID: $ORDER_ID"
echo "iFrame URL: $IFRAME_URL"

if [ -z "$PAYMENT_ID" ] || [ -z "$ORDER_ID" ]; then
    echo -e "${RED}Failed to create payment${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 6: Simulate Successful PayMob Webhook${NC}"

# Simulate successful payment webhook
SUCCESS_WEBHOOK_DATA='{
  "id": 12345678,
  "success": true,
  "status": "success",
  "amount_cents": 9900,
  "currency": "EGP",
  "delivery_needed": false,
  "email": "'$TEST_EMAIL'",
  "first_name": "Test",
  "last_name": "User",
  "phone_number": "",
  "integration_id": 123456,
  "order": {
    "id": '$ORDER_ID'
  }
}'

# Calculate HMAC signature (simplified - in real scenario this would be calculated properly)
HMAC_SIGNATURE="dummy_signature_for_testing"

WEBHOOK_RESPONSE=$(curl -s -X POST "${API_BASE}/paymob-webhook/" \
  -H "Content-Type: application/json" \
  -H "X-PayMob-Signature: $HMAC_SIGNATURE" \
  -d "$SUCCESS_WEBHOOK_DATA")

echo "Webhook Response: $WEBHOOK_RESPONSE"
print_result $? "Successful payment webhook"

echo ""
echo -e "${YELLOW}Step 7: Check Payment Status${NC}"

# Check payment status
PAYMENT_STATUS_RESPONSE=$(curl -s -X GET "${API_BASE}/payment-status/$PAYMENT_ID/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Payment Status: $PAYMENT_STATUS_RESPONSE"
print_result $? "Payment status check"

echo ""
echo -e "${YELLOW}Step 8: Check User Subscription Status${NC}"

# Check user subscription status
SUBSCRIPTION_STATUS_RESPONSE=$(curl -s -X GET "${API_BASE}/subscription-status/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Subscription Status: $SUBSCRIPTION_STATUS_RESPONSE"
print_result $? "Subscription status check"

echo ""
echo -e "${YELLOW}Step 9: Test Failed Payment Flow${NC}"

# Create another subscription for failed payment test
FAILED_SUBSCRIPTION_RESPONSE=$(curl -s -X POST "${API_BASE}/create-subscription/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"subscription_plan_id\": $PLAN_ID
  }")

echo "Failed Payment Subscription Response: $FAILED_SUBSCRIPTION_RESPONSE"

# Extract payment details for failed payment
FAILED_PAYMENT_ID=$(extract_json_value "$FAILED_SUBSCRIPTION_RESPONSE" "payment_id")
FAILED_ORDER_ID=$(extract_json_value "$FAILED_SUBSCRIPTION_RESPONSE" "order_id")

if [ ! -z "$FAILED_PAYMENT_ID" ] && [ ! -z "$FAILED_ORDER_ID" ]; then
    echo ""
    echo -e "${YELLOW}Step 10: Simulate Failed PayMob Webhook${NC}"
    
    # Simulate failed payment webhook
    FAILED_WEBHOOK_DATA='{
      "id": 87654321,
      "success": false,
      "status": "failed",
      "amount_cents": 9900,
      "currency": "EGP",
      "delivery_needed": false,
      "email": "'$TEST_EMAIL'",
      "first_name": "Test",
      "last_name": "User",
      "phone_number": "",
      "integration_id": 123456,
      "order": {
        "id": '$FAILED_ORDER_ID'
      }
    }'
    
    FAILED_WEBHOOK_RESPONSE=$(curl -s -X POST "${API_BASE}/paymob-webhook/" \
      -H "Content-Type: application/json" \
      -H "X-PayMob-Signature: $HMAC_SIGNATURE" \
      -d "$FAILED_WEBHOOK_DATA")
    
    echo "Failed Webhook Response: $FAILED_WEBHOOK_RESPONSE"
    print_result $? "Failed payment webhook"
    
    # Check failed payment status
    FAILED_PAYMENT_STATUS_RESPONSE=$(curl -s -X GET "${API_BASE}/payment-status/$FAILED_PAYMENT_ID/" \
      -H "Authorization: Bearer $ACCESS_TOKEN")
    
    echo "Failed Payment Status: $FAILED_PAYMENT_STATUS_RESPONSE"
    print_result $? "Failed payment status check"
fi

echo ""
echo -e "${YELLOW}Step 11: Test Payment History${NC}"

# Get payment history
PAYMENT_HISTORY_RESPONSE=$(curl -s -X GET "${API_BASE}/payment-history/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Payment History: $PAYMENT_HISTORY_RESPONSE"
print_result $? "Payment history retrieval"

echo ""
echo -e "${GREEN}=== Test Suite Completed ===${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "- Created subscription plans"
echo "- Registered and authenticated user"
echo "- Retrieved subscription plans"
echo "- Created payment with PayMob"
echo "- Simulated successful webhook"
echo "- Simulated failed webhook"
echo "- Checked payment and subscription status"
echo "- Retrieved payment history"
echo ""
echo -e "${YELLOW}Note: This test uses simulated webhook data.${NC}"
echo -e "${YELLOW}For real testing, use PayMob's test environment with actual card numbers:${NC}"
echo -e "${YELLOW}Success: 4987654321098769${NC}"
echo -e "${YELLOW}Failure: Any other card number${NC}"
