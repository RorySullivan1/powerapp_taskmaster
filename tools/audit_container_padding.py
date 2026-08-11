#!/usr/bin/env python3
"""Container-padding audit.

A child of an auto-layout container written `Width: =Parent.Width` is sized to the
container's OUTER width, not its content box, so it hangs off the right by exactly
PaddingLeft + PaddingRight. This walks the indentation tree of a .pa.yaml screen and
reports every child whose Width does not subtract its parent's horizontal padding.

Nesting COMPOUNDS: a section inside a 48-padded body and a row inside that 40-padded
section overflow by 88px together, which is why this is worth checking mechanically
rather than by eye.

Known false positive: a child deliberately sized to leave room for a sibling (e.g.
scrProjectEdit lblPrMissing, `- 512`, which reserves the action bar's buttons). Read
the subtraction, not just the mismatch.

  python3 tools/audit_container_padding.py src/Screens/*.pa.yaml
"""
import io,re,sys

def audit(path):
    L=io.open(path,encoding='utf-8').read().split('\n')
    # stack of (indent, name, padL, padR) for control blocks
    ctrl=[]                      # list of (indent, name, lineno)
    pad={}                       # name -> (padL,padR)
    owner={}                     # lineno -> enclosing control name
    stack=[]
    for i,l in enumerate(L):
        if not l.strip() or l.lstrip().startswith('#'): continue
        ind=len(l)-len(l.lstrip())
        m=re.match(r'^\s*- (\w+):\s*$',l)
        if m:
            while stack and stack[-1][0]>=ind: stack.pop()
            stack.append((ind,m.group(1)))
            pad.setdefault(m.group(1),[0,0])
            continue
        THEME={'Theme.Space.Gutter':24,'Theme.Space.Gap':16,'Theme.Space.HeaderH':64,
               'Theme.Space.NavW':240,'Theme.Space.RowH':52}
        p=re.match(r'^\s*Padding(Left|Right): =(\S+)',l)
        if p and stack:
            v=p.group(2)
            n=int(v) if v.isdigit() else THEME.get(v)
            if n is None: n=0
            pad.setdefault(stack[-1][1],[0,0])[0 if p.group(1)=='Left' else 1]=n
        w=re.match(r'^\s*Width: =Parent\.Width(\s*-\s*(\d+))?\s*$',l)
        if w and len(stack)>=2:
            child=stack[-1][1]; parent=stack[-2][1]
            sub=int(w.group(2)) if w.group(2) else 0
            owner[i+1]=(child,parent,sub)
    out=[]
    for ln,(child,parent,sub) in sorted(owner.items()):
        pl,pr=pad.get(parent,[0,0]); need=pl+pr
        if need!=sub: out.append((ln,child,parent,need,sub))
    return out

for f in sys.argv[1:]:
    bad=audit(f)
    name=f.split('/')[-1]
    if not bad: print("%-28s OK — every child subtracts its parent's padding"%name); continue
    print("%-28s %d MISMATCHES"%(name,len(bad)))
    for ln,child,parent,need,sub in bad[:14]:
        print("   line %-5d %-22s in %-20s padding=%-3d subtracts=%d"%(ln,child,parent,need,sub))
    if len(bad)>14: print("   ... and %d more"%(len(bad)-14))
    print()
