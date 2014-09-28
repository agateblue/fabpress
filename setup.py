import os
from setuptools import setup, find_packages
import persisting_theory

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='persisting-theory',
    version=persisting_theory.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='BSD',  # example license
    description='A python package to build registries that can autodiscover values accross your project components',
    long_description=README,
    url='http://code.eliotberriot.com/eliotberriot/persisting-theory',
    author='Eliot Berriot',
    author_email='contact@eliotberriot.com',
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
    ],
)