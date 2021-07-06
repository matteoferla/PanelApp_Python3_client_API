########################################################################################################################
__doc__ = 'README.md'
__author__ = "Matteo Ferla"
__url__ = 'https://github.com/matteoferla/PanelApp_Python3_client_API'
__email__ = "matteo.ferla@gmail.com"
__date__ = "6 July 2021 A.D."
__license__ = "MIT"
__version__ = "0.1"
__citation__ = "NA"

# ---------- imports  --------------------------------------------------------------------------------------------------
# remember it's `python setup.py sdist` and `python -m twine upload dist/rdkit_to_params-1.0.5.tar.gz`

from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# ---------- setuptools.setup ------------------------------------------------------------------------------------------

setup(
    name='PanelApp_client_API',
    version='0.1',
    packages=find_packages(), #['panel_app_query'],
    url=__url__,
    license=__license__,
    author=__author__,
    author_email=__email__,
    description='unofficial Python3 client API (SDK) for Genomics England (GEL) PanelApp',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['pandas'],

)
