import argparse
from docker_app_generator import configure_docker_apps
from docker_app_generator import generate_docker_app
from docker_app_generator import cleanup_docker_app
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--delete",
        default=False,
        action="store_true",
        help="start from scratch, delete all previous generated apps and stacks",
    )
    parser.add_argument(
        "-f", "--filter", default=False, help="Filter to only specific apps/stacks"
    )
    args = parser.parse_args()

    globalconfig = configure_docker_apps(args.filter)

    if args.delete:
        cleanup_docker_app(globalconfig)
    # print(sys.version)
    generate_docker_app(globalconfig)
