import argparse
from docker_app_generator import configure_docker_apps
from docker_app_generator import generate_docker_app
from docker_app_generator import cleanup_docker_app
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delete",default=False, action='store_true',
                        help="start from scratch, delete all previous generated apps and stacks")
    args = parser.parse_args()

    globalconfig = configure_docker_apps()

    if args.delete:
        cleanup_docker_app(globalconfig)
    else:
        print(sys.version)
        generate_docker_app(globalconfig)
