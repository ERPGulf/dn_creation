from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in dn_auto_creation/__init__.py
from dn_auto_creation import __version__ as version

setup(
	name="dn_auto_creation",
	version=version,
	description="Auto creation of delivery note when sales return is made",
	author="erpgulf.com",
	author_email="support@erpgulf.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
