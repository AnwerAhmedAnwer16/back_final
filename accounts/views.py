# Google OAuth2 Endpoints:
# - GET /api/accounts/google-oauth2-login-url/ : للحصول على رابط تسجيل الدخول عبر Google
# - POST /api/accounts/google-login/ : تسجيل الدخول باستخدام access_token من Google
from .serializers import UserSerializer
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from social_django.utils import load_strategy
from social_core.backends.google import GoogleOAuth2

# Endpoint to get Google OAuth2 login URL
@api_view(['GET'])
def google_oauth2_login_url(request):
    try:
        strategy = load_strategy(request)
        backend = GoogleOAuth2(strategy=strategy)
        redirect_uri = request.build_absolute_uri(reverse('social:complete', args=('google-oauth2',)))
        url = backend.auth_url()
        return Response({'auth_url': url}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login
from social_django.utils import psa
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# Google OAuth2 Login API
@api_view(['POST'])
def google_login(request):
    token = request.data.get('access_token')
    if not token:
        return Response({'error': 'Missing access token'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        strategy = load_strategy(request)
        backend = GoogleOAuth2(strategy=strategy)
        user = backend.do_auth(token)
        if user and user.is_active:
            login(request, user)
            return Response({'message': 'Login successful', 'user': UserSerializer(user).data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Authentication failed'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404
from .models import User, Profile
from .serializers import (
    UserSerializer, ProfileSerialzer, CustomTokenObtainPairSerializer,
    UserRegistrationSerializer, PasswordChangeSerializer, PasswordResetSerializer,
    PasswordStrengthSerializer, PublicUserProfileSerializer
)
from .utils import validate_password_strength, calculate_password_strength, get_password_requirements

# Create your views here.

class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # تحقق إذا كان للمستخدم ملف شخصي بالفعل قبل الإنشاء
            from .models import Profile
            if not Profile.objects.filter(user=user).exists():
                Profile.objects.create(user=user)
            self.send_verification_email(user)

            return Response({
                'message': 'User created successfully. Please check your email for verification.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def send_verification_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"
        
        subject = 'Verify your email address'
        message = f'''
        Hi {user.username},
        
        Please click the link below to verify your email address:
        {verification_link}
        
        If you didn't create this account, please ignore this email.
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
class CustomTokenObtainPairView(TokenObtainPairView):
        serializer_class = CustomTokenObtainPairSerializer
    
        def post(self, request, *args, **kwargs):
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                email = request.data.get('email')
                user = User.objects.get(email=email)
                response.data['user'] = UserSerializer(user).data
            return response


class LogoutView(APIView):
        permission_classes = [permissions.IsAuthenticated]
    
        def post(self, request):
            try:
                refresh_token = request.data.get('refresh_token')
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"Email verification attempt - UID: {uidb64}, Token: {token}")

        try:
            # فك تشفير UID
            uid = force_str(urlsafe_base64_decode(uidb64))
            logger.info(f"Decoded UID: {uid}")

            # البحث عن المستخدم
            user = User.objects.get(pk=uid)
            logger.info(f"Found user: {user.email}, is_verified: {user.is_verified}")

            # التحقق من أن المستخدم غير مفعل بالفعل
            if user.is_verified:
                logger.info(f"User {user.email} is already verified")
                return Response({
                    'message': 'Email is already verified',
                    'user_email': user.email
                }, status=status.HTTP_200_OK)

            # التحقق من صحة التوكن
            if default_token_generator.check_token(user, token):
                user.is_verified = True
                user.save()
                logger.info(f"Email verified successfully for user: {user.email}")

                return Response({
                    'message': 'Email verified successfully',
                    'user_email': user.email,
                    'user_id': user.id
                }, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Invalid token for user {user.email}")
                return Response({
                    'error': 'Invalid or expired verification link',
                    'details': 'The verification link may have expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError, OverflowError) as e:
            logger.error(f"UID decoding error: {str(e)}")
            return Response({
                'error': 'Invalid verification link format',
                'details': 'The verification link appears to be corrupted.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            logger.error(f"User not found for UID: {uid}")
            return Response({
                'error': 'User not found',
                'details': 'The user associated with this verification link does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Unexpected error during email verification: {str(e)}")
            return Response({
                'error': 'Verification failed',
                'details': 'An unexpected error occurred. Please try again or contact support.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, uidb64, token):
        """دعم GET request للتوافق مع الروابط في البريد الإلكتروني"""
        return self.post(request, uidb64, token)


class CheckVerificationTokenView(APIView):
    """فحص صحة رابط التحقق بدون تفعيله"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"Token check attempt - UID: {uidb64}, Token: {token}")

        try:
            # فك تشفير UID
            uid = force_str(urlsafe_base64_decode(uidb64))
            logger.info(f"Decoded UID: {uid}")

            # البحث عن المستخدم
            user = User.objects.get(pk=uid)
            logger.info(f"Found user: {user.email}, is_verified: {user.is_verified}")

            # التحقق من صحة التوكن
            is_valid = default_token_generator.check_token(user, token)

            return Response({
                'is_valid': is_valid,
                'user_email': user.email,
                'user_id': user.id,
                'is_already_verified': user.is_verified,
                'token_info': {
                    'uid': uidb64,
                    'token': token,
                    'decoded_uid': uid
                }
            }, status=status.HTTP_200_OK)

        except (TypeError, ValueError, OverflowError) as e:
            logger.error(f"UID decoding error: {str(e)}")
            return Response({
                'is_valid': False,
                'error': 'Invalid UID format',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            logger.error(f"User not found for UID: {uid}")
            return Response({
                'is_valid': False,
                'error': 'User not found',
                'details': f'No user found with ID: {uid}'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Unexpected error during token check: {str(e)}")
            return Response({
                'is_valid': False,
                'error': 'Check failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateVerificationLinkView(APIView):
    """إنشاء رابط تحقق جديد لمستخدم موجود (للاختبار)"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            # إنشاء رابط تحقق جديد
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"
            api_verification_link = f"http://localhost:8000/api/accounts/verify-email/{uid}/{token}/"
            check_link = f"http://localhost:8000/api/accounts/check-verification/{uid}/{token}/"

            return Response({
                'message': 'Verification link generated',
                'user_email': user.email,
                'user_id': user.id,
                'is_verified': user.is_verified,
                'verification_link': verification_link,
                'api_verification_link': api_verification_link,
                'check_link': check_link,
                'token_info': {
                    'uid': uid,
                    'token': token
                }
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)


class PasswordStrengthCheckView(APIView):
    """فحص قوة كلمة المرور"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordStrengthSerializer(data=request.data)

        if serializer.is_valid():
            password = serializer.validated_data['password']
            strength_info = calculate_password_strength(password)
            validation_errors = validate_password_strength(password)

            return Response({
                'strength': strength_info,
                'validation_errors': validation_errors,
                'is_valid': len(validation_errors) == 0
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordRequirementsView(APIView):
    """الحصول على متطلبات كلمة المرور"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        requirements = get_password_requirements()

        return Response({
            'requirements': requirements,
            'description': {
                'ar': {
                    'min_length': f'يجب أن تكون كلمة المرور {requirements["min_length"]} أحرف على الأقل',
                    'require_letters': 'يجب أن تحتوي على حروف',
                    'require_digit': 'يجب أن تحتوي على رقم واحد على الأقل',
                    'require_special': f'يجب أن تحتوي على رمز خاص واحد على الأقل ({requirements["special_chars"]})'
                },
                'en': {
                    'min_length': f'Password must be at least {requirements["min_length"]} characters long',
                    'require_letters': 'Must contain letters',
                    'require_digit': 'Must contain at least one digit',
                    'require_special': f'Must contain at least one special character ({requirements["special_chars"]})'
                }
            }
        }, status=status.HTTP_200_OK)


class ValidatePasswordView(APIView):
    """التحقق من صحة كلمة المرور مع بيانات المستخدم"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        password = request.data.get('password')

        if not password:
            return Response({
                'error': 'Password is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # التحقق مع بيانات المستخدم
        validation_errors = validate_password_strength(password, request.user)
        strength_info = calculate_password_strength(password)

        return Response({
            'is_valid': len(validation_errors) == 0,
            'validation_errors': validation_errors,
            'strength': strength_info,
            'user_context': {
                'email': request.user.email,
                'username': request.user.username
            }
        }, status=status.HTTP_200_OK)

class ResendVerificationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                return Response({'message': 'Email already verified'}, status=status.HTTP_200_OK)
            
            # Send verification email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"
            
            subject = 'Verify your email address'
            message = f'''
            Hi {user.username},
            
            Please click the link below to verify your email address:
            {verification_link}
            
            If you didn't create this account, please ignore this email.
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return Response({'message': 'Verification email sent'}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            subject = 'Password Reset Request'
            message = f'''
            Hi {user.username},
            
            You requested a password reset. Click the link below to reset your password:
            {reset_link}
            
            If you didn't request this, please ignore this email.
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                serializer = PasswordResetSerializer(data=request.data)

                if serializer.is_valid():
                    new_password = serializer.validated_data['new_password']
                    user.set_password(new_password)
                    user.save()

                    return Response({
                        'message': 'Password reset successfully',
                        'user_email': user.email
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']

            user.set_password(new_password)
            user.save()

            return Response({
                'message': 'Password changed successfully',
                'user_id': user.id
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
   
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ProfileDetailView(generics.RetrieveUpdateAPIView):

    serializer_class = ProfileSerialzer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


class PublicUserProfileView(generics.RetrieveAPIView):
    """عرض البروفايل العام لأي مستخدم مع رحلاته وإحصائياته"""
    serializer_class = PublicUserProfileSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.select_related('profile').prefetch_related(
            'followers', 'following', 'trips'
        )

    def get_object(self):
        user_id = self.kwargs.get('id')
        try:
            user = self.get_queryset().get(id=user_id)
            return user
        except User.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('المستخدم غير موجود')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
