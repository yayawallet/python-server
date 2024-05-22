from rest_framework import serializers
from .models import Scheduled

class ScheduledSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheduled  # Set the model if applicable
        fields = '__all__'  # Include all fields by default (adjust as needed)