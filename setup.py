from setuptools import setup

setup(
    name='GymnosCamera',
    version='0.3.0',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),

    packages=['gymnoscamera', 'gymnoscamera.yolo_network'],
    package_data={
        'gymnoscamera.yolo_network': ['model_data/*txt'],
    }
)
