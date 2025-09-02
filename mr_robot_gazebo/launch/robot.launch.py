#! /usr/bin/env python3
import xacro
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription,DeclareLaunchArgument, TimerAction, LogInfo
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration, Command, PythonExpression
from launch_ros.descriptions import ParameterValue
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    xacro_file=get_package_share_directory('mr_robot_description')+'/urdf/mr_robot.xacro'
    bridge_config=get_package_share_directory('mr_robot_gazebo')+ '/config/bridge.yaml'
    rviz_config=get_package_share_directory("mr_robot_description")+"/config/display.rviz"
    
    robot_state_publisher=Node(
        package = 'robot_state_publisher',
        executable = 'robot_state_publisher',
        name='robot_state_publisher',
        parameters = [
            {'robot_description': ParameterValue(Command( \
                    ['xacro ', xacro_file,
                    ' sim_ign:=', "true"
                    ]), value_type=str)},
            {'use_sim_time': True} 
        ]
    )
    
    robot_spawn=Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
                    '-name', 'mr_robot',
                    '-topic', '/robot_description',
                    "-allow_renaming", "true",
                    '-z', '0.3',
                    # '-y', '-6.0',
                    # '-x', '13.0'   
        ],
        parameters=[
            {'use_sim_time': True}  
        ]
    )

    ros_gz_bridge = Node(
                package="ros_gz_bridge", 
                executable="parameter_bridge",
                parameters = [
                    {'config_file': bridge_config}],
                )
    
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
    	output='screen',
        arguments=['-d' + rviz_config],
        parameters=[
            {'use_sim_time': True}  
        ]
    )

    world_path= get_package_share_directory("mr_robot_gazebo")+"/worlds/world.sdf"


    gazebo=IncludeLaunchDescription(
        PythonLaunchDescriptionSource([get_package_share_directory('ros_gz_sim'), '/launch/gz_sim.launch.py']),launch_arguments={
                    # 'gz_args' : [world_path + " -v 4"] , 'on_exit_shutdown' : 'true'
                    'gz_args' : [world_path] , 'on_exit_shutdown' : 'true'

                }.items()
    )
    
    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        robot_spawn,
        ros_gz_bridge,
        rviz,
    ])