import json
from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch # Import reverse and NoReverseMatch
from django.contrib.auth.models import User

# Note: If using pytest, you might use fixtures (@pytest.fixture)
# and the pytest client (`client`) directly.
# This example uses Django's standard TestCase and Client.

class AuthAPITestCase(TestCase):

    def setUp(self):
        """Set up test client and base URL for API endpoints."""
        self.client = Client()
        # Construct URLs using reverse where possible
        try:
            # Construct Ninja endpoint paths relative to the main 'api' mount point
            api_base_url = reverse('api') # Reverses to '/api/'
            self.register_url = f"{api_base_url}auth/register" # -> /api/auth/register
            self.login_url = f"{api_base_url}auth/login"       # -> /api/auth/login
        except NoReverseMatch:
            # Fallback if 'api' name isn't resolved (should not happen with urls.py change)
            self.register_url = "/api/auth/register"
            self.login_url = "/api/auth/login"
        # self.refresh_url = reverse('token_refresh') # Example if using named URLs

        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123",
            "first_name": "Test",
            "last_name": "User",
        }
        self.login_data = {
            "username": "testuser",
            "password": "StrongPassword123",
        }


    # --- Registration Tests (/api/auth/register) ---

    def test_register_success(self):
        """Test successful user registration."""
        initial_user_count = User.objects.count()
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), initial_user_count + 1)

        # Check response data structure (adjust fields based on UserSchema)
        response_data = response.json()
        self.assertEqual(response_data["username"], self.user_data["username"])
        self.assertEqual(response_data["email"], self.user_data["email"])
        self.assertNotIn("password", response_data) # Ensure password isn't returned

        # Verify user creation in DB
        user = User.objects.get(username=self.user_data["username"])
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"])) # Verify password hash


    def test_register_existing_username(self):
        """Test registration attempt with an existing username."""
        # Create user first
        User.objects.create_user(
            username=self.user_data["username"],
            email="another@example.com",
            password=self.user_data["password"]
        )
        initial_user_count = User.objects.count()

        response = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data), # Attempt to register same username
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(User.objects.count(), initial_user_count) # No new user created
        self.assertEqual(response.json(), {"detail": "Username already exists."})


    def test_register_existing_email(self):
        """Test registration attempt with an existing email."""
         # Create user first
        User.objects.create_user(
            username="anotheruser",
            email=self.user_data["email"], # Use the same email
            password=self.user_data["password"]
        )
        initial_user_count = User.objects.count()

        response = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data), # Attempt to register same email
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(User.objects.count(), initial_user_count) # No new user created
        self.assertEqual(response.json(), {"detail": "Email already registered."})


    def test_register_invalid_payload_short_password(self):
        """Test registration with invalid data (password too short)."""
        invalid_data = self.user_data.copy()
        invalid_data["password"] = "short" # Less than 8 characters

        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_data),
            content_type="application/json"
        )
        # Ninja should handle schema validation and return 422
        self.assertEqual(response.status_code, 422)
        # Check for detail structure from Ninja's validation error
        response_data = response.json()
        self.assertIn("detail", response_data)
        # Example check (structure might vary slightly):
        self.assertTrue(any(err['loc'] == ['body', 'payload', 'password'] for err in response_data['detail']))


    def test_register_invalid_payload_bad_email(self):
        """Test registration with invalid data (bad email format)."""
        invalid_data = self.user_data.copy()
        invalid_data["email"] = "not-an-email"

        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_data),
            content_type="application/json"
        )
        # Ninja should handle schema validation and return 422
        self.assertEqual(response.status_code, 422)
        response_data = response.json()
        self.assertIn("detail", response_data)
        self.assertTrue(any(err['loc'] == ['body', 'payload', 'email'] for err in response_data['detail']))


    # --- Login Tests (/api/auth/login) ---

    def test_login_success(self):
        """Test successful user login."""
        # Create user first
        User.objects.create_user(
            username=self.login_data["username"],
            password=self.login_data["password"],
            email=self.user_data["email"] # Email needed if used elsewhere
        )

        response = self.client.post(
            self.login_url,
            data=json.dumps(self.login_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("access", response_data)
        self.assertIn("refresh", response_data)
        self.assertTrue(len(response_data["access"]) > 10) # Basic check for token format
        self.assertTrue(len(response_data["refresh"]) > 10)


    def test_login_invalid_password(self):
        """Test login attempt with an incorrect password."""
        # Create user first
        User.objects.create_user(
            username=self.login_data["username"],
            password=self.login_data["password"],
            email=self.user_data["email"]
        )

        invalid_login_data = self.login_data.copy()
        invalid_login_data["password"] = "WrongPassword"

        response = self.client.post(
            self.login_url,
            data=json.dumps(invalid_login_data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid username or password."})


    def test_login_nonexistent_user(self):
        """Test login attempt with a username that does not exist."""
        response = self.client.post(
            self.login_url,
            data=json.dumps(self.login_data), # User hasn't been created
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid username or password."}) 