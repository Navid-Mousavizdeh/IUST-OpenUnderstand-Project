"""


"""

import os
from pathlib import Path

from antlr4 import *

from gen.javaLabeled.JavaLexer import JavaLexer
from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener
from analysis_passes.entity_manager import get_created_entity_longname


class ModifyListener(JavaParserLabeledListener):
    def __init__(self, entity_manager_object):
        self.entity_manager = entity_manager_object
        self.package = ""
        self._class = ""
        self.parent = ""
        self.name = ""
        self.enter_modify = False
        self.modify = []

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

    def enterExpression1(self, ctx: JavaParserLabeled.Expression1Context):
        if self.enter_modify:
            self.name = ctx.IDENTIFIER().getText()

    def enterExpression6(self, ctx: JavaParserLabeled.Expression6Context):
        [line, col] = str(ctx.start).split(",")[3].split(":")
        parents = self.entity_manager.get_or_create_parent_entities(ctx)
        parent = parents[-1][1]
        self.modify.append({
            'kind': 208,
            'file': self.entity_manager.file_ent,
            'line': line,
            'column': col.replace("]", ""),
            'ent': get_created_entity_longname(self.package + '.' + self.parent + '.' + self.name),
            'scope': parent[0]
        })

    def enterExpression7(self, ctx: JavaParserLabeled.Expression7Context):
        [line, col] = str(ctx.start).split(",")[3].split(":")
        parents = self.entity_manager.get_or_create_parent_entities(ctx)
        parent = parents[-1][1]
        self.modify.append({
            'kind': 208,
            'file': self.entity_manager.file_ent,
            'line': line,
            'column': col.replace("]", ""),
            'ent': get_created_entity_longname(self.package + '.' + self.parent + '.' + self.name),
            'scope': parent[0]
        })

    def enterExpression21(self, ctx: JavaParserLabeled.Expression21Context):
        operations = ['+=', '-=', '/=', '*=', '&=', '|=', '^=', '%=']
        if ctx.children[1].getText() in operations:
            [line, col] = str(ctx.start).split(",")[3].split(":")
            parents = self.entity_manager.get_or_create_parent_entities(ctx)
            parent = parents[-1][1]
            self.modify.append({
                'kind': 208,
                'file': self.entity_manager.file_ent,
                'line': line,
                'column': col.replace("]", ""),
                'ent': get_created_entity_longname(self.package + '.' + self.parent + '.' + self.name),
                'scope': parent[0]
            })

    def exitExpression6(self, ctx:JavaParserLabeled.Expression6Context):
        self.enter_modify = False

    def exitExpression7(self, ctx:JavaParserLabeled.Expression7Context):
        self.enter_modify = False

    def exitExpression21(self, ctx:JavaParserLabeled.Expression21Context):
        self.enter_modify = False
