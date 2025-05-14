# app/restaurants/serializers.py
from rest_framework import serializers
from core.models import Restaurant, Package, Cuisine, Payment, RestaurantSubscription

class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ['id', 'name']

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ['id', 'name', 'price', 'duration_days', 'description']

class RestaurantStep1Serializer(serializers.ModelSerializer):
    cuisines = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = Restaurant
        fields = ['name', 'phone', 'manager_name', 'manager_phone', 'contact_email',
                  'country', 'state', 'city', 'latitude', 'longitude', 'address',
                  'delivery_type', 'cuisines']

    def validate(self, data):
        if not data.get('name') or not data.get('country') or not data.get('contact_email'):
            raise serializers.ValidationError("Name, country, and contact email are required.")
        if 'latitude' in data and (data['latitude'] < -90 or data['latitude'] > 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        if 'longitude' in data and (data['longitude'] < -180 or data['longitude'] > 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        if not data.get('cuisines'):
            raise serializers.ValidationError("At least one cuisine is required.")
        return data

class RestaurantStep2Serializer(serializers.Serializer):
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())

    def validate(self, data):
        if not data.get('package'):
            raise serializers.ValidationError("A package is required.")
        return data

    def to_representation(self, instance):
        # Ensure only the package ID is returned
        return {'package': instance['package'].pk}

class RestaurantStep3Serializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=[
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
        ('gift_card', 'Gift Card'),
        ('amex', 'Amex Express'),
    ])

    def validate(self, data):
        if not data.get('payment_method'):
            raise serializers.ValidationError("Payment method is required.")
        return data

class RestaurantFinalSerializer(serializers.ModelSerializer):
    cuisines = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'phone', 'manager_name', 'manager_phone', 'contact_email',
                  'country', 'state', 'city', 'latitude', 'longitude', 'address',
                  'delivery_type', 'cuisines', 'logo', 'package', 'user']

    def create(self, validated_data):
        cuisines_data = validated_data.pop('cuisines')
        user = self.context['request'].user
        restaurant = Restaurant.objects.create(user=user, **validated_data)
        restaurant.cuisines.set(cuisines_data)
        restaurant.save()
        return restaurant