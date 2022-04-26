

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


class UseModuleListener(JavaParserLabeledListener):
    """
    #Todo: Implementing the ANTLR listener pass for Java Call and Java Callby reference kind

    """
    useModules = []
    methods = []

    def enterMethodDeclaration(self, ctx: JavaParserLabeled.MethodDeclarationContext):
        self.methods.append(ctx.IDENTIFIER().getText())

    def enterAnnotation(self, ctx:JavaParserLabeled.AnnotationContext):
        line_col = str(ctx.start).split(",")[3][:-1].split(':')
        print("Module ----")
        print(ctx.AT(), ctx.children[1].IDENTIFIER()[0].getText(), line_col)
        self.useModules.append({
            "scope": self.methods[-1], "ent": None,
            "line": line_col[0], "col": line_col[1]
        })
