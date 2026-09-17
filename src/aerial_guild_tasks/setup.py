from setuptools import find_packages, setup

package_name = 'aerial_guild_tasks'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='manoj_2007',
    maintainer_email='manoj_2007@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': ['turtle_mission = aerial_guild_tasks.turtle_mission:main','turtle_goal = aerial_guild_tasks.turtle_goal:main'
        ],
    },
)
