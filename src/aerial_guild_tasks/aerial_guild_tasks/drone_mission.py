import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode, CommandTOL
import math

class DroneMission(Node):
    def __init__(self):
        super().__init__('drone_mission')
        
        # Subscriptions to monitor status
        self.state_sub = self.create_subscription(State, '/mavros/state', self.state_cb, 10)
        self.pose_sub = self.create_subscription(PoseStamped, '/mavros/local_position/pose', self.pose_cb, 10)
        
        # Publisher for movement
        self.local_pos_pub = self.create_publisher(PoseStamped, '/mavros/setpoint_position/local', 10)
        
        # Services for commands
        self.arming_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.set_mode_client = self.create_client(SetMode, '/mavros/set_mode')
        self.takeoff_client = self.create_client(CommandTOL, '/mavros/cmd/takeoff')
        
        self.current_state = State()
        self.current_pose = PoseStamped()
        
        # Square waypoint sequence (X, Y, Z)
        self.waypoints = [
            (5.0, 0.0, 5.0),
            (5.0, 5.0, 5.0),
            (0.0, 5.0, 5.0),
            (0.0, 0.0, 5.0) # Return to start location
        ]
        self.current_wp_index = 0
        self.tolerance = 0.5 # 0.5 meters
        
        self.mission_step = 0
        self.timer = self.create_timer(1.0, self.mission_loop)
        self.get_logger().info("Phase 2: Autonomous Drone Mission Started.")
        
    def state_cb(self, msg):
        self.current_state = msg
        
    def pose_cb(self, msg):
        self.current_pose = msg
        
    def distance_to_target(self, x, y, z):
        dx = x - self.current_pose.pose.position.x
        dy = y - self.current_pose.pose.position.y
        dz = z - self.current_pose.pose.position.z
        return math.sqrt(dx**2 + dy**2 + dz**2)
        
    def mission_loop(self):
        if not self.current_state.connected:
            self.get_logger().info("Waiting for ArduPilot connection...")
            return

        if self.mission_step == 0:
            if self.current_state.mode != "GUIDED":
                self.set_mode("GUIDED")
            else:
                self.mission_step = 1
                
        elif self.mission_step == 1:
            if not self.current_state.armed:
                self.arm(True)
            else:
                self.mission_step = 2
                
        elif self.mission_step == 2:
            if self.current_pose.pose.position.z < 4.5:
                self.takeoff(5.0)
            else:
                self.get_logger().info("Takeoff to 5m complete.")
                self.mission_step = 3
                
        elif self.mission_step == 3:
            if self.current_wp_index < len(self.waypoints):
                wp = self.waypoints[self.current_wp_index]
                self.publish_setpoint(wp[0], wp[1], wp[2])
                
                dist = self.distance_to_target(wp[0], wp[1], wp[2])
                
                if dist < self.tolerance:
                    self.get_logger().info(f"Reached Waypoint {self.current_wp_index + 1}!")
                    self.current_wp_index += 1
            else:
                self.mission_step = 4
                
        elif self.mission_step == 4:
            if self.current_state.mode != "RTL":
                self.get_logger().info("Mission Complete. Commanding Return to Launch (RTL).")
                self.set_mode("RTL")

    def set_mode(self, mode):
        req = SetMode.Request()
        req.custom_mode = mode
        self.set_mode_client.call_async(req)

    def arm(self, state):
        req = CommandBool.Request()
        req.value = state
        self.arming_client.call_async(req)

    def takeoff(self, alt):
        req = CommandTOL.Request()
        req.altitude = alt
        self.takeoff_client.call_async(req)
        
    def publish_setpoint(self, x, y, z):
        pose = PoseStamped()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        self.local_pos_pub.publish(pose)

def main(args=None):
    rclpy.init(args=args)
    node = DroneMission()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
