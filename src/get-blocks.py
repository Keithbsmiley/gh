#!/usr/bin/env python3
#
# Get the list of users you've blocked on github
# Note: your token needs 'user' access for this API
# Usage: ghb get-blocks
#

from helpers import credentials
from requests import get
import argparse
import signal
import sys

URL = "https://api.github.com/user/blocks"
NETRC_MACHINE = "api.github.com"


def signal_handle(sig, frame):
    sys.exit(0)


def main():
    user, password = credentials.credentials(NETRC_MACHINE)
    headers = {
        'Accept': 'application/vnd.github.giant-sentry-fist-preview+json'
    }
    r = get(URL, auth=(user, password), headers=headers)
    if r.status_code != 200:
        print("Failed to get blocked users: %d" % r.status_code)
        print(r.json())
        sys.exit(1)

    for blob in r.json():
        print(blob["login"])

signal.signal(signal.SIGINT, signal_handle)
if __name__ == "__main__":
    main()