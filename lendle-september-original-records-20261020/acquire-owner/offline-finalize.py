"""Offline original-response recovery and identity/field QC only. Zero network."""
from pathlib import Path
import json,hashlib,datetime,collections,re
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(n):return json.loads((P/n).read_text())
def write(n,o):(P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
# Preserve second-session derived E set, use already-complete first responses canonically.
second=read('E_normal.rows.json');write('E_normal-second-session.rows.json',second)
records=[];pages=[]
for page,prefix in [(1,'05-E_normal-page1'),(2,'06-E_normal-page2'),(3,'07-E_normal-page3')]:
 d=read(prefix+'.tool-data.json')['tool_data'];rows=d['result']
 empty=bool(isinstance(rows,list) and not rows and str(d['status'])=='0' and d['message']=='No transactions found')
 assert isinstance(rows,list) and ((d['ok'] is True and str(d['status'])=='1') or empty)
 pages.append({'page':page,'response_prefix':prefix,'business_ok':d['ok'],'business_status':str(d['status']),'business_message':d['message'],'row_count':len(rows),'valid_empty_terminal':empty})
 for i,row in enumerate(rows,1):records.append({'source_page':page,'source_row_1based':i,'source_response':prefix+'.response.sse','in_half_open_month':1788220800<=int(row['timeStamp'])<1790812800,'row':row})
assert pages[-1]['valid_empty_terminal'] is True
canonical={'address':second['address'],'tool':second['tool'],'status':'COMPLETE_PROVIDER_PAGINATION_TO_EMPTY','pages':pages,'records':records}
assert {r['row']['hash'] for r in records}=={r['row']['hash'] for r in second['records']}
write('E_normal.rows.json',canonical)
qc=read('coverage-qc.json');qc['datasets']['E_normal']['pages']=pages
for k,q in qc['datasets'].items():
 rows=read(k+'.rows.json')['records'];monthly=[r['row'] for r in rows if r['in_half_open_month'] is True]
 q['required_field_presence']={f:{'missing':sum(f not in r for r in monthly),'empty_string':sum(r.get(f) == '' for r in monthly)} for f in (['hash','blockNumber','timeStamp','from','to','gasPrice','gasUsed','isError','txreceipt_status'] if k.endswith('normal') else ['hash','blockNumber','timeStamp','from','to','traceId'] if k.endswith('internal') else ['hash','blockNumber','timeStamp','from','to','contractAddress','tokenDecimal','value','logIndex'])}
 q['numeric_string_format_errors']={f:sum(f in r and re.fullmatch(r'[0-9]+',str(r[f])) is None for r in monthly) for f in (['blockNumber','timeStamp','nonce','gasPrice','gasUsed','L1FeesPaid'] if k.endswith('normal') else ['blockNumber','timeStamp'] if k.endswith('internal') else ['blockNumber','timeStamp','tokenDecimal','value'])}
 if k.endswith('internal'):
  q['trace_identity_validation_status']='NOT_TESTABLE_PROVIDER_EMPTY_RESULT' if not monthly else 'CHECKED_AVAILABLE_FIELDS_ONLY'
  q['internal_call_tree_completeness']='UNKNOWN; provider empty list is not proof of no zero-value/internal/reverted calls'
 if k.endswith('erc20') and q['logIndex_missing_count']:
  q['event_identity_validation_status']='UNKNOWN_EXACT_LOG_IDENTITY_NO_LOGINDEX; no dedup performed'
qc['canonical_E_normal_source']='first anonymous session requests05-07 recovered locally; second-session requests12-14 preserved separately, unnecessary refetch counted'
qc['recovery_disclosure']='Initial local TypeError: re.Match not JSON serializable, not HTTP/quota denial. Root later clarified MCP session is not a chain consistency snapshot. No additional refetch after that clarification; remaining fixed datasets continued.'
qc['generated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write('coverage-qc.json',qc)
# Verify raw response/data copies independently of request client state.
r=read('acquisition-receipt.json');raw_checks=[]
for m in r['requests']:
 response=P/m['source_files'][1];headers=read(m['source_files'][2]);raw=response.read_bytes()
 raw_checks.append({'request':m['request_number'],'stored_hash_matches':sha(raw)==m['response_stored_sha256'],'within_4MiB':len(raw)<=4*1024*1024,'safe_header_names_only':set(headers)<= {'content-type','content-length','date','server','retry-after','x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset'}})
assert all(all(v for k,v in c.items() if k!='request') for c in raw_checks)
starts=[datetime.datetime.fromisoformat(m['started_utc']).timestamp() for m in r['requests']]
spacing=[b-a for a,b in zip(starts,starts[1:])]
assert all(d>=1 for d in spacing)
for key,q in qc['datasets'].items():
 assert q['pages'][-1]['valid_empty_terminal'] is True
 assert q['unknown_timestamp_rows']==[] and q['all_timestamps_nondecreasing'] and q['within_block_window']
 if key.endswith('normal'):assert q['normal_hash_unique']
write('offline-verification.json',{'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'response_checks':raw_checks,'minimum_request_start_spacing_seconds':min(spacing),'spacing_measured_as':'request start-to-start; client additionally slept until at least1s after previous response read completion','canonical_E_rows_recovered_from_original_successful_responses':True,'same_E_hashes_in_both_sessions':True,'all_six_terminal_pages_valid_provider_empty':True,'all_normal_hashes_unique':True,'original_rows_and_page_locations_preserved':True,'no_financial_arithmetic_or_network':True})
readme=f'''# 2026年9月E/X公开原记录获取

**完成固定六集的提供者分页原件获取及字段QC；不构成完整账户账或盈利验收。** 请求24/40，所有响应HTTP200（两次initialized通知202），没有来源拒绝、鉴权或限流。两端closest=before返回块100045244、101341244；查询均inclusive，再按每行1788220800≤timeStamp<1790812800筛9月。未发现本批区间外或时间缺失行；原行结构/页/行位置全部保留。

| 集 | 实际非空页 | 9月行 | 有效空末页 |
|---|---|---:|---:|
| E normal | 200、65 | 265 | page3 |
| E internal | 无；provider empty | 0 | page1 |
| E ERC20 | 119 | 119 | page2 |
| X normal | 146 | 146 | page2 |
| X internal | 无；provider empty | 0 | page1 |
| X ERC20 | 200、200、144 | 544 | page4 |

每个末页均为实际result[]、status0、No transactions found，原SSE/业务原文保留；没有把HTTP200、NOTOK、解析失败当空页。短页均补请求空末页。E normal与旧封存265条索引hash集完全一致；E/X normal各自hash唯一。宽区间边缘记录若存在会原样保留，本批边缘行计0。

**身份与字段限制：** 两个internal工具都只返回提供者空列表，traceId身份检查因无行而不可测试；这不能证明浏览器已提示的零值内部调用/内部revert不存在或完整调用树已覆盖。ERC20的119/544行全部缺logIndex；X包含68个父hash，各父hash多行，均保留，未按hash/相同值或看似重复内容去重。确切事件身份仍UNKNOWN，不能仅凭本服务行数声称完整链上Transfer日志。normal保留gasPrice、gasUsed、L1相关字段等原始字符串；没有乘积、费用合计或估值。仅保留付款者归费用原则，未对收款人分摊/扣费。

**本地中断与恢复：** 首匿名会话请求1–7已取得两块、E normal200+65及真实空末页。自有客户端把regex Match对象当bool写JSON，触发TypeError；不是限流或来源拒绝，会话标识未写盘。原件全部保留，修复为bool。第二会话已在Root收紧恢复前发出请求8–14（初始化、两块与E normal不必要重取），如实计入总预算，原始文件不覆写。Root澄清MCP会话不提供历史链一致性快照后，不再重取已完E/块，连续完成其余五集至请求24。最终E_normal.rows.json从首会话5–7本地恢复；第二会话E副本保存在E_normal-second-session.rows.json，其他五集来自请求15–24。必要一致项是同一来源、固定块区间、时间规则及分页，不是会话本身。

**产物：** 六个E/X_normal/internal/erc20.rows.json保存row原字段与source_page/source_row_1based/source_response、月份布尔标记；没有删行。逐请求*.request.json、*.response.sse、*.headers-safe.json、*.acquisition.json以及tool-data副本保留UTC、HTTP、哈希。安全头不含MCP会话标识/Set-Cookie；会话ID仅临时内存，进程退出即丢弃。固定参数先于请求写入fixed-parameters.json；session2记录原总预算未变。coverage-qc.json与offline-verification.json给出分页/身份/日期/字段QC与旧索引比较。

获取止于{r['finished_utc']}；磁盘与RSS见acquisition-receipt.json，均低于64MiB/512MiB。没有注册、取key、安装、配置修改、被拒CSV/balance/IPFS访问，未调用区块链RPC、eth_call、trace或receipt代理；未执行来源JS/EVM/模型/回测/策略/交易或财务核算。只用官方keyless MCP四类公开记录/块时间工具。未触及排除目录、凭证或其他Owner文件。实际model/effort UNKNOWN。
'''
(P/'readme.md').write_text(readme)
r['recovery_disclosure']=qc['recovery_disclosure'];r['canonical_E_normal_source']=qc['canonical_E_normal_source'];r['canonical_datasets_span_two_short_anonymous_sessions']=True;r['same_session_not_claimed_as_snapshot_consistency']=True
r['offline_finalized_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();r['manifest']=[{'file':f.name,'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in sorted(P.iterdir()) if f.is_file() and f.name!='acquisition-receipt.json'];r['disk_bytes_at_receipt']=sum(f.stat().st_size for f in P.iterdir() if f.is_file());write('acquisition-receipt.json',r)
print(json.dumps({'status':r['status'],'requests':r['request_count'],'readme_sha256':sha((P/'readme.md').read_bytes()),'qc_sha256':sha((P/'coverage-qc.json').read_bytes()),'receipt_sha256':sha((P/'acquisition-receipt.json').read_bytes()),'disk_bytes':sum(f.stat().st_size for f in P.iterdir() if f.is_file()),'minimum_start_spacing_seconds':min(spacing)},ensure_ascii=False))
