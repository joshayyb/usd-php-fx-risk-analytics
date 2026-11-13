from pathlib import Path
from fractions import Fraction as F
import csv,json,hashlib
P=Path('.');R=P/'reports/investigation_indicators_v1';R.mkdir(parents=True,exist_ok=True)
spec='''# Approved investigation indicators and actions

Approved 10 November 2026. Fixed hypothetical unhedged long USD1 million; PHP reporting. Guided historical report, not automatic trading.

VaR: reuse exact signed 99% 250/higher main results. Flag strictly when subsequent signed loss exceeds prior signed VaR. Preserve exact ties and original endpoints. Display P&L, loss, prior VaR and exceedance. Review inputs, gap and surrounding observations; no causal assumption.

Drawdown: running peak starts at first numeric study valuation, uses no future values and never resets yearly. Drawdown=(value-peak)/peak; flag at or below -3%, an illustrative review trigger, not calibrated risk limit. Distinguish first crossing from continuing flag. Keep 2022 within-year chart separate. On tied peaks retain first attainment date.

Data status per indicator: Available / Available with qualification / Unavailable. Missing VaR due to warm-up or excluded review intervals is not zero or no flag. Expected calendar nonpublication is context, not automatically an error. Preserve original dates and gap group on every flag. All calculated results carry unverified economic-date/publication-timing qualifications.

One card per original interval, combining triggers. Fields: trigger, impact, original interval/gap, evidence to check and blank reviewer/date/evidence/findings/follow-up note. Existing source checks may be marked complete; substantive review is not completed until recorded. No flag means only no trigger in evaluated rules; unavailable means not evaluated. No automatic action or numerical escalation levels.

Stress is display-only, separately dated 30Sep2026 baseline; BPI supporting illustration dated31Dec2025. Do not interpret fixed stress references as contemporaneous earlier forecasts or combine with VaR exception counts.

Approved sample: Aug4–5,2025; gap1; rates58.392→57.514; P&L -PHP878000; priorVaR PHP425719.97; loss beyondVaR PHP452280.03. Endpoints source-matched in existing audit, rows17391→17392. Review surrounding observations; no macro cause inferred. Drawdown to be calculated separately below.
'''
(P/'INDICATOR_ACTION_SPECIFICATION.md').write_text(spec)
ledger=P/'data/processed/bsp_usd_php_interval_ledger_v1.csv'; vp=P/'reports/var_validation_v1/results/main_250_higher_full.csv'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((P/'reports/var_validation_v1/checksums.json').read_text());assert sha(vp)==manifest['results/main_250_higher_full.csv']
rows=list(csv.DictReader(ledger.open()));var={r['target_interval_id']:r for r in csv.DictReader(vp.open())}
peak=F(rows[0]['start_rate_raw'])*1000000; peakdate=rows[0]['start_source_date']; previous_flag=False;out=[]
for r in rows:
    value=F(r['end_rate_raw'])*1000000
    if value>peak:peak=value;peakdate=r['end_source_date']
    dd=value-peak; ddpct=dd/peak;flag=ddpct<=F(-3,100);v=var.get(r['interval_id'])
    vf=bool(v and v['is_exception']=='True')
    if v:assert (F(v['target_loss_exact'])>F(v['var_exact']))==vf
    out.append(dict(interval_id=r['interval_id'],start_source_date=r['start_source_date'],end_source_date=r['end_source_date'],gap_calendar_days=r['gap_calendar_days'],gap_group=r['gap_group'],position_value_php=str(value),running_peak_php=str(peak),running_peak_source_date=peakdate,drawdown_php=str(dd),drawdown_percent=float(ddpct*100),drawdown_percent_exact=str(ddpct*100),drawdown_flag=flag,drawdown_event='first_crossing' if flag and not previous_flag else 'continuing' if flag else 'no_trigger',drawdown_status='Available with qualification',var_status='Available with qualification' if v else 'Unavailable',var_unavailable_reason='' if v else 'excluded_review' if r['calendar_eligibility']=='review' else 'insufficient_history',var_exception=vf if v else '',prior_var99_php=v['prior_var99_php'] if v else '',target_loss_php=v['target_loss_php'] if v else '',exceedance_php=v['loss_minus_var_php'] if vf else '',any_trigger=flag or vf,qualification='Source-date ordering; economic horizon and public availability unverified'))
    previous_flag=flag
assert len(out)==1647 and sum(r['var_exception'] is True for r in out)==22
# Independent peak check on complete values, including initial valuation.
values=[F(rows[0]['start_rate_raw'])*1000000]+[F(r['end_rate_raw'])*1000000 for r in rows]
assert all(F(r['running_peak_php'])==max(values[:i+2]) for i,r in enumerate(out))
def save(name,rs):
    with (R/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(rs)
save('interval_indicators.csv',out);save('flagged_intervals.csv',[r for r in out if r['any_trigger']])
summary={'intervals':len(out),'initial_valuation_date':rows[0]['start_source_date'],'var_evaluated':len(var),'var_exceptions':22,'drawdown_flagged_intervals':sum(r['drawdown_flag'] for r in out),'drawdown_crossings':sum(r['drawdown_event']=='first_crossing' for r in out),'investigation_cards':sum(r['any_trigger'] for r in out),'first_drawdown_crossing':next(r for r in out if r['drawdown_event']=='first_crossing'),'maximum_drawdown':min(out,key=lambda r:F(r['drawdown_percent_exact'])),'checks':'exact threshold; initial value included; independent prefix maximum; saved VaR exceptions reconcile','ledger_sha256':sha(ledger),'var_results_sha256':sha(vp)}
(R/'checks.json').write_text(json.dumps(summary,indent=2)+'\n')
sample=next(r for r in out if r['end_source_date']=='2025-08-05')
(R/'sample_card.json').write_text(json.dumps({'indicators':sample,'reviewer':'','review_date':'','evidence_examined':'','findings':'','follow_up':'','source_checks':'Existing endpoint audit matches rows17391→17392; no repeated download'},indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['first_drawdown_crossing','maximum_drawdown']},indent=2));print('FIRST',summary['first_drawdown_crossing']['end_source_date']);print('MAX',summary['maximum_drawdown']['end_source_date'],summary['maximum_drawdown']['drawdown_percent'])
