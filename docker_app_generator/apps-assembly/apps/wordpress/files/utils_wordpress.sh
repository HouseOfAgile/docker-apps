#!/bin/bash

WP_ROOT_PATH=${WP_ROOT_PATH}

# update the wordpress archive if not present and return the path where
function retrieve_wordpress() {
  if [ -z "$1" ]; then
    wp_version_name=latest
  else
    wp_version_name=wordpress-${1}
  fi
  if [ ! -f /srv/wordpress/${wp_version_name}.tar.gz ]; then
    curl -SsL http://wordpress.org/${wp_version_name}.tar.gz -o /srv/wordpress/${wp_version_name}.tar.gz
  fi

  # return the file name
  echo "/srv/wordpress/${wp_version_name}.tar.gz"
}


function deploy_wordpress() {
  set -x
  if [ -z "$1" ]; then
    echo -e "\nPlease call '$0 <wp_name> <?wp_lang:-EN_en> <?wp_host:-localhost>' to run this command!\n"
    exit 1
  fi
  wp_name=$1
  wp_lang=${2:-"EN_en"}
  wp_host=${3:-"localhost"}
  wp_version=${4}
  if [ ! -d ${WP_ROOT_PATH}/$wp_name -o "$WP_FORCE_INSTALL" = true ]; then
    wp_version_file=`retrieve_wordpress $wp_version`

    # deal with version
    mkdir -p ${WP_ROOT_PATH}/$wp_name
    tar --strip-components=1 -xzf ${wp_version_file} -C ${WP_ROOT_PATH}/$wp_name
  fi
  if [ ! -f ${WP_ROOT_PATH}/$wp_name/wp-config.php ]; then
    # mysql username should be shorter than 15 characters
    short_name=`echo $wp_name |cut -c1-11`
    WORDPRESS_DB_NAME="wp_db_$short_name"
    WORDPRESS_DB_USER="wp_$short_name"
    WORDPRESS_DB_PASSWORD=`pwgen -c -n -1 12`

    sed -e "s/database_name_here/$WORDPRESS_DB_NAME/
    s/username_here/$WORDPRESS_DB_USER/
    s/password_here/$WORDPRESS_DB_PASSWORD/
    s/localhost/$MYSQL_HOST/
    s/define('WPLANG', '');/define('WPLANG', '$wp_lang');/
    /'AUTH_KEY'/s/put your unique phrase here/`pwgen -c -n -1 65`/
    /'SECURE_AUTH_KEY'/s/put your unique phrase here/`pwgen -c -n -1 65`/
    /'LOGGED_IN_KEY'/s/put your unique phrase here/`pwgen -c -n -1 65`/
    /'NONCE_KEY'/s/put your unique phrase here/`pwgen -c -n -1 65`/
    /'AUTH_SALT'/s/put your unique phrase here/`pwgen -c -n -1 65`/
    /'SECURE_AUTH_SALT'/s/put your unique phrase here/`pwgen -c -n -1 65`/
    /'LOGGED_IN_SALT'/s/put your unique phrase here/`pwgen -c -n -1 65`/
    /'NONCE_SALT'/s/put your unique phrase here/`pwgen -c -n -1 65`/
    /Happy blogging/s/$/\nif (isset(\$_SERVER['HTTP_X_FORWARDED_PROTO']) \&\& \$_SERVER['HTTP_X_FORWARDED_PROTO'] == 'https')\n  \$_SERVER['HTTPS'] = 'on';\n/" ${WP_ROOT_PATH}/$wp_name/wp-config-sample.php > ${WP_ROOT_PATH}/$wp_name/wp-config.php

    # Download nginx helper plugin
    #curl -O `curl -i -s http://wordpress.org/plugins/nginx-helper/ | egrep -o "http://downloads.wordpress.org/plugin/[^']+"`
    #unzip -o nginx-helper.*.zip -d ${WP_ROOT_PATH}/$wp_name/wp-content/plugins
    #chown -R www-data:www-data ${WP_ROOT_PATH}/$wp_name/wp-content/plugins/nginx-helper

    # Activate nginx plugin and set up pretty permalink structure once logged in
    cat << ENDL >> ${WP_ROOT_PATH}/$wp_name/wp-config.php
\$plugins = get_option( 'active_plugins' );
if ( count( \$plugins ) === 0 ) {
  require_once(ABSPATH .'/wp-admin/includes/plugin.php');
  \$wp_rewrite->set_permalink_structure( '/%postname%/' );
  \$pluginsToActivate = array( 'nginx-helper/nginx-helper.php' );
  foreach ( \$pluginsToActivate as \$plugin ) {
  if ( !in_array( \$plugin, \$plugins ) ) {
    activate_plugin( '${WP_ROOT_PATH}/www/wp-content/plugins/' . \$plugin );
  }
  }
}
ENDL
    # update nginx configuration
    cat /srv/nginx-config/default-wordpress-nginx.conf | sed "s/__project_name__/$wp_name/g;s#__project_path__#${WP_ROOT_PATH}/$wp_name#g;s/__project_hosts__/$wp_host/g"  > /etc/nginx/sites-available/project_$wp_name.conf
    ln -s /etc/nginx/sites-available/project_$wp_name.conf /etc/nginx/sites-enabled/project_$wp_name.conf
    service nginx reload

    chown -R www-data:www-data ${WP_ROOT_PATH}/$wp_name

    MYSQL_USER=${MYSQL_ROOT_USER:-"root"}
    MYSQL_PASSWORD=${MYSQL_ROOT_PASSWORD:-""}
    MYSQL_HOST=${MYSQL_HOST=:-""}
    [ $MYSQL_PASSWORD"x" == "x" -o $MYSQL_USER"x" == "x" -o $MYSQL_HOST"x" == "x" ] && \
    echo "Can't find Mysql env variables" && exit 1

    echo "Create Database"
    mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD -e "DROP DATABASE IF EXISTS $WORDPRESS_DB_NAME;CREATE DATABASE $WORDPRESS_DB_NAME;"
    echo "Add user $WORDPRESS_DB_USER"
    mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASSWORD -e "GRANT ALL PRIVILEGES ON $WORDPRESS_DB_NAME.* TO '$WORDPRESS_DB_USER'@'%' IDENTIFIED BY '$WORDPRESS_DB_PASSWORD'; FLUSH PRIVILEGES;"
  fi

  #This is so the passwords show up in logs.
  echo "Wordpress installed for $wp_name"
  echo "- Wordpress User created: $WORDPRESS_DB_USER"
  echo "- Mysql Database created: $WORDPRESS_DB_NAME"
  echo "- Wordpress User password: $WORDPRESS_DB_PASSWORD"
}

function update_wordpress() {
  true
}

function backup_wordpress(){
  if [ -z "$1" ]; then
    echo -e "\nPlease call '$0 <wp_name>' to run this command!\n"
    exit 1
  fi
  wp_path=$1
  if [ -d "${WP_ROOT_PATH}/$wp_path" ]; then
    echo 'Backup installed wordpress in $wp_path'
    tar --create --gzip -vv --directory="${WP_ROOT_PATH}/$wp_path" --file="/srv/backups/backup_`date '+%Y%m%d'`.tar.gz" "./"

    echo 'creating database dump'
    mysqldump -h $MYSQL_ENV_MYSQL_HOST --add-drop-table -u$MYSQL_ENV_MYSQL_USER -p $MYSQL_ENV_MYSQL_DATABASE --password=$MYSQL_ENV_MYSQL_PASSWORD | bzip2 -c > /backups/backup_`date '+%Y%m%d'`.sql.bz2
  fi
}

function restore_wordpress(){
  true
}
