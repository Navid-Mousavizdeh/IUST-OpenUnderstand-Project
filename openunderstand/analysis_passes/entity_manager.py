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
from analysis_passes.class_properties import ClassPropertiesListener, InterfacePropertiesListener

# Constants
FILE_KIND_ID = 1


def get_created_entity(name):
    entity = EntityModel.get_or_none(_name=name)
    if entity is None:
        raise Exception("No entity found with this name.")
    return entity


class EntityGenerator:
    def __init__(self, path, tree):
        """Automatically generates all entities are required for create and createby reference."""
        file_manager = FileEntityManager(path)
        # Making entities
        self.path = path
        self.tree = tree
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
        for i in range(len(parents_entities) - 1):
            entity = parents_entities[i]
            if i == 0:
                for row in self.package_entities_list:
                    if row[0] == self.path:
                        parent_entity_parent = row[1]
                        self.package_string = row[2]
            else:
                parent_entity_parent = EntityModel.get_or_none(_longname=self.package_string)
            if type(entity).__name__ == "MethodDeclarationContext":
                parent_entity_name = entity.IDENTIFIER().getText()
                parent_entity_longname = self.package_string + "." + entity.IDENTIFIER().getText()
                self.package_string = self.package_string + "." + entity.IDENTIFIER().getText()
                parent_entity_contents = entity.getText()
                parent_entity_type = entity.typeTypeOrVoid().getText()
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
            if type(entity).__name__ == "ClassDeclarationContext":
                parent_entity_name = entity.IDENTIFIER().getText()
                parent_entity_longname = self.package_string + "." + entity.IDENTIFIER().getText()
                self.package_string = self.package_string + "." + entity.IDENTIFIER().getText()
                parent_entity_contents = entity.getText()
                props = self.getClassProperties(parent_entity_longname)
                parent_entity_kind = self.findKindWithKeywords("Class", props["modifiers"])
                class_ent = EntityModel.get_or_create(
                    _kind=parent_entity_kind,
                    _parent=parent_entity_parent,
                    _name=parent_entity_name,
                    _longname=parent_entity_longname,
                    _contents=parent_entity_contents)
                result_entities.append((parent_entity_kind, class_ent))
            if type(entity).__name__ == "InterfaceDeclarationContext":
                parent_entity_name = entity.IDENTIFIER().getText()
                parent_entity_longname = self.package_string + "." + entity.IDENTIFIER().getText()
                self.package_string = self.package_string + "." + entity.IDENTIFIER().getText()
                parent_entity_contents = entity.getText()
                props = p.getInterfaceProperties(parent_entity_longname, self.path)
                parent_entity_kind = self.findKindWithKeywords("Class", props["modifiers"])
                Interface_ent = EntityModel.get_or_create(
                    _kind=parent_entity_kind,
                    _parent=parent_entity_parent,
                    _name=parent_entity_name,
                    _longname=parent_entity_longname,
                    _contents=parent_entity_contents)
                result_entities.append((parent_entity_kind, Interface_ent))
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

    def get_method_kind(self, modifiers):
        """Return the kind ID based on the modifier"""
        if '@Override' in modifiers:
            modifiers.remove('@Override')
        if len(modifiers) == 0:
            modifiers.append("default")
        kind_selected = None
        for kind in KindModel.select().where(KindModel._name.contains("Method")):
            if self.checkModifiersInKind(modifiers, kind):
                if not kind_selected or len(kind_selected._name) > len(kind._name):
                    kind_selected = kind
        return kind_selected

    def getClassProperties(self, class_longname):
        listener = ClassPropertiesListener()
        listener.class_longname = class_longname.split(".")
        listener.class_properties = None
        walker = ParseTreeWalker()
        walker.walk(listener=listener, t=self.tree)
        return listener.class_properties

    def getInterfaceProperties(self, interface_longname):
        listener = InterfacePropertiesListener()
        listener.interface_longname = interface_longname.split(".")
        walker = ParseTreeWalker()
        walker.walk(listener=listener, t=self.tree)
        return listener.interface_properties

    def getCreatedClassEntity(self, class_longname, class_potential_longname, file_address):
        props = p.getClassProperties(class_potential_longname, file_address)
        if not props:
            return self.getClassEntity(class_longname, file_address)
        else:
            return self.getClassEntity(class_potential_longname, file_address)

    def getClassEntity(self, class_longname, file_address):
        props = p.getClassProperties(class_longname, file_address)
        if not props:  # This class is unknown, unknown class id: 84
            ent = EntityModel.get_or_create(_kind=84, _name=class_longname.split(".")[-1],
                                            _longname=class_longname, _contents="")
        else:
            if len(props["modifiers"]) == 0:
                props["modifiers"].append("default")
            kind = self.findKindWithKeywords("Class", props["modifiers"])
            ent = EntityModel.get_or_create(_kind=kind, _name=props["name"],
                                            _longname=props["longname"],
                                            _parent=props["parent"] if props["parent"] is not None else file_ent,
                                            _contents=props["contents"])
        return ent[0]

    def getInterfaceEntity(self, interface_longname, file_address):  # can't be of unknown kind!
        props = p.getInterfaceProperties(interface_longname, file_address)
        if not props:
            return None
        else:
            kind = self.findKindWithKeywords("Interface", props["modifiers"])
            ent = EntityModel.get_or_create(_kind=kind, _name=props["name"],
                                            _longname=props["longname"],
                                            _parent=props["parent"] if props["parent"] is not None else file_ent,
                                            _contents=props["contents"])
        return ent[0]

    def getImplementEntity(self, longname, file_address):
        ent = self.getInterfaceEntity(longname, file_address)
        if not ent:
            ent = self.getClassEntity(longname, file_address)
        return ent

    def findKindWithKeywords(self, entity_type, modifiers):
        if len(modifiers) == 0:
            modifiers.append("default")
        leastspecific_kind_selected = None
        for kind in KindModel.select().where(KindModel._name.contains(entity_type)):
            if self.checkModifiersInKind(modifiers, kind):
                if not leastspecific_kind_selected \
                        or len(leastspecific_kind_selected._name) > len(kind._name):
                    leastspecific_kind_selected = kind
        return leastspecific_kind_selected

    def checkModifiersInKind(self, modifiers, kind):
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
                    result.append((self.path, package_ent, package['package_longname']))
                else:
                    package_ent = EntityModel.get_or_none(_longname=package["package_longname"])
                    result.append((self.path, package_ent, package['package_longname']))
        else:
            package_ent, success = EntityModel.get_or_create(
                _kind=73,
                _name="Unnamed Package",
                _longname="Unnamed Package",
                _parent=self.file_ent,
                _contents=self.contents)
            self.package_string = ""
            result.append((self.path, package_ent, ""))
        return result

    @staticmethod
    def get_package_entity(name, longname):
        """get or return none for a package entity abased on its longname as address."""
        package_ent = EntityModel.get_or_none(
            _kind=73 if name == '' else 72,
            _longname=longname
        )
        return package_ent
