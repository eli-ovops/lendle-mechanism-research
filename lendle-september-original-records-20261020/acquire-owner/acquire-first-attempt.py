"""Bounded own anonymous MCP client: public records only, no financial arithmetic."""
from pathlib import Path
import json,hashlib,datetime,time,urllib.request,urllib.error,ssl,re,resource,sys,collections
P=Path(__file__).resolve().parent
URL='https://mcp-keyless.etherscan.io/mcp'
SCHEMA=Path('/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/lendle-complete-ledger-originals-admission-20261020/root/mcp-tools-list.parsed.json')
OLD=Path('/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/lendle-default-executor-realization-20261019/root/september-published-top-level-index-derived.json')
START=1788220800;END=1790812800;DEADLINE=datetime.datetime.fromisoformat('2026-10-19T16:41:01+00:00').timestamp()
MAX_REQ=40;MAX_RESP=4*1024*1024;MAX_DISK=64*1024*1024;MAX_RSS=512*1024*1024
E='0x57D8718f0d24DB1F3F6445337c8A0C24948d77c2';X='0x5483e9260d84b16ac5a32f2CEB333C762dB74718'
DATASETS=[(a,n,tool) for a in ['E','X'] for n,tool in [('normal','get_transactions'),('internal','get_internal_transactions'),('erc20','get_token_transfers')]]
ADDR={'E':E,'X':X};request_count=0;last_end=None;session=None;protocol='2025-03-26';requests=[];results={};stop_reason=None;block_window=None
sha=lambda b:hashlib.sha256(b).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def rss():
 n=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
 return n if sys.platform=='darwin' else n*1024
def used():return sum(x.stat().st_size for x in P.rglob('*') if x.is_file())
def save(name,b):
 if not isinstance(b,bytes):b=b.encode()
 if used()+len(b)>MAX_DISK-1024*1024:raise RuntimeError('LOCAL_DISK_BUDGET_STOP')
 (P/name).write_bytes(b)
def jsave(name,o):save(name,json.dumps(o,ensure_ascii=False,indent=2)+'\n')
fixed={'created_utc':utc(),'endpoint':URL,'chainid':'5000','addresses':ADDR,'month_half_open_utc':['2026-09-01T00:00:00Z','2026-10-01T00:00:00Z'],'timestamps':[START,END],'block_lookup_closest':'before at both endpoints','record_query_block_interval':'both returned blocks inclusive; preserve all wide-window records and mark month membership by row timestamp','datasets_in_fixed_order':[a+'_'+n for a,n,t in DATASETS],'page_start':1,'offset':200,'sort':'asc','termination':'actual empty result[] with success or explicit No transactions found empty-list semantics; short page still followed by another page; NOTOK/parse/error not empty','network_max':40,'minimum_seconds_between_requests':1,'deadline_utc':'2026-10-19T16:41:01Z','max_response_bytes':MAX_RESP,'max_new_disk_bytes':MAX_DISK,'max_resident_memory_bytes':MAX_RSS,'financial_arithmetic':False,'original_rows_never_deduplicated':True,'session_id_persistence':False,'no_redirect_or_identity_retry':True,'source_schema':str(SCHEMA),'source_schema_sha256':sha(SCHEMA.read_bytes()),'prior_index':str(OLD),'prior_index_sha256':sha(OLD.read_bytes()),'actual_model_effort':'UNKNOWN'}
jsave('fixed-parameters.json',fixed)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
opener=urllib.request.build_opener(NoRedirect,urllib.request.HTTPSHandler(context=ssl.create_default_context()))
def parse_body(raw):
 s=raw.decode('utf-8');events=[]
 if not s.strip():return None
 if s.lstrip().startswith(('{','[')):return json.loads(s)
 for block in re.split(r'\r?\n\r?\n',s):
  lines=[x[5:].lstrip() for x in block.splitlines() if x.startswith('data:')]
  if lines:events.append(json.loads('\n'.join(lines)))
 replies=[x for x in events if isinstance(x,dict) and ('result' in x or 'error' in x)]
 if len(replies)!=1:raise ValueError('MCP_RESPONSE_NOT_ONE_REPLY')
 return replies[0]
def req(label,payload,notification=False):
 global request_count,last_end,session,protocol
 if request_count>=MAX_REQ:raise RuntimeError('REQUEST_BUDGET_STOP')
 if time.time()>DEADLINE-26:raise RuntimeError('TIME_BUDGET_STOP')
 if rss()>MAX_RSS:raise RuntimeError('MEMORY_BUDGET_STOP')
 if used()>MAX_DISK-10*1024*1024:raise RuntimeError('DISK_RESERVE_STOP')
 if last_end is not None:time.sleep(max(0,1-(time.monotonic()-last_end)))
 request_count+=1;idx=request_count;prefix=f'{idx:02d}-{label}';body=json.dumps(payload,separators=(',',':')).encode();save(prefix+'.request.json',body+b'\n')
 headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
 if session:headers['Mcp-Session-Id']=session;headers['MCP-Protocol-Version']=protocol
 started=utc();status=None;safe={};raw=b'';truncated=False;error=None;new_session=None
 try:
  try:res=opener.open(urllib.request.Request(URL,data=body,headers=headers,method='POST'),timeout=25)
  except urllib.error.HTTPError as e:res=e
  status=res.code;safe={k.lower():v for k,v in res.headers.items() if k.lower() in {'content-type','content-length','date','server','retry-after','x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset'}}
  new_session=res.headers.get('Mcp-Session-Id');raw=res.read(MAX_RESP+1);res.close()
  if len(raw)>MAX_RESP:raw=raw[:MAX_RESP];truncated=True
 except Exception as e:error=type(e).__name__+': '+str(e)
 finally:last_end=time.monotonic()
 # Never persist transport session identifier or optional SSE resumption id lines.
 stored=raw;redacted=False
 for token in [session,new_session]:
  if token and token.encode() in stored:stored=stored.replace(token.encode(),b'[SESSION_ID_REDACTED]');redacted=True
 if re.search(br'(?m)^id:',stored):stored=re.sub(br'(?m)^id:[^\r\n]*(?:\r?\n)?',b'',stored);redacted=True
 save(prefix+'.response.sse',stored);jsave(prefix+'.headers-safe.json',safe)
 meta={'request_number':idx,'label':label,'url':URL,'method':'POST MCP JSON-RPC public data tool only','started_utc':started,'finished_utc':utc(),'http_status':status,'response_stored_bytes':len(stored),'response_acquired_sha256':sha(raw),'response_stored_sha256':sha(stored),'response_truncated_at_cap':truncated,'session_or_sse_id_removed_from_stored_body':redacted,'transport_session_header_saved':False,'error':error,'source_files':[prefix+'.request.json',prefix+'.response.sse',prefix+'.headers-safe.json']}
 requests.append(meta);jsave(prefix+'.acquisition.json',meta)
 print(json.dumps({'request':idx,'label':label,'http':status,'bytes':len(stored),'error':error}),flush=True)
 if error:raise RuntimeError('TRANSPORT_FAILURE_STOP')
 if truncated:raise RuntimeError('RESPONSE_SIZE_CAP_STOP')
 if status in (401,402,403,429):raise RuntimeError('HTTP_AUTH_OR_QUOTA_DENIAL_STOP_'+str(status))
 if status not in (200,202,204):raise RuntimeError('HTTP_FAILURE_STOP_'+str(status))
 if new_session:session=new_session
 if notification:
  if raw.strip():parse_body(raw)
  return None,prefix
 o=parse_body(raw)
 if not isinstance(o,dict) or 'error' in o:raise RuntimeError('MCP_PROTOCOL_ERROR_STOP')
 if o.get('id')!=payload.get('id'):raise RuntimeError('MCP_RESPONSE_ID_MISMATCH_STOP')
 return o,prefix
next_id=1
def call(tool,args,label):
 global next_id
 next_id+=1;o,prefix=req(label,{'jsonrpc':'2.0','id':next_id,'method':'tools/call','params':{'name':tool,'arguments':args}})
 r=o.get('result',{});data=r.get('structuredContent',{}).get('data');texts=[]
 for c in r.get('content',[]):
  if c.get('type')=='text':
   try:texts.append(json.loads(c.get('text','')))
   except (ValueError,TypeError):pass
 if data is None and len(texts)==1:data=texts[0]
 if data is None:raise RuntimeError('TOOL_RESULT_STRUCTURE_UNKNOWN')
 agreement=all(t==data for t in texts) if texts else None
 jsave(prefix+'.tool-data.json',{'tool_data':data,'structured_text_agreement':agreement,'mcp_isError':r.get('isError',False)})
 message=str(data.get('message','')) if isinstance(data,dict) else ''
 if re.search(r'rate.?limit|quota|api.?key|unauthor|forbidden|access.denied|too many|credit|payment|required.*plan',message,re.I):raise RuntimeError('TOOL_AUTH_OR_QUOTA_DENIAL_STOP')
 if r.get('isError'):raise RuntimeError('MCP_TOOL_ERROR_STOP')
 if agreement is False:raise RuntimeError('STRUCTURED_TEXT_DISAGREEMENT_STOP')
 return data,prefix
try:
 init,_=req('initialize',{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':protocol,'capabilities':{},'clientInfo':{'name':'public-original-availability-research','version':'1.0'}}})
 protocol=init['result']['protocolVersion']
 req('initialized',{'jsonrpc':'2.0','method':'notifications/initialized'},True)
 blocks=[]
 for label,ts in [('start',START),('end',END)]:
  data,prefix=call('get_block_by_timestamp',{'chainid':'5000','timestamp':ts,'closest':'before'},'block-'+label)
  if not isinstance(data,dict) or data.get('ok') is not True or str(data.get('status'))!='1' or not re.fullmatch(r'[0-9]+',str(data.get('result',''))):raise RuntimeError('BOUNDARY_BLOCK_NOT_CONFIRMED')
  blocks.append(int(data['result']))
 block_window=blocks;jsave('block-window.json',{'startblock_inclusive':blocks[0],'endblock_inclusive':blocks[1],'timestamp_interval_half_open':[START,END],'lookup':'closest before both endpoints'})
 if blocks[0]>blocks[1]:raise RuntimeError('INVALID_BLOCK_ORDER')
 for actor,kind,tool in DATASETS:
  key=actor+'_'+kind;records=[];pages=[];results[key]={'address':ADDR[actor],'tool':tool,'status':'IN_PROGRESS','pages':pages,'records':records};page=1
  while True:
   args={'address':ADDR[actor],'chainid':'5000','startblock':blocks[0],'endblock':blocks[1],'page':page,'offset':200,'sort':'asc'}
   if kind=='erc20':args['standard']='erc20'
   data,prefix=call(tool,args,key+'-page'+str(page))
   if not isinstance(data,dict):raise RuntimeError('TOOL_DATA_NOT_OBJECT')
   rows=data.get('result');status=str(data.get('status'));message=str(data.get('message',''))
   empty=isinstance(rows,list) and len(rows)==0 and ((data.get('ok') is True and status=='1') or (status=='0' and re.fullmatch(r'No (?:transactions|records) found[.!]?',message.strip(),re.I)))
   if not isinstance(rows,list) or (not empty and (data.get('ok') is not True or status!='1')):raise RuntimeError('BUSINESS_RESULT_NOT_VALID_RECORDS_OR_EXPLICIT_EMPTY')
   if len(rows)>200:raise RuntimeError('PAGE_LARGER_THAN_FIXED_OFFSET')
   pages.append({'page':page,'response_prefix':prefix,'business_ok':data.get('ok'),'business_status':status,'business_message':message,'row_count':len(rows),'valid_empty_terminal':empty})
   for i,row in enumerate(rows,1):
    if not isinstance(row,dict):raise RuntimeError('NON_OBJECT_ROW')
    ts=row.get('timeStamp');valid=isinstance(ts,(str,int)) and re.fullmatch(r'[0-9]+',str(ts)) is not None
    records.append({'source_page':page,'source_row_1based':i,'source_response':prefix+'.response.sse','in_half_open_month':START<=int(ts)<END if valid else None,'row':row})
   jsave(key+'.rows.json',results[key])
   print(json.dumps({'dataset':key,'page':page,'rows':len(rows),'terminal':empty}),flush=True)
   if empty:results[key]['status']='COMPLETE_PROVIDER_PAGINATION_TO_EMPTY';break
   page+=1
  jsave(key+'.rows.json',results[key])
except Exception as e:
 stop_reason=type(e).__name__+': '+str(e);print(json.dumps({'STOP':stop_reason}),flush=True)
finally:
 # Session token is memory-only and is deliberately not included in any saved file.
 session=None
 for actor,kind,tool in DATASETS:
  key=actor+'_'+kind
  if key not in results:results[key]={'address':ADDR[actor],'tool':tool,'status':'NOT_REQUESTED_AFTER_STOP','pages':[],'records':[]}
  elif results[key]['status']=='IN_PROGRESS':results[key]['status']='PARTIAL_STOPPED_UNKNOWN'
  jsave(key+'.rows.json',results[key])
 qc={}
 for actor,kind,tool in DATASETS:
  key=actor+'_'+kind;s=results[key];rows=s['records'];monthly=[z for z in rows if z['in_half_open_month'] is True];raw=[z['row'] for z in monthly]
  fields=sorted({k for z in raw for k in z});h=[str(z.get('hash','')).lower() for z in raw];counts=collections.Counter(h);badts=[i for i,z in enumerate(rows,1) if z['in_half_open_month'] is None];times=[int(z['row']['timeStamp']) for z in rows if z['in_half_open_month'] is not None]
  q={'status':s['status'],'pages':s['pages'],'wide_window_rows':len(rows),'month_rows':len(monthly),'out_of_month_rows_preserved':len(rows)-len(monthly)-len(badts),'unknown_timestamp_rows':badts,'all_timestamps_nondecreasing':all(a<=b for a,b in zip(times,times[1:])),'fields_union':fields,'field_missing_counts':{f:sum(f not in z for z in raw) for f in fields},'hash_missing_or_invalid_count':sum(re.fullmatch(r'0x[0-9a-f]{64}',v) is None for v in h),'unique_parent_hashes':len(counts),'all_original_rows_preserved':True,'within_block_window':all(block_window[0]<=int(z['row']['blockNumber'])<=block_window[1] for z in rows if block_window and re.fullmatch(r'[0-9]+',str(z['row'].get('blockNumber','')))) if block_window else None,'block_number_missing_or_invalid_count':sum(not re.fullmatch(r'[0-9]+',str(z['row'].get('blockNumber',''))) for z in rows)}
  if kind=='normal':q['normal_hash_unique']=len(h)==len(counts);q['duplicate_hashes_preserved']=[v for v,c in counts.items() if c>1]
  if kind=='internal':
   q['trace_identity_fields_seen']=[f for f in fields if 'trace' in f.lower()];q['traceId_missing_count']=sum('traceId' not in z for z in raw);keys=[(str(z.get('hash','')).lower(),str(z.get('traceId'))) for z in raw if 'traceId' in z];q['hash_traceId_duplicate_keys_preserved']=[list(k) for k,c in collections.Counter(keys).items() if c>1];q['identity_limit']='hash+traceId checked only where available; absence/duplicates do not license deduplication'
  if kind=='erc20':
   q['logIndex_missing_count']=sum('logIndex' not in z for z in raw);keys=[(str(z.get('hash','')).lower(),str(z.get('logIndex'))) for z in raw if 'logIndex' in z];q['hash_logIndex_duplicate_keys_preserved']=[list(k) for k,c in collections.Counter(keys).items() if c>1];q['multi_row_parent_hashes_expected_count']=sum(c>1 for c in counts.values());q['identity_limit']='Without logIndex, precise event identity is not established; same-hash and identical-value rows retained, never deduplicated'
  qc[key]=q
 comparison={'status':'NOT_COMPARABLE_PARTIAL_OR_MISSING'}
 en=results.get('E_normal',{})
 if en.get('status')=='COMPLETE_PROVIDER_PAGINATION_TO_EMPTY':
  old=json.loads(OLD.read_text());oldset={z['tx_hash'].lower() for z in old['rows']};newset={z['row'].get('hash','').lower() for z in en['records'] if z['in_half_open_month'] is True}
  comparison={'status':'HASH_SETS_EQUAL' if oldset==newset else 'HASH_SET_DIFFERENCE','old_count':len(oldset),'new_count':len(newset),'only_old':sorted(oldset-newset),'only_new':sorted(newset-oldset),'prior_index_sha256':sha(OLD.read_bytes())}
 coverage={'generated_utc':utc(),'scope':'provider returned public records; pagination/count/date/identity/field QC only','block_window':block_window,'datasets':qc,'E_month_normal_vs_saved265_index':comparison,'stop_reason':stop_reason,'no_rows_deleted_or_deduplicated':True,'financial_arithmetic':False,'payer_principle_only':'Only a transaction payer could bear its network cost; internal/token gas fields do not authorize charging every recipient. No fee calculation performed.','no_complete_asset_liability_or_profit_claim':True}
 jsave('coverage-qc.json',coverage)
 manifest=[{'file':x.name,'bytes':x.stat().st_size,'sha256':sha(x.read_bytes())} for x in sorted(P.iterdir()) if x.is_file() and x.name not in ['acquisition-receipt.json','readme.md']]
 receipt={'status':'COMPLETE_SIX_DATASET_PROVIDER_READ' if all(z['status']=='COMPLETE_PROVIDER_PAGINATION_TO_EMPTY' for z in results.values()) else 'PARTIAL_OR_BLOCKED_UNKNOWN','finished_utc':utc(),'request_count':request_count,'maximum_requests':MAX_REQ,'stop_reason':stop_reason,'requests':requests,'disk_bytes_at_receipt':used(),'peak_rss_bytes':rss(),'manifest':manifest,'session_identifiers_persisted':False,'new_network_endpoint':URL,'mcp_tools_used_only':['get_block_by_timestamp','get_transactions','get_internal_transactions','get_token_transfers'],'blockchain_RPC_EVM_receipt_proxy_trace_or_call':False,'source_scripts_executed':False,'financial_arithmetic_models_backtests_trades':False,'credentials_or_excluded_directory_read':False,'other_owner_files_modified':False,'rules':['PERMISSIONS-2026-10-14-v1','ROUTING-2026-10-13-v4'],'actual_model_effort':'UNKNOWN'}
 jsave('acquisition-receipt.json',receipt)
 lines=['# 2026年9月E/X公开原记录获取','',f"结果：{receipt['status']}；网络请求{request_count}/40；停止原因：{stop_reason or '无'}。",'', '固定参数先写入fixed-parameters.json。两端均使用closest=before，宽块区间inclusive；每行以1788220800≤timeStamp<1790812800标记月份，边缘行原样保留。', '', '|集|宽区间行|9月行|分页状态|','|---|---:|---:|---|']
 for k,q in qc.items():lines.append(f"|{k}|{q['wide_window_rows']}|{q['month_rows']}|{q['status']}|")
 lines+=['',f"E普通交易与旧265项索引：{comparison['status']}。",'', '六个*.rows.json保留每行原字段和原页/行位置，未按hash、金额或相同值去重。有效终止须真实空列表及成功或明确No transactions found语义；HTTP200/NOTOK不等于空页。ERC20同hash多行合法；没有logIndex时精确事件身份仍受限。内部流按已有hash+traceId字段检查，缺失/重复保留未知。', '', '原始SSE/JSON响应、请求、安全头、UTC/hash逐请求保存；MCP匿名会话标识只保留内存，未写盘。没有新注册、密钥、安装、配置改变、被拒CSV/balance/IPFS访问或区块链RPC/EVM/trace/receipt代理调用。只读公开MCP四类工具。', '', '本单元只获取原件和计数/日期/身份/字段QC，不汇总费用、估值、算账、计算利润/胜率或运行模型/回测/交易；完整资产负债与盈利未认证。实际model/effort UNKNOWN。']
 save('readme.md','\n'.join(lines)+'\n')
 print(json.dumps({'FINAL':receipt['status'],'requests':request_count,'disk_bytes':used(),'rss':rss(),'datasets':{k:q['month_rows'] for k,q in qc.items()},'comparison':comparison['status']}),flush=True)
