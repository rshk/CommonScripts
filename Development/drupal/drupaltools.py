"""
Tools for the Drupal administration scripts

.. WARNING:: This is just a work-in-progress -- nothing usable here yet!
"""

import sys,os
from ConfigParser import RawConfigParser
import subprocess

DEFAULT_DRUSH_COMMAND = '/opt/drush/drush'
CFG_FILE = os.path.join(os.environ['HOME'], '.drupal-platform.ini')

class Drush:
    drush_command = None
    drupal_root = None
    site_uri = None
    process = None
    
    def __init__(self, drush_command=None, drupal_root=None, site_uri=None):
        self.drush_command = drush_command or DEFAULT_DRUSH_COMMAND
        self.drupal_root = drupal_root or os.getcwd()
        self.site_uri = site_uri
    
    def run(self, args, drupal_root=None, site_uri=None):
        """
        Execute a Drush command. The subprocess.Popen object is in
        self.process, so that stdout/stderr/return_code can be
        accesses any time from the caller.
        """
        if not drupal_root:
            drupal_root = self.drupal_root
        if not site_uri:
            site_uri = self.site_uri
        _args = [self.drush_command]
        if drupal_root:
            _args.append('--root=%s' % drupal_root)
        if site_uri:
            _args.append('--uri=%s' % site_uri)
        _args += args
        self.process = subprocess.Popen(_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = self.process.wait()
        return ret == 0
    
    def get_version(self):
        self.run(['--version'])
        _text = self.process.stdout.readline().strip().split()
        if _text[0] == 'drush' and _text[1] == 'version':
            return _text[2]
        else:
            # Unrecognised format
            return " ".join(_text)

class DrupalPlatform:
    """Class to administer a Drupal platform"""
    
    drupal_root = None
    
    @property
    def drupal_version(self):
        return None # Not supported
    
    

class DrupalSite:
    """Class to administer/represent a Drupal site"""
    
    platform = None
    domain_name = None
    site_directory = None # should be os.path.join(platform.drupal_root, 'sites', domain_name)
    
    def __init__(self, platform=None, domain_name=None):
        self.platform = platform
        self.domain_name = domain_name
        try:
            self.site_directory = os.path.join(platform.drupal_root, 'sites', domain_name)
        except:
            self.site_directory = None
    
    def list_sites(self):
        """List the available sites in the platform.
        We do not rely on drush site-alias since sometimes it gets
        unwanted results, just scan the sites directory for sub-directories
        and symlinks containing `settings.php` file.
        """
        pass

class ServerPlatform:
    """Class to represent/manage a Server Platform"""
    
    http_server = None # Only Apache is supported ATM
    db_server = None # Only MySQL is supported ATM
    
    def __init__(self, http_server=None, db_server=None):
        self.http_server = http_server.lower() if http_server else None
        self.db_server = db_server.lower() if db_server else None
    
    def create_virtualhost_config(self, site):
        """Create the VirtualHost configuration file for a given site"""
        pass
    
    pass
