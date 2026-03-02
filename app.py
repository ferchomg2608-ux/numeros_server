import json
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

ADMIN_PASSWORD = "1234"  # Cambia esto a la contraseña que quieras

def cargar_numeros():
    try:
        with open("numeros.json", "r") as f:
            return json.load(f)
    except:
        return {}

numeros = cargar_numeros()

def guardar_numeros():
    with open("numeros.json", "w") as f:
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

# NUEVO: Reiniciar juego con contraseña
@app.route("/reset", methods=["POST"])
def reset():
    password = request.form.get("password", "")
    if password == ADMIN_PASSWORD:
        numeros.clear()
        guardar_numeros()
    return redirect("/")