from collections import deque
from typing import Tuple
from PIL import Image
import cards, pygame, copy

'''
FOR NEXT TIME!
- Clean up code, make many different functions
- Turn the deck into a stack rather than its own thing
- Make entire stacks draggable
'''


# TEST - DELETE PLZ
def stringcards(cards):
    string = ''
    for card in cards:
        string = f'{string}, {card.card}'
    return string

# Dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_CENTER = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
CARD_SIZE = (130, 200)
stacking_distance_percentage = 0.25
stacking_bounds = (int(stacking_distance_percentage * CARD_SIZE[0]), int(stacking_distance_percentage * CARD_SIZE[1]))

# Colors and images
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BACKGROUND_COLOR = WHITE
CARD_BACK = pygame.transform.scale(pygame.image.load('images/red_back.png'), CARD_SIZE)

# Sprite Classes
class Card(pygame.sprite.Sprite):
    def __init__(self, card: Tuple, facedown = False):
        pygame.sprite.Sprite.__init__(self)
        self.card = card
        self.facedown = facedown
        self.stack = None
        if facedown:
            self.image = CARD_BACK
        else:
            self.image = get_card_image(card)
        self.rect = self.image.get_rect()
        self.rect.center = SCREEN_CENTER
    def flip(self):
        if self.facedown:
            self.image = get_card_image(self.card)
            self.facedown = False
        else:
            self.image = CARD_BACK
            self.facedown = True

class Stack:

    stack_count = 0

    def __init__(self, top: Card, bottom: Card):
        # Definitions
        self.cards = deque()
        self.top = bottom
        # Actions
        Stack.stack_count += 1
        self.num = Stack.stack_count
        self.add(bottom)
        self.add(top)

    def stack(self, card: Card):
        card.rect = copy.copy(self.top.rect)
        self.top = card

    def add(self, card: Card):
        cards.place(card, self.cards)
        card.stack = self
        self.stack(card)
        print(f'Added to stack #{self.num}: {stringcards(self.cards)}')

    def take(self):
        print(f'Removed {cards.draw(self.cards).card} from stack #{self.num}')
        self.top = self.cards[0]
        if len(self.cards) <= 1:
            for card in self.cards:
                card.stack = None

    def __del__(self): # Deconstructor--delete this later, only for testing purposes now
        print('Deleting stack now...')

class Deck:
    def __init__(self, deck = cards.create_deck()):
        self.deck = deck
        cards.shuffle(self.deck)
        self.top = Card(deck[0])
        self.rect = copy.copy(self.top.rect)
    def take_card(self):
        '''
        This should be called when a card is dragged away from the graphical deck.
        The card is 'drawn' from the deck in memory and the on-screen pile is updated.
        '''
        cards.draw(self.deck) # Removes the card from the deck in memory
        self.top = Card(self.deck[0])
        card_sprites.add(self.top)

# Functions
def get_card_image(card: Tuple):
    '''
    Returns the image file of the associated card.\n
    Cards are stored as tuples with format (suit, rank).\n
    Image files from http://acbl.mybigcommerce.com/52-playing-cards/
    '''
    filename = f'{card[1]}{card[0]}.png'
    return pygame.transform.scale(pygame.image.load(f'images/{filename}'), CARD_SIZE)

# Screen initiation
pygame.init()
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption('Playing Cards')
screen.fill(BACKGROUND_COLOR)

# Deck initializion
card_sprites = pygame.sprite.LayeredUpdates()
deck = cards.create_deck()

# Main
def main():
    # Local variables
    drag = False
    mouse_down = False
    selected = None

    # Sprites
    deck_sprite = Deck()
    card_sprites.add(deck_sprite.top)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                    # Find which card was selected by user
                    for card in card_sprites:
                        if card.rect.collidepoint(event.pos):
                            selected = card
                    if selected == None and deck_sprite.rect.collidepoint(event.pos):
                        selected = deck_sprite.top
                    # Move selected card to the top and set offset
                    if selected != None:
                        card_sprites.change_layer(selected, 1)
                        mouse_x, mouse_y = event.pos
                        offset_x = selected.rect.x - mouse_x
                        offset_y = selected.rect.y - mouse_y

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    # Only is activated if other clicks on an actual card
                    if selected != None:
                        # If the user has just clicked on the card without dragging, the card is flipped; otherwise the else clause is activated
                        if not drag:
                            selected.flip()
                        else:
                            for card in card_sprites:
                                # Checks if the selected card overlapped another card within the stacking bounds
                                if abs(card.rect.center[0] - selected.rect.center[0]) <= stacking_bounds[0] and abs(card.rect.center[1] - selected.rect.center[1]) <= stacking_bounds[1] and card != selected:
                                    # Creates a new stack if the card being stacked on is not part of a stack
                                    if card.stack == None:
                                        print('New Stack!')
                                        card.stack = Stack(selected, card)
                                    # Add to existing stack if there is one already
                                    else:
                                        card.stack.add(selected)
                                    break
                        drag = False
                        card_sprites.change_layer(selected, 0)
                        selected = None
                
            if event.type == pygame.MOUSEMOTION:
                # Drag an item if selected
                if mouse_down and selected != None and not drag:
                    drag = True
                if drag:
                    # If the selected card is taken from the top of the draw deck, remove it from the deck
                    if selected == deck_sprite.top:
                        deck_sprite.take_card()
                        print(f'Deck Size: {len(deck_sprite.deck)}')
                    # If the selected card was part of a stack (merge with above code later)
                    elif selected.stack != None:
                        selected.stack.take()
                        selected.stack = None
                    
                    # Update selected card sprite position
                    mouse_x, mouse_y = event.pos
                    selected.rect.x = mouse_x + offset_x
                    selected.rect.y = mouse_y + offset_y
        
        # Update
        card_sprites.update()
        
        # Draw
        screen.fill(BACKGROUND_COLOR)
        card_sprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()