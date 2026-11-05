from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class Busqueda(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 criterio = db.Column(db.String(20), nullable=False)
 termino = db.Column(db.String(200), nullable=False)
 fecha = db.Column(db.DateTime, nullable=False,
  default=lambda: datetime.now(timezone.utc))