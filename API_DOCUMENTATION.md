# 📡 API Documentation - مشروع Rahala

## 📋 جدول المحتويات
- [نظرة عامة](#نظرة-عامة)
- [المصادقة](#المصادقة)
- [Trip APIs](#trip-apis)
- [Authentication APIs](#authentication-apis)
- [Interactions APIs](#interactions-apis)
- [Search APIs](#search-apis)
- [Error Handling](#error-handling)

---

## 🎯 نظرة عامة

**Base URL**: `http://localhost:8000/api`

**Content-Type**: `application/json` (إلا في حالة رفع الملفات)

**Authentication**: JWT Bearer Token

---

## 🔐 المصادقة

جميع الـ APIs المحمية تتطلب إرسال JWT token في header:

```http
Authorization: Bearer {access_token}
```

---

## 🧳 Trip APIs

### 1. إنشاء رحلة جديدة (مع AI Tourism)

```http
POST /api/trip/create/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body:**
```
caption: "رحلة رائعة في القاهرة التاريخية"
location: "Cairo, Egypt"
tags: ["سياحة", "تاريخ", "مصر"]
images: [file1.jpg, file2.jpg]
videos: [video1.mp4]
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user": "ahmed_traveler",
  "caption": "رحلة رائعة في القاهرة التاريخية",
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
  "updated_at": "2024-01-15T10:30:00Z",
  "images": [
    {
      "id": 1,
      "image": "http://localhost:8000/media/trips/1/images/image1.jpg"
    }
  ],
  "videos": [
    {
      "id": 1,
      "video": "http://localhost:8000/media/trips/1/videos/video1.mp4"
    }
  ],
  "tags": [
    {
      "id": 1,
      "tripTag": "سياحة"
    }
  ]
}
```

**Error Responses:**
```json
// 400 Bad Request - لا توجد ملفات
{
  "detail": "You must upload at least one image or one video."
}

// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}

// 403 Forbidden - مستخدم غير متحقق
{
  "detail": "User must be verified to create trips."
}
```

---

### 2. قائمة الرحلات

```http
GET /api/trip/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `page`: رقم الصفحة (افتراضي: 1)
- `page_size`: عدد العناصر في الصفحة (افتراضي: 20)

**Response (200 OK):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/trip/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": "ahmed_traveler",
      "caption": "رحلة رائعة في القاهرة",
      "location": "Cairo, Egypt",
      "country": "مصر",
      "city": "القاهرة",
      "tourism_info": { ... },
      "created_at": "2024-01-15T10:30:00Z",
      "images": [...],
      "videos": [...],
      "tags": [...]
    }
  ]
}
```

---

### 3. تفاصيل رحلة محددة

```http
GET /api/trip/{trip_id}/
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "ahmed_traveler",
    "profile": {
      "avatar": "http://localhost:8000/media/avatars/user1.jpg",
      "bio": "مسافر ومصور"
    }
  },
  "caption": "رحلة رائعة في القاهرة",
  "location": "Cairo, Egypt",
  "country": "مصر",
  "city": "القاهرة",
  "tourism_info": {
    "description": "القاهرة مدينة نابضة بالحياة...",
    "recommended_places": [...],
    "warnings": [...],
    "best_time_to_visit": "من أكتوبر إلى مارس",
    "local_tips": [...],
    "currency": "الجنيه المصري",
    "language": "العربية"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "images": [...],
  "videos": [...],
  "tags": [...],
  "stats": {
    "likes_count": 25,
    "comments_count": 8,
    "saves_count": 12,
    "shares_count": 5,
    "is_liked": false,
    "is_saved": true
  }
}
```

---

### 4. حذف رحلة

```http
DELETE /api/trip/{trip_id}/delete/
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

**Error Responses:**
```json
// 403 Forbidden - ليس المالك
{
  "detail": "You do not have permission to perform this action."
}

// 404 Not Found
{
  "detail": "Not found."
}
```

---

### 5. إضافة صور لرحلة موجودة

```http
POST /api/trip/{trip_id}/images/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body:**
```
images: [file1.jpg, file2.jpg]
```

**Response (201 Created):**
```json
{
  "message": "Images uploaded successfully",
  "images": [
    {
      "id": 5,
      "image": "http://localhost:8000/media/trips/1/images/new_image.jpg"
    }
  ]
}
```

---

### 6. إضافة/إزالة تاجات

```http
POST /api/trip/{trip_id}/tags/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "tripTag": "مغامرة"
}
```

**Response (201 Created):**
```json
{
  "id": 10,
  "tripTag": "مغامرة"
}
```

```http
DELETE /api/trip/tags/{tag_id}/
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

---

## 👤 Authentication APIs

### 1. تسجيل مستخدم جديد

```http
POST /api/accounts/register/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "newuser",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "newuser",
    "date_joined": "2024-01-15T10:30:00Z",
    "is_verified": false
  },
  "verification_link": "http://localhost:8000/api/accounts/verify-email/..."
}
```

**Error Responses:**
```json
// 400 Bad Request - كلمة مرور ضعيفة
{
  "password": [
    "This password is too short. It must contain at least 8 characters.",
    "This password is too common."
  ]
}

// 400 Bad Request - بريد إلكتروني موجود
{
  "email": ["User with this email already exists."]
}
```

---

### 2. تسجيل الدخول

```http
POST /api/accounts/login/
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "is_verified": true,
    "subscription_plan": "free",
    "has_verified_badge": false,
    "profile": {
      "avatar": null,
      "bio": "",
      "location": ""
    }
  }
}
```

**Error Responses:**
```json
// 401 Unauthorized
{
  "detail": "No active account found with the given credentials"
}
```

---

### 3. تحديث التوكن

```http
POST /api/accounts/token/refresh/
Content-Type: application/json
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 4. تسجيل الخروج

```http
POST /api/accounts/logout/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

---

### 5. تحقق البريد الإلكتروني

```http
GET /api/accounts/verify-email/{uidb64}/{token}/
```

**Response (200 OK):**
```json
{
  "message": "Email verified successfully",
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "is_verified": true
  }
}
```

---

## 💬 Interactions APIs

### 1. إضافة إعجاب

```http
POST /api/interactions/like/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "trip_id": 1
}
```

**Response (201 Created):**
```json
{
  "message": "Trip liked successfully",
  "is_liked": true
}
```

**Response (200 OK) - إزالة الإعجاب:**
```json
{
  "message": "Like removed successfully",
  "is_liked": false
}
```

---

### 2. إضافة تعليق

```http
POST /api/interactions/comment/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "trip_id": 1,
  "content": "رحلة رائعة! شكراً للمشاركة 😍"
}
```

**Response (201 Created):**
```json
{
  "id": 15,
  "user": {
    "username": "commenter",
    "profile": {
      "avatar": "http://localhost:8000/media/avatars/user2.jpg"
    }
  },
  "content": "رحلة رائعة! شكراً للمشاركة 😍",
  "created_at": "2024-01-15T11:30:00Z"
}
```

---

### 3. حفظ رحلة

```http
POST /api/interactions/save/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "trip_id": 1
}
```

**Response (201 Created):**
```json
{
  "message": "Trip saved successfully",
  "is_saved": true
}
```

---

### 4. مشاركة رحلة

```http
POST /api/interactions/share/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "trip_id": 1,
  "platform": "facebook"
}
```

**Response (201 Created):**
```json
{
  "message": "Trip shared successfully",
  "share_url": "https://facebook.com/share?url=..."
}
```

---

### 5. متابعة مستخدم

```http
POST /api/interactions/follow/
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "user_id": 5
}
```

**Response (201 Created):**
```json
{
  "message": "User followed successfully",
  "is_following": true
}
```

---

## 🔍 Search APIs

### 1. البحث في الرحلات

```http
GET /api/search/trips/?q={query}
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `q`: نص البحث
- `country`: تصفية حسب الدولة
- `city`: تصفية حسب المدينة
- `tags`: تصفية حسب التاجات
- `date_from`: من تاريخ
- `date_to`: إلى تاريخ

**Example:**
```http
GET /api/search/trips/?q=القاهرة&country=مصر&tags=سياحة
```

**Response (200 OK):**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "caption": "رحلة رائعة في القاهرة",
      "location": "Cairo, Egypt",
      "country": "مصر",
      "city": "القاهرة",
      "user": "ahmed_traveler",
      "created_at": "2024-01-15T10:30:00Z",
      "images_count": 5,
      "likes_count": 25,
      "highlight": {
        "caption": "رحلة رائعة في <mark>القاهرة</mark>",
        "tourism_description": "مدينة نابضة بالحياة في <mark>القاهرة</mark>"
      }
    }
  ]
}
```

---

### 2. البحث في المستخدمين

```http
GET /api/search/users/?q={query}
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "username": "ahmed_traveler",
      "profile": {
        "avatar": "http://localhost:8000/media/avatars/user1.jpg",
        "bio": "مسافر ومصور",
        "location": "Cairo, Egypt"
      },
      "followers_count": 150,
      "trips_count": 25,
      "is_following": false
    }
  ]
}
```

---

### 3. الاقتراحات الذكية

```http
GET /api/search/suggestions/?q={partial_query}
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "suggestions": [
    {
      "type": "location",
      "text": "القاهرة، مصر",
      "count": 45
    },
    {
      "type": "tag",
      "text": "سياحة",
      "count": 120
    },
    {
      "type": "user",
      "text": "ahmed_traveler",
      "avatar": "http://localhost:8000/media/avatars/user1.jpg"
    }
  ]
}
```

---

## ❌ Error Handling

### HTTP Status Codes:

- **200 OK**: طلب ناجح
- **201 Created**: تم إنشاء المورد بنجاح
- **204 No Content**: تم الحذف بنجاح
- **400 Bad Request**: خطأ في البيانات المرسلة
- **401 Unauthorized**: غير مصرح بالوصول
- **403 Forbidden**: ممنوع الوصول
- **404 Not Found**: المورد غير موجود
- **429 Too Many Requests**: تجاوز حد الطلبات
- **500 Internal Server Error**: خطأ في الخادم

### Error Response Format:

```json
{
  "error": "validation_error",
  "message": "البيانات المرسلة غير صحيحة",
  "details": {
    "field_name": ["رسالة الخطأ"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Errors:

```json
// Rate Limit Exceeded
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}

// Invalid Token
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}

// Validation Error
{
  "location": ["This field is required."],
  "images": ["No file was submitted."]
}
```

---

## 📊 Rate Limiting

### Limits:
- **Anonymous users**: 100 requests/day
- **Authenticated users**: 1000 requests/day
- **Trip creation**: 10 trips/hour
- **AI service**: 50 requests/day

### Headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642262400
```

---

## 🔧 Development Tools

### Postman Collection:
```json
{
  "info": {
    "name": "Rahala API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000/api"
    },
    {
      "key": "access_token",
      "value": "{{access_token}}"
    }
  ]
}
```

### cURL Examples:

```bash
# تسجيل الدخول
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# إنشاء رحلة
curl -X POST http://localhost:8000/api/trip/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "caption=رحلة رائعة" \
  -F "location=Cairo, Egypt" \
  -F "images=@image.jpg" \
  -F "tags=سياحة"

# البحث في الرحلات
curl -X GET "http://localhost:8000/api/search/trips/?q=القاهرة" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

**📚 هذا الدليل يوفر مرجعاً شاملاً لجميع APIs في مشروع Rahala!**
