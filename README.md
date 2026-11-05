# API REST - Biblioteca Digital

## Descripción
Proyecto desarrollado con Python y Flask que permite buscar libros mediante la API de Open Library, consultar el historial y administrar una biblioteca local utilizando SQLite.

## Tecnologías utilizadas
- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Requests
- Python-dotenv
- Postman

## Instalación

1. Crear el entorno virtual:

```bash
python -m venv venv
```

2. Activar el entorno virtual:

```powershell
.\venv\Scripts\Activate.ps1
```

3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

4. Configurar el archivo `.env`:

```env
DATABASE_URL=sqlite:///biblioteca.db
OPENLIBRARY_CONTACT=tu_correo@ejemplo.com
```

5. Ejecutar la aplicación:

```bash
py app.py
```

Servidor local:

`http://127.0.0.1:5000`

## Endpoints

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/salud` | Verificar la API |
| GET | `/libros/buscar?titulo=python` | Buscar por título |
| GET | `/libros/autor?nombre=martin` | Buscar por autor |
| GET | `/libros/isbn/9780132350884` | Buscar por ISBN |
| GET | `/historial` | Consultar búsquedas |
| POST | `/biblioteca` | Guardar un libro |
| GET | `/biblioteca` | Listar libros guardados |
| DELETE | `/biblioteca/1` | Eliminar un libro |

## Cambios realizados

- Se modificó el límite de búsqueda de 10 a 5 libros.
- Se realizaron pruebas con búsquedas sin resultados y títulos vacíos.
- Se implementaron validaciones de datos.
- Se agregó el almacenamiento de libros en SQLite.
- Se documentó el uso de los códigos HTTP.

## Códigos HTTP

- **200:** Solicitud exitosa.
- **201:** Libro creado correctamente.
- **400:** Datos incorrectos.
- **404:** Libro no encontrado.
- **409:** ISBN duplicado.
- **502:** Error de comunicación con Open Library.

## Flujo de funcionamiento

```text
Postman → Flask → Open Library
                    ↓
Postman ← Flask ← SQLite
```

Flask recibe las solicitudes, valida los datos, consulta Open Library y registra las búsquedas en SQLite.

## Pruebas

Las pruebas se realizaron utilizando Postman, verificando las búsquedas por título, autor e ISBN, el historial y las operaciones de guardar, consultar y eliminar libros.

## Autor

Juan Garcia - ADSO 3409610.
