"""

"""

import os
from fnmatch import fnmatch

from antlr4 import *

from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from gen.javaLabeled.JavaLexer import JavaLexer

from oudb.models import KindModel, EntityModel, ReferenceModel
from oudb.api import open as db_open, create_db
from oudb.fill import main

from analysis_passes.couple_coupleby import ImplementCoupleAndImplementByCoupleBy
from analysis_passes.create_createby_G11 import CreateAndCreateBy
from analysis_passes.declare_declarein import DeclareAndDeclareinListener
from analysis_passes.modify_modifyby_G11 import ModifyModifyByListener
from analysis_passes.usemodule_usemoduleby_G11 import UseModuleUseModuleByListener
from analysis_passes.class_properties import ClassPropertiesListener, InterfacePropertiesListener


class Project:
    tree = None

    def Parse(self, fileAddress):
        file_stream = FileStream(fileAddress)
        lexer = JavaLexer(file_stream)
        tokens = CommonTokenStream(lexer)
        parser = JavaParserLabeled(tokens)
        tree = parser.compilationUnit()
        self.tree = tree
        return tree

    def Walk(self, listener, tree):
        walker = ParseTreeWalker()
        walker.walk(listener=listener, t=tree)

    def getListOfFiles(self, dirName):
        listOfFile = os.listdir(dirName)
        allFiles = list()
        for entry in listOfFile:
            # Create full path
            fullPath = os.path.join(dirName, entry)
            if os.path.isdir(fullPath):
                allFiles = allFiles + self.getListOfFiles(fullPath)
            elif fnmatch(fullPath, "*.java"):
                allFiles.append(fullPath)

        return allFiles

    def getFileEntity(self, path):
        # kind id: 1
        path = path.replace("/", "\\")
        name = path.split("\\")[-1]
        file = open(path, mode='r')
        file_ent = EntityModel.get_or_create(_kind=1, _name=name, _longname=path, _contents=file.read())[0]
        file.close()
        print("processing file:", file_ent)
        return file_ent

    def add_references(self, ref_dict, file_ent):
        scope = EntityModel.get_or_create(_name=ref_dict['scope'])[0]
        ent = EntityModel.get_or_create(_name=ref_dict['ent'],
                                        _kind=154,
                                        _longname=scope._longname + "." + ref_dict['ent'],
                                        _parent_id=scope._id)[0]
        ref, _ = ReferenceModel.get_or_create(
            _kind=KindModel.get_or_none(_name="Java Modify")._id,
            _line=ref_dict['line'],
            _file=file_ent,
            _column=ref_dict['col'],
            _ent=ent._id,
            _scope=scope._id,
        )
        inverse_ref, _ = ReferenceModel.get_or_create(
            _kind=KindModel.get_or_none(_name="Java Modifyby")._id,
            _line=ref_dict['line'],
            _file=file_ent,
            _column=ref_dict['col'],
            _ent=scope._id,
            _scope=ent._id,
        )

    def add_module_references(self, ref_dict, file_ent, file_address):
        ent = EntityModel.get_or_create(_name=ref_dict['name'],
                                        _kind=KindModel.get_or_none(_name="Java Module")._id,
                                      _longname=file_address.replace('/', '\\'))
        ref, _ = ReferenceModel.get_or_create(
            _kind=KindModel.get_or_none(_name="Java ModuleUse")._id,
            _line=ref_dict['line'],
            _file=file_ent,
            _column=ref_dict['col'],
            _ent=ent,
            _scope=file_ent,
        )
        inverse_ref, _ = ReferenceModel.get_or_create(
            _kind=KindModel.get_or_none(_name="Java ModuleUseby")._id,
            _line=ref_dict['line'],
            _file=file_ent,
            _column=ref_dict['col'],
            _ent=file_ent,
            _scope=ent,
        )

    def add_unknown_module_references(self, ref_dicts, file_ent, file_address):
        for ref_dict in ref_dicts:
            ent = EntityModel.get_or_create(_name=ref_dict['name'],
                                      _kind=KindModel.get_or_none(_name="Java Unknown Module")._id,
                                      _longname=file_address.replace('/', '\\'))

            ref, _ = ReferenceModel.get_or_create(
                _kind=KindModel.get_or_none(_name="Java ModuleUse")._id,
                _line=ref_dict['line'],
                _file=file_ent,
                _column=ref_dict['col'],
                _ent=ent,
                _scope=file_ent,
            )
            inverse_ref, _ = ReferenceModel.get_or_create(
                _kind=KindModel.get_or_none(_name="Java ModuleUseby")._id,
                _line=ref_dict['line'],
                _file=file_ent,
                _column=ref_dict['col'],
                _ent=file_ent,
                _scope=ent,
            )

    def add_unresolved_module_references(self, ref_dicts, file_ent, file_address):
        for ref_dict in ref_dicts:
            ent = EntityModel.get_or_create(_name=ref_dict['name'],
                                          _kind=KindModel.get_or_none(_name="Java Unresolved Module")._id,
                                          _longname=file_address.replace('/', '\\'))
            ref, _ = ReferenceModel.get_or_create(
                _kind=KindModel.get_or_none(_name="Java ModuleUse")._id,
                _line=ref_dict['line'],
                _file=file_ent,
                _column=ref_dict['col'],
                _ent=ent,
                _scope=file_ent,
            )
            inverse_ref, _ = ReferenceModel.get_or_create(
                _kind=KindModel.get_or_none(_name="Java ModuleUseby")._id,
                _line=ref_dict['line'],
                _file=file_ent,
                _column=ref_dict['col'],
                _ent=file_ent,
                _scope=ent,
            )

    def addModifyRefs(self, ref_dicts, file_ent):
        for ref_dict in ref_dicts:
            self.add_references(ref_dict, file_ent)

    def addModuleRefs(self, ref_dicts, file_ent, file_address):
        for ref_dict in ref_dicts:
            self.add_module_references(ref_dict, file_ent, file_address)

    # def add_java_file_entity(file_path, file_name):
    #     kind_id = KindModel.get_or_none(_name="Java File")._id
    #     obj, _ = EntityModel.get_or_create(
    #         _kind=kind_id,
    #         _name=file_name,
    #         _longname=file_path,
    #         _contents=FileStream(file_path),
    #     )
    #     return obj

    def addDeclareRefs(self, ref_dicts, file_ent):
        for ref_dict in ref_dicts:
            if ref_dict["scope"] is None:  # the scope is the file
                scope = file_ent
            else:  # a normal package
                scope = self.getPackageEntity(file_ent, ref_dict["scope"], ref_dict["scope_longname"])

            if ref_dict["ent"] is None:  # the ent package is unnamed
                ent = self.getUnnamedPackageEntity(file_ent)
            else:  # a normal package
                ent = self.getPackageEntity(file_ent, ref_dict["ent"], ref_dict["ent_longname"])

            # Declare: kind id 192
            declare_ref = ReferenceModel.get_or_create(_kind=192, _file=file_ent, _line=ref_dict["line"],
                                                       _column=ref_dict["col"], _ent=ent, _scope=scope)

            # Declarein: kind id 193
            declarein_ref = ReferenceModel.get_or_create(_kind=193, _file=file_ent, _line=ref_dict["line"],
                                                         _column=ref_dict["col"], _scope=ent, _ent=scope)

    def addImplementOrImplementByRefs(self, ref_dicts, file_ent, file_address):
        for ref_dict in ref_dicts:
            scope = EntityModel.get_or_create(_kind=self.findKindWithKeywords(ref_dict["scope_kind"],
                                                                              ref_dict["scope_modifiers"]),
                                              _name=ref_dict["scope_name"],
                                              _parent=ref_dict["scope_parent"] if ref_dict[
                                                                                      "scope_parent"] is not None else file_ent,
                                              _longname=ref_dict["scope_longname"],
                                              _contents=ref_dict["scope_contents"])[0]
            ent = self.getImplementEntity(ref_dict["type_ent_longname"], file_address)

            implement_ref = ReferenceModel.get_or_create(_kind=188, _file=file_ent, _line=ref_dict["line"],
                                                         _column=ref_dict["col"], _ent=ent, _scope=scope)
            implementBy_ref = ReferenceModel.get_or_create(_kind=189, _file=file_ent, _line=ref_dict["line"],
                                                           _column=ref_dict["col"], _ent=scope, _scope=ent)

    def addCreateRefs(self, ref_dicts, file_ent, file_address):
        for ref_dict in ref_dicts:
            scope = EntityModel.get_or_create(_kind=self.findKindWithKeywords("Method", ref_dict["scopemodifiers"]),
                                              _name=ref_dict["scopename"],
                                              _type=ref_dict["scopereturntype"]
                                              , _parent=ref_dict["scope_parent"] if ref_dict[
                                                                                        "scope_parent"] is not None else file_ent
                                              , _longname=ref_dict["scopelongname"]
                                              , _contents=["scopecontent"])[0]
            ent = self.getCreatedClassEntity(ref_dict["refent"], ref_dict["potential_refent"], file_address)
            Create = ReferenceModel.get_or_create(_kind=190, _file=file_ent, _line=ref_dict["line"],
                                                  _column=ref_dict["col"], _scope=scope, _ent=ent)
            Createby = ReferenceModel.get_or_create(_kind=191, _file=file_ent, _line=ref_dict["line"],
                                                    _column=ref_dict["col"], _scope=ent, _ent=scope)

    def getPackageEntity(self, file_ent, name, longname):
        # package kind id: 72
        ent = EntityModel.get_or_create(_kind=72, _name=name, _parent=file_ent,
                                        _longname=longname, _contents="")
        return ent[0]

    def getUnnamedPackageEntity(self, file_ent):
        # unnamed package kind id: 73
        ent = EntityModel.get_or_create(_kind=73, _name="(Unnamed_Package)", _parent=file_ent,
                                        _longname="(Unnamed_Package)", _contents="")
        return ent[0]

    def getClassProperties(self, class_longname, file_address):
        listener = ClassPropertiesListener()
        listener.class_longname = class_longname.split(".")
        listener.class_properties = None
        self.Walk(listener, self.tree)
        return listener.class_properties

    def getInterfaceProperties(self, interface_longname, file_address):
        listener = InterfacePropertiesListener()
        listener.interface_longname = interface_longname.split(".")
        listener.interface_properties = None
        self.Walk(listener, self.tree)
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

    def findKindWithKeywords(self, type, modifiers):
        if len(modifiers) == 0:
            modifiers.append("default")
        leastspecific_kind_selected = None
        for kind in KindModel.select().where(KindModel._name.contains(type)):
            if self.checkModifiersInKind(modifiers, kind):
                if not leastspecific_kind_selected \
                        or len(leastspecific_kind_selected._name) > len(kind._name):
                    leastspecific_kind_selected = kind
        return leastspecific_kind_selected

    def checkModifiersInKind(self, modifiers, kind):
        for modifier in modifiers:
            if modifier.lower() not in kind._name.lower():
                return False
        return True


if __name__ == '__main__':
    p = Project()
    create_db("../benchmark2_database.oudb",
              project_dir="..\benchmark")
    main()
    db = db_open("../benchmark2_database.oudb")

    def listToString(s):
        """a method to find projects path dynamically"""
        str1 = ""
        for ele in s[0:len(s) - 1]:
            str1 += (ele + "\\")
        return str1

    rawPath = str(os.path.dirname(__file__).replace("\\", "/"))
    pathArray = rawPath.split('/')
    path = listToString(pathArray) + "benchmark"
    files = p.getListOfFiles(path)

    print(len(files))

    # AGE KHASTID YEK FILE RO RUN KONID:
    # files = ["../../Java codes/javaCoupling.java"]

    for file_address in files:

        try:
            file_ent = p.getFileEntity(file_address)
            tree = p.Parse(file_address)
        except Exception as e:
            print("An Error occurred in file:" + file_address + "\n" + str(e))
            continue

        try:
            # implement
            listener = ImplementCoupleAndImplementByCoupleBy()
            listener.implement = []
            p.Walk(listener, tree)
            p.addImplementOrImplementByRefs(listener.implement, file_ent, file_address)
        except Exception as e:
            print("An Error occurred for reference implement/implementBy in file:" + file_address + "\n" + str(e))

        try:
            # create
            listener = CreateAndCreateBy()
            listener.create = []
            p.Walk(listener, tree)
            p.addCreateRefs(listener.create, file_ent, file_address)
        except Exception as e:
            print("An Error occurred for reference create/createBy in file:" + file_address + "\n" + str(e))

        try:
            # declare
            listener = DeclareAndDeclareinListener()
            listener.declare = []
            p.Walk(listener, tree)
            p.addDeclareRefs(listener.declare, file_ent)
        except Exception as e:
            print("An Error occurred for reference declare/declaredIn in file:" + file_address + "\n" + str(e))

        try:
            # modify
            listener = ModifyModifyByListener()
            listener.modifyBy = []
            p.Walk(listener, tree)
            p.addModifyRefs(listener.modifyBy, file_ent)
        except Exception as e:
            print("An Error occurred for reference modify/modifyBy in file:" + file_address + "\n" + str(e))

        # try:
        #     # useModule
        #     listener = UseModuleUseModuleByListener()
        #     listener.useModules = []
        #     p.Walk(listener, tree)
        #     p.addModuleRefs(listener.useModules, file_ent, file_address)
        #     p.add_unknown_module_references(listener.useUnknownModules, file_ent, file_address)
        #     p.add_unresolved_module_references(listener.useUnresolvedModules, file_ent, file_address)
        # except Exception as e:
        #     print("An Error occurred for reference useModule/useModuleBy in file:" + file_address + "\n" + str(e))
