import docker_app_generator
from setuptools import setup


setup(name='docker_app_generator',
      version='0.1',
      description='generator for docker apps',
      url='http://github.com/TBD',
      author='Jean-Christophe Meillaud',
      author_email='jc@houseofagile.com',
      license='MIT',
      packages=['docker_app_generator'],
      zip_safe=False)

docker_app_generator.execute()
