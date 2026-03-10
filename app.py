<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Safari de Números</title>

<style>

html{
scroll-behavior:smooth;
}

section{
scroll-margin-top:90px;
}

/* BODY */

body{
font-family: Arial, sans-serif;
padding:20px;
min-height:100vh;
background-image:url("{{ url_for('static', filename='selva.png') }}");
background-size:cover;
background-position:center;
}

/* HEADER */

.header{
background:rgba(0,80,0,0.9);
padding:12px 25px;
border-radius:12px;
display:flex;
justify-content:space-between;
align-items:center;
margin-bottom:20px;

position:sticky;
top:0;
z-index:1000;
}

.logo{
font-size:22px;
font-weight:bold;
color:white;
}

.menu a{
color:white;
text-decoration:none;
margin-left:18px;
font-weight:bold;
}

.menu a:hover{
text-decoration:underline;
}

/* GRID */

#numeros-container{
display:grid;
grid-template-columns:repeat(10,1fr);
gap:12px;
}

/* TARJETAS */

.tarjeta{
padding:12px;
border-radius:16px;
border:2px solid #2f5d2f;
background:rgba(255,255,255,0.9);
display:flex;
flex-direction:column;
align-items:center;
justify-content:center;
font-size:18px;
font-weight:bold;
box-shadow:0 4px 10px rgba(0,0,0,0.3);
transition:all .25s;
}

.tarjeta:hover{
transform:scale(1.07);
background:#e8ffe8;
}

.tomado{
background:rgba(180,180,180,.8);
border-color:#555;
}

.tarjeta button{
border:none;
background:none;
font-size:18px;
cursor:pointer;
}

.jugador{
font-size:13px;
margin-top:4px;
}

</style>
</head>

<body>

<!-- HEADER -->

<div class="header">

<div class="logo">🦜 Safari de Números</div>

<div class="menu">
<a href="#resultados">Resultados</a>
<a href="#premios">Premios</a>
<a href="#reglas">Reglas</a>
<a href="#contacto">Contacto</a>
</div>

</div>

<h2>🌿 Safari de Números 🐅</h2>

<h3>
🎯 Números disponibles: {{ 100 - numeros|length }}
</h3>

<div id="numeros-container">

{% for numero in range(1,101) %}
{% set n = numero|string %}

{% if n in numeros %}

<div class="tarjeta tomado">
<div>{{numero}}</div>
<div class="jugador">{{numeros[n]}}</div>
</div>

{% else %}

<form method="POST" action="/pick">
<input type="hidden" name="numero" value="{{numero}}">
<input type="hidden" name="nombre" value="">
<div class="tarjeta">
<button type="submit">{{numero}}</button>
</div>
</form>

{% endif %}
{% endfor %}

</div>

<!-- RESULTADOS -->

<section id="resultados">

<h2>🏆 Resultados</h2>

<p>Aquí aparecerán los ganadores del Safari.</p>

</section>

<!-- PREMIOS -->

<section id="premios">

<h2>🎁 Premios</h2>

<p>🥇 Primer premio</p>
<p>🥈 Segundo premio</p>
<p>🥉 Tercer premio</p>

</section>

<!-- REGLAS -->

<section id="reglas">

<h2>📜 Reglas</h2>

<p>1. Cada número solo puede ser elegido una vez.</p>
<p>2. El ganador se elige con la ruleta.</p>
<p>3. El administrador controla el sorteo.</p>

</section>

<!-- CONTACTO -->

<section id="contacto">

<h2>📞 Contacto</h2>

<p>Email: contacto@safari.com</p>

</section>

</body>
</html>