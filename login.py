from flask import Blueprint, jsonify, request
from conexion import get_db_connection

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('user')
    password = data.get('pass')

    if not username or not password:
        return jsonify({'error': 'Faltan datos, asegúrate de enviar tanto el usuario como la contraseña'}), 400

    try:
        connection = get_db_connection()
        if connection and connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT idlogin, user, pass FROM login WHERE user = %s"
            cursor.execute(query, (username,))
            user_record = cursor.fetchone()

            if user_record:
                if user_record['pass'] == password:
                    return jsonify({'message': 'Login exitoso', 'idlogin': user_record['idlogin']}), 200
                else:
                    return jsonify({'error': 'Contraseña incorrecta'}), 401
            else:
                return jsonify({'error': 'Usuario no encontrado'}), 404

    except Exception as e:
        return jsonify({'error': f'Error al conectar o realizar la consulta: {e}'}), 500

    finally:
        if connection and connection.is_connected():
            connection.close()
