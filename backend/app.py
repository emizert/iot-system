from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import sys

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = 'iot_exam_secret_aws'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# 📍 Configuración SQLite para AWS
DB_PATH = '/home/ubuntu/iot_system.db'

def init_database():
    """Inicializar base de datos SQLite en AWS"""
    if not os.path.exists(DB_PATH):
        print("📀 Creando base de datos en AWS...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Crear tablas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dispositivos (
                dispositivo_id INTEGER PRIMARY KEY,
                nombre TEXT,
                ip_address TEXT,
                pais TEXT,
                ciudad TEXT,
                longitud REAL,
                latitud REAL,
                fecha_registro TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimientos (
                movimiento_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dispositivo_id INTEGER,
                tipo_movimiento TEXT,
                fecha_hora TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS obstaculos (
                obstaculo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dispositivo_id INTEGER,
                distancia REAL,
                fecha_hora TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ejecuciones_secuencia (
                ejecucion_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dispositivo_id INTEGER,
                secuencia_id INTEGER,
                fecha_hora TEXT
            )
        ''')
        
        # Insertar dispositivo principal
        dispositivos = [
            (1, 'Robot IoT Principal', '192.168.1.100', 'México', 'CDMX', -99.1332, 19.4326, datetime.now().isoformat())
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO dispositivos VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', dispositivos)
        
        conn.commit()
        conn.close()
        print("✅ Base de datos AWS creada")

def get_db_connection():
    """Obtener conexión a SQLite en AWS"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Error conectando a BD AWS: {e}")
        return None

# MODELOS (igual que antes)
class DispositivoModel:
    @staticmethod
    def obtener_dispositivos():
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dispositivos")
            return cursor.fetchall()
        except Exception as e:
            print("Error obteniendo dispositivos:", e)
            return []
        finally:
            conn.close()

    @staticmethod
    def contar_movimientos():
        conn = get_db_connection()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM movimientos")
            return cursor.fetchone()[0]
        except Exception as e:
            print("Error contando movimientos:", e)
            return 0
        finally:
            conn.close()

    @staticmethod
    def contar_obstaculos():
        conn = get_db_connection()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM obstaculos")
            return cursor.fetchone()[0]
        except Exception as e:
            print("Error contando obstáculos:", e)
            return 0
        finally:
            conn.close()

    @staticmethod
    def contar_demos():
        conn = get_db_connection()
        if not conn:
            return 0
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ejecuciones_secuencia")
            return cursor.fetchone()[0]
        except Exception as e:
            print("Error contando demos:", e)
            return 0
        finally:
            conn.close()

    @staticmethod
    def registrar_movimiento(dispositivo_id, tipo_movimiento):
        conn = get_db_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO movimientos (dispositivo_id, tipo_movimiento, fecha_hora) VALUES (?, ?, ?)",
                (dispositivo_id, tipo_movimiento, datetime.now().isoformat())
            )
            conn.commit()
            print(f"✅ Movimiento registrado: {tipo_movimiento}")
            return True
        except Exception as e:
            print("Error registrando movimiento:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def registrar_obstaculo(dispositivo_id, distancia):
        conn = get_db_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO obstaculos (dispositivo_id, distancia, fecha_hora) VALUES (?, ?, ?)",
                (dispositivo_id, distancia, datetime.now().isoformat())
            )
            conn.commit()
            print(f"✅ Obstáculo registrado: {distancia}cm")
            return True
        except Exception as e:
            print("Error registrando obstáculo:", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def ejecutar_secuencia_demo(dispositivo_id, secuencia_id):
        conn = get_db_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ejecuciones_secuencia (dispositivo_id, secuencia_id, fecha_hora) VALUES (?, ?, ?)",
                (dispositivo_id, secuencia_id, datetime.now().isoformat())
            )
            conn.commit()
            print(f"✅ Demo ejecutada: Secuencia {secuencia_id}")
            return True
        except Exception as e:
            print("Error ejecutando demo:", e)
            return False
        finally:
            conn.close()

# RUTAS PARA SERVIR ARCHIVOS ESTÁTICOS
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# 📍 ENDPOINTS API DOCUMENTADOS
@app.route('/api/status', methods=['GET'])
def api_status():
    """
    🔍 Endpoint: Estado del Servidor
    Método: GET
    Descripción: Verifica que el servidor esté funcionando
    Respuesta: JSON con estado del sistema
    """
    return jsonify({
        "message": "✅ Servidor IoT Flask en AWS funcionando!", 
        "status": "active",
        "puerto": 5500,
        "websockets": "activos",
        "bd": "SQLite en AWS",
        "ubicacion": "AWS EC2"
    })

@app.route('/api/dispositivos', methods=['GET'])
def obtener_dispositivos():
    """
    🔍 Endpoint: Obtener Dispositivos
    Método: GET
    Descripción: Retorna lista de dispositivos IoT registrados
    Respuesta: JSON array con dispositivos
    """
    try:
        dispositivos = DispositivoModel.obtener_dispositivos()
        resultado = []
        for d in dispositivos:
            resultado.append({
                'dispositivo_id': d[0],
                'nombre': d[1],
                'ip_address': d[2],
                'pais': d[3],
                'ciudad': d[4],
                'longitud': d[5],
                'latitud': d[6]
            })
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """
    🔍 Endpoint: Estadísticas del Sistema
    Método: GET
    Descripción: Retorna estadísticas generales del sistema
    Respuesta: JSON con contadores
    """
    try:
        estadisticas = {
            'total_dispositivos': len(DispositivoModel.obtener_dispositivos()),
            'total_movimientos': DispositivoModel.contar_movimientos(),
            'total_obstaculos': DispositivoModel.contar_obstaculos(),
            'total_demos': DispositivoModel.contar_demos()
        }
        return jsonify(estadisticas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/control/movimiento', methods=['POST'])
def control_movimiento():
    """
    🎮 Endpoint: Control de Movimiento
    Método: POST
    Descripción: Ejecuta movimiento del dispositivo IoT
    Body: {"dispositivo_id": 1, "tipo_movimiento": "adelante"}
    Movimientos válidos: adelante, atras, izquierda, derecha, giro_90, giro_360, detener
    """
    data = request.json
    dispositivo_id = data.get('dispositivo_id', 1)
    tipo_movimiento = data.get('tipo_movimiento', 'adelante')
    
    success = DispositivoModel.registrar_movimiento(dispositivo_id, tipo_movimiento)
    
    if success:
        datos_evento = {
            'dispositivo_id': dispositivo_id,
            'tipo_movimiento': tipo_movimiento,
            'timestamp': datetime.now().isoformat()
        }
        socketio.emit('movimiento_controlado', datos_evento)
        print(f"📢 Evento WebSocket: movimiento_controlado - {tipo_movimiento}")
    
    return jsonify({
        "status": "success" if success else "error", 
        "comando": tipo_movimiento,
        "dispositivo": dispositivo_id
    })

@app.route('/api/control/obstaculo', methods=['POST'])
def control_obstaculo():
    """
    🎮 Endpoint: Detección de Obstáculos
    Método: POST
    Descripción: Registra detección de obstáculo
    Body: {"dispositivo_id": 1, "distancia": 50.5}
    """
    data = request.json
    dispositivo_id = data.get('dispositivo_id', 1)
    distancia = data.get('distancia', 50.0)
    
    success = DispositivoModel.registrar_obstaculo(dispositivo_id, distancia)
    
    if success:
        datos_evento = {
            'dispositivo_id': dispositivo_id,
            'distancia': distancia,
            'timestamp': datetime.now().isoformat()
        }
        socketio.emit('obstaculo_detectado', datos_evento)
        print(f"📢 Evento WebSocket: obstaculo_detectado - {distancia}cm")
    
    return jsonify({
        "status": "success" if success else "error", 
        "distancia": distancia,
        "dispositivo": dispositivo_id
    })

@app.route('/api/control/demo', methods=['POST'])
def control_demo():
    """
    🎮 Endpoint: Ejecutar Secuencia Demo
    Método: POST
    Descripción: Ejecuta secuencia demo del dispositivo
    Body: {"dispositivo_id": 1, "secuencia_id": 1}
    Secuencias: 1 (Demo Básica), 2 (Demo Avanzada)
    """
    data = request.json
    dispositivo_id = data.get('dispositivo_id', 1)
    secuencia_id = data.get('secuencia_id', 1)
    
    success = DispositivoModel.ejecutar_secuencia_demo(dispositivo_id, secuencia_id)
    
    if success:
        datos_evento = {
            'dispositivo_id': dispositivo_id,
            'secuencia_id': secuencia_id,
            'timestamp': datetime.now().isoformat()
        }
        socketio.emit('demo_ejecutada', datos_evento)
        print(f"📢 Evento WebSocket: demo_ejecutada - Secuencia {secuencia_id}")
    
    return jsonify({
        "status": "success" if success else "error", 
        "secuencia": secuencia_id,
        "dispositivo": dispositivo_id
    })

# WEBSOCKETS
@socketio.on('connect')
def handle_connect():
    print('✅ Cliente WebSocket conectado:', request.sid)
    emit('connection_status', {'status': 'connected', 'message': 'Conectado a AWS'})

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Cliente WebSocket desconectado:', request.sid)

if __name__ == '__main__':
    # Inicializar base de datos en AWS
    init_database()
    
    print("=" * 70)
    print("🚀 SISTEMA IoT - EXAMEN TEMA 2 - DEPLOYMENT AWS")
    print("📡 Backend: Flask + WebSockets - Puerto 5500")
    print("🌐 Frontend: Bootstrap + JavaScript")
    print("🗄️  Base de datos: SQLite en AWS")
    print("⚡ Comunicación: WebSockets en tiempo real")
    print("=" * 70)
    print("📍 URLs Públicas:")
    print("   Control: http://TU-IP-AWS:5500/control.html")
    print("   Monitoreo: http://TU-IP-AWS:5500/monitoreo.html")
    print("   API Status: http://TU-IP-AWS:5500/api/status")
    print("=" * 70)
    
    # Ejecutar en modo producción para AWS
    socketio.run(app, host='0.0.0.0', port=5500, debug=False)