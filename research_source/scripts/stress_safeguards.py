"""Contract-enforced static stress calculations and isolated validated run bundles.

No network requests or database connections. Existing v1 results are read-only.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction as F
from pathlib import Path
import csv
import hashlib
import io
import json
import platform
import uuid

APPROVED_ANCHOR_SHA256='d8104c9d4fd23e221fb4f480a2ca107d796a009b73a9bc63fc836edff51b8867'

class InputError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise InputError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def json_fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

def read_csv(path):
    with Path(path).open(newline='') as stream:
        return list(csv.DictReader(stream))

@dataclass(frozen=True)
class StressConfig:
    usd_position: int = 1_000_000
    hypothetical_percent: tuple = (-5, -3, -1, 1, 3, 5)
    starting_date: str = '2026-09-30'
    starting_rate: str = '62.485'

    def validate(self):
        require(type(self.usd_position) is int and self.usd_position == 1_000_000, 'Contract requires exactly USD1,000,000.')
        require(self.hypothetical_percent == (-5, -3, -1, 1, 3, 5), 'Contract requires the exact six approved percentage shocks and order.')
        require(self.starting_date == '2026-09-30' and self.starting_rate == '62.485', 'Contract starting date/rate changed.')

@dataclass(frozen=True)
class Session:
    root: Path
    anchor: dict
    ledger: list
    ledger_fingerprint: str
    config: StressConfig


def verify_protected(session):
    p, a = session.root, session.anchor
    for rel, expected in a['files'].items():
        require((p/rel).is_file() and sha(p/rel) == expected, 'Approved core input changed or missing: '+rel)
    for rel, expected in a['protected_stress_v1_files'].items():
        require(sha(p/rel) == expected, 'Preserved stress v1 file changed: '+rel)
    require(sha(p/a['original_notebook_archive']) == a['original_notebook_sha256'], 'Original notebook archive changed.')
    manifest = json.loads((p/'reports/var_validation_v1/checksums.json').read_text())
    for rel, expected in manifest.items():
        require(sha(p/'reports/var_validation_v1'/rel) == expected, 'Frozen VaR file mismatch: '+rel)
    return len(manifest)


def prepare_inputs(root, config=StressConfig()):
    config.validate()
    p = Path(root).resolve()
    require(sha(p/'data/reference/stress_approved_inputs_v1.json') == APPROVED_ANCHOR_SHA256, 'Approved-input manifest changed; review before updating its trusted hash.')
    anchor = json.loads((p/'data/reference/stress_approved_inputs_v1.json').read_text())
    ledger = read_csv(p/'data/processed/bsp_usd_php_interval_ledger_v1.csv')
    session = Session(p, anchor, ledger, json_fingerprint(ledger), config)
    verify_protected(session)
    require(len(ledger) == 1647 and len({r['interval_id'] for r in ledger}) == 1647, 'Original ledger coverage/identity mismatch.')
    return session


def exact_return(row):
    return F(row['end_rate_raw']) / F(row['start_rate_raw']) - 1


def choose_historical(rows):
    return min(rows, key=lambda r: (exact_return(r), r['end_source_date'], int(r['interval_order'])))


def select_market(session):
    session.config.validate()
    require(json_fingerprint(session.ledger) == session.ledger_fingerprint, 'In-memory ledger changed.')
    verify_protected(session)
    ledger = session.ledger
    for i, r in enumerate(ledger, 1):
        require(int(r['interval_order']) == i, 'Ledger order mismatch.')
        if i > 1:
            previous = ledger[i-2]
            require(previous['end_source_date'] == r['start_source_date'] and previous['end_rate_raw'] == r['start_rate_raw'], 'Original endpoints are not continuous.')
    latest = max(ledger, key=lambda r: r['end_source_date'])
    historical = choose_historical(ledger)
    require(latest['end_source_date'] == session.config.starting_date and latest['end_rate_raw'] == session.config.starting_rate, 'Starting endpoint differs from contract.')
    require((historical['start_source_date'], historical['end_source_date'], historical['start_rate_raw'], historical['end_rate_raw']) == ('2025-08-04','2025-08-05','58.392','57.514'), 'Historical selected endpoints differ.')
    register = {r['source_date']: r for r in read_csv(session.root/'reports/source_audit_remaining_gap1_v1/all_main_exception_endpoint_register.csv')}
    for side in ('start', 'end'):
        record = register[historical[side+'_source_date']]
        require(record['audit_pass'] == 'earlier_eda', 'Historical endpoint audit evidence status not approved.')
        require(F(record['rate']) == F(historical[side+'_rate_raw']) == F(record['bulletin_rate']), 'Audit rate mismatch.')
        require(record['source_row'] == historical[side+'_source_row'], 'Audit source-row mismatch.')
        evidence = session.root/'reports/stress_testing_v1/evidence'/('04Aug2025.pdf' if side == 'start' else '05Aug2025.pdf')
        require(sha(evidence) == record['pdf_sha256'], 'Archived endpoint bulletin mismatch.')
    import openpyxl
    workbook = session.root/session.anchor['workbook_path']
    require(sha(workbook) == latest['snapshot_sha256'], 'Workbook identity differs from ledger snapshot.')
    wb = openpyxl.load_workbook(workbook, read_only=True, data_only=True)
    try:
        ws = wb['peso cross daily']
        endpoints = [(latest['end_source_date'],latest['end_source_row'],latest['end_rate_raw'])] + [(historical[s+'_source_date'],historical[s+'_source_row'],historical[s+'_rate_raw']) for s in ('start','end')]
        for date, row, rate in endpoints:
            cell_date, cell_rate = next(ws.iter_rows(min_row=int(row),max_row=int(row),max_col=2,values_only=True))
            require(str(cell_date)[:10] == date and F(str(cell_rate)) == F(rate), 'Pinned workbook cell mismatch.')
    finally:
        wb.close()
    return {'starting_source_date':latest['end_source_date'],'starting_rate_raw':latest['end_rate_raw'],
            'historical_interval':dict(historical),'historical_return_numerator':exact_return(historical).numerator,
            'historical_return_denominator':exact_return(historical).denominator}


def assess_bpi(session):
    """Withhold this case on any expected evidence/metadata failure; USD still runs."""
    a, p = session.anchor, session.root
    try:
        meta_path = p/a['bpi_metadata_path']
        meta = json.loads(meta_path.read_text())
        expected = {'entity':'BPI Group consolidated, not Parent Bank','reporting_date':'2025-12-31',
                    'units':'millions of PHP; USD instruments in peso equivalent',
                    'assets_million_php':418686,'liabilities_million_php':417872,'signed_net_million_php':814,
                    'definition':'Positive net on-balance-sheet USD position; not regulatory net open position or total economic FX risk',
                    'official_download_matches_previously_inspected_attachment':True,
                    'path':a['bpi_pdf_path'],'sha256':a['bpi_pdf_sha256']}
        for field, value in expected.items():
            require(meta.get(field) == value, 'BPI field not approved: '+field)
        require(meta['comparator'] == {'shock_percent':'1.78','effect_million_php':'14','rounding_tolerance_php':500000}, 'BPI comparator metadata changed.')
        require(sha(meta_path) == a['bpi_metadata_sha256'], 'BPI provenance bytes differ from approved evidence.')
        require(sha(p/meta['path']) == a['bpi_pdf_sha256'], 'BPI PDF differs from officially matched source.')
        exposure = F(str(meta['signed_net_million_php'])) * 1_000_000
        require(meta['assets_million_php']-meta['liabilities_million_php'] == meta['signed_net_million_php'], 'BPI signed net does not reconcile.')
        exact = exposure * F(meta['comparator']['shock_percent']) / 100
        disclosed = F(meta['comparator']['effect_million_php']) * 1_000_000
        require(exact == 14_489_200 and abs(exact-disclosed) <= F(meta['comparator']['rounding_tolerance_php']), 'BPI rounded comparator fails.')
        return {'eligible':True,'reason':None,'exposure_php':str(exposure),'metadata':meta,
                'comparator_exact_php':str(exact),'comparator_difference_php':str(exact-disclosed),
                'publication_date':'not established; no reporting-date availability claim'}
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {'eligible':False,'reason':str(error),'exposure_php':None,
                'publication_date':'not established; no reporting-date availability claim'}


def scenario_record(case, date, base, label, shock, kind, rate, historical):
    pnl = base*shock
    shocked = rate*(1+shock) if case == 'Hypothetical USD1m' else None
    ending = base+pnl if shocked is not None else None
    return {'case':case,'valuation_or_disclosure_date':date,'scenario':label,'scenario_type':kind,
            'shock_percent':float(shock*100),'shock_numerator':shock.numerator,'shock_denominator':shock.denominator,
            'base_value_or_exposure_php':float(base),'stressed_rate_php_per_usd':float(shocked) if shocked is not None else '',
            'ending_position_value_php':float(ending) if ending is not None else '',
            'ending_value_numerator':ending.numerator if ending is not None else '',
            'ending_value_denominator':ending.denominator if ending is not None else '',
            'pnl_php':float(pnl),'signed_loss_php':float(-pnl),'pnl_numerator':pnl.numerator,'pnl_denominator':pnl.denominator,
            'historical_interval_id':historical['interval_id'] if kind == 'historical replay' else '',
            'historical_gap_calendar_days':historical['gap_calendar_days'] if kind == 'historical replay' else ''}


def calculate(session, selection, bpi):
    session.config.validate()
    require(json_fingerprint(session.ledger) == session.ledger_fingerprint, 'In-memory ledger changed.')
    require(selection == select_market(session), 'Selection changed after verification.')
    require(bpi == assess_bpi(session), 'BPI status changed or overridden; reassess evidence.')
    q, rate = session.config.usd_position, F(selection['starting_rate_raw'])
    base, historical = q*rate, selection['historical_interval']
    scenarios = [(f'Hypothetical {n:+d}%', F(n,100),'hypothetical') for n in session.config.hypothetical_percent]
    scenarios += [('Historical decline: 04-05 Aug 2025',exact_return(historical),'historical replay')]
    cases = [('Hypothetical USD1m',session.config.starting_date,base)]
    if bpi['eligible']:
        cases += [('BPI Group static illustration','2025-12-31',F(bpi['exposure_php']))]
    records, controls = [], []
    for case, date, case_base in cases:
        for label, shock, kind in scenarios:
            rec = scenario_record(case,date,case_base,label,shock,kind,rate,historical)
            result = F(rec['pnl_numerator'],rec['pnl_denominator'])
            if case == 'Hypothetical USD1m':
                shocked = rate*(1+shock)
                require(shocked > 0 and q*(shocked-rate) == result, 'Direct revaluation mismatch.')
                if kind == 'hypothetical':
                    independent = Decimal(q)*Decimal(selection['starting_rate_raw'])*Decimal(shock.numerator)/Decimal(shock.denominator)
                    require(F(independent) == result, 'Decimal check failed.')
            require(result/case_base == shock, 'Proportionality mismatch.')
            records.append(rec)
        # Zero shock follows exactly the same record generation and export pipeline.
        controls.append(scenario_record(case,date,case_base,'Control 0%',F(0),'control',rate,historical))
    model = {'records':records,'controls':controls,'selection':selection,'bpi':bpi}
    validate_model(session,model)
    return model


def validate_model(session, model):
    session.config.validate()
    rows, controls = model['records'], model['controls']
    cases = ['Hypothetical USD1m'] + (['BPI Group static illustration'] if model['bpi']['eligible'] else [])
    require(len(rows) == 7*len(cases) and len(controls) == len(cases), 'Missing/extra scenario or control rows.')
    expected_shocks = [F(n,100) for n in (-5,-3,-1,1,3,5)] + [F(-439,29196)]
    expected_labels = [f'Hypothetical {n:+d}%' for n in (-5,-3,-1,1,3,5)] + ['Historical decline: 04-05 Aug 2025']
    for case in cases:
        group = [r for r in rows if r['case']==case]
        require([F(r['shock_numerator'],r['shock_denominator']) for r in group] == expected_shocks, 'Scenario membership/order changed.')
        require([r['scenario'] for r in group] == expected_labels, 'Scenario labels differ from values.')
        base = F(62_485_000 if case=='Hypothetical USD1m' else 814_000_000)
        for r, shock in zip(group,expected_shocks):
            require(F(str(r['base_value_or_exposure_php'])) == base, 'Case base changed.')
            require(F(r['pnl_numerator'],r['pnl_denominator']) == base*shock, 'Exact P&L changed.')
            require(r['signed_loss_php'] == -r['pnl_php'], 'Loss sign mismatch.')
            require(r['shock_percent'] == float(shock*100), 'Displayed shock changed.')
            require(r['pnl_php'] == float(base*shock), 'Displayed P&L changed.')
            if case=='Hypothetical USD1m':
                end=base*(1+shock)
                require(F(r['ending_value_numerator'],r['ending_value_denominator']) == end, 'Ending valuation changed.')
                require(r['ending_position_value_php']==float(end) and r['stressed_rate_php_per_usd']==float(F('62.485')*(1+shock)), 'Ending value/rate display changed.')
    # Literal controls catch same-input consistency tests that could all share a wrong quantity.
    usd = {r['scenario']:r for r in rows if r['case']=='Hypothetical USD1m'}
    require(usd['Hypothetical -1%']['pnl_php'] == -624850 and usd['Hypothetical -5%']['pnl_php'] == -3124250, 'USD known answer failed.')
    require(usd['Hypothetical -1%']['stressed_rate_php_per_usd'] == 61.86015, 'Known shocked rate failed.')
    require([r['case'] for r in controls] == cases, 'Control case coverage differs.')
    for r in controls:
        require(r['scenario']=='Control 0%' and r['pnl_php']==0 and r['shock_numerator']==0, 'Zero output control failed.')
        if r['case']=='Hypothetical USD1m':require(r['ending_position_value_php']==62_485_000, 'Zero ending value failed.')
    historical=model['selection']['historical_interval']
    require(1_000_000*(F(historical['end_rate_raw'])-F(historical['start_rate_raw'])) == -878000, 'Original-interval hypothetical valuation known answer failed.')
    if model['bpi']['eligible']:
        require(next(r['pnl_php'] for r in rows if r['case']=='BPI Group static illustration' and r['scenario']=='Hypothetical +1%') == 8140000, 'BPI known answer failed.')
    return True


def make_chart(model):
    validate_cases = sorted({r['case'] for r in model['records']},key=lambda c:c!='Hypothetical USD1m')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1,len(validate_cases),figsize=(7*len(validate_cases),5.8),squeeze=False)
    for ax, case in zip(axes[0],validate_cases):
        rows = [r for r in model['records'] if r['case']==case]
        values=[r['pnl_php']/1_000_000 for r in rows]
        # Labels come from the validated records, never a parallel hardcoded list.
        labels=[r['scenario'].replace('Hypothetical ','').replace(': ',':\n') for r in rows]
        bars=ax.barh(range(len(rows)),values,color=['#a6323b' if v<0 else '#146b70' for v in values])
        ax.set_yticks(range(len(rows)),labels);ax.invert_yaxis();ax.axvline(0,color='#596873',lw=.8)
        date=rows[0]['valuation_or_disclosure_date'];ax.set_title(case+' | '+date,fontsize=11)
        ax.set_xlabel('Hypothetical P&L (PHP millions); separate panel scales');ax.margins(x=.32);ax.grid(axis='x',alpha=.15)
        for bar,value in zip(bars,values):
            ax.annotate(f'{value:+.3f}',(value,bar.get_y()+bar.get_height()/2),xytext=(4 if value>=0 else -4,0),textcoords='offset points',ha='left' if value>=0 else 'right',va='center',fontsize=9)
    fig.suptitle('Specified FX shocks · fixed, dated exposure illustrations')
    fig.text(.5,.015,'No scenario probability or forecast horizon assigned. Historical percentage replay is not an actual bank loss.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.07,1,.94))
    return fig


def write_csv(path, rows):
    with Path(path).open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def verify_run(path):
    p=Path(path)
    require(not p.name.startswith('.incomplete-'), 'Unpublished run is not accepted.')
    success=json.loads((p/'SUCCESS.json').read_text())
    require(success['status']=='validated' and sha(p/'checksums.json')==success['manifest_sha256'], 'Invalid success record.')
    for name,expected in json.loads((p/'checksums.json').read_text()).items():
        require(sha(p/name)==expected,'Run output mismatch: '+name)
    return success


def publish_run(session, model, *, _fail_at=None):
    """Stage, validate, then atomically publish a unique directory. Never overwrite v1."""
    validate_model(session,model)
    require(model['selection']==select_market(session), 'Market selection changed before export.')
    require(model['bpi']==assess_bpi(session), 'BPI evidence changed before export.')
    verify_protected(session)
    runs=session.root/'reports/stress_runs';runs.mkdir(exist_ok=True)
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'-'+uuid.uuid4().hex[:8]
    stage=runs/('.incomplete-'+run_id);final=runs/run_id;stage.mkdir()
    def fail(point):
        if _fail_at==point:raise RuntimeError('Synthetic export failure at '+point)
    try:
        fig=make_chart(model)
        try:fig.savefig(stage/'stress_comparison.png',dpi=160,bbox_inches='tight')
        finally:
            import matplotlib.pyplot as plt
            plt.close(fig)
        fail('after_chart')
        write_csv(stage/'scenario_results.csv',model['records']);write_csv(stage/'control_results.csv',model['controls'])
        cases=list(dict.fromkeys(r['case'] for r in model['records']))
        comparison=[]
        for first in [r for r in model['records'] if r['case']=='Hypothetical USD1m']:
            comparison.append({'scenario':first['scenario'],'shock_percent':first['shock_percent'],**{case:next(r['pnl_php'] for r in model['records'] if r['case']==case and r['scenario']==first['scenario']) for case in cases}})
        write_csv(stage/'comparison_table.csv',comparison)
        fail('after_csv')
        def dump(name,value):(stage/name).write_text(json.dumps(value,indent=2)+'\n')
        dump('selection.json',model['selection']);dump('bpi_status.json',model['bpi'])
        dump('chart_labels.json',[{'case':c,'scenario_labels':[r['scenario'] for r in model['records'] if r['case']==c]} for c in cases])
        dump('settings.json',{'run_id':run_id,'usd_position':session.config.usd_position,'hypothetical_percent':session.config.hypothetical_percent,
             'starting_date':session.config.starting_date,'starting_rate_raw':session.config.starting_rate,
             'probability':None,'forecast_horizon':None,'python':platform.python_version(),
             'approved_inputs':session.anchor,'approved_inputs_sha256':sha(session.root/'data/reference/stress_approved_inputs_v1.json'),
             'implementation_sha256':sha(Path(__file__)),'notebook_sha256_at_run':sha(session.root/'notebooks/03_stress_testing.ipynb')})
        # Re-read exported exact records before granting success.
        rows=read_csv(stage/'scenario_results.csv');controls=read_csv(stage/'control_results.csv')
        require(len(rows)==len(model['records']) and len(controls)==len(model['controls']), 'Export coverage mismatch.')
        for r,expected in zip(rows,model['records']):
            require(F(r['pnl_numerator'])/F(r['pnl_denominator'])==F(expected['pnl_numerator'],expected['pnl_denominator']), 'Exact export mismatch.')
        count=verify_protected(session)
        dump('checks.json',{'status':'passed','scenario_rows':len(rows),'zero_control_rows':len(controls),'bpi_eligible':model['bpi']['eligible'],
             'bpi_exclusion_reason':model['bpi']['reason'],'known_answers':'passed','three_pinned_workbook_cells':'passed',
             'historical_audit_status':'approved earlier_eda evidence pinned and checked','frozen_var_files_unchanged':count,
             'database_and_existing_stress_bundle_unchanged':True,'scope':'static arithmetic/provenance checks; not financial-method certification'})
        (stage/'FINDINGS.md').write_text('# Static stress run\n\nUSD1 million starts at PHP62.485 million on30 September2026. Six approved shocks and one historical percentage replay; no probability or forecast horizon. Original-interval hypothetical USD1m valuation loss: PHP878,000, distinct from the replay on the September2026 baseline.\n\nBPI: '+('eligible static supporting illustration; original publication date not established.' if model['bpi']['eligible'] else 'WITHHELD: '+str(model['bpi']['reason']))+'\n\nExisting v1 bundle preserved. Exact ending USD valuations, P&Ls and zero controls are exported. BPI exposure is already in pesos; no total-bank loss or risk appetite is inferred.\n')
        fail('before_manifest')
        dump('checksums.json',{f.name:sha(f) for f in sorted(stage.iterdir()) if f.is_file()})
        for name,expected in json.loads((stage/'checksums.json').read_text()).items():require(sha(stage/name)==expected,'Output changed during validation.')
        fail('before_success')
        verify_protected(session)
        dump('SUCCESS.json',{'status':'validated','run_id':run_id,'manifest_sha256':sha(stage/'checksums.json'),'validated_at':datetime.now(timezone.utc).isoformat()})
        require(not final.exists(),'Run ID collision; refusing overwrite.')
        stage.rename(final)
    except Exception as error:
        if stage.exists():
            (stage/'SUCCESS.json').unlink(missing_ok=True)
            (stage/'FAILURE.json').write_text(json.dumps({'status':'failed_unpublished','error':str(error)},indent=2)+'\n')
        raise
    verify_run(final)
    return final
