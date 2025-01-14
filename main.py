import re
from transformer.transformer import Smali2Py

from pprint import PrettyPrinter

def gen_opcode_names():
    tmpl = 'NAME : {}'
    opt = ''

    def custom_sort(s):
        seps = re.findall(r'\-|\/', s)
        if seps:
            return (s.split(seps[0])[0] + seps[0], len(s))
        else:
            return (s, len(s))

    names = [x for x, _ in [code.value for code in Opcode] if not x.startswith('unused')]

    with open('grammars/opcodes.lark', 'w') as f:
        sort_by_len = sorted(names, key = custom_sort)
        sort_by_len.reverse()

        for i, name in enumerate(sort_by_len):
            if i > 0:
                opt += '\n\t|'
            opt += ' "{}"'.format(name)

        f.write(tmpl.format(opt))


if __name__ == '__main__':
    import os
    from opcodes import Opcode
    from libs.lark.lark import Lark

    pp = PrettyPrinter(indent = 4, width = 10)

    gen_opcode_names()

    with open('smali/Sandbox.smali', 'r') as sm:
        text = sm.read()

    with open("grammars/main.lark", "r") as f:
        smali_parser = Lark(r'' + f.read(), start = 'module')
        tree = smali_parser.parse(text)

    print(tree.pretty())

    Smali2Py().transform(tree)

    # pp.pprint(['1', 2, 'foo', {'bar': 1}])