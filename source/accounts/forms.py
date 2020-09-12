from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django import forms
from django.core.exceptions import ValidationError

from accounts.models import Profile


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2',
                  'first_name', 'last_name', 'email']
        field_classes = {'username': UsernameField}

    def save(self, commit=True):
        if settings.ACTIVATE_USERS_EMAIL:
            user: AbstractUser = super().save(commit=False)
            user.is_active = False
            if commit:
                user.save()
                token = self.create_token(user)
                self.send_email(user, token)
        else:
            user = super().save(commit=commit)
            Profile.objects.create(user=user)
        return user

    def clean(self):
        cleaned_data = super().clean()
        errors = []
        email = cleaned_data.get('email')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        if not first_name:
            if not last_name:
                errors.append(ValidationError('Заполните хотя бы одно из двух полей!'))
        if not email:
            errors.append(ValidationError('Введите Email'))
        if errors:
            raise ValidationError(errors)
        return cleaned_data


