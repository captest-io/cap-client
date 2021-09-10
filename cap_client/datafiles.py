"""
handling api requests for assignments
"""

from os.path import basename
from .api import Api


class Datafile(Api):
    """interface for /data/ API endpoints"""

    def list(self, parent_uuid):
        """fetch all datafiles associated with a given parent object"""
        return self.get("/data/list/" + parent_uuid)

    def upload(self, file_path, file_role,
               parent_uuid, parent_type, source, license):
        """upload a file"""
        metadata = {
            "file_role": file_role,
            "file_name": basename(file_path),
            "parent_uuid": parent_uuid,
            "parent_type": parent_type,
            "source": source,
            "license": license
        }
        return self.post_upload("/data/upload", file_path, metadata)

    def delete(self, uuid):
        """send a request to remove a datafile"""
        return self.post("/data/delete/", {"uuid": uuid})
