cmake_minimum_required(VERSION 2.8.3)
project(waypoint_pkg)

find_package(catkin REQUIRED COMPONENTS
  rospy
)

catkin_package()

catkin_install_python(
  PROGRAMS
    scripts/obj_track.py
	scripts/vs_for_rrbot.py 
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
