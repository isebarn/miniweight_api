from json import loads
from mongoengine import signals
from models import Form, DailyMeal
from requests import post
from flask import abort
from pandas import read_csv
from io import StringIO


def create_prompt(sender, document):
    prompt = "Make me a meal plan based on the following. Height: {} , Weight: {}, Age: {}, Target Weight: {} ".format(document.height, document.weight, document.age, document.target_weight)
    prompt += "Make a weekly meal plan where each day has breakfast, snack, lunch, afternoon_snack and dinner. Return as a csv with a | separator instead of a comma."
    prompt += "Example row looks like this: Monday|eggs with tomato|apple|chicken salad|banana|steak and potatoes"
    
    response = post("http://127.0.0.1:5000/openai/prompt", json={"prompt": prompt})
    csv = response.json()
    #csv = 'Monday|Oatmeal with banana and walnuts|Yogurt with granola|Turkey sandwich with lettuce and tomato|Carrot sticks and hummus|Grilled salmon with roasted vegetables|\n\nTuesday|Scrambled eggs with spinach and feta cheese|Berries and almonds|Salad with grilled chicken|Apple slices with peanut butter|Stir fry with tofu and vegetables|\n\nWednesday|Whole wheat toast with peanut butter and banana|String cheese and crackers|Veggie wrap with hummus|Celery sticks with cottage cheese|Grilled steak with roasted potatoes and broccoli|\n\nThursday|Smoothie with yogurt, banana, and berries|Trail mix with dried fruit and nuts|Grilled turkey burger on a whole wheat bun|Cucumber slices with Greek yogurt dip|Vegetable stir fry over brown rice|\n\nFriday|Oatmeal pancakes with fresh fruit|Yogurt parfait with granola and berries|Turkey wrap with lettuce, tomato, and avocado|Apple slices with almond butter|Baked salmon with quinoa and roasted vegetables|\n\nSaturday|Eggs Benedict on whole wheat toast|Cheese cubes and crackers|Greek salad with grilled chicken breast|Carrot sticks and hummus dip|Grilled shrimp with brown rice and steamed vegetables |\n\nSunday|Blueberry muffins and Greek yogurt |Trail mix with dried fruit and nuts |Veggie wrap with hummus |Celery sticks with cottage cheese |Chicken stir fry over brown rice'

    samba = read_csv(StringIO(csv), sep="|", header=None)

    # make the first column into the index
    samba.set_index(0, inplace=True)

    # drop last column
    if len(samba.columns) == 6:
        samba.drop(samba.columns[-1], axis=1, inplace=True)

    # rename columns to day, breakfast, snack1, lunch, snack2, dinner
    samba.columns = ["breakfast", "snack1", "lunch", "snack2", "dinner"]

    # convert to dictionary
    samba_dict = samba.to_dict(orient="index")
    
    meals = [DailyMeal(**x) for x in samba_dict.values()]

    document.meals = meals

signals.pre_save.connect(create_prompt, sender=Form)