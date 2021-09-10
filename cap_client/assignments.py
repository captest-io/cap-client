"""
handling api requests for assignments
"""

from urllib.request import urlretrieve
from .api import Api
from .datafiles import Datafile


class Assignment(Api):
    """interface for /assignment/ API endpoints"""

    def list(self, username=None):
        if username is None:
            username = self.credentials.username
        return self.get("/assignment/"+username)

    def submit(self, uuid, tags=None):
        tags = "" if tags is None else tags
        return self.post("/assignment/submit/" + uuid, {"tags": tags})

    def start(self, uuid=None, name=None, version=None):
        """start a new assignment"""
        body = {"name": name, "version": version}
        if uuid is not None:
            body = {"uuid": uuid}
        return self.post("/assignment/create/", body)

    def download(self, uuid):
        """download data files from the server for one assignment"""
        datafiles = self.get("/data/list/" + uuid)
        for f in datafiles:
            f_url = self.api_url + "/static/" + f["path"]
            f_basename = f_url.split("/")[-1]
            urlretrieve(f_url, f_basename)
        return datafiles

    def upload(self, uuid, file_path):
        """upload a response file for one assignment"""
        datafile = Datafile(self.api_url, self.credentials)
        return datafile.upload(file_path,
                               file_role="response",
                               parent_type="assignment",
                               parent_uuid=uuid,
                               source=self.username,
                               license="CC BY 4.0")

    def remove(self, uuid):
        """remove a response file for one assignment"""
        datafiles = self.get("/data/list/"+uuid)
        datafile = Datafile(self.api_url, self.credentials)
        for df in datafiles:
            if df["file_role"] != "response":
                continue
            return datafile.delete(df["uuid"])

    def view(self, uuid):
        """view the status (including score) of an assignment"""
        return self.get("/assignment/view/" + uuid)
