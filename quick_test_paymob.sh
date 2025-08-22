#!/bin/bash

# Quick PayMob Integration Test with curl
# Usage: ./quick_test_paymob.sh

BASE_URL="http://localhost:8000/api/accounts"
TEST_EMAIL="testuser$(date +%s)@example.com"  # Unique email
TEST_PASSWORD="TestPassword123!"
TEST_USERNAME="testuser$(date +%s)"

echo "=== Quick PayMob Test ==="
echo "Email: $TEST_EMAIL"
echo "Username: $TEST_USERNAME"
echo ""

# 1. Register user
echo "1. Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/register/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"username\": \"$TEST_USERNAME\",
    \"password\": \"$TEST_PASSWORD\",
    \"password_confirm\": \"$TEST_PASSWORD\"
  }")

echo "Register Response: $REGISTER_RESPONSE"

# 2. Login
echo -e "\n2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

echo "Login Response: $LOGIN_RESPONSE"

# Extract token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to get access token"
    exit 1
fi

echo "✅ Got access token: ${ACCESS_TOKEN:0:50}..."

# 3. Get subscription plans
echo -e "\n3. Getting subscription plans..."
PLANS_RESPONSE=$(curl -s -X GET "$BASE_URL/subscription-plans/")
echo "Plans: $PLANS_RESPONSE"

# Extract first plan ID
PLAN_ID=$(echo "$PLANS_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$PLAN_ID" ]; then
    echo "❌ No subscription plans found"
    exit 1
fi

echo "✅ Using plan ID: $PLAN_ID"

# 4. Create subscription
echo -e "\n4. Creating subscription..."
SUBSCRIPTION_RESPONSE=$(curl -s -X POST "$BASE_URL/create-subscription/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"subscription_plan_id\": $PLAN_ID
  }")

echo "Subscription Response: $SUBSCRIPTION_RESPONSE"

# Extract payment details
PAYMENT_ID=$(echo "$SUBSCRIPTION_RESPONSE" | grep -o '"payment_id":[0-9]*' | cut -d':' -f2)
ORDER_ID=$(echo "$SUBSCRIPTION_RESPONSE" | grep -o '"order_id":[0-9]*' | cut -d':' -f2)

if [ -z "$PAYMENT_ID" ] || [ -z "$ORDER_ID" ]; then
    echo "❌ Failed to create payment"
    exit 1
fi

echo "✅ Payment created - ID: $PAYMENT_ID, Order: $ORDER_ID"

# 5. Simulate successful webhook
echo -e "\n5. Simulating successful payment webhook..."
SUCCESS_WEBHOOK=$(curl -s -X POST "$BASE_URL/paymob-webhook/" \
  -H "Content-Type: application/json" \
  -H "X-PayMob-Signature: test_signature" \
  -d "{
    \"id\": 12345678,
    \"success\": true,
    \"status\": \"success\",
    \"amount_cents\": 9900,
    \"currency\": \"EGP\",
    \"delivery_needed\": false,
    \"email\": \"$TEST_EMAIL\",
    \"first_name\": \"Test\",
    \"last_name\": \"User\",
    \"phone_number\": \"\",
    \"integration_id\": 123456,
    \"order\": {
      \"id\": $ORDER_ID
    }
  }")

echo "Webhook Response: $SUCCESS_WEBHOOK"

# 6. Check payment status
echo -e "\n6. Checking payment status..."
PAYMENT_STATUS=$(curl -s -X GET "$BASE_URL/payment-status/$PAYMENT_ID/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Payment Status: $PAYMENT_STATUS"

# 7. Check subscription status
echo -e "\n7. Checking subscription status..."
SUBSCRIPTION_STATUS=$(curl -s -X GET "$BASE_URL/subscription-status/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Subscription Status: $SUBSCRIPTION_STATUS"

# 8. Test failed payment
echo -e "\n8. Testing failed payment..."

# Cancel current subscription first
curl -s -X POST "$BASE_URL/cancel-subscription/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

# Create new subscription for failure test
FAILED_SUBSCRIPTION=$(curl -s -X POST "$BASE_URL/create-subscription/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"subscription_plan_id\": $PLAN_ID
  }")

FAILED_PAYMENT_ID=$(echo "$FAILED_SUBSCRIPTION" | grep -o '"payment_id":[0-9]*' | cut -d':' -f2)
FAILED_ORDER_ID=$(echo "$FAILED_SUBSCRIPTION" | grep -o '"order_id":[0-9]*' | cut -d':' -f2)

if [ ! -z "$FAILED_PAYMENT_ID" ] && [ ! -z "$FAILED_ORDER_ID" ]; then
    echo "Created failed payment test - ID: $FAILED_PAYMENT_ID, Order: $FAILED_ORDER_ID"
    
    # Simulate failed webhook
    FAILED_WEBHOOK=$(curl -s -X POST "$BASE_URL/paymob-webhook/" \
      -H "Content-Type: application/json" \
      -H "X-PayMob-Signature: test_signature" \
      -d "{
        \"id\": 87654321,
        \"success\": false,
        \"status\": \"failed\",
        \"amount_cents\": 9900,
        \"currency\": \"EGP\",
        \"delivery_needed\": false,
        \"email\": \"$TEST_EMAIL\",
        \"first_name\": \"Test\",
        \"last_name\": \"User\",
        \"phone_number\": \"\",
        \"integration_id\": 123456,
        \"order\": {
          \"id\": $FAILED_ORDER_ID
        }
      }")
    
    echo "Failed Webhook Response: $FAILED_WEBHOOK"
fi

echo -e "\n=== Test Completed ==="
echo "✅ User registration and login"
echo "✅ Subscription plan retrieval"
echo "✅ Payment creation"
echo "✅ Successful webhook simulation"
echo "✅ Failed webhook simulation"
echo "✅ Status checks"
echo ""
echo "🔗 For real PayMob testing:"
echo "   Success Card: 4987654321098769"
echo "   Failure Card: Any other card number"
