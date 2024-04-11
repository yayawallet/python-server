from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product  # Set the model if applicable
        fields = '__all__'  # Include all fields by default (adjust as needed)