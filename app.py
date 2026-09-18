import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import psycopg2

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'comprobantes')

app = Flask(__name__)
app.secret_key = "clave_quinceañera_secreta" 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ADMIN_PASSWORD = 'Abigail2026'
DATABASE_URL = os.environ.get('DATABASE_URL')

os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("Falta DATABASE_URL en Render")
    return psycopg2.connect(DATABASE_URL)

def init_db():
    if not DATABASE_URL:
        return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invitados (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                asistira VARCHAR(50) NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regalos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                archivo VARCHAR(255) NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error en DB:", e)

# Inicializar base de datos
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rsvp', methods=['POST'])
def rsvp():
    nombre = request.form.get('nombre', '').strip()
    asistira = request.form.get('asistira')
    
    if not nombre:
        flash("Por favor ingresa tu nombre.")
        return redirect(url_for('index') + '#rsvp')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Evitar duplicados: actualiza si ya existe el nombre
        cursor.execute('SELECT id FROM invitados WHERE LOWER(nombre) = LOWER(%s)', (nombre,))
        existente = cursor.fetchone()
        
        if existente:
            cursor.execute('UPDATE invitados SET asistira = %s, fecha_registro = CURRENT_TIMESTAMP WHERE LOWER(nombre) = LOWER(%s)', (asistira, nombre))
            flash("¡Tu registro ha sido actualizado con éxito!")
        else:
            cursor.execute('INSERT INTO invitados (nombre, asistira) VALUES (%s, %s)', (nombre, asistira))
            flash("¡Gracias por registrar tu respuesta!")
            
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f"Error al guardar: {e}")
        
    return redirect(url_for('index') + '#rsvp')

@app.route('/subir_yape', methods=['POST'])
def subir_yape():
    nombre = request.form.get('nombre_yape')
    foto = request.files.get('comprobante')
    
    if foto and foto.filename:
        filename = secure_filename(foto.filename)
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO regalos (nombre, archivo) VALUES (%s, %s)', (nombre, filename))
            conn.commit()
            cursor.close()
            conn.close()
            flash("¡Gracias por tu regalito! Comprobante enviado con éxito.")
        except Exception:
            flash("Error al guardar el comprobante.")
        
    return redirect(url_for('index') + '#regalos')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = "Contraseña incorrecta."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    invitados = []
    regalos = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Muestra una sola vez a cada invitado con su última respuesta en Neon
        cursor.execute('''
            SELECT DISTINCT ON (LOWER(nombre)) id, nombre, asistira, fecha_registro 
            FROM invitados 
            ORDER BY LOWER(nombre), fecha_registro DESC
        ''')
        invitados = cursor.fetchall()
        
        cursor.execute('SELECT * FROM regalos ORDER BY fecha_registro DESC')
        regalos = cursor.fetchall()
        
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error consultando DB:", e)
        
    return render_template('admin.html', invitados=invitados, regalos=regalos)

if __name__ == '__main__':
    app.run(debug=True)