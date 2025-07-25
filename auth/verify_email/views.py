from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from auth.views import AuthView
from auth.models import UserAccount
from auth.models import EmployeeProfile
from auth.helpers import send_verification_email
import uuid



class VerifyEmailTokenView(AuthView):
    def get(self, request, token):
        try:
            profile = EmployeeProfile.objects.filter(email_token=token).first()
            profile.is_verified = True
            profile.email_token = ""
            profile.save()
            if not request.user.is_authenticated:
                # User is not already authenticated
                # Perform the email verification and any other necessary actions
                messages.success(request, "Email verified successfully")
            return redirect("login")
            # Now, redirect to the login page

        except EmployeeProfile.DoesNotExist:
            messages.error(request, "Invalid token, please try again")
            return redirect("verify-email-page")

class VerifyEmailView(AuthView):
    def get(self, request):
        # Render the login page for users who are not logged in.
        return super().get(request)


class SendVerificationView(AuthView):
    def get(self, request):
        email, message = self.get_email_and_message(request)

        if email:
            user = UserAccount.objects.filter(email=email).first()
            if not user or user.user_type != 'employee':
                messages.error(request, "Employee with this email not found.")
                return redirect("verify-email-page")

            profile = getattr(user, 'employee_profile', None)
            if not profile:
                messages.error(request, "Employee profile not found.")
                return redirect("verify-email-page")

            token = str(uuid.uuid4())
            profile.email_token = token
            profile.save()
            send_verification_email(email, token)
            messages.success(request, "Verification email sent successfully.")
        else:
            messages.error(request, "Email not found in session")

        return redirect("verify-email-page")

    def get_email_and_message(self, request):
        if request.user.is_authenticated:
            email = request.user.email

            if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                message = messages.success(request, "Verification email sent successfully")
            else:
                message = messages.error(request, "Email settings are not configured. Unable to send verification email.")
        else:
            email = request.session.get('email')
            if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                message = "Resend verification email successfully" if email else None
            else:
                 message = messages.error(request, "Email settings are not configured. Unable to send verification email.")

        return email, message
