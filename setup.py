from setuptools import setup, find_packages
import email_log


setup(
    name='django-email-log',
    version=email_log.__version__,
    author='Trey Hunner',
    author_email='trey@treyhunner.com',
    description='Django email backend that logs all emails',
    long_description='\n\n'.join((
        open('README.rst').read(),
        open('CHANGES.rst').read(),
    )),
    url='https://github.com/treyhunner/django-email-log',
    license='LICENSE',
    packages=find_packages(),
    install_requires=['Django >= 2.2.0'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
    tests_require=['Django >= 2.2.0'],
    include_package_data=True,
    test_suite='runtests.runtests',
)
