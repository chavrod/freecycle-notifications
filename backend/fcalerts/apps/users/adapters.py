from django.core.exceptions import ValidationError

from allauth.account.adapter import DefaultAccountAdapter


class MyAccountAdapter(DefaultAccountAdapter):
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
            raise ValidationError({"password": error_message})

        # TODO: Add 'No repeated characters'
        # repeats_regex = re.compile(r"(.)\1{3,}")
        # if repeats_regex.search(password):
        #     raise ValidationError(
        #         "Password must not contain repeated characters in sequence four times or more."
        #     )

        return super().clean_password(password, user)
