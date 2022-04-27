

#expression -> NEW creator


"""
## Description
This module find all OpenUnderstand call and callby references in a Java project


## References


"""

__author__ = 'Shaghayegh Mobasher , Setayesh kouloubandi ,Parisa Alaie'
__version__ = '0.1.0'

from openunderstand.gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener
from openunderstand.gen.javaLabeled.JavaParserLabeled import JavaParserLabeled


class ModifyByListener(JavaParserLabeledListener):
    """
    #Todo: Implementing the ANTLR listener pass for Java Call and Java Callby reference kind

    """
    modifyBy = []
    methods = []

    def enterMethodDeclaration(self, ctx:JavaParserLabeled.MethodDeclarationContext):
        self.methods.append(ctx.IDENTIFIER().getText())



    def enterExpression6(self, ctx:JavaParserLabeled.Expression6Context):
        line_col = str(ctx.children[0].start).split(",")[3][:-1].split(':')
        print("Modify ----")
        print("Expression 6 ->", line_col)
        self.modifyBy.append({
            "scope": self.methods[-1], "ent": None,
            "line": line_col[0], "col": line_col[1]
        })

    def enterExpression7(self, ctx:JavaParserLabeled.Expression7Context):
        line_col = str(ctx.children[1].start).split(",")[3][:-1].split(':')
        print("Modify ----")
        print("Expression 7 ->", line_col)
        self.modifyBy.append({
            "scope": self.methods[-1], "ent": None,
            "line": line_col[0], "col": line_col[1]
        })

    def enterExpression21(self, ctx:JavaParserLabeled.Expression21Context):
        operations = ['+=', '-=', '/=', '*=', '&=', '|=', '^=', '%=']
        print(self.methods[-1])
        line_col = str(ctx.children[0].start).split(",")[3][:-1].split(':')
        if ctx.children[1].getText() in operations:
            print("Modify ----")
            print("Expression 21 ->", line_col)
            self.modifyBy.append({
                "scope": self.methods[-1], "ent": None,
                "line": line_col[0], "col": line_col[1]
            })

