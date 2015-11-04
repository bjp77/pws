from setuptools import setup, find_packages
from os import path

with open('requirements.txt') as f:
    requires = f.read().splitlines()
print find_packages(where='services')

pkgs = {} 
for pkg in find_packages(where='services', exclude=['*test']):
    pkgs['pws.services.' + pkg] = path.join('services', pkg)

pkgs.update({'pws.lib': 'lib', 'pws.services': 'services'})
print pkgs
setup(name='pws',
      version='0.0.13',
      author='Brian Parry',
      packages=pkgs.keys(),
      package_dir=pkgs,
      install_requires=requires
     )
