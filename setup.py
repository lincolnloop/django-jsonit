from distutils.core import setup
from jsonit import get_version

try:
    long_description = open('README', 'rt').read()
except IOError:
    long_description = ''

setup(
    name='django-jsonit',
    version=get_version(),
    description="A JSON helper library for Django apps.",
    long_description=long_description,
    author='Chris Beaven',
    author_email='chris@lincolnloop.com',
    license='BSD',
    url='http://github.com/lincolnloop/django-jsonit',
    packages=[
        'jsonit',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
