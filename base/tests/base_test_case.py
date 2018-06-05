from django.test import TestCase


class BaseTestCase(TestCase):
    def assert_objects(self, model, count=1):
        objects = model.objects.all()
        self.assertEqual(len(objects), count)
        return objects[0] if count is 1 else objects
