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

---

# Stage 1: Coordinate-Based Navigation

### Objective
The objective of this stage was to implement a global navigation system where the robot moves autonomously toward a given (X, Y) coordinate using odometry feedback.

### Technical Approach
The system was implemented using a ROS2 node (`go_to_goal_node`) that subscribes to:

- `/odom` → robot pose estimation (position + orientation)

And publishes to:

- `/cmd_vel` → velocity commands for motion control

The robot continuously computes:

- Euclidean distance to the goal
- Desired heading angle using `atan2`
- Angular error between current orientation and target direction

A proportional controller is used for motion:

- First, the robot aligns itself toward the goal
- Then it moves forward while correcting trajectory

### Control Logic
- If misaligned → rotate in place
- If aligned → move forward proportional to distance
- If within tolerance (0.1 m) → stop

### Results
The robot successfully demonstrated:

- Stable localization using odometry
- Accurate target direction estimation
- Smooth rotation toward goals
- Continuous forward navigation without oscillation
- Reliable stopping behavior when reaching the target

This stage validated the feasibility of coordinate-based navigation in Gazebo using ROS2 control loops.

---

# Stage 2: Reactive Obstacle Avoidance

### Objective
This stage introduced local perception-based obstacle avoidance using depth sensing from a camera.

### Technical Approach
The system uses a ROS2 node (`DepthDirectionDetector`) that processes depth images from:

- `/camera_face/depth/image_raw`

The depth image is converted into a NumPy array using `CvBridge` and divided into three regions:

- Left
- Center
- Right

Each region computes an average depth value representing obstacle distance.

### Decision Mechanism
A threshold value of **1.8 meters** is used:

- If center is clear → move forward
- If obstacle detected → choose left or right path
- If both sides blocked → stop

### Control Output
The system publishes commands to `/control_input`:

- `ly` → forward motion
- `rx` → rotation
- `command` → control mode selector

### Results
The system showed the following behaviors:

- Correct detection of obstacles using depth segmentation
- Real-time decision-making between left/right paths
- Successful avoidance of single obstacles
- Safe stopping when no valid path existed
- Stable performance in controlled simulated environments

However, limitations were observed in complex scenarios such as tight corridors or multiple consecutive obstacles, where local decisions could lead to suboptimal paths.

---

# Stage 3: Integrated Navigation + Obstacle Avoidance (MERGED SYSTEM)

### Objective
The final stage integrates global navigation and obstacle avoidance into a unified autonomous control system capable of dynamic decision-making.

### Implementation
The merged system is implemented in:

 `MergeGo1.py`

This node extends the previous navigation logic by adding LiDAR-based obstacle detection using:

- `/scan` topic (LaserScan)

### System Architecture

The node operates with two sensory inputs:

- `/odom` → robot localization
- `/scan` → obstacle detection

And one output:

- `/cmd_vel` → motion commands

### Obstacle Detection Strategy

A front cone of the LiDAR scan is analyzed (±30 degrees from center).

The system computes:

- Minimum valid distance in front of the robot

If:

- distance < 0.8 m → obstacle detected

### Behavior Switching Logic

The system dynamically switches between two states:

---

### 1. Obstacle Avoidance Mode

When an obstacle is detected:

- linear velocity = 0
- robot rotates in place (`angular.z = -0.4`)
- robot searches for free space

This ensures immediate reaction to prevent collision.

---

### 2. Goal Navigation Mode

When path is clear:

- Compute desired yaw angle toward target
- Align orientation first
- Move forward proportional to distance
- Continuously correct heading

### Control Strategy
- Proportional controller for angular correction
- Distance-based speed scaling
- Safety-limited velocity constraints

---

### Results

The integrated system demonstrated strong performance in simulation:

- Successful navigation to target coordinates
- Real-time detection of obstacles using LiDAR
- Immediate avoidance behavior upon obstacle detection
- Smooth recovery and continuation of global navigation
- Stable transitions between navigation and avoidance states

The system effectively behaves as a **reactive hybrid navigation system**, combining global planning and local obstacle avoidance.

---

## 3. Project Team

- Student: Chat (Ciencia de Datos – 5th Semester)
- University: Montanuniversität Leoben

---

## Conclusion

This project successfully implemented a complete autonomous navigation pipeline for a simulated quadruped robot using ROS2 and Gazebo.

The system evolved through three progressive stages:

1. Global coordinate-based navigation
2. Reactive depth-based obstacle avoidance
3. Fully integrated hybrid navigation system

The final architecture demonstrates that combining odometry-based control with real-time sensor feedback enables robust autonomous behavior in dynamic environments.

The RoboDog was able to:

- Interpret and navigate toward spatial coordinates
- Detect and avoid obstacles using perception systems
- Dynamically switch between behavioral states
- Maintain stability during motion execution

This milestone establishes a solid foundation for future improvements, including global path planning (Nav2), SLAM integration, sensor fusion, and more advanced decision-making strategies for fully autonomous robotic navigation.
