from django.contrib.auth.models import User
from django.core import mail
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from base.tests.base import BrowserTestCase


class TestPasswordReset(BrowserTestCase):
    def test_password_reset(self):
        self.assertEqual(mail.outbox, [])

        username = 'john'
        usermail = 'lennon@thebeatles.com'
        oldpass = 'johnpassword'
        newpass = 'superpass'
        User.objects.create_user(username, usermail, oldpass)
        self.assertEqual(User.objects.all().count(), 1)

        self.navigate('users:login')
        reset_link: WebElement = self.driver.find_element(By.ID, 'link-password-reset')
        with self.wait():
            reset_link.click()

        self.assert_view('users:password_reset')
        mail_textfield = self.driver.find_element(By.NAME, 'email')
        mail_textfield.send_keys(usermail)
        with self.wait():
            mail_textfield.submit()

        self.assert_view('users:password_reset_sent')
        self.assertEqual(len(mail.outbox), 1)
        message: mail.EmailMessage = mail.outbox[0]
        self.assertEqual(message.to, [usermail])
        reactivation_link = message.body.splitlines()[5]
        self.driver.get(reactivation_link)

        self.assert_view('users:password_reset_change')
        pass_textfield = self.driver.find_element(By.NAME, 'new_password1')
        pass_textfield.send_keys(newpass)
        pass_textfield = self.driver.find_element(By.NAME, 'new_password2')
        pass_textfield.send_keys(newpass)
        with self.wait():
            pass_textfield.submit()

        self.assert_view('users:password_reset_success')
        login_link = self.driver.find_element(By.ID, 'link-login-redirect')
        with self.wait():
            login_link.click()

        self.assert_view('users:login')

        self.assertEqual(User.objects.all().count(), 1)
        self.assertFalse(User.objects.first().check_password(oldpass))
        self.assertTrue(User.objects.first().check_password(newpass))
