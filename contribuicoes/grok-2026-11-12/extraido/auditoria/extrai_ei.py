import pymupdf as fitz,re,json,sys
def extract(path,pages,pat):
  d=fitz.open(path); out={}
  for pno in pages:
    p=d[pno]; words=p.get_text('words')
    codes=[w for w in words if re.fullmatch(r'\(?'+pat+r'\)?[.,;]?',w[4])]
    xs=[]
    for x0 in sorted(c[0] for c in codes):
      if not xs or x0-xs[-1]>40: xs.append(x0)
    bounds=[]
    for i,x in enumerate(xs): bounds.append((x-8, (xs[i+1]-8) if i+1<len(xs) else p.rect.width))
    for c in codes:
      b=[bb for bb in bounds if bb[0]<=c[0]<bb[1]][0]
      below=[x for x in codes if b[0]<=x[0]<b[1] and x[1]>c[1]+2]
      ylim=min([x[1] for x in below],default=1e9)
      ws=[w for w in words if b[0]<=w[0]<b[1] and w[1]>=c[1]-2 and w[1]<ylim-2 and w is not c]
      ws.sort(key=lambda w:(w[5],w[6],w[7]))
      txt=' '.join(w[4] for w in ws)
      txt=re.sub(r'(\w)- (\w)',r'\1-\2',txt)  # hifens de quebra são revisados manualmente
      out[re.sub(r'[()\.,;]','',c[4])]={'page':pno+1,'text':txt.strip()}
  return out
if __name__=='__main__':
  ei=extract('/workspace/sb/fontes/BNCC_EI_EF_110518_versaofinal_site.pdf',range(46,54),r'EI0[123][A-Z]{2}\d{2}')
  co=extract('/workspace/sb/fontes/anexo_pceb002_22_computacao.pdf',range(0,12),r'EI0[123]CO\d{2}')
  json.dump({'bncc':ei,'comp':co},open('/workspace/sb/audit/ei_extraido.json','w'),ensure_ascii=False,indent=1)
  print(len(ei),len(co))
  for k in ['EI01EO01','EI02EO01','EI03EO01','EI01EO02','EI03TS03','EI02CG05']: print(k,ei.get(k))
  for k in list(co)[:3]: print(k,co[k])
