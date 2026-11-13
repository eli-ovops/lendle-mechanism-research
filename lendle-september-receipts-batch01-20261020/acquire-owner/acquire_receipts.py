"""Own bounded public MCP receipt acquisition and identity QC; no monetary arithmetic."""
from pathlib import Path
import json,hashlib,datetime,time,re,ssl,urllib.request,urllib.error,resource,sys,collections,threading
P=Path(__file__).resolve().parent
SCOPE=Path('/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/lendle-historical-receipt-fee-fields-20261020/root/next-readonly-source-scope.json')
SCHEMA=Path('/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/lendle-complete-ledger-originals-admission-20261020/root/mcp-tools-list.parsed.json')
OLDCLIENT=Path('/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/lendle-september-original-records-20261020/acquire-owner/acquire.py')
URL='https://mcp-keyless.etherscan.io/mcp';MAX_REQ=34;MAX_RESP=1048576;MAX_TOTAL=33554432;MAX_RSS=536870912
DEADLINE=datetime.datetime.fromisoformat('2026-10-19T17:06:32+00:00').timestamp();START='2026-10-19T16:56:32.500087+00:00'
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def rss():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)
def disk():return sum(f.stat().st_size for f in P.iterdir() if f.is_file())
def put(name,b):
 if not isinstance(b,bytes):b=b.encode()
 f=P/name;existing=f.stat().st_size if f.exists() else 0
 if disk()-existing+len(b)>MAX_TOTAL-512*1024:raise RuntimeError('TOTAL_OUTPUT_BYTES_CAP')
 f.write_bytes(b)
def jput(name,o):put(name,json.dumps(o,ensure_ascii=False,indent=2)+'\n')
scope_raw=SCOPE.read_bytes();scope=json.loads(scope_raw);normal_path=Path(scope['source']);normal_raw=normal_path.read_bytes();assert sha(normal_raw)==scope['source_sha256']
rows=json.loads(normal_raw)['records'];normal={z['row']['hash'].lower():z for z in rows};hashes=scope['next_fixed_hashes'];assert len(hashes)==32 and len(set(h.lower() for h in hashes))==32 and scope['chainid']=='5000'
assert all(re.fullmatch(r'0x[0-9a-fA-F]{64}',h) for h in hashes)
assert not set(h.lower() for h in hashes)&set(h.lower() for h in scope['reuse_existing_receipt_hashes'])
assert all(h.lower() in normal for h in hashes)
tools=json.loads(SCHEMA.read_text())['result']['tools'];tool=next(t for t in tools if t['name']=='get_transaction_receipt');assert set(tool['inputSchema']['properties'])=={'chainid','txhash'}
put('source-scope.original.json',scope_raw)
fixed={'fixed_before_network_utc':utc(),'human_scope_file':str(SCOPE),'human_scope_sha256':sha(scope_raw),'normal_rows_file':str(normal_path),'normal_rows_sha256':sha(normal_raw),'schema_file':str(SCHEMA),'schema_sha256':sha(SCHEMA.read_bytes()),'selected_tool_schema':tool,'reference_client_file_read_not_executed':str(OLDCLIENT),'reference_client_sha256':sha(OLDCLIENT.read_bytes()),'fixed_hashes':hashes,'chainid':'5000','endpoint':URL,'max_http_actions':MAX_REQ,'max_response_bytes':MAX_RESP,'max_all_new_bytes':MAX_TOTAL,'request_timeout_seconds':20,'deadline_utc':'2026-10-19T17:06:32Z','cpu_client_threads_maximum':2,'client_implementation':'single Python main thread, no thread pool','max_rss_bytes':MAX_RSS,'no_retries':True,'session_ids_memory_only':True,'only_tool':'get_transaction_receipt','payer_exceptions_not_classified':['meta/sponsored fee split','deposit/system special/free accounting','call/estimation skip-balance/no-real-payment paths (not ordinary included-transaction evidence)'],'financial_arithmetic':False,'rules':['PERMISSIONS-2026-10-14-v1','ROUTING-2026-10-13-v4','HANDOFF-2026-10-10-v2'],'actual_model_effort':'UNKNOWN'}
jput('source-scope-receipt.json',fixed)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**k):return None
opener=urllib.request.build_opener(NoRedirect,urllib.request.HTTPSHandler(context=ssl.create_default_context()))
count=0;session=None;protocol='2025-03-26';requests=[];items=[];raw_total=0;last_end=None;stop=None
SAFE={'content-type','content-length','date','server','retry-after','x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset'}
def parse(raw):
 s=raw.decode('utf-8')
 if s.lstrip().startswith(('{','[')):return json.loads(s)
 replies=[]
 for block in re.split(r'\r?\n\r?\n',s):
  dat=[l[5:].lstrip() for l in block.splitlines() if l.startswith('data:')]
  if dat:
   o=json.loads('\n'.join(dat))
   if isinstance(o,dict) and ('result' in o or 'error' in o):replies.append(o)
 if len(replies)!=1:raise ValueError('NOT_ONE_MCP_REPLY')
 return replies[0]
def request(label,payload,notify=False):
 global count,session,protocol,raw_total,last_end
 if count>=MAX_REQ:raise RuntimeError('REQUEST_CAP')
 if time.time()>DEADLINE-21:raise RuntimeError('TIME_CAP')
 if rss()>MAX_RSS or threading.active_count()>2:raise RuntimeError('PROCESS_RESOURCE_CAP')
 if last_end is not None:time.sleep(max(0,1-(time.monotonic()-last_end)))
 count+=1;pre=f'{count:02d}-{label}';put(pre+'.request.json',json.dumps(payload,separators=(',',':'))+'\n')
 headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
 if session:headers.update({'Mcp-Session-Id':session,'MCP-Protocol-Version':protocol})
 start=utc();status=None;safe={};raw=b'';error=None;new_session=None;truncated=False
 try:
  try:r=opener.open(urllib.request.Request(URL,data=json.dumps(payload,separators=(',',':')).encode(),headers=headers,method='POST'),timeout=20)
  except urllib.error.HTTPError as e:r=e
  status=r.code;safe={k.lower():v for k,v in r.headers.items() if k.lower() in SAFE};new_session=r.headers.get('Mcp-Session-Id');raw=r.read(MAX_RESP+1);r.close()
  if len(raw)>MAX_RESP:raw=raw[:MAX_RESP];truncated=True
 except Exception as e:error=type(e).__name__+': '+str(e)
 finally:last_end=time.monotonic()
 raw_total+=len(raw);stored=raw;redacted=False
 for token in [session,new_session]:
  if token and token.encode() in stored:stored=stored.replace(token.encode(),b'[SESSION_ID_REDACTED]');redacted=True
 if re.search(br'(?m)^id:',stored):stored=re.sub(br'(?m)^id:[^\r\n]*(?:\r?\n)?',b'',stored);redacted=True
 put(pre+'.response.sse',stored);jput(pre+'.headers-safe.json',safe)
 meta={'http_action':count,'label':label,'endpoint':URL,'method':'POST anonymous MCP public provider receipt retrieval; no direct blockchain node RPC','started_utc':start,'finished_utc':utc(),'http_status':status,'bytes':len(stored),'source_bytes_acquired_sha256':sha(raw),'source_bytes_saved_sha256':sha(stored),'session_or_sse_identifier_redacted_from_body':redacted,'session_identifier_header_saved':False,'truncated':truncated,'error':error,'files':[pre+'.request.json',pre+'.response.sse',pre+'.headers-safe.json']};requests.append(meta);jput(pre+'.acquisition.json',meta)
 print(json.dumps({'action':count,'label':label,'http':status,'bytes':len(stored),'error':error}),flush=True)
 if error:raise RuntimeError('TRANSPORT_FAILURE_STOP')
 if truncated or raw_total>MAX_TOTAL:raise RuntimeError('SOURCE_BYTE_CAP_STOP')
 if status in (401,402,403,429):raise RuntimeError('SOURCE_REFUSAL_AUTH_QUOTA_STOP_'+str(status))
 if status not in (200,202,204):raise RuntimeError('HTTP_FAILURE_STOP_'+str(status))
 if new_session:session=new_session
 if notify:return None,pre
 o=parse(raw);jput(pre+'.parsed.json',o)
 if not isinstance(o,dict) or o.get('id')!=payload.get('id') or 'error' in o:raise RuntimeError('MCP_PROTOCOL_ERROR_STOP')
 return o,pre
def integer(x):
 if isinstance(x,int) and not isinstance(x,bool):return x
 if not isinstance(x,str):return None
 if re.fullmatch(r'0x[0-9a-fA-F]+',x):return int(x,16)
 if re.fullmatch(r'[0-9]+',x):return int(x,10)
 return None
def lower(x):return x.lower() if isinstance(x,str) else x
def identity(txhash,receipt):
 n=normal[txhash.lower()]['row'];checks={};checks['hash']=lower(receipt.get('transactionHash'))==txhash.lower();checks['block_hash']=lower(receipt.get('blockHash'))==lower(n.get('blockHash'));checks['block_number']=integer(receipt.get('blockNumber')) is not None and integer(receipt.get('blockNumber'))==integer(n.get('blockNumber'));checks['transaction_index']=integer(receipt.get('transactionIndex')) is not None and integer(receipt.get('transactionIndex'))==integer(n.get('transactionIndex'));checks['from']=lower(receipt.get('from'))==lower(n.get('from'))
 creation=n.get('to') in ('',None)
 checks['to']=receipt.get('to') in ('',None,'0x') if creation else lower(receipt.get('to'))==lower(n.get('to'))
 checks['created_contract']=lower(receipt.get('contractAddress'))==lower(n.get('contractAddress')) if creation and n.get('contractAddress') else receipt.get('contractAddress') in ('',None,'0x0000000000000000000000000000000000000000')
 checks['execution_status']=integer(receipt.get('status')) in (0,1) and integer(receipt.get('status'))==integer(n.get('txreceipt_status'))
 checks['gas_used_count_equivalence']=integer(receipt.get('gasUsed')) is not None and integer(receipt.get('gasUsed'))==integer(n.get('gasUsed'))
 chain=receipt.get('chainId',receipt.get('chainid'));checks['response_chain_if_present']=integer(chain)==5000 if chain is not None else None
 logs=receipt.get('logs');logchecks=[];keys=[]
 if not isinstance(logs,list):checks['logs_list']=False
 else:
  checks['logs_list']=True
  for i,l in enumerate(logs):
   if not isinstance(l,dict):logchecks.append({'original_log_position_0based':i,'all_identity_checks':False});continue
   idx=integer(l.get('logIndex'));c={'transaction_hash':lower(l.get('transactionHash'))==txhash.lower(),'block_hash':lower(l.get('blockHash'))==lower(receipt.get('blockHash')),'block_number':integer(l.get('blockNumber'))==integer(receipt.get('blockNumber')) and integer(l.get('blockNumber')) is not None,'transaction_index':integer(l.get('transactionIndex'))==integer(receipt.get('transactionIndex')) and integer(l.get('transactionIndex')) is not None,'log_index_present_integer':idx is not None,'emitter_address_format':isinstance(l.get('address'),str) and re.fullmatch(r'0x[0-9a-fA-F]{40}',l['address']) is not None,'removed_false_if_present':l.get('removed') in (None,False)}
   if idx is not None:keys.append((txhash.lower(),idx))
   logchecks.append({'original_log_position_0based':i,'logIndex_verbatim':l.get('logIndex'),'checks':c,'all_identity_checks':all(c.values())})
 dup=[{'transactionHash':h,'logIndex_decimal_identity_only':i,'occurrences':v} for (h,i),v in collections.Counter(keys).items() if v>1]
 checks['all_log_identities']=all(l['all_identity_checks'] for l in logchecks);checks['unique_hash_logIndex']=not dup
 fields=['gasUsed','effectiveGasPrice','l1Fee','l1GasUsed','l1GasPrice','operatorFeeScalar','operatorFeeConstant','tokenRatio','status','from','to','contractAddress','blockHash','blockNumber','transactionIndex']
 presence={f:{'present':f in receipt,'is_null':receipt.get(f) is None,'json_type':type(receipt.get(f)).__name__} for f in fields}
 return {'requested_chainid':'5000','response_chain_identity':'explicit response field matched5000' if chain is not None else 'UNKNOWN_INDEPENDENT_CHAIN_PROOF; chain5000 explicit in request/provider context','normal_source_page':normal[txhash.lower()]['source_page'],'normal_source_row_1based':normal[txhash.lower()]['source_row_1based'],'checks':checks,'all_available_identity_checks':all(v is True for v in checks.values() if v is not None),'field_presence':presence,'receipt_status_verbatim':receipt.get('status'),'log_count':len(logs) if isinstance(logs,list) else None,'log_identity_checks':logchecks,'duplicate_hash_logIndex_preserved':dup,'log_amounts_decoded':False,'payer_classification':'UNKNOWN; no assumption from is universal full payer'}
try:
 init,_=request('initialize',{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':protocol,'capabilities':{},'clientInfo':{'name':'public-original-availability-research','version':'1.0'}}});protocol=init['result']['protocolVersion']
 request('initialized',{'jsonrpc':'2.0','method':'notifications/initialized'},True)
 for i,h in enumerate(hashes,1):
  o,pre=request('receipt-'+str(i).zfill(2),{'jsonrpc':'2.0','id':i+1,'method':'tools/call','params':{'name':'get_transaction_receipt','arguments':{'txhash':h,'chainid':'5000'}}})
  outer=o.get('result',{});data=outer.get('structuredContent',{}).get('data');texts=[]
  for c in outer.get('content',[]):
   if c.get('type')=='text':
    try:texts.append(json.loads(c.get('text','')))
    except (ValueError,TypeError):pass
  if data is None and len(texts)==1:data=texts[0]
  jput(pre+'.tool-data.json',{'data':data,'mcp_isError':outer.get('isError',False),'structured_text_agreement':all(t==data for t in texts) if texts else None})
  business={'ok':data.get('ok') if isinstance(data,dict) else None,'status_field':data.get('status') if isinstance(data,dict) else None,'message_field':data.get('message') if isinstance(data,dict) else None,'mcp_isError':outer.get('isError',False)}
  item={'fixed_position_1based':i,'requested_hash':h,'response_prefix':pre,'business':business};items.append(item)
  if not isinstance(data,dict) or data.get('ok') is not True or outer.get('isError') or (texts and not all(t==data for t in texts)):item['status']='BUSINESS_ERROR_OR_STRUCTURE_UNKNOWN';raise RuntimeError('BUSINESS_ERROR_STOP')
  receipt=data.get('result')
  if not isinstance(receipt,dict):item['status']='NULL_OR_NONOBJECT_RECEIPT_UNKNOWN';raise RuntimeError('NULL_OR_NONOBJECT_RECEIPT_STOP')
  jput(pre+'.receipt-original.json',receipt);q=identity(h,receipt);jput(pre+'.identity-qc.json',q);item['identity_qc']=q;item['status']='PASS_PROVIDER_IDENTITY_QC' if q['all_available_identity_checks'] else 'IDENTITY_MISMATCH_OR_MISSING_UNKNOWN'
  if not q['all_available_identity_checks']:raise RuntimeError('IDENTITY_QC_STOP')
  print(json.dumps({'fixed_position':i,'status':item['status'],'logs':q['log_count']}),flush=True)
except Exception as e:
 stop=type(e).__name__+': '+str(e);print(json.dumps({'STOP':stop}),flush=True)
finally:
 session=None
 acquired={i['requested_hash'].lower() for i in items if i.get('status')=='PASS_PROVIDER_IDENTITY_QC'};missing=[h for h in hashes if h.lower() not in acquired]
 coverage={'status':'COMPLETE_FIXED32_PROVIDER_RECEIPTS_IDENTITY_ONLY' if len(acquired)==32 else 'PARTIAL_UNKNOWN_STOPPED','fixed_requested_count':32,'acquired_identity_pass_count':len(acquired),'missing_or_not_accepted_hashes':missing,'stop_reason':stop,'items':items,'execution_status_verbatim_counts':dict(collections.Counter(i['identity_qc']['receipt_status_verbatim'] for i in items if i.get('identity_qc'))),'same_provider_normal_consistency_only':True,'independent_chain_or_historical_software_version_proof':False,'logs_only_identity_not_amount_decode':True,'no_financial_arithmetic':True,'payer_exceptions_not_classified':fixed['payer_exceptions_not_classified']};jput('coverage-qc.json',coverage)
 manifest=[{'file':f.name,'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in sorted(P.iterdir()) if f.is_file() and f.name not in ['acquisition-receipt.json','README.md']]
 result={'status':coverage['status'],'started_utc':START,'finished_utc':utc(),'http_actions':count,'max_http_actions':MAX_REQ,'provider_receipt_proxy_style_reads':sum(m['label'].startswith('receipt-') for m in requests),'source_response_total_bytes':raw_total,'new_disk_bytes_before_receipt':disk(),'peak_rss_bytes':rss(),'python_active_threads':threading.active_count(),'timeout_seconds':20,'max_response_bytes':MAX_RESP,'requests':requests,'stop_reason':stop,'manifest':manifest,'session_ids_persisted':False,'direct_blockchain_node_RPC':False,'source_code_EVM_call_estimate_trace_execution':False,'models_backtests_financial_calculation_trades_payments':False,'other_owner_credentials_excluded_directory_access':False,'actual_model_effort':'UNKNOWN'}
 jput('acquisition-receipt.json',result)
 lines=['# 固定32笔九月历史receipt原件获取','',f"状态：{coverage['status']}；取得并通过身份QC {len(acquired)}/32；HTTP {count}/34；停止原因：{stop or '无'}。",'','只使用事前固定next_fixed_hashes，显式chainid5000；未重取3份既有receipt或265索引。初始化与通知后单线程顺序读取，未重试/换身份。原SSE、请求、安全头、解析包、receipt原字段、UTC/HTTP/hash与逐笔QC保留。','',f"未取得/未接受：{len(missing)}；具体hash见coverage-qc.json。业务ok与receipt执行status分开记录，status0不是获取失败。",'','QC仅核请求hash/链上下文、父块、from/to/creation地址、tx index/status/gas计量与normal原行等价；log仅核hash/块/索引/地址格式及重复身份，不解码金额。响应缺独立chainId时不冒称独立链认证。缺字段/null不补零。','', '付款归属保留三类例外路径：meta/sponsor分担；deposit/system特殊或免费记账；call/estimate跳过真实付款路径（不能当已发生链上付款证据）。未将样本分类为普通全额from付款，未合计费用、金额、估值、账户或利润。','', '这只是同提供者记录与normal行的一致性，不是9月历史软件部署、全月完整净账或策略可复制性认证。无直接节点RPC、eth_call/estimate/trace/EVM、来源脚本、模型/回测/交易；不读凭证/排除目录。会话标识仅内存，实际model/effort UNKNOWN。']
 put('README.md','\n'.join(lines)+'\n');print(json.dumps({'FINAL':coverage['status'],'accepted':len(acquired),'http':count,'source_bytes':raw_total,'disk_bytes':disk(),'rss':rss()}),flush=True)
