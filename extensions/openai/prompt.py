from datetime import datetime
from datetime import timedelta

# Third party imports
from flask import Flask
from flask import request
from flask_restx import Namespace
from flask_restx.fields import String
from flask_restx.fields import Integer
from flask_restx.fields import Raw
from flask_restx.fields import DateTime
from flask_restx.fields import Boolean
from flask_restx.fields import Nested
from flask_restx.fields import List
from flask_restx.fields import Float as Number
from flask import g

# Local imports
from endpoints import Resource
from extensions.openai.methods import open_ai


api = Namespace("openai/prompt")


@api.route("")
class PromptController(Resource):
    def post(self):
        prompt = request.json.get("prompt")
        return open_ai(prompt)
