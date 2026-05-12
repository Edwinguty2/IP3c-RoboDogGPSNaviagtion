from flask import Flask, request
import threading
import time

app = Flask(__name__)

last_received_time = 0
current_coords = {"lat": None, "lon": None}

@app.route('/gps', methods=['GET', 'POST'])
def receive_gps():
    global last_received_time, current_coords
    
    # Intentamos obtener 'lat' y 'lon' de la URL
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if lat and lon:
        current_coords["lat"] = lat
        current_coords["lon"] = lon
        last_received_time = time.time()
        print(f" [Received] Lat: {lat} | Lon: {lon}")
        return "OK", 200
    else:
        # Esto te ayudará a ver qué está llegando realmente
        print(" [ERROR 400] parameters missing.")
        print(f"Diccionary received: {dict(request.args)}")
        return "Error, you need to use lat and lot", 400

def connection_monitor():
    while True:
        if last_received_time != 0 and (time.time() - last_received_time) > 5:
            print(" [Disconnected] Connection lost")
        elif last_received_time == 0:
            print("⏳ Waiting for a signal...")
        time.sleep(5)

if __name__ == '__main__':
    monitor_thread = threading.Thread(target=connection_monitor, daemon=True)
    monitor_thread.start()
    app.run(host='0.0.0.0', port=5000)