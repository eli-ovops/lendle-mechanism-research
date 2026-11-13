"""Supported same-URL default strict-TLS curl after urllib HTTP-before-handshake error."""
from pathlib import Path
import subprocess,json,hashlib,datetime,resource,sys
P=Path(__file__).resolve().parent;URL='https://oev-dashboard-backend-aws.api3.org/liquidations?dapp=lendle-mantle'
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
assert not (P/'02-response.source.json').exists()
SAFE={'content-type','content-length','content-encoding','date','etag','last-modified','cache-control','server','retry-after','access-control-allow-origin','x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset'}
cmd=['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize','8388608','--dump-header','-','--output',str(P/'02-response.source.json'),'--write-out','\nOWN_CURL_METADATA:%{json}','--header','Accept: application/json',URL]
started=utc();p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);finished=utc();head,marker,metadata=p.stdout.partition(b'\nOWN_CURL_METADATA:');safe={};statuslines=[]
for line in head.decode('iso-8859-1').splitlines():
 if line.startswith('HTTP/'):statuslines.append(line)
 if ':' in line:
  k,v=line.split(':',1)
  if k.lower() in SAFE:safe[k.lower()]=v.strip()
info=json.loads(metadata) if marker else {};chosen={k:info.get(k) for k in ['http_code','size_download','content_type','ssl_verify_result','url_effective','num_redirects','time_total']}
f=P/'02-response.source.json';body=f.read_bytes() if f.exists() else b''
if not f.exists():f.write_bytes(b'')
assert len(body)<=8388608
complete=p.returncode==0 and chosen.get('http_code')==200
meta={'public_action':2,'url':URL,'method':'GET anonymous public JSON','started_utc':started,'finished_utc':finished,'curl_exit_code':p.returncode,'curl_selected_metadata':chosen,'http_status_lines':statuslines,'body_bytes':len(body),'body_sha256':sha(body),'complete_response_body':complete,'source_refusal_auth_limit_stop':chosen.get('http_code') in (401,402,403,407,429),'error_stderr':p.stderr.decode(errors='replace'),'default_strict_TLS_no_version_or_cipher_override':True,'curl_config_loading_disabled':True,'no_redirect_auth_proxy_or_custom_identity_override':True,'source_code_or_financial_arithmetic_executed':False,'supported_fallback_from_action1':'LOCAL_BLOCKERS139 urllib handshake without HTTP refusal -> ordinary curl default TLS same URI; explicit Root confirmation retained in task','no_further_request_if_this_fails_or_refuses':True,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)}
for name,obj in [('02-request.json',{'method':'GET','url':URL,'anonymous':True,'curl_options_excluding_output_paths':['-q','--max-time25','--connect-timeout10','--max-filesize8388608','Accept: application/json']}),('02-headers-safe.json',safe),('02-acquisition.json',meta)]: (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(meta))
