from django.test import TestCase
from base.tests.base import should_include_test


class TestWInclude(TestCase):
    def test_should_exclude_if_no_cmd_tags(self):
        cmd_tags = set([])
        code_tags = set(["exclude"])
        self.assertFalse(should_include_test(cmd_tags, code_tags))

    def test_should_exclude_if_tagged_but_not_called(self):
        cmd_tags = set(["include"])
        code_tags = set(["exclude"])
        self.assertFalse(should_include_test(cmd_tags, code_tags))

    def test_should_include_if_tagged_and_called(self):
        cmd_tags = set(["include"])
        code_tags = set(["include"])
        self.assertTrue(should_include_test(cmd_tags, code_tags))

    def test_should_include_if_single_intersection(self):
        cmd_tags = set(["do", "include", "me"])
        code_tags = set(["include", "you"])
        self.assertTrue(should_include_test(cmd_tags, code_tags))

    def test_should_include_if_multiple_intersections(self):
        cmd_tags = set(["include", "me"])
        code_tags = set(["me", "include", "you"])
        self.assertTrue(should_include_test(cmd_tags, code_tags))
