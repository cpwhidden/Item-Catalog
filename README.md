# Tournament Calculator

This back-end app organizes data and logic for a swiss-system game tournament in a PostgreSQL database with a Python interface.

# How to use

1. Download [Vagrant](www.vagrantup.com), [VirtualBox](www.virtualbox.org), and [Python](www.python.org) if not already installed.
2. Fork this project
3. Navigate to `/vagrant/tournament/` within the project
4. Start the Vagrant virtual machine with `vagrant up` at the command line.
5. Login to the virtual machine with `vagrant ssh`
6. To test the logic of the database application, run `python tournament_test.py`
7. To directly work with with the database, enter PostgreSQL using `psql` then connect to the database with `\c tournament`
8. Table and view declarations are place in the `tournament.sql` file
9. A front-end app can use the database interface via the `tournament.py` file.

# Features
* Calculates Swiss-system tournament pairings
* Handles multiple tournaments
* Handles ties and byes (for tournaments with odd numbers of players)
* Handles tie-breakers by calculating opponent match wins
* Prevents rematches in a tournament