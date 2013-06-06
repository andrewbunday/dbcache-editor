################################################################################
#
# Name: default_settings.py
# Description: Default configuration settings for PyReproWeb. Either edit these,
#              or provide a file via PYREPROWEB_SETTINGS env var.
# Date: 28th Oct 2012
#
################################################################################

# Flask
DEBUG = True

# Application Settings
APP_NAME = 'dbCacheEditor'

# WSGI Settings
SERVER_PORT = 5000
LOGFILE = "/var/tmp/%s.log" % APP_NAME.lower()
