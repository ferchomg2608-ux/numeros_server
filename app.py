import json
import random
import os
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "numeros.json")

ADMIN_PASSWORD = "1235"  # Cambia la contraseña si quieres


def cargar_numeros():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


numeros = cargar_numeros()


def guardar_numeros():
    with open(DATA_FILE, "w") as f:
        json.dump(numeros, f)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", numeros=numeros)


@app.route("/pick", methods=["POST"])
def pick():

    numero = int(request.form["numero"])
    nombre = request.form.get("nombre", "Jugador")

    if str(numero) not in numeros:
        numeros[str(numero)] = nombre
        guardar_numeros()

    return redirect("/")


@app.route("/reset", methods=["POST"])
def reset():

    password = request.form.get("password", "")

    if password == ADMIN_PASSWORD:
        numeros.clear()
        guardar_numeros()

    return redirect("/")


# PANEL ADMIN
@app.route("/admin", methods=["GET","POST"])
def admin():

    password = request.args.get("password","")

    if password != ADMIN_PASSWORD:
        return "Acceso denegado"

    ganador = None

    if request.method == "POST":

        if request.form.get("accion") == "ganador":
            if numeros:
                numero = random.choice(list(numeros.keys()))
                ganador = (numero, numeros[numero])

        if request.form.get("accion") == "liberar":
            numero = request.form.get("numero")
            if numero in numeros:
                del numeros[numero]
                guardar_numeros()

    return render_template("admin.html", numeros=numeros, ganador=ganador)


if __name__ == "__main__":
    app.run(debug=True)

from flask import jsonify

@app.route("/estado")
def estado():
    return jsonify(numeros)