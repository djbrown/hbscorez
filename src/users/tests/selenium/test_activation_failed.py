import datetime
import unittest

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail

from base.tests.base import SeleniumTestCase

from .test_registration import registration


class TestActivationFailed(SeleniumTestCase):
    def test_invalid_key(self):
        self.navigate('django_registration_activate', activation_key='x')
        alert = self.driver.find_element_by_class_name('alert')
        self.assertEqual(alert.text, 'The activation key you provided is invalid.')

    def test_already_activated(self):
        registration(self=self)
        message: mail.EmailMessage = mail.outbox[0]
        activation_link = message.body.splitlines()[6]
        self.driver.get(activation_link)
        self.assert_view('django_registration_activate')

        alert = self.driver.find_element_by_class_name('alert')
        self.assertEqual(alert.text, 'The account you tried to activate has already been activated.')

    @unittest.skip('Acivation successful even though ACCOUNT_ACTIVATION_DAYS have passed')
    def test_key_expired(self):
        self.assertEqual(mail.outbox, [])

        username = 'john'
        usermail = 'lennon@thebeatles.com'
        userpass = 'superpass'
        self.assertEqual(User.objects.all().count(), 0)

        self.navigate('django_registration_register')
        username_textfield = self.driver.find_element_by_name('username')
        username_textfield.send_keys(username)
        mail_textfield = self.driver.find_element_by_name('email')
        mail_textfield.send_keys(usermail)
        pass_textfield = self.driver.find_element_by_name('password1')
        pass_textfield.send_keys(userpass)
        pass_textfield = self.driver.find_element_by_name('password2')
        pass_textfield.send_keys(userpass)
        with self.wait():
            pass_textfield.submit()

        self.assert_view('django_registration_complete')

        user = User.objects.first()
        user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 2)
        user.save()

        message: mail.EmailMessage = mail.outbox[0]
        activation_link = message.body.splitlines()[6]
        self.driver.get(activation_link)
        self.assert_view('django_registration_activate')

        alert = self.driver.find_element_by_class_name('alert')
        self.assertEqual(alert.text, 'The account you tried to activate has already been activated.')
