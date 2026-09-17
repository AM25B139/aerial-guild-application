import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class TurtleMission(Node):
    def __init__(self):
        super().__init__('turtle_mission')
        
        # Publisher to send velocity commands for the circular path
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # Subscriber to listen to the turtle's live telemetry data
        self.subscriber_ = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        
        # Timer to continuously publish the movement command
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        self.get_logger().info('Phase 0: Autonomous Turtle Mission Started!')

    def timer_callback(self):
        msg = Twist()
        # Set constant linear and angular velocity to draw a continuous circle
        msg.linear.x = 2.0
        msg.angular.z = 1.0
        self.publisher_.publish(msg)

    def pose_callback(self, msg):
        # Print the real-time X and Y coordinates directly to the terminal
        self.get_logger().info(f'Turtle Location - X: {msg.x:.2f}, Y: {msg.y:.2f}')

def main(args=None):
    rclpy.init(args=args)
    turtle_mission = TurtleMission()
    
    try:
        rclpy.spin(turtle_mission)
    except KeyboardInterrupt:
        pass
        
    turtle_mission.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
