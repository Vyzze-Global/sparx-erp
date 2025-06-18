from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import UserAccount
from auth.models import UserAccount
from django.contrib import messages
from auth.views import AuthView


class LoginView(AuthView):
    def get(self, request):
        if request.user.is_authenticated:
            # If the user is already logged in, redirect them to the home page or another appropriate page.
            return redirect("index")  # Replace 'index' with the actual URL name for the home page

        # Render the login page for users who are not logged in.
        return super().get(request)

    def post(self, request):
        username_input = request.POST.get("email-phonenumber")
        password = request.POST.get("password")

        if not (username_input and password):
            messages.error(request, "Please enter your email/phone number and password.")
            return redirect("login")

        user = None

        # Check if input is an email
        if "@" in username_input:
            user = UserAccount.objects.filter(email=username_input).first()
            if not user:
                messages.error(request, "No account found with this email.")
                return redirect("login")
            login_identifier = user.email
        else:
            # Otherwise, assume it's a phone number
            user = UserAccount.objects.filter(phone_number=username_input).first()
            if not user:
                messages.error(request, "No account found with this phone number.")
                return redirect("login")
            login_identifier = user.email  # We use email as the USERNAME_FIELD for authentication

        authenticated_user = authenticate(request, email=login_identifier, password=password)
        if authenticated_user is not None:
            login(request, authenticated_user)

            next_url = request.POST.get("next", "index")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect("login")
