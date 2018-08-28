#!/usr/bin/env python3
#
# List your unread GitHub notifications
# Usage: ghb ls-notifications
#

import signal
import sys
from helpers import credentials
from requests import get


URL = "https://api.github.com/notifications"
NETRC_MACHINE = "api.github.com"


def signal_handle(sig, frame):
    sys.exit(0)


def show_pull_requests():
    user, password = credentials.credentials(NETRC_MACHINE)
    r = get(URL, auth=(user, password))
    json = r.json()
    notifications = {}

    for blob in json:
        repo_name = blob["repository"]["full_name"]
        api_url = blob["subject"]["url"]
        html_url = api_url.replace(
            "api.", "", 1).replace("/repos", "", 1).replace("/pulls/", "/pull/")
        notification = "\t%s (%s)" % (blob["subject"]["title"], html_url)
        notifications.setdefault(repo_name, []).append(notification)

    for name, urls in notifications.items():
        print(name)
        for url in urls:
            print(url)
        print()


signal.signal(signal.SIGINT, signal_handle)
if __name__ == "__main__":
    show_pull_requests()