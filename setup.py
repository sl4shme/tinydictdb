from setuptools import setup, find_packages
from codecs import open
from os import path
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tinydictdb',
    version='1.3.1',
    description='A tiny flat file (JSON/YAML) dictionnaries database.',
    long_description=long_description,
    url='https://github.com/sl4shme/tinydictdb',
    author='Pierre-Arthur MATHIEU',
    author_email='pi3rra@root.gg',
    license='Apache Software License',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],

    keywords='json database yaml dict dictionnary',

    packages=find_packages(),
)
