from flask import Flask, jsonify, render_template, request, redirect, url_for
import sqlite3

from database.database import Database

from constants import DB_URL, DEBUG, PORT, COLORS

app = Flask(__name__)


@app.route("/")
def all():

    db = Database(DB_URL)
    con = db.controller
    res = con.get_all()
    db.close()

    return render_template("home.html", cars=res, colors=COLORS)


@app.route("/<color>")
def color(color):

    db = Database(DB_URL)
    con = db.controller
    res = con.get_color(color)
    db.close()

    return render_template("home.html", cars=res, colors=COLORS)


@app.route("/order", methods=["POST"])
def order():
    
    if request.method == "POST":

        if request.form.get("target-move") and request.form.get("to-move"):

            target_move = request.form.get("target-move")
            to_move = request.form.get("to-move")

            db = Database(DB_URL)
            con = db.controller

            car, msg = con.pop(target_move)
            car, msg = con.insert(car, to_move)

            if car is not None:
                try: 
                    db.conn.commit()
                except sqlite3.Error:
                    db.conn.rollback()

            db.close()
    
    return redirect(url_for("all"))


@app.route("/delete", methods=["POST"])
def delete():

    if request.method == "POST":

        if request.form.get("target-delete"):
            target_delete = request.form.get("target-delete")

            db = Database(DB_URL)
            con = db.controller
            car, msg = con.pop(target_delete)

            if car is not None:
                try:
                    db.conn.commit()
                except sqlite3.Error:
                    db.conn.rollback()

            db.close()

    return redirect(url_for("all"))


if __name__ == "__main__":
    app.run(debug=DEBUG, port=PORT)