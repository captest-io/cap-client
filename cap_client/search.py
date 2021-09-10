"""
handling api requests for search
"""

from .api import Api


class Search(Api):
    """interface for /search/ API endpoints"""

    def build(self):
        """send a request to create a new search index"""
        return self.post("/search/build", dict())

    def summary(self):
        """send a request to create a new search index"""
        return self.get("/search/summary/")
