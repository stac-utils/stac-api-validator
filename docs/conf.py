"""Sphinx configuration."""

project = "STAC API Validator"
author = "Phil Varner"
copyright = "2022, Phil Varner"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
