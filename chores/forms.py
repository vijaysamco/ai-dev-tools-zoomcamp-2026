from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class HouseholdForm(forms.Form):
    name = forms.CharField(max_length=100, label='Household name')


class JoinHouseholdForm(forms.Form):
    code = forms.CharField(max_length=12, label='Household code')
