from django.core.management.base import BaseCommand
import pandas as pd
from ptp.models import PTP  # Replace with your actual model and app
from sqlalchemy import create_engine
from slack_sdk import WebClient
import os
from django.db import transaction
import numpy as np

slack = WebClient(os.getenv('SLACK_TOKEN'))
dwh_pass = os.getenv('DWH_PASS')
dwh_host = os.getenv('DWH_HOST')
dwh_name = os.getenv('DWH_NAME')
dwh_user = os.getenv('DWH_USER')
BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Import data from a DataFrame, excluding existing rows'
    try:
        def handle(self, *args, **kwargs):
            df = pd.read_excel('/notif_webhook_unifonic/ptp/management/commands/ptp_migration_data.xlsx') 
            df['ptp_first_date'] = pd.to_datetime(df['ptp_first_date']).dt.date
            df['ptp_second_date'] = pd.to_datetime(df['ptp_second_date']).dt.date
            df = df.replace({np.nan: None})

            new_entries = []
            entries_to_update = []
            
            # Iterate over DataFrame rows
            for _, row in df.iterrows():
                try:
                    obj = PTP.objects.get(order_id=row['order_id'])
                    # Update object if it exists
                    updated = False
#                    if obj.reference != row['reference']:
#                        obj.reference = row['reference']
#                        updated = True
#                    if obj.customer_id != row['customer_id']:
#                        obj.customer_id = row['customer_id']
#                        updated = True
#                    if obj.phone != row['phone']:
#                        obj.phone = row['phone']
#                        updated = True
#                    if obj.merchant_name != row['merchant_name']:
#                        obj.merchant_name = row['merchant_name']
#                        updated = True
#                    if obj.purchase_date != row['purchase_date']:
#                        obj.purchase_date = row['purchase_date']
#                        updated = True
#                    if obj.status != row['status']:
#                        obj.status = row['status']
#                        updated = True
                    if obj.comments != 'Historic Migrated PTP':
                        obj.comments = 'Historic Migrated PTP'
                        updated = True
                    if obj.ptp_second_date != row['ptp_second_date']:
                        obj.ptp_second_date = row['ptp_second_date']
                        updated = True
                    if obj.ptp_first_date != row['ptp_first_date']:
                        obj.ptp_first_date = row['ptp_first_date']
                        updated = True
                    if obj.call_status != 'ptp':
                        obj.call_status = 'ptp'
                        updated = True
                    if updated:
                        entries_to_update.append(obj)
                except PTP.DoesNotExist:
                    continue
                    # Create a new object if it does not exist
#                    new_entry = PTP(order_id=row['order_id'], reference=row['reference'],
#                                    customer_id=row['customer_id'], phone=row['phone'],
#                                    merchant_name=row['merchant_name'], purchase_date=row['purchase_date'],
#                                    status=row['status'], min_scheduled=row['min_scheduled'],
#                                    diff=row['diff'], total_unpaid=row['total_unpaid'], currency=row['currency'])
#                    new_entries.append(new_entry)

            with transaction.atomic():
                # Create new entries in batches
                for i in range(0, len(new_entries), BATCH_SIZE):
                    batch = new_entries[i:i + BATCH_SIZE]
                    PTP.objects.bulk_create(batch)

                # Update existing entries in batches
                if entries_to_update:
                    for i in range(0, len(entries_to_update), BATCH_SIZE):
                        batch = entries_to_update[i:i + BATCH_SIZE]
                        PTP.objects.bulk_update(batch, ['comments', 'ptp_second_date', 'ptp_first_date', 'call_status'])

#            with transaction.atomic():
#                PTP.objects.bulk_create(new_entries)
#                if entries_to_update:
#                    PTP.objects.bulk_update(entries_to_update, ['reference', 'customer_id', 'phone', 'merchant_name', 'purchase_date', 'status', 'min_scheduled', 'diff', 'total_unpaid', 'currency'])

            self.stdout.write(self.style.SUCCESS(f'Successfully processed {len(new_entries)} new and {len(entries_to_update)} updated data'))
            slack.chat_postMessage(channel='bi_portal_jobs_tracker', text=f'Successfully updated {len(entries_to_update)} and added {len(new_entries)} new orders in BI portal.')
    except Exception as e:
        slack.chat_postMessage(channel='bi_portal_jobs_tracker', text='Error at orders updating script in BI portal: `' + str(e) + '`')
