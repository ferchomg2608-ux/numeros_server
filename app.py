from flask import Flask, render_template, redirect, url_for, request
import os
import json

app = Flask(__name__)

FILE = "numeros.json"

if not os.path.exists(FILE):
    with open(FILE, "w") as f:
        json.dump({}, f)

def get_taken_numbers():
    with open(FILE, "r") as f:
        return json.load(f)

def save_number(number, name):
    numbers = get_taken_numbers()
    if str(number) not in numbers:
        numbers[str(number)] = name
        with open(FILE, "w") as f:
            json.dump(numbers, f)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        return redirect(url_for("numbers", name=name))
    return render_template("name.html")

@app.route("/numbers")
def numbers():
    name = request.args.get("name")
    taken = get_taken_numbers()
    return render_template("index.html", taken=taken, name=name)

@app.route("/pick/<int:number>")
def pick(number):
    name = request.args.get("name")
    save_number(number, name)
    return redirect(url_for("numbers", name=name))

if __name__ == "__main__":
    app.run()