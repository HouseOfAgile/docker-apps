import argparse
from docker_app_generator import configure_docker_apps
from docker_app_generator import generate_docker_app
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delete",
                        help="start from scratch, delete all previous generated apps and stacks")
    args = parser.parse_args()

    if args.delete:
        print('delete stuff')
    else:
        print(sys.version)
        globalconfig = configure_docker_apps()
        generate_docker_app(globalconfig)
