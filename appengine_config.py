# appengine_config.py
import os
import google
from google.appengine.ext import vendor

lib_directory = os.path.dirname(__file__) + '/lib'

# Change where to find the google package (point to the lib/ directory)
google.__path__ = [os.path.join(lib_directory, 'google')] + google.__path__

# Add any libraries install in the "lib" folder.
vendor.add(lib_directory)

