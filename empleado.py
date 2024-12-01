from flask import Blueprint, jsonify, request
from conexion import get_db_connection
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory

empleado_bp = Blueprint('empleado', __name__)

@empleado_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Definir el directorio donde se guardarán las fotos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Asegurarse de que el directorio exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Función para verificar las extensiones permitidas de las fotos
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# GET: Obtener empleados registrados
@empleado_bp.route('/empleados', methods=['GET'])
def get_users():
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    e.idEmpleados,
                    e.nombre,
                    e.apellido,
                    e.fecha_nac,
                    e.ciudad,
                    e.direccion,
                    e.telefono,
                    d.nombre AS departamento,
                    CONCAT(s.nombre, ' ', s.apellidos) AS supervisor,
                    e.salario,
                    e.foto
                FROM tb_empleados e
                LEFT JOIN departamento d ON e.idDepartamento = d.idDepartamento
                LEFT JOIN supervisor s ON e.idSupervisor = s.idSupervisor;
            """
            cursor.execute(query)
            users = cursor.fetchall()

            # No es necesario cambiar nada en la foto, solo mostrar la URL
            return jsonify(users), 200

    except Exception as e:
        return jsonify({'error': f'Error al conectar o realizar la consulta: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()


@empleado_bp.route('/empleados', methods=['POST'])
def add_user():
    data = request.form
    foto = request.files.get('foto')
    if foto and allowed_file(foto.filename):
        filename = secure_filename(foto.filename)
        foto_path = os.path.join(UPLOAD_FOLDER, filename)
        foto.save(foto_path)

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO tb_empleados (nombre, apellido, fecha_nac, ciudad, direccion, telefono, idDepartamento, idSupervisor, salario, foto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['nombre'], data['apellido'], data['fecha_nac'], data['ciudad'], 
            data['direccion'], data['telefono'], data['idDepartamento'], 
            data['idSupervisor'], data['salario'], foto_path
        ))
        connection.commit()
        return jsonify({'message': 'Empleado agregado exitosamente.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

        # GET: Obtener un empleado por ID
@empleado_bp.route('/empleados/<int:idEmpleados>', methods=['GET'])
def get_user_by_id(idEmpleados):
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Consulta SQL para buscar un empleado por su ID
            query = """
                SELECT 
                    e.idEmpleados,
                    e.nombre,
                    e.apellido,
                    e.fecha_nac,
                    e.ciudad,
                    e.direccion,
                    e.telefono,
                    d.nombre AS departamento,
                    CONCAT(s.nombre, ' ', s.apellidos) AS supervisor,
                    e.salario,
                    e.foto
                FROM tb_empleados e
                LEFT JOIN departamento d ON e.idDepartamento = d.idDepartamento
                LEFT JOIN supervisor s ON e.idSupervisor = s.idSupervisor
                WHERE e.idEmpleados = %s
            """
            cursor.execute(query, (idEmpleados,))
            empleado = cursor.fetchone()

            if empleado:
                return jsonify(empleado), 200
            else:
                return jsonify({'error': f'Empleado con ID {idEmpleados} no encontrado'}), 404

    except Exception as e:
        return jsonify({'error': f'Error al obtener el empleado: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()


# DELETE: Eliminar un empleado
@empleado_bp.route('/empleados/<int:idEmpleados>', methods=['DELETE'])
def delete_user(idEmpleados):
    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor()

            # Verificar si el empleado existe
            check_query = "SELECT * FROM tb_empleados WHERE idEmpleados = %s"
            cursor.execute(check_query, (idEmpleados,))
            empleado = cursor.fetchone()

            if not empleado:
                return jsonify({'error': f'El empleado con id {idEmpleados} no existe'}), 404

            # Eliminar el empleado
            delete_query = "DELETE FROM tb_empleados WHERE idEmpleados = %s"
            cursor.execute(delete_query, (idEmpleados,))
            connection.commit()

            return jsonify({'message': f'Empleado con id {idEmpleados} eliminado con éxito'}), 200

    except Exception as e:
        return jsonify({'error': f'Error al eliminar el empleado: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()

@empleado_bp.route('/empleados/<int:idEmpleados>', methods=['PUT'])
def update_user(idEmpleados):
    try:
        data = request.json
        foto = request.files.get('foto')  # Obtener nueva imagen del formulario

        if foto and allowed_file(foto.filename):
            # Guardar nueva imagen
            filename = secure_filename(foto.filename)
            foto_path = os.path.join(UPLOAD_FOLDER, filename)
            foto.save(foto_path)
            foto_sql = foto_path  # Ruta de la nueva imagen
        else:
            # Mantener la foto actual si no se proporciona una nueva
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "SELECT foto FROM tb_empleados WHERE idEmpleados = %s"
            cursor.execute(query, (idEmpleados,))
            empleado = cursor.fetchone()

            if empleado:
                foto_sql = empleado['foto']  # Mantener foto actual
            else:
                return jsonify({'error': 'Empleado no encontrado'}), 404

        # Actualizar la información del empleado en la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            UPDATE tb_empleados
            SET nombre = %s, apellido = %s, fecha_nac = %s, ciudad = %s, 
                direccion = %s, telefono = %s, idDepartamento = %s, 
                idSupervisor = %s, salario = %s, foto = %s
            WHERE idEmpleados = %s
        """
        cursor.execute(query, (
            data['nombre'], data['apellido'], data['fecha_nac'], data['ciudad'], 
            data['direccion'], data['telefono'], data['departamento'], 
            data['supervisor'], data['salario'], foto_sql, idEmpleados
        ))
        connection.commit()

        return jsonify({'message': 'Empleado actualizado exitosamente.'}), 200

    except Exception as e:
        return jsonify({'error': f'Error al actualizar empleado: {e}'}), 500
    finally:
        if connection and connection.is_connected():
            connection.close()
