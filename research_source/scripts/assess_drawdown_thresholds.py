"""Exploratory threshold comparison. Read the assessment contract before use."""
import csv
import hashlib
import json
from datetime import date
from fractions import Fraction as F
from pathlib import Path
from statistics import median

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parents[1]
OUT = P / 'reports/drawdown_threshold_assessment_v1'
SOURCE = P / 'reports/investigation_indicators_v1/interval_indicators.csv'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def days(a, b):
    return (date.fromisoformat(b) - date.fromisoformat(a)).days

def save_csv(name, records):
    with (OUT / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

def run():
    OUT.mkdir(parents=True, exist_ok=True)
    protected = [SOURCE, P/'INDICATOR_ACTION_SPECIFICATION.md',
                 P/'reports/guided_historical_report_v1/index.html']
    manifest = json.loads((P/'reports/var_validation_v1/checksums.json').read_text())
    protected += [P/'reports/var_validation_v1'/name for name in manifest]
    before = {str(p.relative_to(P)): digest(p) for p in protected}
    assert all(digest(P/'reports/var_validation_v1'/name) == sha for name, sha in manifest.items())
    rows = list(csv.DictReader(SOURCE.open()))
    assert len(rows) == 1647
    assert all(rows[i-1]['end_source_date'] == r['start_source_date'] for i, r in enumerate(rows) if i)
    # Recover the initial valuation independently from the first interval's P&L.
    ledger = list(csv.DictReader((P/'reports/guided_historical_report_v1/valuation_pnl.csv').open()))
    # Initial source valuation is explicitly recorded in the existing indicator check.
    assert ledger[0]['interval_id'] == rows[0]['interval_id']
    initial = F(rows[0]['position_value_php']) - F(ledger[0]['pnl_exact'])
    assert initial == F(50_802_000)
    assert rows[0]['start_source_date'] == '2020-01-02'
    values = [F(r['position_value_php']) for r in rows]
    peaks = [max([initial] + values[:i+1]) for i in range(len(rows))]
    assert all(peaks[i] == F(r['running_peak_php']) for i, r in enumerate(rows))
    assert all((values[i]/peaks[i]-1)*100 == F(r['drawdown_percent_exact']) for i, r in enumerate(rows))
    # Identify shared peak-to-recovery periods; distinct periods need not be statistically independent.
    underwater_ids = []
    active = False
    period = 0
    for i in range(len(rows)):
        if values[i] < peaks[i]:
            if not active:
                period += 1
            active = True
            underwater_ids.append(period)
        else:
            active = False
            underwater_ids.append(None)

    summaries, episodes, outcomes = [], [], []
    for threshold in (2, 3, 4):
        flags = [F(r['drawdown_percent_exact']) <= -threshold for r in rows]
        starts = [i for i, flag in enumerate(flags) if flag and (i == 0 or not flags[i-1])]
        these_episodes = []
        for n, start in enumerate(starts, 1):
            end = start
            while end+1 < len(rows) and flags[end+1]:
                end += 1
            record = dict(threshold_pct=threshold, episode=n, underwater_period=underwater_ids[start],
                          first_interval_start=rows[start]['start_source_date'], first_crossing=rows[start]['end_source_date'],
                          first_gap_group=rows[start]['gap_group'], first_gap_calendar_days=rows[start]['gap_calendar_days'],
                          crossing_value_php=str(values[start]), crossing_drawdown_pct=float(F(rows[start]['drawdown_percent_exact'])),
                          peak_at_crossing_php=str(peaks[start]),
                          last_flagged_date=rows[end]['end_source_date'], flagged_observations=end-start+1,
                          first_to_last_flag_calendar_days=days(rows[start]['end_source_date'], rows[end]['end_source_date']),
                          threshold_exit=rows[end+1]['end_source_date'] if end+1 < len(rows) else '',
                          status='ended' if end+1 < len(rows) else 'ongoing_at_study_end')
            these_episodes.append(record)
            for horizon in (5, 20):
                complete = start+horizon < len(rows)
                last = min(start+horizon, len(rows)-1)
                future = values[start+1:last+1]
                min_value = min([values[start]] + future)
                terminal = values[last]-values[start] if complete else None
                adverse = values[start]-min_value if complete else None
                outcomes.append(dict(threshold_pct=threshold, episode=n, underwater_period=underwater_ids[start],
                    crossing_date=rows[start]['end_source_date'], horizon_observations=horizon,
                    outcome_status='complete' if complete else 'incomplete_not_in_summary',
                    outcome_end_date=rows[last]['end_source_date'], available_future_observations=last-start,
                    window_calendar_days=days(rows[start]['end_source_date'], rows[last]['end_source_date']),
                    terminal_pnl_php_exact=str(terminal) if complete else '',
                    terminal_pnl_php=float(terminal) if complete else '',
                    worst_additional_loss_php_exact=str(adverse) if complete else '',
                    worst_additional_loss_php=float(adverse) if complete else '',
                    worst_additional_loss_pct_crossing=float(adverse/values[start]*100) if complete else '',
                    lower_at_end=terminal < 0 if complete else '',
                    any_further_decline=adverse > 0 if complete else ''))
        episodes.extend(these_episodes)
        assert sum(x['flagged_observations'] for x in these_episodes) == sum(flags)
        summaries.append(dict(threshold_pct=threshold, new_alerts=len(starts),
            distinct_underwater_periods=len({underwater_ids[s] for s in starts}),
            flagged_observations=sum(flags), total_observations=len(rows),
            flagged_share_pct=sum(flags)/len(rows)*100,
            median_episode_flagged_observations=median(x['flagged_observations'] for x in these_episodes),
            longest_episode_flagged_observations=max(x['flagged_observations'] for x in these_episodes),
            first_crossing=rows[starts[0]]['end_source_date'],
            ongoing_at_study_end=flags[-1]))
    assert [(s['new_alerts'], s['flagged_observations']) for s in summaries if s['threshold_pct']==3] == [(15,733)]
    assert all(a['flagged_observations'] >= b['flagged_observations'] for a,b in zip(summaries,summaries[1:]))
    forward_summary = []
    for threshold in (2,3,4):
        for horizon in (5,20):
            group = [x for x in outcomes if x['threshold_pct']==threshold and x['horizon_observations']==horizon]
            complete = [x for x in group if x['outcome_status']=='complete']
            forward_summary.append(dict(threshold_pct=threshold, horizon_observations=horizon,
                complete_windows=len(complete), incomplete_windows=len(group)-len(complete),
                any_further_decline_count=sum(x['any_further_decline'] for x in complete),
                lower_at_end_count=sum(x['lower_at_end'] for x in complete),
                median_terminal_pnl_php=float(median(F(x['terminal_pnl_php_exact']) for x in complete)),
                median_worst_additional_loss_php=float(median(F(x['worst_additional_loss_php_exact']) for x in complete)),
                max_worst_additional_loss_php=float(max(F(x['worst_additional_loss_php_exact']) for x in complete)),
                min_calendar_days=min(x['window_calendar_days'] for x in complete),
                max_calendar_days=max(x['window_calendar_days'] for x in complete)))
    save_csv('threshold_summary.csv', summaries)
    save_csv('episodes.csv', episodes)
    save_csv('forward_outcomes.csv', outcomes)
    save_csv('forward_summary.csv', forward_summary)
    fig, axes = plt.subplots(1, 2, figsize=(10,4))
    for ax, metric, label in zip(axes, ('new_alerts','flagged_observations'), ('New review alerts','Observations with an active flag')):
        heights = [s[metric] for s in summaries]
        bars = ax.bar(['2%','3%','4%'], heights, color='#386880', width=.55)
        ax.bar_label(bars, padding=3)
        ax.set_title(label)
        ax.set_xlabel('Drawdown threshold from running peak')
        ax.set_ylim(0,max(heights)*1.2)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Historical threshold sensitivity | 2020–September 2026')
    fig.tight_layout()
    fig.savefig(OUT/'threshold_workload.png', dpi=160)
    plt.close(fig)
    assert all(digest(P/name) == sha for name, sha in before.items())
    checks = dict(source_rows=len(rows), exact_peak_and_drawdown_reconciliation='passed',
        original_interval_continuity='passed', episode_counts_reconcile='passed',
        three_percent_existing_result_reproduced='15 episodes; 733 flagged observations',
        nested_flag_membership='passed', forward_outcome_rows=len(outcomes),
        incomplete_windows=sum(x['outcome_status']!='complete' for x in outcomes),
        frozen_var_files_verified=len(manifest), protected_files_unchanged=len(before),
        source_sha256=digest(SOURCE), protected_sha256=before,
        limitation='Exploratory descriptive comparison; dependent windows; no threshold selection or predictive validation.')
    (OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(dict(thresholds=summaries, forward_summary=forward_summary), indent=2))

if __name__ == '__main__':
    run()
