import os
import pandas as pd
import numpy as np
import itertools
from copy import deepcopy
import random
import lightgbm as lgb
from functools import lru_cache

# 46th Chess Olympiad Samarkand 2026 regulations:
#   https://handbook.fide.com/files/handbook/Olympiad2026MainCompetition.pdf
#   https://handbook.fide.com/chapter/OlympiadPairingRules2022  (D.02, pairing)
# Ranking: Match Points, then IS(10) Sonneborn-Berger Cut-1, Game Points,
# then sum of opponents' match points Cut-1.

#To surpress a warning I don't care about...
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "model.txt")
bst = lgb.Booster(model_file=_MODEL_PATH)

_d02_pair_round = None   # lazily bound to d02pairing.pair_round (see simulate_once)


@lru_cache(maxsize=None)
def _win_probs(whiteElo, blackElo):
    """
    Cached [P(black), P(draw), P(white)] for a single board, averaged over a
    small window of the average-rating feature (as the original model call did).

    Elo is integer and bounded, so across a 10k-sim run the same (white, black)
    pair recurs constantly -- caching turns ~4,000 model calls/sim into a handful
    of unique lookups per worker process.
    """
    avg_range = range(-10, 11, 5)
    dat = [[whiteElo - i, blackElo - i, whiteElo - blackElo,
            ((whiteElo - i) + (blackElo - i)) / 2] for i in avg_range]
    return tuple(bst.predict(dat, num_iteration=bst.best_iteration,
                             num_threads=1).mean(axis=0).tolist())


def chessMLPred(model, whiteElo, blackElo):
    preds = _win_probs(int(whiteElo), int(blackElo))
    return np.random.choice([0, 0.5, 1], p=preds)

def getIS10(team, matchSummary):
    teamMatches = matchSummary[matchSummary.playerTeam == team].sort_values(by = ['mpTotalOpp', 'ISi'], ascending = [False, False])

    nOpp = teamMatches.shape[0]
    #TODO: Check on this for new host country
    # if team == "India 2":
    #     print(teamMatches)
    #     print(teamMatches.ISi[0:(nOpp-1)])
    #     print(teamMatches.ISi[0:(nOpp-1)].sum())
    return teamMatches.ISi[0:(nOpp-1)].sum() #IS(10)

def getGP(team, matchSummary):
    teamMatches = matchSummary[matchSummary.playerTeam == team].sort_values(by = ['mpTotalOpp', 'ISi'], ascending = [False, False])
    return teamMatches.gp.sum() #GP

def getMP10(team, matchSummary):
    teamMatches = matchSummary[matchSummary.playerTeam == team].sort_values(by = ['mpTotalOpp', 'ISi'], ascending = [False, False])
    nOpp = teamMatches.shape[0]
    return teamMatches.mpTotalOpp[0:(nOpp-1)].sum() #MP(10)

def pairing(teams: list = [], usedTeams = [], initPass = False):
    """
    Returns the pairings of a list of teams based on their index (+1) in their position in the pool.
    Arguments:
        n = number of Teams
        usedTeams = a parameter used in recursion to carry the found matches to the end of the recursion (i.e. a leaf node)
        teams = used in recursion ^^
        reverse = if you need to prioritize finding a pairing for the lowest rated team
    Returns:
        A list of lists of match pairings, prioritized according tto FIDE regulations for 44th Olympiad.
    """

    # print('trying to pair', n, ' teams')
    # if n > 10:
    #     return None

    # matches = []

    if initPass:
        global matchesSlow
        matchesSlow = []
    n = len(teams)

    # Cap enumeration: this builds *every* pairing permutation (factorial), which
    # is a fallback path (happyPool) only reached for an unpairable pool. A few
    # thousand candidates are plenty for happyPool to pick a max-valid pairing.
    if len(matchesSlow) > 20000:
        return matchesSlow

    usedTeams = deepcopy(usedTeams)

    oppTeams = []

    if len(teams) == 2:
        usedTeams.append((teams[0], teams[1]))
        matchesSlow.append(usedTeams)

    elif len(teams) > 2:
            team = teams[0]
            oppTeams = [teams[i] for i in itertools.chain(range(round(n/2), n), range(round(n/2)-1,0,-1))]

            currUsed = deepcopy(usedTeams)
            for opp in oppTeams:

                newUsed = currUsed + [(team, opp)]

                if len(oppTeams) > 1:
                    tmpTeams = [t for t in teams if t not in (team, opp)]
                    pairing(tmpTeams, newUsed)

    return matchesSlow

class PairingError(Exception):
    """Raised when a round's pairing search exceeds its budget (pathological
    scoregroup). The caller re-rolls the sim with fresh randomness."""


# Remaining pairingFast() invocations allowed for the current round. makeHappyPools'
# float/opponent-search loops all call pairingFast every iteration, so bounding the
# total number of calls per round bounds every one of those loops -- turning a rare
# runaway loop into a fast, catchable PairingError instead of a hang. Reset in
# _pair_round(); each worker process has its own copy.
_pair_budget = [10 ** 9]


# @cached
def pairingFast(teams: list, previousPairings: set = set()):

    # print(previousPairings, teams)
    """
    Returns the pairings of a list of teams based on their index in their position in the pool.
    Arguments:
        teams: list of teams to pair, in order of airing preference
        previousPairings: set of tuples of previous matchups
    Returns:
        Returns the first valid pairing list from a group for the 44th Olympiad
    """

    _pair_budget[0] -= 1
    if _pair_budget[0] <= 0:
        raise PairingError("per-round pairing budget exceeded")

    if len(teams) == 0:
        return []

    # Failure-memoisation + a hard recursion budget. Whether a set of teams has a
    # rematch-free perfect pairing is a property of the SET (every recursive
    # sub-list is a subsequence of the original order, so a given set always has
    # the same first team) -- so caching sets already proven unpairable is exact
    # and only prunes provably-dead branches. Without this the backtracking is
    # exponential and, on a heavily-constrained late-round scoregroup, effectively
    # hangs (root cause of the 10k-run stalls). The budget is a last-resort guard:
    # if a genuinely huge unpairable pool blows past it we return None (treated as
    # "float instead"), which the caller handles.
    failed = set()
    budget = [4_000_000]

    def _rec(ts):
        if not ts:
            return []
        if budget[0] <= 0:
            return None
        budget[0] -= 1
        key = frozenset(ts)
        if key in failed:
            return None
        team = ts[0]
        n = len(ts)
        for i in itertools.chain(range(round(n / 2), n), range(round(n / 2) - 1, 0, -1)):
            opp = ts[i]
            if (team, opp) not in previousPairings:
                sub = _rec([t for t in ts if t != team and t != opp])
                if sub is not None:
                    return [(team, opp)] + sub
        failed.add(key)
        return None

    return _rec(teams)

def pairingDiagnostics(newMatchups, previousMatchups, initPools, verbose = False):

    alreadyPaired = len((previousMatchups.intersection(newMatchups))) > 1

    if alreadyPaired:
        raise Exception("Matchup made that was already paired")


    '''Do something here'''

    if verbose == False:
        print("Stuff")

# pairingFast(list(range(6)), set([(2, 5)]))


def happyPool(pool, prevMatches):

    """
    given a list of teams in a pool, their preferred order of pairings, and a list of previous matches, return the preferred pairings, if any
    """

    if len(pool) % 2 > 0:
        return None, None

    pairingList = pairing(pool, initPass = True)
    # print(pairingList)

    maxPairsGroup = []
    for pairingTry in pairingList:
        
        anyBadMatch = 0

        maxPairs = len(pairingTry)
        # print(pairingTry)
        for match in pairingTry:

            # print(match[0])
            if (match[0], match[1]) in prevMatches:
                maxPairs -= 1
                anyBadMatch +=1
        maxPairsGroup.append(maxPairs)

        if anyBadMatch == 0:
            return pairingTry, None

    bestPairs = pairingList[maxPairsGroup.index(max(maxPairsGroup))]

    floaters = []
    goodMatches = set()

    for match in bestPairs:
        if (match[0], match[1]) in prevMatches:
            floaters.append(match[0])
            floaters.append(match[1])
        if (match[0], match[1]) not in prevMatches:
            goodMatches.add((match[0], match[1]))
    

    return goodMatches, floaters



def playedAllTeams(pool, prevMatches):

    """
    Check if any team has played all the other teams in the pool. If so, return them in a list.
    """

    floaters = [team for team in pool if sum([1 if (team,opp) in prevMatches else 0 for opp in pool]) == (len(pool) - 1)]

    return floaters

def allPlayedAll(currGroup, nextGroup, prevMatches):

    """
    Checks if all teams have polayed all tams in the next group
    """

    return len([team for team in currGroup if sum([1 if (team, opp) in prevMatches else 0 for opp in nextGroup]) == len(nextGroup)]) == len(currGroup)

def findFloater(currGroup, nextGroup, prevMatches, poolHalf = 'bottom'):

    """
    Finds one team that needs to and CAN be floated to the next group
    """
 
    if poolHalf == 'top': #Need to drop bottom team first if half; always sort team list by mp and init rank
        currGroup.reverse()

    playedEntirePool =  playedAllTeams(currGroup, prevMatches)

    if playedEntirePool: #True if len list > 1; magic!
        return playedEntirePool[0]

    allAll = allPlayedAll(currGroup, nextGroup, prevMatches)

    if len(currGroup) % 2 > 0:

        for team in currGroup:
            ## If can't find a team then return None, and future code will need to know to change next group to nextNext group
            if team not in playedAllTeams(team+nextGroup, prevMatches):
                return team
        return None #if no odd team out could play a team in the next pool, we need to drop them to the nextest pool


def makeHappyPools(topPools, bottomPools, medianPool, prevMatches):
    #TODO: If two teams have +2 or -2, then they can't be matched, unless it doesnt create a floater.
    # print(type(topPools), 'sdwffe')
    # print('top', topPools)
    # print('bottom', bottomPools)
    # print('median', medianPool)

    medPoolCopy = deepcopy(medianPool)

    teamSet = set([team for pool in topPools+medianPool+bottomPools for team in pool])
    if len(medianPool) > 0:
        if pairingFast(medianPool[0], prevMatches) is None:
            
            # print('tried to remove median teams')
            # print((medianPool[0][0], medianPool[0][1]))
            topPools[len(topPools)-1] = topPools[len(topPools)-1] + medianPool[0]
            medianPool = []

    # print(len(topPools), len(bottomPools), len(medianPool))
    allPools = topPools + medianPool + list(reversed(bottomPools))
    allPoolsCopy = deepcopy(allPools)
    floatedMatches = set()
    goodMatches = set()
    poolNumber = 0

    if len(topPools) > 0:
        if type(topPools[0]) == str:
            topPools = [topPools]
            allPools = [allPools]

    for pool in topPools:
        # print('this is a top pool')

        # currentMatches = goodMatches.copy()
        # print(pool, 'this is the pool')

        # print(pool)

        isNotHappy = True
        failSafe = 0
        
        while isNotHappy:

            teamsPlayedALl = playedAllTeams(pool, prevMatches)
            # print(teamsPlayedALl)
            
            for team in teamsPlayedALl:

                pool.remove(team) # Once we float it to the next pool, its no longer in current pool

                foundValidOpp = False
                poolIterator = 1
                oppIterator = 0
                while not foundValidOpp: #check if floated team has played all opponents in the next pool
                    # print('whileID: sedfsadf')
                    if oppIterator < len(allPools[(poolNumber+poolIterator)]):
                        # print(allPools[(poolNumber+poolIterator)])
                        opp = allPools[(poolNumber+poolIterator)][oppIterator]
                        # print(opp, 'try opp')
                        remainingNextPool = [x for x in allPools[(poolNumber+poolIterator)] if x != opp]
                        
                        if (team, opp) not in prevMatches:
                            # print(team, opp)
                            if pairingFast(remainingNextPool, prevMatches) is not None:
                                # print(team, opp)
                                floatedMatches.add((team, opp))
                                foundValidOpp = True
                                allPools[(poolNumber+poolIterator)].remove(opp)
                        oppIterator += 1
                    elif oppIterator >= len(allPools[(poolNumber+poolIterator)]): # If he has, go to the next pool since this team has to be floated, bec they already played all teams in their own pool too
                        poolIterator +=1
                        oppIterator = 0
                   

            if len(pool) % 2 > 0:
                # print(len(pool), 'this is the length of the pool')
                # print(pool)
                
                foundValidFloat = False
                i = 0
                poolIterator = 1

                while not foundValidFloat:
                    # print('whileID: ;asedpokrfjnwk')
                    
                    if i >= len(pool):
                        poolIterator +=1
                        i = 0

                    i += 1
                    tryFloat = pd.Series(pool).iat[-i]
                    # print(tryFloat)

                    tempCurrPool = [team for team in pool if team != tryFloat]

                    # floatPriorPoolFloaters = 
                    # print(happyPool(tempCurrPool, prevMatches))

                    if pairingFast(tempCurrPool, prevMatches) is not None:
                        
                        foundValidOpp = False
                        
                        oppIterator = 0
                        while not foundValidOpp: #check if floated team has played all opponents in the next pool
                            # print('whileID: wklej3432')
                            if oppIterator < len(allPools[(poolNumber+poolIterator)]):
                                # print(poolNumber)
                                # print(poolIterator)
                                opp = allPools[(poolNumber+poolIterator)][oppIterator]
                                remainingNextPool = [x for x in allPools[(poolNumber+poolIterator)] if x != opp]
                                if (tryFloat, opp) not in prevMatches:
                                    if pairingFast(remainingNextPool, prevMatches) is not None:
                                        # print(tryFloat)
                                        floatedMatches.add((tryFloat, opp))
                                        foundValidOpp = True
                                        foundValidFloat = True
                                        allPools[(poolNumber+poolIterator)].remove(opp)
                                        pool.remove(tryFloat)
                            elif oppIterator >= len(allPools[(poolNumber+poolIterator)]): # If he has, go to the next pool since this team has to be floated, bec they already played all teams in their own pool too
                                break
                            oppIterator += 1
            # a.where(a!=3).dropna().reset_index(drop = True)
                        
            ##Now that we got rid of the played all teams, and the odd team, we need to pair up this pool, and send the minimum number of teams down to the next pool for float pairing.
            if (len(pool) % 2 == 0) & (playedAllTeams(pool, prevMatches) == []): #after we remove the odd team, we need to verify thats no one has played everyone

                isNotHappy = False #break loop on next iteration

                newGoodMatches = pairingFast(pool, prevMatches)

                if newGoodMatches is None:

                    # print('top pool, we found some weird floaters, but we conquered the issue!')

                    # print(pool, 'this is the pool')
                    # for team in pool:
                    #     for game in prevMatches:
                    #         if team in game:
                    #             print(game)

                    ##Need to run OG pairing algoithm on the pool, find max pairings, pair, then float

                    gm, poolFloaters = happyPool(pool, prevMatches)

                    newGoodMatches = gm

                    for floater in poolFloaters:

                        foundValidOpp = False
                        poolIterator = 1
                        oppIterator = 0
                        while not foundValidOpp: #check if floated team has played all opponents in the next pool
                            # print('whileID: 231ihed')
                            if oppIterator < len(allPools[(poolNumber+poolIterator)]):
                                opp = allPools[(poolNumber+poolIterator)][oppIterator]
                                remainingNextPool = [x for x in allPools[(poolNumber+poolIterator)] if x != opp]
                                if (floater, opp) not in prevMatches:
                                    if pairingFast(remainingNextPool, prevMatches) is not None:
                                        floatedMatches.add((floater, opp))
                                        foundValidOpp = True
                                        allPools[(poolNumber+poolIterator)].remove(opp)
                                oppIterator += 1
                            elif oppIterator >= len(allPools[(poolNumber+poolIterator)]): # If he has, go to the next pool since this team has to be floated, bec they already played all teams in their own pool too
                                poolIterator +=1
                                oppIterator = 0

                    # raise Exception("No matches found, need to improve code to account for floaters in this situation. make max pairings, float least priritized teams")

                goodMatchesFromPool  = set(newGoodMatches)

                goodMatches = goodMatches.union(goodMatchesFromPool)
            

            failSafe += 1                
            if failSafe > 100:
                raise Exception("Fail Safe, while loop over 100 iterations for pool: ", pool)



        poolNumber += 1
        # print('heres the new matches added form the top pool', goodMatches.difference(currentMatches))

    poolNumber = len(allPools)-1 #set index to the last pool in allPools list, then we traverse backwards

    for pool in bottomPools:

        # print(pool)

        isNotHappy = True
        failSafe = 0
        
        while isNotHappy:
            # print('whileID: asdwq354234')

            teamsPlayedAll = playedAllTeams(pool, prevMatches)
            # print(teamsPlayedALl)
            
            for team in reversed(teamsPlayedAll):

                pool.remove(team) # Once we float it to the next pool, its no longer in current pool

                foundValidOpp = False
                # bottomPoolsLen = len(bottomPools)
                poolIterator = 1
                oppIterator = 1
                while not foundValidOpp: #check if floated team has played all opponents in the next pool
                    # print('whileID: asdef432543')
                    if oppIterator < len(allPools[(poolNumber-poolIterator)]):
                        opp = allPools[(poolNumber-poolIterator)][-oppIterator]
                        remainingNextPool = [x for x in allPools[(poolNumber-poolIterator)] if x != opp]
                        if (team, opp) not in prevMatches:
                            if pairingFast(remainingNextPool, prevMatches) is not None:
                                floatedMatches.add((team, opp))
                                foundValidOpp = True
                                allPools[(poolNumber-poolIterator)].remove(opp)
                        oppIterator += 1
                    elif oppIterator >= len(allPools[(poolNumber-poolIterator)]): # If he has, go to the next pool since this team has to be floated, bec they already played all teams in their own pool too
                        poolIterator +=1
                        oppIterator = 0
                    
            

            if len(pool) % 2 > 0:
                # print(pool)
                
                foundValidFloat = False
                i = 0
                poolIterator = 1

                while not foundValidFloat:
                    # print('whileID: dsfgwert456')
                    
                    if i >= len(pool):
                        poolIterator +=1
                        i = 0

                    
                    tryFloat = pd.Series(pool).iat[i]
                    i += 1
                    # print(tryFloat)

                    tempCurrPool = [team for team in pool if team != tryFloat]

                    # floatPriorPoolFloaters = 
                    # print(happyPool(tempCurrPool, prevMatches))

                    if pairingFast(tempCurrPool, prevMatches) is not None:
                        
                        foundValidOpp = False
                        
                        oppIterator = 1
                        while not foundValidOpp: #check if floated team has played all opponents in the next pool
                            # print('whileID: ghfdhrety')
                            if oppIterator <= len(allPools[(poolNumber-poolIterator)]):
                                # print(poolNumber)
                                # print(poolIterator)
                                opp = allPools[(poolNumber-poolIterator)][-oppIterator]
                                remainingNextPool = [x for x in allPools[(poolNumber-poolIterator)] if x != opp]
                                if (tryFloat, opp) not in prevMatches:
                                    if pairingFast(remainingNextPool, prevMatches) is not None:
                                        floatedMatches.add((tryFloat, opp))
                                        foundValidOpp = True
                                        foundValidFloat = True

                                        allPools[(poolNumber-poolIterator)].remove(opp)
                                        # print(bottomPools)

                                        pool.remove(tryFloat)
                            elif oppIterator > len(allPools[(poolNumber-poolIterator)]): # If he has, go to the next pool since this team has to be floated, bec they already played all teams in their own pool too
                                break
                            oppIterator += 1
            # a.where(a!=3).dropna().reset_index(drop = True)
                        
            ##Now that we got rid of the played all teams, and the odd team, we need to pair up this pool, and send the minimum number of teams down to the next pool for float pairing.
            if (len(pool) % 2 == 0) & (playedAllTeams(pool, prevMatches) == []): #after we remove the odd team, we need to verify thats no one has played everyone
                
                isNotHappy = False #break loop on next iteration

                newGoodMatches = pairingFast(pool, prevMatches)

                if newGoodMatches is None:
                    
                    # print('we found some weird floaters, but we conquered the issue!')
                    ##Need to run OG pairing algoithm on the pool, find max pairings, pair, then float

                    gm, poolFloaters = happyPool(pool, prevMatches)

                    newGoodMatches = gm

                    for floater in poolFloaters:

                        foundValidOpp = False
                        poolIterator = 1
                        oppIterator = 0
                        while not foundValidOpp: #check if floated team has played all opponents in the next pool
                            # print('whileID: ewqrwqe5345')
                            if oppIterator < len(allPools[(poolNumber-poolIterator)]):
                                opp = allPools[(poolNumber-poolIterator)][oppIterator]

                                remainingNextPool = [x for x in allPools[(poolNumber-poolIterator)] if x != opp]
                                if (floater, opp) not in prevMatches:
                                    if pairingFast(remainingNextPool, prevMatches) is not None:
                                        floatedMatches.add((floater, opp))
                                        foundValidOpp = True
                                        allPools[(poolNumber-poolIterator)].remove(opp)
                                oppIterator += 1
                            elif oppIterator >= len(allPools[(poolNumber-poolIterator)]): # If he has, go to the next pool since this team has to be floated, bec they already played all teams in their own pool too
                                poolIterator +=1
                                oppIterator = 0
                            



                    # raise Exception("No matches found, need to improve code to account for floaters in this situation. make max pairings, float least priritized teams")

                goodMatchesFromPool  = set(newGoodMatches)

                goodMatches = goodMatches.union(goodMatchesFromPool)
                


                # if floatersRemaining is not None:

                #     # condition where we are not floating anyone unless we cant pair ALL teams, even though thtere isnt an odd number and noone has played everyone
                #     for floaterFromPool in floatersRemaining:

                #         poolIterator = 1

                #         foundValidOpp = False
                        
                #         oppIterator = 0
                #         while not foundValidOpp: #check if floated team has played all opponents in the next pool
                #             if oppIterator < len(allPools[(poolNumber+poolIterator)]):
                #                 opp = allPools[(poolNumber+poolIterator)][oppIterator]
                #                 if floaterFromPool+opp not in prevMatches:
                #                     floatedMatches.append([floaterFromPool, opp])
                #                     foundValidOpp = True
                #                     foundValidFloat = True
                #                     allPools[(poolNumber+poolIterator)].remove(opp)
                #                     pool.remove(floaterFromPool)
                #             elif oppIterator >= len(allPools[(poolNumber+poolIterator)]): # If he has, go to the next pool since this team has to be floated, bec they already played all teams in their own pool too
                #                 oppIterator = 0
                #                 poolIterator +=1
                #                 continue
                #             oppIterator += 1
                        

            failSafe += 1                
            if failSafe > 100:
                raise Exception("Fail Safe, while loop over 100 iterations for pool: ", pool)



        poolNumber -= 1

    # print(medianPool)


    if len(medianPool) > 0:
        if pairingFast(medianPool[0], prevMatches) is None:
            print('floatted', floatedMatches)
            print('median pool pairing')
            print('copy', medPoolCopy)
            print('median pool:', medianPool)
            print('number of median teams', len(medianPool[0]))
            print('prev matches', prevMatches)

            # for i in range(0, len(medianPool[0]))      

        # print(set(pairingFast(medianPool[0], prevMatches)))
        else:
            # print(goodMatches,' current good matches', len(goodMatches))
            # print(floatedMatches,' current floatedMatches matches', len(floatedMatches))
            # print(medianPool)
            # print(pairingFast(medianPool[0], prevMatches), 'median pairings')
            goodMatches = goodMatches.union(set(pairingFast(medianPool[0], prevMatches)))

    # print('good matches:', goodMathces)
    # print('floated:', floatedMatches)

    # print('these are unmatched teams', teamSet.difference(set([team for match in goodMatches.union(floatedMatches) for team in match])))
    if any([a==b for a,b in goodMatches.union(floatedMatches)]):
        # for a,b in goodMatches.union(floatedMatches):
        #     if a==b:
        #         print(a,b)
        # print('')
        # print('')
        # print('')
        # print('')
        # print('original pools',allPoolsCopy)
        # print('')
        # print('')
        # print('')
        # print('')
        # print('previous matchups',prevMatches)
        # print('')
        # print('')
        # print('')
        # print('')
        # print('good matches', goodMatches)
        # print('')
        # print('')
        # print('')
        # print('')
        # print('floated matches', floatedMatches)

        # TODO: This is a bug, need to fix this
        # rmeove match with same team playing itself
        goodMatches = set([match for match in goodMatches if match[0] != match[1]])
        # raise Exception("Something went wrong, matched with itself?")
    return goodMatches.union(floatedMatches)
    # print(medianPool)
    # print(len(medianPool[0]))


def whiteGamesCount(gamesWhite, teams): #TODO only used for initial setup, not sure why I need this

    if gamesWhite.shape[0] > 0:
        gamesWhite = gamesWhite[gamesWhite.board == 1].whiteTeam.value_counts().to_frame().reset_index()
        gamesWhite.columns = ['team', 'whiteCount']

        numRounds = 0
        numRounds = 2 * (gamesWhite.whiteCount.sum() / gamesWhite.shape[0])
        gamesWhite['whiteDiff'] = 2 * gamesWhite.whiteCount - numRounds

        teamsWhite = teams.merge(right = gamesWhite, how = 'left', on = 'team')
        teamsWhite['whiteCount'] = teamsWhite['whiteCount'].fillna(0)
        teamsWhite['whiteDiff'] = teamsWhite['whiteDiff'].fillna(0)
        # print(teamsWhite)

        # matchSummary.merge(right = teamSummary, how = 'inner', on = 'playerTeam')

        return teamsWhite
    else:  
        teams['whiteCount'] = 0
        teams['whiteDiff'] = 0
        return teams

def getWhiteTeam(matchTeams, teams):
    a = matchTeams[0]
    b = matchTeams[1]

    aCount = teams[teams.team == a].whiteCount.item()
    bCount = teams[teams.team == b].whiteCount.item()

    if aCount > bCount:
        return b
    elif aCount < bCount:
        return a
    elif aCount == bCount:
        return random.choice([a,b]) #TODO: This is supposed to be based on alteration
    else:
        raise Exception("Color if-else didn't work")

def simulateGame(whiteElo, blackElo, model):
    supplement = 0
    # print(whiteElo)
    # print(blackElo)
    if min([whiteElo, blackElo]) < 1900:
        supplement = 1900 - min([whiteElo, blackElo])
    return chessMLPred(model, whiteElo + supplement, blackElo + supplement)


# ===========================================================================
# Fast simulation core (2026 rewrite)
# ---------------------------------------------------------------------------
# The pairing engine above (makeHappyPools / pairingFast / happyPool ...) is
# reused verbatim -- it implements FIDE Olympiad Pairing Rules D.02 and was
# validated on the 2024 event. Everything below replaces the old pandas-heavy
# per-round summarise/playMatch/main path with dict-based bookkeeping so a
# 10k-sim run over 200 teams is tractable. Standings tiebreaks are computed
# once, at the end, per Regs Appendix 2.I.
# ===========================================================================

import json
from olympiadConfig import get_event  # noqa: E402


def prep_board_elos(players_df):
    """team -> list of top-4 board Elos (rows are already in board order)."""
    elos = {}
    for team, grp in players_df.groupby("Team", sort=False):
        e = [int(x) for x in grp["Rtg"].tolist()[:4]]
        while len(e) < 4:            # defensive; scraper already pads to 4
            e.append(e[-1])
        elos[team] = e
    return elos


def _match_gp(white_elos, black_elos):
    """
    Play one team match (4 boards) and return (white_team_gp, black_team_gp).
    The board-1-white team has White on boards 1 & 3, Black on boards 2 & 4.
    """
    r1 = simulateGame(white_elos[0], black_elos[0], bst)   # white team, white
    r2 = simulateGame(black_elos[1], white_elos[1], bst)   # black team, white
    r3 = simulateGame(white_elos[2], black_elos[2], bst)
    r4 = simulateGame(black_elos[3], white_elos[3], bst)
    white_gp = r1 + (1 - r2) + r3 + (1 - r4)
    return white_gp, 4 - white_gp


def _gp_to_mp(gp):
    return 2 if gp > 2 else (1 if gp == 2 else 0)


def load_event(cfg, pretournament=False, through_round=None):
    """
    Build the immutable per-event state needed to simulate: participating teams,
    starting ranks, board Elos, the official Round-1 pairings, and any
    completed-round results to start from.

    Participants are every team that appears in ANY published team-vs-team
    pairing (completed or scheduled). Basing this on Round 1 alone silently
    dropped the late-arriving delegations (Angola, Cote d'Ivoire, CAR, Marshall
    Islands showed as "not paired" in R1 and only joined from R2) -- and with
    them every later match they played, including the forfeit wins awarded to
    their opponents. A team that never gets a real pairing (fully withdrawn)
    is still excluded.

    pretournament=True builds the R0 (pre-tournament) state: ignore all completed
    results (simulate from Round 1), pin only the official Round-1 pairings, and
    simulate rounds 2..11 -- i.e. what a forecast knew before any games.

    through_round=N rebuilds the state as it stood after round N: seed only
    rounds <= N, pin round N+1's official pairings, simulate N+1..11. Used to
    (re)generate a historical run for the odds-over-time chart.
    """
    players = pd.read_csv(cfg.players_csv)
    teams = pd.read_csv(cfg.teams_csv)
    r1 = pd.read_csv(cfg.round1_pairings_csv)
    matches = pd.read_csv(cfg.matches_csv)
    try:
        rr = pd.read_csv(cfg.round_results_csv)
    except (FileNotFoundError, OSError):
        rr = None

    r1_pairs = list(zip(r1.whiteTeam, r1.blackTeam))
    if rr is not None and not rr.empty:
        participants = sorted(set(rr.team1) | set(rr.team2))
    else:
        participants = sorted(set(r1.whiteTeam) | set(r1.blackTeam))
    pset = set(participants)

    if through_round is not None:
        if through_round < 1:
            raise ValueError("through_round must be >= 1 (use pretournament=True for R0)")
        matches = matches[matches["round"] <= through_round]

    init_rank = dict(zip(teams.team, teams.initRank.astype(int)))
    # team_id == chess-results starting number (snr). Contiguous 1..n_teams over
    # ALL registered teams (including any that later withdrew), so the site's
    # team_id-indexed arrays line up with its team/roster tables.
    # native ints (not numpy) so psycopg2 can adapt team_ids straight into SQL
    team_id = {t: int(r) for t, r in zip(teams.team, teams.initRank)}
    n_teams = int(teams.initRank.max())
    for t in participants:
        init_rank.setdefault(t, 10_000)
    missing_ids = [t for t in participants if t not in team_id]
    if missing_ids:
        raise RuntimeError(f"Participants missing a start number: {missing_ids[:5]}")

    board_elos = prep_board_elos(players[players.Team.isin(pset)])
    missing = [t for t in participants if t not in board_elos]
    if missing:
        raise RuntimeError(f"No roster for participating teams: {missing[:5]}")

    # Seed completed rounds (empty pre-tournament). matches.csv holds both
    # perspectives already (playerTeam, oppTeam, round, gp).
    seed_mp = {t: 0 for t in participants}
    seed_matches = {t: [] for t in participants}
    seed_round_hp = {t: {} for t in participants}
    seed_round_opp = {t: {} for t in participants}   # round -> opponent team_id
    seed_prev = set()
    next_round = 1
    if not pretournament and not matches.empty:
        for row in matches.itertuples(index=False):
            if row.playerTeam in pset and row.oppTeam in pset:
                seed_mp[row.playerTeam] += _gp_to_mp(row.gp)
                seed_matches[row.playerTeam].append((float(row.gp), row.oppTeam))
                seed_round_hp[row.playerTeam][int(row.round)] = int(round(row.gp * 2))
                seed_round_opp[row.playerTeam][int(row.round)] = team_id[row.oppTeam]
                seed_prev.add((row.playerTeam, row.oppTeam))
        next_round = int(matches["round"].max()) + 1
    if through_round is not None:
        next_round = through_round + 1

    # Official published-but-unplayed pairings for rounds we haven't simulated
    # yet -- typically just the next round. We FIX these instead of generating our
    # own, so round_opps for the next round equals the published pairing (only
    # its result varies across sims). Pre-tournament pins nothing beyond R1
    # (handled via r1_pairs). A through_round backfill pins round N+1 whatever
    # its status now: those were the published pairings at that point in time.
    fixed_pairs = {}
    if rr is not None and not rr.empty and not pretournament:
        if through_round is not None:
            sched = rr[rr["round"] == next_round]
        else:
            sched = rr[(rr["status"] == "scheduled") & (rr["round"] >= next_round)]
        for row in sched.itertuples(index=False):
            if row.team1 in pset and row.team2 in pset:
                fixed_pairs.setdefault(int(row.round), []).append((row.team1, row.team2))

    return {
        "cfg": cfg,
        "participants": participants,
        "init_rank": init_rank,
        "team_id": team_id,
        "n_teams": n_teams,
        "board_elos": board_elos,
        "r1_pairs": r1_pairs,
        "seed_mp": seed_mp,
        "seed_matches": seed_matches,
        "seed_round_hp": seed_round_hp,
        "seed_round_opp": seed_round_opp,
        "seed_prev": seed_prev,
        "fixed_pairs": fixed_pairs,
        "next_round": next_round,
        "n_rounds": cfg.n_rounds,
    }


def _pair_round(teams_by_rank, mp, prev):
    """Pair one non-first round using the D.02 pool engine. Returns set of matches."""
    # Generous budget: a normal round uses a few thousand calls; a pathological
    # scoregroup that would otherwise spin blows past this in ~1s and raises.
    _pair_budget[0] = 600_000
    n = len(teams_by_rank)
    median_index = round(n / 2) if n % 2 == 0 else round(n / 2 - 0.5)
    median_mp = mp[teams_by_rank[median_index]]

    mps = sorted({mp[t] for t in teams_by_rank})
    top_pools = [[t for t in teams_by_rank if mp[t] == v]
                 for v in sorted(mps, reverse=True) if v > median_mp]
    bottom_pools = [[t for t in teams_by_rank if mp[t] == v]
                    for v in mps if v < median_mp]
    median_pool = [[t for t in teams_by_rank if mp[t] == median_mp]]
    return makeHappyPools(top_pools, bottom_pools, median_pool, prev)


def _choose_white(a, b, wc):
    if wc[a] < wc[b]:
        return a, b
    if wc[b] < wc[a]:
        return b, a
    return (a, b) if random.random() < 0.5 else (b, a)


def _final_standings(participants, init_rank, mp, matches):
    """Rank teams by MP -> IS(10) -> GP -> MP(10) (Regs Appendix 2.I, Cut-1)."""
    gp_total, is10, mp10 = {}, {}, {}
    for t in participants:
        recs = matches[t]
        gp_total[t] = sum(g for g, _ in recs)
        # (ISi, opponent final MP) per game; sort by (oppMP, ISi) desc, drop lowest.
        rows = sorted(((g * mp[o], mp[o]) for g, o in recs),
                      key=lambda x: (x[1], x[0]), reverse=True)
        keep = rows[:-1]  # Cut-1: drop the single lowest (or the bye slot)
        is10[t] = sum(isi for isi, _ in keep)
        mp10[t] = sum(om for _, om in keep)
    order = sorted(participants,
                   key=lambda t: (mp[t], is10[t], gp_total[t], mp10[t], -init_rank[t]),
                   reverse=True)
    return order, gp_total


def simulate_once(state):
    """
    Run one full tournament from `state`. Returns a dict of team_id-indexed
    arrays matching the olympiad_2026_sims schema (see SCHEMA.md):
      gold/silver/bronze : team_ids of the final top 3
      top10              : team_ids at final ranks 1..10 (in order)
      final_rank         : final_rank[team_id] = 1..n_teams (0 = did not play)
      match_points       : match_points[team_id]
      game_points        : game_points[team_id] in HALF-points (0..88)
      round_scores       : round_scores[round][team_id] in HALF-points (0..8)
    Arrays are laid out so that, once stored in a (1-based) Postgres array,
    arr[team_id] and round_scores[round][team_id] index directly. In Python
    that means team t sits at index t-1 and round r at index r-1: the team
    dimension has length n_teams and the round dimension length n_rounds.
    A team_id that did not play carries 0 in every array.
    """
    participants = state["participants"]
    init_rank = state["init_rank"]
    board_elos = state["board_elos"]
    team_id = state["team_id"]
    n_teams = state["n_teams"]
    n_rounds = state["n_rounds"]

    mp = dict(state["seed_mp"])
    matches = {t: list(state["seed_matches"][t]) for t in participants}
    round_hp = {t: dict(state["seed_round_hp"][t]) for t in participants}
    round_opp = {t: dict(state["seed_round_opp"][t]) for t in participants}
    prev = set(state["seed_prev"])
    wc = {t: 0 for t in participants}

    def play(white, black, rnd):
        wgp, bgp = _match_gp(board_elos[white], board_elos[black])
        mp[white] += _gp_to_mp(wgp)
        mp[black] += _gp_to_mp(bgp)
        matches[white].append((wgp, black))
        matches[black].append((bgp, white))
        round_hp[white][rnd] = int(round(wgp * 2))
        round_hp[black][rnd] = int(round(bgp * 2))
        round_opp[white][rnd] = team_id[black]
        round_opp[black][rnd] = team_id[white]
        prev.add((white, black))
        prev.add((black, white))
        wc[white] += 1

    # Lazy import breaks the simOlympiad <-> d02pairing cycle.
    global _d02_pair_round
    if _d02_pair_round is None:
        from d02pairing import pair_round as _d02_pair_round

    def _d02_pair(team_list):
        ctx = {"teams": team_list, "mp": mp, "init_rank": init_rank,
               "prev": prev, "last_color": {}}
        return _d02_pair_round(ctx)

    fixed_pairs = state.get("fixed_pairs", {})
    for rnd in range(state["next_round"], n_rounds + 1):
        # Use official published pairings for this round if we have them (fixed
        # across all sims); pre-tournament R1 falls back to r1_pairs.
        fp = fixed_pairs.get(rnd)
        if fp is None and rnd == 1 and state["r1_pairs"]:
            fp = state["r1_pairs"]
        if fp:
            paired_now = set()
            for white, black in fp:
                play(white, black, rnd)
                paired_now.add(white); paired_now.add(black)
            # Participants whose official opponent left the field (participant-set
            # drift) aren't in fp -> pair them with the engine, don't leave unpaired.
            leftover = [t for t in participants if t not in paired_now]
            if leftover:
                for pair in _d02_pair(leftover):
                    a, b = tuple(pair)
                    white, black = _choose_white(a, b, wc)
                    play(white, black, rnd)
            continue

        teams_by_rank = sorted(participants, key=lambda t: (-mp[t], init_rank[t]))
        # Odd field -> lowest-ranked team gets a bye (1 MP + 2 GP, Regs 4.1/4.3).
        if len(teams_by_rank) % 2:
            bye = teams_by_rank[-1]
            teams_by_rank = teams_by_rank[:-1]
            mp[bye] += 1
            matches[bye].append((2.0, None))  # bye GP; opp None -> excluded from TB
            round_hp[bye][rnd] = 4
            round_opp[bye][rnd] = 0            # 0 == bye

        # FIDE D.02 team pairing (validated 100% vs official R2 for both events).
        for pair in _d02_pair(teams_by_rank):
            a, b = tuple(pair)
            white, black = _choose_white(a, b, wc)
            play(white, black, rnd)

    # Bye rows carry opp=None (excluded from IS(10)/MP(10) -- the bye round is
    # dropped anyway); filter them out before computing tiebreaks.
    tb_matches = {t: [(g, o) for g, o in matches[t] if o is not None]
                  for t in participants}
    order, gp_total = _final_standings(participants, init_rank, mp, tb_matches)

    # Length-n_teams lists; team t at index t-1 so Postgres arr[t] == team t.
    final_rank = [0] * n_teams
    match_points = [0] * n_teams
    game_points = [0] * n_teams                            # half-points
    round_scores = [[0] * n_teams for _ in range(n_rounds)]
    round_opps = [[0] * n_teams for _ in range(n_rounds)]  # opponent team_id (0=bye)
    for pos, t in enumerate(order):
        tid = team_id[t]
        final_rank[tid - 1] = pos + 1
        match_points[tid - 1] = mp[t]
        game_points[tid - 1] = int(round(gp_total[t] * 2))
        for rnd, hp in round_hp[t].items():
            round_scores[rnd - 1][tid - 1] = hp
        for rnd, opp in round_opp[t].items():
            round_opps[rnd - 1][tid - 1] = opp

    return {
        "gold": team_id[order[0]],
        "silver": team_id[order[1]],
        "bronze": team_id[order[2]],
        "top10": [team_id[t] for t in order[:10]],
        "final_rank": final_rank,
        "match_points": match_points,
        "game_points": game_points,
        "round_scores": round_scores,
        "round_opps": round_opps,
    }


def main(_=0):
    """Standalone smoke test: simulate one tournament and print the podium."""
    import sys
    key = sys.argv[1] if len(sys.argv) > 1 else "open"
    state = load_event(get_event(key))
    res = simulate_once(state)
    id2name = {v: k for k, v in state["team_id"].items()}
    print("podium:", [id2name[res[m]] for m in ("gold", "silver", "bronze")])
    return res


if __name__ == "__main__":
    main()
