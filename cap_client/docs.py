"""
handling api requests for blog or documentation pages
"""

import os
from os.path import dirname, join, exists, dirname
from yaml import safe_load
from .api import api_post, api_get
from .datafiles import upload
from .errors import ClientError, ValidationError
from .validations import validate_collection


def read_header_content(path):
    """read all content from a file and separate a header from the body"""

    state, _header, _content = None, [], []
    with open(path, "r") as f:
        for line in f:
            if state is None:
                if not line.startswith("---"):
                    raise ClientError("first line should start with ---")
                state = "header"
            elif state == "header":
                if line.startswith("---"):
                    state = "content"
                elif line.rstrip() == "":
                    raise ClientError("empty line in header")
                else:
                    _header.append(line.rstrip("\n"))
            elif state == "content":
                _content.append(line.rstrip("\n"))
    if state != "content":
        raise ClientError("no content")
    _header, _content = "\n".join(_header), "\n".join(_content)
    return safe_load(_header), _content.lstrip().rstrip()


def doc_body(header, content, action=""):
    """helper to construct a body object for create/update requests"""

    for field in ("uuid", "name", "tags", "title", "version"):
        if header.get(field, None) is None:
            header[field] = ""
    return {
        "action": str(action),
        "name": str(header["name"]),
        "version": str(header["version"]),
        "title": str(header["title"]),
        "tags": header["tags"].split(" "),
        "content": str(content)
    }


def prep_input(file_path, action=""):
    header, content = read_header_content(file_path)
    body = doc_body(header, content, action=action)
    return header, body


def prep_output(data, file_path):
    data["_file"] = file_path
    return data


def get_doc_uuid(api_url, credentials, collection="blog", identifier_str=""):
    """use the api to convert a name+version into a uuid identifier"""
    url = api_url + collection + "/update/" + identifier_str
    result = api_get(url, credentials.token)
    try:
        return result["uuid"]
    except KeyError:
        raise ClientError(result["detail"])
    except TypeError:
        raise


def inject_support(content, support_files, file_list, api_url):
    """replace simple file names by paths to support files"""
    result = content
    for file in file_list:
        if file["file_name"] not in support_files:
            continue
        result = result.replace(file["file_name"],
                                api_url + "static/" + file["path"])
    return result


def context_text(v, dir):
    """get text value for a context variable

    :param v: string, raw value, or filename pointing to more text
    :param dir: string, directory where to search for the data
    :return: content within a data file if a file exists, otherwise
        the raw value v
    """
    v_file = join(dir, v)
    if not exists(v_file):
        return v.strip()
    with open(v_file, "rt") as f:
        result = "".join(f.readlines())
    return result.strip()


def inject_context(content, context, dir=None):
    """replace placeholders by values from a context dictionary"""
    result = content
    for k, v in context.items():
        v_text = context_text(v, dir=dir)
        result = result.replace("{" + k + "}", v_text)
    return result


def create(api_url, credentials, file_path, collection="blog", **kwargs):
    """send a request to create a new document"""
    try:
        header, body = prep_input(file_path)
        validate_collection(collection, header)
    except (ClientError, ValidationError) as e:
        return {"_file": file_path, "_exception": e.message}
    url = api_url + collection + "/create/"
    result = api_post(url, credentials.token, body)
    return prep_output(result, file_path)


def update(api_url, credentials, file_path, collection="blog", action="publish"):
    """send document content to the server"""
    try:
        header, body = prep_input(file_path, action=action)
        validate_collection(collection, header)
    except (ClientError, ValidationError) as e:
        return {"_file": file_path, "_exception": e.message}
    # round 1 - get uuid for the document
    identifier = header["name"]
    if header["version"] is not None and header["version"] != "":
        identifier += "/" + str(header["version"])
    try:
        doc_uuid = get_doc_uuid(api_url, credentials, collection, identifier)
    except ClientError as e:
        return {"_file": file_path, "_exception": e.message}
    # round 2 - identify available support files
    list_url = api_url + "data/list/" + doc_uuid
    file_list = api_get(list_url, credentials.token)
    # round 3 - adjust the raw body with urls for support images (webp)
    body["content"] = inject_context(body["content"], header.get("context", {}),
                                     dir=dirname(file_path))
    body["content"] = inject_support(body["content"], header.get("support", []),
                                     file_list, api_url)
    # send the content to the api
    url = api_url + collection + "/update/" + doc_uuid
    result = api_post(url, credentials.token, body)
    return prep_output(result, file_path)


def primary(api_url, credentials, file_path, collection="blog", **kwargs):
    """upload a primary datafile for a document

    :param api_url: string, base url for the api
    :param credentials: object with authorization credentials
    :param file_path: string, path to md file with header and body
    :param collection: string, document type
    :param kwargs: other arguments are not used, but included for consistency
        of the function signature with update()
    :return: dictionary with a summary of the api request
    """
    try:
        header, body = prep_input(file_path)
        validate_collection(collection, header)
    except (ClientError, ValidationError) as e:
        return {"_file": file_path, "_exception": e.message}
    for k in ("datafile", "datafile_source", "datafile_license"):
        if k not in header:
            return {"_file": file_path, "_exception": "missing "+k}
    datafile_path = join(dirname(file_path), header["datafile"])
    # round 1 - fetch the latest information about the document
    identifier_str = str(header["name"]) + "/" + str(header["version"])
    doc_uuid = get_doc_uuid(api_url, credentials, collection, identifier_str)
    # round 2 - upload the datafile specified in the doc header
    result = upload(api_url, credentials, datafile_path, file_role="primary",
                    parent_uuid=doc_uuid, parent_type=collection,
                    source=header["datafile_source"],
                    license=header["datafile_license"])
    return prep_output(result, datafile_path)


def support(api_url, credentials, file_path, collection="blog", **kwargs):
    """upload support files (images/pictures)

    :param api_url: string, base url for the api
    :param credentials: object with authorization credentials
    :param file_path: string, path to md file with header and body
    :param collection: string, document type
    :param kwargs: other arguments are not used, but included for consistency
        of the function signature with update()
    :return: dictionary with a summary of the api request, including an array
        with summaries of api requests for individual support files
    """
    try:
        header, body = prep_input(file_path)
        validate_collection(collection, header)
    except (ClientError, ValidationError) as e:
        return {"_file": file_path, "_exception": e.message}
    if "support" not in header:
        return {"_file": file_path, "_exception": "no support files"}
    # round 1 - fetch the latest information about the document
    identifier = str(header["name"]) + "/" + str(header["version"])
    doc_uuid = get_doc_uuid(api_url, credentials, collection, identifier)
    # round 2 - fetch available support files
    list_url = api_url + "data/list/" + doc_uuid
    file_list = api_get(list_url, credentials.token)
    existing_filenames = [_["file_name"] for _ in file_list]
    # round 3 - upload missing support files
    result = []
    for filename in header["support"]:
        support_path = join(dirname(file_path), filename)
        if filename in existing_filenames:
            result.append({"_file": support_path, "detail": "exists"})
            continue
        file_result = upload(api_url, credentials, support_path,
                             file_role="support",
                             parent_uuid=doc_uuid,
                             parent_type=collection,
                             source=credentials.username,
                             license="CC BY 4.0")
        result.append(prep_output(file_result, support_path))
    return {"_file": file_path, "uuid": doc_uuid, "_support": result}
