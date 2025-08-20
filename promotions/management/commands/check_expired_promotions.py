from django.core.management.base import BaseCommand
from django.utils import timezone
from promotions.services import PromotionManagementService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check and handle expired promotions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS('Starting expired promotions check...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        try:
            if not dry_run:
                expired_count = PromotionManagementService.check_expired_promotions()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully processed {expired_count} expired promotions'
                    )
                )
            else:
                # في وضع dry-run، نعرض فقط الترويجات المنتهية
                from promotions.models import PromotionRequest
                expired_promotions = PromotionRequest.objects.filter(
                    status='active',
                    end_date__lt=timezone.now()
                )
                
                self.stdout.write(
                    self.style.WARNING(
                        f'Found {expired_promotions.count()} expired promotions:'
                    )
                )
                
                for promotion in expired_promotions:
                    self.stdout.write(
                        f'  - Promotion {promotion.id}: {promotion.trip.caption[:50]}... '
                        f'by {promotion.sponsor.username} - '
                        f'Expired: {promotion.end_date}'
                    )
                    
        except Exception as e:
            logger.error(f'Error checking expired promotions: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('Expired promotions check completed!')
        )
