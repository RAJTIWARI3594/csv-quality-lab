"""Conservative CSV profiling with explicit exports; Python standard library only."""
import argparse,csv,hashlib,io,json,sys
from pathlib import Path
from decimal import Decimal,InvalidOperation
from datetime import date
LIMIT=10_000_000

def kind(v):
    if not v:return 'blank'
    try:
        n=Decimal(v)
        if n.is_finite():return 'number'
    except InvalidOperation:pass
    try:date.fromisoformat(v);return 'date'
    except ValueError:return 'text'

def analyze(path,key=None):
    p=Path(path)
    if p.stat().st_size>LIMIT:raise ValueError('Input exceeds 10 MB')
    raw=p.read_bytes(); text=raw.decode('utf-8-sig')
    reader=csv.reader(io.StringIO(text,newline=''),strict=True)
    try:headers=next(reader)
    except StopIteration:raise ValueError('Empty CSV')
    headers=[h.strip() for h in headers]
    if not headers or any(not h for h in headers) or len(set(headers))!=len(headers):raise ValueError('Headers must be nonblank and unique')
    if key and key not in headers:raise ValueError('Unknown key column')
    rows=[]; issues=[];seen=set();duplicates=[]
    for line,row in enumerate(reader,2):
        if len(rows)>=100000:raise ValueError('Too many rows')
        if len(row)!=len(headers):raise ValueError(f'Row {line}: expected {len(headers)} columns, got {len(row)}')
        clean=[v.strip() for v in row];rows.append(clean)
        for h,old,new in zip(headers,row,clean):
            if old!=new:issues.append({'line':line,'column':h,'issue':'surrounding whitespace'})
            if not new:issues.append({'line':line,'column':h,'issue':'blank'})
            if new.startswith(('=','+','-','@')):issues.append({'line':line,'column':h,'issue':'spreadsheet formula prefix'})
        if key:
            value=clean[headers.index(key)]
            if value in seen:duplicates.append({'line':line,'value':value})
            seen.add(value)
    columns={h:{'blank':sum(not r[i] for r in rows),'distinct':len({r[i] for r in rows}),'types':{t:sum(kind(r[i])==t for r in rows) for t in ('blank','number','date','text')}} for i,h in enumerate(headers)}
    return {'source':p.name,'source_sha256':hashlib.sha256(raw).hexdigest(),'row_count':len(rows),'columns':columns,'key':key,'duplicate_keys':duplicates,'issues':issues},headers,rows

def export_csv(path,headers,rows,safe=False):
    with Path(path).open('x',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow([("'"+v if safe and v.startswith(('=','+','-','@')) else v) for v in headers])
        for row in rows:w.writerow([("'"+v if safe and v.startswith(('=','+','-','@')) else v) for v in row])

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input');ap.add_argument('--key');ap.add_argument('--out',required=True);ap.add_argument('--clean');ap.add_argument('--spreadsheet-safe',action='store_true');a=ap.parse_args(argv)
    try:
        paths=[Path(x).resolve() for x in (a.input,a.out,a.clean) if x]
        if len(set(paths))!=len(paths):raise ValueError('Input and output paths must differ')
        if any(p.exists() for p in paths[1:]):raise ValueError('Output exists; choose a new filename')
        report,headers,rows=analyze(a.input,a.key)
        if a.clean:export_csv(a.clean,headers,rows,a.spreadsheet_safe)
        with Path(a.out).open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
        print(f"Profiled {report['row_count']} rows; {len(report['issues'])} issues; {len(report['duplicate_keys'])} repeated keys")
        return 0
    except (OSError,ValueError,UnicodeError,csv.Error) as e:print(f'Error: {e}',file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
