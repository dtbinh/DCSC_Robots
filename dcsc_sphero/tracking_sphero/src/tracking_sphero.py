#!/usr/bin/env python
import rospy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose2D
from geometry_msgs.msg import Twist
import tf
import numpy as np

class Controller:

	def __init__(self):

		self.d = 0.2

		#th = -np.pi/3*4
		#self.R = np.array([[np.cos(th),-np.sin(th),0],[np.sin(th),np.cos(th),0],[0,0,1]])
		#rospy.loginfo(self.R)

		self.xr = np.array([0,0,0]).T
		self.x = np.array([0,0,0]).T

		rospy.init_node('robot_linear_control')
		self.rate = rospy.Rate(10)

		self.pub = rospy.Publisher('cmd_vel', Twist)
		self.sub_odom = rospy.Subscriber('odom',Odometry,self.odom)
    		self.sub_goal = rospy.Subscriber('/sphero_goal',Pose2D,self.goal)
	
		self.offset_x = rospy.get_param('~offset_x',0)
        	self.offset_y = rospy.get_param('~offset_y',0)
		
		rospy.loginfo("Controller initialized.")

		self.control()

	def control(self):

		while not rospy.is_shutdown():
			
			#Define the Twist
			twist = Twist()

			#Get input
			e = np.array([self.xr[0]-self.x[0],self.xr[1]-self.x[1]]).T
			if np.linalg.norm(e) < 0.10:
				#Dont move when in position
				u = np.array([0,0]).T
				twist.linear.x = 0
				twist.linear.y = 0
			else:
				#Get control input
				u = e * 100
				rospy.loginfo("Moving the robot.")			
				twist.linear.x = u[0]
				twist.linear.y = u[1]

			#Publish
			self.pub.publish(twist)		
			self.rate.sleep()
	
	def goal(self,pose):
		self.xr = np.array([pose.x+self.offset_x,pose.y+self.offset_y,pose.theta]).T

	def odom(self,odom):
		quaternion = (odom.pose.pose.orientation.x, odom.pose.pose.orientation.y, odom.pose.pose.orientation.z, odom.pose.pose.orientation.w)
		euler = tf.transformations.euler_from_quaternion(quaternion)
		self.x = np.array([odom.pose.pose.position.x,odom.pose.pose.position.y,(euler[2]+np.pi)%(2*np.pi)-np.pi]).T

if __name__ == '__main__':
    try:
        c = Controller()
    except rospy.ROSInterruptException: pass
