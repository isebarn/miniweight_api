# flask app with two models
# form and meal
# saved in a sqlite db
#
# form has a list of meals

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.orm import declarative_base
# cors
from flask_cors import CORS


from json import loads
from requests import post
from flask import abort
from csv import reader
from io import StringIO

import openai

openai.api_key = "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"


def open_ai(
    prompt,
    max_tokens=2408,
    temperature=0.49,
    top_p=1,
    frequency_penalty=0.2,
    presence_penalty=0,
):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    return response.choices[0].text.strip()

def create_prompt(form):
    prompt = "Make me a meal plan based on the following. Height: {} , Weight: {}, Age: {}, Target Weight: {} ".format(form.height, form.weight, form.age, form.target_weight)
    prompt += "Make a weekly meal plan where each day has breakfast, snack, lunch, afternoon_snack and dinner. Return as a csv with a | separator instead of a comma."
    prompt += "Example row looks like this: Monday|eggs with tomato|apple|chicken salad|banana|steak and potatoes"
    
    response = open_ai(prompt)
    csv = response
    #csv = 'Monday|Oatmeal with banana and walnuts|Yogurt with granola|Turkey sandwich with lettuce and tomato|Carrot sticks and hummus|Grilled salmon with roasted vegetables|\n\nTuesday|Scrambled eggs with spinach and feta cheese|Berries and almonds|Salad with grilled chicken|Apple slices with peanut butter|Stir fry with tofu and vegetables|\n\nWednesday|Whole wheat toast with peanut butter and banana|String cheese and crackers|Veggie wrap with hummus|Celery sticks with cottage cheese|Grilled steak with roasted potatoes and broccoli|\n\nThursday|Smoothie with yogurt, banana, and berries|Trail mix with dried fruit and nuts|Grilled turkey burger on a whole wheat bun|Cucumber slices with Greek yogurt dip|Vegetable stir fry over brown rice|\n\nFriday|Oatmeal pancakes with fresh fruit|Yogurt parfait with granola and berries|Turkey wrap with lettuce, tomato, and avocado|Apple slices with almond butter|Baked salmon with quinoa and roasted vegetables|\n\nSaturday|Eggs Benedict on whole wheat toast|Cheese cubes and crackers|Greek salad with grilled chicken breast|Carrot sticks and hummus dip|Grilled shrimp with brown rice and steamed vegetables |\n\nSunday|Blueberry muffins and Greek yogurt |Trail mix with dried fruit and nuts |Veggie wrap with hummus |Celery sticks with cottage cheese |Chicken stir fry over brown rice'

    samba = reader(StringIO(csv), delimiter="|")

    meals = []
    for row in samba:
        if not any(row): continue
        data = {key: value for key, value in zip(["breakfast", "snack1", "lunch", "snack2", "dinner"], row)}

        meals.append(data)

    return meals



# init app
app = Flask(__name__)

# CORS
CORS(app)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init db
db = SQLAlchemy(app)
Base = declarative_base()

# form class/model
class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    age = db.Column(db.Integer)
    target_weight = db.Column(db.Integer)
    meals = db.relationship('Meal', backref='form', lazy=True)

    def __init__(self, height, weight, age, target_weight):
        self.height = height
        self.weight = weight
        self.age = age
        self.target_weight = target_weight

# meal class/model
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    breakfast = db.Column(db.String(100))
    snack1 = db.Column(db.String(100))
    lunch = db.Column(db.String(100))
    snack2 = db.Column(db.String(100))
    dinner = db.Column(db.String(100))
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=False)

    def __init__(self, breakfast, snack1, lunch, snack2, dinner, form_id):
        self.breakfast = breakfast
        self.snack1 = snack1
        self.lunch = lunch
        self.snack2 = snack2
        self.dinner = dinner
        self.form_id = form_id

# create tables
with app.app_context():
    db.create_all()

# endpoint to post a form, returns the form with meals after calling the openai api
@app.route('/form', methods=['POST'])
def add_form():
    form = Form(request.json['height'], request.json['weight'], request.json['age'], request.json['target_weight'])
    db.session.add(form)
    db.session.commit()

    meals = create_prompt(form)
    for meal in meals:
        meal = Meal(meal['breakfast'], meal['snack1'], meal['lunch'], meal['snack2'], meal['dinner'], form.id)
        db.session.add(meal)
        db.session.commit()

    result = request.json
    result['meals'] = meals

    return jsonify(result)