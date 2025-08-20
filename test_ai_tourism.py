#!/usr/bin/env python
"""
اختبار سريع لخدمة AI Tourism
"""

import os
import sys
import django
from pathlib import Path

# إضافة مسار المشروع
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Rahala.settings')
django.setup()

from trip.ai_services import TourismAIService

def test_ai_service():
    """اختبار خدمة AI Tourism"""
    print("🚀 بدء اختبار خدمة AI Tourism...")
    
    # إنشاء instance من الخدمة
    ai_service = TourismAIService()
    
    # اختبار مواقع مختلفة
    test_locations = [
        "Cairo, Egypt",
        "Paris, France", 
        "Dubai, UAE",
        "Istanbul, Turkey"
    ]
    
    for location in test_locations:
        print(f"\n📍 اختبار الموقع: {location}")
        print("-" * 50)
        
        try:
            result = ai_service.get_destination_info(location)
            
            print(f"🏛️ الدولة: {result.get('country', 'غير محدد')}")
            print(f"🏙️ المدينة: {result.get('city', 'غير محدد')}")
            
            tourism_info = result.get('tourism_info', {})
            if tourism_info:
                print(f"📝 الوصف: {tourism_info.get('description', 'غير متوفر')[:100]}...")
                print(f"🎯 عدد الأماكن المقترحة: {len(tourism_info.get('recommended_places', []))}")
                print(f"⚠️ عدد التحذيرات: {len(tourism_info.get('warnings', []))}")
                print(f"💰 العملة: {tourism_info.get('currency', 'غير محدد')}")
            
            print("✅ نجح الاختبار!")
            
        except Exception as e:
            print(f"❌ فشل الاختبار: {str(e)}")

if __name__ == "__main__":
    test_ai_service()
