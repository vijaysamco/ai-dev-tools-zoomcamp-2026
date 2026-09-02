from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Household, HouseholdMembership


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
