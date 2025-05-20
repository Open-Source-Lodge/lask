from setuptools import setup

setup(
    name='gpterm',
    version='0.1',
    py_modules=['gpterm'],
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'gpterm = gpterm:main',
        ],
    },
    author='Your Name',
    description='A CLI tool to prompt ChatGPT and others from the terminal.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)