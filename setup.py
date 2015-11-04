from disutils.core import setup

with open('requiremnts.txt') as f:
    requires = f.read().splitlines()

setup(name='PWS Observer',
      version='0.0.1',
      author='Brian Parry',
      packages = ['pwsobs'],
      package_dir={'pwsobs': 'lib'},
      requires=requires
     )
