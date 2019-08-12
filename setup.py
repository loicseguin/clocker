from os import path
from setuptools import setup, find_packages
import sys


min_version = (3, 5)
if sys.version_info < min_version:
    error = """
clocker does not support Python {0}.{1}. Python {2}.{3} and above is required.
Check your Python version with:

    python --version

or

    python3 --version

This may be due to an out-of-date pip. Make sure you have pip >= 9.0.1. You can
upgrade pip with:

    python -m pip install -U pip
""".format(sys.version_info[0], sys.version_info[1],
           min_version[0], min_version[1])
    sys.exit(error)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

setup(
    name='clocker',
    version='0.1',
    author='Loïc Séguin-Charbonneau',
    author_email='lsc@loicseguin.com',
    description='Simplistic time tracking',
    long_description=readme,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
                'clocker=clocker.clocker:main',
            ],
    },
    python_requires='>={}.{}'.format(*min_version),
    license='MIT',
    classifiers=[
        # Full list at https://pypi.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Physics',
    ],
)
