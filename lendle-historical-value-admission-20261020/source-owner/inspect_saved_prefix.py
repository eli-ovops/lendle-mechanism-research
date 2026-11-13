"""Own offline incomplete-JSON-prefix field/identity QC. No valuation arithmetic."""
from pathlib import Path
import json,re,collections,hashlib,datetime
P=Path(__file__).resolve().parent;B=P.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(P/'02-response.source.json').read_bytes();text=raw.decode('utf-8');scope=json.loads((P/'fixed-cohort-source-scope.json').read_bytes());pay=set(scope['fixed119_E_receipt_hashes']);out=set(scope['fixed262_E_outgoing_hashes']);E='0x57d8718f0d24db1f3f6445337c8a0c24948d77c2'
reg=json.loads(Path(scope['registry']).read_bytes());normal=json.loads(Path(scope['normal']).read_bytes());nm={q['row']['hash'].lower():q['row'] for q in normal['records']};casefile=Path(scope['positive_E_case_source']);cm={c['hash'].lower():c for c in json.loads(casefile.read_bytes())['cases']}
assert sha(raw)=='5279cec1f3782c83e98d0d659308e945a4bf18c1c1e03c4e818e1f0f17681321'
head=re.match(r'\s*\{\s*"liquidations"\s*:\s*\[',text);assert head;pos=head.end();bytepos=len(text[:pos].encode());decoder=json.JSONDecoder();identities=[];matches=[];stats={};seen=collections.Counter();complete_count=0;stopped=None;last_end=pos;min_ts=None;max_ts=None;first=None;last=None
while True:
 sep=re.match(r'\s*,?\s*',text[pos:]);start=pos+sep.end();startbyte=bytepos+len(text[pos:start].encode())
 if start>=len(text):stopped={'reason':'BODY_PREFIX_END_BEFORE_NEXT_OBJECT','char_offset':start,'byte_offset':startbyte};break
 if text[start]==']':stopped={'reason':'LIQUIDATIONS_ARRAY_END_PRESENT','char_offset':start,'byte_offset':startbyte};break
 try:o,end=decoder.raw_decode(text,start)
 except json.JSONDecodeError as e:stopped={'reason':'FINAL_OBJECT_INCOMPLETE_JSON_PREFIX','object_start_char_offset':start,'object_start_byte_offset':startbyte,'decoder_message':e.msg,'decoder_error_char_offset':e.pos};break
 assert isinstance(o,dict);endbyte=startbyte+len(text[start:end].encode());complete_count+=1
 h=o.get('txHash');valid=isinstance(h,str) and re.fullmatch(r'0x[0-9a-fA-F]{64}',h);h=h.lower() if valid else None
 key=(h,str(o.get('logIndex')),str(o.get('id')));seen[key]+=1
 for k,v in o.items():
  st=stats.setdefault(k,{'present_count':0,'null_count':0,'json_type_counts':collections.Counter()});st['present_count']+=1;st['null_count']+=v is None;st['json_type_counts'][type(v).__name__]+=1
 ts=o.get('blockTimestamp')
 if isinstance(ts,int) and not isinstance(ts,bool):min_ts=ts if min_ts is None or ts<min_ts else min_ts;max_ts=ts if max_ts is None or ts>max_ts else max_ts
 ident={'row_position_in_prefix_1based':complete_count,'source_start_byte':startbyte,'source_end_byte_exclusive':endbyte,'id':o.get('id'),'txHash':h,'logIndex':o.get('logIndex'),'blockNumber':o.get('blockNumber'),'blockTimestamp':ts,'sender':o.get('sender')};identities.append(ident)
 if first is None:first=ident
 last=ident
 if h in out:
  n=nm[h];checks={'hash_in_fixed262':True,'sender_is_E':str(o.get('sender')).lower()==E,'blockNumber_matches_normal':str(o.get('blockNumber'))==str(n['blockNumber']),'blockTimestamp_matches_normal':str(ts)==str(n['timeStamp'])}
  if h in pay:
   c=cm[h];checks['same_pool_liquidation_logIndex_match']=o.get('logIndex') in [q['logIndex_identity_decimal'] for q in c['liquidations']];checks['collateral_addresses_overlap_known_liquidation']=bool({str(a).lower() for a in o.get('collateralAssets',[])}&{q['collateral_token'] for q in c['liquidations']})
  matches.append({'source_row_identity':ident,'in_fixed119_E_receipt_set':h in pay,'identity_checks':checks,'row_source_verbatim':o})
 last_end=end;pos=end;bytepos=endbyte
actual_full={m['row_source_verbatim']['txHash'].lower() for m in matches};actual119=actual_full&pay
appearance={m.group(1).lower() for m in re.finditer(r'"txHash"\s*:\s*"(0x[0-9a-fA-F]{64})"',text)}
for s in stats.values():s['json_type_counts']=dict(s['json_type_counts'])
def qset(fixed,full):return {'fixed_count':len(fixed),'hash_field_appears_in_raw_prefix_count':len(fixed&appearance),'complete_object_matched_hash_count':len(fixed&full),'hash_only_appearance_without_complete_object':sorted((fixed&appearance)-full),'not_observed_in_saved_prefix_hashes':sorted(fixed-full),'not_observed_does_not_mean_absent_from_full_response':True}
DEFAULT='0x5165cdcf3363042ec3f6c4c04e64df1a6378dfeb47acfce978560433722e1507'
result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_body_sha256':sha(raw),'source_body_bytes':len(raw),'response_document_complete':False,'extraction':'Only JSONDecoder-complete object records from the retained raw prefix. No braces appended, no source completion claimed.','complete_objects_decoded':complete_count,'first_complete_object_identity':first,'last_complete_object_identity':last,'blockTimestamp_minmax_in_complete_prefix':{'minimum_raw':min_ts,'maximum_raw':max_ts,'meaning':'transaction timestamps, not price observation timestamps'},'prefix_stop':stopped,'all_observed_row_field_inventory':stats,'fixed119_E_receipts':qset(pay,actual_full),'fixed262_network_fee_hash_cohort':qset(out,actual_full),'matched_cohort_complete_object_count':len(matches),'all_matched_available_identity_checks':all(all(m['identity_checks'].values()) for m in matches),'default_case':{'txHash':DEFAULT,'raw_txHash_field_appears':DEFAULT in appearance,'complete_objects':[m for m in matches if m['row_source_verbatim']['txHash'].lower()==DEFAULT]},'duplicate_id_txHash_logIndex_in_complete_prefix':[{'identity':list(k),'count':n} for k,n in seen.items() if n>1],'top_level_dbLastBlock_not_observed_in_saved_prefix':True,'whole_endpoint_dataset_or_absent_cohort_coverage':'UNKNOWN_INCOMPLETE_RESPONSE','financial_arithmetic_price_derivation_quantity_sums_or_PnL':False}
(P/'prefix-field-and-coverage-qc.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(P/'complete-prefix-record-identities.jsonl').write_text(''.join(json.dumps(x,separators=(',',':'))+'\n' for x in identities))
(P/'fixed-cohort-complete-objects.raw-derived.json').write_text(json.dumps({'source_body_sha256':sha(raw),'partial_document_only_complete_objects_used':True,'matched_rows':matches},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'complete_objects_decoded':complete_count,'stop':stopped,'field_names':sorted(stats),'fixed119':{k:v for k,v in result['fixed119_E_receipts'].items() if not isinstance(v,list)},'fixed262':{k:v for k,v in result['fixed262_network_fee_hash_cohort'].items() if not isinstance(v,list)},'default_complete_count':len(result['default_case']['complete_objects']),'all_matched_available_identity_checks':result['all_matched_available_identity_checks'],'first_timestamp':min_ts,'last_timestamp':max_ts,'field_coverage_qc_sha256':sha((P/'prefix-field-and-coverage-qc.json').read_bytes()),'new_disk_bytes':sum(f.stat().st_size for f in P.iterdir() if f.is_file())},ensure_ascii=False))
