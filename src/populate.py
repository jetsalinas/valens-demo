import csv

from database.database import Database
from database.cars import Car
from constants import DB_URL

db = Database(DB_URL)
con = db.controller

with open("./src/static/data.csv") as file:
    reader = csv.DictReader(file)
    for row in reader:
        car = Car(name=row["name"], color=row["color"])
        con.add_car(car)