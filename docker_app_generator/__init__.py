from .configurator import configure_docker_apps
from .generator import generate_docker_app
import sys


def execute():
    print(sys.version)
    globalconfig = configure_docker_apps()
    generate_docker_app(globalconfig)
