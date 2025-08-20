# trip/ai_services.py

import json
import requests
import logging
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TourismAIService:
    """
    خدمة AI للحصول على معلومات سياحية شاملة عن الوجهات السياحية
    باستخدام OpenRouter API
    """
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  # Required by OpenRouter
            "X-Title": "Rahala Tourism App"  # Optional but recommended
        }
    
    def get_destination_info(self, location: str) -> Dict[str, Any]:
        """
        الحصول على معلومات سياحية شاملة عن الوجهة
        
        Args:
            location (str): اسم الموقع أو المدينة
            
        Returns:
            Dict[str, Any]: معلومات سياحية شاملة
        """
        try:
            prompt = self._create_tourism_prompt(location)
            response = self._call_openrouter_api(prompt)
            
            if response:
                return self._parse_ai_response(response)
            else:
                return self._get_fallback_data(location)
                
        except Exception as e:
            logger.error(f"Error getting destination info for {location}: {str(e)}")
            return self._get_fallback_data(location)
    
    def _create_tourism_prompt(self, location: str) -> str:
        """إنشاء prompt مفصل للحصول على معلومات سياحية"""
        return f"""You are a tourism expert. Analyze: "{location}"

Return ONLY valid JSON (no extra text):

{{
  "country": "Country in Arabic",
  "city": "City in Arabic",
  "tourism_info": {{
    "description": "Brief tourism description in Arabic (max 80 words)",
    "recommended_places": [
      "Place 1 in Arabic",
      "Place 2 in Arabic",
      "Place 3 in Arabic",
      "Place 4 in Arabic"
    ],
    "warnings": [
      "Warning 1 in Arabic",
      "Warning 2 in Arabic"
    ],
    "best_time_to_visit": "Best time in Arabic",
    "local_tips": [
      "Tip 1 in Arabic",
      "Tip 2 in Arabic"
    ],
    "currency": "Currency in Arabic",
    "language": "Language in Arabic"
  }}
}}

Keep descriptions short and concise. Return ONLY JSON."""
    
    def _call_openrouter_api(self, prompt: str) -> Optional[str]:
        """استدعاء OpenRouter API"""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            }

            logger.info(f"Calling OpenRouter API with model: {self.model}")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            logger.info(f"OpenRouter API response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                logger.info(f"AI response received: {content[:200]}...")
                return content
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error calling OpenRouter API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling OpenRouter API: {str(e)}")
            return None
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """تحليل استجابة AI وتحويلها إلى JSON"""
        try:
            # محاولة استخراج JSON من الاستجابة
            response = response.strip()
            logger.info(f"Parsing AI response: {response[:300]}...")

            # البحث عن JSON في النص
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                logger.info(f"Extracted JSON string: {json_str[:200]}...")
                parsed_data = json.loads(json_str)
                logger.info("Successfully parsed JSON from AI response")
                return parsed_data
            else:
                logger.error("No valid JSON found in AI response")
                logger.error(f"Full response: {response}")
                return {}

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response JSON: {str(e)}")
            logger.error(f"Problematic JSON: {response}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error parsing AI response: {str(e)}")
            return {}
    
    def _get_fallback_data(self, location: str) -> Dict[str, Any]:
        """بيانات احتياطية في حالة فشل AI"""
        # محاولة استخراج اسم الدولة والمدينة من النص
        parts = location.split(',')
        city = parts[0].strip() if parts else location
        country = parts[-1].strip() if len(parts) > 1 else "غير محدد"
        
        return {
            "country": country,
            "city": city,
            "tourism_info": {
                "description": f"وجهة سياحية رائعة في {location}. يرجى زيارة مصادر السفر المحلية للحصول على معلومات مفصلة.",
                "recommended_places": [
                    "المعالم التاريخية المحلية",
                    "المتاحف والمراكز الثقافية",
                    "الأسواق التقليدية",
                    "المطاعم المحلية المشهورة"
                ],
                "warnings": [
                    "تحقق من متطلبات التأشيرة",
                    "احمل وثائق السفر الضرورية",
                    "تأكد من التأمين الصحي"
                ],
                "best_time_to_visit": "يرجى مراجعة الطقس المحلي",
                "local_tips": [
                    "تعلم بعض العبارات الأساسية باللغة المحلية",
                    "احترم العادات والتقاليد المحلية",
                    "احمل نقود محلية للمدفوعات الصغيرة"
                ],
                "currency": "العملة المحلية",
                "language": "اللغة المحلية"
            }
        }


# دالة مساعدة للاستخدام السريع
def get_tourism_info(location: str) -> Dict[str, Any]:
    """
    دالة مساعدة للحصول على معلومات سياحية بسرعة
    
    Args:
        location (str): اسم الموقع
        
    Returns:
        Dict[str, Any]: معلومات سياحية
    """
    service = TourismAIService()
    return service.get_destination_info(location)
