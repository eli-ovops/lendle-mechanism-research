"""Own bounded anonymous public JSON GET; no source JS, EVM or financial arithmetic."""
from pathlib import Path
import json,hashlib,datetime,ssl,urllib.request,urllib.error,time,sys,resource
P=Path(__file__).resolve().parent;B=P.parents[1]
URL='https://oev-dashboard-backend-aws.api3.org/liquidations?dapp=lendle-mantle'
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
MAX_RESP=8388608;MAX_ALL_SOURCE=16777216;MAX_DISK=33554432;MAX_RSS=536870912
SAFE={'content-type','content-length','content-encoding','date','etag','last-modified','cache-control','server','retry-after','access-control-allow-origin','x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset'}
def save(n,b):
 if not isinstance(b,bytes):b=(json.dumps(b,ensure_ascii=False,indent=2)+'\n').encode()
 f=P/n;old=f.stat().st_size if f.exists() else 0;assert sum(x.stat().st_size for x in P.iterdir() if x.is_file())-old+len(b)<MAX_DISK;f.write_bytes(b)
js=B/'lendle-default-executor-realization-20261019/definition-owner/20261019T152823Z.04.source.js.txt';jraw=js.read_bytes();assert sha(jraw)=='76fb5261842e70a5bc7b93d8298d9b4b4d0d0929d73574b37c11985dec6720d5'
ex=[]
for a,z,label in [(2816250,2817500,'schema and integer parser'),(3926800,3927580,'actual GET function'),(3933340,3933580,'Lendle dapp config')]:ex.append({'label':label,'start_byte':a,'end_byte_exclusive':z,'source_text':jraw[a:z].decode()})
save('static-source-excerpts.json',{'source':str(js),'sha256':sha(jraw),'static_read_only_no_JS_execution':True,'excerpts':ex})
regpath=B/'lendle-september-receipts-complete-20261020/root/all265-receipt-source-registry.json';regraw=regpath.read_bytes();assert sha(regraw)=='4a0c4442152f677fe51699d6a51d10f17222575d6b8cea919afd7a291747a753';reg=json.loads(regraw);np=Path(reg['full_normal_source']);nr=np.read_bytes();assert sha(nr)==reg['full_normal_source_sha256'];nm=json.loads(nr)['records'];E='0x57d8718f0d24db1f3f6445337c8a0c24948d77c2';out=[r['row']['hash'].lower() for r in nm if r['row']['from'].lower()==E];assert len(out)==len(set(out))==262
cp=B/'lendle-asset-quantity-ledger-20261020/execute-owner/fixed119-liquidator-event-references.json';cr=cp.read_bytes();assert sha(cr)=='dba832ec9a3e2817a58e433f7fda364ba54a2137da49c8cd8670edc1b74260e8';cases=json.loads(cr)['cases'];pay=[c['hash'].lower() for c in cases];assert len(pay)==len(set(pay))==119 and set(pay)<=set(out)
save('fixed-cohort-source-scope.json',{'fixed_utc':utc(),'fixed_before_new_network':True,'registry':str(regpath),'registry_sha256':sha(regraw),'normal':str(np),'normal_sha256':sha(nr),'positive_E_case_source':str(cp),'positive_E_case_source_sha256':sha(cr),'fixed119_E_receipt_hashes':pay,'fixed262_E_outgoing_hashes':out,'only_identity_field_coverage_not_valuation':True,'old_network_bill_outputs_read_or_recalculated':False})
save('request-scope.json',{'fixed_utc':utc(),'source_derived_URL':URL,'method':'GET','parameters':{'dapp':'lendle-mantle'},'parameter_provenance':'retained official frontend E10 function and JR Lendle configuration','maximum_public_actions':6,'this_script_actions':1,'maximum_each_body_bytes':MAX_RESP,'maximum_all_source_body_bytes':MAX_ALL_SOURCE,'maximum_disk_bytes':MAX_DISK,'maximum_RSS_bytes':MAX_RSS,'timeout_seconds':25,'whole_task_deadline_utc':'2026-10-19T18:37:05Z','strict_default_TLS':True,'redirects_retries_authentication_source_execution_financial_calculation':False,'actual_model_effort':'UNKNOWN'})
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**kw):return None
opener=urllib.request.build_opener(NoRedirect,urllib.request.HTTPSHandler(context=ssl.create_default_context()))
started=utc();status=None;headers={};body=b'';err=None;complete=False;limit=None
try:
 try:r=opener.open(urllib.request.Request(URL,headers={'Accept':'application/json'},method='GET'),timeout=25)
 except urllib.error.HTTPError as e:r=e
 status=r.code;headers={k.lower():v for k,v in r.headers.items() if k.lower() in SAFE};cl=headers.get('content-length');length=int(cl) if cl is not None and cl.isdigit() else None
 if length is not None and length>MAX_RESP:limit='DECLARED_BODY_EXCEEDS_8MiB_NO_BODY_READ'
 else:
  parts=[];total=0
  while total<MAX_RESP:
   chunk=r.read(min(65536,MAX_RESP-total))
   if not chunk:complete=True;break
   parts.append(chunk);total+=len(chunk)
  body=b''.join(parts)
  if length is not None and len(body)==length:complete=True
  if not complete:limit='8MiB_BODY_LIMIT_INCOMPLETE_PREFIX_ONLY'
 r.close()
except Exception as e:err=type(e).__name__+': '+str(e)
save('01-request.json',{'method':'GET','url':URL,'anonymous':True,'no_credentials_or_auth_headers':True});save('01-response.source.json',body);save('01-headers-safe.json',headers)
meta={'public_action':1,'url':URL,'method':'GET','started_utc':started,'finished_utc':utc(),'http_status':status,'body_bytes':len(body),'body_sha256':sha(body),'complete_response_body':complete,'limit_stop':limit,'error':err,'strict_default_TLS':True,'headers_safe_allowlist':sorted(SAFE),'source_refusal_auth_limit_stop':status in (401,402,403,407,429),'no_retry_redirect_identity_or_proxy_change':True,'source_executed':False,'amount_arithmetic_or_price_inference':False,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)}
save('01-acquisition.json',meta)
print(json.dumps(meta))
