#!/usr/bin/env python
"""
اختبار API إنشاء الرحلات مع AI Tourism
"""

import requests
import json
from io import BytesIO
from PIL import Image

# إعدادات الاختبار
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

def create_test_image():
    """إنشاء صورة اختبار"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def register_test_user():
    """تسجيل مستخدم اختبار"""
    print("👤 إنشاء مستخدم اختبار...")
    
    user_data = {
        "username": "test_traveler",
        "email": "test@example.com", 
        "password": "testpass123",
        "first_name": "Ahmed",
        "last_name": "Traveler"
    }
    
    try:
        response = requests.post(f"{API_BASE}/accounts/register/", json=user_data)
        if response.status_code == 201:
            print("✅ تم إنشاء المستخدم بنجاح")
            return True
        else:
            print(f"⚠️ المستخدم موجود بالفعل أو خطأ: {response.status_code}")
            return True  # نفترض أن المستخدم موجود
    except Exception as e:
        print(f"❌ خطأ في إنشاء المستخدم: {str(e)}")
        return False

def login_user():
    """تسجيل دخول المستخدم"""
    print("🔐 تسجيل دخول المستخدم...")

    login_data = {
        "email": "test@example.com",  # استخدام email بدلاً من username
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/accounts/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            print("✅ تم تسجيل الدخول بنجاح")
            return token
        else:
            print(f"❌ فشل تسجيل الدخول: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ خطأ في تسجيل الدخول: {str(e)}")
        return None

def create_trip_with_ai(token):
    """إنشاء رحلة مع AI Tourism"""
    print("🧳 إنشاء رحلة جديدة مع AI Tourism...")
    
    # إنشاء صورة اختبار
    test_image = create_test_image()
    
    # بيانات الرحلة
    trip_data = {
        'caption': 'رحلة رائعة في القاهرة التاريخية!',
        'location': 'Cairo, Egypt',
        'tags': ['سياحة', 'تاريخ', 'مصر']
    }
    
    # ملفات الصور
    files = {
        'images': ('test_image.jpg', test_image, 'image/jpeg')
    }
    
    # Headers مع التوكن
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/trip/create/",
            data=trip_data,
            files=files,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ تم إنشاء الرحلة بنجاح!")
            
            trip_data = response.json()
            print(f"🆔 ID الرحلة: {trip_data.get('id')}")
            print(f"📍 الموقع: {trip_data.get('location')}")
            print(f"🏛️ الدولة: {trip_data.get('country')}")
            print(f"🏙️ المدينة: {trip_data.get('city')}")
            
            # عرض المعلومات السياحية
            tourism_info = trip_data.get('tourism_info', {})
            if tourism_info:
                print("\n🎯 المعلومات السياحية من AI:")
                print("-" * 40)
                print(f"📝 الوصف: {tourism_info.get('description', 'غير متوفر')[:150]}...")
                
                places = tourism_info.get('recommended_places', [])
                if places:
                    print(f"\n🏛️ الأماكن المقترحة ({len(places)}):")
                    for i, place in enumerate(places[:3], 1):
                        print(f"   {i}. {place}")
                
                warnings = tourism_info.get('warnings', [])
                if warnings:
                    print(f"\n⚠️ تحذيرات مهمة ({len(warnings)}):")
                    for i, warning in enumerate(warnings[:2], 1):
                        print(f"   {i}. {warning}")
                
                print(f"\n💰 العملة: {tourism_info.get('currency', 'غير محدد')}")
                print(f"🗣️ اللغة: {tourism_info.get('language', 'غير محدد')}")
                print(f"📅 أفضل وقت للزيارة: {tourism_info.get('best_time_to_visit', 'غير محدد')}")
            
            return trip_data.get('id')
        else:
            print(f"❌ فشل إنشاء الرحلة: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء الرحلة: {str(e)}")
        return None

def test_trip_api():
    """اختبار شامل لـ API الرحلات"""
    print("🚀 بدء اختبار API الرحلات مع AI Tourism")
    print("=" * 60)
    
    # 1. إنشاء مستخدم
    if not register_test_user():
        return
    
    # 2. تسجيل دخول
    token = login_user()
    if not token:
        return
    
    # 3. إنشاء رحلة مع AI
    trip_id = create_trip_with_ai(token)
    if trip_id:
        print(f"\n🎉 تم الاختبار بنجاح! ID الرحلة: {trip_id}")
    else:
        print("\n❌ فشل الاختبار")

if __name__ == "__main__":
    test_trip_api()
