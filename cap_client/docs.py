"""
handling api requests for blog or documentation pages
"""

from os.path import join, exists, dirname
from yaml import safe_load
from .api import Api
from .datafiles import Datafile
from .errors import ClientError, ValidationError
from .validations import validate_collection, validate_notes


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


def prep_notes(notes):
    """ensure that a notes object is a markdown-like string"""
    if type(notes) is str:
        return notes
    if type(notes) is list:
        result = []
        for line in notes:
            if not line.startswith("- "):
                line = "- "+line
            result.append(line)
        result = "\n".join(result)
    return result


def prep_output(data, file_path):
    data["_file"] = file_path
    return data


def inject_support(content, support_files, file_list, api_url):
    """replace simple file names by paths to support files"""
    result = content
    for file in file_list:
        if file["file_name"] not in support_files:
            continue
        result = result.replace(file["file_name"],
                                api_url + "/static/" + file["path"])
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
    if type(content) is list:
        return [inject_context(_, context, dir=dir) for _ in content]
    result = content
    for k, v in context.items():
        k_placeholder = "{" + k + "}"
        if k_placeholder in content:
            v_text = context_text(v, dir=dir)
            result = result.replace(k_placeholder, v_text)
        if k == content.strip():
            v_text = context_text(v, dir=dir)
            result = result.replace(k, v_text)
    return result.strip()


class Doc(Api):
    """interface for API endpoints for documents"""

    def doc_uuid(self, collection="blog", identifier=""):
        """use the api to convert a name+version into a uuid identifier"""
        result = self.get("/"+collection + "/update/" + identifier)
        try:
            return result["uuid"]
        except KeyError:
            raise ClientError(result["detail"])
        except TypeError:
            raise

    def create(self, file_path, collection="blog", **kwargs):
        """send a request to create a new document"""
        try:
            header, body = prep_input(file_path)
            validate_collection(collection, header)
        except (ClientError, ValidationError) as e:
            return {"_file": file_path, "_exception": e.message}
        result = self.post("/"+collection + "/create/", body)
        return prep_output(result, file_path)

    def update(self, file_path, collection="blog", action="publish"):
        """send document content to the server"""
        try:
            header, body = prep_input(file_path, action=action)
            validate_collection(collection, header)
            header = validate_notes(header)
        except (ClientError, ValidationError) as e:
            return {"_file": file_path, "_exception": e.message}
        # round 1 - get uuid for the document
        identifier = header["name"]
        if header["version"] is not None and header["version"] != "":
            identifier += "/" + str(header["version"])
        try:
            doc_uuid = self.doc_uuid(collection, identifier)
        except ClientError as e:
            return {"_file": file_path, "_exception": e.message}
        # round 2 - identify available support files
        file_list = self.get("/data/list/"+doc_uuid)
        _context = header.get("context", {})
        _dir = dirname(file_path)
        # round 3 - adjust the paylod
        # (construct urls for support images, use content from templates)
        body["content"] = inject_context(body["content"], _context, dir=_dir)
        body["content"] = inject_support(body["content"],
                                         header.get("support", []),
                                         file_list, self.api_url)
        body["notes"] = inject_context(header["notes"], _context, dir=_dir)
        body["notes"] = prep_notes(body["notes"])
        # send the content to the api
        result = self.post("/" + collection + "/update/" + doc_uuid, body)
        return prep_output(result, file_path)

    def upload_primary(self, file_path, collection="blog",
                       header=None, body=None, doc_uuid=None,
                       **kwargs):
        """upload a primary datafile for a document

        :param file_path: string, path to md file with header and body
        :param collection: string, document type
        :param header: dictionary with header (if not available, it will be
            read from file)
        :param body: document body (if not available, it will be read from file)
        :param doc_uuid: identifier for the document (if not available, will
            be obtained from api)
        :param kwargs: other arguments are not used, but included for consistency
            of the function signature with update()
        :return: dictionary with a summary of the api request
        """
        if header is None or body is None:
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
        if doc_uuid is None:
            identifier = str(header["name"]) + "/" + str(header["version"])
            doc_uuid = self.doc_uuid(collection, identifier)
        # round 2 - upload the datafile specified in the doc header
        datafile = Datafile(self.api_url, self.credentials)
        result = datafile.upload(datafile_path,
                                 file_role="primary",
                                 parent_uuid=doc_uuid,
                                 parent_type=collection,
                                 source=header["datafile_source"],
                                 license=header["datafile_license"])
        return prep_output(result, datafile_path)

    def upload_support(self, file_path, collection="blog",
                       header=None, body=None, doc_uuid=None,
                       **kwargs):
        """upload support files (images/pictures)

        :param file_path: string, path to md file with header and body
        :param collection: string, document type
        :param header: dictionary with header (if not available, it will be
            read from file)
        :param body: document body (if not available, it will be read from file)
        :param doc_uuid: identifier for the document (if not available, will
            be obtained from api)
        :param kwargs: other arguments are not used, but included for consistency
            of the function signature with update()
        :return: dictionary with a summary of the api request, including an array
            with summaries of api requests for individual support files
        """
        if header is None or body is None:
            try:
                header, body = prep_input(file_path)
                validate_collection(collection, header)
            except (ClientError, ValidationError) as e:
                return {"_file": file_path, "_exception": e.message}
        if "support" not in header:
            return {"_file": file_path, "_support": []}
        # round 1 - fetch the latest information about the document
        if doc_uuid is None:
            identifier = str(header["name"]) + "/" + str(header["version"])
            doc_uuid = self.doc_uuid(collection, identifier)
        # round 2 - fetch available support files
        file_list = self.get("/data/list/"+doc_uuid)
        existing_filenames = [_["file_name"] for _ in file_list]
        # round 3 - upload missing support files
        result = []
        datafile = Datafile(self.api_url, self.credentials)
        for filename in header["support"]:
            support_path = join(dirname(file_path), filename)
            if filename in existing_filenames:
                result.append({"_file": support_path, "detail": "exists"})
                continue
            file_result = datafile.upload(support_path,
                                          file_role="support",
                                          parent_uuid=doc_uuid,
                                          parent_type=collection,
                                          source=self.username,
                                          license="CC BY 4.0")
            result.append(prep_output(file_result, support_path))
        return {"_file": file_path, "uuid": doc_uuid, "_support": result}

    def upload(self, file_path, collection="blog", **kwargs):
        """upload both primary and support data files"""
        try:
            header, body = prep_input(file_path)
            validate_collection(collection, header)
        except (ClientError, ValidationError) as e:
            return {"_file": file_path, "_exception": e.message}
        identifier = str(header["name"]) + "/" + str(header["version"])
        doc_uuid = self.doc_uuid(collection, identifier)
        primary = self.upload_primary(file_path, collection,
                                      header=header, body=body,
                                      doc_uuid=doc_uuid)
        support = self.upload_support(file_path, collection,
                                      header=header, body=body,
                                      doc_uuid=doc_uuid)
        return {
            "_file": file_path,
            "uuid": doc_uuid,
            "_primary": primary,
            "_support": support["_support"]
        }

    def delete(self, file_path, collection="blog"):
        """send a command to delete a document"""
        try:
            header, body = prep_input(file_path, action="update")
            validate_collection(collection, header)
        except (ClientError, ValidationError) as e:
            return {"_file": file_path, "_exception": e.message}
        # round 1 - get uuid for the document
        identifier, version = header["name"], header["version"]
        try:
            self.doc_uuid(collection, identifier+"/"+str(version))
        except ClientError as e:
            return {"_file": file_path, "_exception": e.message}
        # round 2 - send command to delete
        body = {"identifier": header["name"], "version": str(version)}
        result = self.post("/"+collection+"/delete/", body)
        return prep_output(result, file_path)
