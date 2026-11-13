from pathlib import Path
import urllib.request,urllib.error,ssl,datetime,hashlib,json,sys
P=Path(__file__).resolve().parent
label,url=sys.argv[1:]
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
opener=urllib.request.build_opener(NoRedirect,urllib.request.HTTPSHandler(context=ssl.create_default_context()))
start=datetime.datetime.now(datetime.timezone.utc).isoformat();raw=b'';status=None;headers={};error=None
try:
 try:r=opener.open(url,timeout=25)
 except urllib.error.HTTPError as e:r=e
 status=r.code;headers={k.lower():v for k,v in r.headers.items() if k.lower() in ('content-type','content-length','date','last-modified','etag','location','x-ratelimit-remaining','x-ratelimit-reset')};raw=r.read(2*1024*1024+1);r.close()
 if len(raw)>2*1024*1024:raw=raw[:2*1024*1024];error='local2MiB cap'
except Exception as e:error=type(e).__name__+': '+str(e)
(P/(label+'.source')).write_bytes(raw)
meta={'url':url,'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'http_status':status,'headers':headers,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'error':error,'method':'ordinary default TLS public GET, no auth, no source execution, no redirect follow'}
(P/(label+'.receipt.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(json.dumps(meta,ensure_ascii=False))
