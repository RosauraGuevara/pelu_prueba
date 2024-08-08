from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()  # Carga las variables de entorno desde el archivo .env

app = Flask(__name__)

# Configuración de la base de datos Supabase
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)

class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    servicio = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(10), nullable=False)
    hora = db.Column(db.String(5), nullable=False)

    cliente = db.relationship('Cliente', backref=db.backref('citas', lazy=True))

db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agendar', methods=['POST'])
def agendar():
    nombre = request.form['nombre']
    email = request.form['email']
    telefono = request.form['telefono']
    servicio = request.form['servicio']
    fecha = request.form['fecha']
    hora = request.form['hora']

    cliente = Cliente(nombre=nombre, email=email, telefono=telefono)
    db.session.add(cliente)
    db.session.commit()

    cita = Cita(cliente_id=cliente.id, servicio=servicio, fecha=fecha, hora=hora)
    db.session.add(cita)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
