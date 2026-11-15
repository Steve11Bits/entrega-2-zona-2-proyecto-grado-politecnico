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

## ⚙️ Instalación y Configuración Local

Sigue estos pasos para ejecutar el proyecto en tu entorno local (Windows / Linux / WSL):

### 1. Clonar o descomprimir el proyecto
Ubícate en la carpeta raíz del proyecto (`zona2_project_v2`).

### 2. Crear y activar un entorno virtual
Se recomienda aislar las dependencias del proyecto usando `venv`:

**En Windows (CMD/PowerShell):**
```cmd
python -m venv venv
venv\Scripts\activate
