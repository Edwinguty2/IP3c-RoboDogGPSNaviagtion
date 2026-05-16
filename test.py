from flask import Flask, request
import threading
import time

app = Flask(__name__)

last_received_time = 0
current_coords = {"lat": None, "lon": None}
# Nueva variable para el destino final
final_destination = {"lat": None, "lon": None}

@app.route('/gps', methods=['GET', 'POST'])
def receive_gps():
    global last_received_time, current_coords
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if lat and lon:
        current_coords["lat"] = lat
        current_coords["lon"] = lon
        last_received_time = time.time()
        print(f" [GPS Update] Lat: {lat} | Lon: {lon}")
        return "GPS OK", 200
    return "Error: Missing lat or lon", 400

@app.route('/finaldestination', methods=['GET', 'POST'])
def set_final_destination():
    global final_destination
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if lat and lon:
        final_destination["lat"] = lat
        final_destination["lon"] = lon
        print(f" 🚩 [DESTINATION SET] Target Lat: {lat} | Target Lon: {lon}")
        return "Destination Set OK", 200
    return "Error: Missing destination parameters", 400

def connection_monitor():
    while True:
        if last_received_time != 0 and (time.time() - last_received_time) > 5:
            print(" [Disconnected] Connection lost")
        elif last_received_time == 0:
            print(" Waiting for signal...")
        time.sleep(5)

if __name__ == '__main__':
    monitor_thread = threading.Thread(target=connection_monitor, daemon=True)
    monitor_thread.start()
    # Ejecutamos en el puerto 5000 (o 5001 si el 5000 te da caracteres raros)
    app.run(host='0.0.0.0', port=5000)