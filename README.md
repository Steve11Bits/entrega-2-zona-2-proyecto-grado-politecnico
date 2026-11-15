# Zona 2 Tracker - Plataforma de Seguimiento Aeróbico

Plataforma web desarrollada en **Python (Flask)** y **SQLite** para el registro, consulta y análisis de sesiones de entrenamiento aeróbico (trote y caminata). 

El sistema clasifica la frecuencia cardíaca promedio de cada sesión comparándola con una referencia teórica de Zona 2 (60% - 70% de la frecuencia cardíaca máxima estimada por edad), manteniendo un historial seguro por usuario. Proyecto desarrollado para la Institución Universitaria Politécnico Grancolombiano.

## 🚀 Características Principales

- **Gestión de Usuarios (UI01):** Autenticación y registro con contraseñas seguras usando hash (`Werkzeug`).
- **CRUD de Sesiones (UI02, UI05):** Creación, lectura, corrección y eliminación (con confirmación) de sesiones de entrenamiento.
- **Precisión Numérica:** Los datos de frecuencia y duración se calculan y persisten en la base de datos en formato de centésimas (multiplicados por 100) para evitar errores de redondeo en punto flotante durante la clasificación.
- **Dashboard y Filtros (UI03):** Gráfica interactiva del historial de promedios vs límites de la Zona 2 utilizando **Chart.js**. Filtros por fecha (desde/hasta) y tipo de actividad.
- **Resumen Diario (UI04):** Totalización de minutos y conteo de sesiones por día, agrupados de forma estricta sin promediar pulsaciones de actividades inconexas.
- **Funcionamiento Offline (RNF05):** Las librerías de frontend (Chart.js) se alojan de forma local para garantizar el funcionamiento sin dependencia de CDNs.

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.x, Flask 3.0.0, Werkzeug
- **Base de Datos:** SQLite3 (Motor relacional local)
- **Frontend:** HTML5, CSS3 (Vanilla - Dark/Yellow Theme), Vanilla JavaScript
- **Gráficas:** Chart.js

## ⚙️ Guía de Instalación y Ejecución Local

Profesor, a continuación detallo los pasos necesarios para que pueda ejecutar y evaluar el proyecto en su entorno local (Windows / Linux / Mac):

### 1. Preparar el directorio
ubique su terminal en la carpeta raíz del proyecto (`zona2_project_v2`).

### 2. Crear y activar el entorno virtual
Para evitar conflictos con otras librerías de su sistema, se recomienda aislar las dependencias usando `venv`:

**En Windows (CMD/PowerShell):**
```cmd
python -m venv venv
venv\Scripts\activate
```
*(Nota: Si su instalación de Python utiliza MSYS2 o generó una estructura tipo Linux, el comando de activación será `venv\bin\activate.bat`)*.

**En Linux / Mac / WSL:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias
Una vez activado el entorno, por favor ejecute el siguiente comando para instalar Flask y Werkzeug:
```bash
pip install -r requirements.txt
```

### 4. Descargar recursos locales (Cumplimiento de RNF05)
Para asegurar que la plataforma y la renderización de las gráficas operen correctamente sin requerir conexión a internet, preparé un script que descarga la dependencia estática. Por favor, ejecútelo:
```bash
python download_assets.py
```
*(Este script descargará automáticamente la librería `chart.js` y la ubicará en la carpeta `/static`)*.

### 5. Iniciar la aplicación
Finalmente, puede levantar el servidor local con el siguiente comando:
```bash
python app.py
```
El servidor iniciará en el puerto 5000. Ya puede abrir su navegador de preferencia e ingresar a: **`http://127.0.0.1:5000`**

*(Nota técnica: La base de datos `zona2.db` y sus respectivas tablas se generarán automáticamente durante el primer arranque de la aplicación, gracias a la función de inicialización integrada `init_db()`)*.

## 🔒 Seguridad y Arquitectura

- **Rutas Protegidas:** El sistema valida la propiedad de cada registro cruzando la información con el `usuario_id` extraído directamente de la sesión activa del servidor, evitando que se puedan consultar o modificar datos ajenos manipulando los parámetros de la URL.
- **Consultas Parametrizadas:** Toda interacción con la base de datos SQLite se realiza a través de consultas con parámetros seguros para prevenir inyecciones SQL.
- **Validación de Integridad:** Se habilitó explícitamente el control de llaves foráneas (`PRAGMA foreign_keys = ON`) a nivel de SQLite para garantizar la integridad referencial de los datos.
