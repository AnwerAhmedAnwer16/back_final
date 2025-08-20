from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import logging

logger = logging.getLogger(__name__)


def send_html_email(subject, template_name, context, recipient_list, from_email=None):
  
    try:
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL
        
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"HTML email sent successfully to: {recipient_list}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send HTML email: {str(e)}")
        return False


def generate_verification_token(user):
   
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid, token


def get_client_ip(request):
   
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
   
    return request.META.get('HTTP_USER_AGENT', '')


def validate_password_strength(password, user=None):
    """
    تحقق بسيط من قوة كلمة المرور
    المتطلبات: 8 أحرف على الأقل + حروف + أرقام + رموز خاصة
    """
    errors = []

    # التحقق من الطول الأدنى
    if len(password) < 8:
        errors.append({
            "code": "password_too_short",
            "message": "كلمة المرور يجب أن تكون 8 أحرف على الأقل",
            "message_en": "Password must be at least 8 characters long"
        })

    # التحقق من وجود أحرف (كبيرة أو صغيرة)
    if not any(char.isalpha() for char in password):
        errors.append({
            "code": "password_no_letters",
            "message": "كلمة المرور يجب أن تحتوي على حروف",
            "message_en": "Password must contain letters"
        })

    # التحقق من وجود أرقام
    if not any(char.isdigit() for char in password):
        errors.append({
            "code": "password_no_digit",
            "message": "كلمة المرور يجب أن تحتوي على رقم واحد على الأقل",
            "message_en": "Password must contain at least one digit"
        })

    # التحقق من وجود رموز خاصة
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?~`"
    if not any(char in special_chars for char in password):
        errors.append({
            "code": "password_no_special",
            "message": "كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل (!@#$%^&*)",
            "message_en": "Password must contain at least one special character (!@#$%^&*)"
        })

    return errors


def calculate_password_strength(password):
    """
    حساب قوة كلمة المرور من 0 إلى 100 (مبسط)
    """
    score = 0
    feedback = []

    # نقاط الطول
    length = len(password)
    if length >= 8:
        score += 30
    if length >= 12:
        score += 10

    # نقاط التنوع
    has_letters = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?~`" for c in password)

    if has_letters:
        score += 20
    if has_digit:
        score += 20
    if has_special:
        score += 20

    # تحديد مستوى القوة
    if score < 40:
        strength = "ضعيف"
        color = "red"
    elif score < 70:
        strength = "متوسط"
        color = "orange"
    else:
        strength = "قوي"
        color = "green"

    return {
        "score": min(100, max(0, score)),
        "strength": strength,
        "color": color,
        "feedback": feedback,
        "requirements": {
            "length": length >= 8,
            "letters": has_letters,
            "digit": has_digit,
            "special": has_special
        }
    }


def get_password_requirements():
    """
    إرجاع متطلبات كلمة المرور المبسطة
    """
    return {
        "min_length": 8,
        "require_letters": True,
        "require_digit": True,
        "require_special": True,
        "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?~`"
    }


def generate_username_from_email(email):
   
    username = email.split('@')[0]
    username = ''.join(char for char in username if char.isalnum() or char in '_-')
    return username[:20]  


def format_user_display_name(user):
  
    if hasattr(user, 'profile') and user.profile:
        if user.profile.first_name and user.profile.last_name:
            return f"{user.profile.first_name} {user.profile.last_name}"
        elif user.profile.first_name:
            return user.profile.first_name
    
    return user.username


def is_email_verified(user):
    
    return user.is_verified


def get_user_avatar_url(user, request=None):
    
    if hasattr(user, 'profile') and user.profile and user.profile.avatar:
        if request:
            return request.build_absolute_uri(user.profile.avatar.url)
        return user.profile.avatar.url
    return None


def sanitize_filename(filename):
    
    import re
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    return filename


def generate_unique_filename(instance, filename):
    
    import uuid
    import os
    
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return filename

