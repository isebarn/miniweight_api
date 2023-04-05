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
daily_meal_base = api.model("daily_meal_base", models.DailyMeal.base())
daily_meal_reference = api.model("daily_meal_reference", models.DailyMeal.reference())
daily_meal_full = api.model("daily_meal", models.DailyMeal.model(api))
form_base = api.model("form_base", models.Form.base())
form_reference = api.model("form_reference", models.Form.reference())
form_full = api.model("form", models.Form.model(api))

""" // embed
table daily_meal {
    breakfast varchar
    snack1 varchar
    lunch varchar
    snack2 varchar
    dinner varchar
}

table form {
    gender varchar
    age integer
    height integer
    weight integer
    target_weight integer
    meals [ref: << daily_meal.id]
} """

form = api.model(
    "form",
    {
        
        "gender": String,
        "age": Integer,
        "height": Integer,
        "weight": Integer,
        "target_weight": Integer,
        "meals": List(Nested(daily_meal_reference)),
    },
)


@api.route("/form")
class FormController(Resource):
    @api.marshal_list_with(api.models.get("form"), skip_none=True)
    def get(self):
        return models.Form.qry(request.args)

    @api.marshal_with(form, skip_none=True)
    def post(self):
        return models.Form.post(request.get_json())

    @api.marshal_with(api.models.get("form"), skip_none=True)
    def put(self):
        return models.Form.put(request.get_json())

    @api.marshal_with(api.models.get("form"), skip_none=True)
    def patch(self):
        return models.Form.patch(request.get_json())


@api.route("/form/<form_id>")
class BaseFormController(Resource):
    @api.marshal_with(api.models.get("form"), skip_none=True)
    def get(self, form_id):
        return models.Form.objects.get(id=form_id).to_json()

    @api.marshal_with(api.models.get("form"), skip_none=True)
    def put(self, form_id):
        return models.Form.put({"id": form_id, **request.get_json()})

    @api.marshal_with(api.models.get("form"), skip_none=True)
    def patch(self, form_id):
        return models.Form.patch({"id": form_id, **request.get_json()})

    def delete(self, form_id):
        return models.Form.get(id=form_id).delete()


routes = list(set([x.urls[0].split("/")[1] for x in api.resources]))
