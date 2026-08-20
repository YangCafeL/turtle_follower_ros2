from setuptools import find_packages, setup

package_name = 'turtle_follower'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        ('share/' + package_name, ['package.xml']),
        (
            'share/' + package_name + '/launch',
            ['launch/turtle_follower.launch.py'],
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='ROS2 five-turtle chain following demo using turtlesim.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'turtle_follower = turtle_follower.turtle_follower:main',
        ],
    },
)
