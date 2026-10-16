import re

# Minimal parser for the Lua table literals in Fandom data modules ("return { ... }")
TOK = re.compile(
    r'\s+|--\[\[.*?\]\]|--[^\n]*'
    r'|(?P<str>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'
    r'|(?P<num>-?\d+\.?\d*(?:[eE][-+]?\d+)?)'
    r'|(?P<name>[A-Za-z_]\w*)'
    r'|(?P<sym>[{}\[\]=,;])',
    re.S,
)

ESC = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', "'": "'", '\\': '\\'}


def tokens(s):
    pos = 0
    while pos < len(s):
        m = TOK.match(s, pos)
        if not m:
            raise ValueError(f'bad char at {pos}: {s[pos:pos + 40]!r}')
        pos = m.end()
        for k in ('str', 'num', 'name', 'sym'):
            if m.group(k) is not None:
                yield k, m.group(k)
                break


def unquote(s):
    return re.sub(r'\\(.)', lambda m: ESC.get(m.group(1), m.group(1)), s[1:-1])


def parse(s):
    """Parse a module that is `return { ... }` or `local name = { ... } ... return name`"""
    start = re.search(r'^\s*(?:return|local\s+\w+\s*=)\s*(?=\{)', s, re.M)
    s = s[start.end():]

    class LazyTokens:
        """Tokens are produced on demand, so code after the table (e.g. functions) is never tokenized"""
        def __init__(self, gen): self.gen, self.buf = gen, []
        def __getitem__(self, j):
            while len(self.buf) <= j: self.buf.append(next(self.gen))
            return self.buf[j]

    toks = LazyTokens(tokens(s))
    i = 0

    def val():
        nonlocal i
        k, v = toks[i]
        i += 1
        if k == 'str':
            return unquote(v)
        if k == 'num':
            return float(v) if any(c in v for c in '.eE') else int(v)
        if k == 'name':
            return {'true': True, 'false': False, 'nil': None}[v]
        if v == '{':
            return table()
        raise ValueError(f'unexpected {v!r} at token {i}')

    def table():
        nonlocal i
        d, arr = {}, []
        while toks[i][1] != '}':
            if toks[i][1] == '[':
                i += 1
                key = val()
                assert toks[i][1] == ']'
                i += 2
                d[key] = val()
            elif toks[i][0] == 'name' and toks[i + 1][1] == '=':
                key = toks[i][1]
                i += 2
                d[key] = val()
            else:
                arr.append(val())
            if toks[i][1] in ',;':
                i += 1
        i += 1
        if arr and not d:
            return arr
        for n, a in enumerate(arr, 1):
            d[n] = a
        return d

    return val()
