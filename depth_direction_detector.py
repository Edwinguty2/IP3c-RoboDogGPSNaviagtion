import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from control_input_msgs.msg import Inputs

import numpy as np


class DepthDirectionDetector(Node):

    def __init__(self):

        super().__init__('depth_direction_detector')

        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            '/camera_face/depth/image_raw',
            self.callback,
            10
        )

        self.control_pub = self.create_publisher(
            Inputs,
            '/control_input',
            10
        )

        self.threshold = 1.8

    def callback(self, msg):

        depth = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='passthrough'
        )

        h, w = depth.shape

        right_region = depth[
            h//2-20:h//2+20,
            w//6-20:w//6+20
        ]

        left_region = depth[
            h//2-20:h//2+20,
            5*w//6-20:5*w//6+20
        ]

        center_region = depth[
            h//2-20:h//2+20,
            w//2-20:w//2+20
        ]

        left_valid = left_region[np.isfinite(left_region)]
        center_valid = center_region[np.isfinite(center_region)]
        right_valid = right_region[np.isfinite(right_region)]

        if (
            len(left_valid) == 0 or
            len(center_valid) == 0 or
            len(right_valid) == 0
        ):
            return

        left = float(np.mean(left_valid))
        center = float(np.mean(center_valid))
        right = float(np.mean(right_valid))

        self.get_logger().info(
            f'L={left:.2f}m | C={center:.2f}m | R={right:.2f}m'
        )

        cmd = Inputs()
        cmd.command = 4

        if center >= self.threshold:

            cmd.ly = 0.5
            cmd.lx = 0.0
            cmd.rx = 0.0
            cmd.ry = 0.0

            self.control_pub.publish(cmd)

            self.get_logger().info(
                'GO FORWARD'
            )

            return

        if left > self.threshold and right > self.threshold:

            if left > right:

                cmd.rx = -0.5
                cmd.ly = 0.0
                self.get_logger().warn(
                    'TURN LEFT'
                )

            else:

                cmd.rx = 0.5
                cmd.ly = 0.0
                self.get_logger().warn(
                    'TURN RIGHT'
                )

        elif left > self.threshold:

            cmd.rx = -0.5

            self.get_logger().warn(
                'TURN LEFT'
            )

        elif right > self.threshold:

            cmd.rx = 0.5

            self.get_logger().warn(
                'TURN RIGHT'
            )

        else:

            cmd.command = 0

            self.get_logger().error(
                'STOP - NO PATH'
            )

        self.control_pub.publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = DepthDirectionDetector()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
