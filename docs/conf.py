# -*- coding: utf-8 -*-
"""
SpicyCMS Mediacenter module documentation build configuration file
"""
from __future__ import unicode_literals

import os
import sys

sys.path.insert(0, os.path.abspath('assets'))
sys.path.insert(0, os.path.abspath('../src/spicy'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo'
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = 'SpicyCMS Mediacenter module'
copyright = '2013, SpicyTeam'

version = '0.1'
release = '0.1'

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'nature'

html_static_path = ['_static']

htmlhelp_basename = 'SpicyCMSMediacenterdoc'

latex_elements = {}

latex_documents = [
    ('index',
     'SpicyCMSMediacenter.tex',
     'SpicyCMS Mediacenter Documentation',
     'SpicyTeam',
     'manual'),
]

man_pages = [
    ('index', 'spicycmslight', 'SpicyCMS Light Documentation',
     ['SpicyTeam'], 1)
]

texinfo_documents = [
  ('index', 'SpicyCMSLight', 'SpicyCMS Light Documentation',
   'SpicyTeam', 'SpicyCMSLight', 'One line description of project.',
   'Miscellaneous'),
]
