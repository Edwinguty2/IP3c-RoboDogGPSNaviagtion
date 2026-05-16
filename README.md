# Unitree Go1 GPS Navigation System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Framework](https://img.shields.io/badge/robotics-ROS%20/%20IoT-orange.svg)](https://www.unitree.com/go1/)

## Description
This project implements a lightweight **RESTful API server** built with Flask to manage and monitor the geographic navigation of a **Unitree Go1** quadruped robot in real-time. 

The system acts as a communication bridge, allowing the robot to constantly report its current GPS position via a companion mobile application, while simultaneously exposing an interface to receive target coordinates for autonomous movement.

### Features & Background
* **Asynchronous Connection Monitoring:** Uses Python threading to track the health of the incoming data stream and detect signal losses under 5 seconds.
* **Dual-Endpoint Architecture:** Separates the telemetry stream (incoming GPS) from the mission control directives (final destination setup).
* **Hardware-Optimized:** Designed as a low-overhead micro-service suitable for the internal computational constraints of edge-robotics platforms.

---

## Repository Branches

This repository is divided into different branches to separate stable deployment code, active development, and project documentation.

- **`main`**  
  Contains the stable version currently deployed and running on the **Unitree Go1** robot.

- **`development`**  
  Used for testing new features, debugging, and experimenting with navigation and robotics integrations before merging into `main`.

- **`documentation`**  
  Stores project-related resources such as meeting notes, research material, presentations, reports, and technical documentation.

---

## Visuals

[Waiting for signal...] -> [GPS Update] Lat: X | Lon: Y
[DESTINATION SET] 🚩 -> Target Lat: A | Target Lon: B

--

## Requirements & Installation

### Requirements
* **Operating System:** Linux (Ubuntu 18.04/20.04 recommended for Unitree environments).
* **Python Version:** Python 3.8 or higher (Avoid running with standard Python 2.7 aliases).
* **Network:** Both the server running on the robot and the client app must share the same **Local Access Point / Hotspot**.

### Installation Steps

1. Clone this repository to your Unitree Go1 system or local testing machine:
   ```bash
   git clone [https://github.com/your-username/go1-gps-navigation.git](https://github.com/your-username/go1-gps-navigation.git)
   cd go1-gps-navigation
2. Install the minimal required dependencies using pip:
   ```bash
   pip3 install flask

---

## Usage

To start the navigation server, connect via SSH to your host/robot and execute the script using Python 3:

```bash
python3 gps_server.py
```

---

## API Endpoints (RESTful Interface)

### 1. Track Robot Current GPS

Updates the server with the current coordinates gathered from the app's GPS module.

- **URL:** `/gps`
- **Method:** `GET / POST`
- **Parameters:** `lat (float)`, `lon (float)`

#### Example Request

```http
http://192.168.12.22:5000/gps?lat=47.3841&lon=15.0924
```

---

### 2. Set Final Destination

Configures the target coordinate towards which the robot should navigate.

- **URL:** `/finaldestination`
- **Method:** `GET / POST`
- **Parameters:** `lat (float)`, `lon (float)`

#### Example Request

```http
http://192.168.12.22:5000/finaldestination?lat=47.3855&lon=15.0940
```

---

## Project Status

### Current State

**Active Development (MVP)**

### Working

The telemetry communication path is fully functional. The robot successfully parses live GPS updates from the app and safely registers mission target coordinates via concurrency-safe threading logs.

---

## Roadmap

- [x] Implement Flask baseline architecture.
- [x] Integrate multi-threaded connection monitoring watchdog.
- [x] Add `/finaldestination` route handlers.
- [ ] Implement data locks (`threading.Lock`) to prevent race conditions during heavy hardware polling.
- [ ] Bind parsed coordinates directly into the Unitree ROS/LCM locomotion nodes to trigger physical movement.

---

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create.

1. Fork the project.
2. Create your feature branch:

```bash
git checkout -b feature
```

3. Commit your changes:

```bash
git commit -m "Add some AmazingFeature"
```

4. Push to the branch:

```bash
git push origin -u feature 
```

5. Open a Pull Request.

> **Note:** Please make sure to test changes locally via `curl` to avoid breaking raw HTTP string serializations.

---

## Support

If you encounter issues with deployment, port conflicts, or malformed URL parameters (`Error 400`), please open an issue in the project's GitHub tracker or contact the maintainers directly.

---

## Author

**Abdullah Khaled Ali El-Hiari**  
**Edwin Alejandro Gutiérrez Rodríguez**  
**Joel Sebastian Montenegro Gonzalez**  
