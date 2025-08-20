from django.core.management.base import BaseCommand
from accounts.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Create default subscription plans'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Creating default subscription plans...')
        )
        
        plans = [
            {
                'name': 'Premium Monthly',
                'plan_type': 'premium',
                'duration': 'monthly',
                'price': 99.00,
                'currency': 'EGP',
                'description': 'Premium features for one month',
                'features': [
                    'Verified badge',
                    'Priority support',
                    'Advanced search filters',
                    'Unlimited trip posts'
                ]
            },
            {
                'name': 'Premium Yearly',
                'plan_type': 'premium',
                'duration': 'yearly',
                'price': 999.00,
                'currency': 'EGP',
                'description': 'Premium features for one year (2 months free)',
                'features': [
                    'Verified badge',
                    'Priority support',
                    'Advanced search filters',
                    'Unlimited trip posts',
                    '2 months free'
                ]
            },
            {
                'name': 'Pro Monthly',
                'plan_type': 'pro',
                'duration': 'monthly',
                'price': 199.00,
                'currency': 'EGP',
                'description': 'All premium features plus business tools',
                'features': [
                    'All Premium features',
                    'Business profile',
                    'Analytics dashboard',
                    'Custom branding',
                    'API access'
                ]
            },
            {
                'name': 'Pro Yearly',
                'plan_type': 'pro',
                'duration': 'yearly',
                'price': 1999.00,
                'currency': 'EGP',
                'description': 'All pro features for one year (2 months free)',
                'features': [
                    'All Premium features',
                    'Business profile',
                    'Analytics dashboard',
                    'Custom branding',
                    'API access',
                    '2 months free'
                ]
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                duration=plan_data['duration'],
                defaults=plan_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {plan.name}')
                )
            else:
                # تحديث البيانات إذا كانت موجودة
                for key, value in plan_data.items():
                    setattr(plan, key, value)
                plan.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated: {plan.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Completed! Created: {created_count}, Updated: {updated_count}'
            )
        )
