from base.models import Env, GlobalMessage, Value
from base.tests.base import ViewTestCase


class TestViews(ViewTestCase):
    def test_home(self):
        response = self.get_url("base:home")
        self.assertContains(response, "Willkommen auf HbScorez!")

    def test_home_message(self):
        GlobalMessage.objects.create(message="Test Message")
        response = self.get_url("base:home")
        self.assertContains(response, "Test Message")

    def test_home_updating(self):
        Env.objects.create(name="UPDATING", value=Value.TRUE.value)
        response = self.get_url("base:home")
        self.assertContains(response, "Daten werden aktualisiert")

    def test_imprint(self):
        response = self.get_url("base:imprint")
        self.assertContains(response, "Impressum")

    def test_privacy(self):
        response = self.get_url("base:privacy")
        self.assertContains(response, "Datenschutzerklärung")

    def test_contact_form(self):
        response = self.get_url("base:contact_form")
        self.assertContains(response, "Nachricht")

    def test_maintenance(self):
        response = self.get_url("base:maintenance")
        self.assertRedirects(response, "/")
