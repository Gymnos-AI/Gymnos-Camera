from setuptools import setup

setup(
    name='GymnosCamera',
    version='0.2.1',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),

    packages=['gymnoscamera', 'gymnoscamera.YoloNetwork'],
    package_data={
        'gymnoscamera.YoloNetwork': ['model_data/*txt'],
    }
)
