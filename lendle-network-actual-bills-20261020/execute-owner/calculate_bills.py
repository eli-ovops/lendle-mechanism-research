"""Own one-shot offline historical network-bill arithmetic, gated by explicit Root GO."""
from pathlib import Path
import json,hashlib,re,datetime,time,signal,resource,sys,os,collections,threading
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
MAX_DISK=8388608;MAX_RSS=536870912

def read(name):return json.loads((P/name).read_bytes())
def write(name,o):
 b=(json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode();f=P/name;old=f.stat().st_size if f.exists() else 0
 assert sum(x.stat().st_size for x in P.iterdir() if x.is_file())-old+len(b)<=MAX_DISK
 f.write_bytes(b)
def quantity(v):
 assert isinstance(v,str) and re.fullmatch(r'(?:0x[0-9a-fA-F]+|[0-9]+)',v)
 i=int(v,16 if v.startswith('0x') else 10);assert i.bit_length()<=256;return i
def mnt(v):
 q,r=divmod(v,10**18);return str(q)+'.'+str(r).zfill(18)
def published_units(v):
 assert re.fullmatch(r'[0-9]+\.[0-9]{1,18}',v)
 a,b=v.split('.');return int(a+b.ljust(18,'0'))
def calculate(r):
 g=quantity(r['gasUsed']);p=quantity(r['effectiveGasPrice']);l=quantity(r['l1Fee']);s=quantity(r['operatorFeeScalar']);k=quantity(r['operatorFeeConstant'])
 execution=g*p;operator=g*s*100+k;total=execution+l+operator
 return {'execution':execution,'l1':l,'operator':operator,'total':total}
def units(o):return {k:str(v) for k,v in o.items()}
def peak_rss():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)
def guard(start):
 assert time.monotonic()-start<30 and peak_rss()<=MAX_RSS and threading.active_count()==1

def main():
 assert len(sys.argv)==3 and sys.argv[1]=='--go','ROOT_GO_ARGUMENT_REQUIRED'
 planraw=(P/'run-plan.json').read_bytes();plan=json.loads(planraw);planhash=sha(planraw)
 assert sys.argv[2]==planhash and sha(Path(__file__).read_bytes())==plan['formal_script_sha256']
 go=read('root-go.json');assert go['explicit_ROOT_GO'] is True and go['run_plan_sha256']==planhash
 fd=os.open(P/'formal-attempt.lock',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.write(fd,b'one formal attempt only\n');os.close(fd)
 start=time.monotonic();started=utc();status='STOPPED';error=None;three=[];bills=[];cache={};outgoing=[];excluded=[];summary=None
 def alarm(signum,frame):raise TimeoutError('FORMAL_30_SECOND_WALL_CAP')
 signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,30)
 try:
  for name,h in plan['frozen_owner_inputs'].items():assert sha((P/name).read_bytes())==h,('FROZEN_OWNER_INPUT_CHANGED',name)
  manifest=read('source-input-manifest.json')
  for f in manifest['files']:
   assert sha(Path(f['path']).read_bytes())==f['sha256'],('SOURCE_CHANGED',f['path']);guard(start)
  pre=read('preflight.json');assert pre['unique_registry_and_normal_hash_count']==265 and pre['role_counts']=={'E_outgoing':262,'E_incoming':3}
  registry=json.loads(Path(plan['registry_file']).read_bytes());normal=json.loads(Path(registry['full_normal_source']).read_bytes());nm={z['row']['hash'].lower():z['row'] for z in normal['records']};pm={z['hash']:z for z in pre['records']};receipts={}
  for e in registry['entries']:
   h=e['hash'].lower();parsed=json.loads(Path(e['parsed']).read_bytes());d=parsed['result']['structuredContent']['data'];assert d['ok'] is True and not parsed['result'].get('isError');r=d['result'];assert r['transactionHash'].lower()==h
   typ=quantity(r['type']);assert typ in (0,2) and not any(k in r and r[k] is not None for k in ['depositNonce','depositReceiptVersion']);assert 'blobGasPrice' not in r and r.get('daFootprintGasScalar') is not None;quantity(r['daFootprintGasScalar']);quantity(r['blobGasUsed'])
   for f in ['gasUsed','effectiveGasPrice','l1Fee','operatorFeeScalar','operatorFeeConstant','l1GasUsed','l1GasPrice','tokenRatio']:quantity(r[f])
   assert (typ==2 if pm[h]['role']=='E_outgoing' else typ==0)
   receipts[h]=r;guard(start)
  literals=read('three-fee-literal-preflight.json')['records'];assert [(z['case'],z['hash']) for z in literals]==[(z['case'],z['hash']) for z in plan['fixed_three_cases_in_order']]
  for z in literals:
   h=z['hash'].lower();assert pm[h]['role']=='E_outgoing';v=calculate(receipts[h]);cache[h]=v;published=published_units(z['published_decimal_literal_MNT']);match=v['total']==published
   three.append({'case':z['case'],'hash':h,'source_html':z['source_html'],'source_html_sha256':z['source_html_sha256'],'actual_fee_child_span':z['actual_fee_child_span'],'published_literal_MNT':z['published_decimal_literal_MNT'],'published_minimal_units':str(published),'fixed_formula_components_minimal_units':units(v),'computed_total_MNT':mnt(v['total']),'computed_minus_published_minimal_units':str(v['total']-published),'exact_equal_no_rounding':match})
   write('three-bill-comparison.json',{'status':'IN_PROGRESS_FIXED3_GATE','records':three,'no_formula_fitting_or_alternative_samples':True})
   assert match,('FIXED_THREE_BILL_EXACT_MISMATCH',z['case']);guard(start)
  assert len(three)==3 and all(z['exact_equal_no_rounding'] for z in three)
  write('three-bill-comparison.json',{'status':'ALL3_EXACT_MATCH_FIXED_FORMULA','records':three,'no_formula_fitting_or_alternative_samples':True,'scope':'Same-provider original receipt/published explorer display consistency; not independent binary/deployment proof'})
  for e in registry['entries']:
   h=e['hash'].lower();q=pm[h];r=receipts[h]
   if q['role']=='E_incoming':excluded.append({'hash':h,'reason':'other sender transaction into E; no network bill charged to E in this output','type_verbatim':r['type']});continue
   v=cache[h] if h in cache else calculate(r);category='failed' if quantity(r['status'])==0 else 'successful_deployment' if q['creation'] else 'other_success';view='X_linked_address_predicate' if q['X_linked_address_predicate'] else 'other_target'
   bills.append({'hash':h,'role':'E_outgoing','type_verbatim':r['type'],'status_verbatim':r['status'],'category_mutually_exclusive':category,'cross_view_not_additive':view,'original_parsed_receipt':e['parsed'],'original_parsed_receipt_sha256':e['parsed_sha256'],'raw_fee_fields':{k:r[k] for k in ['gasUsed','effectiveGasPrice','l1Fee','operatorFeeScalar','operatorFeeConstant','tokenRatio']},'network_gross_bill_minimal_units':units(v),'network_gross_bill_MNT':mnt(v['total'])});outgoing.append((h,category,view,v));guard(start)
  assert len(bills)==len({z['hash'] for z in bills})==262 and len(excluded)==3
  def aggregate(items):
   v={k:sum(q[3][k] for q in items) for k in ['execution','l1','operator','total']};return {'transaction_count':len(items),'components_minimal_units':units(v),'total_MNT':mnt(v['total'])}
  main_groups={k:aggregate([q for q in outgoing if q[1]==k]) for k in ['failed','successful_deployment','other_success']};views={k:aggregate([q for q in outgoing if q[2]==k]) for k in ['X_linked_address_predicate','other_target']};whole=aggregate(outgoing)
  assert sum(v['transaction_count'] for v in main_groups.values())==262 and sum(v['transaction_count'] for v in views.values())==262
  assert sum(int(v['components_minimal_units']['total']) for v in main_groups.values())==int(whole['components_minimal_units']['total']) and sum(int(v['components_minimal_units']['total']) for v in views.values())==int(whole['components_minimal_units']['total'])
  write('individual-network-bills.json',{'status':'FIXED262_E_OUTGOING_NETWORK_GROSS_BILLS','unit':'MNT minimal units; 1 MNT=10^18; integer only','records':bills,'excluded_incoming':excluded,'not_net_profit_or_universal_economic_payer_statement':True})
  summary={'status':'CONDITIONAL_FIXED_FORMULA_THREE_BILLS_ALIGNED_262_GROSS_NETWORK_BILLS','unit':'MNT; no fiat or market valuation','E_outgoing_all':whole,'mutually_exclusive_main_groups':main_groups,'cross_views_same262_do_not_add_to_main':views,'excluded_incoming_count':3,'ordinary_source_conditions':'fixed source type2 E outgoing; DA scalar nonnull footprint serialization; no blobGasPrice/deposit/native-meta branch identified; historical provider binary/deployment independently UNKNOWN','published_display_scope':'Three original spanTxFee child literals align exactly; tooltip alone did not establish L1 inclusion','economic_scope':'Network gross charge; third-party reimbursements/subsidies and complete economic burden UNKNOWN; no token income, net profit, ROI, capital curve or capacity conclusion','three_gate_exact_match':True}
  write('network-bill-summary.json',summary);status='COMPLETE_FIXED_ONCE';guard(start)
 except BaseException as e:error=type(e).__name__+': '+str(e)
 finally:
  signal.setitimer(signal.ITIMER_REAL,0)
  if status!='COMPLETE_FIXED_ONCE' and not (len(three)==3 and all(z['exact_equal_no_rounding'] for z in three)):
   write('three-bill-comparison.json',{'status':'STOPPED_FIXED3_GATE_NO_262_AGGREGATION','error':error,'records_attempted_until_first_failure':three,'not_attempted_fixed_cases':[z for z in plan['fixed_three_cases_in_order'] if z['hash'] not in {q['hash'] for q in three}],'no_formula_change_rounding_fit_retry_or_sample_change':True})
  receipt={'status':status,'started_utc':started,'finished_utc':utc(),'elapsed_seconds':time.monotonic()-start,'root_go_file_sha256':sha((P/'root-go.json').read_bytes()),'run_plan_sha256':planhash,'formal_script_sha256':sha(Path(__file__).read_bytes()),'formal_attempt_count':1,'error':error,'three_fixed_checks_completed':len(three),'all3_exact_matches':len(three)==3 and all(z['exact_equal_no_rounding'] for z in three),'E_outgoing_bills_written_count':len(bills),'incoming_excluded_count':len(excluded),'peak_rss_bytes':peak_rss(),'single_thread':threading.active_count()==1,'network_install_EVM_models_trading_credentials_or_excluded_archive_access':False,'no_formula_retry_fit_or_sample_change':True,'actual_model_effort':'UNKNOWN'}
  receipt['manifest']=[{'file':f.name,'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())} for f in sorted(P.iterdir()) if f.is_file() and f.name!='formal-execution-receipt.json'];write('formal-execution-receipt.json',receipt)
  print(json.dumps({'status':status,'error':error,'fixed3_exact_matches':receipt['all3_exact_matches'],'E_outgoing_count':len(bills),'incoming_excluded':len(excluded),'elapsed_seconds':receipt['elapsed_seconds'],'peak_rss_bytes':receipt['peak_rss_bytes'],'summary_written':summary is not None},ensure_ascii=False))
if __name__=='__main__':main()
