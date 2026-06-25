#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import sys
import threading

class GoToGoalNode(Node):
    def __init__(self):
        super().__init__('go_to_goal_node')
        
        # Publisher to control robot movement (intercepted by junior_ctrl)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Subscription to get real-time position and orientation
        self.subscription = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        
        # Current robot state variables
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        self.odom_received = False
        
        # Target coordinate variables
        self.target_x = None
        self.target_y = None
        self.goal_active = False

        # Acceptance thresholds (tolerances)
        self.distance_tolerance = 0.1  # 10 centimeters
        self.angle_tolerance = 0.05    # Roughly 3 degrees

        # Start a background thread to handle console input without blocking ROS2 execution
        self.input_thread = threading.Thread(target=self.ask_for_coordinates, daemon=True)
        self.input_thread.start()

        # Timer to run the control loop at 20Hz (every 0.05 seconds)
        self.create_timer(0.05, self.control_loop)
        self.get_logger().info("Go-to-Goal node initialized. Waiting for odometry data...")

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        self.odom_received = True
        
        # Convert quaternion to yaw angle to determine the robot's heading
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

    def ask_for_coordinates(self):
        while rclpy.ok():
            if not self.goal_active:
                try:
                    self.get_logger().info("\n--- WAITING FOR NEW TARGET COORDINATE ---")
                    x_input = input("Enter target X coordinate: ")
                    y_input = input("Enter target Y coordinate: ")
                    
                    self.target_x = float(x_input)
                    self.target_y = float(y_input)
                    self.goal_active = True
                    self.get_logger().info(f"Navigating to target coordinate: X={self.target_x}, Y={self.target_y}")
                except ValueError:
                    self.get_logger().error("Invalid input. Please enter valid numerical values.")

    def control_loop(self):
        if not self.odom_received or not self.goal_active:
            return

        # 1. Calculate Euclidean distance to the target goal
        distance_to_goal = math.hypot(self.target_x - self.current_x, self.target_y - self.current_y)
        
        # 2. Calculate target heading (angle to the goal)
        desired_yaw = math.atan2(self.target_y - self.current_y, self.target_x - self.current_x)
        
        # Calculate steering error and normalize it between -PI and PI
        angle_error = desired_yaw - self.current_yaw
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

        twist_msg = Twist()

        # Stop condition: Has the robot reached the target location?
        if distance_to_goal < self.distance_tolerance:
            twist_msg.linear.x = 0.0
            twist_msg.angular.z = 0.0
            self.publisher_.publish(twist_msg)
            self.get_logger().info(f"Goal successfully reached! Current position: X={self.current_x:.2f}, Y={self.current_y:.2f}")
            self.goal_active = False  # Release loop to accept a new coordinate
            return

        # 3. Control state logic: Align heading first, then move forward while correcting course
        if abs(angle_error) > self.angle_tolerance:
            # If severely misaligned, stop linear movement and rotate in place
            twist_msg.linear.x = 0.0
            twist_msg.angular.z = 1.2 * angle_error  # Proportional controller gain (P)
            # Limit maximum rotational speed for safety
            twist_msg.angular.z = max(min(twist_msg.angular.z, 0.5), -0.5)
        else:
            # If aligned, move forward and apply smooth steering micro-corrections
            twist_msg.linear.x = 0.3 * distance_to_goal  # Dynamically scale speed based on remaining distance
            twist_msg.linear.x = max(min(twist_msg.linear.x, 0.4), 0.1)  # Bound safe linear velocity (max 0.4 m/s)
            twist_msg.angular.z = 0.8 * angle_error

        self.publisher_.publish(twist_msg)

def main(args=None):
    rclpy.init(args=args)
    node = GoToGoalNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
