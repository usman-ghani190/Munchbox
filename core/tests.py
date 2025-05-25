from django.test import TestCase, Client
from django.urls import reverse
from core.models import User, Restaurant, Cuisine
from django.utils import timezone
from datetime import datetime, timezone as tz

class UserTests(TestCase):
    def setUp(self):
        # Set up a test client
        self.client = Client()

        # Create a test user using the custom User model
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )

        # Create a second user for testing access control
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='otherpassword123'
        )

        # Create a test cuisine
        self.cuisine = Cuisine.objects.create(name='Italian')

        # Create a test restaurant for the first user
        self.restaurant = Restaurant.objects.create(
            user=self.user,
            name='Test Restaurant',
            phone='(123) 456-7890',
            contact_email='test@restaurant.com',
            country='USA',
            state='NY',
            city='New York',
            latitude=40.7128,
            longitude=-74.0060,
            address='123 Test St, NY',
            delivery_type='delivery_and_pickup',
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        self.restaurant.cuisines.add(self.cuisine)

    def test_user_creation(self):
        """Test that a user can be created successfully."""
        user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='newpassword123'
        )
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('newpassword123'))

    def test_user_login_success(self):
        """Test that a user can log in with correct credentials."""
        login_success = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(login_success)

    def test_user_login_failure(self):
        """Test that a user cannot log in with incorrect credentials."""
        login_failure = self.client.login(username='testuser', password='wrongpassword')
        self.assertFalse(login_failure)

    def test_user_create_restaurant(self):
        """Test that a user can create a restaurant."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.post(reverse('restaurants:add_restaurant'), {
            'name': 'New Restaurant',
            'phone': '(987) 654-3210',
            'contact_email': 'new@restaurant.com',
            'country': 'USA',
            'state': 'CA',
            'city': 'Los Angeles',
            'latitude': 34.0522,
            'longitude': -118.2437,
            'address': '456 New St, LA',
            'delivery_type': 'delivery',
            'cuisines': [self.cuisine.id],
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Restaurant.objects.filter(name='New Restaurant', user=self.user).exists())

    def test_user_access_own_restaurant(self):
        """Test that a user can access their own restaurant."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('restaurants:restaurant', kwargs={'restaurant_id': self.restaurant.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.restaurant.name)

    def test_user_access_other_restaurant(self):
        """Test that a user can still access another user's restaurant (for browsing)."""
        # Create a restaurant for the other user
        other_restaurant = Restaurant.objects.create(
            user=self.other_user,
            name='Other Restaurant',
            phone='(555) 555-5555',
            contact_email='other@restaurant.com',
            country='USA',
            state='TX',
            city='Austin',
            latitude=30.2672,
            longitude=-97.7431,
            address='789 Other St, Austin',
            delivery_type='pickup',
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        other_restaurant.cuisines.add(self.cuisine)

        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('restaurants:restaurant', kwargs={'restaurant_id': other_restaurant.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, other_restaurant.name)

    def test_user_without_restaurant_add_link(self):
        """Test that a user without a restaurant sees the 'Add Restaurant' link."""
        # Create a user without a restaurant
        user_no_restaurant = User.objects.create_user(
            username='norestaurantuser',
            email='norestaurant@example.com',
            password='norestaurant123'
        )
        self.client.login(username='norestaurantuser', password='norestaurant123')
        response = self.client.get(reverse('home:home'))
        self.assertContains(response, 'Add Restaurant')
        self.assertNotContains(response, 'My Restaurant')

    def test_user_with_restaurant_my_restaurant_link(self):
        """Test that a user with a restaurant sees the 'My Restaurant' link and not 'Add Restaurant'."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('home:home'))
        self.assertContains(response, 'My Restaurant')
        self.assertNotContains(response, 'Add Restaurant')

    def test_list_restaurants_access(self):
        """Test that a user can access the list of all restaurants."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('restaurants:list_restaurants'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.restaurant.name)