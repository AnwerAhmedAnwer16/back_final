from django.core.management.base import BaseCommand
from promotions.models import PromotionPlan


class Command(BaseCommand):
    help = 'Create default promotion plans'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Creating default promotion plans...')
        )
        
        plans = [
            {
                'name': 'ترويج سريع',
                'duration_days': 3,
                'price': 50.00,
                'currency': 'EGP',
                'reach_multiplier': '2x',
                'description': 'ترويج سريع لمدة 3 أيام مع مضاعفة الوصول',
                'features': [
                    'ظهور في المقدمة لمدة 3 أيام',
                    'مضاعفة الوصول 2x',
                    'عرض "رحلة مميزة"',
                    'عمولة 10% لصاحب الرحلة'
                ]
            },
            {
                'name': 'ترويج أسبوعي',
                'duration_days': 7,
                'price': 100.00,
                'currency': 'EGP',
                'reach_multiplier': '3x',
                'description': 'ترويج لمدة أسبوع مع مضاعفة الوصول 3 مرات',
                'features': [
                    'ظهور في المقدمة لمدة 7 أيام',
                    'مضاعفة الوصول 3x',
                    'عرض "رحلة مميزة"',
                    'أولوية في نتائج البحث',
                    'عمولة 10% لصاحب الرحلة'
                ]
            },
            {
                'name': 'ترويج شهري',
                'duration_days': 30,
                'price': 300.00,
                'currency': 'EGP',
                'reach_multiplier': '5x',
                'description': 'ترويج لمدة شهر مع مضاعفة الوصول 5 مرات',
                'features': [
                    'ظهور في المقدمة لمدة 30 يوم',
                    'مضاعفة الوصول 5x',
                    'عرض "رحلة مميزة"',
                    'أولوية عالية في نتائج البحث',
                    'إحصائيات مفصلة',
                    'دعم فني مخصص',
                    'عمولة 10% لصاحب الرحلة'
                ]
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for plan_data in plans:
            plan, created = PromotionPlan.objects.get_or_create(
                name=plan_data['name'],
                duration_days=plan_data['duration_days'],
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
        
        # عرض ملخص الخطط
        self.stdout.write('\n' + self.style.SUCCESS('Available Promotion Plans:'))
        for plan in PromotionPlan.objects.filter(is_active=True).order_by('duration_days'):
            commission = plan.owner_commission_amount
            self.stdout.write(
                f'  • {plan.name}: {plan.price} {plan.currency} '
                f'({plan.duration_days} أيام) - عمولة المالك: {commission} {plan.currency}'
            )
