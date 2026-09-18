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
    nombre = request.form.get('nombre')
    asistira = request.form.get('asistira')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO invitados (nombre, asistira) VALUES (%s, %s)', (nombre, asistira))
        conn.commit()
        cursor.close()
        conn.close()
        flash("¡Gracias por registrar tu respuesta!")
    except Exception as e:
        # Esto te mostrará el error exacto en la página web para saber qué campo falló
        flash(f"Error detallado de BD: {e}")
        
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
        
        cursor.execute('SELECT * FROM invitados ORDER BY fecha_registro DESC')
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