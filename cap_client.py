"""
a command-line client for interacting with the captest.io api
Usage: python cap_client.py --help
"""

import logging
from json import dumps
from cap_client.parser import parser, subparsers
from cap_client.validations import validate_config, validate_credentials
from cap_client.errors import ValidationError
from cap_client.credentials import CredentialsManager
from cap_client.datafiles import Datafile
from cap_client.assignments import Assignment


# this is a command line utility
if __name__ != "__main__":
    exit()

logging.basicConfig(format='[%(asctime)s] %(levelname) -8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.WARNING)


# ############################################################################
# Arguments

parser.description = "client for interfacing with www.captest.io"

# list content for assignments, datafiles, etc.
sp_list = subparsers.add_parser("list_assignments", help="list assignments")

sp_list = subparsers.add_parser("list_files", help="list data files")
sp_list.add_argument("--uuid", action="store",
                     default=None, required=True,
                     help="uuid of parent object (e.g. assignment)")

# start a new assignment
sp_start = subparsers.add_parser("start",
                                 help="start a new assignment")
sp_start.add_argument("--name", action="store", default=None,
                      help="challenge name")
sp_start.add_argument("--version", action="store", default=None,
                      help="challenge version")
sp_start.add_argument("--uuid", action="store", default=None,
                      help="challenge identifier (overrides name and version)")

# view/download/upload associated with an assignment
sp_download = subparsers.add_parser("download",
                                    help="download data files for an assignment")
sp_view = subparsers.add_parser("view",
                                help="view the status of an assignment")
sp_upload_response = subparsers.add_parser("upload_response",
                                           help="upload a response file")
sp_remove_response = subparsers.add_parser("remove_response",
                                           help="remove a response file")
for sp in [sp_download, sp_view, sp_upload_response, sp_remove_response]:
    sp.add_argument("--uuid", action="store",
                    default=None, required=True,
                    help="uuid of an assignment")
sp_upload_response.add_argument("--file", action="store",
                                default=None, required=True,
                                help="path to response data file")

# submit an assignment
sp_submit = subparsers.add_parser("submit",
                                  help="submit an assignment for evaluation")
sp_submit.add_argument("--uuid", action="store", default=None, required=True,
                       help="assignment identifier")
sp_submit.add_argument("--tags", action="store", default=None,
                       help="tags (comma separated)")


# ############################################################################
# validation of command-line arguments

try:
    config = validate_config(parser.parse_args())
    credentials = CredentialsManager(username=config.username,
                                     path=config.secrets,
                                     token=config.token)
    credentials = validate_credentials(credentials)
except ValidationError as e:
    logging.error(e.message)
    exit()
if config.verbose:
    logging.getLogger().setLevel(logging.INFO)


# ############################################################################
# distribute work to handling functions

assignment = Assignment(config.api, credentials)
datafile = Datafile(config.api, credentials)

result = []

if config.action == "list_assignments":
    result = assignment.list()
if config.action == "list_files":
    result = datafile.list(config.uuid)

if config.action == "start":
    result = assignment.start(uuid=config.uuid,
                              name=config.name, version=config.version)
if config.action == "download":
    result = assignment.download(uuid=config.uuid)
if config.action == "upload_response":
    result = assignment.upload(uuid=config.uuid, file_path=config.file)
if config.action == "remove_response":
    result = assignment.remove(uuid=config.uuid)
if config.action == "submit":
    result = assignment.submit(uuid=config.uuid, tags=config.tags)
if config.action == "view":
    result = assignment.view(uuid=config.uuid)

print(dumps(result, indent=2))

if config.save_secrets:
    credentials.save()
