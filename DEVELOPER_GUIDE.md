# 📚 دليل المطورين - مشروع Rahala

## 📋 جدول المحتويات
- [نظرة عامة](#نظرة-عامة)
- [إعداد البيئة](#إعداد-البيئة)
- [Backend API](#backend-api)
- [Frontend Integration](#frontend-integration)
- [AI Tourism Service](#ai-tourism-service)
- [قاعدة البيانات](#قاعدة-البيانات)
- [المصادقة والأمان](#المصادقة-والأمان)
- [اختبار النظام](#اختبار-النظام)

---

## 🎯 نظرة عامة

**Rahala** هو تطبيق سياحي ذكي يستخدم الذكاء الاصطناعي لتقديم معلومات سياحية شاملة عن الوجهات السياحية.

### المميزات الرئيسية:
- 🤖 **AI Tourism Assistant**: معلومات سياحية ذكية
- 📸 **Trip Management**: إدارة الرحلات مع الصور والفيديوهات
- 👥 **Social Features**: تفاعل اجتماعي (إعجاب، تعليق، مشاركة)
- 🔍 **Smart Search**: بحث ذكي عن المستخدمين والرحلات
- 💳 **Promotions**: نظام ترويج الرحلات

---

## ⚙️ إعداد البيئة

### متطلبات النظام:
- Python 3.11+
- Django 5.2+
- PostgreSQL
- Redis
- Node.js (للفرنت إند)

### 1. إعداد Backend:

```bash
# استنساخ المشروع
git clone <repository-url>
cd A-master

# إنشاء البيئة الافتراضية
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate     # Linux/Mac

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد قاعدة البيانات
python manage.py migrate

# تشغيل السيرفر
python manage.py runserver
```

### 2. متغيرات البيئة (.env):

```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/rahala_db

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Google OAuth2
GOOGLE_OAUTH2_CLIENT_ID=your-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret

# OpenRouter AI Configuration
OPENROUTER_API_KEY=sk-or-v1-your-api-key
OPENROUTER_MODEL=gpt-oss-20b
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# PayMob Payment Gateway
PAYMOB_API_KEY=your-paymob-key
PAYMOB_INTEGRATION_ID=your-integration-id
PAYMOB_IFRAME_ID=your-iframe-id

# Redis
REDIS_URL=redis://localhost:6379/0
```

---

## 🔧 Backend API

### هيكل المشروع:

```
A-master/
├── accounts/           # إدارة المستخدمين والمصادقة
├── trip/              # إدارة الرحلات + AI Tourism
├── interactions/      # التفاعلات الاجتماعية
├── search/           # البحث الذكي
├── promotions/       # نظام الترويج
├── Rahala/          # إعدادات المشروع
└── media/           # ملفات الوسائط
```

### 📍 Trip API Endpoints:

#### إنشاء رحلة جديدة (مع AI Tourism):
```http
POST /api/trip/create/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

{
  "caption": "رحلة رائعة في القاهرة",
  "location": "Cairo, Egypt",
  "tags": ["سياحة", "تاريخ", "مصر"],
  "images": [file1, file2],
  "videos": [file1]
}
```

#### الاستجابة:
```json
{
  "id": 1,
  "user": "ahmed_traveler",
  "caption": "رحلة رائعة في القاهرة",
  "location": "Cairo, Egypt",
  "country": "مصر",
  "city": "القاهرة",
  "tourism_info": {
    "description": "القاهرة مدينة نابضة بالحياة تجمع بين التاريخ القديم والحداثة...",
    "recommended_places": [
      "أهرامات الجيزة",
      "متحف المصري",
      "خان الخليلي",
      "قصر محمد علي"
    ],
    "warnings": [
      "احذر من الاحتيال في الأسواق السياحية",
      "تجنب القيادة في ساعات الذروة"
    ],
    "best_time_to_visit": "من أكتوبر إلى مارس",
    "local_tips": [
      "استخدم وسائل النقل العام لتجنب الزحام",
      "تأكد من شرب المياه المعلبة"
    ],
    "currency": "الجنيه المصري",
    "language": "العربية"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "images": [...],
  "videos": [...],
  "tags": [...]
}
```

#### قائمة الرحلات:
```http
GET /api/trip/
Authorization: Bearer {access_token}
```

#### تفاصيل رحلة:
```http
GET /api/trip/{trip_id}/
Authorization: Bearer {access_token}
```

### 👤 Authentication API:

#### تسجيل مستخدم جديد:
```http
POST /api/accounts/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "newuser",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
```

#### تسجيل الدخول:
```http
POST /api/accounts/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

#### الاستجابة:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "is_verified": false
  }
}
```

### 💬 Interactions API:

#### إضافة إعجاب:
```http
POST /api/interactions/like/
Authorization: Bearer {access_token}

{
  "trip_id": 1
}
```

#### إضافة تعليق:
```http
POST /api/interactions/comment/
Authorization: Bearer {access_token}

{
  "trip_id": 1,
  "content": "رحلة رائعة!"
}
```

---

## 🎨 Frontend Integration

### React/Vue.js Integration:

#### 1. إنشاء رحلة جديدة:

```javascript
// React Example
const createTrip = async (tripData) => {
  const formData = new FormData();
  formData.append('caption', tripData.caption);
  formData.append('location', tripData.location);
  
  // إضافة الصور
  tripData.images.forEach(image => {
    formData.append('images', image);
  });
  
  // إضافة التاجات
  tripData.tags.forEach(tag => {
    formData.append('tags', tag);
  });

  try {
    const response = await fetch('/api/trip/create/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      },
      body: formData
    });
    
    const result = await response.json();
    
    if (response.ok) {
      // عرض المعلومات السياحية
      displayTourismInfo(result.tourism_info);
      return result;
    }
  } catch (error) {
    console.error('Error creating trip:', error);
  }
};
```

#### 2. عرض المعلومات السياحية:

```javascript
// Tourism Info Component
const TourismInfoCard = ({ tourismInfo, country, city }) => {
  return (
    <div className="tourism-info-card">
      <div className="location-header">
        <h3>{city}, {country}</h3>
      </div>
      
      <div className="description">
        <p>{tourismInfo.description}</p>
      </div>
      
      <div className="recommended-places">
        <h4>🏛️ أماكن مقترحة للزيارة:</h4>
        <ul>
          {tourismInfo.recommended_places.map((place, index) => (
            <li key={index}>{place}</li>
          ))}
        </ul>
      </div>
      
      <div className="warnings">
        <h4>⚠️ تحذيرات مهمة:</h4>
        <ul>
          {tourismInfo.warnings.map((warning, index) => (
            <li key={index} className="warning">{warning}</li>
          ))}
        </ul>
      </div>
      
      <div className="travel-info">
        <div className="info-item">
          <span>💰 العملة:</span> {tourismInfo.currency}
        </div>
        <div className="info-item">
          <span>🗣️ اللغة:</span> {tourismInfo.language}
        </div>
        <div className="info-item">
          <span>📅 أفضل وقت للزيارة:</span> {tourismInfo.best_time_to_visit}
        </div>
      </div>
      
      <div className="local-tips">
        <h4>💡 نصائح محلية:</h4>
        <ul>
          {tourismInfo.local_tips.map((tip, index) => (
            <li key={index}>{tip}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};
```

#### 3. CSS للتصميم:

```css
.tourism-info-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  padding: 20px;
  margin: 20px 0;
  color: white;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.location-header h3 {
  font-size: 24px;
  margin-bottom: 15px;
  text-align: center;
}

.description {
  background: rgba(255,255,255,0.1);
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.recommended-places, .warnings, .local-tips {
  margin-bottom: 15px;
}

.recommended-places ul, .warnings ul, .local-tips ul {
  list-style: none;
  padding: 0;
}

.recommended-places li, .local-tips li {
  background: rgba(255,255,255,0.1);
  padding: 8px 12px;
  margin: 5px 0;
  border-radius: 5px;
}

.warnings li {
  background: rgba(255,193,7,0.2);
  padding: 8px 12px;
  margin: 5px 0;
  border-radius: 5px;
  border-left: 4px solid #ffc107;
}

.travel-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin: 15px 0;
}

.info-item {
  background: rgba(255,255,255,0.1);
  padding: 10px;
  border-radius: 8px;
  text-align: center;
}
```

---

## 🤖 AI Tourism Service

### كيفية عمل الخدمة:

#### 1. هيكل الخدمة:
```python
# trip/ai_services.py
class TourismAIService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL
    
    def get_destination_info(self, location: str) -> Dict[str, Any]:
        """الحصول على معلومات سياحية شاملة"""
        # إنشاء prompt مخصص
        # استدعاء OpenRouter API
        # تحليل الاستجابة
        # إرجاع البيانات المنظمة
```

#### 2. استخدام الخدمة:
```python
# في views.py
from .ai_services import TourismAIService

def post(self, request, *args, **kwargs):
    # ... كود إنشاء الرحلة
    
    # الحصول على معلومات سياحية
    if location:
        ai_service = TourismAIService()
        tourism_data = ai_service.get_destination_info(location)
        
        country = tourism_data.get('country', '')
        city = tourism_data.get('city', '')
        tourism_info = tourism_data.get('tourism_info', {})
    
    # إنشاء الرحلة مع المعلومات السياحية
    trip = Trip.objects.create(
        user=user,
        caption=caption,
        location=location,
        country=country,
        city=city,
        tourism_info=tourism_info
    )
```

#### 3. تخصيص الـ Prompts:
```python
def _create_tourism_prompt(self, location: str) -> str:
    return f"""You are a tourism expert. Analyze: "{location}"
    
    Return ONLY valid JSON:
    {{
      "country": "Country in Arabic",
      "city": "City in Arabic",
      "tourism_info": {{
        "description": "Brief description in Arabic",
        "recommended_places": ["Place 1", "Place 2", ...],
        "warnings": ["Warning 1", "Warning 2"],
        "best_time_to_visit": "Best time in Arabic",
        "local_tips": ["Tip 1", "Tip 2"],
        "currency": "Currency in Arabic",
        "language": "Language in Arabic"
      }}
    }}"""
```

---

## 🗄️ قاعدة البيانات

### Trip Model:
```python
class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    
    # معلومات سياحية مدعومة بالذكاء الاصطناعي
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    tourism_info = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Migration:
```bash
# إنشاء migration للحقول الجديدة
python manage.py makemigrations trip

# تطبيق التغييرات
python manage.py migrate
```

---

## 🔐 المصادقة والأمان

### JWT Authentication:
```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### Permissions:
```python
# في views.py
from accounts.permissons import IsVerifiedUser

class TripCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsVerifiedUser]
```

### CORS Configuration:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
]
```

---

## 🧪 اختبار النظام

### 1. اختبار Backend:
```bash
# تشغيل جميع الاختبارات
python manage.py test

# اختبار تطبيق محدد
python manage.py test trip

# اختبار AI Service
python test_ai_tourism.py
```

### 2. اختبار API:
```bash
# اختبار إنشاء رحلة مع AI
python test_trip_api.py
```

### 3. اختبار يدوي:
```bash
# تشغيل السيرفر
python manage.py runserver

# اختبار Endpoints
curl -X POST http://localhost:8000/api/trip/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "caption=رحلة تجريبية" \
  -F "location=Paris, France" \
  -F "images=@test_image.jpg"
```

---

## 📝 ملاحظات مهمة للمطورين

### 1. Error Handling:
- جميع API calls محمية بـ try-catch
- Fallback data في حالة فشل AI
- Logging مفصل للتتبع

### 2. Performance:
- استخدم caching للمواقع المتكررة
- Optimize database queries
- Compress images قبل الرفع

### 3. Security:
- تحقق من صحة البيانات المدخلة
- Rate limiting للـ API calls
- Sanitize user inputs

### 4. Monitoring:
- تتبع استخدام OpenRouter API
- Monitor response times
- Log errors للمراجعة

---

## 🚀 نشر المشروع

### Production Settings:
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rahala_prod',
        'USER': 'postgres',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Docker Deployment:
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "Rahala.wsgi:application"]
```

---

## 📞 الدعم والمساعدة

للحصول على المساعدة أو الإبلاغ عن مشاكل:
- 📧 Email: support@rahala.com
- 📱 GitHub Issues: [Repository Issues]
- 📚 Documentation: [Full Documentation]

---

**🎉 مبروك! أنت الآن جاهز لتطوير وتحسين مشروع Rahala!**

---

## 📱 Mobile App Integration

### React Native Example:

```javascript
// TripService.js
class TripService {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async createTrip(tripData) {
    const formData = new FormData();

    // إضافة البيانات النصية
    formData.append('caption', tripData.caption);
    formData.append('location', tripData.location);

    // إضافة الصور
    tripData.images.forEach((image, index) => {
      formData.append('images', {
        uri: image.uri,
        type: 'image/jpeg',
        name: `image_${index}.jpg`
      });
    });

    // إضافة التاجات
    tripData.tags.forEach(tag => {
      formData.append('tags', tag);
    });

    try {
      const response = await fetch(`${this.baseURL}/api/trip/create/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'multipart/form-data',
        },
        body: formData
      });

      return await response.json();
    } catch (error) {
      throw new Error(`Failed to create trip: ${error.message}`);
    }
  }
}

// TourismInfoComponent.js
import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';

const TourismInfoComponent = ({ tourismInfo, country, city }) => {
  if (!tourismInfo) return null;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.locationTitle}>{city}, {country}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.description}>{tourismInfo.description}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🏛️ أماكن مقترحة للزيارة</Text>
        {tourismInfo.recommended_places?.map((place, index) => (
          <Text key={index} style={styles.listItem}>• {place}</Text>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚠️ تحذيرات مهمة</Text>
        {tourismInfo.warnings?.map((warning, index) => (
          <Text key={index} style={styles.warningItem}>⚠️ {warning}</Text>
        ))}
      </View>

      <View style={styles.infoGrid}>
        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>💰 العملة</Text>
          <Text style={styles.infoValue}>{tourismInfo.currency}</Text>
        </View>
        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>🗣️ اللغة</Text>
          <Text style={styles.infoValue}>{tourismInfo.language}</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📅 أفضل وقت للزيارة</Text>
        <Text style={styles.timeToVisit}>{tourismInfo.best_time_to_visit}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💡 نصائح محلية</Text>
        {tourismInfo.local_tips?.map((tip, index) => (
          <Text key={index} style={styles.tipItem}>💡 {tip}</Text>
        ))}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    backgroundColor: '#667eea',
    padding: 20,
    borderRadius: 15,
    margin: 15,
  },
  locationTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
  },
  section: {
    backgroundColor: 'white',
    margin: 10,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
    color: '#555',
  },
  listItem: {
    fontSize: 14,
    marginVertical: 3,
    color: '#666',
  },
  warningItem: {
    fontSize: 14,
    marginVertical: 3,
    color: '#d63384',
    backgroundColor: '#f8d7da',
    padding: 8,
    borderRadius: 5,
  },
  tipItem: {
    fontSize: 14,
    marginVertical: 3,
    color: '#0f5132',
    backgroundColor: '#d1e7dd',
    padding: 8,
    borderRadius: 5,
  },
  infoGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    margin: 10,
  },
  infoItem: {
    flex: 1,
    backgroundColor: 'white',
    padding: 15,
    margin: 5,
    borderRadius: 10,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  infoLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 5,
  },
  infoValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  timeToVisit: {
    fontSize: 16,
    color: '#0066cc',
    fontWeight: '500',
  },
});

export default TourismInfoComponent;
```

---

## 🔧 Advanced Backend Features

### 1. Caching System:

```python
# trip/cache_service.py
from django.core.cache import cache
import hashlib

class TourismCacheService:
    CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours

    @staticmethod
    def get_cache_key(location: str) -> str:
        """إنشاء مفتاح cache فريد للموقع"""
        return f"tourism_info_{hashlib.md5(location.encode()).hexdigest()}"

    @staticmethod
    def get_cached_info(location: str):
        """الحصول على معلومات محفوظة"""
        cache_key = TourismCacheService.get_cache_key(location)
        return cache.get(cache_key)

    @staticmethod
    def cache_info(location: str, tourism_data: dict):
        """حفظ المعلومات في cache"""
        cache_key = TourismCacheService.get_cache_key(location)
        cache.set(cache_key, tourism_data, TourismCacheService.CACHE_TIMEOUT)

# استخدام Cache في AI Service
class TourismAIService:
    def get_destination_info(self, location: str) -> Dict[str, Any]:
        # التحقق من Cache أولاً
        cached_data = TourismCacheService.get_cached_info(location)
        if cached_data:
            logger.info(f"Using cached data for {location}")
            return cached_data

        # إذا لم توجد بيانات محفوظة، استدعي AI
        try:
            prompt = self._create_tourism_prompt(location)
            response = self._call_openrouter_api(prompt)

            if response:
                tourism_data = self._parse_ai_response(response)
                # حفظ النتيجة في Cache
                TourismCacheService.cache_info(location, tourism_data)
                return tourism_data
            else:
                return self._get_fallback_data(location)

        except Exception as e:
            logger.error(f"Error getting destination info for {location}: {str(e)}")
            return self._get_fallback_data(location)
```

### 2. Background Tasks with Celery:

```python
# trip/tasks.py
from celery import shared_task
from .models import Trip
from .ai_services import TourismAIService

@shared_task
def update_trip_tourism_info(trip_id):
    """تحديث معلومات سياحية للرحلة في الخلفية"""
    try:
        trip = Trip.objects.get(id=trip_id)

        if trip.location and not trip.tourism_info:
            ai_service = TourismAIService()
            tourism_data = ai_service.get_destination_info(trip.location)

            trip.country = tourism_data.get('country', '')
            trip.city = tourism_data.get('city', '')
            trip.tourism_info = tourism_data.get('tourism_info', {})
            trip.save()

            return f"Updated tourism info for trip {trip_id}"
    except Trip.DoesNotExist:
        return f"Trip {trip_id} not found"
    except Exception as e:
        return f"Error updating trip {trip_id}: {str(e)}"

@shared_task
def batch_update_tourism_info():
    """تحديث معلومات سياحية لجميع الرحلات التي تفتقر لها"""
    trips_without_info = Trip.objects.filter(
        tourism_info__isnull=True
    ).exclude(location='')

    for trip in trips_without_info:
        update_trip_tourism_info.delay(trip.id)

    return f"Queued {trips_without_info.count()} trips for tourism info update"
```

### 3. API Rate Limiting:

```python
# trip/throttles.py
from rest_framework.throttling import UserRateThrottle

class TripCreateThrottle(UserRateThrottle):
    scope = 'trip_create'
    rate = '10/hour'  # 10 رحلات في الساعة

class AIServiceThrottle(UserRateThrottle):
    scope = 'ai_service'
    rate = '50/day'  # 50 استدعاء AI في اليوم

# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'trip_create': '10/hour',
        'ai_service': '50/day'
    }
}

# في views.py
class TripCreateAPIView(generics.CreateAPIView):
    throttle_classes = [TripCreateThrottle, AIServiceThrottle]
```

### 4. Advanced Search with Elasticsearch:

```python
# search/elasticsearch_service.py
from elasticsearch import Elasticsearch
from django.conf import settings

class TripSearchService:
    def __init__(self):
        self.es = Elasticsearch([settings.ELASTICSEARCH_URL])
        self.index_name = 'trips'

    def index_trip(self, trip):
        """فهرسة رحلة في Elasticsearch"""
        doc = {
            'id': trip.id,
            'caption': trip.caption,
            'location': trip.location,
            'country': trip.country,
            'city': trip.city,
            'user': trip.user.username,
            'created_at': trip.created_at,
            'tourism_places': trip.tourism_info.get('recommended_places', []),
            'tourism_description': trip.tourism_info.get('description', ''),
        }

        self.es.index(
            index=self.index_name,
            id=trip.id,
            body=doc
        )

    def search_trips(self, query, filters=None):
        """البحث في الرحلات"""
        search_body = {
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': [
                        'caption^2',
                        'location^2',
                        'country',
                        'city',
                        'tourism_description',
                        'tourism_places'
                    ]
                }
            },
            'sort': [
                {'created_at': {'order': 'desc'}}
            ]
        }

        if filters:
            search_body['query'] = {
                'bool': {
                    'must': [search_body['query']],
                    'filter': filters
                }
            }

        return self.es.search(
            index=self.index_name,
            body=search_body
        )
```

---

## 📊 Analytics and Monitoring

### 1. Custom Metrics:

```python
# trip/metrics.py
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

class TripAnalytics:
    @staticmethod
    def get_popular_destinations():
        """أكثر الوجهات شعبية"""
        return Trip.objects.values('country', 'city')\
            .annotate(trip_count=Count('id'))\
            .order_by('-trip_count')[:10]

    @staticmethod
    def get_ai_usage_stats():
        """إحصائيات استخدام AI"""
        total_trips = Trip.objects.count()
        trips_with_ai = Trip.objects.exclude(tourism_info={}).count()

        return {
            'total_trips': total_trips,
            'trips_with_ai_info': trips_with_ai,
            'ai_usage_percentage': (trips_with_ai / total_trips * 100) if total_trips > 0 else 0
        }

    @staticmethod
    def get_weekly_trip_stats():
        """إحصائيات الرحلات الأسبوعية"""
        week_ago = timezone.now() - timedelta(days=7)

        return Trip.objects.filter(created_at__gte=week_ago)\
            .extra({'day': 'date(created_at)'})\
            .values('day')\
            .annotate(count=Count('id'))\
            .order_by('day')
```

### 2. Logging Configuration:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/rahala.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'ai_service': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/ai_service.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'trip.ai_services': {
            'handlers': ['ai_service', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'trip.views': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## 🔒 Security Best Practices

### 1. Input Validation:

```python
# trip/validators.py
from django.core.exceptions import ValidationError
import re

def validate_location_format(location):
    """التحقق من صيغة الموقع"""
    if not location:
        raise ValidationError("الموقع مطلوب")

    # التحقق من الطول
    if len(location) > 255:
        raise ValidationError("الموقع طويل جداً")

    # التحقق من الأحرف المسموحة
    if not re.match(r'^[a-zA-Z\u0600-\u06FF\s,.-]+$', location):
        raise ValidationError("الموقع يحتوي على أحرف غير مسموحة")

def validate_caption_content(caption):
    """التحقق من محتوى التعليق"""
    if not caption:
        return  # التعليق اختياري

    # التحقق من الطول
    if len(caption) > 1000:
        raise ValidationError("التعليق طويل جداً")

    # التحقق من المحتوى المحظور
    forbidden_words = ['spam', 'scam', 'fake']
    for word in forbidden_words:
        if word.lower() in caption.lower():
            raise ValidationError(f"المحتوى يحتوي على كلمات محظورة: {word}")
```

### 2. API Security:

```python
# trip/permissions.py
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """السماح بالتعديل للمالك فقط"""

    def has_object_permission(self, request, view, obj):
        # قراءة للجميع
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # كتابة للمالك فقط
        return obj.user == request.user

class IsVerifiedUserOrReadOnly(BasePermission):
    """السماح بالإنشاء للمستخدمين المتحققين فقط"""

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        return request.user.is_authenticated and request.user.is_verified
```

### 3. File Upload Security:

```python
# trip/utils.py
from PIL import Image
import os

def validate_and_process_image(image_file):
    """التحقق من الصورة ومعالجتها"""

    # التحقق من نوع الملف
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if image_file.content_type not in allowed_types:
        raise ValidationError("نوع الصورة غير مدعوم")

    # التحقق من حجم الملف (5MB max)
    if image_file.size > 5 * 1024 * 1024:
        raise ValidationError("حجم الصورة كبير جداً")

    try:
        # التحقق من صحة الصورة
        img = Image.open(image_file)
        img.verify()

        # إعادة فتح الصورة للمعالجة
        image_file.seek(0)
        img = Image.open(image_file)

        # تصغير الصورة إذا كانت كبيرة
        max_size = (1920, 1080)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

        return img

    except Exception as e:
        raise ValidationError(f"الصورة تالفة: {str(e)}")
```

---

## 🚀 Performance Optimization

### 1. Database Optimization:

```python
# trip/models.py
class Trip(models.Model):
    # ... الحقول الموجودة

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['country', 'city']),
            models.Index(fields=['user', 'created_at']),
        ]
        ordering = ['-created_at']

# trip/views.py
class TripListAPIView(generics.ListAPIView):
    def get_queryset(self):
        return Trip.objects.select_related('user')\
            .prefetch_related('images', 'videos', 'tags')\
            .order_by('-created_at')
```

### 2. API Response Optimization:

```python
# trip/serializers.py
class TripListSerializer(serializers.ModelSerializer):
    """Serializer محسن لقائمة الرحلات"""
    user = serializers.StringRelatedField()
    images_count = serializers.SerializerMethodField()
    videos_count = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'user', 'caption', 'location',
            'country', 'city', 'created_at',
            'images_count', 'videos_count'
        ]

    def get_images_count(self, obj):
        return obj.images.count()

    def get_videos_count(self, obj):
        return obj.videos.count()

class TripDetailSerializer(serializers.ModelSerializer):
    """Serializer مفصل لتفاصيل الرحلة"""
    images = TripImageSerializer(many=True, read_only=True)
    videos = TripVideoSerializer(many=True, read_only=True)
    tags = TripTagSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Trip
        fields = '__all__'
```

---

## 📚 Additional Resources

### Useful Libraries:
```bash
# إضافية مفيدة
pip install django-extensions      # أدوات تطوير إضافية
pip install django-debug-toolbar   # أداة debug
pip install django-silk           # profiling للأداء
pip install celery               # مهام خلفية
pip install redis               # cache وmessage broker
pip install elasticsearch      # بحث متقدم
```

### Environment Variables Template:
```env
# .env.example
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost:5432/rahala_db

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Google OAuth2
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret

# OpenRouter AI
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
OPENROUTER_MODEL=gpt-oss-20b

# PayMob
PAYMOB_API_KEY=your-paymob-key
PAYMOB_INTEGRATION_ID=your-integration-id

# Redis
REDIS_URL=redis://localhost:6379/0

# Elasticsearch (optional)
ELASTICSEARCH_URL=http://localhost:9200
```

---

**🎯 هذا الدليل يوفر كل ما تحتاجه لتطوير وصيانة مشروع Rahala بكفاءة عالية!**
