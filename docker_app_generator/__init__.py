from .configurator import configure_docker_apps
from .generator import generate_docker_app
from .generator import cleanup_docker_app

import sys


def execute(filter_app):
    print(sys.version)
    print(filter_app)
    globalconfig = configure_docker_apps()
    generate_docker_app(globalconfig)
