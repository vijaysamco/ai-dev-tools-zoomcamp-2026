from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Chore, Household, HouseholdMembership


class HouseholdMembershipTests(TestCase):
    def setUp(self):
        self.user_one = get_user_model().objects.create_user(
            username='alice',
            password='secretpass123',
        )
        self.user_two = get_user_model().objects.create_user(
            username='bob',
            password='secretpass123',
        )

    def test_user_can_create_household(self):
        self.client.login(username='alice', password='secretpass123')
        response = self.client.post(reverse('create_household'), {'name': 'Main House'})

        self.assertEqual(Household.objects.count(), 1)
        self.assertTrue(HouseholdMembership.objects.filter(user=self.user_one).exists())
        self.assertRedirects(response, reverse('dashboard'))

    def test_user_can_join_household_with_code(self):
        household = Household.objects.create(name='Main House')
        self.client.login(username='bob', password='secretpass123')

        response = self.client.post(reverse('join_household'), {'code': household.code})

        self.assertTrue(HouseholdMembership.objects.filter(user=self.user_two, household=household).exists())
        self.assertRedirects(response, reverse('dashboard'))

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_user_cannot_view_other_household_chore(self):
        household_one = Household.objects.create(name='House One')
        household_two = Household.objects.create(name='House Two')
        HouseholdMembership.objects.create(user=self.user_one, household=household_one)
        HouseholdMembership.objects.create(user=self.user_two, household=household_two)

        chore = Chore.objects.create(
            household=household_two,
            title='Do laundry',
            created_by=self.user_two,
            assignee=self.user_two,
        )

        self.client.login(username='alice', password='secretpass123')
        response = self.client.get(reverse('edit_chore', args=[chore.pk]))

        self.assertEqual(response.status_code, 404)


class ChoreModelTests(TestCase):
    def test_chore_can_be_created_for_household(self):
        household = Household.objects.create(name='Main House')
        user = get_user_model().objects.create_user(username='charlie', password='secretpass123')

        chore = Chore.objects.create(
            household=household,
            title='Wash dishes',
            description='Load and rinse the dishes',
            assignee=user,
            created_by=user,
            due_date=date(2026, 9, 10),
            status=Chore.STATUS_IN_PROGRESS,
        )

        self.assertEqual(chore.household, household)
        self.assertEqual(chore.status, Chore.STATUS_IN_PROGRESS)
        self.assertEqual(str(chore), 'Wash dishes')

    def test_chore_can_be_created_via_dashboard(self):
        user = get_user_model().objects.create_user(username='dana', password='secretpass123')
        household = Household.objects.create(name='Home House')
        HouseholdMembership.objects.create(user=user, household=household)

        self.client.login(username='dana', password='secretpass123')
        response = self.client.post(
            reverse('create_chore'),
            {
                'title': 'Vacuum living room',
                'description': 'Do under the couch too',
                'assignee': user.pk,
                'due_date': '2026-09-12',
                'status': Chore.STATUS_PENDING,
            },
        )

        self.assertEqual(Chore.objects.count(), 1)
        self.assertRedirects(response, reverse('dashboard'))

    def test_chore_activity_is_recorded(self):
        household = Household.objects.create(name='Main House')
        user = get_user_model().objects.create_user(username='erin', password='secretpass123')
        chore = Chore.objects.create(
            household=household,
            title='Take out trash',
            created_by=user,
            assignee=user,
        )

        chore.record_activity(user, 'created', "Created 'Take out trash'")

        self.assertEqual(chore.activities.count(), 1)
        self.assertEqual(chore.activities.first().user, user)

    def test_dashboard_filters_chores_by_assignee_and_status(self):
        user_one = get_user_model().objects.create_user(username='frank', password='secretpass123')
        user_two = get_user_model().objects.create_user(username='grace', password='secretpass123')
        household = Household.objects.create(name='Shared House')
        HouseholdMembership.objects.create(user=user_one, household=household)
        HouseholdMembership.objects.create(user=user_two, household=household)

        Chore.objects.create(
            household=household,
            title='Wash dishes',
            created_by=user_one,
            assignee=user_one,
            status=Chore.STATUS_PENDING,
        )
        Chore.objects.create(
            household=household,
            title='Vacuum room',
            created_by=user_two,
            assignee=user_two,
            status=Chore.STATUS_COMPLETED,
        )

        self.client.login(username='frank', password='secretpass123')
        response = self.client.get(reverse('dashboard'), {'assignee': user_two.pk, 'status': Chore.STATUS_COMPLETED})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['chores']), 1)
        self.assertEqual(response.context['chores'][0].title, 'Vacuum room')
