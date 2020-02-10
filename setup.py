from setuptools import setup, find_namespace_packages, Extension
import os

def parse_requirements( filename ):
    with open( filename ) as fp:
        return list(filter(None, (r.strip('\n ').partition('#')[0] for r in fp.readlines())))

def load_source(name, path):
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location(name, path)
    mod  = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

VER = load_source("version", 'pyqgisservercontrib/lizmapaccesspolicy/version.py')

version_tag = "{}".format(VER.__version__)

kwargs = {}

with open('README.md') as f:
    kwargs['long_description'] = f.read()

# Parse requirement file and transform it to setuptools requirements'''
requirements = 'requirements.txt'
if os.path.exists(requirements):
    kwargs['install_requires']=parse_requirements(requirements)

setup(
    name='pyqgiservercontrib-lizmap-access-policy',
    version=version_tag,
    author='3Liz',
    author_email='infos@3liz.org',
    maintainer='David Marteau',
    maintainer_email='dmarteau@3liz.org',
    description=VER.__description__,
    url='https://github.com/pyqgiservercontrib-lizmap-access-policy',
    python_requires=">=3.5",
    packages=find_namespace_packages(include=['pyqgisservercontrib.*']),
    entry_points={
        'qgssrv_contrib_access_policy': [
            'lizmapaccesspolicy = pyqgisservercontrib.lizmapaccesspolicy.filters:register_policy',
        ]
    },
    namespace_packages=['pyqgisservercontrib'],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    **kwargs
)

