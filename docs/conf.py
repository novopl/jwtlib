# -*- coding: utf-8 -*-
import os
import sys
import sphinx_rtd_theme


project = u"jwtlib"
copyright = u"2019, Mateusz 'novo' Klos"
author = u"Mateusz 'novo' Klos"

_testbed = None


def repo_path(path):
    ret = os.path.join(os.path.dirname(__file__), '..', path)
    return os.path.normpath(ret)


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.imgmath',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

sys.path.insert(1, repo_path('src'))
import jwtlib

version = release = jwtlib.__version__
doctest_test_doctest_blocks='default'
templates_path = [repo_path('docs/_templates')]
source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = [
    '_build',
    'env',
    'tmp',
    '.tox',
    'Thumbs.db',
    '.DS_Store'
]
todo_include_todos = False
intersphinx_mapping = {'https://docs.python.org/': None}

pygments_style = 'default'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme = "sphinx_rtd_theme"
html_static_path = []
htmlhelp_basename = 'rdp'

latex_elements = {}
latex_documents = [
    (master_doc, 'jwtlib.tex', 'jwtlib Documentation',
     'Mateusz \'novo\' Klos', 'manual'),
]
man_pages = [
    (master_doc, 'jwtlib', 'jwtlib Documentation', [author], 1)
]
texinfo_documents = [
    (master_doc, 'jwtlib', 'jwtlib Documentation',
     author, 'jwtlib', 'One line description of project.',
     'Miscellaneous'),
]
