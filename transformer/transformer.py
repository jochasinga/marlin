import ast
import astor
from libs.lark.lark import (
    Transformer,
    Token
)
from typing import (
    List,
    Dict,
    Tuple
)
from pprint import PrettyPrinter

alphabets = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
    'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
    'y', 'z'
]

alphabet_gen = lambda _: (a for a in alphabets)

pp = PrettyPrinter(indent = 4, width = 10)


class Mangler(object):
    '''Mangle class and object names which contains forward slashes and colons.'''
    @staticmethod
    def mangle(name):
        return name.replace('L', 'L_').replace('/', '__').replace(';', '')

class ImportFormatter(object):
    @staticmethod
    def format(name):
        if name.startswith('L'):
            name = name[1:]
        if name[len(name) - 1] == ';':
            name = name[:-1]

        packages = name.strip().split('/')
        import_package = packages[0]
        qualifier = '.'.join(packages).replace('$', '.')

        return (import_package, qualifier)


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
        self.imports = []

    def module(self, items):
        """
        The module is a top-level of any smali file. Hence all this method does
        is transform to Python standard AST.
        """

        module = ast.Module(body = items)

        import_stmt = ''
        for mod in self.imports:
            import_stmt += 'import {}\n'.format(mod)

        print(import_stmt)
        print(astor.to_source(module))
        # print(ast.dump(module))
        return module

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

        body = items[self.cursor.now]
        self.cursor.incr()

        class_def = {
            'HEADER': header,
            'BODY': body,
            'BASES': bases,
            'SOURCES': sources,
            'IMPLEMENTS': implements,
            'LFIELDS': fields,
            'BFIELDS': field_blocks,
            'ANNOTATIONS': annotations
        }

        bod = []

        for method in body:
            _, method_dict = method
            method_header = method_dict['header']
            name = method_header['name']
            if name == '<init>':
                name = '__init__'
            elif name == '<clinit>':
                name = '__clinit__'
            method_sig = method_header['signature']
            argslist = ['self'] + method_sig['args']
            arguments = []

            a_gen = alphabet_gen(_)

            for arg in argslist:
                arguments.append(ast.arg(
                    arg = next(a_gen) if arg != 'self' else 'self',
                    # type annotations
                    # annotation = None if arg == 'self' else ast.Name(id = get_type_of(arg), ctx = ast.Load()),
                    annotation = None,
                    default = [], vararg = None, kwarg = None,
                    kwonlyargs = None, kw_defaults = []
                ))

            args = ast.arguments(args = arguments, defaults = [], vararg = None,
                                kwarg = None, kwlonlyargs = None, kw_defaults = [])

            bod.append(
                ast.FunctionDef(
                    name = name, args = args,
                    body = [], decorator_list = [], returns = None
                )
            )

        py_class_def = ast.ClassDef(
            name = header['class_name'],
            bases = [ast.Name(id=name, ctx=ast.Load()) for name in bases],
            body = bod,
            keywords = [],
            starargs = None,
            kwargs = None,
            decorator_list = []
        )

        # print(astor.to_source(py_class_def))

        # pp.pprint(class_def)
        # return class_def
        return py_class_def

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
        module, package = ImportFormatter().format(class_name)
        if module not in self.imports and module != package:
            self.imports.append(module)

        # return Mangler.mangle(class_name)
        return package

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

    def class_body(self, items):
        return items

    def method_def(self, items):
        header = items[0]
        body = items[1]
        d = {
            'header': header,
            'body': body
        }
        return ('METHOD', d)

    def method_header(self, items):
        modifiers = items[0]
        name = items[1]
        signature = items[2]
        d = {
            'modifiers': modifiers,
            'name': name,
            'signature': signature
        }
        return d

    def constructor(self, items):
        val = items[0].value
        return val

    def method_name(self, items):
        return items[0].value

    def method_sig(self, items):
        args = items[0]
        return_type = items[1]
        return {
            'args': args,
            'return_type': return_type
        }


    def method_args(self, items):
        return items

    def method_arg(self, items):
        return items[0].value

    def return_type(self, items):
        return_type = items[0].value
        return return_type

    def method_body(self, items):
        if len(items) > 0:
            return items
        return None

    def label(self, items):
        return items[0].value

    def op_stmt(self, items):
        name = items[0]
        args = items[1]
        return {
            'name': name,
            'args': args
        }

    def op_name(self, items):
        name = items[0].value
        return name

    def args(self, items):
        return items

    def arg(self, items):
        if len(items) > 0:
            return items[0]
        return None

    def dir_stmt(self, items):
        if len(items) > 0:
            return items[0]

    def line_dir(self, items):
        directive = items[0].value
        dir_arg = None
        if len(items) > 1:
            dir_arg = items[1].value
        return ('LINE_DIR', {
            'directive': directive,
            'arg': int(dir_arg)
        })


    def dir_arg(self, items: List[str]) -> str:
        if len(items) > 0:
            return items[0]


    def catch_dir(self, items):
        error_class = items[0]
        try_start = items[1]
        try_end = items[2]
        catch = items[len(items) - 1]
        return ('CATCH_DIR', {
            'error_class': error_class,
            'try_start': try_start,
            'try_end': try_end,
            'catch': catch
        })