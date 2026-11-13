"""Check the candidate's hashes, local HTML links and obvious private artifacts."""
from pathlib import Path
import hashlib,json,re
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
    def __init__(self):super().__init__();self.targets=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and 'href'in a:self.targets.append(a['href'])
        if tag=='img' and 'src'in a:self.targets.append(a['src'])
def main():
    manifest=json.loads((ROOT/'PACKAGE_MANIFEST.json').read_text())
    for name,expected in manifest.items():
        path=ROOT/name
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise RuntimeError('Package file changed: '+name)
    local_links=0
    for path in ROOT.rglob('*.html'):
        parser=Links();parser.feed(path.read_text())
        for ref in parser.targets:
            if ref.startswith(('https:','http:','#','mailto:','data:','blob:')):continue
            target=(path.parent/ref.split('#')[0]).resolve()
            if not target.is_relative_to(ROOT) or not target.is_file():raise RuntimeError('Missing/outside local link: '+str(path.relative_to(ROOT))+' -> '+ref)
            local_links+=1
    for path in ROOT.rglob('*'):
        if not path.is_file() or '.local-runs' in path.parts:continue
        if path.suffix.lower() in {'.xlsx','.xls','.pdf','.duckdb','.pem','.key'} or path.name.startswith('historical-risk-review-notes'):raise RuntimeError('Unexpected restricted file: '+str(path.relative_to(ROOT)))
        if path.suffix in {'.md','.py','.json','.csv','.html','.ipynb','.cjs'}:
            text=path.read_text()
            # Match actual machine-specific prefixes, not descriptions of this check.
            if re.search(('/'+'Users'+r'/[^/\s]+/|'+'/'+'var'+r'/folders/[A-Za-z0-9_]+/|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}'),text):raise RuntimeError('Potential private path/token: '+str(path.relative_to(ROOT)))
    print(json.dumps({'status':'passed','manifest_files':len(manifest),'local_html_links_checked':local_links,'private_artifact_scan':'passed bounded pattern scan; owner review still required','publishing_performed':False},indent=2))
if __name__=='__main__':main()
