import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class TurtleGoal(Node):
    def __init__(self):
        super().__init__('turtle_goal')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscriber_ = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        
        # Declare parameters to allow changing the goal from the terminal
        self.declare_parameter('goal_x', 8.0)
        self.declare_parameter('goal_y', 7.0)
        self.declare_parameter('tolerance', 0.1)

        self.pose = Pose()
        self.timer = self.create_timer(0.1, self.move_to_goal)
        self.goal_reached = False

    def pose_callback(self, msg):
        self.pose = msg

    def move_to_goal(self):
        if self.goal_reached:
            return

        # Fetch the current goal parameters
        goal_x = self.get_parameter('goal_x').get_parameter_value().double_value
        goal_y = self.get_parameter('goal_y').get_parameter_value().double_value
        tolerance = self.get_parameter('tolerance').get_parameter_value().double_value

        # Calculate distance (Euclidean) and direction (atan2)
        distance = math.sqrt((goal_x - self.pose.x)**2 + (goal_y - self.pose.y)**2)
        angle_to_goal = math.atan2(goal_y - self.pose.y, goal_x - self.pose.x)

        msg = Twist()

        if distance >= tolerance:
            # Proportional control: move faster when far, slower when close
            msg.linear.x = 1.0 * distance
            # Steer towards the calculated angle
            msg.angular.z = 4.0 * (angle_to_goal - self.pose.theta)
            self.publisher_.publish(msg)
        else:
            # Stop the turtle once within tolerance
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.publisher_.publish(msg)
            self.get_logger().info(f'Goal Reached! Stopped at X: {self.pose.x:.2f}, Y: {self.pose.y:.2f}')
            self.goal_reached = True

def main(args=None):
    rclpy.init(args=args)
    node = TurtleGoal()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
