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

from oudb.models import EntityModel, KindModel
from antlr4 import *
from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from gen.javaLabeled.JavaLexer import JavaLexer
# Listeners
from analysis_passes.package_entity_listener import PackageListener

# Constants
FILE_KIND_ID = 1



class EntityGenerator:
    def __init__(self, path, tree):
        """Automatically generates all entities are required for create and createby reference."""
        file_manager = FileEntityManager(path)
        # Making entities
        self.path = path
        self.file_ent = file_manager.get_or_creat_file_entity()
        self.package_ent = PackageEntityManager(path, self.file_ent, tree)
        self.package_entities_list = self.package_ent.get_or_create_package_entity()
        self.package_string = self.package_ent.package_string

    def get_or_create_parent_entities(self, ctx):
        """Make all parents entities for create and createby reference."""
        result_entities = []
        parents = [ctx]
        current = ctx
        while current is not None:
            if type(current).__name__ == "ClassDeclarationContext" or \
                    type(current).__name__ == "MethodDeclarationContext" or \
                    type(current).__name__ == "InterfaceDeclarationContext":
                parents.append(current)
            current = current.parentCtx
        parents_entities = list(reversed(parents))
        for i in range(len(parents_entities)):
            entity = parents_entities[i]
            if i == 0:
                for row in self.package_entities_list:
                    if row[0] == self.path:
                        parent_entity_parent = row[1]
            else:
                print("parents_entities[i - 1].IDENTIFIER().getText()", parents_entities[i - 1].IDENTIFIER().getText())
                parent_entity_parent = EntityModel.get_or_none(_name=parents_entities[i - 1].IDENTIFIER().getText(),
                                                               _longname="",
                                                               _contents=entity.parentCtx.getText())
            if type(current).__name__ == "MethodDeclarationContext":
                parent_entity_name = entity.IDENTIFIER().getText()
                parent_entity_longname = self.package_string + entity.IDENTIFIER().getText()
                self.package_string = self.package_string + entity.IDENTIFIER().getText()
                parent_entity_contents = entity.getText()
                parent_entity_type = current.parentCtx.typeTypeOrVoid().getText()
                method_modifiers = self.get_method_accessor(entity)
                parent_entity_kind = self.get_method_kind(method_modifiers)
                method_ent = EntityModel.get_or_create(
                    _kind=parent_entity_kind,
                    _parent=parent_entity_parent,
                    _name=parent_entity_name,
                    _longname=parent_entity_longname,
                    _type=parent_entity_type,
                    _contents=parent_entity_contents)
                result_entities.append((parent_entity_kind, method_ent))
            if type(current).__name__ == "ClassDeclarationContext":
                parent_entity_name = entity.IDENTIFIER().getText()
                parent_entity_longname = self.package_string + entity.IDENTIFIER().getText()
                self.package_string = self.package_string + entity.IDENTIFIER().getText()
                parent_entity_contents = entity.getText()
                class_modifiers = self.get_class_accessor(entity)
                parent_entity_kind = self.get_class_kind(class_modifiers)
                method_ent = EntityModel.get_or_create(
                    _kind=parent_entity_kind,
                    _parent=parent_entity_parent,
                    _name=parent_entity_name,
                    _longname=parent_entity_longname,
                    _contents=parent_entity_contents)
                result_entities.append((parent_entity_kind, method_ent))
            if type(current).__name__ == "InterfaceDeclarationContext":
                parent_entity_name = entity.IDENTIFIER().getText()
                parent_entity_longname = self.package_string + entity.IDENTIFIER().getText()
                self.package_string = self.package_string + entity.IDENTIFIER().getText()
                parent_entity_contents = entity.getText()
                interface_modifiers = self.get_class_accessor(entity)
                parent_entity_kind = self.get_interface_kind(interface_modifiers)
                method_ent = EntityModel.get_or_create(
                    _kind=parent_entity_kind,
                    _parent=parent_entity_parent,
                    _name=parent_entity_name,
                    _longname=parent_entity_longname,
                    _contents=parent_entity_contents)
                result_entities.append((parent_entity_kind, method_ent))
        return result_entities

    @staticmethod
    def get_method_accessor(ctx):
        """will find the access level of parent method by passing the ctx."""
        parents = ""
        modifiers = []
        current = ctx
        while current is not None:
            if "ClassBodyDeclaration" in type(current.parentCtx).__name__:
                parents = (current.parentCtx.modifier())
                break
            current = current.parentCtx
        for x in parents:
            if x.classOrInterfaceModifier():
                modifiers.append(x.classOrInterfaceModifier().getText())
        return modifiers

    @staticmethod
    def get_class_accessor(ctx):
        """will find the access level of parent method by passing the ctx."""
        parents = ""
        modifiers = []
        current = ctx
        while current is not None:
            if "TypeDeclaration" in type(current.parentCtx).__name__:
                parents = (current.parentCtx.modifier())
                break
            current = current.parentCtx
        for x in parents:
            if x.classOrInterfaceModifier():
                modifiers.append(x.classOrInterfaceModifier().getText())
        return modifiers

    @staticmethod
    def get_method_kind(modifiers):
        """Return the kind ID based on the modifier"""
        if len(modifiers) == 0:
            modifiers.append("default")
        kind_selected = None
        for kind in KindModel.select().where(KindModel._name.contains("Method")):
            if EntityGenerator.checkModifiersInKind(modifiers, kind):
                if not kind_selected or len(kind_selected._name) > len(kind._name):
                    kind_selected = kind
        return kind_selected

    @staticmethod
    def get_class_kind(modifiers):
        """Return the kind ID based on the modifier"""
        if len(modifiers) == 0:
            modifiers.append("default")
        kind_selected = None
        for kind in KindModel.select().where(KindModel._name.contains("Class")):
            if EntityGenerator.checkModifiersInKind(modifiers, kind):
                if not kind_selected or len(kind_selected._name) > len(kind._name):
                    kind_selected = kind
        return kind_selected

    @staticmethod
    def get_interface_kind(modifiers):
        """Return the kind ID based on the modifier"""
        if len(modifiers) == 0:
            modifiers.append("default")
        kind_selected = None
        for kind in KindModel.select().where(KindModel._name.contains("Interface")):
            if EntityGenerator.checkModifiersInKind(modifiers, kind):
                if not kind_selected or len(kind_selected._name) > len(kind._name):
                    kind_selected = kind
        return kind_selected

    @staticmethod
    def checkModifiersInKind(modifiers, kind):
        """check if modifier is in kind and return it"""
        for modifier in modifiers:
            if modifier.lower() not in kind._name.lower():
                return False
        return True


class FileEntityManager:
    """This class is for creating and updating file entity in database."""

    def __init__(self, path):
        """Define Name, long Name as address of file and content of it by simply passing path in __init__ method."""
        file_reader = open(path.replace("/", "\\"), mode='r')
        self.path = path
        self.name = path.split("\\")[-1]
        self.longname = path.replace("/", "\\")
        self.contents = file_reader.read()
        file_reader.close()

    def get_or_creat_file_entity(self):
        """Create or get if it exists a file entity and return it according to object fields."""
        file_ent, success = EntityModel.get_or_create(
            _kind=FILE_KIND_ID,
            _name=self.name,
            _longname=self.longname,
            _contents=self.contents)
        print("processing file:", file_ent)
        return file_ent

    @staticmethod
    def get_file_entity(longname):
        """get or return none for a file entity abased on its longname as address."""
        file_ent = EntityModel.get_or_none(
            _kind=FILE_KIND_ID,
            _longname=longname
        )
        return file_ent


class PackageEntityManager:
    """This class is for creating and updating Package entity in database."""

    def __init__(self, path, file_ent, tree):
        """Define the path to the file for finding package entity."""
        file_reader = open(path.replace("/", "\\"), mode='r')
        self.path = path
        self.contents = file_reader.read()
        self.package_string = None
        self.file_ent = file_ent
        self.tree = tree
        file_reader.close()

    def get_or_create_package_entity(self):
        """Create or get if it exists a package entity and return it according to object fields."""
        listener_class = PackageListener()
        result = []
        listener_class.package_data = []
        walker = ParseTreeWalker()
        walker.walk(listener=listener_class, t=self.tree)
        package_data = listener_class.package_data
        if len(package_data) != 0:
            for i in range(len(package_data)):
                package = package_data[i]
                if EntityModel.get_or_none(_longname=package["package_longname"]) is None:
                    parent_package = package_data[i - 1]
                    longname = parent_package['package_longname'] if i > 0 else ""
                    parent_package_entity = EntityModel.get_or_none(_longname=longname)
                    package_ent, success = EntityModel.get_or_create(
                        _kind=72,
                        _name=package['package_name'],
                        _longname=package['package_longname'],
                        _parent=parent_package_entity)
                    self.package_string = package['package_longname']
                    result.append((self.path, package_ent))
        else:
            package_ent, success = EntityModel.get_or_create(
                _kind=73,
                _name="Unnamed Package",
                _longname="Unnamed Package",
                _parent=self.file_ent,
                _contents=self.contents)
            self.package_string = ""
            result.append((self.path, package_ent))
        return result

    @staticmethod
    def get_package_entity(name, longname):
        """get or return none for a package entity abased on its longname as address."""
        package_ent = EntityModel.get_or_none(
            _kind=73 if name == '' else 72,
            _longname=longname
        )
        return package_ent

# class ParentEntityManager:
#     """This class is for creating and updating Method entity in database."""
#
#     def __init__(self, ctx, path):
#         """Define Name, long Name as package that this method is in file, content of it and also its modifier and
#         accessor by simply passing the ctx to __init__ method."""
#         method_type = self.get_parent_method_type(ctx)
#         method_access = self.get_parent_method_accessor(ctx)
#         method_content = self.get_parent_method_contents(ctx)
#         method_name, parent = self.get_parent_names()
#         self.path = path
#         self.kind = self.get_method_kind(method_access)
#         self.parent = 1
#         self.name = method_name
#         self.longname = 1
#         self.type = method_type
#         self.contents = method_content
#
#     @staticmethod
#     def get_parent_names(ctx):
#         parents = []
#         entities = []
#         current = ctx
#         while current is not None:
#             if type(current).__name__ == "ClassDeclarationContext" or type(current).__name__ == "MethodDeclarationContext" or type(current).__name__ == "InterfaceDeclarationContext":
#                 parents.append(current.IDENTIFIER().getText())
#             current = current.parentCtx
#         parents_list = list(reversed(parents))
#         return parents_list[-1], ".".join(parents_list)
#
#
#
#
#     @staticmethod
#     def get_parent_method_type(ctx):
#         """will find the type of parent method by passing the ctx."""
#         method_type = ""
#         current = ctx
#         while current is not None:
#             if type(current.parentCtx).__name__ == "MethodDeclarationContext":
#
#                 break
#             current = current.parentCtx
#         return method_type
#
#     @staticmethod
#     def get_parent_method_contents(ctx):
#         """will find the content of parent method by passing the ctx."""
#         method_contents = ""
#         current = ctx
#         while current is not None:
#             if type(current.parentCtx).__name__ == "MethodDeclarationContext":
#                 method_contents = current.parentCtx.getText()
#                 break
#             current = current.parentCtx
#         return method_contents
#
#     @staticmethod
#     def get_parent_method_accessor(ctx):
#         """will find the access level of parent method by passing the ctx."""
#         parents = ""
#         modifiers = []
#         current = ctx
#         while current is not None:
#             if "ClassBodyDeclaration" in type(current.parentCtx).__name__:
#                 parents = (current.parentCtx.modifier())
#                 break
#             current = current.parentCtx
#         for x in parents:
#             if x.classOrInterfaceModifier():
#                 modifiers.append(x.classOrInterfaceModifier().getText())
#         return modifiers
#
#     @staticmethod
#     def get_method_kind(modifiers):
#         """Return the kind ID based on the modifier"""
#         if len(modifiers) == 0:
#             modifiers.append("default")
#         kind_selected = None
#         for kind in KindModel.select().where(KindModel._name.contains("Method")):
#             if checkModifiersInKind(modifiers, kind):
#                 if not kind_selected or len(kind_selected._name) > len(kind._name):
#                     kind_selected = kind
#         return kind_selected
#
#     @staticmethod
#     def checkModifiersInKind(modifiers, kind):
#         for modifier in modifiers:
#             if modifier.lower() not in kind._name.lower():
#                 return False
#         return True
