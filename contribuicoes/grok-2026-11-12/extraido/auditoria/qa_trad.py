import re,collections as C,unicodedata
KANA=re.compile(r'[\u3040-\u30ff]'); HAN=re.compile(r'[\u4e00-\u9fff]'); LAT=re.compile(r'[A-Za-zÀ-ÿ]')
SIMP=set('这们说来时为会经发现对开关门问间东车长马鸟鱼书买卖读写学习认识数计语话请让从众体办动务图国园圆团块场声处备复够头奖实宝宽导层岁带帮广应庆库张弹归当录总战报担拥择换挥据摄数断无旧显术权条极构标样树桥检欢气汉没济测浅热爱环现电画畅确础离种积稳简类纪约级线练组细终经结给统继续维综网罗职联节药虑见观规视览觉计订认讨让训记讲许论设访证评识诉词译试诗话该详语误说请读课谁调谈谢贝负贡财责贫货质购贯费资赛赵车转轮软轻较辅辈输边达过运还这进远连迟适选递遗邮释针铁银错键长门问间闻队阳阴际陆陈险随隐难雾静须顺顾预领题风飞饭馆驾验马鱼鸟鸡麦黄齐齿龙')
EN_SW=set('the and of to in is that for with as are be on by an this or from which'.split())
PT_SW=set('de do da que em para com os as um uma no na dos das ao se por é e'.split())
def words(s): return re.findall(r"[A-Za-zÀ-ÿ]+",s.lower())
def check(src,tgt,lang):
  r=[]
  if not tgt or not tgt.strip(): return ['vazia']
  s=src.strip(); t=tgt.strip()
  if t==s and len(s)>12: r.append('igual-ao-original')
  ls,lt=len(s),len(t)
  cjk_t=lang in('ja','zh-Hant'); cjk_s=bool(HAN.search(s) or KANA.search(s))
  ratio=lt/max(ls,1)
  lo,hi=(0.5,2.5)
  if cjk_t and not cjk_s: lo,hi=0.12,1.2
  elif cjk_s and not cjk_t: lo,hi=0.9,8
  if ls>=30 and ratio<lo: r.append('curta-demais')
  if ls>=10 and ratio>hi: r.append('longa-demais')
  # repetição
  toks=words(t) if not cjk_t else list(re.sub(r'\W','',t))
  if len(toks)>=8:
    c=C.Counter(toks); w,n=c.most_common(1)[0]
    if n>=4 and n/len(toks)>(0.25 if not cjk_t else 0.18) and w not in PT_SW|EN_SW: r.append('repeticao-dominante')
  if re.search(r'(\b\w+\b(?:\W+\b\w+\b){0,3})(?:\W+\1){2,}',t) or re.search(r'(.{2,12}?)\1{3,}',t): r.append('sequencia-repetitiva')
  # idioma
  if lang=='ja' and not KANA.search(t) and lt>8: r.append('idioma-incorreto(sem-kana)')
  if lang=='zh-Hant':
    if KANA.search(t): r.append('idioma-incorreto(kana-em-chines)')
    if sum(ch in SIMP for ch in t)>=2: r.append('chines-simplificado')
    if not HAN.search(t): r.append('idioma-incorreto(sem-han)')
  if lang in('pt-BR','en'):
    if HAN.search(t) or KANA.search(t): r.append('idioma-incorreto(cjk)')
    ws=words(t)
    if len(ws)>=6:
      en=sum(x in EN_SW for x in ws); pt=sum(x in PT_SW for x in ws)
      if lang=='pt-BR' and en>pt and en>=2: r.append('idioma-incorreto(ingles)')
      if lang=='en' and pt>en and pt>=2: r.append('idioma-incorreto(portugues)')
  return r
