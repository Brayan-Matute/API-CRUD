from flask import Flask, send_from_directory
from flask_cors import CORS
from login import login_bp
from empleado import empleado_bp
from departamento import departamento_bp
from supervisor import supervisor_bp
from conexion import get_db_connection
import os

app = Flask(__name__)
CORS(app)

# Configurar la carpeta donde se guardarán las fotos
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limitar tamaño máximo de archivo a 16MB

# Función para verificar si el archivo tiene una extensión válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para servir las imágenes
@app.route('/uploads/<filename>')
def serve_image(filename):
    # Servir la imagen desde la carpeta 'uploads'
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Registrar los Blueprints
app.register_blueprint(login_bp)
app.register_blueprint(empleado_bp)
app.register_blueprint(departamento_bp)
app.register_blueprint(supervisor_bp)

@app.route('/')
def index():
    return "Bienvenido a la API de Login y Empleados"

def verificar_conexion():
    connection = get_db_connection()
    if connection and connection.is_connected():
        print("🔗 Base de datos conectada exitosamente.")
        connection.close()
    else:
        print("❌ Error al conectar con la base de datos.")

if __name__ == '__main__':
    verificar_conexion()  # Verificar conexión a la base de datos al iniciar
    app.run(debug=True)
