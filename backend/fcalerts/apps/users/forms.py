from django.core.exceptions import ValidationError
from django.contrib.auth.forms import SetPasswordForm

from allauth.account.adapter import get_adapter


class CustomSetPasswordForm(SetPasswordForm):
    def clean_new_password1(self):
        password1 = self.cleaned_data.get("new_password1")

        # Use the clean_password method from the adapter for validation
        try:
            get_adapter().clean_password(password1)
        except ValidationError as e:
            raise ValidationError(e.messages)

        return password1
