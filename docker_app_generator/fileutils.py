import boltons.fileutils as bf
import yaml
import pkg_resources
from distutils.dir_util import copy_tree
import pprint
from pathlib import Path
import shutil
import re

from jinja2 import Environment, PackageLoader, select_autoescape

resource_package = __name__


env = Environment(
    loader=PackageLoader("docker_app_generator", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

def regex_match(string, p):
    return bool(re.search(p,string))

def regex_split(string, p):
    return string[:string.rfind(p)]

env.filters['regex_match'] = regex_match
env.filters['regex_split'] = regex_split

pp = pprint.PrettyPrinter(indent=4)


def load_config_file(filename):
    if is_valid_file(pkg_resources.resource_filename(resource_package, filename)):
        return yaml.load(pkg_resources.resource_string(resource_package, filename))
    else:
        return []


def create_app_structure(path_app):
    bf.mkdir_p(path_app)
    bf.mkdir_p(path_app + "/dockerfiles")


def cleanup_directory(dir):
    if is_valid_directory(dir):
        shutil.rmtree(dir)


def copy_files_old(from_path, to_path):
    copy_tree(from_path, to_path) if is_valid_file(from_path) else None


def copy_files(from_path_base, stack_element, name, to_path_base):
    # copy files
    for file_type in ["config", "files"]:
        from_path = from_path_base + "/" + stack_element + "/" + name + "/" + file_type
        to_path = to_path_base + "/" + file_type + "/" + name
        print("from {}, to {}".format(from_path, to_path))
        copy_tree(from_path, to_path,) if is_valid_file(from_path) else None

    # copy config
    # copy_tree(from_path, to_path) if is_valid_file(from_path) else None


def generate_app_dockerfile(
    path_app, docker_stack, docker_base, docker_flavors, variant_name=None
):
    # print('Dockerfile config {}\ndocker_base: {}\ndocker_stack: {}\n'.format(
    # path_app, docker_base, docker_stack))

    data = {
        "docker_base": docker_base,
        "docker_stack": docker_stack,
        "docker_flavors": docker_flavors,
    }
    generate_file(
        data,
        "Dockerfile",
        path_app
        + "/dockerfiles/"
        + (variant_name + "." if variant_name else "")
        + "Dockerfile",
    )


def generate_build_shell(path_app, docker_image_name, docker_bases, settings):
    # print('Shell config\npath_app: {}\docker_image_name: {}\docker_bases: {}\n'.format(
    # path_app, docker_image_name, docker_bases))
    data = {
        "docker_image_name": docker_image_name,
        "docker_bases": docker_bases,
        "settings": settings,
    }
    generate_file(data, "build.sh", path_app + "/build.sh")


def generate_docker_compose(path_app, app_config, settings):
    data = {
        "app_config": app_config,
        "compose": app_config["compose"],
        "settings": settings,
    }
    generate_file(data, "docker-compose.yml", path_app + "/docker-compose.yml")
    for env in app_config["compose"]["env"]:
        data['env'] = env
        data['compose_env'] = app_config["compose"]["env"][env]
        generate_file(
            data,
            "docker-compose.env.yml",
            path_app + "/docker-compose." + env + ".yml",
        )
    generate_file(
        data, "docker-compose.common.yml", path_app + "/docker-compose.common.yml"
    )


def generate_file(data, filename, target):
    template = env.get_template(filename + ".j2")
    template.stream(data).dump(target)


def is_valid_file(filename):
    p = Path(filename)
    return p.exists()


def is_valid_directory(filename):
    p = Path(filename)
    return p.exists() and p.is_dir()
