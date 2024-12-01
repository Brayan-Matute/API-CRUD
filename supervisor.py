from flask import Blueprint, jsonify, request
from conexion import get_db_connection
from werkzeug.utils import secure_filename
import os

# Configurar la carpeta donde se guardarán las fotos
UPLOAD_FOLDER = 'uploads/'  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


supervisor_bp = Blueprint('supervisor', __name__)

#CRUD

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


# Ruta GET para obtener un supervisor específico por id
@supervisor_bp.route('/supervisores/<int:idSupervisor>', methods=['GET'])
def get_supervisor(idSupervisor):
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM supervisor WHERE idSupervisor = %s"
            cursor.execute(query, (idSupervisor,))
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


# Ruta POST para agregar un nuevo supervisor
@supervisor_bp.route('/supervisores', methods=['POST'])
def add_supervisor():
    if 'foto' not in request.files:
        return jsonify({'error': 'No se ha cargado ninguna foto'}), 400

    foto = request.files['foto']
    nombre = request.form.get('nombre')
    apellidos = request.form.get('apellidos')
    estado = request.form.get('estado')

    if not nombre or not apellidos or not estado:
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    if foto and allowed_file(foto.filename):
        filename = secure_filename(foto.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        foto.save(filepath)
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
    

# Ruta PUT para editar un supervisor
@supervisor_bp.route('/supervisores/<int:idSupervisor>', methods=['PUT'])
def update_supervisor(idSupervisor):
    try:
        nombre = request.json.get('nombre')
        apellidos = request.json.get('apellidos')
        estado = request.json.get('estado')

        if not all([nombre, apellidos, estado]):
            return jsonify({'error': 'Faltan datos obligatorios'}), 400

        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM supervisor WHERE idSupervisor = %s", (idSupervisor,))
            if not cursor.fetchone():
                return jsonify({'error': f'El supervisor con id {idSupervisor} no existe'}), 404

            update_query = "UPDATE supervisor SET nombre = %s, apellidos = %s, estado = %s WHERE idSupervisor = %s"
            cursor.execute(update_query, (nombre, apellidos, estado, idSupervisor))
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
            check_query = "SELECT * FROM supervisor WHERE idSupervisor = %s"
            cursor.execute(check_query, (idSupervisor,))
            supervisor = cursor.fetchone()

            if not supervisor:
                return jsonify({'error': f'El supervisor con id {idSupervisor} no existe'}), 404

            delete_query = "DELETE FROM supervisor WHERE idSupervisor = %s"
            cursor.execute(delete_query, (idSupervisor,))
            connection.commit()

            return jsonify({'message': f'Supervisor con id {idSupervisor} eliminado con éxito'}), 200

    except Exception as e:
        return jsonify({'error': f'Error al eliminar el supervisor: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()

