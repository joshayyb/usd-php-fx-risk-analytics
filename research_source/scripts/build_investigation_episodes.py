from pathlib import Path
from fractions import Fraction as F
import csv,json,hashlib
from datetime import date
P=Path('.')
R=P/'reports/investigation_episodes_v1';R.mkdir(parents=True,exist_ok=True)
source=P/'reports/investigation_indicators_v1/interval_indicators.csv'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source_hash=sha(source)
spec=P/'INDICATOR_ACTION_SPECIFICATION.md'
addition='''
## Approved episode layout and rules — 10 November 2026

New-item cards show VaR exceptions and new observed -3% drawdown crossings, combined into one card per original interval. Continuing drawdown is a compact ongoing-episode summary, not a new drawdown card. The complete original-interval table remains supporting detail.

An episode is a consecutive sequence of available numeric-endpoint observations with drawdown <=-3%. A subsequent observed drawdown >-3% ends the threshold episode. Equality remains flagged. The first crossing is first OBSERVED crossing, not reconstructed intraday timing. Calendar gaps remain visible, and days between endpoints are elapsed calendar span, not proven continuous time below threshold. VaR exclusions do not remove available drawdown observations.

Track first-crossing interval/gap, running peak at episode start, current/latest interval/gap, latest drawdown, deepest drawdown so far, count of flagged observations and observed threshold exit. Retain the earliest occurrence on tied deepest drawdowns. Daily/as-of summaries may use only observations up to that date; later exit/trough/recovery dates are never shown as if known earlier. Retrospective summaries must be labelled explicitly.

Recovery to the peak recorded at first crossing is a separate first-observed event (value >= that peak); threshold exit does not establish peak recovery. Multiple threshold episodes can share the same reference peak. Unobserved exits/recoveries remain unknown within the study, not assumed never to occur. Review notes are blank; automatic trigger ending never completes a review. No trading or numerical escalation action.
'''
if '## Approved episode layout and rules' not in spec.read_text():spec.write_text(spec.read_text()+addition)

def build(rows):
    episodes=[];support=[];snapshots=[];newitems=[];active=None
    for r in rows:
        flagged=F(r['drawdown_percent_exact'])<=-3
        assert flagged==(r['drawdown_flag']=='True')
        new=flagged and active is None
        if new:
            active={'episode_id':f'DD-{len(episodes)+1:03d}','first':r,'last':r,'deepest':r,'count':0,'exit':None}
            episodes.append(active)
        if flagged:
            active['count']+=1;active['last']=r
            if F(r['drawdown_percent_exact'])<F(active['deepest']['drawdown_percent_exact']):active['deepest']=r
            snapshots.append({'as_of_source_date':r['end_source_date'],'episode_id':active['episode_id'],
                'state':'new_crossing' if new else 'continuing','first_crossing_source_date':active['first']['end_source_date'],
                'current_interval_id':r['interval_id'],'current_interval_start':r['start_source_date'],'current_interval_end':r['end_source_date'],
                'gap_calendar_days':r['gap_calendar_days'],'gap_group':r['gap_group'],
                'reference_peak_php':active['first']['running_peak_php'],'reference_peak_source_date':active['first']['running_peak_source_date'],
                'current_drawdown_php':r['drawdown_php'],'current_drawdown_percent':r['drawdown_percent'],
                'deepest_so_far_source_date':active['deepest']['end_source_date'],
                'deepest_so_far_percent':active['deepest']['drawdown_percent'],
                'flagged_observations_so_far':active['count'],
                'elapsed_calendar_days_since_first_observed_crossing':(date.fromisoformat(r['end_source_date'])-date.fromisoformat(active['first']['end_source_date'])).days,
                'review_note':''})
        exiting=None
        if not flagged and active:
            active['exit']=r;exiting=active['episode_id'];active=None
        episode_id=active['episode_id'] if flagged else ''
        support.append({**r,'drawdown_episode_id':episode_id,'threshold_exit_episode_id':exiting or '',
            'presentation_state':'new_crossing' if new else 'continuing' if flagged else 'threshold_episode_ended' if exiting else 'no_drawdown_trigger'})
        vf=r['var_exception']=='True'
        if new or vf:
            newitems.append({'interval_id':r['interval_id'],'start_source_date':r['start_source_date'],
                'end_source_date':r['end_source_date'],'gap_calendar_days':r['gap_calendar_days'],'gap_group':r['gap_group'],
                'triggers':'; '.join(x for x,b in [('VaR exception',vf),('New drawdown crossing',new)] if b),
                'drawdown_episode_id':episode_id,'drawdown_state':'new_crossing' if new else 'continuing' if flagged else 'not_triggered',
                'drawdown_php':r['drawdown_php'],'drawdown_percent':r['drawdown_percent'],
                'target_loss_php':r['target_loss_php'],'prior_var99_php':r['prior_var99_php'],
                'exceedance_php':r['exceedance_php'] if vf else '',
                'data_status':'Available with qualification; see per-indicator status in supporting table',
                'reviewer':'','review_date':'','evidence_examined':'','findings':'','follow_up':''})
    return episodes,support,snapshots,newitems

rows=list(csv.DictReader(source.open()));episodes,support,snapshots,newitems=build(rows)
retrospective=[]
for e in episodes:
    first,last,deep,exit=e['first'],e['last'],e['deepest'],e['exit']
    peak=F(first['running_peak_php'])
    recovery=next((r for r in rows if r['end_source_date']>=first['end_source_date'] and F(r['position_value_php'])>=peak),None)
    retrospective.append({'episode_id':e['episode_id'],'first_crossing_interval_start':first['start_source_date'],
        'first_crossing_source_date':first['end_source_date'],'first_gap_group':first['gap_group'],
        'first_gap_calendar_days':first['gap_calendar_days'],'reference_peak_php':first['running_peak_php'],
        'reference_peak_source_date':first['running_peak_source_date'],'flagged_observations':e['count'],
        'last_flagged_source_date':last['end_source_date'],'last_flagged_interval_start':last['start_source_date'],
        'last_gap_group':last['gap_group'],'deepest_source_date':deep['end_source_date'],
        'deepest_drawdown_php':deep['drawdown_php'],'deepest_drawdown_percent':deep['drawdown_percent'],
        'threshold_exit_source_date':exit['end_source_date'] if exit else '',
        'threshold_exit_drawdown_percent':exit['drawdown_percent'] if exit else '',
        'threshold_status_at_study_end':'ended' if exit else 'ongoing',
        'reference_peak_recovery_source_date':recovery['end_source_date'] if recovery else '',
        'recovery_status':'observed' if recovery else 'not observed within study',
        'elapsed_calendar_days_first_to_last_flag':(date.fromisoformat(last['end_source_date'])-date.fromisoformat(first['end_source_date'])).days,
        'scope':'retrospective episode summary; exit/deepest/recovery may be later than first crossing',
        'review_note':''})
assert len(rows)==1647 and len(episodes)==15 and len(snapshots)==733
assert sum(e['count'] for e in episodes)==733
assert len({r['interval_id'] for r in newitems})==len(newitems)
assert sum('VaR exception' in r['triggers'] for r in newitems)==22
assert sum('New drawdown crossing' in r['triggers'] for r in newitems)==15
# Verify as-of summaries do not change when later observations are removed.
for n in [1,300,600,1000,len(rows)]:
    _,_,prefix,_=build(rows[:n])
    assert prefix==[s for s in snapshots if s['as_of_source_date']<=rows[n-1]['end_source_date']]
for e in episodes:
    assert F(e['first']['drawdown_percent_exact'])<=-3
    if e['exit']:assert F(e['exit']['drawdown_percent_exact'])>-3

def save(name,data):
    with (R/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
save('episode_summary_retrospective.csv',retrospective);save('episode_snapshots_asof.csv',snapshots)
save('complete_interval_detail.csv',support);save('new_item_cards.csv',newitems)
ongoing=[s for s in snapshots if s['as_of_source_date']==rows[-1]['end_source_date']]
(R/'latest_ongoing_summary.json').write_text(json.dumps({'as_of':rows[-1]['end_source_date'],'ongoing':ongoing,'meaning_if_empty':'No active -3% threshold episode; does not establish zero drawdown or no risk.'},indent=2)+'\n')
lines=['# Drawdown episode summary','', '**Retrospective view, through 30 September 2026.** Later exits, deepest values and recoveries were not known at initial crossings.','', '| Episode | First observed crossing | Flagged observations | Deepest drawdown | Observed threshold exit | Recovery to reference peak |','|---|---|---:|---:|---|---|']
for e in retrospective:lines.append(f"| {e['episode_id']} | {e['first_crossing_source_date']} | {e['flagged_observations']} | {float(e['deepest_drawdown_percent']):.4f}% | {e['threshold_exit_source_date'] or 'Not observed'} | {e['reference_peak_recovery_source_date'] or 'Not observed'} |")
lines+=['','## Reading the result','',f"733 flagged observations form 15 threshold episodes. Only {len(newitems)} intervals need new-item cards, combining 22 VaR exceptions and 15 drawdown crossings where they overlap. Continuing drawdown remains visible in the as-of summary. An episode ending means drawdown rose above -3%; recovery to its reference peak is a separate event.",'','The supporting table preserves all 1,647 original intervals, source dates and gap groups, including unavailable VaR results. Episode spans are observed endpoint spans, not proof of continuous time below threshold. Review notes remain blank. No automatic trading action.','', 'As-of data: episode_snapshots_asof.csv contains only information known by each recorded source endpoint under retrospective sequence assumptions. Retrospective episode summaries are never substituted for earlier as-of cards.','', 'Next: review one episode across its first crossing, continuation and threshold exit before building the full guided report.']
(R/'EPISODE_SUMMARY.md').write_text('\n'.join(lines)+'\n')
manifest=json.loads((P/'reports/var_validation_v1/checksums.json').read_text())
assert all(sha(P/'reports/var_validation_v1'/n)==h for n,h in manifest.items())
assert sha(source)==source_hash
checks={'episodes':len(episodes),'flagged_observations':len(snapshots),'new_item_cards':len(newitems),'overlapping_new_triggers':37-len(newitems),'complete_original_intervals':len(support),'source_indicators_unchanged':True,'source_sha256':source_hash,'frozen_VaR_files_verified_unchanged':len(manifest),'exact_boundary_checks':'passed','prefix_invariance_checks':5,'review_notes':'blank; no review completion inferred','limitations':'Numeric source endpoints only; economic/publication timing qualified; no full report built.'}
(R/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
(R/'checksums.json').write_text(json.dumps({p.name:sha(p) for p in sorted(R.iterdir()) if p.is_file() and p.name!='checksums.json'},indent=2)+'\n')
print(json.dumps(checks,indent=2));print('FIRST EPISODE',json.dumps(retrospective[0],indent=2));print('LATEST',ongoing)
