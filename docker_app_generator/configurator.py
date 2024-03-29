from . import fileutils as fu
import os
import sys
from . import settings


def load_user_config():
    myconfig = fu.load_config_file('./myconfig.yml')

    for section in myconfig:
        print('{} => {}'.format(section, myconfig[section]))
    return myconfig


def load_assemblies(myconfig):
    if myconfig is not []:
        myconfig['assemblies'] = {}
        print('myconfig {}'.format(myconfig))
        for app_config in myconfig['apps_inventory']:
            myconfig['assemblies'][app_config['name']] = fu.load_config_file(
                settings.assembly_path + '/apps/' + app_config['name'] + '/main.yml')


def load_config(name, part, type='app'):
    return fu.load_config_file(settings.assembly_path + '/' + part + '/' + name + '/' + ('main' if type == 'app' else 'service') + '.yml')



def load_flavors_config(flavors, type='app'):
    config_dict = {}
    for flavor in flavors:
        # print('Loading flavor {}'.format(flavor))
        config_dict[flavor] = fu.load_config_file(
            settings.assembly_path + '/flavors/' + flavor + '/' + ('main' if type == 'app' else 'service') + '.yml')
    return config_dict


def view_assemblies(config):
    for app in config['assemblies']:
        print(settings.__dict__['assemblies'][app])


def configure_docker_apps(app_filter):
    myconfig = load_user_config()
    specific_app = next((item for item in  myconfig['apps_inventory'] if item.get("name") and item["name"] == app_filter), None)
    if specific_app:
        myconfig['apps_inventory'] = [specific_app]
        print('\n\n\nNew myconfig %s' % myconfig)

    load_assemblies(myconfig)
    settings.current_path = os.path.dirname(os.path.abspath(__file__))
    return myconfig
