from django.core.management.base import BaseCommand
from core.models import FeatureAccess


class Command(BaseCommand):
    help = 'Create / Update default Feature Access controls for Employer visibility'

    def handle(self, *args, **options):
        features = [
            {
                'key': 'store_module',
                'name': 'Store Module',
                'description': 'Product list, stock management, store pages',
                'is_enabled_for_employer': False
            },
            {
                'key': 'settings_module',
                'name': 'Settings Module',
                'description': 'System settings page',
                'is_enabled_for_employer': False
            },
            {
                'key': 'reports_module',
                'name': 'Reports Module',
                'description': 'All reports and analytics',
                'is_enabled_for_employer': False
            },
            {
                'key': 'expenses_module',
                'name': 'Expenses Module',
                'description': 'Expenses management',
                'is_enabled_for_employer': False
            },
            {
                'key': 'customers_module',
                'name': 'Customers Module',
                'description': 'Customer management',
                'is_enabled_for_employer': False
            },
            {
                'key': 'pos_module',
                'name': 'POS Module',
                'description': 'Point of Sale',
                'is_enabled_for_employer': True
            },
            {
                'key': 'sales_module',
                'name': 'Sales Module',
                'description': 'Sales history',
                'is_enabled_for_employer': True
            },
            # ========== NEW FEATURE ==========
            {
                'key': 'sales_profit_info',
                'name': 'Sales Profit Information',
                'description': 'Total Buy Price, Gross Profit and Net Profit cards on Sales History page',
                'is_enabled_for_employer': False
            },
        ]

        created_count = 0
        updated_count = 0

        for feature_data in features:
            obj, created = FeatureAccess.objects.update_or_create(
                key=feature_data['key'],
                defaults={
                    'name': feature_data['name'],
                    'description': feature_data['description'],
                    'is_enabled_for_employer': feature_data['is_enabled_for_employer'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {obj.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated: {obj.name}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone! Created: {created_count} | Updated: {updated_count}'
            )
        )