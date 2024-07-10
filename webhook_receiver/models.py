from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

class Notification(models.Model):
    confidence = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    speechResult = models.CharField(max_length=255, null=True, blank=True)
    digits = models.CharField(max_length=1, null=True, blank=True, validators=[RegexValidator(r'^[0-9]$')])
    recipient = models.CharField(max_length=20, blank=False, null=False, validators=[RegexValidator(r'^\+\d{1,19}$', 'Enter a valid phone number starting with +')])
    callerId = models.CharField(max_length=20, null=True, blank=True, validators=[RegexValidator(r'^\+\d{1,19}$', 'Enter a valid phone number starting with +')])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient} from {self.callerId}"
