"""
a command-line client for admin users of the captest.io api
Usage: python cap_admin_client.py --help
"""

import logging
from json import dumps
from os import listdir
from os.path import join, basename
from cap_client.parser import parser, subparsers
from cap_client.validations import validate_config, validate_credentials
from cap_client.errors import ValidationError
from cap_client.credentials import CredentialsManager
from cap_client.docs import Doc
from cap_client.search import Search


# this is a command line utility
if __name__ != "__main__":
    exit()

logging.basicConfig(format='[%(asctime)s] %(levelname) -8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.WARNING)


# ############################################################################
# Arguments

parser.description = "admin client for interfacing with www.captest.io"

# create/publish/upload for documentation/blog/image/challenge/resource docs
sp_create = subparsers.add_parser("create",
                                  help="create a new document")
sp_publish = subparsers.add_parser("publish",
                                   help="publish/update a document")
sp_upload_primary = subparsers.add_parser("upload_primary",
                                          help="upload primary data files")
sp_upload_support = subparsers.add_parser("upload_support",
                                          help="upload support data files")
sp_upload = subparsers.add_parser("upload",
                                  help="upload primary and support data files")
sp_delete = subparsers.add_parser("delete",
                                  help="delete a document")
for sp in [sp_create, sp_publish, sp_upload,
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
    sp.add_argument("--checks", action="store", default="strict",
                    choices=["strict", "none"],
                    help="run non-obligatory consistency checks")

# build search
sp_search = subparsers.add_parser("build_search")

# summarize content
sp_summarize = subparsers.add_parser("summarize")


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

doc = Doc(config.api, credentials)
search = Search(config.api, credentials)
result = []

# managing images, challenged, documentation pages, blog posts, etc.
doc_actions = {
    "create": doc.create,
    "publish": doc.update,
    "upload_primary": doc.upload_primary,
    "upload_support": doc.upload_support,
    "upload": doc.upload
}
if config.action in doc_actions:
    action = doc_actions[config.action]
    files = [config.file]
    if config.dir is not None:
        files = [join(config.dir, _) for _ in listdir(config.dir)]
    files = [_ for _ in files if _ is not None and _.endswith(".md")]
    files = [_ for _ in files if not basename(_).startswith("_")]
    for f in files:
        result.append(action(f, config.collection, action=config.action))

# deleting challenges, resources, etc.
if config.action == "delete":
    result.append(doc.delete(config.file, config.collection))

# managing search
if config.action == "build_search":
    result = search.build()
if config.action == "summarize":
    result = search.summary()

# display output from the script
print(dumps(result, indent=2))

if config.save_secrets:
    credentials.save()
