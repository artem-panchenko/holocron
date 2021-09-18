"""
    Sphinx configuration file for building Holocron"s documentation.
"""

from __future__ import unicode_literals

import os
import re
import sys

import pkg_resources

# project settings
project = "Holocron"
copyright = "2015, the Holocron Team"
release = pkg_resources.get_distribution("holocron").version
version = re.sub("[^0-9.]", "", release)

# sphinx settings
extensions = ["sphinx.ext.autodoc"]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ["_build"]
pygments_style = "default"

# html settings
html_static_path = ["_static"]

if not os.environ.get("READTHEDOCS") == "True":
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Unfortunately, Sphinx doesn't support code highlighting for standard
# reStructuredText `code` directive. So let's register 'code' directive
# as alias for Sphinx's own implementation.
#
# https://github.com/sphinx-doc/sphinx/issues/2155
from docutils.parsers.rst import directives
from sphinx.directives.code import CodeBlock

directives.register_directive("code", CodeBlock)

# flake8: noqa
