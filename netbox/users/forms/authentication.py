from django import forms
from django.contrib.auth.forms import (
    UsernameField,
    AuthenticationForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
)
from django.utils.translation import gettext_lazy as _

from utilities.forms import BootstrapMixin

__all__ = (
    'LoginForm',
    'PasswordChangeForm',
)


class LoginForm(BootstrapMixin, AuthenticationForm):
    """
    Used to authenticate a user by username and password.
    """
    username = UsernameField(
        label=_("Username"),
        widget=forms.TextInput(attrs={"autofocus": True})
        )


class PasswordChangeForm(BootstrapMixin, DjangoPasswordChangeForm):
    """
    This form enables a user to change his or her own password.
    """
    pass
