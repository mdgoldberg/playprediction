import sys

import pandas as pd

import pfr

yr = int(sys.argv[1])

pbp = pd.DataFrame()
bsIDs = set()
for i, tmID in enumerate(pfr.teams.listTeams()):
    print i+1, tmID
    tm = pfr.teams.Team(tmID)
    bss = tm.boxscores(yr)[:16]
    for bs in bss:
        if bs.bsID in bsIDs:
            continue
        else:
            bsIDs.add(bs.bsID)
        addon = bs.pbp(keepErrors=True)
        addon['bsID'] = bs.bsID
        pbp = pd.concat((pbp, addon))

pbp = pbp.reset_index(drop=True)

matches = map(pfr.utils.parsePlayDetails, pbp.detail)
matches = list(enumerate(matches))
missed = [i for i, m in matches if m is None]
missed = [(i, pbp.ix[i, 'bsID'], pbp.ix[i, 'detail']) for i in missed]
print len(missed)

pbp.to_csv('{}plays.csv'.format(yr), index_share=False, index=False)
