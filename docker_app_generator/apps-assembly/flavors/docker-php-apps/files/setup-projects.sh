#!/bin/bash

# debug mode :
set -x
SM_CONF_DIR=/root/.symfony-manager

source ~/.bash-profile.d/bash-profile

for file in `find $SM_CONF_DIR/sm-config/ -type f -printf "%f\n" | egrep "^sm-config"`
do
  source $SM_CONF_DIR/sm-config/$file
  ### highly dependant
  cat /srv/nginx-config/default-app-nginx.conf | sed "s/__project_name__/$application_projectname/g;s#__project_path__#$application_install_path#g;s/__project_hosts__/$application_host/g"  > /etc/nginx/sites-available/project_$application_projectname.conf
  [ -e /etc/nginx/sites-enabled/project_$application_projectname.conf ] && rm /etc/nginx/sites-enabled/project_$application_projectname.conf
  ln -s /etc/nginx/sites-available/project_$application_projectname.conf /etc/nginx/sites-enabled/project_$application_projectname.conf
  project_name=${file/sm-config-}
  mkdir -p $application_install_path
  case "$application_type" in
      "grav")
          (
          # grav 1.5.1
          # GRAV_SHA1=5292b05d304329beefeddffbf9f542916012c221
          # grav 1.5.5
          GRAV_SHA1=af0433facdae1afeb1d973a66db2315c5022b10d
          cd $application_install_path
          curl -o grav-admin.zip -SL https://getgrav.org/download/core/grav-admin/${application_version} && \
          echo "$GRAV_SHA1 grav-admin.zip" | sha1sum -c - && \
          unzip grav-admin.zip
          rm grav-admin.zip
          )
          ;;
      "pagekit")
          (
          wget -q --show-progress https://github.com/pagekit/pagekit/releases/download/$application_version/pagekit-$application_version.zip
          unzip pagekit-$application_version.zip
          )
          ;;
      "symfony")
          (
          set -x
          cd $application_install_path
          if [ "$(ls -A $application_install_path)" ]; then
            # It seems we already have the app, so we do nothing
            true
          else
            # lets try to check out the scm
            git clone $application_scmurl .
          fi
          # copy project specific files (override)
          [ -d "/root/projects/$application_projectname" ] && cp -R /root/projects/$application_projectname/* $application_install_path
          [ ${application_do_sm_install:-true} == true ] && COMPOSER_HOME=$application_install_path $SM_CONF_DIR/symfony_manager.sh -l $SM_CONF_DIR/sm-config/$file -fdu install || true
          )
          ;;
      *)
        true
      ;;
  esac

done
