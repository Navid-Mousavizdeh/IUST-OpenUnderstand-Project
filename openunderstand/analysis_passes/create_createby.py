"""This module is for create, Read of entities of different kinds in project,

in this module there are many classes for each individual entity as follows:
    1. File
    2. Package
    3. Parent Entities:
        Class
        Method
        Interface
"""

__author__ = "Navid Mousavizadeh, Amir Mohammad Sohrabi, Sara Younesi, Deniz Ahmadi"
__copyright__ = "Copyright 2022, The OpenUnderstand Project, Iran University of Science and technology"
__credits__ = ["Dr.Parsa", "Dr.Zakeri", "Mehdi Razavi", "Navid Mousavizadeh", "Amir Mohammad Sohrabi", "Sara Younesi",
               "Deniz Ahmadi"]
__license__ = "GPL"
__version__ = "1.0.0"

__author__ = 'Shaghayegh Mobasher , Setayesh kouloubandi ,Parisa Alaie'
__version__ = '0.1.0'

from openunderstand.gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener
from openunderstand.gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from openunderstand.analysis_passes.entity_manager import EntityGenerator


class CreateAndCreateBy(JavaParserLabeledListener):
    create = []

    def __init__(self, entity_manager_object):
        self.entity_manager = entity_manager_object

    def enterExpression4(self, ctx: JavaParserLabeled.Expression4Context):
        print("SAAAAAAAG KASIFFFFFF")
        parents = self.entity_manager.get_or_create_parent_entities(ctx)

        # if ctx.creator().classCreatorRest():
        #     allrefs = class_properties.ClassPropertiesListener.findParents(ctx)  # self.findParents(ctx)
        #     refent = allrefs[-1]
        #     entlongname = ".".join(allrefs)
        #     [line, col] = str(ctx.start).split(",")[3].split(":")
        #
        #     self.create.append({"scopename": refent, "scopelongname": entlongname, "scopemodifiers": modifiers,
        #                         "scopereturntype": mothodedreturn, "scopecontent": methodcontext,
        #                         "line": line, "col": col[:-1], "refent": ctx.creator().createdName().getText(),
        #                         "scope_parent": allrefs[-2] if len(allrefs) > 2 else None,
        #                         "potential_refent": ".".join(
        #                             allrefs[:-1]) + "." + ctx.creator().createdName().getText()})
