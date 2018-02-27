from unittest import TestCase
from cloud_cleaner.resources.resource import Resource, UnimplementedError


class TestResource(TestCase):
    def test_unimplemented_methods(self):
        resource = Resource()
        with self.assertRaises(UnimplementedError):
            resource.process()
        with self.assertRaises(UnimplementedError):
            resource.clean()
