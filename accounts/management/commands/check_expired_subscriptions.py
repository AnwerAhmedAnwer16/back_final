from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.services import SubscriptionService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check and handle expired subscriptions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS('Starting expired subscriptions check...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        try:
            if not dry_run:
                expired_count = SubscriptionService.check_expired_subscriptions()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully processed {expired_count} expired subscriptions'
                    )
                )
            else:
                # في وضع dry-run، نعرض فقط الاشتراكات المنتهية
                from accounts.models import User
                expired_users = User.objects.filter(
                    subscription_end_date__lt=timezone.now(),
                    subscription_plan__in=['premium', 'pro']
                )
                
                self.stdout.write(
                    self.style.WARNING(
                        f'Found {expired_users.count()} expired subscriptions:'
                    )
                )
                
                for user in expired_users:
                    self.stdout.write(
                        f'  - {user.username} ({user.email}) - '
                        f'Plan: {user.subscription_plan}, '
                        f'Expired: {user.subscription_end_date}'
                    )
                    
        except Exception as e:
            logger.error(f'Error checking expired subscriptions: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('Expired subscriptions check completed!')
        )
