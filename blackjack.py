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

# ==============Koniec logiki gry=================
