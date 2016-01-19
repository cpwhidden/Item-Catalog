-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Player in a tournament
create table player(
	id serial primary key,
	name text not null
);

-- Basic tournament entity
create table tournament(
	id serial primary key,
	name text not null unique
);

-- Weak table connecting players to tournaments
create table tournamentRegistration(
	tournament serial references tournament(id) on delete cascade,
	player serial references player(id) on delete cascade,
	primary key(tournament, player)
);

-- Records of matches within a tournament
-- If winner is null, the match was a tie
-- If player1, player2, and winner are the same, it was a bye
create table match(
	tournament serial references tournament(id) on delete cascade,
	player1 serial references player(id) on delete cascade,
	player2 serial references player(id) on delete cascade,
	winner serial references player(id) on delete cascade,
	primary key(tournament, player1, player2)
);

-- Union of all matches whether the player is recorded as player 1 or 2
create view matchPermutation as(
	select tournament, player1, player2, winner
	from match
	union
	select tournament, player2, player1, winner
	from match
);

-- Find all opponents to a players in matches in a tournament
create view tournamentOpponent as(
	select tournamentRegistration.tournament, tournamentRegistration.player, player2 as opponent
	from tournamentRegistration
	left join matchPermutation on tournamentRegistration.player = player1
);

-- Count wins and total matches for a player in a tournament
create view tournamentStatistics as(
	select tournament, player1 as player, count(case when player1 = winner then 1 else null end) as wins, count(*) as matches
	from matchPermutation
	group by tournament, player
);

-- Find all player standings without opponent match wins
create view partialStanding as(
	select id, player.name, tournamentRegistration.tournament, coalesce(wins, 0) as wins, coalesce(matches, 0) as matches
	from player
	left join tournamentRegistration on player.id = tournamentRegistration.player
	left join tournamentStatistics on player.id = tournamentStatistics.player 
	and tournamentRegistration.tournament = tournamentStatistics.tournament
	order by wins desc
);

-- Count wins from all opponents that a player has played against
-- in a tournament
create view opponentMatchWins as(
	select tournamentOpponent.player, tournamentOpponent.tournament, sum(wins) as omw
	from tournamentOpponent
	left join partialStanding on tournamentOpponent.opponent = partialStanding.id
	group by tournamentOpponent.player, tournamentOpponent.tournament
);

-- Find all player standings including opponent match wins
-- to calculate tie breakers
create view fullStanding as(
	select partialStanding.id, name, partialStanding.tournament, wins, matches, omw
	from partialStanding 
	left join opponentMatchWins on partialStanding.id = opponentMatchWins.player and partialStanding.tournament = opponentMatchWins.tournament
	order by wins desc, omw desc
);

-- Find all valid pairings for future matches in a tournament
create view tournamentUniquePairing as(
	select r1.tournament, r1.player as player1, r2.player as player2
	from tournamentRegistration r1, tournamentRegistration r2
	where r1.player != r2.player
	and (r1.tournament, r1.player, r2.player) not in (select tournament, player1, player2 from matchPermutation)
);