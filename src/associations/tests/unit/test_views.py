from django.test import TestCase


class TestViews(TestCase):
    def test_list(self):
        response = self.client.get("/verbaende/")
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        response = self.client.get("/verbaende/Test/")
        self.assertEqual(response.status_code, 404)
