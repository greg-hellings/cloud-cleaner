"""
Contains the Fip class to process arguments for and results from floating
IP addresses
"""
from ipaddress import ip_address, ip_network
from cloud_cleaner.resources.resource import Resource


class Fip(Resource):
    """
    Performs processing and cleansing of floating IP addresses from the
    configured OpenStack endpoint.
    """
    type_name = "fip"

    def __init__(self):
        super(Fip, self).__init__()
        self.__fips = []

    def register(self, config):
        super(Fip, self).register(config)
        _desc = "By default, only FIPs not attached are considered. Include "\
                "this flag to consider ALL fips"
        self._sub_config.add_argument("--with-attached",
                                      dest='with_attached',
                                      help=_desc,
                                      action='store_true')
        _desc = "Definition of a subnet within which the floating IP address"\
                " must reside in order to be purged."
        self._sub_config.add_argument('--floating-subnet',
                                      dest='floating_subnet',
                                      help=_desc)
        _desc = "Definition of a subnet within which the host's primary IP "\
                "address must reside."
        self._sub_config.add_argument('--static-subnet',
                                      dest='static_subnet',
                                      help=_desc)

    def process(self):
        shade = self._get_shade()
        self._config.info("Connecting to OpenStack to fetch floating IPs")
        self.__fips = shade.list_floating_ips()
        self._config.info("Found %d floating IPs" % len(self.__fips))
        self.__debug_fips()
        self.__filter_attached()
        self.__filter_by_address()
        self._config.info("%d floating IPs passed address test" %
                          len(self.__fips))

    def clean(self):
        shade = self._get_shade()
        for fip in self.__fips:
            shade.delete_floating_ip(fip.id)

    def __filter_attached(self):
        force_attached = self._config.get_arg('with_attached')
        if not force_attached:
            self.__fips = list(filter(lambda f: not f.attached, self.__fips))
            self._config.info("%d floating IPs passed attached test" %
                              len(self.__fips))
            self.__debug_fips()

    def __filter_by_address(self):
        # TODO: Properly wrap conditions where there is an IPv4/6 mismatch
        # The user can pass in an IPv6 address, and that will result in a type
        # mismatch if the floating IP is IPv4 (or vice-versa mismatch). This
        # should be handled by the below code, but it currently is not.
        #
        # Define functions to do the filtering
        floating_subnet = self._config.get_arg('floating_subnet')
        if floating_subnet is not None:
            __fips = filter(self.__filter_factory('floating_ip_address',
                                                  floating_subnet),
                            self.__fips)
            self.__fips = list(__fips)
            self._config.info("%d passed floating_subnet" % len(self.__fips))
            self.__debug_fips()
        static_subnet = self._config.get_arg('static_subnet')
        if static_subnet is not None:
            __fips = filter(self.__filter_factory('fixed_ip_address',
                                                  static_subnet),
                            self.__fips)
            self.__fips = list(__fips)
            self._config.info("%d passed static_subnet" % len(self.__fips))
            self.__debug_fips()

    def __debug_fips(self):
        for fip in self.__fips:
            self._config.debug(fip.floating_ip_address)

    @classmethod
    def __filter_factory(cls, field, network):
        """
        Creates and returns a function that can be used as the basis of
        filtering IP addresses based on user input netmasks

        :param field: Name of the API field to test
        :param network: Netmask to test an address is in
        :return: Function to perform the network testing
        """
        net = ip_network(network)
        return lambda x: ip_address(x[field]) in net
