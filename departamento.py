from flask import Blueprint, jsonify, request
from conexion import get_db_connection

# Crear el Blueprint
departamento_bp = Blueprint('departamento', __name__)

# Ruta GET para obtener todos los departamentos
@departamento_bp.route('/departamentos', methods=['GET'])
def get_departamentos():
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM departamento"
            cursor.execute(query)
            departamentos = cursor.fetchall()
            return jsonify(departamentos), 200

    except Exception as e:
        return jsonify({'error': f'Error al conectar o realizar la consulta: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()

# Ruta GET para obtener un supervisor específico por id
@departamento_bp.route('/departamentos/<int:idDepartamento>', methods=['GET'])
def get_supervisor(idDepartamento):
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM departamento WHERE idDepartamento = %s"
            cursor.execute(query, (idDepartamento,))
            supervisor = cursor.fetchone()

            if supervisor:
                return jsonify(supervisor), 200
            else:
                return jsonify({'error': 'Supervisor no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Error al obtener los datos: {e}'}), 500
    finally:
        if connection and connection.is_connected():
            connection.close()

# Ruta POST para agregar un nuevo departamento
@departamento_bp.route('/departamentos', methods=['POST'])
def add_departamento():
    data = request.get_json()
    required_fields = ['nombre']

    # Verificar que los datos requeridos estén presentes
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            query = """
                INSERT INTO departamento (nombre) 
                VALUES (%s)
            """
            cursor.execute(query, (data['nombre'],))
            connection.commit()

            return jsonify({'message': 'Departamento creado con éxito'}), 201

    except Exception as e:
        return jsonify({'error': f'Error al insertar el departamento: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# Ruta PUT para actualizar un departamento por id
@departamento_bp.route('/departamentos/<int:idDepartamento>', methods=['PUT'])
def update_departamento(idDepartamento):
    data = request.get_json()
    required_fields = ['nombre']

    if not all(field in data and data[field] for field in required_fields):
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            check_query = "SELECT * FROM departamento WHERE idDepartamento = %s"
            cursor.execute(check_query, (idDepartamento,))
            departamento = cursor.fetchone()

            if not departamento:
                return jsonify({'error': f'El departamento con id {idDepartamento} no existe'}), 404

            update_query = "UPDATE departamento SET nombre = %s WHERE idDepartamento = %s"
            cursor.execute(update_query, (data['nombre'], idDepartamento))
            connection.commit()

            return jsonify({'message': f'Departamento con id {idDepartamento} actualizado con éxito'}), 200

    except Exception as e:
        return jsonify({'error': f'Error al actualizar el departamento: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# Ruta DELETE para eliminar un departamento por id
@departamento_bp.route('/departamentos/<int:idDepartamento>', methods=['DELETE'])
def delete_departamento(idDepartamento):
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            check_query = "SELECT * FROM departamento WHERE idDepartamento = %s"
            cursor.execute(check_query, (idDepartamento,))
            departamento = cursor.fetchone()

            if not departamento:
                return jsonify({'error': f'El departamento con id {idDepartamento} no existe'}), 404

            delete_query = "DELETE FROM departamento WHERE idDepartamento = %s"
            cursor.execute(delete_query, (idDepartamento,))
            connection.commit()

            return jsonify({'message': f'Departamento con id {idDepartamento} eliminado con éxito'}), 200

    except Exception as e:
        return jsonify({'error': f'Error al eliminar el departamento: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()
