import json
import random
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
CORS(app)

PRECIO_NUMERO = 1

# -----------------------------
# ARCHIVOS
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
# NUMEROS
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

    pagados = [
    n for n,d in numeros.items()
    if isinstance(d, dict) and d.get("pagado")
]

    if not pagados:
        return jsonify({"error":"no pagados"})

    numero = random.choice(pagados)
    nombre = numeros[numero]["nombre"]

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

    pagados = [n for n,d in numeros.items() if d["pagado"]]

    if not pagados:
        return

    numero = random.choice(pagados)
    nombre = numeros[numero]["nombre"]

    print("🏆 GANADOR AUTOMATICO:", numero, nombre)

    guardar_ganador(numero, nombre)

    del numeros[numero]
    guardar_numeros()

# -----------------------------
# LIMPIAR NUMEROS NO PAGADOS
# -----------------------------

def limpiar_pendientes():

    global numeros

    ahora = datetime.now()
    eliminar = []

    for numero, data in numeros.items():

        if not data["pagado"]:

            hora = datetime.strptime(data["hora"], "%Y-%m-%d %H:%M:%S")

            if (ahora - hora).seconds > 600:
                eliminar.append(numero)

    for n in eliminar:
        del numeros[n]

    guardar_numeros()

# -----------------------------
# SCHEDULER
# -----------------------------

scheduler = BackgroundScheduler()

scheduler.add_job(
    sorteo_automatico,
    "cron",
    hour="13,15,18",
    minute=0
)

scheduler.add_job(
    limpiar_pendientes,
    "interval",
    minutes=1
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

        numeros[numero] = {
            "nombre": nombre,
            "pagado": False,
            "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        guardar_numeros()

    return redirect("/")

# -----------------------------
# CONFIRMAR PAGO
# -----------------------------

@app.route("/confirmar/<numero>", methods=["POST"])
def confirmar(numero):

    if numero in numeros:

        numeros[numero]["pagado"] = True
        guardar_numeros()

        return {"ok": True}

    return {"error": "numero no existe"}

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

            pagados = [n for n,d in numeros.items() if d["pagado"]]

            if pagados:

                numero = random.choice(pagados)
                nombre = numeros[numero]["nombre"]

                ganador = (numero, nombre)

                guardar_ganador(numero, nombre)

                del numeros[numero]
                guardar_numeros()

        if accion == "liberar":

            numero = request.form.get("numero")

            if numero in numeros:

                del numeros[numero]
                guardar_numeros()

        pagados = sum(
    1 for n in numeros
    if isinstance(numeros[n], dict) and numeros[n].get("pagado")
)
    total = pagados * PRECIO_NUMERO

    return render_template(
        "admin.html",
        numeros=numeros,
        ganador=ganador,
        pagados=pagados,
        total=total
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