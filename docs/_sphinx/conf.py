"""Sphinx configuration for ooai-skills documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

project = "ooai-skills"
copyright = "2025, William R. Astley"
author = "William R. Astley"
release = "0.1.0"

extensions = [
    # Autodoc
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "autoapi.extension",
    # Markdown
    "myst_parser",
    # UI
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxcontrib.mermaid",
]

# --- AutoAPI (generates API docs from source) ---
autoapi_type = "python"
autoapi_dirs = ["../../src/ooai_skills"]
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autoapi_ignore = ["*/__main__.py"]
autoapi_keep_files = True

# --- MyST (Markdown) ---
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# --- Theme: Furo ---
html_theme = "furo"
html_title = "ooai-skills"
html_theme_options = {
    "source_repository": "https://github.com/ooai/tools/ooai-skills",
    "source_branch": "main",
    "source_directory": "docs/_sphinx/",
    "navigation_with_keys": True,
}

# --- Napoleon (Google-style docstrings) ---
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

# --- Autodoc ---
autodoc_member_order = "bysource"
autodoc_typehints = "description"
always_document_param_types = True

# --- Intersphinx ---
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# --- Copy button ---
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

# --- General ---
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_static_path = []
