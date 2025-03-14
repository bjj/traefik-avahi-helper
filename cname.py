#!/bin/env python3

import sys
import os
import logging
import logging.handlers
import syslog
import re
import signal
import functools

from argparse import ArgumentParser, ArgumentTypeError
from time import sleep

from mpublisher import AvahiPublisher

log = logging.getLogger("docker-to-cname");

def positive_int_arg(value):
    """Helper type (for argparse) to validate and return positive integer argument."""

    try:
        ivalue = int(value)
    except ValueError:
        raise ArgumentTypeError("invalid int value: %s" % repr(value))

    if ivalue <= 0:
        raise ArgumentTypeError("value must be greater than zero")

    return ivalue


def local_hostname_arg(hostname):
    """Helper type (for argparse) to validate and return a (normalized) local hostname argument."""

    if not re.match(r"^[a-z0-9][a-z0-9_-]*(?:\.[a-z0-9][a-z0-9_-]*)*\.local$", hostname, re.I):
        raise ArgumentTypeError("malformed CNAME: %s" % repr(hostname))

    return hostname.lower()


def handle_signals(publisher, signum, frame):
    """Unpublish all mDNS records and exit cleanly."""

    signame = next(v for v, k in signal.__dict__.items() if k == signum)
    log.info("Exiting on %s...", signame)
    publisher.__del__()

    # Avahi needs time to forget us...
    sleep(1)

    os._exit(0)

def main():

    pid = os.getpid()
    f = open("cname.pid", "w")
    f.write(str(pid))
    f.close()

    cnames = [line.rstrip('\n') for line in open("cnames")]
    
    handler = logging.StreamHandler(sys.stderr)
    format_string = "%(levelname)s: %(message)s"

    handler.setFormatter(logging.Formatter(format_string))
    logging.getLogger().addHandler(handler)

    log.setLevel(logging.INFO)
    publisher = None

    dns_type = os.getenv('TRAEFIK_AVAHI_HELPER_DNS_TYPE') or 'CNAME'

    while True:
        if not publisher or not publisher.available():
            publisher = AvahiPublisher(30)

            signal.signal(signal.SIGTERM, functools.partial(handle_signals, publisher))
            signal.signal(signal.SIGINT, functools.partial(handle_signals, publisher))
            signal.signal(signal.SIGQUIT, functools.partial(handle_signals, publisher))

            for cname in cnames:
                status = publisher.publish(cname, force=True, dns_type=dns_type)
                if not status:
                    log.error("failed to publish '%s'", cname)
                    continue
            if publisher.count() == len(cnames):
                log.info(f"All {dns_type} records published")
            else:
                log.warning("%d of %d {dns_type} records published", publisher.count(), len(cnames))

        sleep(1)

if __name__ == "__main__":
    main()
