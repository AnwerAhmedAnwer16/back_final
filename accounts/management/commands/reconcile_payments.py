from django.core.management.base import BaseCommand
from accounts.services import SubscriptionService


class Command(BaseCommand):
    help = 'Reconcile pending payments with PayMob'

    def handle(self, *args, **options):
        self.stdout.write('Starting payment reconciliation...')
        
        reconciled_count = SubscriptionService.reconcile_payments()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully reconciled {reconciled_count} payments'
            )
        )
