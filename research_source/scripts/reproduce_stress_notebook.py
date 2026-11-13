"""Run the safeguarded notebook in a fresh project kernel; preserve original outputs."""
from pathlib import Path
import json, os, re, sys, hashlib, traceback, tempfile
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

P=Path(__file__).resolve().parents[1]
source=P/'notebooks/03_stress_testing.ipynb'
nb=nbformat.read(source,as_version=4)
for cell in nb.cells:
    if cell.cell_type=='code':cell.outputs=[];cell.execution_count=None
os.environ['IPYTHONDIR']='/private/tmp/fx-stress-ipython'
os.environ['JUPYTER_RUNTIME_DIR']='/private/tmp/fx-stress-jupyter'
Path(os.environ['IPYTHONDIR']).mkdir(exist_ok=True)
Path(os.environ['JUPYTER_RUNTIME_DIR']).mkdir(exist_ok=True)
km=KernelManager(kernel_name='python3',connection_file=str(Path(os.environ['JUPYTER_RUNTIME_DIR'])/'kernel-stress.json'))
km.kernel_spec.argv=[str(P/'.venv/bin/python'),'-m','ipykernel_launcher','-f','{connection_file}']
client=NotebookClient(nb,km=km,resources={'metadata':{'path':str(P)}},timeout=180,allow_errors=False)
warning=None
try:
    client.execute(env={**os.environ,'MPLBACKEND':'Agg','MPLCONFIGDIR':'/private/tmp/fx-threshold-mpl'})
except Exception as error:
    warning=repr(error)
    print(traceback.format_exc())
code=[c for c in nb.cells if c.cell_type=='code']
errors=[o for c in code for o in c.outputs if o.output_type=='error']
stdout='\n'.join(o.get('text','') for c in code for o in c.outputs if o.output_type=='stream')
complete=all(c.execution_count is not None for c in code) and not errors and 'Status: validated' in stdout
record={'fresh_project_kernel_completed':complete,'code_cells':len(code),'cell_errors':len(errors),'execution_warning':warning,'scope':'fresh kernel plus exact export reconciliation; not operational risk certification'}
if complete:
    nbformat.write(nb,source)
    match=re.search(r'Validated run: (.+)',stdout)
    record['validated_run_path']=match.group(1).strip()
    sys.path.insert(0,str(P/'scripts'))
    import stress_safeguards as stress
    run=Path(record['validated_run_path']);stress.verify_run(run)
    new=stress.read_csv(run/'scenario_results.csv');old=stress.read_csv(P/'reports/stress_testing_v1/scenario_results.csv')
    from fractions import Fraction as F
    lookup={(r['case'],r['scenario']):r for r in new}
    assert len(new)==len(old)==14
    for r in old:
        other=lookup[r['case'],r['scenario']]
        assert F(r['pnl_numerator'])/F(r['pnl_denominator'])==F(other['pnl_numerator'])/F(other['pnl_denominator'])
    record['existing_exact_scenarios_reconciled']=14
    record['notebook_sha256_after_saving']=hashlib.sha256(source.read_bytes()).hexdigest()
    out=P/'reports/stress_safeguards_reproduction_20261111.json'
    out.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))
else:
    print(json.dumps(record,indent=2));raise RuntimeError('Fresh-kernel notebook did not complete; primary notebook outputs not overwritten.')
