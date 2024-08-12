from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

class horarioatencion(db.Model):
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
    max_citas_por_dia = 8

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
        horarios = horarioatencion.query.all()
        dia = request.form['dia']
        hora_apertura = request.form['hora_apertura']
        hora_cierre = request.form['hora_cierre']

        horario = horarioatencion.query.filter_by(dia=dia).first()
        if horario:
            horario.hora_apertura = hora_apertura
            horario.hora_cierre = hora_cierre
        else:
            horario = horarioatencion(dia=dia, hora_apertura=hora_apertura, hora_cierre=hora_cierre)
            db.session.add(horario)

        db.session.commit()
        flash(f'Horario de {dia} actualizado.', 'success')
        return redirect(url_for('admin_horarios'))

    horarios = horarioatencion.query.all()
    return render_template('admin_horarios.html', horarios=horarios)

@app.route('/admin/servicios', methods=['GET', 'POST'])
def admin_servicios():
    if request.method == 'POST':
        nombre_servicio = request.form['nombre_servicio']
        duracion_servicio = int(request.form['duracion_servicio'])

        servicio_existente = Servicio.query.filter_by(nombre=nombre_servicio).first()
        if servicio_existente:
            flash(f'El servicio "{nombre_servicio}" ya existe.', 'error')
        else:
            nuevo_servicio = Servicio(nombre=nombre_servicio, duracion=duracion_servicio)
            db.session.add(nuevo_servicio)
            db.session.commit()
            flash(f'Servicio "{nombre_servicio}" agregado.', 'success')
        return redirect(url_for('admin_servicios'))

    servicios = Servicio.query.all()
    return render_template('admin_servicios.html', servicios=servicios)

@app.route('/admin/servicios/delete/<int:id>', methods=['POST'])
def eliminar_servicio(id):
    servicio = Servicio.query.get(id)
    if servicio:
        db.session.delete(servicio)
        db.session.commit()
        flash('Servicio eliminado con éxito.', 'success')
    else:
        flash('Servicio no encontrado.', 'error')
    return redirect(url_for('admin_servicios'))

@app.route('/admin/cancelar_cita/<int:id>', methods=['POST'])
def cancelar_cita(id):
    cita = Cita.query.get(id)
    if cita:
        db.session.delete(cita)
        db.session.commit()
        flash('Cita cancelada con éxito.', 'success')
    else:
        flash('Cita no encontrada.', 'error')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)
