#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random

def db_and_new_cursor():
	db = connect()
	cursor = db.cursor()
	return db, cursor

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def deleteTournaments():
    """Remove all of the tournament records from the database."""
    db, cursor = db_and_new_cursor()
    cursor.execute("delete from tournamentRegistration; "
        "delete from tournament;")
    db.commit()
    db.close()

def countTournaments():
    db, cursor = db_and_new_cursor()
    cursor.execute("select count(*) from tournament;")
    rows = cursor.fetchall()
    db.close()
    return rows[0][0]

def createTournament(name):
    """Adds a tournament to the tournament table.

    The database assigns a unique serial id number for the tournament. 
    The name argument must be unique in the tournament table.

    Args:
        name: the tournament's name (needs to be unique)

    Returns:
        The id number of the tournament being created
    """

    db,cursor = db_and_new_cursor()
    cursor.execute("insert into tournament (id, name)"
        "values (DEFAULT, %s)"
        "returning id", (name,))
    rows = cursor.fetchall()
    db.commit()
    db.close()
    return rows[0][0]

def deleteMatches():
    """Remove all the match records from the database."""
    db, cursor = db_and_new_cursor()
    cursor.execute("delete from match;")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db, cursor = db_and_new_cursor()
    cursor.execute("delete from player;")
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db, cursor = db_and_new_cursor()
    cursor.execute("select count(*) from player;")
    rows = cursor.fetchall()
    db.close()
    return rows[0][0]

def registerPlayer(name, tournamentID):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
      tournamentID: the id number of the tournament the player is joining
    """
    db, cursor = db_and_new_cursor()
    cursor.execute("with player_id as (insert into player (id, name)"
        "values (DEFAULT, %s)"
        "returning id)"
        "insert into tournamentRegistration (tournament, player)"
        "values (%s, (select id from player_id))", (name, tournamentID,))
    db.commit()
    db.close()

def allStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player with the highest 
    total wins, or a player tied for highest wins.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db, cursor = db_and_new_cursor()
    cursor.execute("select id, name, wins, matches from fullStanding;")
    rows = cursor.fetchall()
    db.close()
    return rows

def fullStandings(tournamentID):
    """Returns a list of the players and their win records, 
        sorted by wins, for a specific tournament.

    The first entry in the list should be the player in first place, or a 
    player tied for first place if there is currently a tie.

    Args:
        tournamentID: the id number of the tournament for which standings 
        are requested

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db, cursor = db_and_new_cursor()
    cursor.execute("select id, name, wins, matches from fullStanding "
        "where tournament = %s;", (tournamentID,))
    rows = cursor.fetchall()
    db.close()
    return rows


def reportMatch(tournamentID, player1, player2, winner):
    """Records the outcome of a single match between two players.
    Note: a bye is recorded for a player with player1, player2, 
    and winner arguments the same

    Args:
        tournamentID: the id number of the tournament the match is for
        player1:  the id number of player 1
        player2:  the id number of player 2
        winner: the id number of the player who won (null if tied)
    """
    db, cursor = db_and_new_cursor()
    cursor.execute("insert into match (tournament, player1, player2, winner) "
        "values (%s, %s, %s, %s);", (tournamentID, player1, player2, winner))
    db.commit()
    db.close()
 
def swissPairings(tournamentID):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    db, cursor = db_and_new_cursor()
    cursor.execute("select id, name from fullStanding "
        "where tournament = %s order by wins desc, omw desc;", (tournamentID,))
    players = cursor.fetchall()
    # If there is an odd number of players
    # give a bye to one of the players and return remaining players
    if len(players) % 2 == 1:
        players = playersAfterGivingBye(players, tournamentID)

    # Array to build pairings
    pairings = []

    # Get all valid pairings
    cursor.execute("select player1, player2 "
        "from tournamentUniquePairing where tournament = %s;", (tournamentID,))
    uniquePairings = cursor.fetchall()

    while len(players) != 0:
        first = players.pop(0)
        # Take first player and iterate through the rest
        # checking 
        for i in range(len(players)):
            second = players[i]
            # Create pair if it's a valid pairing
            # or if it's the last option
            if (first[0], second[0]) in uniquePairings \
            or i == len(players) - 1:
                players.pop(i)
                pairings.append((first[0], first[1], second[0], second[1]))
                break
    db.close()
    return pairings

def playersAfterGivingBye(players, tournamentID):
    """Returns a list of pair of players from an odd-list of players. 
        One random player is awarded a bye

    Args:
        players: a odd list of players, among which one bye will be given
        tournamentID: the tournament in which the bye is given
    Returns:
        A even list of players without the one player given a bye
    """
    db, cursor = db_and_new_cursor()
    # Get matches already reported
    cursor.execute("select player1, player2, winner from match "
        "where tournament = %s", (tournamentID,))
    matches = cursor.fetchall()

    # Randomize a list of indices for the player list
    indices = range(len(players))
    random.shuffle(indices)

    # Only give a bye if not given one before
    # in the tournament, or if it's the last player in the list
    for i in indices:
        id = players[i][0]
        if (id, id, id) not in matches or i == len(players) - 1:
            reportMatch(tournamentID, id, id, id)
            # return the list without the player given a bye
            return players[:i] + players[i+1:]

def countWins(tournamentID):
    """Return the number of wins within the tournament

    Args:
        tournamentID: the id number of the tournament to observe
    Returns:
        A count of the wins in the tournament
    """

    db, cursor = db_and_new_cursor()
    cursor.execute("select count(winner) as wins from match "
        "where tournament = %s", (tournamentID,))
    return cursor.fetchall()[0][0]
