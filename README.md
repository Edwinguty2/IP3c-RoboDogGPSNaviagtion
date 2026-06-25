# Development – RoboDog Navigation System

## Overview

This folder contains the core Python implementations of the RoboDog autonomous navigation system, including:

- Coordinate-based navigation
- Obstacle detection and avoidance
- System integration (merged behavior)

---

## Files Description

### 1. Direction_Detector.py
Implements obstacle detection using depth perception / sensor-based logic.  
It processes environmental data and determines safe movement directions.

---

### 2. Go_to_coordinate.py
Implements global navigation using ROS2 odometry.  
The robot calculates distance and orientation toward a target coordinate (X, Y) and moves autonomously using a control loop.

---

### 3. MergeGo1.py
This is the integrated system combining:
- Goal-based navigation
- Obstacle avoidance

The robot dynamically switches between:
- navigation mode (go-to-goal)
- avoidance mode (reactive obstacle response)

This represents the final behavior of the system.

---

### 4. Test.py
Used for debugging and testing individual components of the system.
