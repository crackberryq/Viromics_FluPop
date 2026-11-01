"""Workflow stages for supplied records only; no read processing or inference."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import tempfile
from . import __version__
from .cfasta import Entry, parse
from .pipeline import assemble, summarize, serialize, write_outputs, digest


def atomic_text(path, text):
    path=Path(path);path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,delete=False) as f:
        temp=Path(f.name)
        try:
            f.write(text);f.flush();os.fsync(f.fileno())
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
    try: os.replace(temp,path)
    finally: temp.unlink(missing_ok=True)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='stage',required=True)
    v=sub.add_parser('validate')
    for name in ('consensus','haplotypes','sample'):v.add_argument('--'+name,required=True)
    v.add_argument('--evidence',default='')
    v.add_argument('--demo',choices=['true','false'],default='false')
    c=sub.add_parser('cfasta');c.add_argument('--input',required=True)
    r=sub.add_parser('report');r.add_argument('--input',required=True);r.add_argument('--cfasta',required=True)
    for command in (v,c,r):command.add_argument('--output',required=True)
    args=parser.parse_args(argv)
    print(f'FluPop {__version__}: {args.stage}',flush=True)
    try:
        if args.stage=='validate':
            inputs={}
            def read(name):
                path=Path(getattr(args,name));raw=path.read_bytes()
                inputs[name]={'filename':path.name,'sha256':digest(raw)}
                return raw.decode('utf-8-sig')
            entries=assemble(read('consensus'),read('haplotypes'),args.sample)
            evidence=json.loads(read('evidence')) if args.evidence else None
            summarize(entries,evidence)
            data={'schema':'flupop-validated-v1','entries':[asdict(e) for e in entries],
                  'evidence':evidence,'inputs':inputs,'synthetic_demo':args.demo=='true',
                  'provenance':{'flupop_version':__version__,'python':platform.python_version(),
                  'platform':platform.platform(),'validated_at':datetime.now(timezone.utc).isoformat()}}
            atomic_text(args.output,json.dumps(data,indent=2,allow_nan=False)+'\n')
        else:
            data=json.loads(Path(args.input).read_text())
            if data.get('schema')!='flupop-validated-v1':raise ValueError('Unsupported validated-record schema')
            entries=[Entry(**e) for e in data['entries']]
            text=serialize(entries)
            if args.stage=='cfasta':atomic_text(args.output,text)
            else:
                if Path(args.cfasta).read_text()!=text:raise ValueError('cFASTA does not match validated records')
                destination=Path(args.output);destination.parent.mkdir(parents=True,exist_ok=True)
                # Stage outputs privately; replace only the explicitly owned files.
                # Unrelated files in the run folder are never deleted.
                with tempfile.TemporaryDirectory(dir=destination.parent) as temp:
                    prepared=Path(temp)/'report'
                    write_outputs(parse(text),data['evidence'],prepared,data['inputs'],data['synthetic_demo'])
                    manifest=json.loads((prepared/'manifest.json').read_text())
                    manifest['execution']=data['provenance']
                    (prepared/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
                    destination.mkdir(exist_ok=True)
                    for path in prepared.iterdir():os.replace(path,destination/path.name)
        print('Completed',flush=True)
    except (ValueError,TypeError,KeyError,OSError) as exc:
        parser.exit(2,f'FluPop: {exc}\n')

if __name__=='__main__':main()
