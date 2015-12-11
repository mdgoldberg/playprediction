import multiprocessing as mp
import sys

import pandas as pd

import pfr

def processBS(args):
    i, bs = args
    print i
    bs = pfr.boxscores.BoxScore(bs)
    addon = bs.pbp(keepErrors=True)
    return addon

yr = int(sys.argv[1])

bsIDs = set()
for tmID in pfr.teams.listTeams():
    tm = pfr.teams.Team(tmID)
    bss = tm.boxscores(yr)[:16]
    bsIDs.update(bss)

print len(bsIDs)
pool = mp.Pool(mp.cpu_count())
dfs = pool.map_async(processBS, enumerate(bsIDs)).get(sys.maxint)

pbp = pd.concat(dfs)
pbp = pbp.reset_index(drop=True)

matches = map(pfr.utils.parsePlayDetails, pbp.detail)
matches = list(enumerate(matches))
missed = [i for i, m in matches if m is None]
missed = [(i, pbp.ix[i, 'bsID'], pbp.ix[i, 'detail']) for i in missed]
print len(missed)

pbp.to_csv('{}plays.csv'.format(yr), index_share=False, index=False)
