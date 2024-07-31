#! /usr/bin/env python3

import rospy
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, CommandBoolRequest, SetMode, SetModeRequest
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist

import numpy
import math
from tf.transformations import quaternion_from_euler, euler_from_quaternion
from mavros_msgs.msg import PositionTarget

class midterm_drone():
	def __init__(self):
		self.distThr = 0.01;
		print("Init initi")
		rospy.init_node("offb_node_py")
		self.current_state = State();
		
		#self.state_sub = rospy.Subscriber("/odom", Odometry, callback = self.odom_callback)
		#self.pose_pub = rospy.Publisher("mavros/setpoint_position/local", PoseStamped, queue_size=10)
		self.vel_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
		
		
		# Mission Starts here!!!
		print("----Mission Starts here!!!----")
		self.drone_pose_sub = rospy.Subscriber("/odom", Odometry, callback = self.odom_callback)
		self.rate = rospy.Rate(50)
		self.des = []
		self.currPose = PoseStamped()
		self.desPose = PoseStamped()
		self.curr = self.currPose.pose.position
		self.rock_x,self.rock_y, self.rock_z = 60.2,-12.5, 18.8
		print("------------================= READY to GO =============-----------------")
		#rospy.spin();
		
		
	def odom_callback(self, msg):
		self.currPose.pose.position.x = msg.pose.pose.position.x
		self.currPose.pose.position.y = msg.pose.pose.position.y
		self.currPose.pose.position.z = msg.pose.pose.position.z
		
		self.currPose.pose.orientation.x = msg.pose.pose.orientation.x
		self.currPose.pose.orientation.y = msg.pose.pose.orientation.y
		self.currPose.pose.orientation.z = msg.pose.pose.orientation.z
		self.currPose.pose.orientation.w = msg.pose.pose.orientation.w
		self.curr = self.currPose.pose.position
		x = msg.pose.pose.position.x
		y = msg.pose.pose.position.y
		z = msg.pose.pose.position.z
		qx = msg.pose.pose.orientation.x
		qy = msg.pose.pose.orientation.y
		qz = msg.pose.pose.orientation.z
		qw = msg.pose.pose.orientation.w
		#print(self.currPose.pose.position.x, " ", self.currPose.pose.position.y , "  ", self.currPose.pose.position.z,"    -callback-- ")
		#rospy.loginfo("Position: ({}, {}, {})".format(x, y, z))
		#rospy.loginfo("Orientation: ({}, {}, {}, {})".format(qx, qy, qz, qw))

	def state_cb(self, msg):
		self.current_state = msg

	def drone_pose_cb(self, msg):
		self.currPose = msg
		self.curr = self.currPose.pose.position
		# print("Drone pose received", self.curr)

	def getDist(self, curr, des):
		return math.sqrt(pow(curr.x - des[0], 2) + pow(curr.y - des[1], 2) + pow(curr.z - des[2], 2))
		
	def navigate(self, x, y, z ):
		self.desPose.pose.position.x = x
		self.desPose.pose.position.y = y
		self.desPose.pose.position.z = z
		rospy.loginfo("Desired position: x={}, y={}, z={}".format(x, y, z))
		self.des = [x, y, z]
		# print(self.curr)
		d = self.getDist(self.curr, self.des)
		while d > self.distThr and not rospy.is_shutdown():
			# print("Drone pose received", self.curr)
			# self.curr = self.currPose.pose.position
			# print(d, '--' , self.curr, '--' , self.des)
			azimuth = math.atan2(self.rock_y - self.currPose.pose.position.y,self.rock_x - self.currPose.pose.position.x)
			# print(azimuth)
			if azimuth > math.pi:
				azimuth -= 2.0 * math.pi
			else:
				azimuth += 2.0 * math.pi
			q = quaternion_from_euler(0, 0, azimuth)
			# print(q)
			self.desPose.pose.orientation.x = q[0]
			self.desPose.pose.orientation.y = q[1]
			self.desPose.pose.orientation.z = q[2]
			self.desPose.pose.orientation.w = q[3]
			d = self.getDist(self.curr, self.des)
			self.pose_pub.publish(self.desPose)
			self.rate.sleep()
			if d <= self.distThr:
				print(azimuth)
				print(q)
				break
		
	def navigateroverVelctrl(self, x, y ):
		print(1)
		self.desPose.pose.position.x = x
		self.desPose.pose.position.y = y
		self.desPose.pose.position.z = 0
		print(2)
		
		
		#rospy.loginfo("Desired position: x={}, y={}, z={}".format(x, y, 0))
		self.des = [x, y, 0]
		print(3)
		# print(self.curr)
		rospy.sleep(0.1)
		d = self.getDist(self.curr, self.des)
		#print(4,"  d  ", d ,  "  ", )
		cx = self.currPose.pose.position.x;
		cy = self.currPose.pose.position.y;
		cz = self.currPose.pose.position.z;
			
		print("Desired position: x={}, y={}, z={}".format(x, y, 0));
			
		while d > self.distThr and not rospy.is_shutdown():
			#print(5)
			cx = self.currPose.pose.position.x;
			cy = self.currPose.pose.position.y;
			cz = self.currPose.pose.position.z;
			#print(6)
			#print(self.currPose.pose.position.x, " ", self.currPose.pose.position.y , "  ", self.currPose.pose.position.z,"    -navigateroverVelctrl-- ")
			#print(7)
			# Publish rot + vel till azimuth close to zero, then only forward vel
			azimuth = math.atan2(self.desPose.pose.position.y - self.currPose.pose.position.y,self.desPose.pose.position.x - self.currPose.pose.position.x)
			#print(8)
			while azimuth > math.pi or azimuth < -math.pi:
				if azimuth > math.pi:
					azimuth -= 2.0 * math.pi
				else:
					azimuth += 2.0 * math.pi
			#print(9)
			# print("Drone pose received", self.curr)
			self.curr = self.currPose.pose.position
			# print(d, '--' , self.curr, '--' , self.des)
			# print(azimuth)
			
			#q = quaternion_from_euler(0, 0, azimuth)
			# print(q)
			botangles = euler_from_quaternion([self.currPose.pose.orientation.x, self.currPose.pose.orientation.y, self.currPose.pose.orientation.z, self.currPose.pose.orientation.w])
			#print("bot angles : ", botangles)
			botazimuth = botangles[2];
			#print(10)
			#print("Angles : azimuth={}, botazimuth={}".format(azimuth, botazimuth));
			while botazimuth > math.pi or botazimuth < -math.pi:
				if botazimuth > math.pi:
					botazimuth -= 2.0 * math.pi
				else:
					botazimuth += 2.0 * math.pi
			#print(11)
			angerr = azimuth - botazimuth;
			
			vel_cmd = Twist()
			vel_cmd.linear.x = 0.5  # Set linear velocity in the x-axis direction
			#print(12)
			if abs(angerr) < 0.05:
				vel_cmd.angular.z = 0.0  # Set angular velocity around the z-axis
			else:
				if angerr > 0:
					if angerr < math.pi:
						vel_cmd.angular.z = 1.0  # Set angular velocity around the z-axis
					else:
						vel_cmd.angular.z = -1.0  # Set angular velocity around the z-axis
				else:
					if angerr > -math.pi:
						vel_cmd.angular.z = -1.0  # Set angular velocity around the z-axis
					else:
						vel_cmd.angular.z = 1.0  # Set angular velocity around the z-axis
			#print(12)

			# Publish the velocity command
			self.vel_pub.publish(vel_cmd)
			self.rate.sleep()
			d = self.getDist(self.curr, self.des)
			#print(13)
			if d <= self.distThr:
				vel_cmd.linear.x = 0.0
				vel_cmd.angular.z = 0.0
				self.vel_pub.publish(vel_cmd)
				self.rate.sleep()			
				break
			#print(14)
			
			
	def circleRock(self,x,y,z,r,n,zh):
		print("=== Circle rock ========")
		#r = 8;
		#n = 24;
		init_ang = math.atan2(y - self.curr.y, x - self.curr.x)
		for i in range(n):
			self.despose.pose.position.x = x+r*math.cos(i*2*math.pi/n - init_ang);
			self.despose.pose.position.y = y+r*math.sin(i*2*math.pi/n - init_ang);
			self.despose.pose.position.z = z + zh;
			self.des = [self.despose.pose.position.x, self.despose.pose.position.y, self.despose.pose.position.z];
			#rospy.loginfo("Desired position: x={}, y={}, z={}".format(self.des[0], self.des[1], self.des[2]))
			azimuth = math.atan2(y - self.despose.pose.position.y, x - self.despose.pose.position.x)
			# print(azimuth)
			if azimuth > math.pi:
				azimuth -= 2.0 * math.pi
			else:
				azimuth += 2.0 * math.pi
			q = quaternion_from_euler(0, 0, azimuth)
			# print(q)
			self.despose.pose.orientation.x = q[0]
			self.despose.pose.orientation.y = q[1]
			self.despose.pose.orientation.z = q[2]
			self.despose.pose.orientation.w = q[3]
			rospy.loginfo("Desired position: x={}, y={}, z={}, qx={}, qy = {}, qz = {}, qw = {}".format(self.des[0], self.des[1], self.des[2], q[0], q[1],q[2],q[3]))
			d = self.getDist(self.curr, self.des)
			while d > self.distThr and not rospy.is_shutdown():
				self.pose_pub.publish(self.despose);
				d = self.getDist(self.curr, self.des);
				self.rate.sleep()
				
								
	def gotoSampleprobe(self):
		print("=== Going to probe location ========")
		locations = numpy.matrix([[40.8, 3.5, 20],])
		for waypt in locations:
			x, y, z = waypt.tolist()[0]
			self.navigate(x, y, z)

	def pickProbe(self):
		print("=== Pick probe using visual servoing(currently position control) ========")
		locations = numpy.matrix([[40.8, 3.5, 12.2],[40.8, 3.5, 20]]);
		for waypt in locations:
			x, y, z = waypt.tolist()[0]
			self.navigate(x, y, z)

	def gotoRock(self):
		print("=== GO to rock and Face rock ========")
		locations = numpy.matrix([[60, -15, 18.89],])
		for waypt in locations:
			x, y, z = waypt.tolist()[0]
			self.navigate(x, y, z)
	
	def gotoRover(self):
		print("=== GO to rock and Face rock ========")
		locations = numpy.matrix([[12.62, -64.8, 2],[12.62, -64.85, 0.5]])
		for waypt in locations:
			x, y, z = waypt.tolist()[0]
			self.navigate(x, y, z)

	def land_on_rover(self):
		local_pos_pub = rospy.Publisher('/mavros/setpoint_raw/local', PositionTarget, queue_size=10)
		arm_service = rospy.ServiceProxy('/mavros/cmd/arming', CommandBool)
		landing_position = PositionTarget()
		landing_position.position.x = 12.621
		landing_position.position.y = -64.85
		landing_position.position.z = -3.5
		landing_position.coordinate_frame = PositionTarget.FRAME_LOCAL_NED
		landing_position.type_mask = PositionTarget.IGNORE_VX + PositionTarget.IGNORE_VY + PositionTarget.IGNORE_VZ \
							+ PositionTarget.IGNORE_AFX + PositionTarget.IGNORE_AFY + PositionTarget.IGNORE_AFZ \
							+ PositionTarget.IGNORE_YAW + PositionTarget.IGNORE_YAW_RATE
		# Publish the landing position command
		rate = rospy.Rate(10)
		while not rospy.is_shutdown():
			local_pos_pub.publish(landing_position)
			rate.sleep()
			if(self.currPose.pose.position.z < -3.2):
				print("Landed =========")
				arm_service(False);

	def navigateMap(self):
		locations = numpy.matrix([  [1, -6.5],[3, -8],[8, -8],[9.5, -6], [ 9.5, -4], [ 11.5, -3]  ])
		for waypt in locations:
			x, y = waypt.tolist()[0]
			self.navigateroverVelctrl(x, y);
		


	def run(self):
		self.navigateroverVelctrl(1, -3);
		self.navigateMap();
		locations = numpy.matrix([[40.8, 3.5, 20],])
		for waypt in locations:
			x, y, z = waypt.tolist()[0]
			self.navigate(x, y, z)
		#
		#self.gotoSampleprobe();
		#self.pickProbe();
		#self.gotoRock();
		###self.circleRock(0,-3,3,4,16);
		#self.circleRock(self.rock_x,self.rock_y,self.rock_z,3.5,24,1);
		#self.gotoRover();
		#self.land_on_rover();
	
if __name__ == "__main__":
    highflier = midterm_drone();
    highflier.run();
