"""This module is for create, Read of entities of type package."""

__author__ = "Navid Mousavizadeh, Amir Sohrabi, Sara Younesi, Deniz Ahmadi"
__copyright__ = "Copyright 2022, The OpenUnderstand Project, Iran University of Science and technology"
__credits__ = ["Dr.Parsa", "Dr.Zakeri", "Mehdi Razavi", "Navid Mousavizadeh", "Amir Sohrabi", "Sara Younesi",
               "Deniz Ahmadi"]
__license__ = "GPL"
__version__ = "1.0.0"

from openunderstand.gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener
from openunderstand.gen.javaLabeled.JavaParserLabeled import JavaParserLabeled


class PackageListener(JavaParserLabeledListener):
    """A listener class for detecting package"""

    package_data = {
        'package_name': '',
        'package_longname': ''
    }

    def enterPackageDeclaration(self, ctx: JavaParserLabeled.PackageDeclarationContext):
        package_data['package_longname'] = ctx.getText().replace('package', '')
        package_data['package_name'] = package_data['package_longname'].split('.')[-1]
