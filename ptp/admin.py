from django.contrib import admin
from .models import PTP
import csv
from django.http import HttpResponse

# Register your models here.
#admin.site.register(Notification)

def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if callable(value):
                value = value()
            data_row.append(value)
        writer.writerow(data_row)
    return response

export_to_csv.short_description = 'Export to CSV'

@admin.register(PTP)
class PTPAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PTP._meta.get_fields()]
    list_editable = ['call_status', 'agent', 'ptp_first_date', 'ptp_second_date', 'comments', 'call_date', 'ptp_followup_call_status']
    search_fields = ['customer_id', 'order_id', 'reference', 'phone', 'merchant_name', 'agent', 'purchase_date', 'currency', 'status', 'diff']
    list_filter = ['agent', 'call_status', 'ptp_followup_call_status', 'currency', 'status', 'call_week', 'merchant_name']
    actions = [export_to_csv]
