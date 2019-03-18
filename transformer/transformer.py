from libs.lark.lark import (
    Transformer,
    Token
)
from typing import (
    List,
    Dict,
    Tuple
)
import ast
from pprint import PrettyPrinter

pp = PrettyPrinter(indent = 4, width = 10)


class Mangler():
    '''Mangle class and object names which contains forward slashes and colons.'''
    @staticmethod
    def mangle(name):
        return name.replace('L', 'L_').replace('/', '__').replace(';', '')


class Cursor(object):
    def __init__(self):
        self._current = 0

    def incr(self):
        self._current += 1

    @property
    def now(self):
        return self._current


class Smali2Py(Transformer):

    def __init__(self):
        super().__init__()
        self.cursor = Cursor()

    def module(self, items):
        """
        The module is a top-level of any smali file. Hence all this method does
        is transform to Python standard AST.
        """
        return ast.Module(body = items)

    def class_def(self, items):

        header = items[0]
        self.cursor.incr()

        bases = []
        sources = []
        implements = []
        fields = []
        field_blocks = []
        annotations = []

        while 1:
            current_item = items[self.cursor.now]
            if type(current_item) != tuple:
                break

            token_type, val = current_item

            if token_type == 'BASE':
                bases.append(val)
            elif token_type == 'SOURCE':
                sources.append(val)
            elif token_type == 'IMPL':
                implements.append(val)
            elif token_type == 'LFIELD':
                fields.append(val)
            elif token_type == 'BFIELD':
                field_blocks.append(val)
            elif token_type == 'ANNOTATION':
                annotations.append(val)

            self.cursor.incr()

        class_def = {
            'HEADER': header,
            'BASES': bases,
            'SOURCES': sources,
            'IMPLEMENTS': implements,
            'LFIELDS': fields,
            'BFIELDS': field_blocks,
            'ANNOTATIONS': annotations
        }

        pp.pprint(class_def)
        return class_def

    def class_header(self, items):
        return {
            'modifiers': items[0],
            'class_name': items[1],
        }

    def modifiers(self, items):
        if len(items) == 1:
            return { 'mods': items[0] }
        if len(items) == 2:
            return {
                'mods': items[0],
                'acc_mods': items[1]
            }

    def mod(self, items: List[Token]) -> List[str]:
        modifiers = [token.value for token in items]
        return modifiers

    def acc_mod(self, items: List[Token]) -> List[str]:
        modifiers = [token.value for token in items]
        return modifiers

    def class_name(self, items: List[Token]) -> str:
        class_name = items[0].value
        return Mangler.mangle(class_name)

    def super_stmt(self, items: List[str]) -> Tuple[str, str]:
        return ('BASE', items[0])

    def source_stmt(self, items: List[Token]) -> Tuple[str, str]:
        return ('SOURCE', items[0].value)

    def impl_stmt(self, items: List[Token]) -> Tuple[str, str]:
        return ('IMPL', items[0].value)

    def field_block(self, items):
        field_def = items[0]
        _, anno = items[1]
        val = {
            'field_def': field_def,
            'annotation': anno
        }
        return ('BFIELD', val)

    def anno_stmt(self, items):
        header = items[0]
        body = items[1]
        return ('ANNOTATION', {
            'header': header,
            'body': body
        })

    def anno_header(self, items):
        is_system = items[0].value == 'system'
        annotation_class = items[1]
        return {
            'annotation_class': annotation_class,
            'system': is_system,
        }

    def anno_body(self, items):
        return items[0]

    def values(self, items):
        if type(items[0]) == str:
            return items
        if type(items[0]) == Token:
            return [item.value for item in items]

    def field_def(self, items):
        val = {
            'modifiers': items[0],
            'symbol': items[1],
            'object_name': items[2]
        }
        return ('LFIELD', val)

    def obj(self, items):
        name = Mangler.mangle(items[0])
        return name

    def symbol(self, items):
        return items[0].value
