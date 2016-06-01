"""
Program do gry w Blackjack (a.k.a. Oczko) w języku Python przy użyciu biblioteki PyGame
Projekt zaliczeniowy - Języki Skryptowe, Informatyka i Ekonometria, rok 1, WZ, AGH
Autorzy: Joanna Jeziorek, Mateusz Koziestański, Katarzyna Maciocha
III 2016
"""
import random as rd
import os
import sys
import pygame
from pygame import *

pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((800, 480))
clock = pygame.time.Clock()
# poniższe zmienne muszę wstępnie zadeklarować tu, bo inaczej wywala błędy niżej w metodach.
display_font = pygame.font.Font(None, 28)
aces = ['ki_a', 'ka_a', 'pi_a', 'tr_a']
player_hand, dealer_hand = [], []


def load_image(imgname, card):
    """
    Metoda do wczytywania plików obrazów.
    :param imgname: nazwa pliku png
    :param card: obiekt karty
    :return: zwraca obraz oraz prostokąt go ograniczający
    """
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
        deck.append(played_deck.pop())
        
    shuffle(deck)
    return deck, played_deck


def deck_deal(deck, played_deck):
    # Jeśli talia nie jest pusta, rozdaje pierwsze cztery obrazy z talii na przemian graczowi i krupierowi.
    # Zwraca kolejno: talię, zagraną talię, rękę gracza i rękę krupiera
    dealer_hand, player_hand = [], []
    shuffle(deck)
    if len(deck) < 5:
        deck, played_deck = return_played(deck, played_deck)

# wymaga dopracowania zwracania kart do talii, jeśli jest już pusta.
    dealer_hand.append(deck.pop(0))
    played_deck.append(dealer_hand[-1])
    player_hand.append(deck.pop(0))
    played_deck.append(player_hand[-1])
    dealer_hand.append(deck.pop(0))
    played_deck.append(dealer_hand[-1])
    player_hand.append(deck.pop(0))
    played_deck.append(player_hand[-1])

    return deck, played_deck, player_hand, dealer_hand


def hit(deck, played_deck, hand):
    # Jeśli talia nie jest pusta, daje graczowi kartę do ręki.
    if len(deck) < 2:
        deck, played_deck = return_played(deck, played_deck)

    hand.append(deck.pop(0))
    played_deck.append(hand[-1])
    return deck, played_deck, hand


def value(hand):
    # Oblicza wartość kart w ręce.
    # Jeśli w ręce znajduje się as, a wartość przekracza 21, zmienia wartość asa z 11 do 1pkt.
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


def round_end(deck, player_hand, dealer_hand, played_deck, funds, money_gain, money_loss, dealer_cards, CardSprite):
    if len(player_hand) == 2 and player_hand[:1] in aces:
        money_gain += (money_gain * 3 / 2)

    dealer_cards.empty()

    dealer_card_position = (50, 70)

    for x in dealer_hand:
        card = CardSprite(x, dealer_card_position)
        dealer_card_position = (dealer_card_position[0] + 80, dealer_card_position[1])
        dealer_cards.add(card)

    if not dealer_hand:
        for card in player_hand:
            played_deck.append(card)
            player_hand.pop()
        for card in dealer_hand:
            played_deck.append(card)
            dealer_hand.pop()
            

    funds += money_gain
    funds -= money_loss

    display_font = pygame.font.Font(None, 28)

    if funds <= 0:
        game_over()

    end_round = 1

    return deck, player_hand, dealer_hand, played_deck, funds, end_round


def bust(deck, player_hand, dealer_hand, played_deck, funds, money_gain, money_loss, dealer_cards, CardSprite):

    font = pygame.font.Font(None, 28)
    display_font = display(font, "Gracz przebił! Przegrana: $%.1f." % money_loss)

    deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                              played_deck, funds,
                                                                              money_gain, money_loss, dealer_cards,
                                                                              CardSprite)

    return deck, player_hand, dealer_hand, played_deck, funds, end_round, display_font


def compare(deck, played_deck, player_hand, dealer_hand, funds, bet, dealer_cards, CardSprite):
    pv, dv = value(player_hand), value(dealer_hand)
    display_font = pygame.font.Font(None, 28)
    while dv < 17:
        deck, played_deck, dealer_hand = hit(deck, played_deck, dealer_hand)
        dv = value(dealer_hand)

    if dv < pv <= 21:
        # Gracz wygrywa
        funds += 2 * bet
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck, funds, bet, 0,
                                                                                  dealer_cards,
                                                                                  CardSprite)
        display_font = display(display_font, "Wygrana: $%.1f." % bet)
    elif pv == dv and pv <= 21:
        # Remis
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck, funds, 0, 0,
                                                                                  dealer_cards,
                                                                                  CardSprite)
        display_font = display(display_font, "Remis!")
    elif dv > 21 >= pv:
        # Krupier przebił, a gracz nie
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck, funds, bet, 0,
                                                                                  dealer_cards,
                                                                                  CardSprite)
        display_font = display(display_font, "Krupier przebił! Wygrana: $%.1f." % bet)
    else:
        # W każdej innej sytuacji krupier wygrywa
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck, funds, 0, bet,
                                                                                  dealer_cards,
                                                                                  CardSprite)
        display_font = display(display_font, "Krupier wygrywa! Przegrana $%.1f." % bet)

    return deck, played_deck, end_round, funds, display_font


def blackJack(deck, played_deck, player_hand, dealer_hand, funds, bet, dealer_cards, CardSprite):
    """ Metoda sprawdzająca, czy któryś z graczy ma blackjack (BJ) """

    textFont = pygame.font.Font(None, 28)

    pv = value(player_hand)
    dv = value(dealer_hand)

    if pv == 21 and dv == 21:
        # Zarówno gracz, jak i krupier mają BJ, jest remis i nikt nie traci pieniędzy.
        display_font = display(textFont, "Blackjack! Krupier także go ma, więc jest remis!")
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck,
                                                                                  funds, 0, bet, dealer_cards,
                                                                                  CardSprite)

    elif pv == 21 and dv != 21:
        # Krupier przegrywa, gracz ma BJ
        display_font = display(textFont, "Blackjack! Wygrana: $%.1f." % (bet * 1.5))
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck,
                                                                                  funds, bet, 0, dealer_cards,
                                                                                  CardSprite)

    elif dv == 21 and pv != 21:
        # Gracz przegrywa, a krupier ma BJ
        deck, player_hand, dealer_hand, played_deck, funds, end_round = round_end(deck, player_hand, dealer_hand,
                                                                                  played_deck,
                                                                                  funds, 0, bet, dealer_cards,
                                                                                  CardSprite)
        display_font = display(textFont, "Krupier ma blackjack! Przegrana: $%.1f." % bet)

    return display_font, player_hand, dealer_hand, played_deck, funds, end_round


# ==============Koniec logiki gry===============
class CardSprite(pygame.sprite.Sprite):
    """ Sprite wyświetlający określoną kartę. """

    def __init__(self, card, position):
        pygame.sprite.Sprite.__init__(self)
        card_image = card + ".png"
        self.image, self.rect = load_image(card_image, 1)
        self.position = position

    def update(self):
        self.rect.center = self.position


# metoda update w każdym guziku to zasadniczo instrukcja wykonywania funkcjonalności każdego guzika po kliknięciu


class BetButtonUp(pygame.sprite.Sprite):
    """ Guzik zwiększający zakład """

    # noinspection PyTypeChecker
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("arrow_up.png", 0)
        self.position = (710, 225)

    def update(self, mX, mY, bet, funds, click, end_round):

        self.image, self.rect = load_image("arrow_up.png", 0)

        self.position = (710, 225)
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
        self.position = (710, 225)

    def update(self, mX, mY, bet, click, end_round):
        self.image, self.rect = load_image("arrow_down.png", 0)

        self.position = (760, 225)
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
        self.position = (735, 390)

    def update(self, mX, mY, deck, played_deck, player_hand, dealer_cards, player_card_position, end_round, CardSprite,
               click):

        self.image, self.rect = load_image("hit.png", 0)

        self.position = (735, 390)
        self.rect.center = self.position

        if self.rect.collidepoint(mX, mY) == 1 and click == 1:
            if end_round == 0:
                deck, played_deck, player_hand = hit(deck, played_deck, player_hand)

                current_card = len(player_hand) - 1
                card = CardSprite(player_hand[current_card], player_card_position)
                dealer_cards.add(card)
                player_card_position = (player_card_position[0] - 80, player_card_position[1])

                click = 0

        return deck, played_deck, player_hand, player_card_position, click


class StandButton(pygame.sprite.Sprite):
    """ Guzik umożliwiający graczowi zostanie przy obecnej liczbie kart. """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("stand.png", 0)
        self.position = (735, 350)

    def update(self, mX, mY, deck, played_deck, player_hand, dealer_hand, dealer_cards, player_card_position, end_round,
               CardSprite, funds,
               bet, display_font):

        self.image, self.rect = load_image("stand.png", 0)

        self.position = (735, 350)
        self.rect.center = self.position

        if self.rect.collidepoint(mX, mY) == 1:
            if end_round == 0:
                deck, played_deck, end_round, funds, display_font = compare(deck, played_deck, player_hand, dealer_hand,
                                                                            funds, bet, dealer_cards, CardSprite)

        return deck, played_deck, end_round, funds, player_hand, played_deck, player_card_position, display_font


class DoubleButton(pygame.sprite.Sprite):
    """ Guzik umożliwiający graczowi podwojenie zakładu i wzięcie jedynej dodatkowej karty."""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("double.png", 0)
        self.position = (735, 305)

    def update(self, mX, mY, deck, played_deck, player_hand, dealer_hand, playerCards, dealer_cards,
               player_card_position,
               end_round,
               CardSprite, funds, bet, display_font):

        self.image, self.rect = load_image("double.png", 0)

        self.position = (735, 305)
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
                                                                            funds, bet, dealer_cards, CardSprite)

                bet /= 2

        return deck, played_deck, end_round, funds, player_hand, played_deck, player_card_position, display_font, bet


class DealButton(pygame.sprite.Sprite):
    """ Guzik umożliwiający rozpoczęcie nowej rundy / rozdania """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("deal.png", 0)
        self.position = (735, 430)

    def update(self, mX, mY, deck, played_deck, end_round, CardSprite, dealer_cards, player_hand, dealer_hand,
               dealer_card_posit,
               player_card_position, display_font, playerCards, click, handsPlayed) -> object:

        textFont = pygame.font.Font(None, 28)

        self.image, self.rect = load_image("deal.png", 0)

        self.position = (735, 430)
        self.rect.center = self.position

        if self.rect.collidepoint(mX, mY) == 1:
            if end_round == 1 and click == 1:
                display_font = display(textFont, "")

                dealer_cards.empty()
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
                dealer_cards.add(faceDownCard)

                card = CardSprite(dealer_hand[0], dealer_card_posit)
                dealer_cards.add(card)
                end_round = 0
                click = 0
                handsPlayed += 1

        return deck, played_deck, player_hand, dealer_hand, dealer_card_posit, player_card_position, end_round, display_font, click, handsPlayed


# czcionka używana po prawej stronie ekranu (fundusze, zakład itd)
textFont = pygame.font.Font(None, 28)

# ustawiam plik tła/ planszy
background, backgroundRect = load_image("plansza.png", 0)

# grupa grafik kart krupiera
dealer_cards = pygame.sprite.Group()
# jak wyżej, tylko dla gracza
player_cards = pygame.sprite.Group()

# Tworzę instancje wszystkich guzików
bet_up = BetButtonUp()
bet_down = BetButtonDown()
stand_button = StandButton()
deal_butt = DealButton()
hit_butt = HitButton()
dbl_butt = DoubleButton()

# Grupa zawierająca wszystkie guziki
buttons = pygame.sprite.Group(bet_up, bet_down, hit_butt, stand_button, deal_butt, dbl_butt)

# Tworzę talię
deck = create_deck()
# Definiuję pusty zbiór zużytych kart
played_deck = []

dealer_card_position, player_card_position = (), ()
mX, mY = 0, 0
click = 0

# Startowe wartości stawki i banku.
funds = 100.0
bet = 10.0

# Ile rund zostało zagrane - inicjalizacja zmiennej
handsPlayed = 0

# Zmienna używana do oznaczenia końca rundy. Równa 0, oprócz pomiędzy rundami, gdzie ma wartość 1.
end_round = 1

firstTime = 1

while 1:
    screen.blit(background, backgroundRect)

    if bet > funds:
       
        bet = funds

    if end_round == 1 and firstTime == 1:
       
        display_font = display(textFont,
                               "Klikaj w strzałki, aby określić stawkę. Potem wciśnij Deal aby rozpocząć grę.")
        firstTime = 0

    screen.blit(display_font, (10, 455))
    fundsFont = pygame.font.Font.render(textFont, "Bank: $%.1f" % funds, 1, (255, 255, 255), (0, 0, 0))
    screen.blit(fundsFont, (658, 175))
    betFont = pygame.font.Font.render(textFont, "Stawka: $%.1f" % bet, 1, (255, 255, 255), (0, 0, 0))
    screen.blit(betFont, (658, 259))
    hpFont = pygame.font.Font.render(textFont, "Runda: %i " % handsPlayed, 1, (255, 255, 255), (0, 0, 0))
    screen.blit(hpFont, (658, 150))

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

    # początkowe sprawdzenie, czy po rozdaniu dwóch pierwszych kart ktoś ma blackjack.
    # Jako że nie umiem zaprogramować "insurance bet" , jeśli krupier ma BJ od razu, to od razu wygrywa.
    if end_round == 0:
        # to co dzieje się w trakcie rundy
        pv = value(player_hand)
        dv = value(dealer_hand)

        if pv == 21 and len(player_hand) == 2:
            # Jeśli gracz ma BJ
            display_font, player_hand, dealer_hand, played_deck, funds, end_round = blackJack(deck, played_deck,
                                                                                              player_hand,
                                                                                              dealer_hand, funds, bet,
                                                                                              dealer_cards,
                                                                                              CardSprite)

        if dv == 21 and len(dealer_hand) == 2:
            # Jeśli krupier ma BJ
            display_font, player_hand, dealer_hand, played_deck, funds, end_round = blackJack(deck, played_deck,
                                                                                              player_hand,
                                                                                              dealer_hand, funds, bet,
                                                                                              dealer_cards,
                                                                                              CardSprite)

        if pv > 21:
            # Jesli gracz przebił
            deck, player_hand, dealer_hand, played_deck, funds, end_round, display_font = bust(deck, player_hand,
                                                                                               dealer_hand,
                                                                                               played_deck, funds, 0,
                                                                                               bet, dealer_cards,
                                                                                               CardSprite)

    # Update guzików
    # deal
    deck, played_deck, player_hand, dealer_hand, dealer_card_position, player_card_position, end_round, display_font, click, handsPlayed = deal_butt.update(
        mX, mY, deck, played_deck, end_round, CardSprite, dealer_cards, player_hand, dealer_hand, dealer_card_position,
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
        dealer_cards,
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
        dealer_cards,
        player_card_position,
        end_round,
        CardSprite,
        funds,
        bet,
        display_font)
    # Stawka - guziki
    bet, click = bet_up.update(mX, mY, bet, funds, click, end_round)
    bet, click = bet_down.update(mX, mY, bet, click, end_round)
    # wrzucam je na ekran.
    buttons.draw(screen)

    # jeśli są karty na ekranie, wrzuć je tam
    if dealer_cards:
        player_cards.update()
        player_cards.draw(screen)
        dealer_cards.update()
        dealer_cards.draw(screen)

    # update okna gry
    pygame.display.flip()
