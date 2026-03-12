import json
import random
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
CORS(app)

# -----------------------------
# ARCHIVOS (COMPATIBLE CON RENDER)
# -----------------------------

DATA_FILE = "/tmp/numeros.json"
GANADORES_FILE = "/tmp/ganadores.json"

ADMIN_PASSWORD = "1235"


# -----------------------------
# CREAR ARCHIVOS SI NO EXISTEN
# -----------------------------

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(GANADORES_FILE):
    with open(GANADORES_FILE, "w") as f:
        json.dump([], f)


# -----------------------------
# CARGAR NUMEROS
# -----------------------------

def cargar_numeros():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


numeros = cargar_numeros()


def guardar_numeros():
    with open(DATA_FILE, "w") as f:
        json.dump(numeros, f, indent=4)


# -----------------------------
# GANADORES
# -----------------------------

def guardar_ganador(numero, nombre):

    data = []

    if os.path.exists(GANADORES_FILE):
        with open(GANADORES_FILE, "r") as f:
            data = json.load(f)

    data.append({
        "numero": numero,
        "nombre": nombre,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    with open(GANADORES_FILE, "w") as f:
        json.dump(data, f, indent=4)


def cargar_ganadores():

    if os.path.exists(GANADORES_FILE):

        with open(GANADORES_FILE, "r") as f:
            return json.load(f)

    return []

# -----------------------------
# API GIRAR RULETA
# -----------------------------

@app.route("/api/girar")
def api_girar():

    global numeros

    if not numeros:
        return jsonify({"error": "no jugadores"})

    numero = random.choice(list(numeros.keys()))
    nombre = numeros[numero]

    guardar_ganador(numero, nombre)

    del numeros[numero]
    guardar_numeros()

    return jsonify({
        "numero": numero,
        "nombre": nombre
    })


# -----------------------------
# SORTEO AUTOMATICO
# -----------------------------

def sorteo_automatico():

    global numeros

    if not numeros:
        return

    numero = random.choice(list(numeros.keys()))
    nombre = numeros[numero]

    print("🏆 GANADOR AUTOMATICO:", numero, nombre)

    guardar_ganador(numero, nombre)

    del numeros[numero]
    guardar_numeros()


# -----------------------------
# SCHEDULER
# -----------------------------

scheduler = BackgroundScheduler()

scheduler.add_job(
    sorteo_automatico,
    "cron",
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

                del numeros[numero]
                guardar_numeros()

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
# HISTORIAL GANADORES
# -----------------------------

@app.route("/ganadores")
def ganadores():

    data = cargar_ganadores()

    return render_template(
        "ganadores.html",
        ganadores=reversed(data)
    )


# -----------------------------
# API ULTIMO GANADOR
# -----------------------------

@app.route("/ultimo-ganador")
def ultimo_ganador():

    data = cargar_ganadores()

    if data:
        return jsonify(data[-1])

    return jsonify({})


# -----------------------------
# PANTALLA SORTEO
# -----------------------------

@app.route("/sorteo")
def sorteo():

    return render_template("sorteo.html")


# -----------------------------
# PANTALLA GIGANTE
# -----------------------------

@app.route("/pantalla")
def pantalla():

    return render_template("pantalla.html")


# -----------------------------
# START SERVER
# -----------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )