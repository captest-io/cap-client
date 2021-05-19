"""
a command-line client for interacting with the api
Usage: python cap_client.py --help
"""


import argparse
import logging
from json import dumps
from os import listdir
from os.path import join, basename
from getpass import getpass
from cap_client.validations import validate_config, ValidationError
from cap_client.credentials import CredentialsManager
from cap_client import assignments, docs, datafiles, search


# this is a command line utility
if __name__ != "__main__":
    exit()


# ############################################################################
# Arguments

parser = argparse.ArgumentParser(description="cap_client")

# compulsory arguments
parser.add_argument("action", action="store",
                    help="Name of action to perform with the client",
                    choices=["assignments", "datafiles",
                             "upload", "remove",
                             "submit",
                             "create", "publish", "obsolete",
                             "upload_primary", "upload_support",
                             "build_search", "summary"])
parser.add_argument("--username", action="store", required=True,
                    help="username")
parser.add_argument("--token", action="store", default=None,
                    help="authorization token")


# access address and credentials
parser.add_argument("--api", action="store", default="https://api.captest.io/",
                    help="url to the api server")
parser.add_argument("--secrets", action="store", default="secrets.yaml",
                    help="file with username and passwords")
parser.add_argument("--save_secrets", action="store_true",
                    help="save secrets into a local disk file")

# documents (e.g. blog, documentation, resource, etc.)
parser.add_argument("--collection", action="store", default=None,
                    choices=["documentation", "blog", 'resource', "challenge",
                             "image"],
                    help="document type used with --create and --publish")
parser.add_argument("--file", action="store", default=None,
                    help="path to file to process")
parser.add_argument("--dir", action="store", default=None,
                    help="path to directory to process")

# uploading of data files
parser.add_argument("--parent_uuid", action="store", default=None,
                    help="uuid of parent object for uploaded file")
parser.add_argument("--parent_type", action="store", default=None,
                    choices=["assignment", "challenge", "resource"],
                    help="association for uploaded file")
parser.add_argument("--file_role", action="store", default=None,
                    choices=["response", "primary", "support"],
                    help="role for uploaded file")
parser.add_argument("--uuid", action="store", default=None,
                    help="object identifier")

# logging
parser.add_argument("--verbose", action="store_true",
                    help="output INFO logging messages")

logging.basicConfig(format='[%(asctime)s] %(levelname) -8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.WARNING)


# ############################################################################
# script body

try:
    config = validate_config(parser.parse_args())
    if config.verbose:
        logging.getLogger().setLevel(logging.INFO)
except ValidationError as e:
    logging.error(e.message)
    exit()

credentials = CredentialsManager(config.api+"auth/token/",
                                 username=config.username,
                                 path=config.secrets)

# get credentials from:
# (1) command line, (2) secrets file, (3) interactive prompt
if config.token is not None:
    credentials.token = config.token
if credentials.token is None:
    credentials.token = getpass("Oauth token: ")
if credentials.token is None:
    logging.error("could not identify authorization token")
    exit()


# ############################################################################
# distribute work to handling functions

api = config.api
result = []

# listing items
if config.action == "assignments":
    result = assignments.list_assignments(api, credentials)
if config.action == "datafiles":
    result = datafiles.list_datafiles(api, credentials, config.parent_uuid)

# data upload and data file management
if config.action == "upload":
    result = datafiles.upload(api, credentials,
                              file_path=config.file,
                              file_role=config.file_role,
                              parent_type=config.parent_type,
                              parent_uuid=config.parent_uuid)
if config.action == "remove":
    result = datafiles.remove(api, credentials, uuid=config.uuid)
if config.action == "submit":
    result = assignments.submit(api, credentials, uuid=config.uuid)

# managing search
if config.action == "build_search":
    result = search.build(api, credentials)
if config.action == "summary":
    result = search.summary(api, credentials)

# text document management
doc_actions = ("create", "publish", "obsolete",
               "upload_primary", "upload_support")
if config.action in doc_actions:
    action_fun = docs.update
    if config.action == "create":
        action_fun = docs.create
    elif config.action == "upload_primary":
        action_fun = docs.primary
    elif config.action == "upload_support":
        action_fun = docs.support
    files = [config.file]
    if config.dir is not None:
        files = [join(config.dir, _) for _ in listdir(config.dir)]
    files = [_ for _ in files if _.endswith(".md")]
    files = [_ for _ in files if not basename(_).startswith("_")]
    for f in files:
        result.append(action_fun(api, credentials, f,
                                 collection=config.collection,
                                 action=config.action))


# display output from the script
print(dumps(result, indent=2))

if config.save_secrets:
    credentials.save()
