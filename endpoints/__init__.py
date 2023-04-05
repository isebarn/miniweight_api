# Standard library imports
import os
from datetime import datetime
from requests import post
from requests import get

# Third party imports
from flask import Flask
from flask import request
from flask import g
from flask_restx import Namespace
from flask_restx import Resource as _Resource
from flask_restx.fields import DateTime
from flask_restx.fields import Float
from flask_restx.fields import Integer
from flask_restx.fields import List
from flask_restx.fields import Nested
from flask_restx.fields import String
from flask_restx.fields import Boolean
from flask_restx.fields import Raw

# Local application imports
import models


class Resource(_Resource):
    dispatch_requests = []

    def __init__(self, api=None, *args, **kwargs):
        super(Resource, self).__init__(api, args, kwargs)

    def dispatch_request(self, *args, **kwargs):

        tmp = request.args.to_dict()

        if request.method == "GET":
            request.args = tmp

            [
                tmp.update({k: v.split(",")})
                for k, v in tmp.items()
                if k.endswith("__in")
            ]

            [
                tmp.update({k: v.split(",")})
                for k, v in tmp.items()
                if k.startswith("$sort")
            ]            

        if (
            request.method == "POST"
            and request.headers.get("Content-Type", "") == "application/json"
        ):
            json = request.get_json()

            for key, value in json.items():
                if isinstance(value, dict) and key in routes:
                    if "id" in value:
                        json[key] = value["id"]

                    else:
                        item = post(
                            "http://localhost:5000/api/{}".format(key), json=value
                        )
                        json[key] = item.json()["id"]

        for method in self.dispatch_requests:
            method(self, args, kwargs)

        return super(Resource, self).dispatch_request(*args, **kwargs)



api = Namespace("api", description="")
layout_base = api.model('layout_base', models.Layout.base())
layout_reference = api.model('layout_reference', models.Layout.reference())
layout_full = api.model('layout', models.Layout.model(api))


@api.route("/layout")
class LayoutController(Resource):
    def get(self):
        return models.Layout.qry(request.args)

    def post(self):
        return models.Layout.post(request.get_json())

    def put(self):
        return models.Layout.put(request.get_json())

    def patch(self):
        return models.Layout.patch(request.get_json())


@api.route("/layout/<layout_id>")
class BaseLayoutController(Resource):
    def get(self, layout_id):
        return models.Layout.objects.get(id=layout_id).to_json()

    def put(self, layout_id):
        return models.Layout.put({"id": layout_id, **request.get_json()})

    def patch(self, layout_id):
        return models.Layout.patch({"id": layout_id, **request.get_json()})

    def delete(self, layout_id):
        return models.Layout.get(id=layout_id).delete()




routes = list(set([x.urls[0].split('/')[1] for x in api.resources]))