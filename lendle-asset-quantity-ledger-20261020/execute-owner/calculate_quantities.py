"""Own one-shot historical raw ERC20 quantity arithmetic. Explicit Root GO required."""
from pathlib import Path
import sys,json,hashlib,re,datetime,time,signal,os,resource,threading,collections
sys.dont_write_bytecode=True
import source_parser as sp
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
MAX_DISK=8388608;MAX_RSS=536870912

def read(n):return json.loads((P/n).read_bytes())
def write(n,o,compact=False):
 b=(json.dumps(o,ensure_ascii=False,**({'separators':(',',':')} if compact else {'indent':2}))+'\n').encode();f=P/n;old=f.stat().st_size if f.exists() else 0
 assert sum(x.stat().st_size for x in P.iterdir() if x.is_file())-old+len(b)<=MAX_DISK;f.write_bytes(b)
def rss():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)
def signed(v):return ('+' if v>0 else '')+str(v)
def direction(e,subject):
 if e['from']==subject==e['to']:return 'self'
 if e['to']==subject:return 'in'
 if e['from']==subject:return 'out'
 raise AssertionError('EVENT_NOT_TOUCHING_SUBJECT')
def add(groups,e,d,v):
 t=e['token_contract'];g=groups.setdefault(t,{'in':0,'out':0,'self':0,'counts':{'in':0,'out':0,'self':0}});g[d]+=v;g['counts'][d]+=1

def freeze_groups(groups):
 return [{'token_contract':t,'raw_in_total':str(g['in']),'raw_out_total_magnitude':str(g['out']),'raw_self_total_counted_once':str(g['self']),'signed_raw_net_in_minus_out_self_zero':signed(g['in']-g['out']),'event_counts_by_direction':g['counts'],'precision':'original smallest units only; no decimals scaling'} for t,g in sorted(groups.items())]
def project(subject,ids,events,quantities):
 groups={};rows=[];seen=set()
 for key in ids:
  assert key not in seen;seen.add(key);e=events[key];v=quantities[key];d=direction(e,subject);sv=v if d=='in' else -v if d=='out' else 0;add(groups,e,d,v)
  rows.append({'event_id':key,'token_contract':e['token_contract'],'direction':d,'unsigned_raw_decimal':str(v),'signed_raw_decimal':signed(sv),'source_raw_hex_in_event_pool':True,'self_transfer_one_row_no_income_expense_double_entry':d=='self'})
 return {'subject':subject,'event_count':len(rows),'events':rows,'by_token_contract_and_direction':freeze_groups(groups),'all_tokens_preserved_even_zero_net':True},groups

def main():
 assert len(sys.argv)==3 and sys.argv[1]=='--go','EXPLICIT_ROOT_GO_ARGUMENT_REQUIRED'
 pr=(P/'run-plan.json').read_bytes();plan=json.loads(pr);ph=sha(pr);assert sys.argv[2]==ph and sha(Path(__file__).read_bytes())==plan['formal_script_sha256']
 go=read('root-go.json');assert go['explicit_ROOT_GO'] is True and go['run_plan_sha256']==ph
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-10-19T18:23:18+00:00')
 fd=os.open(P/'formal-attempt.lock',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.write(fd,b'one formal quantity attempt only\n');os.close(fd)
 start=time.monotonic();started=utc();status='STOPPED';error=None;summary=None
 def guard():assert time.monotonic()-start<30 and rss()<=MAX_RSS and threading.active_count()==1
 def alarm(a,b):raise TimeoutError('FORMAL_30_SECOND_CAP')
 signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,30)
 try:
  for n,h in plan['frozen_owner_inputs'].items():assert sha((P/n).read_bytes())==h,('FROZEN_INPUT_CHANGED',n)
  assert sha((P/'source_parser.py').read_bytes())==plan['source_parser_sha256']
  for f in read('source-input-manifest.json')['files']:
   assert sha(Path(f['path']).read_bytes())==f['sha256'],('SOURCE_CHANGED',f['path']);guard()
  pf=read('preflight.json');assert pf['status']=='READY_WAIT_ROOT_GO_NO_QUANTITY_AGGREGATION' and pf['counts_only']['receipt_count']==265 and pf['counts_only']['unsupported_or_malformed_candidates']==0
  assert read('unsupported-or-malformed-candidates.json')['records']==[]
  pool=read('event-pool.raw.json')['events'];events={e['event_id']:e for e in pool};assert len(events)==len(pool)==pf['counts_only']['standard_ERC20_Transfer_events']
  cases=read('fixed119-liquidator-event-references.json')['cases'];assert len(cases)==119 and len({c['hash'] for c in cases})==119
  quantities={}
  for e in pool:
   raw=e['raw_value_hex'];assert re.fullmatch(r'0x[0-9a-fA-F]{64}',raw);v=int(raw,16);assert (v==0)==e['zero_literal'];quantities[e['event_id']]=v;guard()
  Eids=[e['event_id'] for e in pool if sp.E in (e['from'],e['to'])];Fids=[e['event_id'] for e in pool if sp.F21 in (e['from'],e['to'])]
  E,Egroups=project(sp.E,Eids,events,quantities);F,Fgroups=project(sp.F21,Fids,events,quantities)
  E.update({'scope':'All standard Transfer events touching E across fixed265 receipts; not full economic income','F21_not_combined':True});F.update({'scope':'F21 separate subject across fixed265 receipts; never added to or deducted from E totals'})
  write('E-event-ledger-and-token-totals.json',E);write('F21-event-ledger-and-token-totals.json',F)
  expected={k for c in cases for k in c['expected_positive_E_event_ids']};actual={e['event_id'] for e in pool if e['to']==sp.E and e['from']!=sp.E and quantities[e['event_id']]>0}
  assert len(expected)==119 and expected==actual
  reconciliation={'status':'ALL119_PRIOR_POSITIVE_E_EVENT_IDENTITIES_EXACT_MATCH','expected_count':119,'actual_positive_E_event_count':len(actual),'missing_event_ids':sorted(expected-actual),'additional_positive_E_event_ids':sorted(actual-expected),'event_id_format':'chain5000:transactionHash:canonicalLogIndex','original_quantity_hex_matched_in_preflight':True,'not_hash_only_dedup':True}
  write('prior119-event-identity-reconciliation.json',reconciliation)
  Lrows=[];Lglobal={};Lglobal_seen=collections.defaultdict(set);zero_books=0;empty_books=0;nonzero_rows=0
  for case in cases:
   for L in case['actual_liquidators']:
    refs=case['per_liquidator_standard_event_ids'][L];assert set(refs)=={e['event_id'] for e in pool if e['hash']==case['hash'] and L in (e['from'],e['to'])}
    book,groups=project(L,refs,events,quantities);book.update({'hash':case['hash'],'liquidation_event_refs':[q['event_id'] for q in case['liquidations'] if q['liquidator']==L],'all_same_receipt_standard_Transfer_tokens_including_aTokens':True,'no_zero_or_nonzero_net_filtering':True,'subject_overlaps_E':L==sp.E,'subject_overlaps_F21':L==sp.F21})
    empty_books+=not groups;zero_books+=bool(groups) and all(g['in']==g['out'] for g in groups.values());nonzero_rows+=sum(g['in']!=g['out'] for g in groups.values());Lrows.append(book)
    target=Lglobal.setdefault(L,{})
    for key in refs:
     assert key not in Lglobal_seen[L];Lglobal_seen[L].add(key);e=events[key];add(target,e,direction(e,L),quantities[key])
    guard()
  write('fixed119-per-receipt-liquidator-books.json',{'scope':'Only fixed119 receipts; each actual liquidator separate; all standard Transfer legs, aTokens included','books':Lrows,'same_event_pool_referenced_no_protocol_event_double_count':True,'BalanceTransfer_Burn_Withdraw_Swap_not_extra_quantity_legs':True,'no_interpretation_as_balances_ownership_or_zero_external_costs':True},True)
  write('fixed119-liquidator-address-token-totals.json',{'scope':'Same119 receipt projections only, not full address history; distinct L subjects never merged','subjects':[{'address':L,'by_token_contract_and_direction':freeze_groups(groups),'unique_event_count':len(Lglobal_seen[L])} for L,groups in sorted(Lglobal.items())],'never_add_to_or_deduct_again_from_E_final_receipts':True})
  summary={'status':'COMPLETE_FIXED_ONCE_STANDARD_ERC20_RAW_QUANTITY_LEDGER','source_scope_receipts':265,'standard_Transfer_events_in_shared_pool':len(pool),'E':{'address':sp.E,'event_count':E['event_count'],'token_contract_count':len(Egroups),'direction_event_counts':{d:sum(q['direction']==d for q in E['events']) for d in ['in','out','self']}},'F21':{'address':sp.F21,'event_count':F['event_count'],'token_contract_count':len(Fgroups),'direction_event_counts':{d:sum(q['direction']==d for q in F['events']) for d in ['in','out','self']},'separate_from_E':True},'fixed119_positive_E_identity_reconciliation':'PASS_EXACT_EVENTS_AND_RAW_HEX','liquidator_same_receipt_books':{'fixed_receipt_count':119,'separate_receipt_address_books':len(Lrows),'distinct_actual_L_addresses':len(Lglobal),'all_token_net_zero_books':zero_books,'empty_books_not_claimed_zero_balance':empty_books,'nonzero_token_net_rows_preserved':nonzero_rows,'all_tokens_including_aTokens_retained':True},'unit':'raw integer smallest units per issuing contract; no sum across contracts and no precision scaling','provider_metadata':'Separate reference labels only, no independent issuer or decimals authentication','other_protocol_events':'Context only; not additional quantity legs','network_bills':'Not read or recalculated in this unit; separate sealed network gross fee result, never subtracted from token quantities','boundaries':['Standard Transfer log net inflow is not complete economic net income.','No opening/end balance, rebase/nonstandard transfer/native/internal/ownership/capital or outside-fixed-receipt proof.','L same-receipt flow balance is not E profit or absence of external economic costs.','F21 and distinct L subjects never combined with E.','No price multiplication, net profit, ROI or capital curve.']}
  write('quantity-ledger-summary.json',summary);guard();status='COMPLETE_FIXED_ONCE'
 except BaseException as e:error=type(e).__name__+': '+str(e)
 finally:
  signal.setitimer(signal.ITIMER_REAL,0)
  r={'status':status,'started_utc':started,'finished_utc':utc(),'elapsed_seconds':time.monotonic()-start,'formal_attempt_count':1,'error':error,'run_plan_sha256':ph,'script_sha256':sha(Path(__file__).read_bytes()),'root_go_sha256':sha((P/'root-go.json').read_bytes()),'peak_rss_bytes':rss(),'single_thread':threading.active_count()==1,'formal_summary_written':summary is not None,'fee_recalculation_price_scaling_net_profit_models_EVM_network_or_trades':False,'actual_model_effort':'UNKNOWN'}
  r['manifest']=[{'file':f.name,'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in sorted(P.iterdir()) if f.is_file() and f.name!='formal-execution-receipt.json'];write('formal-execution-receipt.json',r)
  print(json.dumps({'status':status,'error':error,'elapsed_seconds':r['elapsed_seconds'],'peak_rss_bytes':r['peak_rss_bytes'],'summary':summary},ensure_ascii=False))
if __name__=='__main__':main()
