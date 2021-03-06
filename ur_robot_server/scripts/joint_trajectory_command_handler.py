#!/usr/bin/env python
import rospy
from trajectory_msgs.msg import JointTrajectoryPoint, JointTrajectory
from Queue import Queue

class JointTrajectoryCH:
    def __init__(self):
        rospy.init_node('joint_trajectory_command_handler')
        self.real_robot =  rospy.get_param("~real_robot")
        ac_rate = rospy.get_param("~action_cycle_rate")
        self.rate = rospy.Rate(ac_rate)

        # Publisher to JointTrajectory robot controller
        if self.real_robot:
            self.jt_pub = rospy.Publisher('/jr_arm_controller/command', JointTrajectory, queue_size=10)
        else:
            self.jt_pub = rospy.Publisher('/arm_controller/command', JointTrajectory, queue_size=10)

        # Subscriber to JointTrajectory Command coming from Environment
        rospy.Subscriber('env_arm_command', JointTrajectory, self.callback_env_joint_trajectory, queue_size=1)
        self.msg = JointTrajectory()
        # Queue with maximum size 1
        self.queue = Queue(maxsize=1)

    def callback_env_joint_trajectory(self,data):
        try:
            # Add to the Queue the next command to execute
            self.queue.put(data)
        except:
            pass

    def joint_trajectory_publisher(self):

        while not rospy.is_shutdown():
            # If a command from the environment is waiting to be executed,
            # publish the command, otherwise preempt trajectory
            if self.queue.full():
                self.jt_pub.publish(self.queue.get())
            else:
                self.jt_pub.publish(JointTrajectory())
            self.rate.sleep()


if __name__ == '__main__':
    try:
        ch = JointTrajectoryCH()
        ch.joint_trajectory_publisher()
    except rospy.ROSInterruptException:
        pass
