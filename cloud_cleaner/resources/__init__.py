from .server import Server
from .fip import Fip


all_resources = {
    'server': Server(),
    'fip': Fip()
}
