from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ChoreForm, HouseholdForm, JoinHouseholdForm, SignUpForm
from .models import Chore, ChoreActivity, Household, HouseholdMembership


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
        members = household.members.select_related('user').all()
        chores = household.chores.select_related('assignee', 'created_by').all()

        assignee_id = request.GET.get('assignee')
        status = request.GET.get('status')
        search_query = (request.GET.get('q') or '').strip()

        if assignee_id:
            chores = chores.filter(assignee_id=assignee_id)
        if status:
            chores = chores.filter(status=status)
        if search_query:
            chores = chores.filter(title__icontains=search_query)

        activity = ChoreActivity.objects.filter(chore__household=household).select_related('user', 'chore')[:10]
        context['members'] = members
        context['chores'] = chores
        context['chore_form'] = ChoreForm(household=household)
        context['activity'] = activity
        context['status_choices'] = Chore.STATUS_CHOICES
        context['assignee_filter'] = assignee_id
        context['status_filter'] = status
        context['search_query'] = search_query

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


@login_required
def create_chore(request):
    membership = getattr(request.user, 'household_membership', None)
    if not membership:
        messages.error(request, 'Create or join a household before adding chores.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ChoreForm(request.POST, household=membership.household)
        if form.is_valid():
            chore = form.save(commit=False)
            chore.household = membership.household
            chore.created_by = request.user
            chore.save()
            chore.record_activity(
                request.user,
                ChoreActivity.ACTION_CREATED,
                f"Created '{chore.title}'",
            )
            if chore.assignee and chore.assignee != request.user:
                chore.record_activity(
                    request.user,
                    ChoreActivity.ACTION_ASSIGNED,
                    f"Assigned to {chore.assignee.username}",
                )
            messages.success(request, 'Chore created successfully.')
            return redirect('dashboard')
        messages.error(request, 'Please correct the chore form and try again.')

    return redirect('dashboard')


@login_required
def edit_chore(request, chore_id):
    membership = getattr(request.user, 'household_membership', None)
    household = membership.household if membership else None
    chore = get_object_or_404(Chore, pk=chore_id, household=household)

    if request.method == 'POST':
        old_assignee = chore.assignee
        old_status = chore.status
        form = ChoreForm(request.POST, instance=chore, household=household)
        if form.is_valid():
            updated = form.save()
            if updated.assignee != old_assignee:
                updated.record_activity(
                    request.user,
                    ChoreActivity.ACTION_ASSIGNED,
                    f"Assigned to {updated.assignee.username if updated.assignee else 'unassigned'}",
                )
            if updated.status != old_status:
                if updated.status == Chore.STATUS_COMPLETED:
                    updated.record_activity(
                        request.user,
                        ChoreActivity.ACTION_COMPLETED,
                        f"Marked as completed",
                    )
                else:
                    updated.record_activity(
                        request.user,
                        ChoreActivity.ACTION_UPDATED,
                        f"Status changed to {updated.get_status_display()}",
                    )
            if not updated.assignee and old_assignee is not None:
                updated.record_activity(
                    request.user,
                    ChoreActivity.ACTION_UPDATED,
                    'Removed assignee',
                )
            updated.record_activity(
                request.user,
                ChoreActivity.ACTION_UPDATED,
                'Chore details updated',
            )
            messages.success(request, 'Chore updated successfully.')
            return redirect('dashboard')
    else:
        form = ChoreForm(instance=chore, household=household)

    return render(request, 'chore_form.html', {'form': form, 'chore': chore})


@login_required
def delete_chore(request, chore_id):
    membership = getattr(request.user, 'household_membership', None)
    household = membership.household if membership else None
    chore = get_object_or_404(Chore, pk=chore_id, household=household)

    if request.method == 'POST':
        chore.record_activity(request.user, ChoreActivity.ACTION_DELETED, f"Deleted '{chore.title}'")
        chore.delete()
        messages.success(request, 'Chore deleted successfully.')

    return redirect('dashboard')
