import unittest

from django.contrib.auth.models import User
from django.core import mail
from selenium.webdriver.common.by import By

from base.tests.base import BrowserTestCase

from .test_registration import registration


class TestActivationFailed(BrowserTestCase):
    def test_invalid_key(self):
        self.navigate('django_registration_activate', activation_key='x')
        alert = self.driver.find_element(By.CLASS_NAME, 'alert')
        self.assertEqual(alert.text, 'The activation key you provided is invalid.')

    def test_already_activated(self):
        registration(self=self)
        message: mail.EmailMessage = mail.outbox[0]
        activation_link = message.body.splitlines()[6]
        self.driver.get(activation_link)
        self.assert_view('django_registration_activate')

        alert = self.driver.find_element(By.CLASS_NAME, 'alert')
        self.assertEqual(alert.text, 'The account you tried to activate has already been activated.')

    @unittest.skip('Yet to find a way to mock time.time in LiveServer')
    def test_key_expired(self):
        self.assertEqual(mail.outbox, [])

        username = 'john'
        usermail = 'lennon@thebeatles.com'
        userpass = 'superpass'
        self.assertEqual(User.objects.all().count(), 0)

        self.navigate('django_registration_register')
        username_textfield = self.driver.find_element(By.NAME, 'username')
        username_textfield.send_keys(username)
        mail_textfield = self.driver.find_element(By.NAME, 'email')
        mail_textfield.send_keys(usermail)
        pass_textfield = self.driver.find_element(By.NAME, 'password1')
        pass_textfield.send_keys(userpass)
        pass_textfield = self.driver.find_element(By.NAME, 'password2')
        pass_textfield.send_keys(userpass)
        with self.wait():
            pass_textfield.submit()

        self.assert_view('django_registration_complete')

        # monkey patch time.time() to make django.core.signing.unsign() fail
        # this way the registration would fail since the activaion link seems to be outdated

        message: mail.EmailMessage = mail.outbox[0]
        activation_link = message.body.splitlines()[6]
        self.driver.get(activation_link)
        self.assert_view('django_registration_activate')

        alert = self.driver.find_element(By.CLASS_NAME, 'alert')
        self.assertEqual(alert.text, 'The account you tried to activate has already been activated.')
