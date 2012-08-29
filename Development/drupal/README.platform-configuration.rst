Platform configuration file
===========================

The platform configuration file is used by the platform management scripts
(see `README.rst`). This file contains a brief explaination on the syntax to
be used when writing platform configuration files.

Example `.drupal-platform.ini`::

    [drupal]
    drupal_root=/path/to/drupal-6
    
    [webserver]
    domain_suffix=drupal6.example.com
    www_user=www-data

    [database]
    type=mysqli
    root_user=root
    root_password=mypass
    host=localhost
    db_name_prefix=d6_
    drupal_user=auto
    drupal_password=auto

- Scripts usually accept a `-C <file>` to specify a different configuration file.
  By default, `./.drupal-platform.ini` is used as configuration file.
- If not specified, `drupal_root` defaults to the current working directory.
- `domain_suffix` is appended to the specified site name in order to generate
  the whole domain name. This should be configured as a wildcard in the webserver
  VirtualHost.
- Supported database types are `mysql` and `mysqli`. PostgreSQL support will
  be added in the future.
- `db_name_prefix` is used to prefix the database name (that defaults to the
  specified site name, with symbols converted to `_` and dots converted to `__`).
