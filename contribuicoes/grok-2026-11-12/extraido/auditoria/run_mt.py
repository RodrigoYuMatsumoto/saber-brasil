"""Pipeline de tradução automática com conferência nova (Grok, 2026-11-12).
Fontes: textos pt-BR/en do saber-brasil (commit e66772d). Reaproveita o cache Grok anterior
somente como ponto de partida; TODA saída passa por (1) heurísticas estruturais e (2) retrotradução
para inglês com chrF; reprovadas ficam sem tradução (a interface mostra o original)."""
import json,sys,os,re,time
sys.path.insert(0,'/workspace/sb/mt'); sys.path.insert(0,'/workspace/sb/audit')
from mt import translate
from qa_trad import check
from opencc import OpenCC
t2s=OpenCC('t2s'); s2tw=OpenCC('s2twp')
R='/workspace/sb/repo/data/'
OUT='/workspace/sb/mt/cache.json'
C=json.load(open(OUT)) if os.path.exists(OUT) else {}
old=json.load(open('/workspace/marble/grok/data/cache/traducoes-i18n.json'))
oldjp=json.load(open('/workspace/marble/grok/data/cache/traducoes-jp-cn.json'))
def seed(key,d):
  m=C.setdefault(key,{})
  for k,v in d.items():
    if k not in m: m[k]={'t':v,'via':'cache-grok-anterior'}
seed('pt>en',old['pt>en']); seed('en>ja',old['en>ja']); seed('en>zt',old['en>zt'])
seed('ja>en',oldjp['ja>en']); seed('zh>en',oldjp['zh>en']); seed('en>pt',oldjp['en>pt'])
def save(): json.dump(C,open(OUT+'.tmp','w'),ensure_ascii=False); os.replace(OUT+'.tmp',OUT)
def run(texts,src,tgt):
  key=f'{src}>{tgt}'; m=C.setdefault(key,{})
  todo=sorted({t for t in texts if t and t not in m})
  print(time.strftime('%H:%M:%S'),key,'novos',len(todo),'de',len(set(texts)),flush=True)
  for k in range(0,len(todo),400):
    ch=todo[k:k+400]
    for a,b in zip(ch,translate(ch,src if src!='zt' else 'zh',tgt)):
      if tgt=='zt': b=s2tw.convert(b)
      m[a]={'t':b,'via':'argos-2026-11-12'}
    save(); print(time.strftime('%H:%M:%S'),key,k+len(ch),'/',len(todo),flush=True)
  return {t:m[t]['t'] for t in texts if t}
br=json.load(open(R+'brazil_topics.json'))['topics']; it=json.load(open(R+'international.json'))['topics']
tr=json.load(open(R+'translations.json'))['topics']
pt_texts=set()
for x in br:
  for f in ('name','description','domain'): pt_texts.add(x[f])
pt_texts=sorted(t for t in pt_texts if t)
en_br=run(pt_texts,'pt','en')
en_texts=set(en_br.values())
for x in it:
  for f in ('originalName','originalDescription','domain'): 
    v=x.get(f) or ''; en_texts.add(v)
for x in it: en_texts.add(tr.get(x['id'],{}).get('en',{}).get('domain',''))
en_texts=sorted(t for t in en_texts if t)
ja=run(en_texts,'en','ja'); zt=run(en_texts,'en','zt')
# retrotradução para conferência
run(sorted(set(ja.values())),'ja','en')
zh_s={v:t2s.convert(v) for v in zt.values()}
run(sorted(set(zh_s.values())),'zh','en')
save(); print('FIM',flush=True)
