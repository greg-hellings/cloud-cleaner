Travis CI status: [![Build Status](https://travis-ci.org/greg-hellings/cloud-cleaner.svg?branch=master)](https://travis-ci.org/greg-hellings/cloud-cleaner)

Current code coverage: [![codecov](https://codecov.io/gh/greg-hellings/cloud-cleaner/branch/master/graph/badge.svg)](https://codecov.io/gh/greg-hellings/cloud-cleaner)

Current PyPI Release: [![PyPI version](https://badge.fury.io/py/cloud-cleaner.svg)](https://badge.fury.io/py/cloud-cleaner)

# Function

Cloud Cleaner is a utility designed to cleanup left over resources in an OpenStack environment. Often, when an
OpenStack tenant is used for testing and ephemeral host provisioning, artifacts can be left over from previous runs
for a number of reasons. Perhaps a test run failed and did not include proper teardown procedures. Perhaps someone
provisioned a test resource but forgot about it or left the team and never tore it down.

Cloud Cleaner provides a way to specify that resources fitting certain criteria ought to be expunged from the
tenant. This can help free up quota and limit the resources being utilized to only those that are actively necessary.
The primary component needing to be freed up are VMs, as these are resource intensive to maintain and are difficult
to reuse properly. Other resource types can be added to Cloud Cleaner as the need arises.

# Installation

Cloud Cleaner depends on several Python libraries, and supports Python versions 2.7 and 3.3+. The recommended way to
install the application is through a Virtual Environment. To create a virtualenv do the following:

#### Python 2
`virtualenv cloud-cleaner`

#### Python 3
`pyvenv cloud-cleaner`

Once the virtualenv is created, you can install the application with the "pip" command, as follows:

```bash
source cloud-cleaner/bin/activate
pip install -U cloud-cleaner
```

This will install the latest version of Cloud Cleaner in your virtualenv. Likewise, if you already have it installed in
that virtualenv, this will update you to the latest installed version.

# Configuration

Cloud Cleaner needs to know about your OpenStack endpoints. It uses the standard
[openstack sdk](https://docs.openstack.org/openstacksdk/latest/user/config/configuration.html) mechanism to configure
the client for OpenStack access. This mechanism is in standard use across many OpenStack clients already, and by using
the same library, Cloud Cleaner should be accessible via the standard idioms OpenStack users are accustomed to using.

The three main mechanisms that openstack sdk uses are environment variables beginning with OS_, command line flags
which can be seen by running the command `cloud-clean --help`, or through a yaml file documented as part of the standard
openstack sdk documentation. Check the docs linked above or elsewhere on the Internet to find more about how to
properly configure this app to connect to OpenStack.

# Usage

The general structure of a call to Cloud Cleaner is

`cloud-clean [global_options] {resource} [resource_options]`

The global options are things like verbosity, dry/wet run, OpenStack connection flags, email configurations, and the like. Calling the
program with the "--help" or "-h" flag will give you the full list of those options. The resource is the type of object
being cleaned up. The general "--help" option should also display all known resource types. These are such things as
"server" - meaning exactly what it says on the tin or "fip" which is a floating IP address. Each resource type can
possibly support options of its own to limit which items are actually deleted.

## Global Options

By default the application runs very quietly. Adding a single -v flag should give enough output to make you comfortable
that the program is working as intended. If the details are of particular concern, then adding a second -v switch (or
making the switch -vv) will give full debugging output. This amount of detail might be a bit "over the top", but can
be helpful if you really want to know what the program is doing

By default, the program only executes in dry-run mode. Thus, it will fetch a list of data from the OpenStack endpoint,
process it, and output locally that it is working on the devices. However, it will not actually perform any alterations
to your OpenStack environment unless run in force mode. This can be done by adding the global flag "-f" or "--force" to
the options. Doing so will result in the command performing the actual deletes after fetching and optionally filtering
the resources.

Cloud Cleaner also features email functionality, wherein the creator of a resource can be emailed if something
has or will be done to their resource. By default, the program will execute without sending any email. Email functionality
can be added by adding the global flag "-e" or "--email" to the options. If this is added, then the flags "--sender", "--smtpN",
and "--smtpP" must be included with the email address to send from, the smtp server name to use, and the smtp port to use. Precisely
what is emailed, or whether email functionality is included at all, will vary by resource.

## Resource Specific Options

### Servers

Select this type of resource by telling the cloud-clean script to operate on the "server" type. Servers currently
support three options to filter them down from the full list.

Age filtering, represented by the flag --age will search for any servers older than the specified age. If a server is half
or more than half of the specified age, then its creator will be emailed a warning if email functionality is enabled. The age uses a
basic shorthand and can be measured in hours, days, weeks, months, or years. If you want to select all servers that are
more than 2 days old, add the option "--age 2d". If you wanted servers more than 2 weeks old, go with "--age 2w". In this example,
any server older than 1 week and younger than 2 weeks would have the creator of the server emailed a warning message that their server
may be deleted at some point in the future. At the moment, there is no support for mixing and matching different time durations,
so you can't say "1d12h", you would have to say "36h".

Name filtering, represented by the flag "--name" accepts a Python-compatible regular expression that will get matched
against the name using Python's standard "match" function. Note that the "match" function defaults to matching against
the START of the name. So if you want to match "any server that has the word 'test' anywhere in its name" you need to
include wildcard characters. An appropriate string would then be ".*test.*". It is important to note that several of the
special characters in a regular expression have special meanings in shells, as well. So you will need to escape those
characters appropriately using quoting or slashes or whatever your shell environment uses. Details on the Python regex
syntax can be found [here](https://docs.python.org/3/howto/regex.html#regex-howto). The section titled "The Backslash
Plague" can be safely ignored, as it applies only to people writing a regex inside of Python code. However, a similar
"plague" could be experienced when writing out a complex regular expression in Bash.

In addition to selecting servers by name, it is possible to exclude them by name. Rather than crafting a complicated
regular expression to select against such names, you can use the "--skip-name" option. It works exactly like the --name
option, but inverts the selection by only taking servers that do not match.

It is possible to combine all three of these options. That is, if you want every server that is more than a week old,
has a name that begins with "test-" but does not contain the string "keep" anywhere in its name, you would construct the
command like this:

`cloud-clean server --age 1w --name "test-.*" --skip-name ".*keep.*"`

### Floating IPs

Select this type of resource by telling the cloud-clean script to operate on the "fip" type. Floating IP addresses
currently allow for three different options.

By default, only floating IP addresses which are not in an attached state, according to the API, will be deleted. If
all floating IPs should be considered, add the option "--with-attached" and the auto filtering will be skipped. This
option is only a flag, and accepts no arguments.

If only floating IP addresses in a certain subnet should be considered, then the option "--floating-subnet" should be
used. It takes as an argument a subnet mask definition. Arguments of this type are parsed using the Python library
documented [here](https://docs.python.org/3/library/ipaddress.html) in both Python 2 (a backport of this code exists for
Python 2.6+) and 3. In general, you can specify syntax such as "10.0.0.0/8" or "10.0.0.0/255.0.0.0".

If only floating IP addresses associated with a particular fixed IP subnet should be considered, then the option
"--static-subnet" should be used. This uses the same syntax and parsing library as the --floating-subnet option above.

As of right now no email functionality is included for Floating IPs. Attempting to do so will incur an UnimplementedError.
It is recommended to not include any of the email flags when cleaning Floating IPs.

As one would expect, any combination of these options can be used. They will all be applied, and only floating IPs that
match all conditions will be up for deletion.

Although the library underlying IP address parsing can handle both IPv4 and IPv6, it may give issues when comparing a
subnet mask from one version against an IP address from the other version. If this raises a problem, the script can be
enhanced with better handling of those cases. For now, it is a known and untested possibility that such mixing and
matching might result in the program crashing during filtering. If this happens, it will happen before any changes are
made to your OpenStack tenant.
