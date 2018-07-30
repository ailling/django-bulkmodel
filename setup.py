import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-bulkmodel',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    license='Apache Software License',
    description='Adds missing features to Django ORM for working with data in bulk operations',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/ailling/django-bulkmodel',
    author='Alan Illing',
    author_email='alanilling@protonmail.com',
    keywords = ['django', 'orm', 'database', 'bulk', 'data'],

    install_requires= [
        'django>=1.9',
    ],

    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends'
    ],
)
