from setuptools import find_packages, setup

setup(
    name='simple_graph_etl',
    packages=find_packages(include=['simple_graph_etl']),
    version='1.1.0',
    description="Minimal wrapper lib for Python ETLs using Microsoft's Graph API",
    author='glennpai / chglenn20@gmail.com',
    license='MIT',
    install_requires=['msal', 'requests'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)
