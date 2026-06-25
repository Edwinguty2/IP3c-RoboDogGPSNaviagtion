#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import math
import threading

class GoToGoalWithObstacleNode(Node):
    def __init__(self):
        super().__init__('go_to_goal_obstacle_node')
        
        # Publishers and Subscribers
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        # Robot position state
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        self.odom_received = False
        
        # Obstacle detection state
        self.obstacle_detected = False
        self.min_front_distance = float('inf')
        self.safe_distance = 0.8  # Distance threshold to trigger avoidance (80 cm)
        
        # Target state
        self.target_x = None
        self.target_y = None
        self.goal_active = False

        # Tuning parameters
        self.distance_tolerance = 0.15
        self.angle_tolerance = 0.08 

        # Input console thread
        self.input_thread = threading.Thread(target=self.ask_for_coordinates, daemon=True)
        self.input_thread.start()

        # Control loop at 20Hz
        self.create_timer(0.05, self.control_loop)
        self.get_logger().info("Navigation Node with Obstacle Avoidance initialized.")

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        self.odom_received = True
        
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

    def scan_callback(self, msg):
        """ Processes LiDAR data to check for obstacles directly in front of the robot """
        if not msg.ranges:
            return

        # Define a front cone window (e.g., center index +/- 30 degrees)
        num_readings = len(msg.ranges)
        center_index = num_readings // 2
        cone_window = int(num_readings * (30.0 / 360.0)) # 30 degrees window
        
        start_idx = max(0, center_index - cone_window)
        end_idx = min(num_readings - 1, center_index + cone_window)
        
        # Extract slices of distances right in front
        front_ranges = msg.ranges[start_idx:end_idx]
        
        # Filter out invalid readings (0.0 or inf are common errors/out of range)
        valid_ranges = [r for r in front_ranges if msg.range_min < r < msg.range_max]
        
        if valid_ranges:
            self.min_front_distance = min(valid_ranges)
            if self.min_front_distance < self.safe_distance:
                if not self.obstacle_detected and self.goal_active:
                    self.get_logger().warn(f"Obstacle detected ahead! Distance: {self.min_front_distance:.2f}m. Turning to clear path...")
                self.obstacle_detected = True
            else:
                self.obstacle_detected = False
        else:
            self.obstacle_detected = False

    def ask_for_coordinates(self):
        while rclpy.ok():
            if not self.goal_active:
                try:
                    self.get_logger().info("\n--- READY FOR TARGET COORDINATE ---")
                    x_input = input("Enter target X coordinate: ")
                    y_input = input("Enter target Y coordinate: ")
                    
                    self.target_x = float(x_input)
                    self.target_y = float(y_input)
                    self.goal_active = True
                    self.get_logger().info(f"Target locked. Moving towards: X={self.target_x}, Y={self.target_y}")
                except ValueError:
                    self.get_logger().error("Please enter numbers only.")

    def control_loop(self):
        if not self.odom_received or not self.goal_active:
            return

        twist_msg = Twist()

        # 1. Global Goal Check: Have we reached the target?
        distance_to_goal = math.hypot(self.target_x - self.current_x, self.target_y - self.current_y)
        if distance_to_goal < self.distance_tolerance:
            twist_msg.linear.x = 0.0
            twist_msg.angular.z = 0.0
            self.publisher_.publish(twist_msg)
            self.get_logger().info(f"SUCCESS: Goal coordinate reached at X={self.current_x:.2f}, Y={self.current_y:.2f}")
            self.goal_active = False
            return

        # 2. STATE DECISION: Obstacle Avoidance vs Go-To-Goal
        if self.obstacle_detected:
            # REACTIVE STATE: Stop walking forward, rotate on its own axis to clear the front
            twist_msg.linear.x = 0.0
            # Gira hacia la derecha para buscar salida. Si quieres izquierda, cámbialo a positivo (0.4)
            twist_msg.angular.z = -0.4  
        else:
            # NORMAL STATE: Go-To-Goal control law
            desired_yaw = math.atan2(self.target_y - self.current_y, self.target_x - self.current_x)
            angle_error = desired_yaw - self.current_yaw
            angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

            if abs(angle_error) > self.angle_tolerance:
                # Align phase
                twist_msg.linear.x = 0.0
                twist_msg.angular.z = 1.0 * angle_error
                twist_msg.angular.z = max(min(twist_msg.angular.z, 0.4), -0.4)
            else:
                # Forward navigation phase
                twist_msg.linear.x = 0.25 * distance_to_goal
                twist_msg.linear.x = max(min(twist_msg.linear.x, 0.35), 0.1)
                twist_msg.angular.z = 0.6 * angle_error

        self.publisher_.publish(twist_msg)

def main(args=None):
    rclpy.init(args=args)
    node = GoToGoalWithObstacleNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
