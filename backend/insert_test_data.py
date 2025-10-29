# insert_test_data.py - Script para insertar datos de prueba
import pymysql
from datetime import datetime, timedelta
import random

def insert_test_data():
    print("📝 INSERTANDO DATOS DE PRUEBA EN LA BD...")
    
    db_config = {
        'host': 'instancia-iot.c7ewc4b4cf1.us-east-1.rds.amazonaws.com',
        'user': 'administrator',
        'password': 'MgTGA@UXNQ0akkELWS%CdldFXxCqAea7',
        'database': 'iot_system',
        'port': 3306
    }
    
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        # 1. Insertar dispositivos de prueba si no existen
        print("1. Insertando dispositivos...")
        dispositivos = [
            (1, 'Robot Principal', '192.168.1.100', 'México', 'Ciudad de México', -99.1332, 19.4326),
            (2, 'Sensor Exterior', '192.168.1.101', 'México', 'Guadalajara', -103.3496, 20.6597),
            (3, 'Dron Vigilancia', '192.168.1.102', 'México', 'Monterrey', -100.3161, 25.6866)
        ]
        
        for dispositivo in dispositivos:
            cursor.execute("""
                INSERT IGNORE INTO dispositivos 
                (dispositivo_id, nombre, ip_address, país, ciudad, longitud, latitud, fecha_registro) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, dispositivo)
        
        # 2. Insertar movimientos de prueba
        print("2. Insertando movimientos...")
        tipos_movimiento = ['adelante', 'atras', 'izquierda', 'derecha', 'giro_90', 'giro_360', 'detener']
        for i in range(20):
            dispositivo_id = random.randint(1, 3)
            tipo = random.choice(tipos_movimiento)
            fecha = datetime.now() - timedelta(hours=random.randint(0, 24))
            
            cursor.execute("""
                INSERT INTO movimientos 
                (dispositivo_id, tipo_movimiento, fecha_hora) 
                VALUES (%s, %s, %s)
            """, (dispositivo_id, tipo, fecha))
        
        # 3. Insertar obstáculos de prueba
        print("3. Insertando obstáculos...")
        for i in range(10):
            dispositivo_id = random.randint(1, 3)
            distancia = round(random.uniform(10, 150), 2)
            fecha = datetime.now() - timedelta(hours=random.randint(0, 12))
            
            cursor.execute("""
                INSERT INTO obstáculos 
                (dispositivo_id, distancia, fecha_hora) 
                VALUES (%s, %s, %s)
            """, (dispositivo_id, distancia, fecha))
        
        # 4. Insertar ejecuciones de demo
        print("4. Insertando ejecuciones de demo...")
        for i in range(8):
            dispositivo_id = random.randint(1, 3)
            secuencia_id = random.randint(1, 2)
            fecha = datetime.now() - timedelta(hours=random.randint(0, 6))
            
            cursor.execute("""
                INSERT INTO ejecuciones_secuencia 
                (dispositivo_id, secuencia_id, fecha_hora) 
                VALUES (%s, %s, %s)
            """, (dispositivo_id, secuencia_id, fecha))
        
        connection.commit()
        print("✅ DATOS DE PRUEBA INSERTADOS CORRECTAMENTE")
        print("   - 3 dispositivos agregados")
        print("   - 20 movimientos de prueba")
        print("   - 10 detecciones de obstáculos") 
        print("   - 8 ejecuciones de demo")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    insert_test_data()