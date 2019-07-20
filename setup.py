from setuptools import setup

setup(
    name='GymnosCamera',
    version='0.4.0',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),

    packages=['gymnoscamera', 'gymnoscamera.yolo_network'],
    package_data={
        'gymnoscamera.yolo_network': ['model_data/*txt'],
    },

    install_requires=[
        'absl-py>=0.7.1',
        'astor>=0.8.0',
        'cycler>=0.10.0',
        'gast>=0.2.2',
        'google-pasta>=0.1.7',
        'grpcio>=1.22.0',
        'h5py>=2.9.0',
        'Keras>=2.2.4',
        'Keras-Applications>=1.0.8',
        'Keras-Preprocessing>=1.1.0',
        'kiwisolver>=1.1.0',
        'Markdown>=3.1.1',
        'matplotlib>=3.1.1',
        'numpy>=1.16.4',
        'opencv-python>=4.1.0.25',
        'Pillow>=6.1.0',
        'protobuf>=3.8.0',
        'pyparsing>=2.4.0',
        'python-dateutil>=2.8.0',
        'PyYAML>=5.1.1',
        'scipy>=1.3.0',
        'six>=1.12.0',
        'tensorboard>=1.14.0',
        'tensorflow-estimator>=1.14.0',
        'termcolor>=1.1.0',
        'Werkzeug>=0.15.4',
        'wrapt>=1.11.2',
    ]
)
