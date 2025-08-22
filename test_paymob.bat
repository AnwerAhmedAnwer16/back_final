@echo off
echo ===== PayMob Integration Test =====
echo.

set BASE_URL=http://localhost:8000/api/accounts
set TEST_EMAIL=testuser@example.com
set TEST_PASSWORD=TestPassword123!
set TEST_USERNAME=testuser

echo Step 1: Register User
curl -X POST "%BASE_URL%/register/" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"%TEST_EMAIL%\", \"username\": \"%TEST_USERNAME%\", \"password\": \"%TEST_PASSWORD%\", \"password_confirm\": \"%TEST_PASSWORD%\"}"

echo.
echo.
echo Step 2: Login User
curl -X POST "%BASE_URL%/login/" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"%TEST_EMAIL%\", \"password\": \"%TEST_PASSWORD%\"}"

echo.
echo.
echo Step 3: Get Subscription Plans
curl -X GET "%BASE_URL%/subscription-plans/" ^
  -H "Content-Type: application/json"

echo.
echo.
echo ===== Manual Steps Required =====
echo 1. Copy the 'access' token from Step 2
echo 2. Copy the 'id' from a subscription plan in Step 3
echo 3. Run the following commands manually:
echo.
echo Create Subscription:
echo curl -X POST "%BASE_URL%/create-subscription/" ^
echo   -H "Content-Type: application/json" ^
echo   -H "Authorization: Bearer YOUR_ACCESS_TOKEN" ^
echo   -d "{\"subscription_plan_id\": PLAN_ID}"
echo.
echo Simulate Success Webhook:
echo curl -X POST "%BASE_URL%/paymob-webhook/" ^
echo   -H "Content-Type: application/json" ^
echo   -H "X-PayMob-Signature: test_signature" ^
echo   -d "{\"id\": 12345678, \"success\": true, \"status\": \"success\", \"amount_cents\": 9900, \"currency\": \"EGP\", \"delivery_needed\": false, \"email\": \"%TEST_EMAIL%\", \"first_name\": \"Test\", \"last_name\": \"User\", \"phone_number\": \"\", \"integration_id\": 5242071, \"order\": {\"id\": ORDER_ID}}"
echo.
echo Check Payment Status:
echo curl -X GET "%BASE_URL%/payment-status/PAYMENT_ID/" ^
echo   -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
echo.
echo Check Subscription Status:
echo curl -X GET "%BASE_URL%/subscription-status/" ^
echo   -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
echo.
echo ===== Test Complete =====
pause
