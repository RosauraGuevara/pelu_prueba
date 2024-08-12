from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime
from flask_migrate import Migrate

load_dotenv()  # Carga las variables de entorno desde el archivo .env

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Asigna la clave secreta

# Configuración de la base de datos Supabase
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Inicializar Migrate después de la base de datos

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

class HorarioAtencion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.String(10), nullable=False)  # lunes, martes, etc.
    hora_apertura = db.Column(db.String(5), nullable=False)  # Ej. "09:00"
    hora_cierre = db.Column(db.String(5), nullable=False)  # Ej. "22:00"

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    duracion = db.Column(db.Integer, nullable=False)  # Duración en minutos


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
    fechas_ocupadas = {}
    max_citas_por_dia = 8  # Puedes ajustar este valor según tu capacidad diaria

    for cita in citas:
        fecha = cita.fecha
        if fecha not in fechas_ocupadas:
            fechas_ocupadas[fecha] = 0
        fechas_ocupadas[fecha] += 1

    citas_json = []
    for fecha, conteo in fechas_ocupadas.items():
        if conteo >= max_citas_por_dia:
            citas_json.append({
                "title": "No disponible",
                "start": f"{fecha}",
                "display": "background",
                "color": "red"
            })
        else:
            citas_json.append({
                "title": "Disponible",
                "start": f"{fecha}",
                "display": "background",
                "color": "green"
            })

    return jsonify(citas_json)

@app.route('/admin/horarios', methods=['GET', 'POST'])
def admin_horarios():
    if request.method == 'POST':
        # Código para agregar o modificar horarios
        # Aquí agregarías la lógica para manejar la creación o modificación
        pass
    horarios = HorarioAtencion.query.all()
    return render_template('admin_horarios.html', horarios=horarios)

@app.route('/admin/servicios', methods=['GET', 'POST'])
def admin_servicios():
    if request.method == 'POST':
        # Código para agregar o eliminar servicios
        # Aquí agregarías la lógica para manejar la creación o eliminación
        pass
    servicios = Servicio.query.all()
    return render_template('admin_servicios.html', servicios=servicios)


if __name__ == '__main__':
    app.run(debug=True)
