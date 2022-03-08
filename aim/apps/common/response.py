"""
Definition of response common.
"""


class Response:
    data = None
    mess = None
    status = None

    def __init__(self, **kwargs):
        self.data = kwargs.get("data")
        self.mess = kwargs.get("mess")
        self.status = kwargs.get("status")
