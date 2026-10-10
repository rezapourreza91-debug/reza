# Expected pass probabilities of the registered GP01/GP02 rank tests, by Monte Carlo.
# True FE-equivalent EA: P1-P4 = their FE values; GP01 ~ N(190.1, 12.5), GP02 ~ N(136.3, 11.1)
# (the registered predictions and 1-sd). A common level factor k multiplies all designs and
# cancels in any rank test. Each design is tested n times with coefficient of variation cv;
# the test uses the mean of the n specimens. Also the pure-scatter case (GP value taken as exact).
import numpy as np
from itertools import permutations
rng=np.random.default_rng(20261010)
FE={'P4':62.38842586815206,'P3':114.2817142909738,'P2':159.6282826156652,'P1':214.5575903587366}
def spearman_perfect(m, order):
    return np.all(np.diff(m[:,order],axis=1)>0,axis=1)
def rho(m, order):
    # Spearman between registered order positions and observed ranks
    r=np.argsort(np.argsort(m[:,order],axis=1),axis=1)+1
    k=len(order); ref=np.arange(1,k+1)
    d2=((r-ref)**2).sum(1); return 1-6*d2/(k*(k*k-1))
def run(cv,n,gp_unc=True,N=200000,bias=0.0):
    t={k:np.full(N,v) for k,v in FE.items()}
    t['P5']=190.1+bias+(rng.normal(0,12.5,N) if gp_unc else 0)
    t['P6']=136.3+(rng.normal(0,11.1,N) if gp_unc else 0)
    names=['P4','P3','P6','P2','P5','P1']
    m=np.stack([t[k]*(1+rng.normal(0,cv,(N,n))).mean(1) for k in names],1)
    P5=(m[:,4]>m[:,3])&(m[:,4]<m[:,5]); P6=(m[:,2]>m[:,1])&(m[:,2]<m[:,3])
    five=[0,1,3,4,5]; six=list(range(6))
    r5=rho(m,five); r6=rho(m,six)
    return dict(GP01_between=P5.mean(),GP02_between=P6.mean(),rho5_eq1=(r5>=0.9999).mean(),rho5_ge09=(r5>=0.9-1e-9).mean(),rho6_eq1=(r6>=0.9999).mean(),rho6_ge09=(r6>=0.9-1e-9).mean())
for gp in (False,True):
    for cv in (0.05,0.10,0.15):
        r=run(cv,3,gp)
        print(('GP sd included' if gp else 'scatter only  '),'cv %.2f n 3 '%cv,' '.join('%s %.3f'%(k,v) for k,v in r.items()))
r=run(0.10,3,True,bias=9.3); print('GP sd + known high-EA bias +9.3 J, cv 0.10:',' '.join('%s %.3f'%(k,v) for k,v in r.items()))
# R3's two-design statement: P(mean of 3 orders two designs correctly), cv 10 %, true gap 10 % and 5 %
for gap in (0.10,0.05):
    N=400000; a=(1+rng.normal(0,0.10,(N,3))).mean(1); b=(1+gap)*(1+rng.normal(0,0.10,(N,3))).mean(1)
    print('two designs, gap %d %%, cv 10 %%, n 3: P(correct order) %.3f'%(gap*100,(b>a).mean()))
