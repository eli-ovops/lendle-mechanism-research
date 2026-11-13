"""Own bounded public documentation/text getter; no source execution."""
from pathlib import Path
import subprocess,json,sys,hashlib,datetime
P=Path(__file__).resolve().parent;P.mkdir(parents=True,exist_ok=True)
number,url=sys.argv[1:];target=P/(number+'.source.txt')
assert not target.exists(),'No overwrite/refetch'
U=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
H=lambda b:hashlib.sha256(b).hexdigest()
SAFE={'content-type','content-length','content-encoding','date','etag','last-modified','cache-control','server','retry-after'}
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,19,19,5,30,tzinfo=datetime.timezone.utc)
assert sum(f.stat().st_size for f in P.glob('*.source.txt'))<2097152
(P/(number+'.request.json')).write_text(json.dumps({'fixed_utc':U(),'method':'GET','url':url,'max_body_bytes':2097152,'timeout_seconds':25,'strict_default_TLS':True,'no_source_execution_or_price_requests':True},indent=2)+'\n')
cmd=['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize','2097152','--dump-header','-','--output',str(target),'--write-out','\nOWN_META:%{json}',url]
start=U();r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);end=U()
headers,sep,metadata=r.stdout.partition(b'\nOWN_META:');info=json.loads(metadata)if sep else {};safe={}
for line in headers.decode('iso-8859-1').splitlines():
 if ':'in line:
  k,v=line.split(':',1)
  if k.lower()in SAFE:safe[k.lower()]=v.strip()
b=target.read_bytes()if target.exists()else b''
if not target.exists():target.write_bytes(b'')
rec={'url':url,'started_utc':start,'finished_utc':end,'curl_exit':r.returncode,'http_status':info.get('http_code'),'strict_TLS_verify_result':info.get('ssl_verify_result'),'redirects':info.get('num_redirects'),'bytes':len(b),'sha256':H(b),'safe_headers':safe,'stderr':r.stderr.decode(errors='replace'),'complete':r.returncode==0 and info.get('http_code')==200,'refusal_auth_limit':info.get('http_code')in[401,402,403,407,429]}
(P/(number+'.acquisition.json')).write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec))
