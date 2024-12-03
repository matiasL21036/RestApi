from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from sqlalchemy.sql import extract
from flask_cors import CORS  # Importa la extensión CORS
# Inicializar Flask y SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


CORS(app) 
# Modelo Departamento
class Departamento(db.Model):
    __tablename__ = 'departamentos'
    id = db.Column(db.Integer, primary_key=True)
    numero_departamento = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    tipo_departamento = db.Column(db.String(255), nullable=False)  # Tipo del departamento
    gastos_comunes = db.relationship('GastoComun', backref='departamento', lazy=True)
    pagos = db.relationship('Pago', backref='departamento', lazy=True)
usuario = db.relationship('Usuario', backref='departamento', uselist=False)
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
    
    
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    rut = db.Column(db.String(12), unique=True, nullable=False)
    correo = db.Column(db.String(255))
    contrasena = db.Column(db.String(255), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=True)   
    departamento = db.relationship('Departamento', backref='usuario', uselist=False) 

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

# Modelo Usuario


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

    if not departamentos:
        return jsonify({"mensaje": "No se encontraron departamentos"}), 200

    lista_departamentos = []
    for departamento in departamentos:
        # Accedemos al primer usuario en la lista (si existe)
        usuario = departamento.usuario[0] if departamento.usuario else None
        lista_departamentos.append({
            "id": departamento.id,
            "numero_departamento": departamento.numero_departamento,
            "nombre": departamento.nombre,
            "tipo_departamento": departamento.tipo_departamento,
            "rut_usuario": usuario.rut if usuario else None  # Añadir el rut del usuario
        })

    return jsonify(lista_departamentos), 200


# Endpoint para modificar un departamento
@app.route('/departamentos_modificar/<int:id>', methods=['PUT'])
def modificar_departamento(id):
    data = request.get_json()
    departamento = Departamento.query.get(id)

    if not departamento:
        return jsonify({"error": "Departamento no encontrado"}), 404

    departamento.numero_departamento = data.get('numero_departamento', departamento.numero_departamento)
    departamento.nombre = data.get('nombre', departamento.nombre)
    departamento.tipo_departamento = data.get('tipo_departamento', departamento.tipo_departamento)

    db.session.commit()

    return jsonify({
        "id": departamento.id,
        "numero_departamento": departamento.numero_departamento,
        "nombre": departamento.nombre,
        "tipo_departamento": departamento.tipo_departamento
    }), 200
    
    # Endpoint para eliminar un departamento
@app.route('/departamentos_eliminar/<int:id>', methods=['DELETE'])
def eliminar_departamento(id):
    departamento = Departamento.query.get(id)

    if not departamento:
        return jsonify({"error": "Departamento no encontrado"}), 404

    db.session.delete(departamento)
    db.session.commit()

    return jsonify({"mensaje": "Departamento eliminado exitosamente"}), 200


@app.route('/generar_gastos', methods=['POST'])
def generar_gastos():
    try:
        # Obtener parámetros del request
        data = request.get_json()
        mes = data.get('mes')
        anio = data.get('anio')

        if not anio:
            return jsonify({"error": "El año es obligatorio"}), 400

        # Convertir 'anio' a entero explícitamente
        try:
            anio = int(anio)
        except ValueError:
            return jsonify({"error": "El año debe ser un número entero válido."}), 400

        # Validar rango de mes si se incluye
        if mes is not None:
            try:
                mes = int(mes)
            except ValueError:
                return jsonify({"error": "El mes debe ser un número entero válido."}), 400
            
            if mes < 1 or mes > 12:
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
                    monto = departamento.monto_fijo if hasattr(departamento, 'monto_fijo') else 50000  # Ejemplo de monto fijo
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

        # Intentar hacer commit en la base de datos
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Hacer rollback en caso de error
            print("Error al hacer commit:", e)
            return jsonify({"error": "Error al guardar los gastos en la base de datos"}), 500

        if not gastos_generados:
            return jsonify({"message": "Todos los gastos ya estaban registrados"}), 200

        return jsonify({"gastos_generados": gastos_generados}), 201

    except Exception as e:
        print("Error al generar gastos:", e)  # Imprime el error en los logs del servidor
        return jsonify({"error": str(e)}), 500

# Endpoint para listar todos los gastos comunes
@app.route('/gastos_comunes', methods=['GET'])
def listar_gastos_comunes():
    filtro_pagado = request.args.get('pagado', type=bool, default=None)

    # Filtrar por estado de pagado
    if filtro_pagado is not None:
        gastos = GastoComun.query.filter_by(pagado=filtro_pagado).all()
    else:
        gastos = GastoComun.query.all()

    if not gastos:
        return jsonify({"mensaje": "No se encontraron gastos comunes"}), 200

    lista_gastos = []
    for gasto in gastos:
        # Obtener el departamento asociado con el gasto común
        departamento = Departamento.query.filter_by(id=gasto.departamento_id).first()

        # Verificar si el departamento existe
        if departamento:
            # Buscar el usuario que corresponde al departamento_id del departamento
            usuario = Usuario.query.filter_by(departamento_id=departamento.id).first()
            if usuario:
                rut_propietario = usuario.rut  # Obtener el RUT del propietario
            else:
                rut_propietario = None  # Si no se encuentra un usuario, asignar None
        else:
            rut_propietario = None  # Si no se encuentra un departamento, asignar None

        # Agregar el gasto a la lista
        lista_gastos.append({
            "departamento_id": gasto.departamento_id,
            "periodo": gasto.periodo.strftime("%Y-%m"),
            "monto": gasto.monto,
            "pagado": gasto.pagado,
            "rut_propietario": rut_propietario  # Incluir el RUT del propietario
        })

    return jsonify(lista_gastos), 200

@app.route('/gastos_comunes_eliminar/<int:id>', methods=['DELETE'])
def eliminar_gasto_comun(id):
    gasto = GastoComun.query.get(id)

    if not gasto:
        return jsonify({"error": "Gasto común no encontrado"}), 404

    db.session.delete(gasto)
    db.session.commit()

    return jsonify({"mensaje": "Gasto común eliminado exitosamente"}), 200

@app.route('/eliminar_todos_los_gastos', methods=['DELETE'])
def eliminar_todos_los_gastos():
    try:
        # Eliminar todos los registros de la tabla GastoComun
        GastoComun.query.delete()

        # Confirmar los cambios en la base de datos
        db.session.commit()

        return jsonify({"mensaje": "Todos los gastos comunes han sido eliminados exitosamente."}), 200
    except Exception as e:
        db.session.rollback()  # Hacer rollback en caso de error
        return jsonify({"error": f"Error al eliminar los gastos comunes: {str(e)}"}), 500

# Endpoint para marcar un gasto como pagado
@app.route('/marcar_como_pagado', methods=['POST'])
def marcar_como_pagado():
    try:
        data = request.get_json()
        departamento_id = data.get('departamento_id')
        anio = data.get('anio')
        mes = data.get('mes')
        fecha_pago = datetime.now().date()

        # Convertir 'anio' y 'mes' a enteros
        anio = int(anio)
        mes = int(mes)

        if not (departamento_id and anio and mes):
            return jsonify({"error": "Faltan parámetros: 'departamento_id', 'anio' o 'mes'"}), 400

        # Validación: Verifica si el gasto existe para ese departamento, año y mes
        periodo = date(anio, mes, 1)
        gasto = GastoComun.query.filter_by(departamento_id=departamento_id, periodo=periodo).first()

        if not gasto:
            return jsonify({"error": "No se encontró un gasto para el periodo indicado"}), 404

        # Verifica si el gasto ya está pagado
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

        db.session.add(pago)

        # Marcar como pagado el gasto
        gasto.pagado = True
        gasto.fecha_pago = fecha_pago

        # Confirmar transacción
        db.session.commit()

        return jsonify({
            "departamento_id": departamento_id,
            "fecha_cancelacion": fecha_pago.strftime("%Y-%m-%d"),
            "periodo": periodo.strftime("%Y-%m"),
            "mensaje": "Pago exitoso"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500



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



# Endpoint para crear un nuevo usuario
@app.route('/usuarios_crear', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    
    if not data.get('nombre') or not data.get('rut') or not data.get('contrasena'):
        return jsonify({"error": "Faltan datos requeridos"}), 400

    # Verificar si el RUT ya existe
    rut_existente = Usuario.query.filter_by(rut=data['rut']).first()
    if rut_existente:
        return jsonify({"error": "El RUT ya está registrado"}), 400

    nuevo_usuario = Usuario(
        nombre=data['nombre'],
        rut=data['rut'],
        correo=data.get('correo'),
        contrasena=data['contrasena'],
        es_admin=data.get('es_admin', False),
        departamento_id=data.get('departamento_id')
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "rut": nuevo_usuario.rut,
        "correo": nuevo_usuario.correo,
        "es_admin": nuevo_usuario.es_admin,
        "departamento_id": nuevo_usuario.departamento_id
    }), 201

# Endpoint para listar todos los usuarios
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    if not usuarios:
        return jsonify({"mensaje": "No se encontraron usuarios"}), 200

    lista_usuarios = []
    for usuario in usuarios:
        lista_usuarios.append({
            "id": usuario.id,
            "nombre": usuario.nombre,
            "rut": usuario.rut,
            "correo": usuario.correo,
            "es_admin": usuario.es_admin,
            "departamento_id": usuario.departamento_id
        })
    
    return jsonify(lista_usuarios), 200

# Endpoint para modificar un usuario
@app.route('/usuarios_modificar/<int:id>', methods=['PUT'])
def modificar_usuario(id):
    data = request.get_json()
    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    usuario.nombre = data.get('nombre', usuario.nombre)
    usuario.rut = data.get('rut', usuario.rut)
    usuario.correo = data.get('correo', usuario.correo)
    usuario.contrasena = data.get('contrasena', usuario.contrasena)
    usuario.es_admin = data.get('es_admin', usuario.es_admin)
    usuario.departamento_id = data.get('departamento_id', usuario.departamento_id)

    db.session.commit()

    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "rut": usuario.rut,
        "correo": usuario.correo,
        "es_admin": usuario.es_admin,
        "departamento_id": usuario.departamento_id
    }), 200

# Endpoint para eliminar un usuario
@app.route('/usuarios_eliminar/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"mensaje": "Usuario eliminado exitosamente"}), 200

@app.route('/api/gastos_pendientes/<string:rut>', methods=['GET'])
def get_gastos_pendientes(rut):
    usuario = Usuario.query.filter_by(rut=rut).first()

    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    gastos = GastoComun.query.filter_by(departamento_id=usuario.departamento_id, pagado=False).all()

    if not gastos:
        return jsonify({'message': 'No se encontraron gastos pendientes'}), 404

    # Convertir las fechas a formato más manejable (YYYY-MM-DD)
    gastos_pendientes = [{
        'periodo': gasto.periodo.strftime('%Y-%m-%d'),  # Formato de fecha
        'monto': str(gasto.monto)
    } for gasto in gastos]

    return jsonify(gastos_pendientes)



# Envolver la creación de las tablas dentro del contexto de la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear tablas en la base de datos
    app.run(debug=True)
