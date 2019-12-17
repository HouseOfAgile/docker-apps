import pprint
from . import configurator as conf
from . import fileutils as fu
import os
from . import settings

pp = pprint.PrettyPrinter(indent=4)

def generate_docker_app(myconfig):

    for app_config in myconfig['apps_inventory']:
        path_app = settings.apps_path + '/' + app_config['name']
        # create dir
        fu.create_app_structure(path_app)

        # load_config
        docker_stack = conf.load_config(
            app_config['name'], 'apps')
        docker_bases = conf.load_config(
            app_config['docker_base'],   'bases') if app_config['docker_base'] else []
        docker_flavors = conf.load_flavors_config(
            app_config['docker_flavors'])

        # generate each variant
        if docker_bases:
            # add main vars
            docker_bases['variants'].append(
                {'name': 'main', 'variant_vars': docker_bases['main_vars']})

            for variant in docker_bases['variants']:
                # docker_base is the cleaned docker commands with replaced variants if they exist
                docker_base = {}
                # print('Variant {} with vars: {}'.format(variant['name'], variant['variant_vars']))
                for element in settings.docker_main_sections:
                    content = docker_bases['main'][element]
                    if variant != 'main':
                        for key in variant['variant_vars']:
                            content = content.replace(
                                key, variant['variant_vars'][key])
                    else:
                        for key in docker_bases['main_vars']:
                            content = content.replace(
                                key, docker_bases['main_vars'][key])

                    docker_base[element] = content

                # merge all values
                docker_base = dict(
                    list(docker_bases['main'].items()) + list(docker_base.items()))
                # update dynamic parameters
                docker_stack = update_parameters(
                    docker_stack, myconfig['parameters'])
                docker_base = update_parameters(
                    docker_base, myconfig['parameters'])                    
                for flavor in docker_flavors:
                    docker_flavors[flavor] = update_parameters(
                        docker_flavors[flavor], myconfig['parameters'])

                fu.generate_app_dockerfile(path_app, docker_stack, docker_base,
                                           docker_flavors, variant['name'] if variant['name'] != 'main' else None)
                image_variants = [v['name']
                                  for v in docker_bases['variants'] if v['name'] != 'main']
                image_name = app_config['image_name'] if app_config['image_name'] else app_config['name']
                fu.generate_build_shell(
                    path_app, image_name, image_variants, settings)
                print("Generated docker apps for %s:%s" %
                      (app_config['name'], variant['name']))
        else:
            print('base is empty')

        # copy files
        assembly_path = settings.current_path + \
            os.path.join(os.path.sep, settings.assembly_path)

        fu.copy_files(assembly_path + '/apps/' +
                      app_config['name'] + '/files', path_app + '/files/' + app_config['name'])
        fu.copy_files(assembly_path + '/bases/' +
                      app_config['docker_base'] + '/files', path_app + '/files/' + app_config['docker_base'])
        for flavor in app_config['docker_flavors']:
            fu.copy_files(assembly_path + '/flavors/' + flavor + '/files',
                          path_app + '/files/' + flavor)

        # pp.pprint(myconfig['assemblies'][app_config['name']])

    for stack_config in myconfig['stacks_inventory']:
        stack_path = settings.stacks_path + '/' + stack_config['name']
        # create dir
        fu.create_app_structure(stack_path)
        # load service config
        service_main = conf.load_config(
            stack_config['app_main_service'], 'bases', 'stacks') if app_config['docker_base'] else []
        service_definition = conf.load_flavors_config(
            stack_config['app_other_services'], 'stacks')
        # generate docker compose
        fu.generate_app_docker_compose(stack_path, stack_config,
                                       service_main, service_definition, settings)


def update_parameters(yaml_dict, parameters):
    if(parameters):
        for element in yaml_dict:
            if element != 'docker_expose':
                for parameter in parameters:
                    yaml_dict[element] = yaml_dict[element].replace(
                        '#'+parameter+'#', parameters[parameter]) 

    return yaml_dict
