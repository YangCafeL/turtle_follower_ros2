#!/usr/bin/env python3

import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Pose
from turtlesim.srv import SetPen, Spawn


class TurtleFollower(Node):
    """Create five turtles and make them follow one another in a chain."""

    def __init__(self):
        super().__init__('turtle_follower')

        self.turtle_poses = {}
        self.cmd_publishers = {}

        # turtlesim provides the /spawn service.
        self.spawn_client = self.create_client(Spawn, '/spawn')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')

        self.create_turtles()
        self.create_subscribers_and_publishers()
        self.get_logger().info('Five-turtle following system started.')

    def create_turtles(self):
        """Spawn turtle2-turtle5 and set different pen colors."""
        turtle_names = ['turtle1', 'turtle2', 'turtle3', 'turtle4', 'turtle5']
        positions = [
            (2.0, 2.0, 0.0),
            (4.0, 4.0, 0.0),
            (6.0, 6.0, 0.0),
            (8.0, 8.0, 0.0),
            (10.0, 10.0, 0.0),
        ]
        colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 0, 255),
        ]

        # turtle1 is created automatically by turtlesim.
        self.set_pen_color('turtle1', *colors[0], width=2)

        for index, name in enumerate(turtle_names[1:], start=1):
            x, y, theta = positions[index]
            self.spawn_turtle(name, x, y, theta)
            time.sleep(0.2)
            self.set_pen_color(name, *colors[index], width=2)

    def spawn_turtle(self, name, x, y, theta):
        """Spawn a turtle asynchronously."""
        request = Spawn.Request()
        request.x = float(x)
        request.y = float(y)
        request.theta = float(theta)
        request.name = name

        future = self.spawn_client.call_async(request)
        future.add_done_callback(
            lambda completed_future, turtle_name=name:
            self.spawn_callback(completed_future, turtle_name)
        )

    def spawn_callback(self, future, name):
        """Log the result of a spawn request."""
        try:
            response = future.result()
            if response.name == name:
                self.get_logger().info(f'Turtle {name} spawned successfully.')
        except Exception as exc:
            self.get_logger().error(f'Failed to spawn {name}: {exc}')

    def set_pen_color(self, turtle_name, r, g, b, width=2, off=0):
        """Set a turtle's pen color."""
        service_name = f'/{turtle_name}/set_pen'
        pen_client = self.create_client(SetPen, service_name)

        if not pen_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warning(f'{service_name} service is unavailable.')
            return

        request = SetPen.Request()
        request.r = int(r)
        request.g = int(g)
        request.b = int(b)
        request.width = int(width)
        request.off = int(off)
        pen_client.call_async(request)

    def create_subscribers_and_publishers(self):
        """Subscribe to turtle poses and publish velocity commands."""
        turtle_names = ['turtle1', 'turtle2', 'turtle3', 'turtle4', 'turtle5']

        for name in turtle_names:
            pose_topic = f'/{name}/pose'
            self.create_subscription(
                Pose,
                pose_topic,
                lambda msg, turtle_name=name: self.pose_callback(msg, turtle_name),
                10,
            )

            if name != 'turtle1':
                cmd_topic = f'/{name}/cmd_vel'
                self.cmd_publishers[name] = self.create_publisher(Twist, cmd_topic, 10)

    def pose_callback(self, msg, turtle_name):
        """Store the latest pose and update the corresponding follower."""
        self.turtle_poses[turtle_name] = msg
        self.implement_following(turtle_name)

    def implement_following(self, current_turtle):
        """Apply turtle2->1, turtle3->2, turtle4->3, turtle5->4."""
        follow_pairs = {
            'turtle2': 'turtle1',
            'turtle3': 'turtle2',
            'turtle4': 'turtle3',
            'turtle5': 'turtle4',
        }

        if current_turtle not in follow_pairs:
            return

        leader = follow_pairs[current_turtle]
        if current_turtle in self.turtle_poses and leader in self.turtle_poses:
            self.follow_leader(current_turtle, leader)

    def follow_leader(self, follower, leader):
        """Compute and publish a proportional control command."""
        follower_pose = self.turtle_poses[follower]
        leader_pose = self.turtle_poses[leader]

        dx = leader_pose.x - follower_pose.x
        dy = leader_pose.y - follower_pose.y
        distance = math.hypot(dx, dy)

        target_angle = math.atan2(dy, dx)
        angle_diff = target_angle - follower_pose.theta
        angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

        cmd = Twist()
        cmd.linear.x = min(0.5 * distance, 2.0)
        cmd.angular.z = 4.0 * angle_diff
        self.cmd_publishers[follower].publish(cmd)

    def stop_all_followers(self):
        """Stop all follower turtles before shutdown."""
        stop = Twist()
        for publisher in self.cmd_publishers.values():
            publisher.publish(stop)

    def destroy_node(self):
        self.stop_all_followers()
        self.get_logger().info('Shutting down turtle follower system...')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = TurtleFollower()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
