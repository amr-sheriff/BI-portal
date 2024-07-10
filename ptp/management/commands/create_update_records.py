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
            engine = create_engine('redshift+psycopg2://' + dwh_user  + ':' + dwh_pass  + '@' + dwh_host  + ':5439/' + dwh_name, connect_args={"keepalives": 1, "keepalives_idle": 60, "keepalives_interval": 60})
            conn = engine.connect()
        
            df = pd.read_sql_query("""select a.order_id, a.reference, a.currency, a.customer_id, a.phone, a.merchant_name, a.created::date as purchase_date, coalesce(b.status, 'paid-due') as status, b.min_scheduled, b.diff, b.total_unpaid
            from dl.instalment_plans a
            left join (select instalment_plan_id, status, min(scheduled) as min_scheduled, datediff(days, min(scheduled), current_date) as diff, sum(amount-refunded_amount) as total_unpaid
            from dl.instalments
            where status = 'unpaid'
            group by 1,2) b on a.instalment_plan_id = b.instalment_plan_id
            where a.num_instalments > 1
            and a.created::date >= '2023-01-01'""", con=conn)

            df = df.replace({np.nan: None})

            new_entries = []
            entries_to_update = []
            
            # Iterate over DataFrame rows
            for _, row in df.iterrows():
                try:
                    obj = PTP.objects.get(order_id=row['order_id'])
                    # Update object if it exists
                    updated = False
                    if obj.reference != row['reference']:
                        obj.reference = row['reference']
                        updated = True
                    if obj.customer_id != row['customer_id']:
                        obj.customer_id = row['customer_id']
                        updated = True
                    if obj.phone != row['phone']:
                        obj.phone = row['phone']
                        updated = True
                    if obj.merchant_name != row['merchant_name']:
                        obj.merchant_name = row['merchant_name']
                        updated = True
                    if obj.purchase_date != row['purchase_date']:
                        obj.purchase_date = row['purchase_date']
                        updated = True
                    if obj.status != row['status']:
                        obj.status = row['status']
                        updated = True
                    if obj.min_scheduled != row['min_scheduled']:
                        obj.min_scheduled = row['min_scheduled']
                        updated = True
                    if obj.diff != row['diff']:
                        obj.diff = row['diff']
                        updated = True
                    if obj.total_unpaid != row['total_unpaid']:
                        obj.total_unpaid = row['total_unpaid']
                        updated = True
                    if obj.currency != row['currency']:
                        obj.currency = row['currency']
                        updated = True
                    if updated:
                        entries_to_update.append(obj)
                except PTP.DoesNotExist:
                    # Create a new object if it does not exist
                    new_entry = PTP(order_id=row['order_id'], reference=row['reference'],
                                    customer_id=row['customer_id'], phone=row['phone'],
                                    merchant_name=row['merchant_name'], purchase_date=row['purchase_date'],
                                    status=row['status'], min_scheduled=row['min_scheduled'],
                                    diff=row['diff'], total_unpaid=row['total_unpaid'], currency=row['currency'])
                    new_entries.append(new_entry)

            with transaction.atomic():
                # Create new entries in batches
                for i in range(0, len(new_entries), BATCH_SIZE):
                    batch = new_entries[i:i + BATCH_SIZE]
                    PTP.objects.bulk_create(batch)

                # Update existing entries in batches
                if entries_to_update:
                    for i in range(0, len(entries_to_update), BATCH_SIZE):
                        batch = entries_to_update[i:i + BATCH_SIZE]
                        PTP.objects.bulk_update(batch, ['reference', 'customer_id', 'phone', 'merchant_name', 'purchase_date', 'status', 'min_scheduled', 'diff', 'total_unpaid', 'currency'])

#            with transaction.atomic():
#                PTP.objects.bulk_create(new_entries)
#                if entries_to_update:
#                    PTP.objects.bulk_update(entries_to_update, ['reference', 'customer_id', 'phone', 'merchant_name', 'purchase_date', 'status', 'min_scheduled', 'diff', 'total_unpaid', 'currency'])

            self.stdout.write(self.style.SUCCESS(f'Successfully processed {len(new_entries)} new and {len(entries_to_update)} updated data'))
            slack.chat_postMessage(channel='bi_portal_jobs_tracker', text=f'Successfully updated {len(entries_to_update)} and added {len(new_entries)} new orders in BI portal.')
    except Exception as e:
        slack.chat_postMessage(channel='bi_portal_jobs_tracker', text='Error at orders updating script in BI portal: `' + str(e) + '`')
