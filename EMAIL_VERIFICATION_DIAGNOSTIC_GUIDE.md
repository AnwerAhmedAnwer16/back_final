# Email Verification Diagnostic Guide

## 🔍 تشخيص مشاكل التحقق من البريد الإلكتروني

تم تطوير نظام تشخيص شامل لمساعدتك في حل مشاكل التحقق من البريد الإلكتروني.

## 🛠️ أدوات التشخيص الجديدة

### 1. فحص صحة رابط التحقق
```bash
GET /api/accounts/check-verification/{uid}/{token}/
```

**مثال:**
```bash
curl -X GET "http://localhost:8000/api/accounts/check-verification/Ng/cusotu-0afdbf9e6372d27de2ab4ead94fa12bc/"
```

**الاستجابة:**
```json
{
    "is_valid": true,
    "user_email": "user@example.com",
    "user_id": 6,
    "is_already_verified": false,
    "token_info": {
        "uid": "Ng",
        "token": "cusotu-0afdbf9e6372d27de2ab4ead94fa12bc",
        "decoded_uid": "6"
    }
}
```

### 2. إنشاء رابط تحقق جديد
```bash
POST /api/accounts/generate-verification-link/
```

**مثال:**
```bash
curl -X POST http://localhost:8000/api/accounts/generate-verification-link/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**الاستجابة:**
```json
{
    "message": "Verification link generated",
    "user_email": "user@example.com",
    "user_id": 6,
    "is_verified": false,
    "verification_link": "http://localhost:8080/verify-email/Ng/cusotu-0afdbf9e6372d27de2ab4ead94fa12bc/",
    "api_verification_link": "http://localhost:8000/api/accounts/verify-email/Ng/cusotu-0afdbf9e6372d27de2ab4ead94fa12bc/",
    "check_link": "http://localhost:8000/api/accounts/check-verification/Ng/cusotu-0afdbf9e6372d27de2ab4ead94fa12bc/",
    "token_info": {
        "uid": "Ng",
        "token": "cusotu-0afdbf9e6372d27de2ab4ead94fa12bc"
    }
}
```

### 3. تحقق محسن مع تفاصيل الأخطاء
```bash
POST /api/accounts/verify-email/{uid}/{token}/
```

**الاستجابات المحتملة:**

#### نجح التحقق:
```json
{
    "message": "Email verified successfully",
    "user_email": "user@example.com",
    "user_id": 6
}
```

#### المستخدم مفعل بالفعل:
```json
{
    "message": "Email is already verified",
    "user_email": "user@example.com"
}
```

#### رابط غير صحيح أو منتهي الصلاحية:
```json
{
    "error": "Invalid or expired verification link",
    "details": "The verification link may have expired. Please request a new one."
}
```

#### مستخدم غير موجود:
```json
{
    "error": "User not found",
    "details": "The user associated with this verification link does not exist."
}
```

## 🔧 خطوات التشخيص

### الخطوة 1: تحقق من إعدادات البريد الإلكتروني
```bash
# تحقق من ملف .env
cat .env | grep EMAIL
```

**يجب أن تحتوي على:**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

### الخطوة 2: اختبار إنشاء مستخدم جديد
```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "testpass123"}'
```

### الخطوة 3: إنشاء رابط تحقق جديد
```bash
curl -X POST http://localhost:8000/api/accounts/generate-verification-link/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### الخطوة 4: فحص صحة الرابط
```bash
# استخدم الرابط من الخطوة السابقة
curl -X GET "http://localhost:8000/api/accounts/check-verification/{uid}/{token}/"
```

### الخطوة 5: اختبار التحقق
```bash
# استخدم نفس uid و token
curl -X POST "http://localhost:8000/api/accounts/verify-email/{uid}/{token}/"
```

## 🚨 الأخطاء الشائعة وحلولها

### 1. "Invalid verification link"
**السبب:** التوكن منتهي الصلاحية أو غير صحيح
**الحل:** 
- إنشاء رابط جديد باستخدام `/generate-verification-link/`
- التأكد من نسخ الرابط بالكامل بدون مسافات

### 2. "User not found"
**السبب:** المستخدم محذوف أو UID غير صحيح
**الحل:**
- التحقق من وجود المستخدم في قاعدة البيانات
- إنشاء مستخدم جديد إذا لزم الأمر

### 3. "Email already verified"
**السبب:** المستخدم مفعل بالفعل
**الحل:** هذا ليس خطأ، المستخدم يمكنه تسجيل الدخول

### 4. مشاكل إرسال البريد الإلكتروني
**الأسباب المحتملة:**
- كلمة مرور التطبيق غير صحيحة
- إعدادات SMTP خاطئة
- حساب Gmail محظور

**الحل:**
```bash
# اختبار إرسال بريد إلكتروني
curl -X POST http://localhost:8000/api/accounts/resend-verification/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## 📧 إعداد Gmail للتطبيق

### 1. تفعيل المصادقة الثنائية
- اذهب إلى إعدادات حساب Google
- فعل المصادقة الثنائية

### 2. إنشاء كلمة مرور التطبيق
- اذهب إلى "App passwords"
- اختر "Mail" و "Other"
- انسخ كلمة المرور المُنشأة

### 3. تحديث ملف .env
```env
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=generated_app_password
```

## 🧪 اختبار شامل

### سكريبت اختبار كامل:
```bash
#!/bin/bash

echo "=== اختبار نظام التحقق من البريد الإلكتروني ==="

# 1. إنشاء مستخدم جديد
echo "1. إنشاء مستخدم جديد..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser", "password": "testpass123"}')
echo "Response: $REGISTER_RESPONSE"

# 2. إنشاء رابط تحقق
echo "2. إنشاء رابط تحقق..."
LINK_RESPONSE=$(curl -s -X POST http://localhost:8000/api/accounts/generate-verification-link/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}')
echo "Response: $LINK_RESPONSE"

# استخراج UID و Token من الاستجابة
UID=$(echo $LINK_RESPONSE | grep -o '"uid":"[^"]*"' | cut -d'"' -f4)
TOKEN=$(echo $LINK_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

echo "UID: $UID"
echo "Token: $TOKEN"

# 3. فحص صحة الرابط
echo "3. فحص صحة الرابط..."
CHECK_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/accounts/check-verification/$UID/$TOKEN/")
echo "Response: $CHECK_RESPONSE"

# 4. تفعيل الحساب
echo "4. تفعيل الحساب..."
VERIFY_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/accounts/verify-email/$UID/$TOKEN/")
echo "Response: $VERIFY_RESPONSE"

echo "=== انتهى الاختبار ==="
```

## 📝 ملاحظات مهمة

1. **انتهاء صلاحية التوكن:** التوكن له مدة صلاحية محدودة (عادة 24 ساعة)
2. **استخدام واحد:** كل توكن يمكن استخدامه مرة واحدة فقط
3. **الأمان:** لا تشارك التوكن أو UID مع أي شخص
4. **البيئة:** تأكد من أن السيرفر يعمل على المنفذ الصحيح

## 🔗 الروابط المفيدة

- **API Documentation:** `NOTIFICATIONS_API_DOCUMENTATION.md`
- **Server Status:** `http://localhost:8000/admin/`
- **Email Settings:** `Rahala/settings.py`

## 📞 الدعم

إذا استمرت المشكلة، يرجى:
1. تشغيل سكريبت الاختبار أعلاه
2. إرسال نتائج الاختبار
3. التحقق من logs السيرفر
4. التأكد من إعدادات Gmail
