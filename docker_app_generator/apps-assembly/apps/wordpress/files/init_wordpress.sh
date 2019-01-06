#!/bin/bash

source /srv/wordpress/utils_wordpress.sh

# update nginx configuration if there is an update conf file
if [ -f /srv/nginx-config/update_nginx_conf ]; then
  echo "$(cat /srv/nginx-config/update_nginx_conf) /srv/nginx-config/default-wordpress-nginx.conf"| bash
fi

install_wordpress
if [ -d /srv/projects/ ]; then
  for wp_project in `find /srv/projects/ -not -path '*/\.*' -type f -printf "%f\n"| egrep "^wp-config"`
  do
    source /srv/projects/$wp_project
    deploy_wordpress $WP_NAME ${WP_LANG:-"ES_es"} ${WP_HOST:-"localhost"}
  done
fi
