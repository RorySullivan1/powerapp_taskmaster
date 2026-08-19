import io, sys, yaml

def scan(src):
    """Character state machine: '' and "" are Power Fx string literals ('' is an
    identifier quote but balances the same way); // starts a comment only in code."""
    i, n = 0, len(src)
    depth = mind = 0
    st = 'code'
    while i < n:
        c = src[i]
        if st == 'code':
            if c == '/' and i + 1 < n and src[i+1] == '/':
                while i < n and src[i] != '\n': i += 1
                continue
            if c == '"': st = 'dq'
            elif c == "'": st = 'sq'
            elif c in '([{': depth += 1
            elif c in ')]}':
                depth -= 1; mind = min(mind, depth)
        elif st == 'dq':
            if c == '"':
                if i + 1 < n and src[i+1] == '"': i += 1
                else: st = 'code'
        elif st == 'sq':
            if c == "'":
                if i + 1 < n and src[i+1] == "'": i += 1
                else: st = 'code'
        i += 1
    return depth, mind, st

def props(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "Properties" and isinstance(v, dict):
                for pk, pv in v.items():
                    if isinstance(pv, str) and pv.lstrip().startswith('='):
                        yield path, pk, pv
            else:
                yield from props(v, path + "/" + str(k))
    elif isinstance(node, list):
        for i in node: yield from props(i, path)

bad = 0
for f in sys.argv[1:]:
    d = yaml.safe_load(io.open(f, encoding='utf-8'))
    for p, k, body in props(d):
        depth, mind, st = scan(body)
        if depth or mind or st != 'code':
            print(f"  UNBALANCED {f} {p}.{k}: final={depth} min={mind} end-state={st}")
            bad += 1
    print(f"{f}: checked")
print("unbalanced:", bad)
