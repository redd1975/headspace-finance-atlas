#!/usr/bin/env python3
"""Validate architecture adoption metadata, not business correctness or Owner approval."""
import argparse,hashlib,json,os,pathlib,re,sys
CANONICAL='redd1975/SAAS'
def check(root, event=None):
    errors=[]
    def require(ok,msg):
        if not ok: errors.append(msg)
    path=root/'.architecture-policy.json'
    if not path.is_file():return ['Missing .architecture-policy.json']
    try:m=json.loads(path.read_text())
    except (ValueError,OSError):return ['Invalid architecture manifest']
    require(m.get('schema_version')==1,'Unknown manifest schema')
    require(m.get('authority_repository')==CANONICAL,'Architecture source must be redd1975/SAAS')
    require(m.get('policy_path')=='architecture/v1/decisions.json','Incorrect canonical policy path')
    require(m.get('baseline')=='1.0.0-owner-confirmed','Unknown baseline; adopt a reviewed version explicitly')
    sha=m.get('canonical_revision','');authority=m.get('repository')==CANONICAL
    require(bool(re.fullmatch('[0-9a-f]{40}',sha)) or (authority and sha=='self'),'Consumer requires immutable canonical commit SHA')
    require(bool(re.fullmatch('[0-9a-f]{64}',m.get('decisions_sha256',''))),'Missing SHA256 decision digest')
    repo=os.getenv('GITHUB_REPOSITORY')
    if repo:require(m.get('repository')==repo,'Manifest repository does not match workflow repository')
    for p in ['AGENTS.md','CLAUDE.md','.github/copilot-instructions.md','docs/ARCHITECTURE.md']:
        f=root/p
        require(f.is_file(),f'Missing {p}')
        if f.is_file():require(CANONICAL in f.read_text(),f'{p} lacks canonical authority pointer')
    require(m.get('implementation_status')=='policy-adoption-only','Do not imply production implementation in adoption manifest')
    if authority:
        try:
            raw=(root/'architecture/v1/decisions.json').read_bytes();d=json.loads(raw)
            require(hashlib.sha256(raw).hexdigest()==m['decisions_sha256'],'Decision digest mismatch')
            records=d['decisions'];require([x['conversation_question_number'] for x in records]==list(range(1,102)),'Need exactly Q1..Q101')
            require(len({x['id'] for x in records})==101,'Duplicate decision ID')
            require(sum(x['status']=='owner-confirmed' for x in records)==100,'Expected 100 active decisions')
            require(records[6]['status']=='superseded' and records[6]['superseded_by']=='HSX-008','Catalog supersession missing')
            require(any(x['id']=='OPEN-102' and x['approved_default'] is None for x in d['open_questions']),'Q102 must remain unresolved')
        except (ValueError,KeyError,OSError):errors.append('Canonical register unreadable or invalid')
    if event and event.get('pull_request'):
        body=event['pull_request'].get('body') or ''
        required={'Architecture-Revision':sha,'Architecture-Impact':None,'Architecture-Decisions':None}
        for name,value in required.items():
            match=re.search(r'^'+name+r':\s*(\S[^\n]*)$',body,re.M)
            require(bool(match),f'PR must include {name}: ...')
            if match and value:require(match.group(1).strip()==value,f'{name} must equal manifest revision')
        match=re.search(r'^Architecture-Decisions:\s*(.+)$',body,re.M)
        if match:
            ids=re.findall(r'HSX-(\d{3})',match.group(1))
            require(bool(ids),'List applicable HSX IDs, not only a checkbox')
            require(all(1<=int(n)<=101 for n in ids),'Unknown HSX ID')
        impact=re.search(r'^Architecture-Impact:\s*(.+)$',body,re.M)
        if impact:require(impact.group(1).strip() in ['documentation-only','implementation','conflict'],'Invalid impact type')
    return errors
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.');parser.add_argument('--event');args=parser.parse_args()
    event_path=args.event or os.getenv('GITHUB_EVENT_PATH');event=json.loads(pathlib.Path(event_path).read_text()) if event_path else None
    errors=check(pathlib.Path(args.root),event)
    for error in errors:print('ERROR: '+error)
    if errors:sys.exit(1)
    print('Architecture adoption metadata and PR acknowledgment valid. Semantic compliance and Owner approval still require review.')
