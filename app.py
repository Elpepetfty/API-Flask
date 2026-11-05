from flask import Flask, request, jsonify

from config import Config
from models import db, Busqueda, LibroGuardado

from openlibrary_service import (
    buscar_por_titulo,
    buscar_por_autor,
    buscar_por_isbn,
    OpenLibraryError
)


app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)


# Registrar las búsquedas realizadas
def registrar_busqueda(criterio, termino):
    busqueda = Busqueda(
        criterio=criterio,
        termino=termino
    )

    db.session.add(busqueda)
    db.session.commit()


@app.route("/salud", methods=["GET"])
def salud():
    return jsonify({
        "mensaje": "API de biblioteca funcionando correctamente"
    }), 200


# Buscar libros por título
@app.route("/libros/buscar", methods=["GET"])
def buscar_titulo():
    titulo = request.args.get("titulo", "").strip()

    if len(titulo) < 2:
        return jsonify({
            "error": "El título debe tener al menos 2 caracteres"
        }), 400

    try:
        resultados = buscar_por_titulo(titulo)

        registrar_busqueda("titulo", titulo)

        return jsonify({
            "titulo_buscado": titulo,
            "resultados": resultados
        }), 200

    except OpenLibraryError as error:
        return jsonify({
            "error": str(error)
        }), 502

@app.route("/libros/autor", methods=["GET"])
def buscar_autor():
    nombre = request.args.get("nombre", "").strip()

    if len(nombre) < 2:
        return jsonify({
            "error": "El nombre del autor debe tener al menos 2 caracteres"
        }), 400

    try:
        resultados = buscar_por_autor(nombre)

        registrar_busqueda("autor", nombre)

        return jsonify({
            "autor_buscado": nombre,
            "resultados": resultados
        }), 200

    except OpenLibraryError as error:
        return jsonify({
            "error": str(error)
        }), 502


# Consultar un libro por ISBN
@app.route("/libros/isbn/<isbn>", methods=["GET"])
def consultar_isbn(isbn):
    if not isbn.isdigit() or len(isbn) not in (10, 13):
        return jsonify({
            "error": "El ISBN debe contener 10 o 13 dígitos"
        }), 400

    try:
        resultado = buscar_por_isbn(isbn)

        registrar_busqueda("isbn", isbn)

        return jsonify(resultado), 200

    except OpenLibraryError as error:
        return jsonify({
            "error": str(error)
        }), 502


# Consultar historial de búsquedas
@app.route("/historial", methods=["GET"])
def consultar_historial():
    historial = Busqueda.query.order_by(
        Busqueda.fecha.desc()
    ).all()

    resultados = []

    for busqueda in historial:
        resultados.append({
            "id": busqueda.id,
            "criterio": busqueda.criterio,
            "termino": busqueda.termino,
            "fecha": busqueda.fecha.isoformat()
        })

    return jsonify(resultados), 200


# Guardar un libro en la biblioteca local
@app.route("/biblioteca", methods=["POST"])
def guardar_libro():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Debe enviar un objeto JSON válido"
        }), 400

    titulo = datos.get("titulo")
    autor = datos.get("autor")
    isbn = datos.get("isbn")
    anio = datos.get("anio")

    if not isinstance(titulo, str) or not titulo.strip():
        return jsonify({
            "error": "El título es obligatorio"
        }), 400

    if not isinstance(autor, str) or not autor.strip():
        return jsonify({
            "error": "El autor es obligatorio"
        }), 400

    if not isinstance(isbn, str):
        return jsonify({
            "error": "El ISBN debe ser un texto"
        }), 400

    titulo = titulo.strip()
    autor = autor.strip()
    isbn = isbn.strip()

    if len(titulo) > 250 or len(autor) > 200:
        return jsonify({
            "error": "El título o autor supera la longitud permitida"
        }), 400

    if not isbn.isdigit() or len(isbn) not in (10, 13):
        return jsonify({
            "error": "El ISBN debe contener 10 o 13 dígitos"
        }), 400

    if anio is not None:
        if type(anio) is not int or anio <= 0 or anio > 2100:
            return jsonify({
                "error": "El año debe ser un número válido"
            }), 400

    libro_existente = LibroGuardado.query.filter_by(
        isbn=isbn
    ).first()

    if libro_existente:
        return jsonify({
            "error": "Ya existe un libro con ese ISBN"
        }), 409

    nuevo_libro = LibroGuardado(
        titulo=titulo,
        autor=autor,
        isbn=isbn,
        anio=anio
    )

    db.session.add(nuevo_libro)
    db.session.commit()

    return jsonify({
        "mensaje": "Libro guardado correctamente",
        "id": nuevo_libro.id
    }), 201


@app.route("/biblioteca", methods=["GET"])
def listar_biblioteca():
    libros = LibroGuardado.query.order_by(
        LibroGuardado.id.desc()
    ).all()

    resultados = []

    for libro in libros:
        resultados.append({
            "id": libro.id,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "isbn": libro.isbn,
            "anio": libro.anio
        })

    return jsonify(resultados), 200


@app.route("/biblioteca/<int:id>", methods=["DELETE"])
def eliminar_libro(id):
    libro = db.session.get(LibroGuardado, id)

    if libro is None:
        return jsonify({
            "error": "El libro no existe en la biblioteca"
        }), 404

    db.session.delete(libro)
    db.session.commit()

    return jsonify({
        "mensaje": "Libro eliminado correctamente"
    }), 200

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )