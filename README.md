# Milestone 2 – Autonomous Navigation and Obstacle Avoidance for RoboDog

---

## 1. Project Description

This project aims to develop an autonomous navigation system for the Unitree Go1 RoboDog in a simulated environment using ROS2 Humble and Gazebo. The main goal is to enable the robot to move from a starting position to a target coordinate while ensuring safe navigation in the presence of obstacles.

The system addresses two fundamental robotics problems:

- Global navigation using coordinate-based goal setting
- Local obstacle avoidance using sensor-based perception

The final objective is to combine both behaviors into a unified autonomous system capable of real-time decision-making in dynamic environments.

---

## 2. Methodology & Execution

The development of this milestone was structured into three main stages:

### Stage 1: Coordinate-Based Navigation

The first implementation focused on enabling the robot to move toward a target coordinate (X, Y) using ROS2 odometry data.

Key components:
- `/odom` topic for robot localization
- `/cmd_vel` for velocity control
- Control loop running at 20Hz
- Angle and distance error computation

The robot aligns itself toward the target and then moves forward while continuously correcting its trajectory.

---

### Stage 2: Reactive Obstacle Avoidance

The second stage introduced perception-based navigation using a depth camera system.

The node `DepthDirectionDetector` processes a depth image and divides it into three regions:

- Left
- Center
- Right

Each region is analyzed by computing the average depth value. A threshold (1.8m) determines whether an obstacle is considered blocking the path.

Behavior rules:
- If center is clear → move forward
- If obstacle detected → choose left or right path
- If no path exists → stop

This implementation provides a reactive local avoidance strategy.

---

### Stage 3: Integrated Navigation + Obstacle Avoidance (MERGED SYSTEM)

The final stage combines global navigation and obstacle avoidance into a single ROS2 node:

📄 `1.1_Go1.py`

This system uses both:
- Odometry-based goal navigation
- LiDAR-based obstacle detection (`/scan` topic)

#### System Architecture

The node subscribes to:
- `/odom` → robot position and orientation
- `/scan` → obstacle detection using LiDAR

And publishes:
- `/cmd_vel` → velocity commands

---

#### Obstacle Detection Strategy

A front cone is extracted from the LiDAR scan (±30 degrees). The system computes:

- Minimum distance in front of the robot
- If distance < 0.8m → obstacle detected

When an obstacle is detected:
- The robot stops forward motion
- Executes a rotation in place (default right turn)
- Searches for a free path

---

#### Go-To-Goal Behavior

When no obstacle is detected, the robot follows a standard navigation pipeline:

1. Compute distance to goal
2. Compute desired yaw angle
3. Align orientation
4. Move forward with proportional speed control

---

#### Control States

The system operates in two states:

**1. Obstacle Mode**
- linear velocity = 0
- angular velocity = fixed turn (-0.4 rad/s)
- robot rotates until path is clear

**2. Navigation Mode**
- align toward goal
- move forward proportional to distance
- continuously correct heading

---

#### Key Parameters

- Safe distance (LiDAR): 0.8 m  
- Distance tolerance: 0.15 m  
- Angle tolerance: 0.08 rad  
- Max linear speed: 0.35 m/s  
- Max angular speed: 0.4 rad/s  

---

### Experimental Results

The integrated system was tested in simulation (`Gazebo`) using multiple scenarios.

The robot successfully:
- Navigated toward target coordinates
- Detected obstacles in real time
- Stopped and reoriented when blocked
- Found alternative paths using reactive turning
- Resumed global navigation after obstacle clearance

---

## 3. Project Team

- Student: Chat (Ciencia de Datos – 5th Semester)
- University: Montanuniversität Leoben

---

## Conclusion

This milestone demonstrates a complete autonomous navigation pipeline combining global goal planning and local obstacle avoidance.

The final merged system successfully integrates perception (LiDAR), localization (odometry), and control (ROS2 velocity commands), achieving real-time decision-making in a simulated robotic environment.
The node publishes movement commands through the `/cmd_vel` topic using `geometry_msgs/Twist`. These commands are then interpreted by the locomotion controller, which converts the linear and angular velocity values into coordinated leg movements for the Unitree Go1.

At the same time, the node subscribes to the `/odom` topic to obtain real-time odometry information, including the robot’s current X position, Y position, and orientation.

Before the robot starts moving, the script waits until odometry data is received. The orientation is received as a quaternion and converted into a yaw angle, allowing the robot to determine its current heading.

The target coordinate is entered manually through the terminal. A separate background thread is used to ask for X and Y coordinates without blocking ROS2 execution. Once valid coordinates are entered, the robot begins the navigation process.

During navigation, the control loop runs every 0.05 seconds (20 Hz). In each cycle, the script calculates:

- The Euclidean distance to the target.
- The desired heading angle.
- The angular error between the current orientation and the target orientation.

The robot follows a two-stage navigation strategy:

1. Rotate in place until aligned with the target.
2. Move forward while continuously correcting its trajectory.

The linear velocity is dynamically adjusted according to the remaining distance to the target, while angular corrections maintain the desired trajectory.

To ensure stable locomotion, safety limits are applied:

- Maximum angular velocity: 0.5 rad/s
- Linear velocity range: 0.1–0.4 m/s

The destination is considered reached when the robot is within 0.1 m of the target coordinate. At that point, the robot stops and waits for a new destination.

## Experimental Results

Several navigation tests were conducted by assigning target coordinates such as (1,1) and (5,1). In each experiment, the RoboDog successfully:

- Calculated the target direction.
- Rotated toward the destination.
- Walked autonomously to the specified coordinate.
- Maintained stable locomotion during movement.
- Stopped once the destination was reached.

The results demonstrated that the navigation architecture and control logic operated correctly within the Gazebo simulation environment.

## Conclusion

Milestone 2 successfully validated autonomous coordinate-based navigation for the Unitree Go1 RoboDog in a simulated environment.

The robot demonstrated the ability to determine its position using odometry, calculate the required heading, align itself with a target location, navigate autonomously, and stop once the goal was reached.

This milestone establishes the foundation required for future development stages involving GPS integration, path planning, and obstacle avoidance.

## Obstacle Avoidance (Stereo Depth-Based Perception)

### Objective

The objective of this module was to implement a reactive obstacle avoidance system using stereo depth perception. Unlike a simple threshold-based controller, this approach interprets depth information from a camera sensor to estimate spatial structure in front of the robot and determine safe movement directions.

### Stereo Camera Model and Depth Interpretation

The system is based on a stereo/depth camera model, where each pixel in the image represents a distance value (depth in meters) instead of RGB color information.

This can be represented conceptually using a camera projection model:

- The stereo camera generates a **depth matrix (D)**:
  
  D(x, y) → distance from the camera to the nearest object at pixel (x, y)

This matrix is the result of stereo disparity estimation or RGB-D sensor fusion, where closer objects have smaller depth values and distant objects have larger values.

### Region-Based Spatial Extraction

To simplify navigation decision-making, the depth matrix is divided into three key spatial regions:

- **Left region** → detects obstacles on the left side of the robot’s field of view
- **Center region** → detects obstacles directly in front
- **Right region** → detects obstacles on the right side

Each region is extracted from a specific portion of the depth matrix:

- Left: left third of the image
- Center: middle section
- Right: right third

Each region is further reduced to a small ROI (Region of Interest) around the horizontal center line to focus on navigation-relevant obstacles.

Mathematically, each region computes:

\[
D_{region} = \frac{1}{N} \sum_{i=1}^{N} D(x_i, y_i)
\]

where invalid values (NaN or infinite depth readings) are removed before averaging.

### Implementation (ROS2 Node)

The obstacle avoidance system is implemented in the ROS2 node `DepthDirectionDetector`, which subscribes to:

- `/camera_face/depth/image_raw` → depth image input

and publishes to:

- `/control_input` → movement commands

The depth image is converted into a NumPy array using `CvBridge`, enabling pixel-level processing.

### Decision-Making Logic

The navigation behavior is fully reactive and based on the following rules:

#### 1. Forward Motion (No Obstacle Ahead)

If the center region distance satisfies:

- `center >= threshold (1.8m)`

then the robot moves forward with constant linear velocity:

- `ly = 0.5`

This represents safe navigation in open space.

#### 2. Obstacle Detected in Front

If the center region is blocked, the system evaluates side regions:

- If left > threshold and right > threshold:
  - choose the direction with more available space
- If only one side is free:
  - turn toward the free side
- If both sides are blocked:
  - stop robot (no valid path)

#### 3. Control Output

The system publishes control signals using a custom message:

- `lx`, `ly` → linear movement
- `rx` → rotation
- `ry` → unused

Turning behavior is defined as:

- `rx = -0.5` → turn left
- `rx = 0.5` → turn right

### Key Parameter (Threshold Calibration)

The system depends heavily on the depth threshold:

- **threshold = 1.8 meters**

This parameter defines how early the robot reacts to obstacles. A smaller threshold makes the robot more aggressive, while a larger one increases safety but reduces maneuverability.

### Experimental Behavior

During testing in simulation:

- The robot successfully detected obstacles using depth segmentation
- It was able to select left/right paths based on available space
- It maintained forward motion in free environments
- It stopped when no valid path was detected

### Limitations and Improvements

This implementation is a **reactive local planner**, meaning it does not compute a global path. As a result, it may fail in complex scenarios such as dead-ends or highly cluttered environments.

Proposed improvements include:

- Dynamic threshold adaptation based on environment density
- Smoother turning using PID control instead of fixed values
- Integration of stereo camera calibration matrix for more accurate depth scaling
- Fusion with global navigation (e.g., Nav2 or A* planning)
- Addition of LiDAR or multi-sensor fusion for robustness
