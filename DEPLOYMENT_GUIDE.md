# 🚀 دليل النشر والصيانة - مشروع Rahala

## 📋 جدول المحتويات
- [نظرة عامة](#نظرة-عامة)
- [إعداد الإنتاج](#إعداد-الإنتاج)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Database Setup](#database-setup)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Performance Optimization](#performance-optimization)

---

## 🎯 نظرة عامة

هذا الدليل يغطي نشر مشروع Rahala في بيئة الإنتاج مع أفضل الممارسات للأمان والأداء.

### متطلبات الإنتاج:
- 🐧 **Ubuntu 20.04+** أو **CentOS 8+**
- 🐍 **Python 3.11+**
- 🗄️ **PostgreSQL 13+**
- 🔴 **Redis 6+**
- 🌐 **Nginx**
- 🔒 **SSL Certificate**
- 🐳 **Docker** (اختياري)

---

## ⚙️ إعداد الإنتاج

### 1. إعداد الخادم:

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات الأساسية
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server
sudo apt install -y nginx
sudo apt install -y git curl wget

# إنشاء مستخدم للتطبيق
sudo adduser rahala
sudo usermod -aG sudo rahala
```

### 2. إعداد قاعدة البيانات:

```bash
# تسجيل الدخول لـ PostgreSQL
sudo -u postgres psql

-- إنشاء قاعدة البيانات والمستخدم
CREATE DATABASE rahala_prod;
CREATE USER rahala_user WITH PASSWORD 'secure_password_here';
ALTER ROLE rahala_user SET client_encoding TO 'utf8';
ALTER ROLE rahala_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE rahala_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE rahala_prod TO rahala_user;
\q
```

### 3. إعداد Redis:

```bash
# تحرير إعدادات Redis
sudo nano /etc/redis/redis.conf

# إضافة كلمة مرور
requirepass your_redis_password_here

# إعادة تشغيل Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### 4. نشر التطبيق:

```bash
# التبديل للمستخدم rahala
sudo su - rahala

# استنساخ المشروع
git clone https://github.com/your-repo/rahala.git
cd rahala

# إنشاء البيئة الافتراضية
python3.11 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# إعداد متغيرات البيئة
cp .env.example .env.production
nano .env.production
```

### 5. إعدادات الإنتاج (.env.production):

```env
# Django Settings
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://rahala_user:secure_password_here@localhost:5432/rahala_prod

# Redis
REDIS_URL=redis://:your_redis_password_here@localhost:6379/0

# Email (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Google OAuth2
GOOGLE_OAUTH2_CLIENT_ID=your-production-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-production-client-secret

# OpenRouter AI
OPENROUTER_API_KEY=sk-or-v1-your-production-api-key
OPENROUTER_MODEL=gpt-oss-20b
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# PayMob (Production)
PAYMOB_API_KEY=your-production-paymob-key
PAYMOB_INTEGRATION_ID=your-production-integration-id
PAYMOB_IFRAME_ID=your-production-iframe-id
PAYMOB_BASE_URL=https://accept.paymob.com/api

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### 6. تطبيق التغييرات:

```bash
# تطبيق migrations
python manage.py migrate

# جمع الملفات الثابتة
python manage.py collectstatic --noinput

# إنشاء superuser
python manage.py createsuperuser

# اختبار التطبيق
python manage.py check --deploy
```

---

## 🐳 Docker Deployment

### 1. Dockerfile:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# إعداد مجلد العمل
WORKDIR /app

# نسخ متطلبات Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كود التطبيق
COPY . .

# إنشاء مستخدم غير root
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# تعريف المنفذ
EXPOSE 8000

# أمر التشغيل
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "Rahala.wsgi:application"]
```

### 2. docker-compose.yml:

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: rahala_prod
      POSTGRES_USER: rahala_user
      POSTGRES_PASSWORD: secure_password_here
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    command: redis-server --requirepass your_redis_password_here
    ports:
      - "6379:6379"

  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 Rahala.wsgi:application
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://rahala_user:secure_password_here@db:5432/rahala_prod
      - REDIS_URL=redis://:your_redis_password_here@redis:6379/0

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

  celery:
    build: .
    command: celery -A Rahala worker -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://rahala_user:secure_password_here@db:5432/rahala_prod
      - REDIS_URL=redis://:your_redis_password_here@redis:6379/0

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### 3. تشغيل Docker:

```bash
# بناء وتشغيل الحاويات
docker-compose up -d --build

# تطبيق migrations
docker-compose exec web python manage.py migrate

# جمع الملفات الثابتة
docker-compose exec web python manage.py collectstatic --noinput

# إنشاء superuser
docker-compose exec web python manage.py createsuperuser
```

---

## ☁️ Cloud Deployment

### 1. AWS Deployment:

```bash
# تثبيت AWS CLI
pip install awscli

# إعداد AWS credentials
aws configure

# إنشاء EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1d0 \
  --count 1 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx
```

### 2. إعداد RDS (PostgreSQL):

```bash
# إنشاء RDS instance
aws rds create-db-instance \
  --db-instance-identifier rahala-prod-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username rahala_user \
  --master-user-password secure_password_here \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxxx
```

### 3. إعداد ElastiCache (Redis):

```bash
# إنشاء Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id rahala-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

### 4. إعداد S3 للملفات:

```python
# settings.py - إضافة S3 configuration
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')

# استخدام S3 للملفات الثابتة والوسائط
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'

AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

---

## 🌐 Nginx Configuration

### nginx.conf:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream rahala_app {
        server web:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Security Headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

        # Static files
        location /static/ {
            alias /app/staticfiles/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Media files
        location /media/ {
            alias /app/media/;
            expires 1y;
            add_header Cache-Control "public";
        }

        # API endpoints with rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://rahala_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Login endpoint with stricter rate limiting
        location /api/accounts/login/ {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://rahala_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Admin panel
        location /admin/ {
            allow 192.168.1.0/24;  # Allow only from specific IP range
            deny all;
            proxy_pass http://rahala_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend (React app)
        location / {
            root /var/www/rahala-frontend/build;
            try_files $uri $uri/ /index.html;
        }
    }
}
```

---

## 🔧 Systemd Services

### 1. Gunicorn Service:

```ini
# /etc/systemd/system/rahala.service
[Unit]
Description=Rahala Django App
After=network.target

[Service]
User=rahala
Group=rahala
WorkingDirectory=/home/rahala/rahala
Environment=PATH=/home/rahala/rahala/venv/bin
EnvironmentFile=/home/rahala/rahala/.env.production
ExecStart=/home/rahala/rahala/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/rahala/rahala/rahala.sock \
    Rahala.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Celery Service:

```ini
# /etc/systemd/system/rahala-celery.service
[Unit]
Description=Rahala Celery Worker
After=network.target

[Service]
User=rahala
Group=rahala
WorkingDirectory=/home/rahala/rahala
Environment=PATH=/home/rahala/rahala/venv/bin
EnvironmentFile=/home/rahala/rahala/.env.production
ExecStart=/home/rahala/rahala/venv/bin/celery -A Rahala worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. تفعيل الخدمات:

```bash
# تفعيل وتشغيل الخدمات
sudo systemctl enable rahala
sudo systemctl enable rahala-celery
sudo systemctl start rahala
sudo systemctl start rahala-celery

# التحقق من الحالة
sudo systemctl status rahala
sudo systemctl status rahala-celery
```

---

## 📊 Monitoring & Logging

### 1. إعداد Logging:

```python
# settings.py - Production logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/rahala/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/rahala/django_errors.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'trip.ai_services': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 2. Health Check Endpoint:

```python
# health/views.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis

def health_check(request):
    """فحص صحة النظام"""
    status = {
        'status': 'healthy',
        'database': 'unknown',
        'redis': 'unknown',
        'timestamp': timezone.now().isoformat()
    }
    
    # فحص قاعدة البيانات
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['database'] = 'healthy'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
    
    # فحص Redis
    try:
        cache.set('health_check', 'ok', 30)
        if cache.get('health_check') == 'ok':
            status['redis'] = 'healthy'
        else:
            status['redis'] = 'error'
            status['status'] = 'unhealthy'
    except Exception as e:
        status['redis'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'
    
    return JsonResponse(status)
```

### 3. Monitoring Script:

```bash
#!/bin/bash
# monitor.sh - مراقبة النظام

LOG_FILE="/var/log/rahala/monitor.log"
HEALTH_URL="https://your-domain.com/health/"

# فحص صحة التطبيق
check_health() {
    response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)
    if [ $response -eq 200 ]; then
        echo "$(date): Health check passed" >> $LOG_FILE
    else
        echo "$(date): Health check failed - HTTP $response" >> $LOG_FILE
        # إرسال تنبيه
        send_alert "Rahala health check failed"
    fi
}

# فحص استخدام القرص
check_disk_usage() {
    usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $usage -gt 80 ]; then
        echo "$(date): Disk usage high: ${usage}%" >> $LOG_FILE
        send_alert "Disk usage is ${usage}%"
    fi
}

# إرسال تنبيه
send_alert() {
    message=$1
    # يمكن إرسال email أو Slack notification
    echo "ALERT: $message" >> $LOG_FILE
}

# تشغيل الفحوصات
check_health
check_disk_usage
```

---

## 💾 Backup & Recovery

### 1. Database Backup:

```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/backups/rahala"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="rahala_prod"
DB_USER="rahala_user"

# إنشاء مجلد النسخ الاحتياطية
mkdir -p $BACKUP_DIR

# نسخ احتياطي لقاعدة البيانات
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# ضغط النسخة الاحتياطية
gzip $BACKUP_DIR/db_backup_$DATE.sql

# حذف النسخ القديمة (أكثر من 30 يوم)
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: db_backup_$DATE.sql.gz"
```

### 2. Media Files Backup:

```bash
#!/bin/bash
# backup_media.sh

MEDIA_DIR="/home/rahala/rahala/media"
BACKUP_DIR="/backups/rahala/media"
DATE=$(date +%Y%m%d_%H%M%S)

# نسخ احتياطي للملفات
rsync -av --delete $MEDIA_DIR/ $BACKUP_DIR/media_$DATE/

# ضغط النسخة الاحتياطية
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C $BACKUP_DIR media_$DATE/
rm -rf $BACKUP_DIR/media_$DATE/

echo "Media backup completed: media_backup_$DATE.tar.gz"
```

### 3. Automated Backup (Crontab):

```bash
# إضافة للـ crontab
crontab -e

# نسخ احتياطي يومي في الساعة 2:00 صباحاً
0 2 * * * /home/rahala/scripts/backup_db.sh
30 2 * * * /home/rahala/scripts/backup_media.sh

# نسخ احتياطي أسبوعي للكود
0 3 * * 0 tar -czf /backups/rahala/code_backup_$(date +\%Y\%m\%d).tar.gz -C /home/rahala rahala/
```

---

## ⚡ Performance Optimization

### 1. Database Optimization:

```sql
-- إنشاء indexes مهمة
CREATE INDEX CONCURRENTLY idx_trip_created_at ON trip_trip(created_at);
CREATE INDEX CONCURRENTLY idx_trip_country_city ON trip_trip(country, city);
CREATE INDEX CONCURRENTLY idx_trip_user_created ON trip_trip(user_id, created_at);

-- تحليل الجداول
ANALYZE;

-- إعدادات PostgreSQL للأداء
-- في postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

### 2. Redis Optimization:

```bash
# redis.conf optimizations
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 3. Django Settings Optimization:

```python
# settings.py - Production optimizations

# Database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rahala_prod',
        'USER': 'rahala_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'MAX_CONNS': 20,
        }
    }
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        }
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Static files optimization
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

---

## 🔒 Security Checklist

### Production Security:
- ✅ DEBUG = False
- ✅ Strong SECRET_KEY
- ✅ HTTPS enabled
- ✅ Security headers configured
- ✅ Database credentials secured
- ✅ API rate limiting enabled
- ✅ Admin panel IP restricted
- ✅ Regular security updates
- ✅ Backup encryption
- ✅ Log monitoring

### SSL Certificate (Let's Encrypt):

```bash
# تثبيت Certbot
sudo apt install certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# تجديد تلقائي
sudo crontab -e
0 12 * * * /usr/bin/certbot renew --quiet
```

---

**🎯 مع هذا الدليل، ستتمكن من نشر مشروع Rahala بأمان وكفاءة عالية في بيئة الإنتاج!**
