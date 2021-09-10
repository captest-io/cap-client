"""
argparse object with common arguments for user-level and admin-level clients
"""

import argparse

parser = argparse.ArgumentParser(
    description="client for interfacing with www.captest.io"
)

# users and credentials
parser.add_argument("--username", action="store", default=None,
                    help="username")
parser.add_argument("--token", action="store", default=None,
                    help="authorization token")
parser.add_argument("--secrets", action="store", default="secrets.yaml",
                    help="file with username and passwords")
parser.add_argument("--save_secrets", action="store_true",
                    help="save secrets into a local disk file")
# url for api
parser.add_argument("--api", action="store", default="https://api.captest.io",
                    help="url to the api server")
# verbosity level
parser.add_argument("--verbose", action="store_true",
                    help="output INFO logging messages")

# subparsers
subparsers = parser.add_subparsers(help="action", dest="action", required=True)
