"""This module is for create, Read of entities of type package."""

__author__ = "Navid Mousavizadeh, Amir Mohammad Sohrabi, Sara Younesi, Deniz Ahmadi"
__copyright__ = "Copyright 2022, The OpenUnderstand Project, Iran University of Science and technology"
__credits__ = ["Dr.Parsa", "Dr.Zakeri", "Mehdi Razavi", "Navid Mousavizadeh", "Amir Mohammad Sohrabi", "Sara Younesi",
               "Deniz Ahmadi"]
__license__ = "GPL"
__version__ = "1.0.0"

from openunderstand.gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener
from openunderstand.gen.javaLabeled.JavaParserLabeled import JavaParserLabeled


class VariableListener(JavaParserLabeledListener):
    """A listener class for detecting variables"""

    def __init__(self, entity_manager_object):
        self.entity_manager = entity_manager_object
        self.package = ""
        self._class = ""
        self.parent = ""
        self.type = None
        self.modifiers = []
        self.value = None

    # package
    def enterPackageDeclaration(self, ctx: JavaParserLabeled.PackageDeclarationContext):
        self.package = ctx.qualifiedName().getText()

    # class parent
    def enterClassDeclaration(self, ctx: JavaParserLabeled.ClassDeclarationContext):
        self._class = ctx.IDENTIFIER().getText() + '.'
        self.parent = ctx.IDENTIFIER().getText()

    # exit class parent
    def exitClassDeclaration(self, ctx: JavaParserLabeled.ClassDeclarationContext):
        self._class = ""

    # method parent
    def enterMethodDeclaration(self, ctx: JavaParserLabeled.MethodDeclarationContext):
        self.parent = self._class + ctx.IDENTIFIER().getText()

    # interface parent
    def enterInterfaceDeclaration(self, ctx: JavaParserLabeled.InterfaceDeclarationContext):
        self.parent = ctx.IDENTIFIER().getText()

    # interface modifiers
    def enterInterfaceBodyDeclaration(self, ctx: JavaParserLabeled.InterfaceBodyDeclarationContext):
        self.modifiers = ctx.modifier()
        for i in range(len(self.modifiers)):
            self.modifiers[i] = self.modifiers[i].getText()

    # class modifiers
    def enterClassBodyDeclaration2(self, ctx: JavaParserLabeled.ClassBodyDeclaration2Context):
        self.modifiers = ctx.modifier()
        for i in range(len(self.modifiers)):
            self.modifiers[i] = self.modifiers[i].getText()

    # method modifiers and data type
    def enterLocalVariableDeclaration(self, ctx: JavaParserLabeled.LocalVariableDeclarationContext):
        self.modifiers = ctx.variableModifier()
        self.type = ctx.typeType().getText()
        for i in range(len(self.modifiers)):
            self.modifiers[i] = self.modifiers[i].getText()
        self.modifiers.append('local')

    # interface variable type
    def enterConstDeclaration(self, ctx: JavaParserLabeled.ConstDeclarationContext):
        self.type = ctx.typeType().getText()

    #
    def enterFieldDeclaration(self, ctx: JavaParserLabeled.FieldDeclarationContext):
        self.type = ctx.typeType().getText()

    # method parameters modifiers and data type
    def enterFormalParameter(self, ctx: JavaParserLabeled.FormalParameterContext):
        self.modifiers = None
        self.type = ctx.typeType().getText()

    # value
    def enterVariableInitializer1(self, ctx:JavaParserLabeled.VariableInitializer1Context):
        self.value = ctx.getText()

    # interface variable
    def enterConstantDeclarator(self, ctx: JavaParserLabeled.ConstantDeclaratorContext):
        res = {"name": ctx.IDENTIFIER().getText(),
               "parent_longname": self.package + '.' + self.parent,
               "type": self.type,
               "modifiers": self.modifiers,
               "value": self.value}
        self.entity_manager.get_or_create_variable_entity(res)
        print(self.modifiers, self.package, self.parent, self.type, ctx.IDENTIFIER().getText())

    # variable
    def enterVariableDeclaratorId(self, ctx: JavaParserLabeled.VariableDeclaratorIdContext):
        res = {"name": ctx.IDENTIFIER().getText(),
               "parent_longname": self.package + '.' + self.parent,
               "type": self.type,
               "modifiers": self.modifiers,
               "value": self.value}
        self.entity_manager.get_or_create_variable_entity(res)
        print(self.modifiers, self.package, self.parent, self.type, ctx.IDENTIFIER().getText())
