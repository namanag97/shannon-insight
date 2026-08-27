#!/usr/bin/env python3
from __future__ import annotations
import json,re,struct,unicodedata
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit

HERE=Path(__file__).resolve().parent

def load_jsonl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
UNRESERVED=set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~')

def pct_norm(text:str)->str:
    def repl(m):
        b=int(m.group(1),16); ch=chr(b)
        return ch if ch in UNRESERVED else '%'+m.group(1).upper()
    if re.search(r'%(?![0-9A-Fa-f]{2})',text): raise ValueError('malformed percent encoding')
    return re.sub(r'%([0-9A-Fa-f]{2})',repl,text)

def remove_dot_segments(path:str)->str:
    out=[]
    for seg in path.split('/'):
        if seg in ('','.'): 
            if not out and seg=='': out.append('')
            continue
        if seg=='..':
            if len(out)>1 or (out and out[0]!=''): out.pop()
        else: out.append(seg)
    result='/'.join(out)
    if path.startswith('/') and not result.startswith('/'): result='/'+result
    return result or ('/' if path.startswith('/') else '')

def uri_norm(uri:str)->str:
    p=urlsplit(uri)
    if not p.scheme: raise ValueError('relative uri')
    # Bound this oracle to generic authority without userinfo/IPv6 reconstruction.
    host=p.hostname.lower() if p.hostname else ''
    netloc=host
    if p.port is not None: netloc+=f':{p.port}'
    path=remove_dot_segments(pct_norm(p.path))
    return urlunsplit((p.scheme.lower(),netloc,path,pct_norm(p.query),pct_norm(p.fragment)))

def main():
    errors=[]
    profiles=load_jsonl(HERE/'semantic-equality-profiles.jsonl'); sources=load_jsonl(HERE/'semantic-equality-sources.jsonl'); vectors=load_jsonl(HERE/'semantic-equality-test-vectors.jsonl')
    pids={p['profile_id'] for p in profiles}; sids={s['source_id'] for s in sources}
    if len(pids)!=len(profiles): errors.append('duplicate equality profile id')
    if len(sids)!=len(sources): errors.append('duplicate equality source id')
    for p in profiles:
        if not set(p['source_refs'])<=sids: errors.append(f"unresolved source {p['profile_id']}")
        if not p['non_collapse'] or not p['refusals'] or p['ratification']!='WITHHELD' or p['completion_claim']: errors.append(f"weak/overclaimed profile {p['profile_id']}")
    if any(v['profile_ref'] not in pids for v in vectors): errors.append('test vector references unknown profile')
    # Executable bounded vectors.
    if unicodedata.normalize('NFC','é')!=unicodedata.normalize('NFC','e\u0301'): errors.append('NFC positive vector failed')
    if unicodedata.normalize('NFC','①')==unicodedata.normalize('NFC','1'): errors.append('NFC compatibility noncollapse failed')
    if unicodedata.normalize('NFKC','①')!=unicodedata.normalize('NFKC','1'): errors.append('NFKC circled digit failed')
    if unicodedata.normalize('NFKC','ｶ')!=unicodedata.normalize('NFKC','カ'): errors.append('NFKC width failed')
    a,b=Decimal('2.1'),Decimal('2.10')
    if a!=b or a.compare_total(b)==0: errors.append('decimal scale dual relation failed')
    z,nz=Decimal('0'),Decimal('-0')
    if z!=nz or z.compare_total(nz)==0: errors.append('decimal signed-zero dual relation failed')
    plus0=struct.unpack('>d',bytes.fromhex('0000000000000000'))[0]; minus0=struct.unpack('>d',bytes.fromhex('8000000000000000'))[0]
    if plus0!=minus0 or bytes.fromhex('0000000000000000')==bytes.fromhex('8000000000000000'): errors.append('float signed-zero noncollapse failed')
    nan=struct.unpack('>d',bytes.fromhex('7ff8000000000001'))[0]
    if nan==nan: errors.append('NaN numerical unordered vector failed')
    u1='eXAMPLE://a/./b/../b/%63/%7bfoo%7d'; u2='example://a/b/c/%7Bfoo%7D'
    if uri_norm(u1)!=uri_norm(u2): errors.append(f'RFC3986 vector failed: {uri_norm(u1)} != {uri_norm(u2)}')
    required={'equality.unicode.nfc.canonical','equality.unicode.nfkc.compatibility','ordering.unicode.uca17.default','ordering.ieee754.binary.totalorder','equality.decimal.numeric_and_representation','equivalence.uri.rfc3986.syntax','canonicalization.rdf.rfdc1'}
    if pids!=required: errors.append('profile inventory drift')
    if errors:
        for e in errors: print('ERROR: '+e)
        return 1
    print(f'PASS semantic equality profiles: {len(profiles)} versioned profiles / {len(vectors)} boundary vectors; local executable vectors pass; independent conformance/ratification remains withheld')
    return 0
if __name__=='__main__': raise SystemExit(main())
