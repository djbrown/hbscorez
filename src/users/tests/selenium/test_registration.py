from django.contrib.auth.models import User
from django.core import mail
from selenium.webdriver.common.by import By

from base.tests.base import SeleniumTestCase


class TestRegistration(SeleniumTestCase):
    def test_registration(self):
        registration(self=self)


def registration(self):
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
    self.assertEqual(len(mail.outbox), 1)
    message: mail.EmailMessage = mail.outbox[0]
    self.assertEqual(message.to, [usermail])
    activation_link = message.body.splitlines()[6]
    self.driver.get(activation_link)

    self.assert_view('django_registration_activation_complete')
    self.assertEqual(User.objects.all().count(), 1)
    login_link = self.driver.find_element(By.ID, 'link-login-redirect')
    with self.wait():
        login_link.click()

    self.assert_view('users:login')
    username_textfield = self.driver.find_element(By.NAME, 'username')
    username_textfield.send_keys(username)
    password_textfield = self.driver.find_element(By.NAME, 'password')
    password_textfield.send_keys(userpass)
    with self.wait():
        password_textfield.submit()

    self.assert_view('users:profile')
