"""
handling api requests to download example datasets
"""

from os.path import join
from urllib.request import urlretrieve
from .api import Api
from .errors import ClientError


class ExampleDataset(Api):
    """downloading example datasets associated with challenges"""

    def download(self, uuid=None, name=None, version=None, data_dir="."):
        """download all example files associated with a challenge"""
        identifier = uuid if uuid is not None else name + "/" + version
        doc_data = self.get("/challenge/view/" + identifier)
        if "name" not in doc_data:
            raise ClientError(str(doc_data))
        doc_name, doc_version = doc_data["name"], doc_data["version"]
        assignment_uuid = doc_data["demo_assignment_uuid"]
        datafiles = self.get("/data/list/" + assignment_uuid)
        result = []
        for f in datafiles:
            f_url = self.api_url + "/static/" + f["path"]
            f_basename = f_url.split("/")[-1]
            f_pretty = f_basename.replace(assignment_uuid,
                                          doc_name + "_v" + doc_version)
            f_path = join(data_dir, f_pretty)
            urlretrieve(f_url, f_path)
            result.append({
                "file_role": f["file_role"],
                "path": f["path"],
                "local_path": f_path
            })
        return result
