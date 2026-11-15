from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_poli_2026_v2'

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

def calcular_clasificacion(edad, promedio_cent):
    M = 220 - edad
    L100 = 60 * M
    U100 = 70 * M
    if promedio_cent < L100: return 'Inferior', L100, U100, M
    elif promedio_cent > U100: return 'Superior', L100, U100, M
    return 'Dentro', L100, U100, M

@app.route('/')
def index():
    if 'usuario_id' in session: return redirect(url_for('dashboard'))
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
            flash('Cuenta creada. Inicia sesión.')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('El usuario ya existe.')
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
    flash('Credenciales incorrectas.')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session: return redirect(url_for('index'))
    
    desde = request.args.get('desde', '')
    hasta = request.args.get('hasta', '')
    actividad = request.args.get('actividad', 'Todas')
    
    query = "SELECT * FROM SESION_ENTRENAMIENTO WHERE usuario_id = ?"
    params = [session['usuario_id']]
    
    if desde:
        query += " AND fecha_sesion >= ?"
        params.append(desde)
    if hasta:
        query += " AND fecha_sesion <= ?"
        params.append(hasta)
    if actividad != 'Todas':
        query += " AND tipo_actividad = ?"
        params.append(actividad)
        
    query += " ORDER BY fecha_sesion DESC, sesion_id DESC"
    
    conn = get_db_connection()
    sesiones = conn.execute(query, params).fetchall()
    conn.close()
    
    datos = []
    for s in sesiones:
        clasif, L100, U100, M = calcular_clasificacion(s['edad_sesion'], s['fc_promedio_centesimas'])
        datos.append({
            'id': s['sesion_id'], 'fecha': s['fecha_sesion'], 'actividad': s['tipo_actividad'],
            'minutos': s['duracion_centiminutos'] / 100, 'promedio': s['fc_promedio_centesimas'] / 100,
            'lim_inf': L100 / 100, 'lim_sup': U100 / 100, 'clasificacion': clasif
        })
    return render_template('dashboard.html', sesiones=datos, usuario=session['nombre_usuario'], 
                           desde=desde, hasta=hasta, actividad=actividad)

@app.route('/daily_summary')
def daily_summary():
    if 'usuario_id' not in session: return redirect(url_for('index'))
    # Filtros idénticos al dashboard
    desde = request.args.get('desde', '')
    hasta = request.args.get('hasta', '')
    actividad = request.args.get('actividad', 'Todas')
    
    query = "SELECT fecha_sesion, COUNT(sesion_id) as cant, SUM(duracion_centiminutos) as total_cent FROM SESION_ENTRENAMIENTO WHERE usuario_id = ?"
    params = [session['usuario_id']]
    if desde: query += " AND fecha_sesion >= ?"; params.append(desde)
    if hasta: query += " AND fecha_sesion <= ?"; params.append(hasta)
    if actividad != 'Todas': query += " AND tipo_actividad = ?"; params.append(actividad)
    query += " GROUP BY fecha_sesion ORDER BY fecha_sesion DESC"
    
    conn = get_db_connection()
    resumen = conn.execute(query, params).fetchall()
    conn.close()
    
    datos = [{'fecha': r['fecha_sesion'], 'cantidad': r['cant'], 'minutos': r['total_cent']/100} for r in resumen]
    return render_template('daily.html', resumen=datos, usuario=session['nombre_usuario'])

@app.route('/session/<int:id>', methods=('GET', 'POST'))
def session_detail(id):
    if 'usuario_id' not in session: return redirect(url_for('index'))
    conn = get_db_connection()
    s = conn.execute('SELECT * FROM SESION_ENTRENAMIENTO WHERE sesion_id = ? AND usuario_id = ?', (id, session['usuario_id'])).fetchone()
    
    if not s:
        conn.close()
        flash('Registro no disponible o no tienes permisos.')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST': # Eliminar
        conn.execute('DELETE FROM SESION_ENTRENAMIENTO WHERE sesion_id = ?', (id,))
        conn.commit()
        conn.close()
        flash('Sesión eliminada correctamente.')
        return redirect(url_for('dashboard'))
        
    conn.close()
    clasif, L100, U100, M = calcular_clasificacion(s['edad_sesion'], s['fc_promedio_centesimas'])
    detalle = {
        'id': s['sesion_id'], 'fecha': s['fecha_sesion'], 'actividad': s['tipo_actividad'], 'edad': s['edad_sesion'],
        'minutos': s['duracion_centiminutos']/100, 'promedio': s['fc_promedio_centesimas']/100,
        'maxima': M, 'lim_inf': L100/100, 'lim_sup': U100/100, 'clasificacion': clasif
    }
    return render_template('detail.html', s=detalle)

@app.route('/edit_session/<int:id>', methods=('GET', 'POST'))
def edit_session(id):
    if 'usuario_id' not in session: return redirect(url_for('index'))
    conn = get_db_connection()
    s = conn.execute('SELECT * FROM SESION_ENTRENAMIENTO WHERE sesion_id = ? AND usuario_id = ?', (id, session['usuario_id'])).fetchone()
    if not s:
        conn.close()
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        fecha = request.form['fecha']
        actividad = request.form['actividad']
        edad = int(request.form['edad'])
        dur = int(float(request.form['duracion']) * 100)
        prom = int(float(request.form['promedio']) * 100)
        conn.execute('''UPDATE SESION_ENTRENAMIENTO SET fecha_sesion=?, tipo_actividad=?, edad_sesion=?, 
                        duracion_centiminutos=?, fc_promedio_centesimas=?, actualizado_en=CURRENT_TIMESTAMP 
                        WHERE sesion_id=?''', (fecha, actividad, edad, dur, prom, id))
        conn.commit()
        conn.close()
        return redirect(url_for('session_detail', id=id))
        
    conn.close()
    data = dict(s)
    data['duracion'] = data['duracion_centiminutos']/100
    data['promedio'] = data['fc_promedio_centesimas']/100
    return render_template('form.html', s=data)

@app.route('/add_session', methods=('GET', 'POST'))
def add_session():
    if 'usuario_id' not in session: return redirect(url_for('index'))
    if request.method == 'POST':
        fecha = request.form['fecha']
        actividad = request.form['actividad']
        edad = int(request.form['edad'])
        dur = int(float(request.form['duracion']) * 100)
        prom = int(float(request.form['promedio']) * 100)
        conn = get_db_connection()
        conn.execute('''INSERT INTO SESION_ENTRENAMIENTO (usuario_id, fecha_sesion, tipo_actividad, edad_sesion, duracion_centiminutos, fc_promedio_centesimas)
                        VALUES (?, ?, ?, ?, ?, ?)''', (session['usuario_id'], fecha, actividad, edad, dur, prom))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('form.html', s=None)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
