import json
import random
import os
from flask import Flask, render_template, request, redirect, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "numeros.json")
GANADORES_FILE = os.path.join(BASE_DIR, "ganadores.json")

ADMIN_PASSWORD = "1235"


# -----------------------------
# CARGAR NUMEROS
# -----------------------------

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


# -----------------------------
# GANADORES
# -----------------------------

def guardar_ganador(numero, nombre):

    try:
        with open(GANADORES_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append({
        "numero": numero,
        "nombre": nombre
    })

    with open(GANADORES_FILE, "w") as f:
        json.dump(data, f)


def cargar_ganadores():

    try:
        with open(GANADORES_FILE, "r") as f:
            return json.load(f)
    except:
        return []


# -----------------------------
# SORTEO AUTOMATICO
# -----------------------------

def sorteo_automatico():

    global numeros

    if numeros:

        numero = random.choice(list(numeros.keys()))
        ganador = numeros[numero]

        print("🏆 GANADOR AUTOMATICO:", numero, ganador)

        guardar_ganador(numero, ganador)


# -----------------------------
# SCHEDULER
# -----------------------------

scheduler = BackgroundScheduler(daemon=True)

scheduler.add_job(
    sorteo_automatico,
    'cron',
    hour=20,
    minute=0
)

scheduler.start()


# -----------------------------
# PAGINA PRINCIPAL
# -----------------------------

@app.route("/")
def index():

    return render_template(
        "index.html",
        numeros=numeros
    )


# -----------------------------
# ELEGIR NUMERO
# -----------------------------

@app.route("/pick", methods=["POST"])
def pick():

    numero = request.form["numero"]
    nombre = request.form.get("nombre", "Jugador")

    if numero not in numeros:

        numeros[numero] = nombre
        guardar_numeros()

    return redirect("/")


# -----------------------------
# RESET ADMIN
# -----------------------------

@app.route("/reset", methods=["POST"])
def reset():

    password = request.form.get("password", "")

    if password == ADMIN_PASSWORD:

        numeros.clear()
        guardar_numeros()

    return redirect("/")


# -----------------------------
# ESTADO TIEMPO REAL
# -----------------------------

@app.route("/estado")
def estado():

    return jsonify(numeros)


# -----------------------------
# PANEL ADMIN
# -----------------------------

@app.route("/admin", methods=["GET", "POST"])
def admin():

    password = request.args.get("password", "")

    if password != ADMIN_PASSWORD:
        return "Acceso denegado"

    ganador = None

    if request.method == "POST":

        accion = request.form.get("accion")

        if accion == "ganador":

            if numeros:

                numero = random.choice(list(numeros.keys()))
                nombre = numeros[numero]

                ganador = (numero, nombre)

                guardar_ganador(numero, nombre)

        if accion == "liberar":

            numero = request.form.get("numero")

            if numero in numeros:

                del numeros[numero]
                guardar_numeros()

    return render_template(
        "admin.html",
        numeros=numeros,
        ganador=ganador
    )


# -----------------------------
# HISTORIAL
# -----------------------------

@app.route("/ganadores")
def ganadores():

    data = cargar_ganadores()

    return render_template(
        "ganadores.html",
        ganadores=data
    )


# -----------------------------
# PANTALLA SORTEO
# -----------------------------

@app.route("/sorteo")
def sorteo():

    return render_template("sorteo.html")


# -----------------------------
# START SERVER
# -----------------------------

if __name__ == "__main__":
    app.run()