from django.contrib.auth.models import User
from django.core import mail
from django.test.utils import override_settings
from selenium.webdriver.common.by import By

from base.tests.base import SeleniumTestCase

CAPTCHA = 'test'


class TestRegistration(SeleniumTestCase):
    def test_registration(self):
        registration(self=self)

    def test_invalid_captcha(self):
        username = 'john'
        usermail = 'lennon@thebeatles.com'
        userpass = 'superpass'

        self.navigate('django_registration_register')
        username_textfield = self.driver.find_element(By.NAME, 'username')
        username_textfield.send_keys(username)
        mail_textfield = self.driver.find_element(By.NAME, 'email')
        mail_textfield.send_keys(usermail)
        pass1_textfield = self.driver.find_element(By.NAME, 'password1')
        pass1_textfield.send_keys(userpass)
        pass2_textfield = self.driver.find_element(By.NAME, 'password2')
        pass2_textfield.send_keys(userpass)
        captcha_textfield = self.driver.find_element(By.NAME, 'captcha')
        captcha_textfield.send_keys('invalid captcha')

        with self.load():
            captcha_textfield.submit()

        self.assert_view('django_registration_register')
        self.assertEqual(User.objects.all().count(), 0)
        self.assertEqual(mail.outbox, [])
        self.assertTrue('Falsches Captcha' in self.driver.page_source)


@override_settings(CAPTCHA=CAPTCHA)
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
    pass1_textfield = self.driver.find_element(By.NAME, 'password1')
    pass1_textfield.send_keys(userpass)
    pass2_textfield = self.driver.find_element(By.NAME, 'password2')
    pass2_textfield.send_keys(userpass)
    captcha_textfield = self.driver.find_element(By.NAME, 'captcha')
    captcha_textfield.send_keys(CAPTCHA)

    with self.wait():
        captcha_textfield.submit()

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
