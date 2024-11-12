from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Inicializar Flask y SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo Departamento
class Departamento(db.Model):
    __tablename__ = 'departamentos'
    id = db.Column(db.Integer, primary_key=True)
    numero_departamento = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    tipo_departamento = db.Column(db.String(255), nullable=False)  # Tipo del departamento
    gastos_comunes = db.relationship('GastoComun', backref='departamento', lazy=True)
    pagos = db.relationship('Pago', backref='departamento', lazy=True)

# Modelo Gasto Común
class GastoComun(db.Model):
    __tablename__ = 'gastos_comunes'
    id = db.Column(db.Integer, primary_key=True)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=False)
    periodo = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    pagado = db.Column(db.Boolean, default=False)
    fecha_pago = db.Column(db.Date)

# Modelo Pago
class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    periodo = db.Column(db.Date, nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False)

# Función para obtener el monto del gasto común según el tipo de departamento
def obtener_monto_por_tipo(tipo_departamento):
    # Definir el monto según el tipo de departamento
    if tipo_departamento == "Residencial":
        return 100.00  # Ejemplo de monto para residencial
    elif tipo_departamento == "Comercial":
        return 200.00  # Ejemplo de monto para comercial
    elif tipo_departamento == "Oficina":
        return 150.00  # Ejemplo de monto para oficina
    else:
        return 120.00  # Valor predeterminado



# Endpoint para crear un nucevo departamento
@app.route('/departamentos_crear', methods=['POST'])
def crear_departamento():
    data = request.get_json()
    
    # Validar los datos recibidos
    if not data.get('numero_departamento') or not data.get('nombre') or not data.get('tipo_departamento'):
        return jsonify({"error": "Faltan datos requeridos"}), 400
    
    # Crear un nuevo departamento
    nuevo_departamento = Departamento(
        numero_departamento=data['numero_departamento'],
        nombre=data['nombre'],
        tipo_departamento=data['tipo_departamento']
    )
    
    # Agregar el departamento a la base de datos
    db.session.add(nuevo_departamento)
    db.session.commit()
    
    return jsonify({
        "id": nuevo_departamento.id,
        "numero_departamento": nuevo_departamento.numero_departamento,
        "nombre": nuevo_departamento.nombre,
        "tipo_departamento": nuevo_departamento.tipo_departamento
    }), 201




# Endpoint para listar todos los departamentos
@app.route('/departamentos', methods=['GET'])
def listar_departamentos():
    departamentos = Departamento.query.all()
    
    # Verificar si existen departamentos
    if not departamentos:
        return jsonify({"mensaje": "No se encontraron departamentos"}), 200
    
    # Formatear la respuesta
    lista_departamentos = []
    for depto in departamentos:
        lista_departamentos.append({
            "id": depto.id,
            "numero_departamento": depto.numero_departamento,
            "nombre": depto.nombre,
            "tipo_departamento": depto.tipo_departamento
        })
    
    return jsonify(lista_departamentos), 200




# Endpoint para generar los gastos comunes
@app.route('/generar_gastos', methods=['POST'])
def generar_gastos():
    data = request.get_json()
    tipo_carga = data['tipo_carga']  # 'mes' o 'año'
    periodo = data['periodo']  # Formato: 'YYYY-MM'
    
    if tipo_carga == 'mes':
        fecha = datetime.strptime(periodo, "%Y-%m")
        departamentos = Departamento.query.all()
        for depto in departamentos:
            monto = obtener_monto_por_tipo(depto.tipo_departamento)
            gasto = GastoComun(departamento_id=depto.id, periodo=fecha, monto=monto)
            db.session.add(gasto)
        db.session.commit()
        return jsonify({"message": "Gastos comunes generados correctamente."}), 200
    elif tipo_carga == 'año':
        fecha_inicio = datetime.strptime(periodo, "%Y")
        for mes in range(1, 13):
            fecha_mes = fecha_inicio.replace(month=mes)
            departamentos = Departamento.query.all()
            for depto in departamentos:
                monto = obtener_monto_por_tipo(depto.tipo_departamento)
                gasto = GastoComun(departamento_id=depto.id, periodo=fecha_mes, monto=monto)
                db.session.add(gasto)
        db.session.commit()
        return jsonify({"message": "Gastos comunes generados para todo el año."}), 200
    else:
        return jsonify({"error": "Tipo de carga no válido."}), 400

# Endpoint para marcar un gasto como pagado
@app.route('/marcar_como_pagado', methods=['POST'])
def marcar_como_pagado():
    data = request.get_json()
    departamento_id = data['departamento_id']
    periodo = data['periodo']  # Formato: 'YYYY-MM'
    fecha_pago = data['fecha_pago']  # Formato: 'YYYY-MM-DD'

    fecha = datetime.strptime(periodo, "%Y-%m")
    pago = Pago.query.filter_by(departamento_id=departamento_id, periodo=fecha).first()

    if pago:
        return jsonify({"message": "Pago duplicado"}), 400

    gasto = GastoComun.query.filter_by(departamento_id=departamento_id, periodo=fecha).first()

    if gasto and not gasto.pagado:
        gasto.pagado = True
        gasto.fecha_pago = datetime.strptime(fecha_pago, "%Y-%m-%d")

        # Registrar el pago
        pago = Pago(departamento_id=departamento_id, monto=gasto.monto, periodo=fecha, fecha_pago=gasto.fecha_pago)
        db.session.add(pago)
        db.session.commit()

        # Verificar si el pago fue dentro o fuera de plazo
        mensaje = "Pago exitoso dentro del plazo" if gasto.fecha_pago <= datetime.now() else "Pago exitoso fuera de plazo"
        
        return jsonify({
            "departamento": departamento_id,
            "periodo": periodo,
            "fecha_pago": gasto.fecha_pago.strftime("%Y-%m-%d"),
            "mensaje": mensaje
        }), 200
    else:
        return jsonify({"message": "Gasto no encontrado o ya pagado."}), 404

# Endpoint para obtener los gastos comunes pendientes
@app.route('/gastos_pendientes', methods=['GET'])
def gastos_pendientes():
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)
    fecha = datetime(anio, mes, 1)

    gastos_pendientes = GastoComun.query.filter(GastoComun.periodo <= fecha, GastoComun.pagado == False).all()

    if not gastos_pendientes:
        return jsonify({"mensaje": "Sin montos pendientes"}), 200

    gastos = []
    for gasto in gastos_pendientes:
        departamento = Departamento.query.get(gasto.departamento_id)
        gastos.append({
            "departamento": departamento.numero_departamento,
            "periodo": gasto.periodo.strftime("%Y-%m"),
            "monto": str(gasto.monto)
        })
    
    return jsonify(gastos), 200

# Envolver la creación de las tablas dentro del contexto de la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear tablas en la base de datos
    app.run(debug=True)
