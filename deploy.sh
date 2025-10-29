#!/bin/bash
echo "🚀 DEPLOYMENT SISTEMA IoT - AWS EC2"

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y dependencias
sudo apt install python3-pip python3-venv -y

# Crear directorio de la aplicación
mkdir -p /home/ubuntu/iot-system
cd /home/ubuntu/iot-system

# Crear entorno virtual
python3 -m venv iot-env
source iot-env/bin/activate

# Instalar dependencias Python
pip install flask flask-socketio flask-cors

# Crear estructura de carpetas
mkdir -p backend frontend

# Los archivos app.py, control.html, monitoreo.html se copian manualmente

# Configurar servicio systemd
sudo tee /etc/systemd/system/iot-server.service > /dev/null <<EOF
[Unit]
Description=IoT Server - Examen Tema 2
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/iot-system
Environment=PATH=/home/ubuntu/iot-system/iot-env/bin
ExecStart=/home/ubuntu/iot-system/iot-env/bin/python3 backend/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Recargar y habilitar servicio
sudo systemctl daemon-reload
sudo systemctl enable iot-server.service

echo "✅ Deployment configurado en AWS"
echo "📝 Comandos útiles:"
echo "   sudo systemctl start iot-server    # Iniciar servicio"
echo "   sudo systemctl stop iot-server     # Detener servicio"
echo "   sudo systemctl status iot-server   # Ver estado"
echo "   journalctl -u iot-server -f       # Ver logs en tiempo real"