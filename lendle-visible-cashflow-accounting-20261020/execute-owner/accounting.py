"""Single offline visible-cashflow historical marking. No network or upstream code imports.
prepare performs metadata/identity checks ONLY; money arithmetic exists only in formal().
"""
from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal,localcontext,Inexact,Rounded,InvalidOperation
from collections import Counter
import json,hashlib,sys,argparse,re,time,resource,os
D=Path(__file__).resolve().parent.parent;O=D/'execute-owner';B=D.parent
Q=B/'lendle-asset-quantity-ledger-20261020/execute-owner/E-event-ledger-and-token-totals.json'
M=Q.parent/'provider-metadata.references.json'
N=B/'lendle-network-actual-bills-20261020/execute-owner/individual-network-bills.json'
S=B/'lendle-historical-price-coverage-20261020/source-owner'
P=S/'fixed381-price-time-mapping.json';QC=S/'coverage-qc.json';POOL=S/'returned-price-pool.raw-derived.json'
PROTOCOL=D/'root/protocol.json';PRICE_PROTOCOL=S.parent/'root/protocol.json'
MANIFEST=O/'input-manifest-v3.json';PREFLIGHT=O/'preflight-v3.json'
EXPECTED={str(Q):'797bb26970e21e285ea47ec1337c3c016921f35815034565fc135a25b9813dd3',str(P):'3a39ef86fc9b9b7063b9fe9b9c829bcaa8f1983a534a273ce8e398be2b559ab6'}
DEFAULT='0x5165cdcf3363042ec3f6c4c04e64df1a6378dfeb47acfce978560433722e1507'
DEADLINE='2026-10-19T19:05:30+00:00'
CATS={'failed':133,'successful_deployment':8,'other_success':121}
def utc():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(),parse_float=Decimal)
def fp(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return {'sha256':h.hexdigest(),'bytes':p.stat().st_size}
def save(p,v):
    with Path(p).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def check_deadline():assert datetime.now(timezone.utc)<datetime.fromisoformat(DEADLINE),'WORK_DEADLINE'
def datasets():
    check_deadline();inputs={str(p):fp(p) for p in (Q,M,N,P,QC,POOL,PROTOCOL,PRICE_PROTOCOL)}
    for p,s in EXPECTED.items():assert inputs[p]['sha256']==s,'FIXED_INPUT_HASH:'+p
    assert fp(PROTOCOL)['sha256']=='3990455a255d3c71bae897761de5ee91ddb3ac06cd25f60d7a80f75952342564'
    for ref in read(PROTOCOL)['inputs'].values():assert inputs[ref['path']]=={'sha256':ref['sha256'],'bytes':ref['bytes']},'ROOT_PROTOCOL_INPUT_CHANGED'
    q,m,n,pm,pool=read(Q),read(M),read(N),read(P)['rows'],read(POOL)['rows']
    events=q['events'];bills=n['records'];meta=m['by_token_contract']
    assert q['event_count']==len(events)==119 and len(bills)==262 and len(pm)==381
    assert q['F21_not_combined'] is True and q['subject']=='0x57d8718f0d24db1f3f6445337c8a0c24948d77c2'
    assert len({x['event_id'] for x in events})==119 and len({x['hash'] for x in bills})==262
    assert dict(Counter(x['category_mutually_exclusive'] for x in bills))==CATS
    assert len(n['excluded_incoming'])==3
    assert all(x['role']=='E_outgoing' for x in bills)
    dec={}
    for token,ms in meta.items():
        assert len(ms)==1 and ms[0]['decimals_as_reported'] in ('6','8','18')
        dec[token]=int(ms[0]['decimals_as_reported'])
    assert len(dec)==9 and {x['token_contract'] for x in events}==set(dec)
    price={};pools={x['pool_row']:x for x in pool}
    for r in pm:
        key=(r['kind'],r['event_id'] if r['kind']=='E_payout' else r['hash']);assert key not in price
        assert isinstance(r['selected_price_lexeme'],str)
        d=Decimal(r['selected_price_lexeme']);assert d.is_finite() and d>0
        assert r['accounting_window_inclusive'][0]<=r['selected_timestamp']<=r['transaction_timestamp']==r['accounting_window_inclusive'][1]
        assert r['old_pilot_excluded'] is True and r['selected_point']['price']==r['selected_price_lexeme']
        assert r['selected_point']['timestamp']==r['selected_timestamp']
        assert r['selected_pool_rows']
        for ix in r['selected_pool_rows']:
            x=pools[ix];assert x['coin']==r['coin'] and x['price_value_lexeme']==r['selected_price_lexeme']
            assert x['returned_point']['timestamp']==r['selected_timestamp']
        price[key]=r
    hashes={x['hash'] for x in bills}
    for x in events:
        assert x['direction']=='in' and re.fullmatch('[0-9]+',x['unsigned_raw_decimal'])
        assert x['signed_raw_decimal']=='+'+x['unsigned_raw_decimal']
        chain,h,log=x['event_id'].split(':');assert chain=='5000' and h in hashes
        r=price[('E_payout',x['event_id'])]
        assert r['hash']==h and r['coin']=='mantle:'+x['token_contract']
    for x in bills:
        assert isinstance(x['network_gross_bill_MNT'],str)
        d=Decimal(x['network_gross_bill_MNT']);assert d.is_finite() and d>=0
        r=price[('E_network_gross_bill',x['hash'])];assert r['coin']=='coingecko:mantle'
    assert len([x for x in events if x['event_id'].split(':')[1]==DEFAULT])==1
    assert DEFAULT in hashes
    return q,m,n,price,dec,inputs

def prepare():
    q,m,n,price,dec,inputs=datasets()
    manifest={'created_UTC':utc(),'inputs':inputs,'fixed_expected_SHA256':EXPECTED,'metadata_validation_only':True,'no_money_arithmetic_or_formal_run':True,'provider_decimals_by_token':dec,'provider_decimals_independently_authenticated':False,'fixed_event_counts':{'payout':119,'network_bills':262,'tokens':9,'fee_categories':CATS},'default_bridge_hash':DEFAULT,'deadline_UTC':DEADLINE,'source_USD_gate_status_at_preflight':{'coverage_all381_USD_mark_gate_passed':read(QC)['all381_USD_mark_gate_passed'],'definition':read(QC)['USD_definition']},'script':{str(Path(__file__).resolve()):fp(__file__)},'supervisor':{str(O/'supervise.py'):fp(O/'supervise.py')},'required_root_go_keys':['allow_accounting','script_identity','input_manifest_identity','USD_unit_accepted','USD_evidence_inputs'],'actual_model_effort':'UNKNOWN','scope':'119 terminal E inflow Transfer marks minus fixed262 outgoing gross MNT bills marked individually; no X/F21 additive or subtractive view; no profit/ROI/alpha/capacity claim'}
    save(MANIFEST,manifest)
    save(PREFLIGHT,{'UTC':utc(),'status':'PASS_METADATA_ONLY_AWAIT_ROOT_GO_AND_USD_ADMISSION','manifest_identity':fp(MANIFEST),'script_identity':fp(__file__),'source_pool_selected_lexemes_and_timestamps_bound':True,'quantity_price_fee_multiplications':0,'amount_additions_or_subtractions':0,'formal_runs':0,'money_outputs':0,'temporary_files':[]})
    print('PASS_METADATA_ONLY_AWAIT_ROOT_GO_AND_USD_ADMISSION',flush=True)

def text(v):return format(v,'f')
def formal(gate_path):
    started=time.monotonic();check_deadline();gate_path=Path(gate_path);g=read(gate_path);manifest=read(MANIFEST)
    assert g['allow_accounting'] is True and g['USD_unit_accepted'] is True
    assert fp(__file__)==g['script_identity'] and fp(MANIFEST)==g['input_manifest_identity']
    assert g['USD_evidence_inputs']
    for p,ident in manifest['supervisor'].items():assert fp(p)==ident,'SUPERVISOR_CHANGED'
    for p,ident in g['USD_evidence_inputs'].items():assert fp(p)==ident,'USD_EVIDENCE_CHANGED'
    q,m,n,price,dec,inputs=datasets();assert inputs==manifest['inputs'],'INPUTS_CHANGED'
    save(O/'formal-started.lock',{'UTC':utc(),'PID':os.getpid(),'gate':str(gate_path),'gate_identity':fp(gate_path)})
    save(O/'configuration-before-arithmetic.seal.json',{'UTC':utc(),'gate':{str(gate_path):fp(gate_path)},'script':{str(Path(__file__).resolve()):fp(__file__)},'manifest':fp(MANIFEST),'inputs':inputs,'USD_evidence_inputs':g['USD_evidence_inputs']})
    # FIRST MONEY ARITHMETIC OCCURS BELOW THIS LINE, AFTER GO AND EXCLUSIVE LOCK.
    with localcontext() as c:
        c.prec=120;c.traps[Inexact]=True;c.traps[Rounded]=True
        payouts=[];fees=[];groups={t:{'raw_quantity':Decimal(0),'quantity':Decimal(0),'marked_receipts':Decimal(0),'count':0} for t in dec}
        categories={k:{'gross_MNT':Decimal(0),'marked_fee':Decimal(0),'marked_receipts':Decimal(0),'fee_count':0,'payout_count':0} for k in CATS}
        bill_by_hash={x['hash']:x for x in n['records']}
        for x in q['events']:
            t=x['token_contract'];r=price[('E_payout',x['event_id'])];h=r['hash']
            raw=Decimal(x['unsigned_raw_decimal']);qty=raw.scaleb(-dec[t]);value=qty*Decimal(r['selected_price_lexeme'])
            row={'event_id':x['event_id'],'hash':h,'token_contract':t,'provider_symbol':m['by_token_contract'][t][0]['symbol'],'provider_decimals':dec[t],'provider_decimals_reference':{'path':str(M),'sha256':inputs[str(M)]['sha256'],'field':'by_token_contract.'+t+'[0].decimals_as_reported'},'raw_quantity':x['unsigned_raw_decimal'],'quantity_conditioned_on_provider_decimals':text(qty),'selected_price_lexeme':r['selected_price_lexeme'],'transaction_timestamp':r['transaction_timestamp'],'selected_timestamp':r['selected_timestamp'],'selected_pool_rows':r['selected_pool_rows'],'historical_receipt_mark_USD':text(value),'mutually_exclusive_tx_category':bill_by_hash[h]['category_mutually_exclusive']}
            payouts.append(row);z=groups[t];z['raw_quantity']+=raw;z['quantity']+=qty;z['marked_receipts']+=value;z['count']+=1
            z=categories[row['mutually_exclusive_tx_category']];z['marked_receipts']+=value;z['payout_count']+=1
        for x in n['records']:
            r=price[('E_network_gross_bill',x['hash'])];mnt=Decimal(x['network_gross_bill_MNT']);value=mnt*Decimal(r['selected_price_lexeme']);cat=x['category_mutually_exclusive']
            fees.append({'hash':x['hash'],'category_mutually_exclusive':cat,'cross_view_not_additive':x['cross_view_not_additive'],'network_gross_bill_MNT_lexeme':x['network_gross_bill_MNT'],'selected_MNT_price_lexeme':r['selected_price_lexeme'],'transaction_timestamp':r['transaction_timestamp'],'selected_timestamp':r['selected_timestamp'],'selected_pool_rows':r['selected_pool_rows'],'historical_network_gross_bill_mark_USD':text(value),'fee_formula_recomputed':False})
            z=categories[cat];z['gross_MNT']+=mnt;z['marked_fee']+=value;z['fee_count']+=1
        total_receipts=sum((Decimal(x['historical_receipt_mark_USD']) for x in payouts),Decimal(0));total_fees=sum((Decimal(x['historical_network_gross_bill_mark_USD']) for x in fees),Decimal(0));difference=total_receipts-total_fees
        assert sum((v['marked_receipts'] for v in groups.values()),Decimal(0))==total_receipts
        assert sum((v['marked_fee'] for v in categories.values()),Decimal(0))==total_fees
        assert sum((v['marked_receipts'] for v in categories.values()),Decimal(0))==total_receipts
        token_output=[]
        for t,v in groups.items():token_output.append({'token_contract':t,'provider_metadata':m['by_token_contract'][t][0],'payout_count':v['count'],'raw_quantity_sum':text(v['raw_quantity']),'quantity_sum_provider_precision_conditional':text(v['quantity']),'historical_receipts_mark_USD':text(v['marked_receipts'])})
        category_output={k:{'network_bill_count':v['fee_count'],'payout_count':v['payout_count'],'network_gross_MNT_sum':text(v['gross_MNT']),'historical_receipts_mark_USD':text(v['marked_receipts']),'historical_network_gross_bill_mark_USD':text(v['marked_fee']),'visible_mark_difference_USD':text(v['marked_receipts']-v['marked_fee'])} for k,v in categories.items()}
        assert {k:v['network_bill_count'] for k,v in category_output.items()}==CATS
        default_p=[r for r in payouts if r['hash']==DEFAULT];default_f=[r for r in fees if r['hash']==DEFAULT];assert len(default_p)==len(default_f)==1
        default_diff=Decimal(default_p[0]['historical_receipt_mark_USD'])-Decimal(default_f[0]['historical_network_gross_bill_mark_USD'])
        bridge={'hash':DEFAULT,'terminal_E_payout':default_p[0],'gross_network_bill':default_f[0],'visible_mark_difference_USD':text(default_diff),'F21_or_internal_repayment_or_swap_cost_deducted_again':False,'X_view_added':False}
        result={'UTC':utc(),'status':'HISTORICAL_VISIBLE_CASHFLOW_MARK_ONLY','decimal_precision':120,'decimal_exact_operations_trap_Inexact_and_Rounded':True,'price_lexemes_unchanged':True,'provider_decimals_conditional_not_independent_chain_authentication':True,'payout_event_count':119,'network_bill_count':262,'token_group_count':9,'total_terminal_E_receipts_mark_USD':text(total_receipts),'total_262_network_gross_bills_mark_USD':text(total_fees),'visible_receipts_minus_network_gross_bills_mark_USD':text(difference),'token_groups':token_output,'mutually_exclusive_network_categories':category_output,'default_bridge':bridge,'not_complete_personal_profit_realized_sale_ROI_alpha_or_capacity':True,'third_party_reimbursement_subsidy_full_initial_final_assets_and_redemption_not_certified':True,'F21_internal_debt_swap_legs_not_readded_or_rededucted':True,'X_cross_view_not_additive':True,'excluded_other_sender_incoming_fee_count':3,'cashflow_mark_price_realizability_not_certified':True}
    save(O/'payout119-priced-rows.json',{'rows':payouts});save(O/'network262-priced-rows.json',{'rows':fees});save(O/'accounting-results.json',result)
    for p,ident in inputs.items():assert fp(p)==ident,'INPUT_CHANGED_AFTER_ARITHMETIC'
    check_deadline();assert time.monotonic()-started<=60,'COMPUTE_LIMIT'
    save(O/'final-result.seal.json',{'UTC':utc(),'outputs':{str(O/f):fp(O/f) for f in ('payout119-priced-rows.json','network262-priced-rows.json','accounting-results.json')},'configuration_seal':fp(O/'configuration-before-arithmetic.seal.json'),'formal_lock':fp(O/'formal-started.lock'),'unchanged_inputs':inputs,'formal_run_count':1,'actual_model_effort':'UNKNOWN'})
    print('HISTORICAL_VISIBLE_CASHFLOW_MARK_ONLY',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=('prepare','formal'));ap.add_argument('--go');a=ap.parse_args()
    if a.stage=='prepare':prepare()
    else:
        assert a.go
        formal(a.go)
