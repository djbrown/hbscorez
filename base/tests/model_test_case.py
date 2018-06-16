from django.test import TestCase


class ModelTestCase(TestCase):
    def assert_objects(self, model, count=1, filters=None):
        if filters is None:
            filters = {}

        objects = model.objects.filter(**filters)
        self.assertEqual(len(objects), count)
        return objects[0] if count is 1 else objects
