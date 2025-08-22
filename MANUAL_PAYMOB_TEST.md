# Manual PayMob Integration Test Guide

## Prerequisites

1. **Start Django Server:**
   ```bash
   python manage.py runserver 8000
   ```

2. **Create Subscription Plans:**
   ```bash
   python manage.py create_subscription_plans
   ```

## Step-by-Step Test Commands

### Step 1: Register a Test User

```bash
curl -X POST "http://localhost:8000/api/accounts/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "username": "testuser",
    "password": "TestPassword123!",
    "password_confirm": "TestPassword123!"
  }'
```

**Expected Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "testuser@example.com",
    "username": "testuser"
  }
}
```

### Step 2: Login to Get JWT Token

```bash
curl -X POST "http://localhost:8000/api/accounts/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPassword123!"
  }'
```

**Expected Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "testuser@example.com",
    "username": "testuser"
  }
}
```

**⚠️ IMPORTANT:** Copy the `access` token for the next steps!

### Step 3: Get Available Subscription Plans

```bash
curl -X GET "http://localhost:8000/api/accounts/subscription-plans/" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "name": "Premium Monthly",
    "plan_type": "premium",
    "duration": "monthly",
    "price": "99.00",
    "currency": "EGP",
    "description": "Premium features for one month",
    "features": ["Verified badge", "Priority support"],
    "is_active": true
  }
]
```

**⚠️ IMPORTANT:** Note the `id` of the plan you want to test with!

### Step 4: Create Subscription (Success Test)

Replace `YOUR_ACCESS_TOKEN` with the token from Step 2 and `PLAN_ID` with the ID from Step 3:

```bash
curl -X POST "http://localhost:8000/api/accounts/create-subscription/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "subscription_plan_id": PLAN_ID
  }'
```

**Expected Response:**
```json
{
  "message": "Payment initiated successfully",
  "payment_id": 1,
  "iframe_url": "https://accept.paymob.com/api/acceptance/iframes/951380?payment_token=...",
  "order_id": 12345
}
```

**⚠️ IMPORTANT:** Note the `payment_id` and `order_id` for the next steps!

### Step 5: Simulate Successful PayMob Webhook

Replace `ORDER_ID` with the order ID from Step 4:

```bash
curl -X POST "http://localhost:8000/api/accounts/paymob-webhook/" \
  -H "Content-Type: application/json" \
  -H "X-PayMob-Signature: test_signature" \
  -d '{
    "id": 12345678,
    "success": true,
    "status": "success",
    "amount_cents": 9900,
    "currency": "EGP",
    "delivery_needed": false,
    "email": "testuser@example.com",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "",
    "integration_id": 5242071,
    "order": {
      "id": ORDER_ID
    }
  }'
```

**Expected Response:**
```json
{
  "status": "success"
}
```

### Step 6: Check Payment Status

Replace `PAYMENT_ID` with the payment ID from Step 4:

```bash
curl -X GET "http://localhost:8000/api/accounts/payment-status/PAYMENT_ID/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "amount": "99.00",
  "currency": "EGP",
  "status": "completed",
  "subscription_plan_details": {
    "id": 1,
    "name": "Premium Monthly",
    "plan_type": "premium"
  },
  "created_at": "2025-01-29T...",
  "completed_at": "2025-01-29T..."
}
```

### Step 7: Check User Subscription Status

```bash
curl -X GET "http://localhost:8000/api/accounts/subscription-status/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "plan": "premium",
  "is_active": true,
  "start_date": "2025-01-29T...",
  "end_date": "2025-02-28T...",
  "days_remaining": 30,
  "has_verified_badge": true
}
```

### Step 8: Test Failed Payment (Optional)

First, cancel the current subscription:

```bash
curl -X POST "http://localhost:8000/api/accounts/cancel-subscription/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Then create a new subscription and simulate a failed webhook:

```bash
# Create new subscription (repeat Step 4)
# Then simulate failed webhook with the new order_id:

curl -X POST "http://localhost:8000/api/accounts/paymob-webhook/" \
  -H "Content-Type: application/json" \
  -H "X-PayMob-Signature: test_signature" \
  -d '{
    "id": 87654321,
    "success": false,
    "status": "failed",
    "amount_cents": 9900,
    "currency": "EGP",
    "delivery_needed": false,
    "email": "testuser@example.com",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "",
    "integration_id": 5242071,
    "order": {
      "id": NEW_ORDER_ID
    }
  }'
```

**Expected Response:**
```json
{
  "status": "failed"
}
```

## Test Results Checklist

- [ ] ✅ User registration successful
- [ ] ✅ User login and JWT token received
- [ ] ✅ Subscription plans retrieved
- [ ] ✅ Payment created with PayMob
- [ ] ✅ Successful webhook processed
- [ ] ✅ Payment status shows "completed"
- [ ] ✅ User subscription is active
- [ ] ✅ Failed webhook processed correctly

## Real PayMob Testing

For actual PayMob testing with real cards:

### Success Card: `4987654321098769`
- Use this card number in PayMob's payment form
- Any CVV and future expiry date
- Should result in successful payment

### Failure Card: Any other card number
- Example: `4000000000000002`
- Should result in failed payment

## Troubleshooting

### Common Issues:

1. **"Invalid signature" error:**
   - Check if PAYMOB_HMAC_SECRET is correctly set
   - Verify webhook signature calculation

2. **"Payment not found" error:**
   - Ensure order_id in webhook matches the created payment
   - Check database for payment records

3. **"Authentication failed" error:**
   - Verify JWT token is valid and not expired
   - Check Authorization header format

4. **"Subscription plan not found" error:**
   - Run `python manage.py create_subscription_plans`
   - Check if plans exist in database

## Next Steps

After successful testing:
1. Configure webhook URL in PayMob dashboard
2. Test with real PayMob environment
3. Set up production environment variables
4. Implement proper error handling and logging
