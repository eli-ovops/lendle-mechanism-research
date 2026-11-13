"""Own bounded static official-doc asset GET; no source JS execution or price request."""
from pathlib import Path
import subprocess,json,hashlib,datetime,sys,resource
P=Path(__file__).resolve().parent
URL='https://api-docs.defillama.com/assets/api-specifications-Crq_v_wx.js'
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
SAFE={'content-type','content-length','content-encoding','date','etag','last-modified','cache-control','server','retry-after'}
cmd=['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize','4194304','--dump-header','-','--output',str(P/'01-api-specifications.source.js.txt'),'--write-out','\nOWN_META:%{json}',URL]
(P/'01-doc-request.json').write_text(json.dumps({'fixed_utc':utc(),'public_action':1,'method':'GET','url':URL,'source_link_provenance':'Actual modulepreload href in prior official docs HTML 04-defillama-docs.source.html; no path guessing','scope':'Official static OpenAPI/source text only; no new prices until Root freezes unified rule','maximum_body_bytes':4194304,'whole_new_source_bytes_cap':8388608,'new_disk_bytes_cap':16777216,'deadline_utc':'2026-10-19T18:56:10Z','TLS_default_strict':True,'no_login_JS_execution_EVM_price_or_PnL_calculation':True},indent=2)+'\n')
start=utc();r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);end=utc();head,marker,meta=r.stdout.partition(b'\nOWN_META:');info=json.loads(meta) if marker else {};safe={}
for line in head.decode('iso-8859-1').splitlines():
 if ':'in line:
  k,v=line.split(':',1)
  if k.lower()in SAFE:safe[k.lower()]=v.strip()
f=P/'01-api-specifications.source.js.txt';body=f.read_bytes() if f.exists() else b''
if not f.exists():f.write_bytes(b'')
assert len(body)<=4194304
result={'public_action':1,'url':URL,'started_utc':start,'finished_utc':end,'curl_exit':r.returncode,'http_status':info.get('http_code'),'SSL_verify_result':info.get('ssl_verify_result'),'content_type':info.get('content_type'),'body_bytes':len(body),'sha256':sha(body),'complete':r.returncode==0 and info.get('http_code')==200,'error':r.stderr.decode(errors='replace'),'refusal_auth_rate_limit':info.get('http_code')in(401,402,403,407,429),'no_redirect_or_tls_proxy_identity_override':True,'source_executed_or_prices_requested':False,'peak_RSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)}
(P/'01-doc-headers-safe.json').write_text(json.dumps(safe,indent=2)+'\n');(P/'01-doc-acquisition.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
