import re,collections as C
def chrf(hyp,ref,n=4,beta=2):
  h=re.sub(r'\s+',' ',hyp.lower()).strip(); r=re.sub(r'\s+',' ',ref.lower()).strip()
  if not h or not r: return 0.0
  P=R=0; k=0
  for i in range(1,n+1):
    hc=C.Counter(h[j:j+i] for j in range(len(h)-i+1)); rc=C.Counter(r[j:j+i] for j in range(len(r)-i+1))
    if not hc or not rc: continue
    m=sum((hc&rc).values()); P+=m/sum(hc.values()); R+=m/sum(rc.values()); k+=1
  if not k: return 0.0
  P/=k; R/=k
  return 0.0 if P+R==0 else (1+beta**2)*P*R/(beta**2*P+R)
