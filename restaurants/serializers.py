from rest_framework import serializers
from core.models import Restaurant, Cuisine, Package

class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ['id', 'name']

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ['id', 'name', 'price', 'duration_days', 'description']

class RestaurantStep1Serializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    manager_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    manager_phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    contact_email = serializers.EmailField()
    country = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    address = serializers.CharField(required=False, allow_blank=True)
    delivery_type = serializers.ChoiceField(choices=['delivery', 'pickup', 'delivery_and_pickup'])
    cuisines = serializers.ListField(child=serializers.IntegerField(), min_length=1)

class RestaurantStep2Serializer(serializers.Serializer):
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())

class RestaurantStep3Serializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=['credit_card', 'paypal', 'cash', 'gift_card', 'amex'])

class RestaurantFinalSerializer(serializers.ModelSerializer):
    cuisines = serializers.PrimaryKeyRelatedField(queryset=Cuisine.objects.all(), many=True)
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all())

    class Meta:
        model = Restaurant
        fields = [
            'name', 'phone', 'manager_name', 'manager_phone', 'contact_email',
            'country', 'state', 'city', 'latitude', 'longitude', 'address',
            'delivery_type', 'cuisines', 'package'
        ]

    def create(self, validated_data):
        cuisines = validated_data.pop('cuisines', [])
        package = validated_data.pop('package', None)  # Not saved in Restaurant model directly
        # Create the restaurant instance
        restaurant = Restaurant.objects.create(
            user=self.context['request'].user,  # Set the user
            **validated_data
        )
        # Set the ManyToMany cuisines
        restaurant.cuisines.set(cuisines)
        return restaurant