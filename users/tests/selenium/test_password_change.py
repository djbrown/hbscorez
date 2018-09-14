from django.contrib.auth.models import User

from base.tests.base import SeleniumTestCase


class TestPasswordChange(SeleniumTestCase):
    def test_password_change(self):
        username = 'john'
        usermail = 'lennon@thebeatles.com'
        oldpass = 'johnpassword'
        newpass = 'superpass'
        User.objects.create_user(username, usermail, oldpass)

        self.login(username, oldpass)
        self.assert_view('index')

        self.navigate('users:password_change')
        old_password_textfield = self.driver.find_element_by_name('old_password')
        old_password_textfield.send_keys(oldpass)
        new_pass_textfield = self.driver.find_element_by_name('new_password1')
        new_pass_textfield.send_keys(newpass)
        new_pass_textfield = self.driver.find_element_by_name('new_password2')
        new_pass_textfield.send_keys(newpass)
        with self.wait():
            new_pass_textfield.submit()

        self.assert_view('users:password_change_success')
        success_text = self.driver.find_element_by_tag_name('p').text
        self.assertEqual(success_text, 'Your password was changed.')

        self.assertEqual(User.objects.all().count(), 1)
        self.assertFalse(User.objects.first().check_password(oldpass))
        self.assertTrue(User.objects.first().check_password(newpass))

    def login(self, username, password):
        self.navigate('users:login')
        username_textfield = self.driver.find_element_by_name('username')
        username_textfield.send_keys(username)
        password_textfield = self.driver.find_element_by_name('password')
        password_textfield.send_keys(password)
        with self.wait():
            password_textfield.submit()
