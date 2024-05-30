#!/usr/bin/env python3
import rospy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose
from std_msgs.msg import Float64
import numpy as np

class OdomError:
    def __init__(self):
        rospy.init_node('odom_error_node')
        self.pub = rospy.Publisher('/odom_error', Float64, queue_size=10)
        self.sub1 = rospy.Subscriber('/lio_sam/mapping/odometry', Odometry, self.odom_callback)
        self.sub2 = rospy.Subscriber('/odom', Odometry, self.odom_gt_callback)
        self.odom_queue = []
        self.odom_gt_queue = []
        self.max_time_diff = 1.0  # maximum time difference to consider for time synchronization

    def odom_callback(self, msg):
        self.odom_queue.append(msg)

    def odom_gt_callback(self, msg):
        self.odom_gt_queue.append(msg)
        self.compute_odom_error()

    def compute_odom_error(self):
        if self.odom_queue and self.odom_gt_queue:
            odom = self.odom_queue.pop(0)
            odom_gt = self.find_closest_msg(odom.header.stamp, self.odom_gt_queue)
            if odom_gt:
                x_diff = odom.pose.pose.position.x - odom_gt.pose.pose.position.x
                y_diff = odom.pose.pose.position.y - odom_gt.pose.pose.position.y
                z_diff = odom.pose.pose.position.z - odom_gt.pose.pose.position.z
                odom_diff = np.sqrt(x_diff**2 + y_diff**2 + z_diff**2)
                print(" error pubbed :",odom_diff)
                self.pub.publish(Float64(odom_diff))

    def find_closest_msg(self, stamp, msg_queue):
        time_diffs = [(np.abs((stamp - m.header.stamp).to_sec()), m) for m in msg_queue]
        sorted_msgs = sorted(time_diffs, key=lambda x: x[0])
        #print( " sorted_msgs = ", sorted_msgs[0][0] , " max_time_diff " , self.max_time_diff  );
        if sorted_msgs[0][0] > self.max_time_diff:
            return None  # return None if no message is found within the maximum time difference
        else:
            return sorted_msgs[0][1]

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    odom_error = OdomError()
    odom_error.run()
