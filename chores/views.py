from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import HouseholdForm, JoinHouseholdForm, SignUpForm
from .models import Household, HouseholdMembership


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    membership = getattr(request.user, 'household_membership', None)
    household = membership.household if membership else None

    context = {
        'household': household,
        'create_form': HouseholdForm(),
        'join_form': JoinHouseholdForm(),
    }

    if household:
        context['members'] = household.members.select_related('user').all()

    return render(request, 'dashboard.html', context)


@login_required
def create_household(request):
    if getattr(request.user, 'household_membership', None):
        messages.error(request, 'You already belong to a household.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = HouseholdForm(request.POST)
        if form.is_valid():
            household = Household.objects.create(name=form.cleaned_data['name'])
            HouseholdMembership.objects.create(user=request.user, household=household)
            messages.success(request, f"Household '{household.name}' created.")
            return redirect('dashboard')
        messages.error(request, 'Please provide a valid household name.')

    return redirect('dashboard')


@login_required
def join_household(request):
    if request.method == 'POST':
        form = JoinHouseholdForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].strip().upper()
            household = Household.objects.filter(code=code).first()

            if hasattr(request.user, 'household_membership'):
                messages.error(request, 'You already belong to a household.')
                return redirect('dashboard')

            if household is None:
                messages.error(request, 'That household code was not found.')
                return redirect('dashboard')

            HouseholdMembership.objects.create(user=request.user, household=household)
            messages.success(request, f"You joined '{household.name}'.")
            return redirect('dashboard')

    return redirect('dashboard')
