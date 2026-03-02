import json
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Cargar números guardados al iniciar
try:
    with open("numeros.json", "r") as f:
        numeros = json.load(f)
except:
    numeros = {}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", numeros=numeros)

@app.route("/pick", methods=["POST"])
def pick():
    numero = int(request.form["numero"])
    nombre = request.form.get("nombre", "Jugador")
    
    if str(numero) not in numeros:
        numeros[str(numero)] = nombre
        with open("numeros.json", "w") as f:
            json.dump(numeros, f)
    
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)