#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *

def testDeleteTournaments():
    deleteTournaments()
    print "0a. Old tournaments can be deleted."

def testCountTournaments():
    deleteTournaments()
    c = countTournaments()
    if c == '0':
        raise TypeError(
            "testCountTournaments() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countTournaments should return zero.")
    print "0b. After deleting, countTournaments() returns zero."

def testCreateTournament():
    deleteTournaments()
    createTournament("Test Tournament")
    c = countTournaments()
    if c != 1:
        raise ValueError(
            "After a tournament is created, countTournaments() should be 1.")
    print "0c. After creating a tournament, countTournaments() returns 1."

def testDeleteMatches():
    deleteTournaments()
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteTournaments()
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteTournaments()
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."

def testRegister():
    deleteTournaments()
    deleteMatches()
    deletePlayers()
    tournamentID = createTournament("Test Tournament")
    registerPlayer("Chandra Nalaar", tournamentID)
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteTournaments()
    deleteMatches()
    deletePlayers()
    tournamentID = createTournament("Test Tournament")
    registerPlayer("Markov Chaney", tournamentID)
    registerPlayer("Joe Malik", tournamentID)
    registerPlayer("Mao Tsu-hsi", tournamentID)
    registerPlayer("Atlanta Hope", tournamentID)
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteTournaments()
    deleteMatches()
    deletePlayers()
    tournamentID = createTournament("Test Tournament")
    registerPlayer("Melpomene Murray", tournamentID)
    registerPlayer("Randy Schwartz", tournamentID)
    # Test for any tournament because matches have not been created
    standings = allStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each allStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteTournaments()
    deleteMatches()
    deletePlayers()
    tournamentID = createTournament("Test Tournament")
    registerPlayer("Bruno Walton", tournamentID)
    registerPlayer("Boots O'Neal", tournamentID)
    registerPlayer("Cathy Burton", tournamentID)
    registerPlayer("Diane Grant", tournamentID)
    # Test for any tournament because matches have not been created
    standings = allStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tournamentID, id1, id2, id1)
    reportMatch(tournamentID, id3, id4, id3)
    standings = fullStandings(tournamentID)
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteTournaments()
    deleteMatches()
    deletePlayers()
    tournamentID = createTournament("Test Tournament")
    registerPlayer("Twilight Sparkle", tournamentID)
    registerPlayer("Fluttershy", tournamentID)
    registerPlayer("Applejack", tournamentID)
    registerPlayer("Pinkie Pie", tournamentID)
    # Test for any tournament because matches have not been created
    standings = allStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(tournamentID, id1, id2, id1)
    reportMatch(tournamentID, id3, id4, id3)
    pairings = swissPairings(tournamentID)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."

def testOddNumberPlayers():
    deleteTournaments()
    deleteMatches()
    deletePlayers()
    tournamentID = createTournament("Test Tournament")
    registerPlayer("Twilight Sparkle", tournamentID)
    registerPlayer("Fluttershy", tournamentID)
    registerPlayer("Applejack", tournamentID)
    registerPlayer("Pinkie Pie", tournamentID)
    registerPlayer("Summer Sunshine", tournamentID)
    standings = allStandings()
    [id1, id2, id3, id4, id5] = [row[0] for row in standings]
    reportMatch(tournamentID, id1, id2, id1)
    reportMatch(tournamentID, id3, id4, id3)
    pairings = swissPairings(tournamentID)
    if len(pairings) != 2:
        raise ValueError(
            "For five players, swissPairings should return two pairs.")
    wins = countWins(tournamentID)
    if wins != 3:
        raise ValueError(
            "For five players after one round, countWins should return 3.")
    print "9. For five players after one match, there are two pairings and three wins."


if __name__ == '__main__':
    testDeleteTournaments()
    testCountTournaments()
    testCreateTournament()
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    testOddNumberPlayers()
    print "Success!  All tests pass!"


