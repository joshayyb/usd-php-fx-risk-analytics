"""Portable numerical replay of saved main VaR and stress outputs (standard library).

This does not reproduce raw-workbook acquisition or certify public release timing.
It never edits the bundled financial inputs or the original research workspace.
"""
from pathlib import Path
from fractions import Fraction as F
import csv, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
def rows(name):
    with (ROOT/name).open(newline='') as stream:return list(csv.DictReader(stream))
def require(ok,message):
    if not ok:raise RuntimeError(message)
def main():
    ledger=rows('data/processed/bsp_usd_php_interval_ledger_v1.csv')
    saved=rows('reports/var_validation_v1/results/main_250_higher_full.csv')
    eligible=[r for r in ledger if r['calendar_eligibility']=='candidate']
    require(len(ledger)==1647 and len(eligible)==1640,'Unexpected frozen interval coverage.')
    byid={r['interval_id']:r for r in ledger};exceptions=0
    for result in saved:
        target=byid[result['target_interval_id']]
        training=[r for r in eligible if int(r['interval_order'])<int(target['interval_order'])][-250:]
        require(len(training)==250,'Insufficient prior eligible history.')
        rate=F(target['start_rate_raw']);base=1_000_000*rate
        losses=sorted(-base*(F(r['end_rate_raw'])/F(r['start_rate_raw'])-1) for r in training)
        index=(99*(len(losses)-1)+99)//100
        var=losses[index];loss=1_000_000*(rate-F(target['end_rate_raw']))
        require(var==F(result['var_exact']) and loss==F(result['target_loss_exact']),'Exact target mismatch: '+result['target_end'])
        flag=loss>var;require(flag==(result['is_exception']=='True'),'Exception mismatch.');exceptions+=flag
    require(len(saved)==1390 and exceptions==22,'Main counts differ from verified baseline.')
    historical=min(ledger,key=lambda r:(F(r['end_rate_raw'])/F(r['start_rate_raw'])-1,r['end_source_date'],int(r['interval_order'])))
    require((historical['start_source_date'],historical['end_source_date'])==('2025-08-04','2025-08-05'),'Historical selection changed.')
    hist=F(historical['end_rate_raw'])/F(historical['start_rate_raw'])-1
    stress=rows('reports/stress_testing_v1/scenario_results.csv')
    for row in stress:
        shock=F(row['shock_numerator'])/F(row['shock_denominator'])
        base=F('62.485')*1_000_000 if row['case']=='Hypothetical USD1m' else F(814_000_000)
        require(base*shock==F(row['pnl_numerator'])/F(row['pnl_denominator']),'Stress exact P&L mismatch.')
        require(shock==hist if row['scenario_type']=='historical replay' else shock in {F(n,100) for n in (-5,-3,-1,1,3,5)},'Unexpected stress scenario.')
    require(len(stress)==14,'Stress row coverage changed.')
    result={'status':'passed','main_targets_exactly_replayed':1390,'exceptions':22,'stress_rows_exactly_replayed':14,
            'scope':'numerical replay from attributed published-observation extracts; not raw-source or BPI-PDF reverification',
            'ledger_sha256':hashlib.sha256((ROOT/'data/processed/bsp_usd_php_interval_ledger_v1.csv').read_bytes()).hexdigest()}
    out=ROOT/'.local-runs';out.mkdir(exist_ok=True);(out/'replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
