"""Own bounded public source acquisition; address labels only, no account action."""
from pathlib import Path
import json,hashlib,datetime,subprocess,time
P=Path(__file__).resolve().parent;P.mkdir(parents=True,exist_ok=True)
B=P.parent.parent
U=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
H=lambda b:hashlib.sha256(b).hexdigest()
E='0x57d8718f0d24db1f3f6445337c8a0c24948d77c2'
N=B/'lendle-september-original-records-20261020/acquire-owner/E_normal.rows.json'
G=B/'lendle-september-receipts-complete-20261020/root/all265-receipt-source-registry.json'
n=json.loads(N.read_bytes());g=json.loads(G.read_bytes());idx={x['hash'].lower():x for x in g['entries']}
incoming=[x for x in n['records']if x['row'].get('to','').lower()==E and x['row'].get('from','').lower()!=E]
assert len(incoming)==3
ident=[]
for wrapper in incoming:
 row=wrapper['row'];entry=idx[row['hash'].lower()];f=Path(entry['parsed']);raw=f.read_bytes();assert H(raw)==entry['parsed_sha256']
 j=json.loads(raw);data=j['result']['structuredContent']['data'];r=data['result']
 assert data['ok'] is True and r['transactionHash'].lower()==row['hash'].lower()and r['from'].lower()==row['from'].lower()and r['to'].lower()==E
 ident.append({'hash':row['hash'],'from':row['from'],'to':row['to'],'input':row['input'],'blockNumber':row['blockNumber'],'timeStamp':row['timeStamp'],'receipt_status':r['status'],'receipt_type':r['type'],'logs':r['logs'],'log_count':len(r['logs']),'contractAddress':r.get('contractAddress'),'normal_source_page':wrapper.get('source_page'),'normal_source_row':wrapper.get('source_row'),'receipt_parsed_path':str(f),'receipt_parsed_sha256':H(raw),'receipt_SSE_path':entry['source'],'receipt_SSE_sha256':entry['source_sha256'],'income_purpose_from_existing_record':'UNKNOWN'})
assert all(x['input']=='0x'and x['log_count']==0 for x in ident)
fixed={'fixed_utc':U(),'scope':'Classify only three existing incoming native transfers via existing receipt context and two actual sender address pages; no money arithmetic','existing_normal_path':str(N),'existing_normal_sha256':H(N.read_bytes()),'receipt_registry_path':str(G),'receipt_registry_sha256':H(G.read_bytes()),'transactions':ident,'public_URLs':['https://mantlescan.xyz/address/0x91604f590d66ace8975eed6bd16cf55647d1c499','https://mantlescan.xyz/address/0x5c30940a4544ca845272fe97c4a27f2ed2cd7b64'],'public_action_cap':4,'single_raw_cap':1048576,'all_raw_cap':2097152,'disk_cap':4194304,'deadline_utc':'2026-10-19T19:13:10Z','no_source_code_EVM_model_price_or_amount_calculation':True}
(P/'fixed-source-scope.json').write_text(json.dumps(fixed,indent=2)+'\n')
SAFE={'content-type','content-length','content-encoding','date','etag','last-modified','cache-control','server','retry-after'}
for i,url in enumerate(fixed['public_URLs'],1):
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,10,19,19,13,10,tzinfo=datetime.timezone.utc):break
 f=P/f'{i:02d}-sender-address.source.html';assert not f.exists()
 (P/f'{i:02d}-sender-address.request.json').write_text(json.dumps({'method':'GET','url':url,'fixed_before_request_utc':U(),'scope_sha256':H((P/'fixed-source-scope.json').read_bytes()),'timeout_seconds':25,'body_cap':1048576,'strict_default_TLS':True,'no_login_or_credentials_or_proxy_identity_changes':True},indent=2)+'\n')
 cmd=['/usr/bin/curl','-q','--silent','--show-error','--max-time','25','--connect-timeout','10','--max-filesize','1048576','--dump-header','-','--output',str(f),'--write-out','\nOWN_META:%{json}',url]
 start=U();r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30);end=U();heads,sep,meta=r.stdout.partition(b'\nOWN_META:');info=json.loads(meta)if sep else {};safe={}
 for line in heads.decode('iso-8859-1').splitlines():
  if ':'in line:
   k,v=line.split(':',1)
   if k.lower()in SAFE:safe[k.lower()]=v.strip()
 b=f.read_bytes()if f.exists()else b''
 if not f.exists():f.write_bytes(b'')
 result={'public_action':i,'url':url,'started_utc':start,'finished_utc':end,'http_status':info.get('http_code'),'curl_exit':r.returncode,'strict_TLS_verify_result':info.get('ssl_verify_result'),'redirects':info.get('num_redirects'),'body_bytes':len(b),'sha256':H(b),'safe_headers':safe,'stderr':r.stderr.decode(errors='replace'),'complete':r.returncode==0 and info.get('http_code')==200,'refusal_or_auth_or_ratelimit':info.get('http_code')in[401,402,403,407,429]}
 (P/f'{i:02d}-sender-address.acquisition.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 if not result['complete']:break
 time.sleep(1)
