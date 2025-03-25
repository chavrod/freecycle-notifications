import json

from django.core.exceptions import ValidationError
from django.core.exceptions import ImproperlyConfigured

from allauth.headless.internal.restkit.response import APIResponse
from allauth.headless.adapter import DefaultHeadlessAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.internal.httpkit import render_url
from allauth.core.exceptions import (
    ImmediateHttpResponse,
)

from config.settings import TEMP_ALLOWED_EMAILS, BASE_ORIGIN, HEADLESS_FRONTEND_URLS


class CustomHeadlessAdapter(DefaultHeadlessAdapter):
    def get_frontend_url(self, urlname, **kwargs):
        """Return the frontend URL for the given URL name."""
        url_ext = HEADLESS_FRONTEND_URLS.get(urlname)
        if not url_ext:
            raise ImproperlyConfigured(f"HEADLESS_FRONTEND_URLS['{url_ext}']")
        if url_ext:
            return render_url(self.request, f"{BASE_ORIGIN}/{url_ext}", **kwargs)


class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_password(self, password, user=None):
        password_errors = []

        # Minimum length
        if len(password) < 8:
            password_errors.append("at least 8 characters")

        # At least one uppercase letter
        if not any(char.isupper() for char in password):
            password_errors.append("at least one uppercase letter")

        # At least one lowercase letter
        if not any(char.islower() for char in password):
            password_errors.append("at least one uppercase letter")

        # At least one number
        if not any(char.isdigit() for char in password):
            password_errors.append("at least one digit")

        # At least one special character
        if not any(char in "!@#$%^&*" for char in password):
            password_errors.append("at least one special character from !@#$%^&*")

        if password_errors:
            # Join the error messages with bullet points and a newline at the start
            error_message = "Password must contain:\n - " + "\n - ".join(
                password_errors
            )
            raise ValidationError(error_message)

        # TODO: Add 'No repeated characters'
        # repeats_regex = re.compile(r"(.)\1{3,}")
        # if repeats_regex.search(password):
        #     raise ValidationError(
        #         "Password must not contain repeated characters in sequence four times or more."
        #     )

        return super().clean_password(password, user)

    # def is_open_for_signup(self, request):
    #     body_unicode = request.body.decode("utf-8")
    #     body_data = json.loads(body_unicode)
    #     email = body_data.get("email")

    #     if email not in TEMP_ALLOWED_EMAILS:
    #         raise ImmediateHttpResponse(
    #             APIResponse(
    #                 request,
    #                 errors=[{"message": "We are not open for Signup at the moment."}],
    #                 status=403,
    #             )
    #         )
    #     else:
    #         return True
