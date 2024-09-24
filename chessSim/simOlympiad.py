import pandas as pd
import numpy as np
import itertools
from copy import deepcopy
import random
import lightgbm as lgb

# https://handbook.fide.com/files/handbook/Olympiad2022MainCompetition.pdf
# https://handbook.fide.com/chapter/OlympiadPairingRules2022

##SHould use teams starting rank from chess-results

#To surpress a warning I don't care about...
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# from chessSim.utils import summarizeCurrent
urllib3.disable_warnings(InsecureRequestWarning)

bst = lgb.Booster(model_file = './chessSim/models/model.txt')

def chessMLPred(model, whiteElo, blackElo):
    avgRange = range(-10, 11, 5)
    
    dat = [[whiteElo - i, blackElo - i, whiteElo - blackElo,((whiteElo - i) + (blackElo - i)) / 2] for i in avgRange]
    preds = model.predict(dat,num_iteration=model.best_iteration, num_threads = 1).mean(axis = 0).tolist()
    result = np.random.choice([0,0.5,1], p=preds) 
    # print(whiteElo, blackElo, preds)

    return result

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

    # print('trying to pair', n, ' teams')
    # if n > 10:
    #     return None

    if len(teams) == 0:
        return []
    # if len(teams) % 2 > 0:
    #     raise Exception("odd number of teams passed into pairing algorithm")

    # oppTeams = []

    team = teams[0]
    # oppTeams = [teams[i] for i in itertools.chain(range(round(n/2), n), range(round(n/2)-1,0,-1))]
    n = len(teams)
    for i in itertools.chain(range(round(n/2), n), range(round(n/2)-1,0,-1)):
        opp = teams[i]

        if (team, opp) not in previousPairings:
            tmpTeams = [t for t in teams if t not in [team, opp]]
            subResult = pairingFast(tmpTeams, previousPairings)
            if subResult is not None:
                return [(team, opp)] + subResult
    # raise Exception("No valid pairing found, need to add supplemental code for this situation TODO")
    return None

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

def playMatch(matchTeams, teams, players, model):

    a = matchTeams[0]
    b = matchTeams[1]

    whiteTeam = getWhiteTeam(matchTeams, teams)
    try:
        blackTeam = [team for team in [a,b] if team != whiteTeam][0]
    except IndexError:
        print('list index error')
        print(a)
        print(b)
        print(whiteTeam)

    # im having trouble with the code below because its giving me empty data frames, but I think Germany and Ncaragua have players

    whiteRoster = players[players.Team == whiteTeam][["Name", "Team", "Rtg"]]
    blackRoster = players[players.Team == blackTeam][["Name", "Team", "Rtg"]]


    newGame1 = [whiteRoster.iloc[0,0], whiteRoster.iloc[0,1], whiteRoster.iloc[0,2], blackRoster.iloc[0,0], blackRoster.iloc[0,1], blackRoster.iloc[0,2]]
    newGame2 = [blackRoster.iloc[1,0], blackRoster.iloc[1,1], blackRoster.iloc[1,2], whiteRoster.iloc[1,0], whiteRoster.iloc[1,1], whiteRoster.iloc[1,2]]
    newGame3 = [whiteRoster.iloc[2,0], whiteRoster.iloc[2,1], whiteRoster.iloc[2,2], blackRoster.iloc[2,0], blackRoster.iloc[2,1], blackRoster.iloc[2,2]]
    newGame4 = [blackRoster.iloc[3,0], blackRoster.iloc[3,1], blackRoster.iloc[3,2], whiteRoster.iloc[3,0], whiteRoster.iloc[3,1], whiteRoster.iloc[3,2]]

    results = [simulateGame(game[2], game[5], model) for game in [newGame1, newGame2, newGame3, newGame4]]

    newGames = pd.DataFrame( [newGame1, newGame2, newGame3, newGame4], columns = ['whiteName', 'whiteTeam', 'whiteElo', 'blackName', 'blackTeam','blackElo'])

    newGames['result'] = results

    # newGames.loc[newGames.whiteName == 'Gukesh D.', 'result'] = 1
    # newGames.loc[newGames.blackName == 'Gukesh D.', 'result'] = 0

    return newGames

'''
evaluating a pool:
1) remove any team that has played everyone
2) remove best odd team (current and next groups validate)
3) make sure pool validates after removing odd team
'''


def summarizeResults(games, teams, players, current = None):
    # print('this is the teams input', teams, 'end of teams input')
    ##Need table of games from each players perspective, and their score + team
    ##Then we can summarize the number of points each team scored in the match by looking at team points in that round

    # teams = whiteGamesCount(games, teams)

    whiteGames = games.copy()
    whiteGames['color'] = 'white'

    blackColSort = ['blackName', 'blackTeam', 'blackElo', 'whiteName', 'whiteTeam', 'whiteElo', 'result', 'round', 'board', 'EloDiff', 'EloAvg']
    blackGames = games[blackColSort].copy()
    
    blackGames.loc[:,'result'] = 1 - blackGames.result
    blackGames.loc[:,'EloDiff'] = -1 * blackGames.EloDiff
    blackGames['color'] = 'black'

    newColNames = ['playerName', 'playerTeam', 'playerElo', 'oppName', 'oppTeam', 'oppElo', \
        'result', 'round', 'board', 'EloDiff', 'EloAvg', 'color']

    completeResults = pd.DataFrame(np.concatenate(
        (whiteGames, blackGames)
        , axis = 0), columns = newColNames)
    # print(len(completeResults.playerTeam.unique()), 'fffff')
    
    ##summarize results by team, check if team played 4 games and if result matches opponent

    matchSummary = completeResults.groupby(['playerTeam', 'oppTeam', 'round']).agg(
        gp = ('result','sum'),
        ).sort_values(by = ['round', 'gp', ], ascending = True).reset_index()
    # print(len(matchSummary.playerTeam.unique()))
    # print(matchSummary, 'new game match summary')

    # im trying to figure out why current and matchSummary have dupliactes in them, please do some diagnostics below

    # print(current)
    # print(matchSummary)

    # if current is not None:
    #     matchSummary = pd.concat([current, matchSummary])

    # print(matchSummary, 'this is the match summary')
    
    mpConditions = [
        (matchSummary.gp > 2),
        (matchSummary.gp == 2),
        (matchSummary.gp < 2),
    ]
    mpValues = [2,1,0]

    matchSummary['mp'] = np.select(mpConditions, mpValues)
    matchSummary.loc[matchSummary.oppTeam == 'bye', 'mp'] = 1

    # print(matchSummary[matchSummary['round'] == 10].to_string())

    teamSummary = matchSummary.groupby(['playerTeam',]).agg(
        mpTotal = ('mp','sum'),
        ).sort_values(by = ['mpTotal', ], ascending = False).reset_index()
    # print(teamSummary.shape[0], 'teamasassdsd')

    matchSummary = matchSummary.merge(right = teamSummary, how = 'inner', on = 'playerTeam')
    matchSummary = matchSummary.merge(right = teamSummary, how = 'inner', left_on = 'oppTeam', right_on = 'playerTeam', suffixes = ('', 'Opp'))
    # print(len(matchSummary.playerTeam.unique()))
    matchSummary['ISi'] = matchSummary.gp * matchSummary.mpTotalOpp  

    teamSummary['IS(10)'] = teamSummary.playerTeam.apply(getIS10, matchSummary = matchSummary)
    teamSummary['GP'] = teamSummary.playerTeam.apply(getGP, matchSummary = matchSummary)
    teamSummary['MP(10)'] = teamSummary.playerTeam.apply(getMP10, matchSummary = matchSummary)

    teamSummary = teamSummary.rename(columns = {'playerTeam': 'team'})
    # teamSummary = teamSummary.merge(right = teams[['team', 'initRank', 'whiteCount']], how = 'inner', on = 'team')
    teamSummary = teams[['team', 'initRank', 'whiteCount']].merge(right = teamSummary, how = 'left', on = 'team')
    # print(teamSummary, 'initial team summary table')

    teamSummary = teamSummary.sort_values(by = ['mpTotal', 'IS(10)', 'GP', 'MP(10)'], ascending = False)
    teamSummary['bye'] = 0

    # print(teamSummary)
    # print(matchSummary)

    return teamSummary, matchSummary

def main(_):
    # print('Simulation: ', nSim)
    # get Olympiad players
    players = pd.read_csv('./chessSim/data/olympiad/players2024.csv')
    
    #  get teams
    teams = pd.read_csv('./chessSim/data/olympiad/teams2024.csv')
    # print(teams.shape[0], 'num temas')

    games = pd.read_csv('./chessSim/data/olympiad/games2024.csv')

    current = pd.read_csv('./chessSim/data/olympiad/matches2024.csv')
   
    # games = games.loc[games['round'] < olympiadRound] #TODO remove this, just using to test simulating future rounds. eventually want to loop through all rounds

    teams = whiteGamesCount(games, teams) #TODO: Do I need this?
    teamSummary, matchSummary = summarizeResults(games, teams, players, current) #TODO: add back after round 1
    # if matchSummary is empty DF nextRound = 1
    if matchSummary.shape[0] == 0:
        nextRound = 1
    else:
        nextRound = int(max(matchSummary['round']) + 1)
        # print('next round:', nextRound)

    # print(matchSummary)
    # print('beginning next round', max(matchSummary['round']))
    # print(teamSummary.shape[0],'number of teams in beginning')

    # print(teamSummary.to_string())

    #TODO create first round pairings, code that folows simulates remaining rounds only

    # if games.shape[0] == 0:
    #     nextRound = 1
    # else: nextRound = max(matchSummary['round']) + 1


    for pairingRound in range(nextRound, 12): # 11 rounds total, start after last round
        # print('new round: ', pairingRound)
        
        if pairingRound == 1:
            # print('first round')
            previousMatchups = set()
        elif pairingRound > 1:
            previousMatchups = set(zip(matchSummary.playerTeam, matchSummary.oppTeam))
        else: raise Exception("Pairing round number error (<1)")

        teamsMatching = teamSummary.sort_values(by = ['mpTotal', 'initRank'], ascending = [False, True]).reset_index(drop = True)
        # print(teamsMatching.to_string())
        # print(matchSummary.to_string())

        #remove bye team and find median team to find median group.
        nTeams = len(teamsMatching.team.unique())
        # print(nTeams, 'there are nteams')



        # remove odd team out and give them a bye
        byeTeam = None  #TODO does the bye team just get dropped, does it really matter?
        if nTeams % 2 > 0:
            byeTeam = teamsMatching.team[teamsMatching.bye == 0].tail(1).item()
            # print(byeTeam, type(byeTeam), 'bye team')
            teamsMatching = teamsMatching[teamsMatching.team != byeTeam]
            #TODO: add bye to byeTeams record later on
            # print('we removed a team and the new length is', teamsMatching.shape[0])



        matchups = []

        # print(pairingRound == 1, 'pairingRound')

        if pairingRound == 1:
            # print('rouind 1')
            # print(teamsMatching)
            initRankedTeams = list(teamsMatching.team)
            # print('initiral pairing list', initRankedTeams)
            matchups = makeHappyPools(initRankedTeams, [], [], previousMatchups)
            # print('round 1 matchups:', matchups)

        elif pairingRound > 1:
            # print('later rounds')
            # print('pairing roun > 1 and PR is: ', pairingRound)
            # print(teamsMatching)


            medianIndex = round(nTeams / 2) if nTeams % 2 == 0 else round(nTeams / 2 - 0.5)
            medianTeamMP = teamsMatching.iloc[medianIndex].mpTotal

            # print('median points', medianTeamMP)

            mps = teamsMatching.mpTotal.unique()
            mpsAsc = np.sort(mps)
            mpsDesc = -np.sort(-mps)
            
            #create initial pools
            topPools = []
            bottomPools = []
            medianPool = []

            # medianPool.append([teamsMatching[(teamsMatching.mpTotal == medianTeamMP)].team])

            for mp in [mp for mp in mpsDesc if mp > medianTeamMP]: # create top half of pools
                mpPool = teamsMatching[(teamsMatching.mpTotal == mp)]
                mpPool = mpPool.sort_values(by = ['mpTotal', 'initRank'], ascending = [False, True])
                # print(mpPool, 'this is the one')
                topPools.append(list(mpPool.team))

            for mp in [mp for mp in mpsAsc if mp < medianTeamMP]: # create botttom half of pools
                mpPool = teamsMatching[(teamsMatching.mpTotal == mp)]
                mpPool = mpPool.sort_values(by = ['mpTotal', 'initRank'], ascending = [False, True])
                bottomPools.append(list(mpPool.team))

            for mp in [mp for mp in mpsDesc if mp == medianTeamMP]: # create botttom half of pools
                mpPool = teamsMatching[(teamsMatching.mpTotal == mp)]
                mpPool = mpPool.sort_values(by = ['mpTotal', 'initRank'], ascending = [False, True])
                medianPool.append(list(mpPool.team))
            # print(bottomPools, ' this is the bottom')
            # print('len bottom', len(bottomPools[0]))
            
            # if pairingRound ==2:
            #     print(medianPool)

            # print('number of pooled teams:', len([team for pool in topPools+medianPool+bottomPools for team in pool]))
            # print('number of pre pool teams', nTeams)
            # print(teamsMatching.shape[0])

            # print(topPools, 'here it is')

            allPoolsDiagnostic = topPools + medianPool + bottomPools
            pairingDiagnostics(matchups, previousMatchups, allPoolsDiagnostic, verbose = True) #Diagnostic to evlauate pairing process heuristics

            matchups = makeHappyPools(topPools, bottomPools, medianPool, previousMatchups)

            # print('round', pairingRound, 'matchups:', matchups)
            # print('-------------')

            # if pairingRound == 6:
            #     # print(bottomPools, ' this is the bottom')
            #     print(matchups)
            # print('number of matches made', len(matchups))
# 
        else: raise Exception("Pairing round number error (<1)")
        # print(matchups)

        newGamesList = []
        for matchPair in matchups:
            if matchPair[0] == matchPair[1]:
                raise Exception("Why is the same team playing itself?")
            newGames = playMatch(matchPair, teams, players, bst)
            newGames['round'] = pairingRound
            newGames['board'] = [1,2,3,4]
            newGames['EloDiff'] = newGames.whiteElo - newGames.blackElo
            newGames['EloAvg'] =((newGames.whiteElo + newGames.blackElo) / 2 ).astype(int)
            newGamesList.append(newGames)

        # print(matchups)
        # print(newGamesList, 'new games')

        if games.shape[0] == 0:
            games = pd.concat(newGamesList)
        else:
            games = pd.concat([games] + newGamesList)
        # print(games.shape[0], 'game rows')

        teamSummary, matchSummary = summarizeResults(games, teams, players, current)
        # print('completed round')
        # print(teamSummary, matchSummary)


    a, b = summarizeResults(games, teams, players, current)

    # # # print(b[b.playerTeam=='Russia'])
    # a_tenrows = a.head(10)
    # print(a_tenrows.to_string())

    # # b tenrows
    # b_tenrows = b.head(10)
    # print(b_tenrows.to_string())

    # print all rows of b where playerTeam = lookupTeam

    # lookupTeam = 'Vietnam'
    # print(b[b.playerTeam == lookupTeam].to_string())

    
    # print(a.mpTotal.sum())
    # print((a.team.iloc[0], a.team.iloc[1], a.team.iloc[2]))
    return (a.team.iloc[0], a.team.iloc[1], a.team.iloc[2])

    # print(a)
    # print(b.sort_values(by = 'mpTotal', ascending = False))

if __name__ == "__main__":
    main(0)