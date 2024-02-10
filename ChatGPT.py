import random

from LoLTournament import Tournament

t = Tournament(25, 5, 3)

for i in range(25 * 5):
    t.register_player(f"Player {i}")

print(t.main())
