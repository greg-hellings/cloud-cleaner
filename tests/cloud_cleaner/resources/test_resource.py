from unittest import TestCase

from cloud_cleaner.resources.resource import Resource


class TestResource(TestCase):
    def test_unimplemented_methods(self):
        resource = Resource()
        with self.assertRaises(NotImplementedError):
            resource.process()
        with self.assertRaises(NotImplementedError):
            resource.clean()
