import json,sys,re,time,hashlib,collections as Co
sys.path.insert(0,'/workspace/sb/mt'); sys.path.insert(0,'/workspace/sb/audit')
from chrf import chrf; from qa_trad import check
from opencc import OpenCC; t2s=OpenCC('t2s'); S2TW=OpenCC('s2twp')
R='/workspace/sb/repo/data/'
C=json.load(open('/workspace/sb/mt/cache.json'))
TH=0.5
def g(k,s):
  v=C.get(k,{}).get(s); return (v['t'] if isinstance(v,dict) else v) if v is not None else None
n=lambda s:(s or '').replace('\u3000',' ').replace('\n',' ').strip()
END=re.compile(r'[,，、;；:：]\s*$|\.\.\.$|…$')
def trunc(src,tgt): return bool(END.search(tgt)) and not END.search(src)
from qa_trad import SIMP
def extra(src,tgt,lang):
  r=[]
  if ('\u2047' in tgt or '??' in tgt) and not ('?' in src): r.append('token-desconhecido')
  if lang in ('ja','zh-Hant') and __import__('re').search(r'(.{2,4})(?:.{0,2}\1){2,}',tgt): r.append('repeticao-cjk')
  if lang=='zh-Hant' and any(ch in SIMP for ch in tgt): r.append('chines-simplificado(1+)')
  return r
stats=Co.Counter(); reasons=Co.Counter()
def acc(lang,ok,why):
  stats[(lang,ok)]+=1
  for w in why: reasons[(lang,w)]+=1
def to_en(src,sl):
  e=g(f'{sl}>en',n(src)); 
  if e is None: return None,['sem-saida']
  return e, check(n(src),e,'en')+extra(n(src),e,'en')
def from_en(en,lang):
  if lang=='pt-BR':
    o=g('en>pt',en); 
    if o is None: return None,['sem-saida'],None
    return o, check(en,o,'pt-BR')+extra(en,o,'pt-BR')+(['truncada'] if trunc(en,o) else []), None
  if lang=='ja':
    o=g('en>ja',en)
    if o is None: return None,['sem-saida'],None
    b=g('ja>en',o); sc=chrf(b,en) if b else 0
  else:
    o=g('en>zt',en)
    if o is None: return None,['sem-saida'],None
    o=S2TW.convert(o)  # normaliza resíduos simplificados do modelo zt
    b=g('zh>en',t2s.convert(o)); sc=chrf(b,en) if b else 0
  why=check(en,o,lang)+extra(en,o,lang)+(['truncada'] if trunc(en,o) else [])
  if sc<TH and len(en)>=8: why.append(f'retrotraducao-chrF<{TH}')
  return o,why,round(sc,3)
out={}
def put(tid,lang,field,text,meta):
  out.setdefault(tid,{}).setdefault(lang,{'fields':{}})['fields'][field]={'text':text,**meta}
def process(tid,srclang,fields,targets):
  for f,src in fields.items():
    if not src: continue
    if srclang=='en': en,w0=n(src),[]
    else: en,w0=to_en(src,{'pt-BR':'pt','ja':'ja','zh':'zh'}[srclang])
    if 'en' in targets:
      ok=en is not None and not w0; acc('en',ok,w0)
      if ok: put(tid,'en',f,en,{'via':f'{srclang}>en','qa':'heuristica-aprovada'})
    if en is None or w0: 
      for L in targets:
        if L!='en': acc(L,False,['pivo-ingles-reprovado'])
      continue
    for L in targets:
      if L=='en': continue
      o,why,sc=from_en(en,L); ok=o is not None and not why; acc(L,ok,why)
      if ok: put(tid,L,f,o,{'via':f'{srclang}>en>{L}','qa':'heuristica-aprovada'+('' if sc is None else ' + retrotraducao'),**({} if sc is None else {'chrF':sc})})
br=json.load(open(R+'brazil_topics.json'))['topics']; it=json.load(open(R+'international.json'))['topics']
tr=json.load(open(R+'translations.json'))['topics']; ou=json.load(open(R+'official_units.json'))['topics']
for x in br: process(x['id'],'pt-BR',{f:x.get(f) for f in('name','description','domain')},['en','ja','zh-Hant'])
for x in it: process(x['id'],'en',{'name':x.get('originalName'),'description':x.get('originalDescription'),'domain':x.get('domain')},['ja','zh-Hant'])
for x in ou:
  if x['origin']==['JP']: process(x['id'],'ja',{f:x.get(f) for f in('name','description')},['en','pt-BR','zh-Hant'])
  elif x['origin']==['CN']: process(x['id'],'zh',{f:x.get(f) for f in('name','description','domain')},['en','pt-BR','ja'])
  else: process(x['id'],'pt-BR',{f:x.get(f) for f in('name','description','domain')},['en','ja','zh-Hant'])
# zh-Hant da camada chinesa: conversão OpenCC do original (não é tradução)
from opencc import OpenCC as O2; s2tw=O2('s2twp')
for x in ou:
  if x['origin']==['CN']:
    for f in ('name','description','domain'):
      if x.get(f): put(x['id'],'zh-Hant',f,s2tw.convert(x[f]),{'via':'OpenCC s2twp (conversão de escrita, não tradução)','qa':'conversao-de-caracteres'}); stats[('zh-Hant(opencc)',True)]+=1
topics={}
for tid,langs in out.items():
  for L,rec in langs.items():
    d={k:v['text'] for k,v in rec['fields'].items()}
    d['_automatic']=True; d['_provenance']={k:{kk:vv for kk,vv in v.items() if kk!='text'} for k,v in rec['fields'].items()}
    topics.setdefault(tid,{})[L]=d
meta={'lang':'pt-BR','author':'Rodrigo Yú Matsumoto OAB/PE nº 1.338-B','manager':'Rodrigo Yú Matsumoto OAB/PE nº 1.338-B','keywords':'Rodrigo Yú Matsumoto OAB/PE nº 1.338-B',
 'title':'Traduções automáticas rotuladas (auditoria Grok 2026-11-12)',
 'subject':'Traduções automáticas aprovadas por heurística e retrotradução; não revisadas por humano',
 'generatedAt':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'engine':'Argos Translate (OPUS-MT, CTranslate2) local no box; pivô inglês; zh-Hant normalizado com OpenCC s2twp',
 'gate':{'heuristicas':'vazia, igual ao original, proporção de tamanho, repetição, idioma incorreto, chinês simplificado, truncamento','retrotraducao':f'chrF (n=4, beta=2) da retrotradução para o inglês >= {TH} para ja e zh-Hant'},
 'notice':'Tradução automática não revisada. Reprovados ficam sem tradução e a interface mostra o texto original. Não substitui textos oficiais.',
 'stats':{f'{k[0]}|{"aprovado" if k[1] else "reprovado"}':v for k,v in sorted(stats.items())},
 'reasons':{f'{k[0]}|{k[1]}':v for k,v in reasons.most_common()}}
text=json.dumps({'metadata':meta,'topics':topics},ensure_ascii=False,indent=1)
for ch in ('\u2013','\u2014'): text=text.replace(ch,'-')
open(R+'translations_machine.json','w').write(text)
print(json.dumps(meta['stats'],ensure_ascii=False,indent=0)); print(reasons.most_common(25))
