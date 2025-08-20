# Password Validation System - دليل نظام التحقق من كلمة المرور

## 🔐 نظام بسيط وفعال للتحقق من كلمة المرور

تم تطوير نظام مبسط للتحقق من قوة وصحة كلمات المرور مع دعم كامل للغة العربية والإنجليزية.

## 🛡️ متطلبات كلمة المرور (مبسطة)

### المتطلبات الأساسية:
- **الطول الأدنى:** 8 أحرف
- **حروف:** يجب أن تحتوي على حروف (كبيرة أو صغيرة)
- **أرقام:** رقم واحد على الأقل (0-9)
- **رموز خاصة:** رمز خاص واحد على الأقل (!@#$%^&*()_+-=[]{}|;:,.<>?~`)

## 🚀 API Endpoints

### 1. فحص قوة كلمة المرور
```http
POST /api/accounts/password-strength-check/
```

**Request Body:**
```json
{
    "password": "MyPass123!"
}
```

**Response:**
```json
{
    "strength": {
        "score": 90,
        "strength": "قوي",
        "color": "green",
        "feedback": [],
        "requirements": {
            "length": true,
            "letters": true,
            "digit": true,
            "special": true
        }
    },
    "validation_errors": [],
    "is_valid": true
}
```

### 2. الحصول على متطلبات كلمة المرور
```http
GET /api/accounts/password-requirements/
```

**Response:**
```json
{
    "requirements": {
        "min_length": 8,
        "require_letters": true,
        "require_digit": true,
        "require_special": true,
        "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?~`"
    },
    "description": {
        "ar": {
            "min_length": "يجب أن تكون كلمة المرور 8 أحرف على الأقل",
            "require_letters": "يجب أن تحتوي على حروف",
            "require_digit": "يجب أن تحتوي على رقم واحد على الأقل",
            "require_special": "يجب أن تحتوي على رمز خاص واحد على الأقل"
        },
        "en": {
            "min_length": "Password must be at least 8 characters long",
            "require_letters": "Must contain letters",
            "require_digit": "Must contain at least one digit",
            "require_special": "Must contain at least one special character"
        }
    }
}
```

### 3. التحقق من كلمة المرور مع سياق المستخدم
```http
POST /api/accounts/validate-password/
Authorization: Bearer {token}
```

**Request Body:**
```json
{
    "password": "test123!"
}
```

**Response:**
```json
{
    "is_valid": false,
    "validation_errors": [
        {
            "code": "password_similar_to_email",
            "message": "كلمة المرور يجب ألا تكون مشابهة لبريدك الإلكتروني",
            "message_en": "Password must not be similar to your email"
        }
    ],
    "strength": {
        "score": 45,
        "strength": "ضعيف",
        "color": "orange"
    },
    "user_context": {
        "email": "test@example.com",
        "username": "testuser"
    }
}
```

### 4. تسجيل مستخدم جديد مع validation
```http
POST /api/accounts/register/
```

**Request Body:**
```json
{
    "email": "user@example.com",
    "username": "newuser",
    "password": "MyPass123!",
    "password_confirm": "MyPass123!"
}
```

### 5. تغيير كلمة المرور مع validation
```http
POST /api/accounts/change-password/
Authorization: Bearer {token}
```

**Request Body:**
```json
{
    "old_password": "OldPass123!",
    "new_password": "NewPass456!",
    "new_password_confirm": "NewPass456!"
}
```

### 6. إعادة تعيين كلمة المرور مع validation
```http
POST /api/accounts/password-reset-confirm/{uid}/{token}/
```

**Request Body:**
```json
{
    "new_password": "NewPass789!",
    "new_password_confirm": "NewPass789!"
}
```

## 📊 نظام تقييم قوة كلمة المرور (مبسط)

### مستويات القوة:
- **0-39:** ضعيف (أحمر)
- **40-69:** متوسط (برتقالي)
- **70-100:** قوي (أخضر)

### معايير التقييم:
- **الطول 8+:** +30 نقطة
- **الطول 12+:** +10 نقاط إضافية
- **وجود حروف:** +20 نقطة
- **وجود أرقام:** +20 نقطة
- **وجود رموز خاصة:** +20 نقطة

## 🔍 رموز الأخطاء (مبسطة)

| الكود | الوصف العربي | الوصف الإنجليزي |
|-------|--------------|------------------|
| `password_too_short` | كلمة المرور قصيرة جداً | Password too short |
| `password_no_letters` | لا تحتوي على حروف | No letters |
| `password_no_digit` | لا تحتوي على أرقام | No digits |
| `password_no_special` | لا تحتوي على رموز خاصة | No special characters |

## 💻 Frontend Integration

### JavaScript Example:
```javascript
class PasswordValidator {
    constructor() {
        this.apiBase = 'http://localhost:8000/api/accounts';
    }

    async checkPasswordStrength(password) {
        const response = await fetch(`${this.apiBase}/password-strength-check/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password })
        });
        return await response.json();
    }

    async getRequirements() {
        const response = await fetch(`${this.apiBase}/password-requirements/`);
        return await response.json();
    }

    displayStrength(strengthData) {
        const { score, strength, color, requirements } = strengthData;

        // Update progress bar
        const progressBar = document.getElementById('password-strength-bar');
        progressBar.style.width = `${score}%`;
        progressBar.style.backgroundColor = color;

        // Update strength text
        document.getElementById('strength-text').textContent = strength;

        // Update requirements checklist
        Object.keys(requirements).forEach(req => {
            const element = document.getElementById(`req-${req}`);
            if (element) {
                element.className = requirements[req] ? 'valid' : 'invalid';
            }
        });
    }
}

// Usage
const validator = new PasswordValidator();

document.getElementById('password-input').addEventListener('input', async (e) => {
    const password = e.target.value;
    if (password.length > 0) {
        const result = await validator.checkPasswordStrength(password);
        validator.displayStrength(result.strength);
    }
});
```

### HTML Example:
```html
<div class="password-strength-container">
    <input type="password" id="password-input" placeholder="أدخل كلمة المرور">
    
    <div class="strength-meter">
        <div id="password-strength-bar" class="strength-bar"></div>
    </div>
    
    <div id="strength-text" class="strength-text"></div>
    
    <div class="requirements-list">
        <div id="req-length" class="requirement">✓ 8 أحرف على الأقل</div>
        <div id="req-letters" class="requirement">✓ حروف</div>
        <div id="req-digit" class="requirement">✓ رقم</div>
        <div id="req-special" class="requirement">✓ رمز خاص</div>
    </div>
</div>
```

### CSS Example:
```css
.password-strength-container {
    max-width: 400px;
    margin: 20px auto;
}

.strength-meter {
    width: 100%;
    height: 8px;
    background-color: #e0e0e0;
    border-radius: 4px;
    margin: 10px 0;
    overflow: hidden;
}

.strength-bar {
    height: 100%;
    transition: all 0.3s ease;
    border-radius: 4px;
}

.strength-text {
    text-align: center;
    font-weight: bold;
    margin: 10px 0;
}

.requirements-list {
    margin-top: 15px;
}

.requirement {
    padding: 5px 0;
    transition: color 0.3s ease;
}

.requirement.valid {
    color: green;
}

.requirement.invalid {
    color: red;
}
```

## 🧪 Testing

### تشغيل الاختبارات:
```bash
# تشغيل جميع اختبارات كلمة المرور
python manage.py test accounts.tests.PasswordValidationTests

# تشغيل اختبار محدد
python manage.py test accounts.tests.PasswordValidationTests.test_password_strength_check_endpoint
```

### أمثلة اختبار:
```python
# اختبار كلمة مرور ضعيفة
response = self.client.post('/api/accounts/password-strength-check/', {
    'password': '123456'
})
self.assertFalse(response.data['is_valid'])

# اختبار كلمة مرور قوية
response = self.client.post('/api/accounts/password-strength-check/', {
    'password': 'MyPass123!'
})
self.assertTrue(response.data['is_valid'])
```

## 📝 ملاحظات مهمة

1. **الأمان:** جميع كلمات المرور يتم تشفيرها باستخدام Django's built-in hashing
2. **الأداء:** التحقق يتم على الخادم لضمان الأمان
3. **التوافق:** يدعم جميع المتصفحات الحديثة
4. **اللغة:** دعم كامل للعربية والإنجليزية
5. **التخصيص:** يمكن تخصيص المتطلبات حسب الحاجة

## 🔧 التخصيص

لتخصيص متطلبات كلمة المرور، قم بتعديل function `get_password_requirements()` في `accounts/utils.py`:

```python
def get_password_requirements():
    return {
        "min_length": 10,  # تغيير الطول الأدنى
        "require_special": False,  # إلغاء متطلب الرموز الخاصة
        # ... باقي المتطلبات
    }
```
