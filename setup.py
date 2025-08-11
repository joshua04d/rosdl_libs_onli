from setuptools import setup, find_packages

setup(
    name="rosdl",
    version="0.1.0",
    author="Your Name",
    description="ROS Data Library CLI + Modules",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "rosdl = cli:main"
        ]
    },
    python_requires=">=3.7",
)
