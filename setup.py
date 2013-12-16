from setuptools import setup, find_packages

with open('README.rst') as file:
    long_description = file.read()

pyver_requires = []
with open('requirements.txt') as file:
    for line in file.readlines():
        pyver_requires.append(line.strip())

VERSION = '0.0.1'

setup(
    name='kvmdashclient',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=find_packages(),
    url='http://github.com/jantman/kvmdashclient/',
    license='AGPLv3+',
    description='Client (data collector) for kvmdash',
    long_description=long_description,
    install_requires=pyver_requires,
    keywords="libvirt kvm",
    include_package_data=True
)
