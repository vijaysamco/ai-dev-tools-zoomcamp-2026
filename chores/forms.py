from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Chore


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class HouseholdForm(forms.Form):
    name = forms.CharField(max_length=100, label='Household name')


class JoinHouseholdForm(forms.Form):
    code = forms.CharField(max_length=12, label='Household code')


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ['title', 'description', 'assignee', 'due_date', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, household=None, **kwargs):
        super().__init__(*args, **kwargs)
        if household is not None:
            self.fields['assignee'].queryset = household.members.select_related('user').values_list('user_id', flat=True)
            members = household.members.select_related('user')
            self.fields['assignee'].queryset = User.objects.filter(id__in=[m.user_id for m in members])
        else:
            self.fields['assignee'].queryset = User.objects.none()
