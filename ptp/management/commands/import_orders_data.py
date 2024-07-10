from django.core.management.base import BaseCommand
import pandas as pd
from ptp.models import PTP  # Replace with your actual model and app
from sqlalchemy import create_engine
from slack_sdk import WebClient
import os
from django.db import transaction

slack = WebClient(os.getenv('SLACK_TOKEN'))
dwh_pass = os.getenv('DWH_PASS')
dwh_host = os.getenv('DWH_HOST')
dwh_name = os.getenv('DWH_NAME')
dwh_user = os.getenv('DWH_USER')

class Command(BaseCommand):
    help = 'Import data from a DataFrame, excluding existing rows'
    try:
        def handle(self, *args, **kwargs):
            engine = create_engine('redshift+psycopg2://' + dwh_user  + ':' + dwh_pass  + '@' + dwh_host  + ':5439/' + dwh_name, connect_args={"keepalives": 1, "keepalives_idle": 60, "keepalives_interval": 60})
            conn = engine.connect()
        
            df = pd.read_sql_query("""select order_id, reference, customer_id, phone, merchant_name
            from dl.instalment_plans
            where num_instalments > 1
            and created::date >= '2023-01-01'""", con=conn)

            new_entries = []

            # Iterate over DataFrame rows
            for _, row in df.iterrows():
                # Check if the entry exists in your model
                if not PTP.objects.filter(order_id=row['order_id']).exists():
                    # If not, create and save a new object
                    new_entry = PTP(order_id=row['order_id'], reference=row['reference'], customer_id=row['customer_id'], phone=row['phone'], merchant_name=row['merchant_name'])
                    new_entries.append(new_entry)

            with transaction.atomic():
                PTP.objects.bulk_create(new_entries)

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(new_entries)} new data'))
            slack.chat_postMessage(channel='bi_portal_jobs_tracker', text=f'Successfully updated {len(new_entries)} new orders in BI portal.')
    except Exception as e:
        slack.chat_postMessage(channel='bi_portal_jobs_tracker', text='Error at orders updating script in BI portal: `' + str(e) + '`')
