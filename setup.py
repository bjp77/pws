from setuptools import setup

with open('requirements.txt') as f:
    requires = f.read().splitlines()

setup(name='pws',
      version='0.0.1',
      author='Brian Parry',
      packages = ['pws'],
      package_dir={'pws': 'lib'},
      install_requires=requires,
      scripts=['scripts/pwsrun']
     )
