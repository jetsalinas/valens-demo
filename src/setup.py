from database.database import Database
from constants import DB_URL

db = Database(DB_URL)
con = db.controller

con.create_table()