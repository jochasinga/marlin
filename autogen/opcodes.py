from bs4 import BeautifulSoup


def parse_inner_text(src_html):
    with open(src_html, 'r') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'lxml')
    trs = soup.table.tbody.find_all('tr')[1:]
    tds = [tr.select('td')[1] for tr in trs]

    return [td.text for td in tds]


def to_enum_format(text):
    return text.upper().replace('-', '_').replace('/', '__')


def parse_name_from_text(text):
    return text.strip().split(' ')[0]


if __name__ == "__main__":
    import os

    source = os.path.abspath(os.path.join("resource", "dalvik-opcodes.html"))
    tmpl = os.path.abspath(os.path.join("autogen", "opcodes.tmpl"))
    dest = os.path.abspath("__opcodes.py")

    with open(dest, 'w') as df:
        with open(tmpl, 'r') as tf:
            tmpl_text = tf.read()
            inner_texts = parse_inner_text(source)
            names = [to_enum_format(parse_name_from_text(text)) for text in inner_texts]


            line = "\t{name} = auto()\n"
            chunk = ''

            for name in names:
                chunk += line.format(name = name.strip())

            code = tmpl_text.format(auto_gen_names = chunk)
            df.write(code)
