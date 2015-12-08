import copy
import numpy as np
import pandas as pd
import pfr
import time

def addPriorColumns(df):
    df = copy.deepcopy(df)
    dates = df.bsID.apply(lambda bID: pfr.boxscores.BoxScore(bID).date())
    years, months, days = zip(*((d.year, d.month, d.day) for d in dates))
    df['year'] = years
    df['month'] = months
    df['day'] = days
    df = df.sort_values(['tm', 'year', 'month', 'day', 'secsElapsedInGame'],
                        ascending=True)
    # add gameNum column
    tmgb = df.groupby('tm')
    for tm, tmdf in tmgb:
        bsIDsInOrder = tmdf.bsID.unique()
        for i, bs in enumerate(bsIDsInOrder):
            df.loc[df.bsID == bs, 'gameNum'] = i+1
    # add inSeasonPassPct column
    df['inSeasonPassPct'] = df.apply(inSeasonPassPct, args=(df,), axis=1)
    print 'done with inSeasonPassPct'
    # add inGamePassPct column
    df['inGamePassPct'] = df.apply(inGamePassPct, args=(df,))
    return df


def inSeasonPassPct(row, df):
    curYear = row['year']
    prevYear = curYear - 1
    if prevYear <= 2001:
        return np.nan
    prevSeasonPriors = df[df.year == prevYear].groupby('tm').isPass.mean()
    thisSeason = df[df.year == curYear]
    if row.gameNum == 1:
        # get previous year's pass pct
        return prevSeasonPriors.loc[row.tm]
    else:
        # get pass pct in games before current game
        prevGames = thisSeason[(thisSeason.tm == row.tm) &
                               (thisSeason.gameNum < row.gameNum)]
        return prevGames.isPass.mean()


def inGamePassPct(row, df):
    firstTime = df.loc[(df.tm == row.tm) & (df.bsID == row.bsID),
                       'secsElapsedInGame'].iloc[0]
    prevSeasonPriors = df[df.year == prevYear].groupby('tm').isPass.mean()
    thisGame = df[df.bsID == row.bsID]
    if row.secsElapsedInGame == firstTime:
        # use in-season pass pct for the first play in a game
        return inSeasonPassPct(row, df)
    else:
        # get in-game pass pct
        inGame = thisGame[(thisGame.tm == row.tm) &
                          (thisGame.secsElapsedInGame < row.secsElapsedInGame)]
        return inGame.isPass.mean()
