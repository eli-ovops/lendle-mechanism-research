"""Own bounded anonymous GET client; no vendor code execution or valuation."""
from pathlib import Path
import json,hashlib,datetime,subprocess,time,resource,sys
from urllib.parse import urlencode
P=Path(__file__).resolve().parent
R=P.parent/'root'
H=lambda b:hashlib.sha256(b).hexdigest()
U=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
SAFE={'content-type','content-length','content-encoding','date','etag','last-modified','cache-control','server','retry-after'}
DEADLINE=datetime.datetime(2026,10,19,18,56,10,tzinfo=datetime.timezone.utc)
protocol=(R/'protocol.json').read_bytes();requests=(R/'fixed-price-requests.json').read_bytes()
assert H(protocol)=='01946f8f3a98d63060d37fab3993a671b3cc9c2b77d45a97d865c5ca6b7a007e'
assert H(requests)=='1e7d741d116397281a1c843a488f6034ecef3ffa2c108c3f98a048a5e32000b1'
j=json.loads(requests);pairs=sorted((c,t)for c,ts in j['coins'].items()for t in ts)
assert len(pairs)==376 and len(set(pairs))==376 and len(j['coins'])==10
def package(ps):
 coins={}
 for c,t in ps:coins.setdefault(c,[]).append(t)
 query=json.dumps(coins,separators=(',',':'),sort_keys=True)
 url='https://coins.llama.fi/batchHistorical?'+urlencode({'coins':query})
 return {'pairs':[[c,t]for c,t in ps],'coins':coins,'query_coins_json':query,'url':url,'url_bytes':len(url.encode())}
chunks=[];cur=[]
for pair in pairs:
 candidate=package(cur+[pair])
 if cur and (len(cur)>=90 or candidate['url_bytes']>7000):chunks.append(package(cur));cur=[]
 cur.append(pair)
if cur:chunks.append(package(cur))
assert len(chunks)==5 and sum(len(x['pairs'])for x in chunks)==376
assert all(len(x['pairs'])<=90 and x['url_bytes']<=7000 for x in chunks)
manifest={'fixed_utc':U(),'protocol_sha256':H(protocol),'fixed_requests_sha256':H(requests),'root_authorization':'Root message: confirmed exactly five unique batches, USD remains UNKNOWN; no more docs or retries','pre_price_public_action_count_conservative':5,'public_action_cap':10,'deadline_utc':DEADLINE.isoformat(),'limits':{'single_raw_bytes':4194304,'total_raw_bytes':8388608,'new_disk_bytes':16777216,'memory_bytes':536870912,'threads':1},'USD_definition_verified':False,'price_time_coverage_only_no_valuation':True,'chunks':[dict(x,batch=i+1,public_action=i+6,request_pairs=len(x['pairs']))for i,x in enumerate(chunks)]}
mf=P/'fixed-five-batch-request-manifest.json'
assert not mf.exists(), 'Do not overwrite frozen request manifest'
mf.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'frozen_manifest':str(mf),'sha256':H(mf.read_bytes()),'batches':len(chunks),'pairs':len(pairs),'urls_bytes':[x['url_bytes']for x in chunks]}),flush=True)
records=[];stop=None
for n,x in enumerate(chunks,1):
 if datetime.datetime.now(datetime.timezone.utc)>=DEADLINE:stop='deadline_before_request';break
 raw_so_far=sum(f.stat().st_size for f in P.glob('*.source*'))
 disk=sum(f.stat().st_size for f in P.rglob('*')if f.is_file())
 if raw_so_far+4194304>8388608 or disk+8388608>16777216:stop='conservative_resource_budget';break
 prefix=f'{n+5:02d}-batch-{n:02d}';target=P/(prefix+'.source.json')
 req={'manifest_sha256':H(mf.read_bytes()),'public_action':n+5,'batch':n,'method':'GET','url':x['url'],'coins':x['coins'],'maximum_body_bytes':4194304,'default_strict_TLS':True,'timeout_seconds':25,'no_retry':True}
 (P/(prefix+'.request.json')).write_text(json.dumps(req,indent=2)+'\n')
 cmd=['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize','4194304','--dump-header','-','--output',str(target),'--write-out','\nOWN_META:%{json}',x['url']]
 began=U();r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);ended=U()
 head,marker,meta=r.stdout.partition(b'\nOWN_META:');info=json.loads(meta)if marker else {};safe={}
 for line in head.decode('iso-8859-1').splitlines():
  if ':'in line:
   k,v=line.split(':',1)
   if k.lower()in SAFE:safe[k.lower()]=v.strip()
 b=target.read_bytes()if target.exists()else b''
 if not target.exists():target.write_bytes(b'')
 record={'public_action':n+5,'batch':n,'url':x['url'],'started_utc':began,'finished_utc':ended,'curl_exit':r.returncode,'http_status':info.get('http_code'),'SSL_verify_result':info.get('ssl_verify_result'),'body_bytes':len(b),'sha256':H(b),'safe_headers':safe,'stderr':r.stderr.decode(errors='replace'),'complete_HTTP_200':r.returncode==0 and info.get('http_code')==200,'source_executed':False,'price_arithmetic_or_valuation':False}
 records.append(record);(P/(prefix+'.acquisition.json')).write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps({'batch':n,'http':record['http_status'],'bytes':len(b),'complete':record['complete_HTTP_200']}),flush=True)
 if not record['complete_HTTP_200']:stop='HTTP_or_transport_failure_no_retry';break
 try:
  parsed=json.loads(b,parse_float=str)
  if not isinstance(parsed,dict)or not isinstance(parsed.get('coins'),dict):raise ValueError('Missing documented coins object')
  if parsed.get('error')or parsed.get('message'):raise ValueError('Provider error/message requires stop')
  if set(parsed['coins'])-set(x['coins']):raise ValueError('Unexpected coin identity')
  (P/(prefix+'.parsed-preserved.json')).write_text(json.dumps(parsed,indent=2)+'\n')
 except Exception as exc:stop='parse_or_business_or_identity_error:'+str(exc);break
 if n<5:time.sleep(1)
receipt={'finished_utc':U(),'state':'COMPLETE_FIXED_FIVE_BATCHES'if len(records)==5 and stop is None else 'STOP_PARTIAL','stop_reason':stop,'public_action_count_conservative':5+len(records),'public_action_cap':10,'new_price_HTTP_requests':len(records),'request_manifest_sha256':H(mf.read_bytes()),'records':records,'USD_definition_verified':False,'network_stopped':True,'peak_RSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024),'no_quantity_scaling_fees_valuation_PnL_or_source_execution':True,'actual_model_effort':'UNKNOWN'}
(P/'fixed-batch-acquisition-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'state':receipt['state'],'actions':receipt['public_action_count_conservative'],'stop':stop}),flush=True)
