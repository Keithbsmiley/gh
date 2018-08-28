#!/usr/bin/env python3
#
# Download the first asset from the newest release from a GitHub repo
# Usage: ghb download-release USER/REPO [-f/--filename only print the filename]
#

from requests import get
import argparse
import signal
import sys

URL = "https://api.github.com/repos/%s/releases"


def signal_handle(sig, frame):
    sys.exit(0)


def extension(t, default):
    if t == "zip":
        return t
    elif t == "x-gzip":
        return "tar.gz"
    else:
        return default


def print_filename(filename, only_filename):
    if only_filename:
        print(filename)
    else:
        print("Release saved to %s" % filename)


def main(repo):
    r = get(URL % repo)
    response_json = r.json()
    if len(response_json) < 1:
        print("No releases for %s" % repo)
        sys.exit(1)

    newest = response_json[0]
    assets = newest["assets"]
    first_asset = assets[0]
    asset_url = first_asset["browser_download_url"]
    content_type = first_asset["content_type"].split('/')[-1]
    default = first_asset["name"].split(".")[-1]
    headers = {"Accept": "application/octet-stream"}
    r = get(asset_url, headers=headers, stream=True)
    filename = "release.%s" % extension(content_type, default)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
            f.flush()

    return filename


signal.signal(signal.SIGINT, signal_handle)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Download the most recent release of a repo")
    parser.add_argument("repo", help="the user/repo")
    parser.add_argument("-f", "--filename", action="store_true",
                        help="only print the filename",
                        default=False)
    ns = parser.parse_args()
    filename = main(ns.repo)
    print_filename(filename, ns.filename)