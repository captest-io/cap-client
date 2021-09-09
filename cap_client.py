"""
a command-line client for interacting with the captest.io api
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
parser.add_argument("--api", action="store", default="https://api.captest.io/",
                    help="url to the api server")
# set verbosity level
parser.add_argument("--verbose", action="store_true",
                    help="output INFO logging messages")


# subparsers
subparsers = parser.add_subparsers(help="action", dest="action")

# create/publish/upload for documentation/blog/image/challenge/resource docs
sp_create = subparsers.add_parser("create",
                                 help="create a new document")
sp_publish = subparsers.add_parser("publish",
                                   help="publish/update a document")
sp_obsolete = subparsers.add_parser("obsolete",
                                   help="mark as obsolete")
sp_upload_primary = subparsers.add_parser("upload_primary",
                                          help="upload primary data files")
sp_upload_support = subparsers.add_parser("upload_support",
                                          help="upload support data files")
sp_delete = subparsers.add_parser("delete",
                                  help="delete a document")
for sp in [sp_create, sp_publish, sp_obsolete,
           sp_upload_primary, sp_upload_support, sp_delete]:
    sp.add_argument("--collection", action="store",
                    default=None, required=True,
                    choices=["documentation", "blog", 'resource',
                             "challenge", "image"],
                    help="type of document to process")
    sp.add_argument("--file", action="store", default=None,
                    help="path to document file")
    sp.add_argument("--dir", action="store", default=None,
                    help="path to directory with document files")

# list content for assignments, datafiles, etc.
sp_list = subparsers.add_parser("list", help="list content")
sp_list.add_argument("--collection", action="store",
                     default=None, required=True,
                     choices=["assignment", "datafile"],
                     help="type of document to list")
sp_list.add_argument("--parent_uuid", action="store",
                     default=None,
                     help="uuid of parent object (required to list datafiles)")

# start a new assignment
sp_start = subparsers.add_parser("start",
                                 help="start a new assignment")
sp_start.add_argument("--name", action="store", default=None,
                      help="challenge name")
sp_start.add_argument("--version", action="store", default=None,
                      help="challenge version")
sp_start.add_argument("--uuid", action="store", default=None,
                      help="challenge identifier (overrides name and version)")

# download data associated with an assignment
sp_download = subparsers.add_parser("download",
                                    help="download data files for an assignment")
sp_view = subparsers.add_parser("view",
                                help="view the status of an assignment")
for sp in [sp_download, sp_view]:
    sp.add_argument("--uuid", action="store",
                    default=None, required=True,
                    help="uuid of an assignment")

# upload response data files
sp_upload_response = subparsers.add_parser("upload_response",
                                           help="upload a response to the server")
sp_upload_response.add_argument("--uuid", action="store",
                                default=None, required=True,
                                help="uuid of assignment")
sp_upload_response.add_argument("--file", action="store",
                                default=None, required=True,
                                help="path to response data file")

# remove a temporary datafile
sp_remove = subparsers.add_parser("remove", help="remove data files from server")
sp_remove.add_argument("--uuid", action="store",
                       default=None, required=True,
                       help="data file identifier")

# submit an assignment
sp_submit = subparsers.add_parser("submit",
                                  help="submit an assignment for evaluation")
sp_submit.add_argument("--uuid", action="store", default=None, required=True,
                       help="assignment identifier")
sp_submit.add_argument("--tags", action="store", default=None,
                       help="tags (comma separated)")


# build search
sp_search = subparsers.add_parser("build_search")

# summarize content
sp_summarize = subparsers.add_parser("summarize")


# ############################################################################
# validation of command-line arguments

logging.basicConfig(format='[%(asctime)s] %(levelname) -8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.WARNING)

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

# make sure there is a username from: (1) command line or (2) secrets file
if credentials.username is None:
    logging.error("could not determine username")
    exit()

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
if config.action == "list":
    if config.collection == "assignment":
        result = assignments.list_assignments(api, credentials)
    elif config.collection == "datafile":
        result = datafiles.list_datafiles(api, credentials, config.parent_uuid)

# managing assignments
if config.action == "start":
    result = assignments.start(api, credentials, uuid=config.uuid,
                               name=config.name, version=config.version)
if config.action == "download":
    result = assignments.download(api, credentials, uuid=config.uuid)
if config.action == "upload_response":
    result = datafiles.upload(api, credentials,
                              file_path=config.file,
                              file_role="response",
                              parent_type="assignment",
                              parent_uuid=config.uuid,
                              source=credentials.username,
                              license="CC BY 4.0")
if config.action == "remove":
    result = datafiles.remove(api, credentials, uuid=config.uuid)
if config.action == "submit":
    result = assignments.submit(api, credentials,
                                uuid=config.uuid,
                                tags=config.tags)
if config.action == "view":
    result = assignments.view(api, credentials, uuid=config.uuid)


# admin tools - managing blog/documentation/challenge/resource documents
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

# admin tools - managing search
if config.action == "build_search":
    result = search.build(api, credentials)
if config.action == "summarize":
    result = search.summary(api, credentials)


# admin tools - delete assignments, challenges, etc.
if config.action == "delete":
    result.append(docs.delete(api, credentials, config.file,
                              collection=config.collection))


# display output from the script
print(dumps(result, indent=2))

if config.save_secrets:
    credentials.save()
