from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_poli_2026'

def get_db_connection():
    conn = sqlite3.connect('zona2.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    if not os.path.exists('zona2.db'):
        conn = get_db_connection()
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.close()

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username'].lower().strip()
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO USUARIO (nombre_usuario, clave_hash) VALUES (?, ?)',
                         (username, generate_password_hash(password)))
            conn.commit()
            flash('Cuenta creada con éxito. Ya puedes iniciar sesión.')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe.')
        finally:
            conn.close()
    return render_template('login.html', register=True)

@app.route('/login', methods=('POST',))
def login():
    username = request.form['username'].lower().strip()
    password = request.form['password']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM USUARIO WHERE nombre_usuario = ?', (username,)).fetchone()
    conn.close()
    if user and check_password_hash(user['clave_hash'], password):
        session['usuario_id'] = user['usuario_id']
        session['nombre_usuario'] = user['nombre_usuario']
        return redirect(url_for('dashboard'))
    flash('Usuario o contraseña incorrectos.')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    conn = get_db_connection()
    sesiones = conn.execute('''
        SELECT * FROM SESION_ENTRENAMIENTO 
        WHERE usuario_id = ? 
        ORDER BY fecha_sesion DESC, sesion_id DESC
    ''', (session['usuario_id'],)).fetchall()
    conn.close()
    datos_vista = []
    for s in sesiones:
        M = 220 - s['edad_sesion']
        L100 = 60 * M
        U100 = 70 * M
        P100 = s['fc_promedio_centesimas']
        clasificacion = 'Dentro'
        if P100 < L100: clasificacion = 'Inferior'
        elif P100 > U100: clasificacion = 'Superior'
        datos_vista.append({
            'id': s['sesion_id'],
            'fecha': s['fecha_sesion'],
            'actividad': s['tipo_actividad'],
            'minutos': s['duracion_centiminutos'] / 100,
            'promedio': s['fc_promedio_centesimas'] / 100,
            'lim_inf': L100 / 100,
            'lim_sup': U100 / 100,
            'clasificacion': clasificacion
        })
    return render_template('dashboard.html', sesiones=datos_vista, usuario=session['nombre_usuario'])

@app.route('/add_session', methods=('GET', 'POST'))
def add_session():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        fecha = request.form['fecha']
        actividad = request.form['actividad']
        edad = int(request.form['edad'])
        duracion = float(request.form['duracion'])
        promedio = float(request.form['promedio'])
        duracion_cent = int(duracion * 100)
        promedio_cent = int(promedio * 100)
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO SESION_ENTRENAMIENTO 
            (usuario_id, fecha_sesion, tipo_actividad, edad_sesion, duracion_centiminutos, fc_promedio_centesimas)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['usuario_id'], fecha, actividad, edad, duracion_cent, promedio_cent))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('form.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)