import json,sys
sys.path.insert(0,'/workspace/sb/mt')
from mtlib import run,save,t2s,s2tw
U=json.load(open('/workspace/sb/repo/data/official_units.json'))['topics']
n=lambda s:s.replace('\u3000',' ').replace('\n',' ').strip()
ja=sorted({n(t[f]) for t in U if t['origin']==['JP'] for f in ('name','description')})
zh=sorted({n(t[f]) for t in U if t['origin']==['CN'] for f in ('name','description','domain')})
pt=sorted({n(t[f]) for t in U if t['kind']=='objetivo-ei' for f in ('name','description','domain')})
en1=run(ja,'ja','en'); en2=run(zh,'zh','en'); en3=run(pt,'pt','en')
ens=sorted(set(en1.values())|set(en2.values())|set(en3.values()))
run(ens,'en','pt'); run(ens,'en','ja'); zt=run(ens,'en','zt')
run(sorted({t2s.convert(v) for v in zt.values()}),'zh','en')
save(); print('FIM2',flush=True)
