from flask import Blueprint, jsonify, request
from conexion import get_db_connection
from werkzeug.utils import secure_filename
import os

# Configurar la carpeta donde se guardarán las fotos
UPLOAD_FOLDER = 'uploads/'  # Asegúrate de crear esta carpeta en tu directorio raíz
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Función para verificar si el archivo tiene una extensión válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Crear el Blueprint para Supervisor
supervisor_bp = Blueprint('supervisor', __name__)

# Ruta POST para agregar un nuevo supervisor
@supervisor_bp.route('/supervisores', methods=['POST'])
def add_supervisor():
    # Verificar si la solicitud tiene el archivo (foto) y los otros campos
    if 'foto' not in request.files:
        return jsonify({'error': 'No se ha cargado ninguna foto'}), 400

    foto = request.files['foto']
    nombre = request.form.get('nombre')
    apellidos = request.form.get('apellidos')
    estado = request.form.get('estado')

    # Verificar que los datos requeridos estén presentes
    if not nombre or not apellidos or not estado:
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    # Verificar que la foto tenga una extensión permitida
    if foto and allowed_file(foto.filename):
        # Crear el nombre seguro para el archivo
        filename = secure_filename(foto.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Guardar el archivo en la carpeta configurada
        foto.save(filepath)

        # Guardar los datos del supervisor en la base de datos
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            query = """
                INSERT INTO supervisor (nombre, apellidos, estado, foto) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (nombre, apellidos, estado, filepath))
            connection.commit()

            return jsonify({'message': 'Supervisor creado con éxito'}), 201

        except Exception as e:
            return jsonify({'error': f'Error al insertar el supervisor: {e}'}), 500

        finally:
            if connection and connection.is_connected():
                connection.close()
    else:
        return jsonify({'error': 'Foto no válida'}), 400


# Ruta GET para obtener todos los supervisores
@supervisor_bp.route('/supervisores', methods=['GET'])
def get_supervisores():
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM supervisor"  # Aquí estamos apuntando a la tabla `supervisor`
            cursor.execute(query)
            supervisores = cursor.fetchall()
            return jsonify(supervisores), 200

    except Exception as e:
        return jsonify({'error': f'Error al conectar o realizar la consulta: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# Ruta PUT para actualizar un supervisor por id
@supervisor_bp.route('/supervisores/<int:idSupervisor>', methods=['PUT'])
def update_supervisor(idSupervisor):
    data = request.get_json()
    required_fields = ['nombre', 'apellidos', 'estado', 'foto']

    # Verificar que los datos requeridos estén presentes
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()

            # Verificar si el supervisor existe
            check_query = "SELECT * FROM supervisor WHERE idSupervisor = %s"
            cursor.execute(check_query, (idSupervisor,))
            supervisor = cursor.fetchone()

            if not supervisor:
                return jsonify({'error': f'El supervisor con id {idSupervisor} no existe'}), 404

            # Actualizar el supervisor
            update_query = """
                UPDATE supervisor 
                SET nombre = %s, apellidos = %s, estado = %s, foto = %s 
                WHERE idSupervisor = %s
            """
            cursor.execute(update_query, (data['nombre'], data['apellidos'], data['estado'], data['foto'], idSupervisor))
            connection.commit()

            return jsonify({'message': f'Supervisor con id {idSupervisor} actualizado con éxito'}), 200

    except Exception as e:
        return jsonify({'error': f'Error al actualizar el supervisor: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# Ruta DELETE para eliminar un supervisor por id
@supervisor_bp.route('/supervisores/<int:idSupervisor>', methods=['DELETE'])
def delete_supervisor(idSupervisor):
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()

            # Verificar si el supervisor existe
            check_query = "SELECT * FROM supervisor WHERE idSupervisor = %s"
            cursor.execute(check_query, (idSupervisor,))
            supervisor = cursor.fetchone()

            if not supervisor:
                return jsonify({'error': f'El supervisor con id {idSupervisor} no existe'}), 404

            # Eliminar el supervisor
            delete_query = "DELETE FROM supervisor WHERE idSupervisor = %s"
            cursor.execute(delete_query, (idSupervisor,))
            connection.commit()

            return jsonify({'message': f'Supervisor con id {idSupervisor} eliminado con éxito'}), 200

    except Exception as e:
        return jsonify({'error': f'Error al eliminar el supervisor: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()

