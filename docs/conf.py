"""Sphinx configuration."""
project = "TikTok Dynamics"
author = "Anders Giovanni Møller"
copyright = "2023, Anders Giovanni Møller"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
