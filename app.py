
from flask import Flask, jsonify, request
from config import Config
from models import db, Busqueda
from openlibrary_service import buscar, consultar_isbn, OpenLibraryError

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.errorhandler(OpenLibraryError)
def error_externo(error):
    return jsonify({"error": str(error)}), 502


@app.get("/salud")
def salud():
    return jsonify({"estado": "activo"}), 200


def registrar(criterio, termino):
    db.session.add(Busqueda(criterio=criterio, termino=termino))
    db.session.commit()


@app.get("/libros/buscar")
def buscar_titulo():
    titulo = (request.args.get("titulo") or "").strip()

    if len(titulo) < 2:
        return jsonify({"error": "titulo debe tener al menos 2 caracteres"}), 400

    resultados = buscar("title", titulo)
    registrar("titulo", titulo)

    return jsonify({
        "consulta": titulo,
        "total": len(resultados),
        "resultados": resultados
    }), 200


@app.get("/libros/autor")
def buscar_autor():
    nombre = (request.args.get("nombre") or "").strip()

    if len(nombre) < 2:
        return jsonify({"error": "nombre debe tener al menos 2 caracteres"}), 400

    resultados = buscar("author", nombre)
    registrar("autor", nombre)

    return jsonify({
        "consulta": nombre,
        "total": len(resultados),
        "resultados": resultados
    }), 200


@app.get("/libros/isbn/<isbn>")
def libro_por_isbn(isbn):
    if not (isbn.isdigit() and len(isbn) in (10, 13)):
        return jsonify({"error": "ISBN debe contener 10 o 13 dígitos"}), 400

    try:
        libro = consultar_isbn(isbn)
    except OpenLibraryError:
        return jsonify({"error": "No fue posible obtener el ISBN"}), 502

    registrar("isbn", isbn)

    return jsonify({
        "isbn": isbn,
        "titulo": libro.get("title"),
        "fecha_publicacion": libro.get("publish_date"),
        "editoriales": libro.get("publishers", [])
    }), 200


@app.get("/historial")
def historial():
    registros = Busqueda.query.order_by(
        Busqueda.id.desc()
    ).limit(50).all()

    return jsonify([
        {
            "id": r.id,
            "criterio": r.criterio,
            "termino": r.termino,
            "fecha": r.fecha.isoformat()
        }
        for r in registros
    ]), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )
