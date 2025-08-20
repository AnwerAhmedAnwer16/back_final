# Rahala - Django Backend API

مشروع Rahala هو نظام إدارة الرحلات السياحية مبني بـ Django REST Framework مع دعم للإشعارات الفورية والذكاء الاصطناعي.

## المميزات الرئيسية

- 🔐 **نظام المصادقة والتفويض**: تسجيل الدخول بـ JWT وGoogle OAuth2
- 🧳 **إدارة الرحلات**: إنشاء وتعديل وحذف الرحلات مع الصور والفيديوهات
- 🤖 **الذكاء الاصطناعي**: توليد معلومات سياحية تلقائية للرحلات
- 💳 **نظام الدفع**: تكامل مع PayMob لمعالجة المدفوعات
- 📱 **الإشعارات الفورية**: WebSocket للإشعارات المباشرة
- 🔍 **البحث المتقدم**: بحث في الرحلات والمستخدمين
- 📊 **نظام الاشتراكات**: خطط اشتراك متعددة للمستخدمين
- 🎯 **نظام الترويج**: إدارة العروض والخصومات

## التقنيات المستخدمة

- **Backend**: Django 5.2.5, Django REST Framework 3.15.1
- **Database**: SQLite (قابل للتغيير إلى PostgreSQL)
- **Authentication**: JWT, Google OAuth2
- **Real-time**: Django Channels, Redis
- **AI Integration**: OpenRouter API
- **Payment**: PayMob Gateway
- **File Storage**: Django Media Files

## متطلبات التشغيل

- Python 3.11+
- Redis Server
- Git

## التثبيت والإعداد

### 1. استنساخ المشروع
```bash
git clone https://github.com/AnwerAhmedAnwer16/back_final.git
cd back_final
```

### 2. إنشاء البيئة الافتراضية
```bash
python -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate     # على Windows
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. إعداد متغيرات البيئة
انسخ ملف `.env.example` إلى `.env` وقم بتعديل القيم:
```bash
cp .env.example .env
```

املأ المتغيرات التالية في ملف `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Google OAuth2
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret

# PayMob (اختياري)
PAYMOB_API_KEY=your-paymob-api-key
PAYMOB_INTEGRATION_ID=your-integration-id
PAYMOB_IFRAME_ID=your-iframe-id

# OpenRouter AI (اختياري)
OPENROUTER_API_KEY=your-openrouter-api-key
```

### 5. تشغيل Redis
```bash
redis-server
```

### 6. تطبيق قاعدة البيانات
```bash
python manage.py migrate
```

### 7. إنشاء مستخدم إداري
```bash
python manage.py createsuperuser
```

### 8. تشغيل الخادم
```bash
python manage.py runserver
```

## هيكل المشروع

```
Rahala/
├── accounts/           # إدارة المستخدمين والمصادقة
├── trip/              # إدارة الرحلات والذكاء الاصطناعي
├── interactions/      # التفاعلات والإشعارات
├── search/           # نظام البحث
├── promotions/       # نظام الترويج والعروض
├── media/           # ملفات الوسائط المرفوعة
├── Rahala/          # إعدادات المشروع الرئيسية
└── requirements.txt # متطلبات المشروع
```

## API Endpoints

### المصادقة
- `POST /accounts/register/` - تسجيل مستخدم جديد
- `POST /accounts/login/` - تسجيل الدخول
- `POST /accounts/logout/` - تسجيل الخروج
- `GET /accounts/auth/google/` - تسجيل الدخول بـ Google

### الرحلات
- `GET /trip/trips/` - قائمة الرحلات
- `POST /trip/trips/` - إنشاء رحلة جديدة
- `GET /trip/trips/{id}/` - تفاصيل رحلة
- `PUT /trip/trips/{id}/` - تحديث رحلة
- `DELETE /trip/trips/{id}/` - حذف رحلة

### البحث
- `GET /search/trips/` - البحث في الرحلات
- `GET /search/users/` - البحث في المستخدمين

## المساهمة

1. Fork المشروع
2. إنشاء branch جديد (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى Branch (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

## الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## التواصل

- GitHub: [@AnwerAhmedAnwer16](https://github.com/AnwerAhmedAnwer16)
- Email: anwerahmedanwer16@gmail.com

## الدعم

إذا واجهت أي مشاكل أو لديك اقتراحات، يرجى فتح [Issue](https://github.com/AnwerAhmedAnwer16/back_final/issues) جديد.
