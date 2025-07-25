from django.shortcuts import redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.conf import settings
from auth.views import AuthView
from auth.helpers import send_verification_email
# from auth.models import Profile
from auth.models import UserAccount, EmployeeProfile
import uuid


class RegisterView(AuthView):
    def get(self, request):
        if request.user.is_authenticated:
            # If the user is already logged in, redirect them to the home page or another appropriate page.
            return redirect("index")  # Replace 'index' with the actual URL name for the home page

        # Render the login page for users who are not logged in.
        return super().get(request)

    def post(self, request):
        email = request.POST.get("email")
        phone_number = request.POST.get('phone_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get("password")

        # Check if a user with the same username or email already exists
        if UserAccount.objects.filter(phone_number=phone_number, email=email).exists():
            messages.error(request, "User already exists, Try logging in.")
            return redirect("register")
        elif UserAccount.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")
        elif UserAccount.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already exists.")
            return redirect("register")

        # Create the user and set their password
        created_user = UserAccount.objects.create_employee(phone_number=phone_number, email=email, first_name=first_name, last_name=last_name, password=password)
        created_user.set_password(password)
        created_user.save()

        # Add the user to the 'client' group (or any other group you want to use as default for new users)
        user_group, created = Group.objects.get_or_create(name="employee")
        created_user.groups.add(user_group)

        # Generate a token and send a verification email here
        token = str(uuid.uuid4())

        # Set the token in the user's profile
        user_profile, created = EmployeeProfile.objects.get_or_create(user=created_user)
        user_profile.email_token = token
        user_profile.email = email
        user_profile.save()

        send_verification_email(email, token)

        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            messages.success(request, "Verification email sent successfully")
        else:
            messages.error(request, "Email settings are not configured. Unable to send verification email.")

        request.session['email'] = email ## Save email in session
        # Redirect to the verification page after successful registration
        return redirect("verify-email-page")
