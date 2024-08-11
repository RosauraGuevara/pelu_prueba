from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()  # Carga las variables de entorno desde el archivo .env

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Asigna la clave secreta

# Configuración de la base de datos Supabase
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    telefono = db.Column(db.String(15), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)  
    cumpleanos = db.Column(db.String(10), nullable=False)
    lugar = db.Column(db.String(20), nullable=False)
    pago = db.Column(db.String(20), nullable=False)

class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    servicio = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(10), nullable=False)
    hora = db.Column(db.String(5), nullable=False)
    lugar = db.Column(db.String(20), nullable=False)

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
    direccion = request.form['direccion']  
    cumpleanos = request.form['cumpleanos']
    lugar = request.form['lugar']
    pago = request.form['pago']

    try:
        cliente = Cliente.query.filter_by(email=email).first()
        if not cliente:
            cliente = Cliente(
                nombre=nombre,
                email=email,
                telefono=telefono,
                direccion=direccion,
                cumpleanos=cumpleanos,
                lugar=lugar,
                pago=pago
            )
            db.session.add(cliente)
            db.session.commit()
        
        cita = Cita(cliente_id=cliente.id, servicio=servicio, fecha=fecha, hora=hora, lugar=lugar)
        db.session.add(cita)
        db.session.commit()

        fecha_formateada = "-".join(reversed(fecha.split("-")))
        
        flash(f'Tu cita ha sido agendada correctamente para el {fecha_formateada} a las {hora}.', 'success')
    
    except Exception as e:
        flash(f'Hubo un error al agendar tu cita: {str(e)}', 'error')

    return redirect(url_for('confirmacion'))
    
@app.route('/confirmacion')
def confirmacion():
    return render_template('confirmacion.html')

@app.route('/admin')
def admin():
    citas = Cita.query.all()
    return render_template('admin.html', citas=citas)

@app.route('/citas', methods=['GET'])
def obtener_citas():
    citas = Cita.query.all()
    citas_json = [
        {
            "title": cita.servicio,
            "start": f"{cita.fecha}T{cita.hora}"
        }
        for cita in citas
    ]
    return jsonify(citas_json)

if __name__ == '__main__':
    app.run(debug=True)
