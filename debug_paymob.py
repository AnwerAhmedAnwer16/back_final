#!/usr/bin/env python3
"""
Debug PayMob API - Simple version
"""

from accounts.services import PayMobService
from django.conf import settings
import requests
import json

def debug_paymob():
    print("🔍 Debugging PayMob API Integration")
    print("="*50)
    
    # Check configuration
    print("1. PayMob Configuration:")
    print(f"   API Key: {settings.PAYMOB_API_KEY[:20]}...")
    print(f"   Integration ID: {settings.PAYMOB_INTEGRATION_ID}")
    print(f"   Base URL: {settings.PAYMOB_BASE_URL}")
    
    # Test authentication manually
    print("\n2. Testing Authentication:")
    auth_url = f"{settings.PAYMOB_BASE_URL}/auth/tokens"
    auth_data = {"api_key": settings.PAYMOB_API_KEY}
    
    try:
        response = requests.post(auth_url, json=auth_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            auth_token = result.get('token')
            print(f"   ✅ Auth successful: {auth_token[:30]}...")
            
            # Test order creation
            print("\n3. Testing Order Creation:")
            order_url = f"{settings.PAYMOB_BASE_URL}/ecommerce/orders"
            order_data = {
                "auth_token": auth_token,
                "delivery_needed": "false",
                "amount_cents": 9900,
                "currency": "EGP",
                "items": []
            }
            
            order_response = requests.post(order_url, json=order_data, timeout=10)
            print(f"   Status: {order_response.status_code}")
            
            if order_response.status_code == 201:
                order_result = order_response.json()
                order_id = order_result.get('id')
                print(f"   ✅ Order created: {order_id}")
                
                # Test payment key creation
                print("\n4. Testing Payment Key Creation:")
                payment_key_url = f"{settings.PAYMOB_BASE_URL}/acceptance/payment_keys"
                payment_key_data = {
                    "auth_token": auth_token,
                    "amount_cents": 9900,
                    "expiration": 3600,
                    "order_id": order_id,
                    "billing_data": {
                        "apartment": "NA",
                        "email": "test@example.com",
                        "floor": "NA",
                        "first_name": "Test",
                        "street": "NA",
                        "building": "NA",
                        "phone_number": "+201234567890",
                        "shipping_method": "NA",
                        "postal_code": "NA",
                        "city": "NA",
                        "country": "EG",
                        "last_name": "User",
                        "state": "NA"
                    },
                    "currency": "EGP",
                    "integration_id": settings.PAYMOB_INTEGRATION_ID
                }
                
                payment_response = requests.post(payment_key_url, json=payment_key_data, timeout=10)
                print(f"   Status: {payment_response.status_code}")
                
                if payment_response.status_code == 201:
                    payment_result = payment_response.json()
                    payment_token = payment_result.get('token')
                    print(f"   ✅ Payment key created: {payment_token[:30]}...")
                    
                    # Generate iframe URL
                    iframe_url = f"https://accept.paymob.com/api/acceptance/iframes/{settings.PAYMOB_IFRAME_ID}?payment_token={payment_token}"
                    print(f"   ✅ iFrame URL: {iframe_url}")
                    
                    print("\n🎉 ALL PAYMOB API TESTS PASSED!")
                    return True, {
                        'auth_token': auth_token,
                        'order_id': order_id,
                        'payment_token': payment_token,
                        'iframe_url': iframe_url
                    }
                else:
                    print(f"   ❌ Payment key failed: {payment_response.text}")
                    return False, None
            else:
                print(f"   ❌ Order creation failed: {order_response.text}")
                return False, None
        else:
            print(f"   ❌ Auth failed: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, None

# Test using service class
def test_service_class():
    print("\n5. Testing PayMobService Class:")
    try:
        service = PayMobService()
        
        # Test authentication
        auth_token = service.authenticate()
        print(f"   ✅ Service auth: {auth_token[:30]}...")
        
        # Test order creation
        order = service.create_order(amount=99.00, currency='EGP')
        print(f"   ✅ Service order: {order.get('id')}")
        
        # Test payment key
        user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+201234567890'
        }
        
        payment_token = service.create_payment_key(
            order_id=order.get('id'),
            amount=99.00,
            user_data=user_data,
            currency='EGP'
        )
        print(f"   ✅ Service payment key: {payment_token[:30]}...")
        
        iframe_url = service.get_iframe_url(payment_token)
        print(f"   ✅ Service iframe: {iframe_url}")
        
        print("\n🎉 SERVICE CLASS TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"   ❌ Service class error: {str(e)}")
        return False

if __name__ == "__main__":
    success1, data = debug_paymob()
    if success1:
        success2 = test_service_class()
        if success2:
            print("\n✅ PayMob integration is fully functional!")
        else:
            print("\n⚠️  Manual API works but service class has issues")
    else:
        print("\n❌ PayMob API configuration issues detected")

debug_paymob()
