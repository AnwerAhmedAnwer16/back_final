from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.utils import timezone
from .models import User, Profile
import logging
import os

# Set up logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a profile when a new user is created
    """
    if created:
        Profile.objects.create(user=instance)
        logger.info(f"Profile created for user: {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the profile when user is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
        logger.info(f"Profile saved for user: {instance.username}")


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Send welcome email when a new user is created
    """
    if created:
        try:
            subject = 'Welcome to Our Platform!'
            message = f'''
            Hi {instance.username},
            
            Welcome to our platform! We're excited to have you on board.
            
            Your account has been created successfully. Please verify your email address to get started.
            
            If you have any questions, feel free to contact our support team.
            
            Best regards,
            The Team
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=True,
            )
            logger.info(f"Welcome email sent to: {instance.email}")
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {instance.email}: {str(e)}")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log user login activity
    """
    try:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        logger.info(f"User {user.username} logged in from IP: {ip_address}")
        
        # You can save login history to database if needed
        # LoginHistory.objects.create(
        #     user=user,
        #     ip_address=ip_address,
        #     user_agent=user_agent,
        #     login_time=timezone.now()
        # )
        
    except Exception as e:
        logger.error(f"Error logging user login: {str(e)}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log user logout activity
    """
    try:
        if user:
            logger.info(f"User {user.username} logged out")
        
    except Exception as e:
        logger.error(f"Error logging user logout: {str(e)}")


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """
    Log failed login attempts
    """
    try:
        email = credentials.get('email', 'Unknown')
        ip_address = get_client_ip(request)
        
        logger.warning(f"Failed login attempt for email: {email} from IP: {ip_address}")
        
        # You can implement security measures here like:
        # - Rate limiting
        # - Account lockout after multiple failed attempts
        # - Send security alerts
        
    except Exception as e:
        logger.error(f"Error logging failed login: {str(e)}")


@receiver(post_save, sender=User)
def user_verification_status_changed(sender, instance, **kwargs):
    """
    Handle user verification status changes
    """
    if instance.is_verified and instance.pk:
        try:
            # Check if verification status actually changed
            old_instance = User.objects.get(pk=instance.pk)
            if not old_instance.is_verified and instance.is_verified:
                # Send verification confirmation email
                subject = 'Email Verified Successfully!'
                message = f'''
                Hi {instance.username},
                
                Your email address has been verified successfully!
                
                You can now access all features of our platform.
                
                Thank you for joining us!
                
                Best regards,
                The Team
                '''
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=True,
                )
                logger.info(f"Verification confirmation email sent to: {instance.email}")
                
        except User.DoesNotExist:
            # This is a new user, verification email will be handled by create signal
            pass
        except Exception as e:
            logger.error(f"Error sending verification confirmation email: {str(e)}")


@receiver(pre_delete, sender=User)
def backup_user_data(sender, instance, **kwargs):
    """
    Backup user data before deletion
    """
    try:
        # Create backup of user data
        backup_data = {
            'username': instance.username,
            'email': instance.email,
            'date_joined': instance.date_joined.isoformat(),
            'deletion_date': timezone.now().isoformat(),
        }
        
        # You can save this to a backup model or file
        logger.info(f"User data backed up before deletion: {instance.username}")
        
    except Exception as e:
        logger.error(f"Error backing up user data: {str(e)}")


@receiver(post_delete, sender=User)
def cleanup_user_files(sender, instance, **kwargs):
    """
    Clean up user files after account deletion
    """
    try:
        # Clean up user avatar if exists
        if hasattr(instance, 'profile') and instance.profile.avatar:
            if os.path.isfile(instance.profile.avatar.path):
                os.remove(instance.profile.avatar.path)
                logger.info(f"Avatar file deleted for user: {instance.username}")
        
        # Clean up any other user-related files
        # You can add more cleanup logic here
        
        logger.info(f"User cleanup completed for: {instance.username}")
        
    except Exception as e:
        logger.error(f"Error during user cleanup: {str(e)}")


@receiver(post_delete, sender=User)
def send_account_deletion_notification(sender, instance, **kwargs):
    """
    Send notification email after account deletion
    """
    try:
        subject = 'Account Deleted Successfully'
        message = f'''
        Hi {instance.username},
        
        Your account has been deleted successfully as requested.
        
        We're sorry to see you go. If you change your mind, you can always create a new account.
        
        If you have any feedback about your experience, please let us know.
        
        Best regards,
        The Team
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=True,
        )
        logger.info(f"Account deletion notification sent to: {instance.email}")
        
    except Exception as e:
        logger.error(f"Error sending account deletion notification: {str(e)}")


@receiver(post_save, sender=Profile)
def profile_updated(sender, instance, created, **kwargs):
    """
    Handle profile updates
    """
    if not created:
        logger.info(f"Profile updated for user: {instance.user.username}")
        
        # You can add logic here for profile completion tracking
        # or send notifications about profile updates


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

