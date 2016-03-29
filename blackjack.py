"""
Program do gry w Blackjack (a.k.a. Oczko) w języku Python przy użyciu biblioteki PyGame
Projekt zaliczeniowy - Języki Skryptowe, Informatyka i Ekonometria, rok 1, WZ, AGH
Autorzy: Joanna Jeziorek, Mateusz Koziestański, Katarzyna Maciocha
III 2016
"""

import os
import random as rd
import sys

import pygame

pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((800, 480))
clock = pygame.time.Clock()

aces = ['ki_a', 'ka_a', 'pi_a', 'tr_a']


def load_image(imgname, card):
    if card == 1:
        fullname = os.path.join("obrazy/karty", imgname)
    else:
        fullname = os.path.join('obrazy', imgname)

    try:
        imgname = pygame.image.load(fullname)
    except pygame.error as message:
        print('Nie można zaladować obrazu:', imgname)

    imgname = imgname.convert()

    return imgname, imgname.get_rect()


def display(font, sentence):
    """ Wyswietlacz tekstu na dole ekranu. Tekst sluży do informowania gracza o tym co sie dzieje."""

    display_font = pygame.font.Font.render(font, sentence, 1, (255, 255, 255), (0, 0, 0))
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
        screen.fill((0, 0, 0))

        # Napis Koniec Gry
        oFont = pygame.font.Font(None, 50)
        display_font = pygame.font.Font.render(oFont, "Koniec gry! Skonczyly ci sie pieniadze!", 1, (255, 255, 255),
                                               (0, 0, 0))
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
        return_played(deck, played_deck)

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
        money_gain += (money_gain * 3 / 2.0)

    cards.empty()

    dealer_card_position = (50, 70)

    for x in dealer_hand:
        card = CardSprite(x, dealer_card_position)
        dealer_card_position = (dealer_card_position[0] + 80, dealer_card_position[1])
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
        funds += 2 * bet
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck, funds, bet, 0, cards,
                                                                                  CardSprite)
        display_font = display(display_font, "Wygrana: $%.2f." % bet)
    elif pv == dv and pv <= 21:
        # Remis
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck, funds, 0, 0, cards,
                                                                                  CardSprite)
        display_font = display(display_font, "Remis!")
    elif dv > 21 >= pv:
        # Krupier przebił, a gracz nie
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck, funds, bet, 0, cards,
                                                                                  CardSprite)
        display_font = display(display_font, "Krupier przebił! Wygrana: $%.2f." % bet)
    else:
        # W każdej innej sytuacji krupier wygrywa
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck, funds, 0, bet, cards,
                                                                                  CardSprite)
        display_font = display(display_font, "Krzupier wygrywa! Przegrana $%.2f." % bet)

    return deck, played_deck, end_round, funds, display_font


def blackJack(deck, played_deck, player_hand, dealer_hand, funds, bet, cards, CardSprite):
    """ Called when the player or the dealer is determined to have blackjack. Hands are compared to determine the outcome. """

    textFont = pygame.font.Font(None, 28)

    pv = value(player_hand)
    dv = value(dealer_hand)

    if pv == 21 and dv == 21:
        # The opposing player ties the original blackjack getter because he also has blackjack
        # No money will be lost, and a new hand will be dealt
        display_font = display(textFont, "Blackjack! The dealer also has blackjack, so it's a push!")
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck,
                                                                                  funds, 0, bet, cards, CardSprite)

    elif pv == 21 and dv != 21:
        # Dealer loses
        display_font = display(textFont, "Blackjack! You won $%.2f." % (bet * 1.5))
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck,
                                                                                  funds, bet, 0, cards, CardSprite)

    elif dv == 21 and pv != 21:
        # Player loses, money is lost, and new hand will be dealt
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck,
                                                                                  funds, 0, bet, cards, CardSprite)
        display_font = display(textFont, "Dealer has blackjack! You lose $%.2f." % (bet))

    return display_font, player_hand, dealer_hand, played_deck, funds, end_round


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
        self.image, self.rect = load_image("arrow_up.png", 0)
        self.position = (710, 255)

    def update(self, mX, mY, bet, funds, click, end_round):

        self.image, self.rect = load_image("arrow_up.png", 0)

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
        self.image, self.rect = load_image("arrow_down.png", 0)
        self.position = (710, 255)

    def update(self, mX, mY, bet, click, end_round):
        self.image, self.rect = load_image("arrow_down.png", 0)

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
        self.image, self.rect = load_image("hit.png", 0)
        self.position = (735, 400)

    def update(self, mX, mY, deck, played_deck, player_hand, cards, player_card_position, end_round, CardSprite, click):

        self.image, self.rect = load_image("hit.png", 0)

        self.position = (735, 400)
        self.rect.center = self.position

        if self.rect.collidepoint(mX, mY) == 1 and click == 1:
            if end_round == 0:
                deck, played_deck, player_hand = hit(deck, played_deck, player_hand)

                current_card = len(player_hand) - 1
                card = CardSprite(player_hand[current_card], player_card_position)
                cards.add(card)
                player_card_position = (player_card_position[0] - 80, player_card_position[1])

                click = 0

        return deck, played_deck, player_hand, player_card_position, click


class StandButton(pygame.sprite.Sprite):
    """ Guzik umożliwiający graczowi zostanie przy obecnej liczbie kart. """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("stand.png", 0)
        self.position = (735, 365)

    def update(self, mX, mY, deck, played_deck, player_hand, dealer_hand, cards, player_card_position, end_round,
               CardSprite, funds,
               bet, display_font):

        self.image, self.rect = load_image("stand.png", 0)

        self.position = (735, 365)
        self.rect.center = self.position

        if self.rect.collidepoint(mX, mY) == 1:
            if end_round == 0:
                deck, played_deck, end_round, funds, display_font = compare(deck, played_deck, player_hand, dealer_hand,
                                                                            funds, bet, cards, CardSprite)

        return deck, played_deck, end_round, funds, player_hand, played_deck, player_card_position, display_font


class DoubleButton(pygame.sprite.Sprite):
    """ Guzik umożliwiający graczowi podwojenie zakładu i wzięcie jedynej dodatkowej karty."""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("double.png", 0)
        self.position = (735, 330)

    def update(self, mX, mY, deck, played_deck, player_hand, dealer_hand, playerCards, cards, player_card_position,
               end_round,
               CardSprite, funds, bet, display_font):

        self.image, self.rect = load_image("double.png", 0)

        self.position = (735, 330)
        self.rect.center = self.position

        if self.rect.collidepoint(mX, mY) == 1:
            if end_round == 0 and funds >= bet * 2 and len(player_hand) == 2:
                bet *= 2

                deck, played_deck, player_hand = hit(deck, played_deck, player_hand)

                current_card = len(player_hand) - 1
                card = CardSprite(player_hand[current_card], player_card_position)
                playerCards.add(card)
                player_card_position = (player_card_position[0] - 80, player_card_position[1])

                deck, played_deck, end_round, funds, display_font = compare(deck, played_deck, player_hand, dealer_hand,
                                                                            funds, bet, cards, CardSprite)

                bet /= 2

        return deck, played_deck, end_round, funds, player_hand, played_deck, player_card_position, display_font, bet


class DealButton(pygame.sprite.Sprite):
    """ Guzik umożliwiający rozpoczęcie nowej rundy / rozdania """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("deal.png", 0)
        self.position = (735, 450)

    def update(self, mX, mY, deck, played_deck, end_round, CardSprite, cards, player_hand, dealer_hand,
               dealer_card_posit,
               player_card_position, display_font, playerCards, click, handsPlayed) -> object:

        textFont = pygame.font.Font(None, 28)

        self.image, self.rect = load_image("deal.png", 0)

        self.position = (735, 450)
        self.rect.center = self.position

        if self.rect.collidepoint(mX, mY) == 1:
            if end_round == 1 and click == 1:
                display_font = display(textFont, "")

                cards.empty()
                playerCards.empty()

                deck, played_deck, player_hand, dealer_hand = deck_deal(deck, played_deck)

                dealer_card_posit = (50, 70)
                player_card_position = (540, 370)

                for x in player_hand:
                    card = CardSprite(x, player_card_position)
                    player_card_position = (player_card_position[0] - 80, player_card_position[1])
                    playerCards.add(card)

                faceDownCard = CardSprite("back", dealer_card_posit)
                dealer_card_posit = (dealer_card_posit[0] + 80, dealer_card_posit[1])
                cards.add(faceDownCard)

                card = CardSprite(dealer_hand[0], dealer_card_posit)
                cards.add(card)
                end_round = 0
                click = 0
                handsPlayed += 1

        return deck, played_deck, player_hand, dealer_hand, dealer_card_posit, player_card_position, end_round, display_font, click, handsPlayed


# This font is used to display text on the right-hand side of the screen
textFont = pygame.font.Font(None, 28)

# This sets up the background image, and its container rect
background, backgroundRect = load_image("back.png", 0)

# cards is the sprite group that will contain sprites for the dealer's cards
cards = pygame.sprite.Group()
# playerCards will serve the same purpose, but for the player
player_cards = pygame.sprite.Group()

# This creates instances of all the button sprites
bet_up = BetButtonUp()
bet_down = BetButtonDown()
stand_button = StandButton()
deal_butt = DealButton()
hit_butt = HitButton()
dbl_butt = DoubleButton()

# This group containts the button sprites
buttons = pygame.sprite.Group(bet_up, bet_down, hit_butt, stand_button, deal_butt, dbl_butt)

# The 52 card deck is created
deck = create_deck()
# The dead deck will contain cards that have been discarded
played_deck = []

# These are default values that will be changed later, but are required to be declared now
# so that Python doesn't get confused
player_hand, dealer_hand, dealer_card_position, player_card_position = [], [], (), ()
mX, mY = 0, 0
click = 0

# The default funds start at $100.00, and the initial bet defaults to $10.00
funds = 100.00
bet = 10.00

# This is a counter that counts the number of rounds played in a given session
handsPlayed = 0

# When the cards have been dealt, end_round is zero.
# In between rounds, it is equal to one
end_round = 1

# firstTime is a variable that is only used once, to display the initial
# message at the bottom, then it is set to zero for the duration of the program.
firstTime = 1

while 1:
    screen.blit(background, backgroundRect)

    if bet > funds:
        # If you lost money, and your bet is greater than your funds, make the bet equal to the funds
        bet = funds

    if end_round == 1 and firstTime == 1:
        # When the player hasn't started. Will only be displayed the first time.
        display_font = display(textFont, "Click on the arrows to declare your bet, then deal to start the game.")
        firstTime = 0

    # Show the blurb at the bottom of the screen, how much money left, and current bet
    screen.blit(display_font, (10, 444))
    fundsFont = pygame.font.Font.render(textFont, "Funds: $%.2f" % (funds), 1, (255, 255, 255), (0, 0, 0))
    screen.blit(fundsFont, (663, 205))
    betFont = pygame.font.Font.render(textFont, "Bet: $%.2f" % (bet), 1, (255, 255, 255), (0, 0, 0))
    screen.blit(betFont, (680, 285))
    hpFont = pygame.font.Font.render(textFont, "Round: %i " % (handsPlayed), 1, (255, 255, 255), (0, 0, 0))
    screen.blit(hpFont, (663, 180))

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                mX, mY = pygame.mouse.get_pos()
                click = 1
        elif event.type == MOUSEBUTTONUP:
            mX, mY = 0, 0
            click = 0

    # Initial check for the value of the player's hand, so that his hand can be displayed and it can be determined
    # if the player busts or has blackjack or not
    if end_round == 0:
        # Stuff to do when the game is happening
        pv = value(player_hand)
        dv = value(dealer_hand)

        if pv == 21 and len(player_hand) == 2:
            # If the player gets blackjack
            display_font, player_hand, dealer_hand, played_deck, funds, end_round = blackJack(deck, played_deck,
                                                                                              player_hand,
                                                                                              dealer_hand, funds, bet,
                                                                                              cards,
                                                                                              CardSprite)

        if dv == 21 and len(dealer_hand) == 2:
            # If the dealer has blackjack
            display_font, player_hand, dealer_hand, played_deck, funds, end_round = blackJack(deck, played_deck,
                                                                                              player_hand,
                                                                                              dealer_hand, funds, bet,
                                                                                              cards,
                                                                                              CardSprite)

        if pv > 21:
            # If player busts
            deck, player_hand, dealer_hand, played_deck, funds, end_round, display_font = bust(deck, player_hand,
                                                                                               dealer_hand,
                                                                                               played_deck, funds, 0,
                                                                                               bet, cards,
                                                                                               CardSprite)

    # Update the buttons
    # deal
    deck, played_deck, player_hand, dealer_hand, dealer_card_position, player_card_position, end_round, display_font, click, handsPlayed = deal_butt.update(
        mX, mY, deck, played_deck, end_round, CardSprite, cards, player_hand, dealer_hand, dealer_card_position,
        player_card_position, display_font,
        player_cards, click, handsPlayed)
    # hit
    deck, played_deck, player_hand, player_card_position, click = hit_butt.update(mX, mY, deck, played_deck,
                                                                                  player_hand,
                                                                                  player_cards,
                                                                                  player_card_position, end_round,
                                                                                  CardSprite, click)
    # stand
    deck, played_deck, end_round, funds, player_hand, played_deck, player_card_position, display_font = stand_button.update(
        mX,
        mY,
        deck,
        played_deck,
        player_hand,
        dealer_hand,
        cards,
        player_card_position,
        end_round,
        CardSprite,
        funds,
        bet,
        display_font)
    # double
    deck, played_deck, end_round, funds, player_hand, played_deck, player_card_position, display_font, bet = dbl_butt.update(
        mX,
        mY,
        deck,
        played_deck,
        player_hand,
        dealer_hand,
        player_cards,
        cards,
        player_card_position,
        end_round,
        CardSprite,
        funds,
        bet,
        display_font)
    # Bet buttons
    bet, click = bet_up.update(mX, mY, bet, funds, click, end_round)
    bet, click = bet_down.update(mX, mY, bet, click, end_round)
    # draw them to the screen
    buttons.draw(screen)

    # If there are cards on the screen, draw them
    if len(cards) is not 0:
        player_cards.update()
        player_cards.draw(screen)
        cards.update()
        cards.draw(screen)

    # Updates the contents of the display
    pygame.display.flip()
