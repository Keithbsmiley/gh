#!/usr/bin/env python3
#
# Open a GitHub PR from the current branch to master or a specified branch
# Edit the PR message in vim
# Usage: ghb pr [BRANCH]
#
# Example:
# ghb pr # This opens a PR against master
# ghb pr some-branch # This opens the PR against 'some-branch'
#

from helpers import credentials
from json import dumps
from subprocess import check_output
from webbrowser import open_new_tab
import os
import os.path
import requests
import signal
import sys

URL = "https://api.github.com/repos/%s/pulls"
EXISTING_URL = URL
NETRC_MACHINE = "api.github.com"
HEADERS = {'Accept': 'application/vnd.github.v3+json'}


def signal_handle(sig, frame):
    sys.exit(0)


def current_branch_name():
    branch = check_output("git symbolic-ref --short HEAD".split()).strip()
    return "%s:%s" % (repo_username(), branch)


def repo_username():
    return repo_with_username().split("/")[0]


def repo_with_username():
    if "@" in origin_url():
        url_parts = filter_empty_string(origin_url().split(":"))
        username_repo = url_parts[-1]
    else:
        url_parts = filter_empty_string(origin_url().split("/"))
        username_repo = "/".join(url_parts[-2:])

    if username_repo.endswith(".git"):
        return username_repo[:-4]

    return username_repo


def filter_empty_string(array):
    return [a for a in array if len(a) > 0]


def origin_url():
    return check_output("git config --get remote.origin.url".split()).strip()


def git_directory():
    return check_output("git rev-parse -q --git-dir".split()).strip()


def pr_message_file():
    return os.path.join(git_directory(), "PULLREQUEST_EDITMSG")


def last_commit_message():
    message = check_output("git log --format=%B -n 1".split()).strip()
    return commit_from_string(message)


def _get_last_branch():
    return check_output("git rev-parse --abbrev-ref @{-1}".split()).strip()


def commit_from_string(string):
    values = [x.strip() for x in string.split("\n", 1)]
    if len(values) < 2:
        values.append("")
    return values


def pr_message():
    file_path = pr_message_file()
    title, body = last_commit_message()
    with open(file_path, "w") as f:
        f.write(title + "\n\n" + body + "\n")
        f.write("\n# The first line will be the title of the PR")
        f.write("\n# Anything below the first line will be the body\n")

    command = 'vim -c "set ft=gitcommit" %s' % file_path
    code = os.system(command)
    if code != 0:
        sys.exit("Not submitting PR")

    f = open(file_path, "r")
    text = f.read()
    f.close()

    lines = text.split("\n")
    lines = [x for x in lines if not x.startswith("#")]
    text = "\n".join(lines)
    if len(text.strip()) < 1:
        sys.exit("Not submitting with empty message")

    return commit_from_string(text)


def open_existing_pr(api_url, local, remote):
    print("Opening existing PR")
    username, password = credentials.credentials(NETRC_MACHINE)
    payload = {"head": local, "base": remote}
    r = requests.get(api_url,
                     auth=(username, password),
                     headers=HEADERS,
                     data=dumps(payload))
    if r.status_code == 200:
        pr = r.json()[0]
        open_new_tab(pr["html_url"])


def submit_pr(remote):
    if remote == "-":
        remote = _get_last_branch()

    text, body = pr_message()
    username, password = credentials.credentials(NETRC_MACHINE)
    local = current_branch_name()
    if local.split(":")[-1] == remote:
        sys.exit("Cannot submit PR from the same branch")
    api_url = URL % repo_with_username()
    payload = {"title": text, "body": body, "base": remote, "head": local}
    r = requests.post(api_url,
                      auth=(username, password),
                      headers=HEADERS,
                      data=dumps(payload),
                      )
    json = r.json()
    if r.status_code == 201:
        open_new_tab(json["html_url"])
    elif r.status_code == 422:
        open_existing_pr(api_url, local, remote)
    else:
        error_message = json["errors"][0]["message"]
        print(error_message)


signal.signal(signal.SIGINT, signal_handle)
if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Usage: ghb pr [REMOTE]")
    elif len(sys.argv) == 2:
        submit_pr(sys.argv[1])
    else:
        submit_pr("master")