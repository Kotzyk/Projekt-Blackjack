"""
Program do gry w Blackjack (a.k.a. Oczko) w języku Python przy użyciu biblioteki PyGame
Projekt zaliczeniowy - Języki Skryptowe, Informatyka i Ekonometria, rok 1, WZ, AGH
Autorzy: Joanna Jeziorek, Mateusz Koziestański, Katarzyna Maciocha
III 2016
"""
import random as rd
import pygame
import sys, os
from pygame.locals import *

pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((800, 480))
clock = pygame.time.Clock()


def load_image(img, card):
    if card == 1:
        fullname = os.path.join("karty/", name)
    else: fullname = os.path.join('karty', name)
    
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Nie można zaladować obrazu:', name
        raise SystemExit, message
    image = image.convert()
    
    return image, image.get_rect()
    
    
def display(font, sentence):
    """ Wyswietlacz tekstu na dole ekranu. Tekst sluży do informowania gracza o tym co sie dzieje."""
    
    displayFont = pygame.font.Font.render(font, sentence, 1, (255,255,255), (0,0,0)) 
    return displayFont

def gameOver():
        """ 
        Jesli graczowi skoncza sie pieniadze, wyswietla ekran koncowy. Gracz moze tylko zamknac gre.
        """
        
        while 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    sys.exit()

            # Fill the screen with black
            screen.fill((0,0,0))
            
            # Render "Game Over" sentence on the screen
            oFont = pygame.font.Font(None, 50)
            displayFont = pygame.font.Font.render(oFont, "Koniec gry! Skonczyly ci sie pieniadze!", 1, (255,255,255), (0,0,0)) 
            screen.blit(displayFont, (125, 220))
            
            # Update the display
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
    # Przekazuje zagrane karty do głównej talii.
    # Zwraca potasowaną talię i pustą talię zagranych kart.


    for card in played_deck:
        deck.append(card)
        del card
    shuffle(deck)
    return deck, played_deck


def deck_deal(deck, played_deck):
    # Jeśli talia nie jest pusta, rozdaje pierwsze cztery karty z talii na przemian graczowi i krupierowi.
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
    aces = ['ki_a', 'ka_a', 'pi_a', 'tr_a']
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


def compare(deck, played_deck, player_hand, dealer_hand, funds, bet):
    pv, dv = value(player_hand), value(dealer_hand)
    while dv < 17:
        deck, played_deck, dealer_hand = hit(deck, played_deck, dealer_hand)
        dv = value(dealer_hand)
        #do dokończenia
