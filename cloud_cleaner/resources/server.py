"""Contains implementation of the Server class"""
import re
import smtplib
from datetime import datetime
from pytz import utc
from cloud_cleaner.config import DATE_FORMAT
from cloud_cleaner.resources.resource import Resource
from cloud_cleaner.string_matcher import StringMatcher


class Server(Resource):
    """
    Performs processing and cleansing of instances of servers from the
    configured OpenStack endpoints
    """
    type_name = "server"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__targets = []
        self._interval = None
        # Default objects that pass through all instances without filtering
        self.__skip_name = StringMatcher(False)
        self.__name = StringMatcher(True)
        self.__deleted_ids = []
        self.__deletion = False

    def register(self, config):
        """

        :type parser: argparse.ArgumentParser
        """
        super().register(config)
        _desc = "Regex to match the name of the servers"
        self._sub_config.add_argument("--name", "-n", help=_desc)
        _desc = "Regex to match for servers to ignore"
        self._sub_config.add_argument("--skip-name", "-s", dest="skip_name",
                                      help=_desc)
        _desc = "Minimum age (1d, 2w, 6m, 1y)"
        self._sub_config.add_argument("--age", "-a", help=_desc)

    def process(self):
        """
        Fetches the list of servers and processes them to filter out which
        ones ought to actually be deleted.

        :return: None
        """
        conn = self._get_conn()
        self._config.info("Connecting to OpenStack to retrieve server list")
        self.__age = self._config.get_arg('age')
        self.__targets = conn.list_servers()
        if not self.__deletion:
            if self.__age is not None:
                self._interval = self.parse_interval(self.__age)
                self._interval = self._interval / 2
            server_accum = []
            # We only want to look over servers which have not been deleted
            for server in conn.list_servers():
                if server.id not in self.__deleted_ids:
                    server_accum.append(server)
            self.__targets = server_accum
        self._config.info("Found %d servers" % len(self.__targets))
        self.__debug_targets()
        # Process for time
        self.__process_dates()
        self._config.info("%d servers passed age test" % len(self.__targets))
        # Process for name
        self.__process_names()
        self._config.info("%d servers passed name test" % len(self.__targets))
        # We are now done with deletion(aside from the cleaning itself)
        self.__deletion = False

    def __debug_targets(self):
        for target in self.__targets:
            self._config.debug("   *** " + target.name)

    def clean(self):
        """
        Call delete on the list of servers left over after the process
        stage is completed.

        :return: None
        """
        conn = self._get_conn()
        self._config.info("Deleting %d servers" % len(self.__targets))
        for target in self.__targets:
            self._config.debug("Deleting %s" % target.id)
            self.__deleted_ids.append(target.id)
            conn.delete_server(target.id)
            print("Deleted %s" % target.name)

    def __process_dates(self):
        """
        Process out all the items from this system that are not targeted based
        on the age of the server

        :return: None
        """
        if self._interval is not None:
            # interval has been set, meaning that we are using a different
            # time then the one directly fed as an argument
            self._config.debug("Working with age %s" % (self._interval,))
            self.__targets = list(filter(self.__right_age, self.__targets))
            self._config.debug("Parsed ages, servers remaining: ")
            self.__debug_targets()
            self._interval = None
        elif self.__age is not None:
            self._config.debug("Parsing dates")
            self._interval = self.parse_interval(self.__age)
            self._config.debug("Working with age %s" % (self._interval,))
            self.__targets = list(filter(self.__right_age, self.__targets))
            self._config.debug("Parsed ages, servers remaining: ")
            self.__debug_targets()
        else:
            self._config.debug("No age provided")

    def __process_names(self):
        skip_name = self._config.get_arg("skip_name")
        if skip_name is not None:
            self.__skip_name = re.compile(skip_name)
        name = self._config.get_arg('name')
        if name is not None:
            self.__name = re.compile(name)
        if name is not None or skip_name is not None:
            self._config.debug("Parsing names")
            self.__targets = list(filter(self.__right_name, self.__targets))
            self._config.debug("Parsed names, servers remaining: ")
            self.__debug_targets()
        else:
            self._config.debug("No name restrictions provided")

    def __right_name(self, target):
        return not self.__skip_name.match(target.name) and \
               self.__name.match(target.name)

    def __right_age(self, target):
        system_age = datetime.strptime(target.launched_at, DATE_FORMAT)
        system_age = system_age.replace(tzinfo=utc)
        return self._now > (system_age + self._interval)

    def send_emails(self):
        """
        Sends warning emails to the owners of all flagged servers, if they have
        an email to send to. Email settings depend on input args to the script.

        :return: None
        """
        sender = self._config.get_arg("sender")
        smtp_name = self._config.get_arg("smtpN")
        port = self._config.get_arg("smtpP")
        conn = self._get_conn()
        receiver = self._config.get_arg("receiver")
        skip_name = self._config.get_arg("skip_name")
        servers = {}

        # Loop over flagged servers to send emails to the proper recipient
        for server in self.__targets:
            user = conn.get_user_by_id(server.user_id, False)
            # If the receiver flag is set, we want to email that address for
            # everything.
            recipient = receiver if receiver != "" else user.email
            name = receiver if receiver != "" else user.name
            if recipient in servers:
                servers[recipient]["servers"].append(server.name)
            else:
                servers[recipient] = {"servers": [server.name], "name": name}

        for email in servers:
            # Set the values which will send this email(s)
            server_names = "\n".join(servers[email]["servers"])
            user = servers[email]["name"]
            message = message = (
                "{user}, The following server(s) may be deleted when its"
                " (their) age reaches {age} if you do not change the name of"
                " the server(s) to include {skip} at the start of the name."
                " These are the names of the servers:\n{server}"
            )
            message = message.format(user=user, server=server_names,
                                     age=self.__age, skip=skip_name)
            with smtplib.SMTP(smtp_name, port) as emailer:
                emailer.sendmail(sender, email, message)

    def prep_deletion(self):
        """
        Prepares the server resource for deletion. Sets a flag that will be
        used in the process function to decide whether we are scanning for
        deletion or for email warnings.

        :return: None
        """
        self.__deletion = True
