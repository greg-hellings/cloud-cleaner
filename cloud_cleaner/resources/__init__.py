"""
Base Class: resource.Resource - should not be instantiated directly

Concrete Classes: server.Server, fip.Fip - these should not be created
directly outside of test cases. They should be generally regarded as
singleton classes. These are intended mainly to serve as a namespace for the
related activity and actions of configuring and processing CLI arguments

Constants: ALL_RESOURCES - a dict with an instance of each of the
concrete classes. These should be considered singleton objects and their
instances ought to be acted upon directly, instead of creating new instances
of their underlying classes.
"""
from .server import Server
from .fip import Fip


ALL_RESOURCES = {
    'server': Server(),
    'fip': Fip()
}
