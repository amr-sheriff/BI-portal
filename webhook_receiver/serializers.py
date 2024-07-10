from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('timestamp',)
        depth = 3

    def validate_recipient(self, value):
        if not value:
            raise serializers.ValidationError("Recipient field is required.")
        return value

