from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, date, time
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
    cumpleanos = db.Column(db.Date, nullable=False)
    lugar = db.Column(db.String(20), nullable=False)
    pago = db.Column(db.String(20), nullable=False)

class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    servicio = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    lugar = db.Column(db.String(20), nullable=False)

    cliente = db.relationship('Cliente', backref=db.backref('citas', lazy=True))

class horario_atencion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.String, nullable=False)  # lunes, martes, etc.
    hora_apertura = db.Column(db.Time, nullable=False)  # Ej. "09:00"
    hora_cierre = db.Column(db.Time, nullable=False)  # Ej. "22:00"

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    duracion = db.Column(db.Integer, nullable=False)  # Duración en minutos

class Fecha_disponible(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    dia_semana = db.Column(db.String(10), nullable=False)
    disponible = db.Column(db.Boolean, default=True)


def calcular_horas_disponibles(hora_apertura, hora_cierre, intervalo):
    # hora_apertura y hora_cierre deben ser objetos datetime.time, no cadenas
    hora_apertura = datetime.combine(date.today(), hora_apertura)
    hora_cierre = datetime.combine(date.today(), hora_cierre)
    
    horas_disponibles = []
    while hora_apertura < hora_cierre:
        horas_disponibles.append(hora_apertura.time())
        hora_apertura += intervalo

    return horas_disponibles

def obtener_horarios_ocupados(citas):
    horarios_ocupados = []
    for cita in citas:
        hora_inicio = datetime.combine(date.today(), cita.hora)
        duracion_servicio = Servicio.query.filter_by(nombre=cita.servicio).first().duracion
        hora_fin = hora_inicio + timedelta(minutes=duracion_servicio)
        horarios_ocupados.append((hora_inicio, hora_fin))
    return horarios_ocupados
    
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
                cumpleanos=datetime.strptime(cumpleanos, '%Y-%m-%d').date(),
                lugar=lugar,
                pago=pago
            )
            db.session.add(cliente)
            db.session.commit()
        
        cita = Cita(
            cliente_id=cliente.id, 
            servicio=servicio, 
            fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
            hora=datetime.strptime(hora, '%H:%M').time(),
            lugar=lugar
        )
        db.session.add(cita)
        db.session.commit()
    
        flash(f'Tu cita ha sido agendada correctamente para el {fecha} a las {hora}.', 'success')
    
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
    fechas_disponibles = Fecha_disponible.query.all()
    citas = Cita.query.all()

    fechas_ocupadas = {}
    for fecha in fechas_disponibles:
        horario = horario_atencion.query.filter_by(dia_semana=fecha.dia_semana).first()
        if horario:
            # Aquí asegúrate de que horario.hora_apertura y horario.hora_cierre sean objetos datetime.time
            fecha_total_horas = calcular_horas_disponibles(horario.hora_apertura, horario.hora_cierre, timedelta(minutes=15))
            
            # Lógica para procesar las horas ocupadas y disponibles
            citas_en_fecha = [cita for cita in citas if cita.fecha == fecha.fecha]
            horas_ocupadas = obtener_horarios_ocupados(citas_en_fecha)
            horas_disponibles = [hora for hora in fecha_total_horas if hora not in horas_ocupadas]
            
            if len(horas_disponibles) == 0:
                fechas_ocupadas[fecha.fecha] = "No disponible"
            else:
                fechas_ocupadas[fecha.fecha] = "Disponible"

    citas_json = []
    for fecha, estado in fechas_ocupadas.items():
        color = "red" if estado == "No disponible" else "green"
        citas_json.append({
            "title": estado,
            "start": f"{fecha}",
            "display": "background",
            "color": color
        })

    return jsonify(citas_json)


@app.route('/admin/horarios', methods=['GET', 'POST'])
def admin_horarios():
    if request.method == 'POST':
        dia_semana = request.form['dia_semana']
        hora_apertura = datetime.strptime(request.form['hora_apertura'], '%H:%M').time()
        hora_cierre = datetime.strptime(request.form['hora_cierre'], '%H:%M').time()

        horario = horario_atencion.query.filter_by(dia_semana=dia_semana).first()
        if horario:
            horario.hora_apertura = hora_apertura
            horario.hora_cierre = hora_cierre
        else:
            nuevo_horario = horario_atencion(dia_semana=dia_semana, hora_apertura=hora_apertura, hora_cierre=hora_cierre)
            db.session.add(nuevo_horario)

        hoy = date.today()
        for i in range(90):
            fecha_futura = hoy + timedelta(days=i)
            dia_futura = fecha_futura.strftime('%A').lower()
            if dia_futura == dia_semana:
                fecha_disponible = Fecha_disponible.query.filter_by(fecha=fecha_futura).first()
                if not fecha_disponible:
                    nueva_fecha = Fecha_disponible(fecha=fecha_futura, disponible=True)
                    db.session.add(nueva_fecha)

        db.session.commit()
        flash('Horarios y fechas actualizados.', 'success')
        return redirect(url_for('admin_horarios'))

    horarios = horario_atencion.query.all()
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

@app.route('/horas_disponibles', methods=['POST'])
def obtener_horas_disponibles():
    data = request.get_json()
    fecha = data.get('fecha')
    servicio_id = data.get('servicio_id')

    servicio = Servicio.query.get(servicio_id)
    if not servicio:
        return jsonify({'error': 'Servicio no encontrado.'}), 400

    dia_semana = datetime.strptime(fecha, '%Y-%m-%d').strftime('%A').lower()
    horario = horario_atencion.query.filter_by(dia=dia_semana).first()  # Cambié 'dia_semana' a 'dia' para consistencia
    if not horario:
        return jsonify({'error': 'No hay horario de atención configurado para este día.'}), 400

    citas_en_fecha = Cita.query.filter_by(fecha=datetime.strptime(fecha, '%Y-%m-%d').date()).all()
    horarios_ocupados = obtener_horarios_ocupados(citas_en_fecha)

    horas_disponibles = calcular_horas_disponibles(horario.hora_apertura, horario.hora_cierre, timedelta(minutes=15))

    # Lógica para eliminar horarios ocupados de la lista de horas disponibles
    horas_disponibles = [hora for hora in horas_disponibles if hora not in horarios_ocupados]

    return jsonify({'horas_disponibles': [hora.strftime('%H:%M') for hora in horas_disponibles]})


@app.route('/admin/verificar_fechas', methods=['GET'])
def verificar_fechas():
    fechas = Fecha_disponible.query.all()
    fechas_json = [{'fecha': fecha.fecha, 'dia_semana': fecha.dia_semana, 'disponible': fecha.disponible} for fecha in fechas]
    return jsonify(fechas_json)

if __name__ == '__main__':
    app.run(debug=True)
