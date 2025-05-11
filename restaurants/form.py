# forms.py
from django import forms
from django.contrib.auth import get_user_model
from core.models import Restaurant, Cuisine, Package, RestaurantSubscription

User = get_user_model()

class RestaurantForm(forms.ModelForm):
    username = forms.CharField(max_length=50, required=True, help_text="Choose a unique username")
    user_email = forms.EmailField(required=True, help_text="Email for the restaurant account")
    cuisines = forms.ModelMultipleChoiceField(
        queryset=Cuisine.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True,
        help_text="Hold Ctrl (Windows) or Command (Mac) to select multiple cuisines for fusion restaurants."
    )
    package = forms.ModelChoiceField(
        queryset=Package.objects.all(),
        empty_label=None,
        required=True,
        widget=forms.RadioSelect
    )

    class Meta:
        model = Restaurant
        fields = ['name', 'phone', 'manager_name', 'manager_phone', 'contact_email',
                  'country', 'state', 'city', 'latitude', 'longitude', 'address',
                  'delivery_type', 'cuisines', 'logo']
        widgets = {
            'delivery_type': forms.Select(choices=Restaurant.delivery_type),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        restaurant = super().save(commit=False)
        if commit:
            restaurant.user = User.objects.get(id=self.user.id)
            restaurant.user.is_restaurant_manager = True
            restaurant.user.save()
            restaurant.save()
            subscription = RestaurantSubscription.objects.create(
                restaurant=restaurant,
                package=self.cleaned_data['package'],
                end_date=self.cleaned_data['package'].duration_days + self.instance.created_at
            )
            subscription.save()
        return restaurant