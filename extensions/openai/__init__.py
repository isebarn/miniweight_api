# Standard library imports
from os import environ

# Third party imports
from jwt import decode
from flask import request

# Local application imports
from endpoints import Resource


def dispatch_request(self, *args, **kwargs):
    # data = decode(
    #     request.headers.get("AccessToken"),
    #     options={"verify_signature": False},
    #     algorithms=["RS256"],
    # )
    pass


Resource.dispatch_requests.append(dispatch_request)
