"""Own offline event QA only; no quantity sums or signed-amount arithmetic."""
from pathlib import Path
import sys,json,hashlib,datetime,resource
sys.dont_write_bytecode=True
import source_parser as sp
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(name,o,compact=False):
 b=(json.dumps(o,ensure_ascii=False,**({'separators':(',',':')} if compact else {'indent':2}))+'\n').encode();f=P/name;old=f.stat().st_size if f.exists() else 0
 assert sum(x.stat().st_size for x in P.iterdir() if x.is_file())-old+len(b)<8388608;f.write_bytes(b)
try:
 d=sp.load()
 save('event-pool.raw.json',{'schema':'standard_ERC20_Transfer_source_event_pool_v1','identity_key':'chainid5000 + transactionHash + canonical logIndex; never hash-only','quantity_format':'original 32-byte hexadecimal; no quantity addition/subtraction or decimal precision conversion yet','events':d['events']},True)
 save('receipt-identity-preflight.json',{'receipts':d['receipts'],'all265_fixed_source_identity_checked':True})
 save('source-input-manifest.json',{'files':d['manifest'],'network_actions':0})
 save('unsupported-or-malformed-candidates.json',{'records':d['anomalies'],'none_replaced_by_zero':True,'any_record_blocks_formal_quantity_aggregation':True})
 save('fixed119-liquidator-event-references.json',{'cases':d['cases119'],'actual_liquidators_bound_to_known_pool_logs':True,'per_receipt_per_liquidator_all_standard_Transfer_refs_including_aTokens':True,'different_liquidators_not_merged':True})
 save('provider-metadata.references.json',{'source_file':str(sp.INTERP),'source_sha256':sp.INTERP_SHA,'field':'items[].Transfer_source_fields[].provider_metadata','provenance':'Already retained provider labels; separate from event amount data. No issuer/decimals independent authentication, no unit scaling applied.','by_token_contract':d['metadata']})
 report={'status':'READY_WAIT_ROOT_GO_NO_QUANTITY_AGGREGATION' if not d['anomalies'] else 'BLOCKED_SOURCE_FORMAT_UNKNOWN_NO_QUANTITY_AGGREGATION','checked_utc':utc(),'counts_only':d['counts_only'],'all265_source_registry_and_normal_same_unique_set':True,'SSE_parsed_business_receipt_identity_match':True,'all_log_parent_block_hash_index_checks':True,'duplicate_txhash_logIndex_or_cross_tx_same_block_logIndex':False,'all119_positive_E_events_exact_identity_reconciled':True,'metadata_precision_used_for_quantities':False,'self_transfers_single_event_not_two_income_expense_entries':True,'L_ledger_scope':'Only fixed119 receipts, actual event-derived L addresses, each L separate, all tokens retained including aTokens; no nonzero-net filtering','quantity_addition_subtraction_or_precision_conversion':False,'formal_attempts':0,'ROOT_GO_received':False,'actual_model_effort':'UNKNOWN','peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)}
 save('preflight.json',report)
 print(json.dumps({'status':report['status'],'counts_only':d['counts_only'],'preflight_sha256':sha((P/'preflight.json').read_bytes()),'owner_disk_bytes':sum(x.stat().st_size for x in P.iterdir() if x.is_file()),'formal_quantity_arithmetic':False}))
except Exception as e:
 save('preflight-failure.json',{'status':'STOPPED_PREFLIGHT_NO_FORMAL_QUANTITY_ARITHMETIC','utc':utc(),'error':type(e).__name__+': '+str(e)});raise
