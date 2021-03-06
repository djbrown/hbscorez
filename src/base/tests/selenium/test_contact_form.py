from django.core import mail
from django.test.utils import override_settings

from base.tests.base import SeleniumTestCase

CAPTCHA = 'test'


@override_settings(CAPTCHA=CAPTCHA)
class ContactFormTest(SeleniumTestCase):

    def test_contact_form(self):
        self.assertEqual(mail.outbox, [])

        username = 'john'
        usermail = 'lennon@thebeatles.com'
        message = 'this is a message'
        self.navigate('base:contact_form')

        username_textfield = self.driver.find_element_by_name('name')
        username_textfield.send_keys(username)
        mail_textfield = self.driver.find_element_by_name('email')
        mail_textfield.send_keys(usermail)
        message_textarea = self.driver.find_element_by_name('body')
        message_textarea.send_keys(message)
        message_textarea = self.driver.find_element_by_name('captcha')
        message_textarea.send_keys(CAPTCHA)

        with self.wait():
            message_textarea.submit()

        self.assert_view('base:contact_form_sent')

        self.assertEqual(len(mail.outbox), 1)
        body: mail.EmailMessage = mail.outbox[0].body
        self.assertIn(username, body)
        self.assertIn(message, body)
        self.assertIn(usermail, body)
