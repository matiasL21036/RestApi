from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from sqlalchemy.sql import extract
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
    if tipo_departamento == "Duplex":
        return 100.000  # Ejemplo de monto para residencial
    elif tipo_departamento == "Home studio":
        return 70.000  # Ejemplo de monto para comercial
    elif tipo_departamento == "Oficina":
        return 70.000  # Ejemplo de monto para oficina
    else:
        return 50.000  # Valor predeterminado



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
    try:
        # Obtener parámetros del request
        data = request.get_json()
        mes = data.get('mes')
        anio = data.get('anio')

        if not anio:
            return jsonify({"error": "El año es obligatorio"}), 400

        # Validar rango de mes si se incluye
        if mes and (mes < 1 or mes > 12):
            return jsonify({"error": "El mes debe estar entre 1 y 12"}), 400

        # Obtener todos los departamentos
        departamentos = Departamento.query.all()
        if not departamentos:
            return jsonify({"error": "No hay departamentos registrados"}), 400

        # Crear gastos por mes o por todo el año
        gastos_generados = []
        meses = [mes] if mes else range(1, 13)  # Mes específico o todos los meses
        for m in meses:
            for departamento in departamentos:
                # Verificar si el gasto ya existe
                periodo = date(anio, m, 1)
                gasto_existente = GastoComun.query.filter_by(
                    departamento_id=departamento.id,
                    periodo=periodo
                ).first()

                if not gasto_existente:
                    # Crear gasto nuevo (montos diferenciados si aplica)
                    monto = departamento.monto_fijo if hasattr(departamento, 'monto_fijo') else 50000  # Por ejemplo
                    nuevo_gasto = GastoComun(
                        departamento_id=departamento.id,
                        periodo=periodo,
                        monto=monto,
                        pagado=False
                    )
                    db.session.add(nuevo_gasto)
                    gastos_generados.append({
                        "departamento_id": departamento.id,
                        "periodo": periodo.strftime("%Y-%m"),
                        "monto": monto
                    })

        db.session.commit()

        if not gastos_generados:
            return jsonify({"message": "Todos los gastos ya estaban registrados"}), 200

        return jsonify({"gastos_generados": gastos_generados}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint para marcar un gasto como pagado
@app.route('/marcar_como_pagado', methods=['POST'])
def marcar_como_pagado():
    try:
        # Obtener parámetros del request
        data = request.get_json()
        departamento_id = data.get('departamento_id')
        anio = data.get('anio')
        mes = data.get('mes')
        fecha_pago = datetime.now().date()  # Fecha de pago actual

        if not (departamento_id and anio and mes):
            return jsonify({"error": "Los campos 'departamento_id', 'anio' y 'mes' son obligatorios"}), 400

        # Validar si el gasto existe
        periodo = date(anio, mes, 1)
        gasto = GastoComun.query.filter_by(departamento_id=departamento_id, periodo=periodo).first()

        if not gasto:
            return jsonify({"error": "No existe un gasto para el período indicado"}), 404

        # Validar estado del gasto
        if gasto.pagado:
            return jsonify({
                "departamento_id": departamento_id,
                "fecha_cancelacion": gasto.fecha_pago.strftime("%Y-%m-%d"),
                "periodo": periodo.strftime("%Y-%m"),
                "mensaje": "Pago duplicado"
            }), 400

        # Crear el pago
        pago = Pago(
            departamento_id=departamento_id,
            monto=gasto.monto,
            periodo=periodo,
            fecha_pago=fecha_pago
        )

        # Agregar el pago a la base de datos
        db.session.add(pago)

        # Marcar el gasto como pagado
        gasto.pagado = True
        gasto.fecha_pago = fecha_pago

        # Confirmar los cambios en la base de datos
        db.session.commit()

        return jsonify({
            "departamento_id": departamento_id,
            "fecha_cancelacion": fecha_pago.strftime("%Y-%m-%d"),
            "periodo": periodo.strftime("%Y-%m"),
            "mensaje": "Pago exitoso"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Endpoint para obtener los gastos comunes pendientes
@app.route('/gastos_pendientes', methods=['GET'])
def gastos_pendientes():
    try:
        # Obtener parámetros del request
        mes = request.args.get('mes', type=int)
        anio = request.args.get('anio', type=int)

        # Validar parámetros
        if not mes or not anio:
            return jsonify({"error": "Parámetros 'mes' y 'anio' son obligatorios"}), 400

        if mes < 1 or mes > 12:
            return jsonify({"error": "El mes debe estar entre 1 y 12"}), 400

        # Filtrar gastos no pagados desde enero hasta el mes indicado del año
        gastos = (
            GastoComun.query
            .filter(
                GastoComun.pagado == False,
                extract('year', GastoComun.periodo) == anio,
                extract('month', GastoComun.periodo) <= mes
            )
            .order_by(GastoComun.periodo.asc())
            .all()
        )

        # Si no hay gastos pendientes
        if not gastos:
            return jsonify({"message": f"No hay gastos pendientes para {anio}-{str(mes).zfill(2)}"}), 200

        # Preparar respuesta con los gastos sin 'fecha_limite'
        gastos_pendientes = []
        for gasto in gastos:
            gastos_pendientes.append({
                "departamento_id": gasto.departamento_id,
                "periodo": gasto.periodo.strftime("%Y-%m"),
                "monto": gasto.monto
            })

        # Devolver lista de gastos pendientes
        return jsonify(gastos_pendientes), 200

    except Exception as e:
        # Manejo de errores internos
        return jsonify({"error": str(e)}), 500


# Envolver la creación de las tablas dentro del contexto de la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear tablas en la base de datos
    app.run(debug=True)
