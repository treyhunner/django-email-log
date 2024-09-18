from setuptools import setup, find_packages
import email_log


setup(
    name="django-email-log",
    version=email_log.__version__,
    author="Trey Hunner",
    author_email="trey@treyhunner.com",
    description="Django email backend that logs all emails",
    long_description="\n\n".join(
        (
            open("README.rst").read(),
            open("CHANGES.rst").read(),
        )
    ),
    long_description_content_type="text/x-rst",
    url="https://github.com/treyhunner/django-email-log",
    license="LICENSE",
    packages=find_packages(),
    install_requires=["Django >= 2.2.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
    ],
    include_package_data=True
)
