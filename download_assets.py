import urllib.request
import os

print("Descargando Chart.js localmente para cumplir RNF05 (funcionamiento offline)...")
os.makedirs('static', exist_ok=True)
try:
    urllib.request.urlretrieve('https://cdn.jsdelivr.net/npm/chart.js', 'static/chart.js')
    print("¡Descarga completada! El prototipo ya puede operar sin conexión a internet.")
except Exception as e:
    print(f"Error descargando: {e}")
