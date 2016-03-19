"""
Program do gry w Blackjack (a.k.a. Oczko) w języku Python przy użyciu biblioteki PyGame
Projekt zaliczeniowy - Języki Skryptowe, Informatyka i Ekonometria, rok 1, WZ, AGH
Autorzy: Joanna Jeziorek, Mateusz Koziestański, Katarzyna Maciocha
III 2016
"""

import random as rd
import pygame
import sys
import os
from pygame.locals import *

pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((800, 480))
clock = pygame.time.Clock()

aces = ['ki_a', 'ka_a', 'pi_a', 'tr_a']

def load_image(imgname, card):
    if card == 1:
        fullname = os.path.join("obrazy/", imgname)
    else: fullname = os.path.join('obrazy', imgname)
    
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print ('Nie można zaladować obrazu:', imgname)
        raise (SystemExit, message)
    image = image.convert()
    
    return image, image.get_rect()
    
    
def display(font, sentence):
    """ Wyswietlacz tekstu na dole ekranu. Tekst sluży do informowania gracza o tym co sie dzieje."""
    
    display_font = pygame.font.Font.render(font, sentence, 1, (255,255,255), (0,0,0))
    return display_font

# =============Funkcje logiki gry==================

def game_over():
        """ 
        Jesli graczowi skoncza sie pieniadze, wyswietla ekran koncowy. Gracz moze tylko zamknac gre.
        """
        
        while 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    sys.exit()

           # Czarny ekran
            screen.fill((0,0,0))
            
            # Napis Koniec Gry
            oFont = pygame.font.Font(None, 50)
            display_font = pygame.font.Font.render(oFont, "Koniec gry! Skonczyly ci sie pieniadze!", 1, (255,255,255), (0,0,0)) 
            screen.blit(display_font, (125, 220))

            pygame.display.flip()


def create_deck():
    """
    Tworzy talię kart nazwanych w konwencji [dwie pierwsze litery koloru]_[karta],
    po czym zwraca talię
    a = as, k = król, d = dama, w = walet
    """
    deck = ['ki_a', 'ki_k', 'ki_d', 'ki_w',
            'ka_a', 'ka_k', 'ka_d', 'ka_w',
            'tr_a', 'tr_k', 'tr_d', 'tr_w',
            'pi_a', 'pi_k', 'pi_d', 'pi_w']

    for x in range(2, 11):
        kier = 'ki_' + str(x)
        karo = 'ka_' + str(x)
        trefl = 'tr_' + str(x)
        pik = 'pi_' + str(x)

        for kolor in [kier, karo, trefl, pik]:
            deck.append(kolor)

    return deck


def shuffle(deck):
    # Przyjmuje talię jako argument i zwraca potasowaną talię. Tasowanie metodą random.shuffle().
    rd.shuffle(deck)
    return deck


def return_played(deck, played_deck):
    # Przekazuje zagrane obrazy do głównej talii.
    # Zwraca potasowaną talię i pustą talię zagranych kart.


    for card in played_deck:
        deck.append(card)
        del card
    shuffle(deck)
    return deck, played_deck


def deck_deal(deck, played_deck):
    # Jeśli talia nie jest pusta, rozdaje pierwsze cztery obrazy z talii na przemian graczowi i krupierowi.
    # Zwraca kolejno: talię, zagraną talię, rękę gracza i rękę krupiera
    dealer_hand, player_hand = [], []

    if not deck:
        return_played(deck, played_deck)

    dealer_hand.append(deck.pop(i=0))
    player_hand.append(deck.pop(i=0))
    dealer_hand.append(deck.pop(i=0))
    player_hand.append(deck.pop(i=0))

    return deck, played_deck, player_hand, dealer_hand


def hit(deck, played_deck, hand):
    # Jeśli talia nie jest pusta, daje graczowi kartę do ręki.
    if not deck:
        return_played(deck,played_deck)

    hand.append(deck.pop(i=0))
    return deck, played_deck, hand


def value(hand):
    # Oblicza wartość kart w ręce.
    # Jeśli w ręce znajduje się as, a wartość przekracza 21, zmienia wartość asa z 11 do 1pkt.
    # WYMAGA POPRAWKI w sytuacji gdy w ręce jest kilka asów.
    value_total = 0
    for card in hand:
        if card[3] == 'a':
            value_total += 11
        elif card[3] in ['k', 'd', 'w', '1']:
            value_total += 10
        else:
            value_total += int(card[3])

    if value_total > 21:
            for card in hand:
                if card[3] == 'a': 
                    value_total -= 10
                if value_total <= 21:
                    break
                else:
                    continue
    return value_total


def round_end(deck, player_hand, dealer_hand, played_deck, funds, money_gain, money_loss, cards, card_sprite):

    if len(player_hand) == 2 and player_hand[:1] in aces:
        money_gain += (money_gain*3 /2.0)

    cards.empty()

    dCardPos = (50, 70)

    for x in dealer_hand:
        card = CardSprite(x, dCardPos)
        dCardPos = (dCardPos[0] + 80, dCardPos [1])
        cards.add(card)

    # Remove the cards from the player's and dealer's hands
    for card in player_hand:
        played_deck.append(dealer_hand.pop(card))
    for card in dealer_hand:
        played_deck.append(player_hand.pop(card))

    funds += money_gain
    funds -= money_loss

    display_font = pygame.font.Font(None, 28)

    if funds <= 0:
        game_over()

    end_round = 1

    return deck, player_hand, dealer_hand, played_deck, funds, end_round


def compare(deck, played_deck, player_hand, dealer_hand, funds, bet):
    pv, dv = value(player_hand), value(dealer_hand)
    while dv < 17:
        deck, played_deck, dealer_hand = hit(deck, played_deck, dealer_hand)
        dv = value(dealer_hand)

    if dv < pv <= 21:
        # Gracz wygrywa
            funds += 2*bet
            deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand, played_deck, funds, bet, 0, cards, CardSprite)
            display_font = display(display_font, "Wygrana: $%.2f." %bet)
        elif pv == dv and pv <= 21:
            # Remis
            deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand, played_deck, funds, 0, 0, cards, CardSprite)
            display_font = display(display_font, "Remis!")
        elif dv > 21 >= pv:
            # Krupier przebił, a gracz nie
            deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand, played_deck, funds, bet, 0, cards, CardSprite)
            display_font = display(display_font, "Krupier przebił! Wygrana: $%.2f." %bet)
        else:
            # W każdej innej sytuacji krupier wygrywa
            deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand, played_deck, funds, 0, bet, cards, CardSprite)
            display_font = display(display_font, "Krzupier wygrywa! Przegrana $%.2f." %bet)

        return deck, played_deck, end_round, funds, display_font

# ==============Koniec logiki gry===============
class CardSprite(pygame.sprite.Sprite):
        """ Sprite wyświetlający określoną kartę. """

        def __init__(self, card, position):
            pygame.sprite.Sprite.__init__(self)
            cardImage = card + ".png"
            self.image, self.rect = load_image(cardImage, 1)
            self.position = position
        def update(self):
            self.rect.center = self.position

class BetButtonUp(pygame.sprite.Sprite):
        """ Guzik zwiększający zakład """

        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = load_image("up.png", 0)
            self.position = (710, 255)

        def update(self, mX, mY, bet, funds, click, end_round):
            if end_round == 1:self.image, self.rect = load_image("up.png", 0)
            else: self.image, self.rect = load_image("up-grey.png", 0)

            self.position = (710, 255)
            self.rect.center = self.position

            if self.rect.collidepoint(mX, mY) == 1 and click == 1 and end_round == 1:
                

                if bet < funds:
                    bet += 5.0
                    if bet % 5 != 0:
                        while bet % 5 != 0:
                            bet -= 1

                click = 0

            return bet, click

class BetButtonDown(pygame.sprite.Sprite):
        """ Guzik zmniejszający zakład """

        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = load_image("down.png", 0)
            self.position = (710, 255)

        def update(self, mX, mY, bet, click, end_round):
            if end_round == 1: self.image, self.rect = load_image("down.png", 0)
            else: self.image, self.rect = load_image("down-grey.png", 0)

            self.position = (760, 255)
            self.rect.center = self.position

            if self.rect.collidepoint(mX, mY) == 1 and click == 1 and end_round == 1:
                if bet > 5:
                    bet -= 5.0
                    if bet % 5 != 0:
                        while bet % 5 != 0:
                            bet += 1

                click = 0

            return bet, click


class HitButton(pygame.sprite.Sprite):
        """ Guzik pozwalający graczowi dobrać kartę z talii. """

        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = load_image("hit-grey.png", 0)
            self.position = (735, 400)

        def update(self, mX, mY, deck, played_deck, player_hand, cards, pCardPos, end_round, CardSprite, click):
            """ If the button is clicked and the round is NOT over, Hits the player with a new card from the deck. It then creates a sprite
            for the card and displays it. """

            if end_round == 0: self.image, self.rect = load_image("hit.png", 0)
            else: self.image, self.rect = load_image("hit-grey.png", 0)

            self.position = (735, 400)
            self.rect.center = self.position

            if self.rect.collidepoint(mX, mY) == 1 and click == 1:
                if end_round == 0:

                    deck, played_deck, player_hand = hit(deck, played_deck, player_hand)

                    current_card = len(player_hand) - 1
                    card = CardSprite(player_hand[current_card], pCardPos)
                    cards.add(card)
                    pCardPos = (pCardPos[0] - 80, pCardPos[1])

                    click = 0

            return deck, played_deck, player_hand, pCardPos, click

class StandButton(pygame.sprite.Sprite):
        """ Guzik umożliwiający graczowi zostanie przy obecnej liczbie kart. """

        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = load_image("stand-grey.png", 0)
            self.position = (735, 365)

        def update(self, mX, mY, deck, played_deck, player_hand, dealer_hand, cards, pCardPos, end_round, CardSprite, funds, bet, display_font):
            """ If the button is clicked and the round is NOT over, let the player stand (take no more cards). """

            if end_round == 0: self.image, self.rect = load_image("stand.png", 0)
            else: self.image, self.rect = load_image("stand-grey.png", 0)

            self.position = (735, 365)
            self.rect.center = self.position

            if self.rect.collidepoint(mX, mY) == 1:
                if end_round == 0:

                    deck, played_deck, end_round, funds, display_font = compare(deck, played_deck, player_hand, dealer_hand, funds, bet, cards, CardSprite)

            return deck, played_deck, end_round, funds, player_hand, played_deck, pCardPos, display_font

class DoubleButton(pygame.sprite.Sprite):
        """ Guzik umożliwiający graczowi podwojenie zakładu i wzięcie jedynej dodatkowej karty."""

        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = load_image("double-grey.png", 0)
            self.position = (735, 330)

        def update(self, mX, mY,   deck, played_deck, player_hand, dealer_hand, playerCards, cards, pCardPos, end_round, CardSprite, funds, bet, display_font):
            """ If the button is clicked and the round is NOT over, let the player stand (take no more cards). """

            if end_round == 0 and funds >= bet * 2 and len(player_hand) == 2: self.image, self.rect = load_image("double.png", 0)
            else: self.image, self.rect = load_image("double-grey.png", 0)

            self.position = (735, 330)
            self.rect.center = self.position

            if self.rect.collidepoint(mX, mY) == 1:
                if end_round == 0 and funds >= bet * 2 and len(player_hand) == 2:
                    bet = bet * 2


                    deck, played_deck, player_hand = hit(deck, played_deck, player_hand)

                    current_card = len(player_hand) - 1
                    card = CardSprite(player_hand[current_card], pCardPos)
                    playerCards.add(card)
                    pCardPos = (pCardPos[0] - 80, pCardPos[1])

                    deck, played_deck, end_round, funds, display_font = compare(deck, played_deck, player_hand, dealer_hand, funds, bet, cards, CardSprite)

                    bet = bet / 2

            return deck, played_deck, end_round, funds, player_hand, played_deck, pCardPos, display_font, bet

class DealButton(pygame.sprite.Sprite):
        """ Guzik umożliwiający rozpoczęcie nowej rundy / rozdania """

        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = load_image("deal.png", 0)
            self.position = (735, 450)

        def update(self, mX, mY, deck, played_deck, end_round, CardSprite, cards, player_hand, dealer_hand, dCardPos, pCardPos, display_font, playerCards, click, handsPlayed):
            """ If the mouse position collides with the button, and the mouse is clicking, and end_round does not = 0,
            then Calls deck_deal to deal a hand to the player and a hand to the dealer. It then
            takes the cards from the player's hand and the dealer's hand and creates sprites for them,
            placing them on the visible table. The deal button can only be pushed after the round has ended
            and a winner has been declared. """

            # Get rid of the in between-hands chatter
            textFont = pygame.font.Font(None, 28)

            if end_round == 1: self.image, self.rect = load_image("deal.png", 0)
            else: self.image, self.rect = load_image("deal-grey.png", 0)

            self.position = (735, 450)
            self.rect.center = self.position


            if self.rect.collidepoint(mX, mY) == 1:
                if end_round == 1 and click == 1:
                    display_font = display(textFont, "")

                    cards.empty()
                    playerCards.empty()

                    deck, played_deck, player_hand, dealer_hand = deck_deal(deck, played_deck)

                    dCardPos = (50, 70)
                    pCardPos = (540,370)

                    # Create player's card sprites
                    for x in player_hand:
                        card = CardSprite(x, pCardPos)
                        pCardPos = (pCardPos[0] - 80, pCardPos [1])
                        playerCards.add(card)

                    # Create dealer's card sprites
                    faceDownCard = CardSprite("back", dCardPos)
                    dCardPos = (dCardPos[0] + 80, dCardPos[1])
                    cards.add(faceDownCard)

                    card = CardSprite(dealer_hand [0], dCardPos)
                    cards.add(card)
                    end_round = 0
                    click = 0
                    handsPlayed += 1

            return deck, played_deck, player_hand, dealer_hand, dCardPos, pCardPos, end_round, display_font, click, handsPlayed
