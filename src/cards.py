import itertools, random
from collections import deque
from typing import Deque, List

# Default suits and ranks, but players can create custom decks with the 'createdeck' function
SUITS = ('C', 'S', 'H', 'D')
RANKS = ('A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K')
RANK_VALUES = {RANKS[i]: i+1 for i in range(len(RANKS))}

class Player:
    total_players = 0
    def __init__(self, name = 'Player'):
        Player.total_players += 1
        self.hand = list()
        self.number = Player.total_players
        self.name = name
        print(f'Player {self.number}, AKA {self.name}, initiated.')

class Rules:
    def __init__(self, win_type: int, round_collection_type: int, viewable_cards: bool):
        self.win_type = win_type #win_type will be an int that determines how the game ends (run out of cards, pick a certain card, last one standing, etc.)
        self.round_collection_type = round_collection_type #round_collection_type will be an int that determines how cards are collected each round (trick collected, no collection, etc.)
        self.viewable_cards = viewable_cards #viewable_cards flags whether or not players can see their cards after cards are dealt

class Game:
    def __init__(self, playercount: int, deck: List, rules: Rules):
        self.playercount = playercount
        self.deck = deck
        self.rules = rules

def create_deck(suits = SUITS, ranks = RANKS, jokers = 0):
    deck = deque(itertools.product(suits, ranks))
    for i in range(jokers):
        deck.append('Joker')
    return deck

def shuffle(deck):
    random.shuffle(deck)

def deal(deck: List, players: List[Player], cards_per_player = 0):
    '''
    Deals a given deck to given list of players.\n
    Cards are dealt equally unless given otherwise (0 is used as default argument to indicate that cards are dealt equally).\n
    If cards per player is set too high, automatically deals equally.
    '''
    deck_size = len(deck)
    player_count = len(players)

    #If deck is meant to be dealt equally, finds the amount of cards to deal
    def dealequally(deck_size, player_count):
        if player_count > deck_size:
            raise RuntimeError('Too many players')
        if deck_size % player_count == 0:
            return deck_size / player_count
        return dealequally(deck_size-1, player_count)
    
    if cards_per_player > 0:
        if cards_per_player * player_count > deck_size:
            print("Deck too small to deal appropriate cards, dealing equally instead...")
        else:
            for i in range(cards_per_player):
                for player in players:
                    player.hand.append(deck.pop())
            return cards_per_player
    
    cards_per_player = int(dealequally(deck_size, player_count))

    for i in range(cards_per_player):
        for player in players:
            player.hand.append(deck.pop())

    return cards_per_player

def draw(deck: deque):
    return deck.popleft()

def place(card, deck: Deque, position = 'top'):
    '''
    Places a card into a deck at a given position.
    The default position is the top of the deck (position 0).
    Position argument can also be 'top' or 'bottom' to insert the card at one end of the deck, or 'random' to put in a random place
    '''
    if position == 'top':
        return deck.insert(0, card)
    elif position == 'bottom':
        return deck.append(card)
    elif position == 'random':
        position = random.randint(0, len(deck)-1)
    deck.insert(position, card)

def draw_random(deck: List):
    return deck.pop(random.randint(0, len(deck)-1))

def aces_high(flag: bool):
    if flag:
        RANK_VALUES['A'] = 14
    else:
        RANK_VALUES['A'] = 1

def set_rank_value(rank, value):
    RANK_VALUES[rank] = value