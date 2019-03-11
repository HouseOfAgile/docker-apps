import boltons.fileutils as bf
import yaml
import os.path
import pkg_resources
from distutils.dir_util import copy_tree

from jinja2 import Environment, PackageLoader, select_autoescape

resource_package = __name__


env = Environment(
    loader=PackageLoader('docker_app_generator', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def load_config_file(filename):
    if os.path.exists(pkg_resources.resource_filename(resource_package, filename)):
        return yaml.load(pkg_resources.resource_string(resource_package, filename))
    else:
        return []


def create_app_structure(path_app):
    bf.mkdir_p(path_app)


def copy_files(from_path, to_path):
    copy_tree(from_path, to_path) if os.path.exists(from_path) else None


def generate_app_dockerfile(path_app, docker_stack, docker_base, docker_flavors, variant_name=None):
    # print('Dockerfile config {}\ndocker_base: {}\ndocker_stack: {}\n'.format(
        # path_app, docker_base, docker_stack))

    template = env.get_template('Dockerfile.j2')
    template.stream(
        docker_base=docker_base,
        docker_stack=docker_stack,
        docker_flavors=docker_flavors,
    ).dump(path_app + '/Dockerfile' + ('.' + variant_name if variant_name else ''))


def generate_build_shell(path_app, docker_image_name, docker_bases, settings):
    # print('Shell config\npath_app: {}\docker_image_name: {}\docker_bases: {}\n'.format(
        # path_app, docker_image_name, docker_bases))

    template = env.get_template('build.sh.j2')
    template.stream(
        settings=settings,
        docker_image_name=docker_image_name,
        docker_bases=docker_bases,
    ).dump(path_app + '/build.sh')


def generate_app_docker_compose(path_app, service_config, service_main, service_definition, settings):
    # print('compose {}\n{}\n{}\n{}\n###'.format(
        # service_config, service_main, service_definition, myconfig))

    template = env.get_template('docker-compose.yml.j2')
    template.stream(
        service_config=service_config,
        service_main=service_main,
        service_definition=service_definition,
        settings=settings
    ).dump(path_app + '/docker-compose.yml')
