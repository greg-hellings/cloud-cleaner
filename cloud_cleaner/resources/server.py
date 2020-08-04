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
        super(Server, self).__init__(*args, **kwargs)
        self.__targets = []
        self._interval = None
        # Default objects that pass through all instances without filtering
        self.__skip_name = StringMatcher(False)
        self.__name = StringMatcher(True)

        self.__flagged = []
        self.__deleted_ids = []

    def register(self, config):
        """

        :type parser: argparse.ArgumentParser
        """
        super(Server, self).register(config)
        _desc = "Regex to match the name of the servers"
        self._sub_config.add_argument("--name", "-n", help=_desc)
        _desc = "Regex to match for servers to ignore"
        self._sub_config.add_argument("--skip-name", "-s", dest="skip_name",
                                      help=_desc)
        _desc = "Minimum age (1d, 2w, 6m, 1y)"
        self._sub_config.add_argument("--age", "-a", help=_desc)

    def process(self, deletion):
        """
        Fetches the list of servers and processes them to filter out which
        ones ought to actually be deleted.

        :return: None
        """
        conn = self._get_conn()
        self._config.info("Connecting to OpenStack to retrieve server list")
        if(deletion):
            # We only wish to look at servers which have been flagged
            self.__set_flagged()
            self.__targets = self.__flagged
        else:
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
        self.__flagged = []

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
        age = self._config.get_arg('age')
        if age is not None:
            self._config.debug("Parsing dates")
            self._interval = self.parse_interval(self._config.get_arg('age'))
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

    def __set_flagged(self):
        """
        Processes the txt file associated with the cloud to put all flagged
        servers into the __flagged field.

        :return: None
        """
        self.__flagged = []
        conn = self._get_conn()
        # List of server names that have been flagged to possibly be deleted
        delete_list = []
        # Open reader for the flagged file
        reader = open(conn.name + "_flagged", 'r+')
        for line in reader:
            # delete the newline character at the end of the line
            delete_list.append(line[:-1])

        for id in delete_list:
            server = conn.get_server(id)
            self.__flagged.append(server)
        reader.write("")
        reader.close()

    def write_to_flagged(self):
        """
        Writes the ids of flagged servers to the correct _flagged.txt file,
        then sends emails if the flag is set in emails.json.
        """
        conn = self._get_conn()
        writer = open(conn.name + "_flagged", 'w')
        flag_log = ""
        for server in self.__targets:
            self.__flagged.append(server)
            id = server.id
            flag_log = flag_log + (id + "\n")
        writer.write(flag_log)
        writer.close()
        if(self._config.get_emails()["Email"]) == "Y":
            self.send_emails()

    def send_emails(self):
        """
        Sends warning emails to the owners of all flagged servers, if they have
        an email to send to. Email settings depend on input args to the script.

        :return: None
        """
        emails = self._config.get_emails()
        sender = emails["Sender"]
        smtp_name = emails["smtp_server"]
        port = emails["smtp_port"]
        conn = self._get_conn()
        # Loop over flagged servers to send emails to the users associated with
        # them.
        for server in self.__flagged:
            user = conn.get_user_by_id(server.user_id, False)
            # Cannot send an email to a user with no email
            if(user.email is not None):
                receiver = user.email
                message = user.name + ", \n Your server, " + server.name
                message = message + ''' will be deleted in 24 hours, or at the
                    next call to this script, if you do not change the name of
                    the server to include 'pet_' at the start of the name. '''

                with smtplib.SMTP(smtp_name, port) as email:
                    email.sendmail(sender, receiver, message)
