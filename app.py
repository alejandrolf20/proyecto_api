import requests,json
from flask import Flask, render_template, abort, redirect, request

app = Flask(__name__)
url = "https://gateway.marvel.com/v1/public/characters?apikey=91a32b0a5fa09d06e763a3a99d03f85b&ts=1715167907.7655444&hash=af1eda9eac0159513f75c81f27eae676"

@app.route('/')
def inicio():
    return render_template("index.html")

@app.route('/personajes')
def personajes():
    return render_template("personajes.html")

@app.route('/listapersonajes', methods=["GET", "POST"])
def listapersonajes():
    buscar_personaje = request.form.get('busqueda') if request.method == 'POST' else request.args.get('busqueda')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    respuesta = requests.get(url)
    personajes = respuesta.json()

    lista_personajes_a_mostrar = []
    if buscar_personaje:
        for personaje in personajes['data']['results']:
            if personaje['name'].lower().startswith(buscar_personaje.lower()):
                lista_personajes_a_mostrar.append(personaje)
    else:
        lista_personajes_a_mostrar = personajes['data']['results']

    total = len(lista_personajes_a_mostrar)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_personajes = lista_personajes_a_mostrar[start:end]

    return render_template('listapersonajes.html', personajes=paginated_personajes, page=page, total=total, per_page=per_page, busqueda=buscar_personaje)

@app.route('/personajesV2', methods=['GET', 'POST'])
def personajesV2():
    buscar_personaje = request.form.get('buscar_personaje')
    año_filtro = request.form.get('año_filtro')

    respuesta = requests.get(url)
    personajes = respuesta.json()

    lista_personajes_a_mostrar = []
    lista_años = []
    if buscar_personaje or año_filtro:
        for personaje in personajes['data']['results']:
            nombre = personaje['name'].lower()
            año = personaje['modified'][:4]
            
            if (not buscar_personaje or nombre.startswith(buscar_personaje.lower())) and (not año_filtro or año == año_filtro):
                lista_personajes_a_mostrar.append(personaje)
                
                if año not in lista_años:
                    lista_años.append(año)
    else:
        for personaje in personajes['data']['results']:
            lista_personajes_a_mostrar.append(personaje)
            año = personaje['modified'][:4]
            
            if año not in lista_años:
                lista_años.append(año)

    lista_años.sort()

    return render_template('personajes_V2.html', personajes=lista_personajes_a_mostrar, años=lista_años, buscar_personaje=buscar_personaje, año_filtro=año_filtro)

@app.route('/detalle/<personaje_id>')
def detalle(personaje_id):
    detalle_url = f"https://gateway.marvel.com:443/v1/public/characters/{personaje_id}?apikey=91a32b0a5fa09d06e763a3a99d03f85b&ts=1715167907.7655444&hash=af1eda9eac0159513f75c81f27eae676"
    respuesta = requests.get(detalle_url)
    detalle_personaje = respuesta.json()

    if detalle_personaje['data']['results']:
        personaje = detalle_personaje['data']['results'][0]

        # https://developer.marvel.com/documentation/images
        ruta_imagen = personaje['thumbnail']['path']
        extension_imagen = personaje['thumbnail']['extension']
        imagen_personaje = f"{ruta_imagen}/standard_fantastic.{extension_imagen}"

        comics = []
        for comic in personaje['comics']['items']:
            comics.append(comic['name'])

        series = []
        for serie in personaje['series']['items']:
            series.append(serie['name'])

        historias = []
        for historia in personaje['stories']['items']:
            historias.append(historia['name'])

        eventos = []
        for evento in personaje['events']['items']:
            eventos.append(evento['name'])

        return render_template('detalle.html', personaje=personaje, imagen_personaje=imagen_personaje, comics=comics, series=series, historias=historias, eventos=eventos)

@app.route('/error')
def error():
    return abort(404)

app.run("0.0.0.0", 15000, debug=True)
