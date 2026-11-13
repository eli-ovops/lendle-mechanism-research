"""Identity/time/conflict QC only. No token quantity, fee or monetary arithmetic."""
from pathlib import Path
from decimal import Decimal,InvalidOperation
from collections import defaultdict,Counter
import json,hashlib,datetime
P=Path(__file__).resolve().parent;R=P.parent/'root'
H=lambda b:hashlib.sha256(b).hexdigest()
U=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def load(path):return json.loads(path.read_bytes(),parse_float=str)
mf=load(P/'fixed-five-batch-request-manifest.json');ev=load(R/'fixed-valuation-events.json');protocol=load(R/'protocol.json')
assert H((R/'fixed-valuation-events.json').read_bytes())=='11a85bfa4c9897dade4b91be7555b9bad2d63b14c14daeca6649773409768326'
assert H((R/'protocol.json').read_bytes())==mf['protocol_sha256']
assert len(ev['rows'])==381
pool=[];groups=defaultdict(list);business=[]
for chunk in mf['chunks']:
 n=chunk['batch'];prefix=f'{n+5:02d}-batch-{n:02d}';raw=P/(prefix+'.source.json');doc=load(raw);acq=load(P/(prefix+'.acquisition.json'))
 assert acq['complete_HTTP_200'] and H(raw.read_bytes())==acq['sha256']
 assert isinstance(doc.get('coins'),dict) and not(set(doc['coins'])-set(chunk['coins']))
 business.append({'batch':n,'requested_pairs':len(chunk['pairs']),'returned_coin_identifiers':list(doc['coins']),'requested_coins_missing':sorted(set(chunk['coins'])-set(doc['coins'])),'complete_JSON':True,'schema_top_level':list(doc)})
 for coin,obj in doc['coins'].items():
  assert isinstance(obj,dict)and isinstance(obj.get('prices'),list)
  for i,point in enumerate(obj['prices']):
   assert isinstance(point,dict)
   ts=point.get('timestamp');price=point.get('price');valid_time=isinstance(ts,int)and not isinstance(ts,bool)and ts>=0
   try:d=Decimal(str(price));valid_price=d.is_finite()and d>0
   except(InvalidOperation,ValueError,TypeError):valid_price=False
   p={'pool_row':len(pool)+1,'coin':coin,'source_batch':n,'source_price_index':i,'source_path':str(raw),'source_sha256':acq['sha256'],'returned_coin_metadata':{k:v for k,v in obj.items()if k!='prices'},'returned_point':point,'timestamp_valid':valid_time,'price_valid_positive_finite':valid_price,'currency_definition':'UNKNOWN','price_value_lexeme':str(price),'no_requested_timestamp_assigned':True}
   pool.append(p)
   if valid_time:groups[(coin,ts)].append(p)
duplicates=[];conflicts=[];group_flags={}
for key,rows in groups.items():
 signatures={(p['price_value_lexeme'],json.dumps({k:p['returned_coin_metadata'].get(k,'MISSING')for k in ['symbol','decimals','currency','quoteCurrency']},sort_keys=True),json.dumps({k:p['returned_point'].get(k,'MISSING')for k in ['decimals','currency','quoteCurrency']},sort_keys=True))for p in rows}
 conflict=len(signatures)>1
 group_flags[key]=conflict
 if len(rows)>1:duplicates.append({'coin':key[0],'timestamp':key[1],'pool_rows':[p['pool_row']for p in rows],'equal_price_unit_precision':not conflict,'conflict':conflict})
 if conflict:conflicts.append(duplicates[-1])
results=[];used=Counter()
for row in ev['rows']:
 coin=row['coin'];T=row['timestamp'];ks=[k for k in groups if k[0]==coin and T-3600<=k[1]<=T]
 r={'kind':row['kind'],'event_id':row.get('event_id'),'hash':row['hash'],'coin':coin,'transaction_timestamp':T,'accounting_window_inclusive':[T-3600,T],'main_USD_mark_accepted':False,'USD_gate_reason':'Official same-service USD definition not obtained in bounded docs reads; no currency supplied in response','future_observations_exist':any(k[0]==coin and k[1]>T for k in groups),'old_pilot_excluded':True}
 if not ks:r.update(price_time_candidate_status='MISSING_NO_IN_WINDOW_OBSERVATION',selected_timestamp=None,selected_pool_rows=[])
 else:
  key=max(ks,key=lambda k:k[1]);rs=groups[key];bad=any(not p['price_valid_positive_finite']for p in rs)
  identity_bad=(coin=='coingecko:mantle'and any(p['returned_coin_metadata'].get('symbol')!='MNT'for p in rs))
  status='MISSING_MAX_TIMESTAMP_CONFLICT'if group_flags[key]else'MISSING_SELECTED_INVALID_PRICE'if bad else'MISSING_MNT_IDENTITY'if identity_bad else'AVAILABLE_PRICE_TIME_CANDIDATE_ONLY'
  r.update(price_time_candidate_status=status,selected_timestamp=key[1],age_seconds=T-key[1],selected_pool_rows=[p['pool_row']for p in rs],selected_price_lexeme=rs[0]['price_value_lexeme'],selected_metadata=rs[0]['returned_coin_metadata'],selected_point=rs[0]['returned_point'])
  if status=='AVAILABLE_PRICE_TIME_CANDIDATE_ONLY':used[key]+=1
 results.append(r)
by_kind={kind:{'events':sum(r['kind']==kind for r in results),'candidate_available':sum(r['kind']==kind and r['price_time_candidate_status']=='AVAILABLE_PRICE_TIME_CANDIDATE_ONLY'for r in results),'USD_accepted':0,'status_counts':dict(Counter(r['price_time_candidate_status']for r in results if r['kind']==kind))}for kind in sorted({r['kind']for r in results})}
summary={'completed_utc':U(),'scope':'Fixed381 event identities and timestamp coverage only; no scaling, value multiplication, netting, fee or quantity recomputation','protocol_sha256':mf['protocol_sha256'],'event_manifest_sha256':H((R/'fixed-valuation-events.json').read_bytes()),'fixed_request_manifest_sha256':H((P/'fixed-five-batch-request-manifest.json').read_bytes()),'requested_coin_timestamp_pairs':376,'returned_price_rows':len(pool),'returned_unique_coin_timestamp_groups':len(groups),'returned_exact_coin_identifiers':sorted({p['coin']for p in pool}),'business_results':business,'duplicate_equal_or_conflicting_groups':len(duplicates),'conflicting_groups':len(conflicts),'conflicts':conflicts,'invalid_timestamp_rows':sum(not p['timestamp_valid']for p in pool),'invalid_price_rows':sum(not p['price_valid_positive_finite']for p in pool),'by_event_kind':by_kind,'all381_candidate_price_time_covered':all(r['price_time_candidate_status']=='AVAILABLE_PRICE_TIME_CANDIDATE_ONLY'for r in results),'all381_USD_mark_gate_passed':False,'USD_definition':'UNKNOWN','complete_USD_main_account_not_calculated':True,'unique_observations_selected':len(used),'selected_shared_observations':sum(n>1 for n in used.values()),'maximum_events_using_one_observation':max(used.values(),default=0),'batch_response_not_request_pair_bijection_certified':'No requested timestamp field in returned prices; array position not treated as mapping proof. All matching is fixed returned-pool matching.','old_pilot_not_loaded_or_used':True,'future_points_auxiliary_only':True,'confidence_metadata_only_no_threshold':True,'no_new_network':True,'actual_model_effort':'UNKNOWN'}
(P/'returned-price-pool.raw-derived.json').write_text(json.dumps({'rows':pool},indent=2)+'\n')
(P/'duplicate-observation-provenance.json').write_text(json.dumps({'groups':duplicates},indent=2)+'\n')
(P/'fixed381-price-time-mapping.json').write_text(json.dumps({'rows':results},indent=2)+'\n')
(P/'coverage-qc.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
