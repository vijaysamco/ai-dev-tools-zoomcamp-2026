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
