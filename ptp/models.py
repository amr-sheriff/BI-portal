from django.db import models
from django.contrib.admin.widgets import AdminDateWidget
from datetime import timedelta

call_status_choices = (
        ('cancellation', 'Cancellation'),
        ('fraud', 'Fraud'),
        ('hung-up', 'Hung Up'),
        ('no-answer', 'No Answer'),
        ('not-reachable', 'Not Reachable'),
        ('paid-by-customer', 'Paid by customer'),
        ('collected-by-agent', 'Collected by agent'),
        ('ptp', 'PTP'),
        ('rtp', 'RTP'),
        ('sent-to-agency', 'Sent to agency'),
        ('follow-up', 'Follow Up'),
        ('ptp-not-paid', 'PTP not paid'),
        ('2nd-unreachable', '2nd Unreachable')
        )

agents = (
        ('chantal', 'Chantal'),
        ('elmoaz', 'Elmoaz'),
        ('hasan', 'Hasan'),
        ('moustafa', 'Moustafa'),
        ('rawia', 'Rawia'),
        ('sarah', 'Sarah'),
        ('robocalls', 'Robocalls')
        )


class PTP(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    order_id = models.IntegerField(null=False, blank=False, editable=False)
    reference = models.CharField(max_length=255, null=False, blank=False, editable=False)
    customer_id = models.IntegerField(null=False, blank=False, editable=False)
    phone = models.CharField(max_length=20, blank=False, null=False, editable=False)
    merchant_name = models.CharField(max_length=255, null=False, blank=False, editable=False)
    purchase_date = models.DateField(null=True, blank=True, default=None, editable=False)
    status = models.CharField(max_length=255, null=True, blank=True, default=None, editable=False)
    min_scheduled = models.DateField(null=True, blank=True, default=None, editable=False)
    diff = models.IntegerField(null=True, blank=True, default=None, editable=False)
    total_unpaid = models.FloatField(null=True, blank=True, default=None, editable=False)
    currency = models.CharField(max_length=255, null=True, blank=True, default=None, editable=False)
    call_status = models.CharField(max_length=100, choices=call_status_choices, default=None, null=True, blank=True)
    call_date = models.DateField(null=True, blank=True, default=None)
    call_week = models.DateField(null=True, blank=True, default=None, editable=False)
    ptp_followup_call_status = models.CharField(max_length=100, choices=call_status_choices, default=None, null=True, blank=True)
    agent = models.CharField(max_length=100, choices=agents, default=None, null=True, blank=True)
    ptp_first_date = models.DateField(null=True, blank=True)
    ptp_second_date = models.DateField(null=True, blank=True)
    comments = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Order {self.order_id} from {self.customer_id} and {self.merchant_name}"

    def save(self, *args, **kwargs):
        if self.call_date:
            # Calculate the start of the week (assuming Monday is the start)
            self.call_week = self.call_date - timedelta(days=self.call_date.weekday())
        super(PTP, self).save(*args, **kwargs)
