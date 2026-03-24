import pygame
import random
import sys

pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 750
FPS = 60

CLR_FELT        = (7,  99,  36)
CLR_FELT_DARK   = (5,  75,  27)
CLR_FELT_LIGHT  = (10, 120, 45)
CLR_WHITE       = (255, 255, 255)
CLR_BLACK       = (0,   0,   0)
CLR_GOLD        = (212, 175, 55)
CLR_GOLD_DARK   = (160, 130, 30)
CLR_RED         = (200,  30,  30)
CLR_RED_LIGHT   = (230,  60,  60)
CLR_GRAY        = (160, 160, 160)
CLR_GRAY_DARK   = (100, 100, 100)
CLR_CHIP_BLUE   = (30,  80, 180)
CLR_CHIP_GREEN  = (20, 140,  60)
CLR_CHIP_RED    = (190,  30,  30)
CLR_CHIP_BLACK  = (30,  30,  30)
CLR_CYAN        = (0,  200, 220)

CARD_W, CARD_H  = 80, 115
CARD_RADIUS     = 8

fnt_huge   = pygame.font.SysFont("Georgia",           64, bold=True)
fnt_large  = pygame.font.SysFont("Georgia",           36, bold=True)
fnt_med    = pygame.font.SysFont("Georgia",           26, bold=True)
fnt_small  = pygame.font.SysFont("Arial",             20)
fnt_tiny   = pygame.font.SysFont("Arial",             16)
fnt_card_s = pygame.font.SysFont("Georgia",           13, bold=True)

SUITS     = ["\u2660", "\u2665", "\u2666", "\u2663"]
RANKS     = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
RED_SUITS = {"\u2665", "\u2666"}

# ── Deck ───────────────────────────────────────────────────────────────────────
def build_deck(num_decks=6):
    deck = [(r, s) for r in RANKS for s in SUITS] * num_decks
    random.shuffle(deck)
    return deck

# ── Hand value ─────────────────────────────────────────────────────────────────
def hand_value(hand):
    total, aces = 0, 0
    for rank, _ in hand:
        if rank in ("J","Q","K"):
            total += 10
        elif rank == "A":
            total += 11
            aces += 1
        else:
            total += int(rank)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21

def bust(hand):
    return hand_value(hand) > 21

# ── Card surface ───────────────────────────────────────────────────────────────
def draw_card_surface(rank, suit, face_up=True):
    surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)

    if not face_up:
        pygame.draw.rect(surf, (30, 30, 120), (0, 0, CARD_W, CARD_H), border_radius=CARD_RADIUS)
        pygame.draw.rect(surf, (50, 50, 160), (5, 5, CARD_W-10, CARD_H-10), border_radius=6)
        for i in range(-CARD_H, CARD_W, 12):
            pygame.draw.line(surf, (40, 40, 140), (i, 0), (i+CARD_H, CARD_H), 1)
        pygame.draw.rect(surf, CLR_GOLD, (0, 0, CARD_W, CARD_H), 2, border_radius=CARD_RADIUS)
        return surf

    is_red   = suit in RED_SUITS
    txt_col  = CLR_RED if is_red else (20, 20, 20)

    pygame.draw.rect(surf, CLR_WHITE, (0, 0, CARD_W, CARD_H), border_radius=CARD_RADIUS)
    pygame.draw.rect(surf, CLR_GRAY,  (0, 0, CARD_W, CARD_H), 1, border_radius=CARD_RADIUS)

    r_surf = fnt_card_s.render(rank, True, txt_col)
    s_surf = fnt_card_s.render(suit, True, txt_col)
    surf.blit(r_surf, (5, 3))
    surf.blit(s_surf, (5, 3 + r_surf.get_height()))

    r_surf2 = pygame.transform.rotate(r_surf, 180)
    s_surf2 = pygame.transform.rotate(s_surf, 180)
    surf.blit(r_surf2, (CARD_W - r_surf2.get_width() - 5,
                        CARD_H - r_surf2.get_height() - 3))
    surf.blit(s_surf2, (CARD_W - s_surf2.get_width() - 5,
                        CARD_H - r_surf2.get_height() - s_surf2.get_height() - 3))

    centre_fnt = pygame.font.SysFont("Arial", 36, bold=True)
    cs = centre_fnt.render(suit, True, txt_col)
    surf.blit(cs, (CARD_W//2 - cs.get_width()//2, CARD_H//2 - cs.get_height()//2))

    return surf

# ── Chips ──────────────────────────────────────────────────────────────────────
CHIP_DENOMINATIONS = [5, 25, 100, 500]
CHIP_COLOURS = {5: CLR_CHIP_RED, 25: CLR_CHIP_GREEN,
                100: CLR_CHIP_BLUE, 500: CLR_CHIP_BLACK}

def draw_chip(surface, x, y, denom, radius=22):
    col = CHIP_COLOURS[denom]
    pygame.draw.circle(surface, col,      (x, y), radius)
    pygame.draw.circle(surface, CLR_WHITE,(x, y), radius,     2)
    pygame.draw.circle(surface, col,      (x, y), radius - 6)
    pygame.draw.circle(surface, CLR_WHITE,(x, y), radius - 6, 1)
    lbl = fnt_tiny.render(f"${denom}", True, CLR_WHITE)
    surface.blit(lbl, (x - lbl.get_width()//2, y - lbl.get_height()//2))

# ── Button ─────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, text, colour, hover_colour,
                 text_colour=None, font=None):
        self.rect         = pygame.Rect(rect)
        self.text         = text
        self.colour       = colour
        self.hover_colour = hover_colour
        self.text_colour  = text_colour or CLR_WHITE
        self.font         = font or fnt_med
        self.hovered      = False
        self.enabled      = True

    def draw(self, surface):
        if not self.enabled:
            col = CLR_GRAY_DARK
            tcol = CLR_GRAY
        else:
            col  = self.hover_colour if self.hovered else self.colour
            tcol = self.text_colour
        pygame.draw.rect(surface, col,      self.rect, border_radius=10)
        pygame.draw.rect(surface, CLR_WHITE if self.enabled else CLR_GRAY,
                         self.rect, 2, border_radius=10)
        lbl = self.font.render(self.text, True, tcol)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()//2,
                            self.rect.centery - lbl.get_height()//2))

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, event):
        return (self.enabled
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))

# ── Animated card ──────────────────────────────────────────────────────────────
class AnimCard:
    def __init__(self, rank, suit, start, end, face_up=True, delay=0):
        self.rank    = rank
        self.suit    = suit
        self.start   = list(start)
        self.end     = list(end)
        self.pos     = list(start)
        self.face_up = face_up
        self.delay   = delay
        self.t       = 0.0
        self.speed   = 0.07
        self.done    = False

    def update(self):
        if self.delay > 0:
            self.delay -= 1
            return
        if self.done:
            return
        self.t = min(1.0, self.t + self.speed)
        ease = 1 - (1 - self.t) ** 3
        self.pos[0] = self.start[0] + (self.end[0] - self.start[0]) * ease
        self.pos[1] = self.start[1] + (self.end[1] - self.start[1]) * ease
        if self.t >= 1.0:
            self.done = True

    def draw(self, surface):
        s = draw_card_surface(self.rank, self.suit, self.face_up)
        surface.blit(s, (int(self.pos[0]), int(self.pos[1])))

# ── Particle ───────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, colour):
        self.x    = float(x)
        self.y    = float(y)
        self.vx   = random.uniform(-4, 4)
        self.vy   = random.uniform(-7, -1)
        self.col  = colour
        self.life = random.randint(40, 80)
        self.r    = random.randint(4, 9)

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.18
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, int(255 * self.life / 80))
        s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, alpha), (self.r, self.r), self.r)
        surface.blit(s, (int(self.x) - self.r, int(self.y) - self.r))

# ── Main game ──────────────────────────────────────────────────────────────────
class BlackjackGame:
    STATE_BETTING  = "BETTING"
    STATE_DEALING  = "DEALING"
    STATE_PLAYER   = "PLAYER"
    STATE_DEALER   = "DEALER"
    STATE_RESULT   = "RESULT"
    STATE_GAMEOVER = "GAMEOVER"

    DECK_POS = (SCREEN_W//2 - CARD_W//2, 10)

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("\u2660 Blackjack \u2665")
        self.clock  = pygame.time.Clock()
        self.reset_game()

    # ── Full reset ─────────────────────────────────────────────────────────────
    def reset_game(self):
        self.balance       = 1000
        self.bet           = 0
        self.deck          = build_deck()
        self.state         = self.STATE_BETTING
        self.player_hand   = []
        self.dealer_hand   = []
        self.anim_cards    = []
        self.particles     = []
        self.result_text   = ""
        self.result_sub    = ""
        self.dealer_reveal = False
        self.dealer_timer  = 0
        self.bet_input     = ""
        self.input_error   = ""
        self._build_buttons()

    # ── Round reset ────────────────────────────────────────────────────────────
    def new_round(self):
        self.bet           = 0
        self.player_hand   = []
        self.dealer_hand   = []
        self.anim_cards    = []
        self.particles     = []
        self.result_text   = ""
        self.result_sub    = ""
        self.dealer_reveal = False
        self.dealer_timer  = 0
        self.bet_input     = ""
        self.input_error   = ""
        if len(self.deck) < 52:
            self.deck = build_deck()
        self.state = self.STATE_BETTING

    def _build_buttons(self):
        self.btn_deal  = Button((460, 630, 180, 52), "DEAL",
                                (20,120,50), (30,160,70))
        self.btn_hit   = Button((310, 630, 150, 52), "HIT",
                                (20,120,50), (30,160,70))
        self.btn_stand = Button((490, 630, 150, 52), "STAND",
                                (160,30,30), (200,50,50))
        self.btn_double= Button((670, 630, 150, 52), "DOUBLE",
                                (120,80,10), (170,120,20))
        self.btn_again = Button((420, 630, 260, 52), "NEW ROUND",
                                (20,80,160), (30,110,200))
        self.btn_restart=Button((420, 530, 260, 52), "PLAY AGAIN",
                                (20,80,160), (30,110,200))

        cx_start = SCREEN_W//2 - (len(CHIP_DENOMINATIONS)*80)//2 + 20
        self.chip_btns = []
        for i, d in enumerate(CHIP_DENOMINATIONS):
            rect = pygame.Rect(cx_start + i*80 - 28, 565, 56, 56)
            self.chip_btns.append((d, rect))

    # ── Card position helpers ──────────────────────────────────────────────────
    def _player_card_pos(self, idx):
        n = max(len(self.player_hand), idx+1)
        spread = min(n, 8)
        sx = SCREEN_W//2 - (spread*(CARD_W-20))//2
        return (sx + idx*(CARD_W-20), 430)

    def _dealer_card_pos(self, idx):
        n = max(len(self.dealer_hand), idx+1)
        spread = min(n, 8)
        sx = SCREEN_W//2 - (spread*(CARD_W-20))//2
        return (sx + idx*(CARD_W-20), 130)

    # ── Deal initial 4 cards ───────────────────────────────────────────────────
    def deal_initial(self):
        self.state       = self.STATE_DEALING
        self.player_hand = []
        self.dealer_hand = []
        self.anim_cards  = []

        # order: player1, dealer1(hidden), player2, dealer2(visible)
        sequence = [(True, True), (False, False), (True, True), (False, True)]
        delay = 0
        for is_player, face_up in sequence:
            card = self.deck.pop()
            if is_player:
                idx = len(self.player_hand)
                self.player_hand.append(card)
                dest = self._player_card_pos(idx)
            else:
                idx = len(self.dealer_hand)
                self.dealer_hand.append(card)
                dest = self._dealer_card_pos(idx)
            ac = AnimCard(card[0], card[1], self.DECK_POS, dest,
                          face_up=face_up, delay=delay)
            self.anim_cards.append(ac)
            delay += 12

    def _all_anim_done(self):
        return all(ac.done for ac in self.anim_cards)

    # ── Player draws ──────────────────────────────────────────────────────────
    def player_draw(self):
        card = self.deck.pop()
        idx  = len(self.player_hand)
        self.player_hand.append(card)
        dest = self._player_card_pos(idx)
        self.anim_cards.append(
            AnimCard(card[0], card[1], self.DECK_POS, dest, face_up=True))

    # ── Dealer draws ──────────────────────────────────────────────────────────
    def dealer_draw(self):
        card = self.deck.pop()
        idx  = len(self.dealer_hand)
        self.dealer_hand.append(card)
        dest = self._dealer_card_pos(idx)
        self.anim_cards.append(
            AnimCard(card[0], card[1], self.DECK_POS, dest, face_up=True))

    # ── Reveal hole card ───────────────────────────────────────────────────────
    def reveal_hole_card(self):
        hole = self.dealer_hand[0]
        for ac in self.anim_cards:
            if (not ac.face_up
                    and ac.rank == hole[0] and ac.suit == hole[1]):
                ac.face_up = True
                break
        self.dealer_reveal = True

    # ── Resolve outcome ────────────────────────────────────────────────────────
    def resolve(self):
        pv  = hand_value(self.player_hand)
        dv  = hand_value(self.dealer_hand)
        pBJ = is_blackjack(self.player_hand)
        dBJ = is_blackjack(self.dealer_hand)

        if bust(self.player_hand):
            result, sub, gain = "BUST", f"Dealer wins  \u2013  you lose ${self.bet}", 0
        elif pBJ and dBJ:
            result, sub, gain = "PUSH", "Both Blackjack  \u2013  bet returned", self.bet
        elif pBJ:
            win = int(self.bet * 2.5)
            result, sub, gain = "BLACKJACK!", f"\u2660 Blackjack pays 2.5\u00d7  +${win}", win
        elif dBJ:
            result, sub, gain = "DEALER BLACKJACK", f"Dealer wins  \u2013  you lose ${self.bet}", 0
        elif bust(self.dealer_hand):
            win = self.bet * 2
            result, sub, gain = "DEALER BUSTS", f"You win  +${win}", win
        elif pv > dv:
            win = self.bet * 2
            result, sub, gain = "YOU WIN!", f"{pv} beats {dv}  \u2013  +${win}", win
        elif dv > pv:
            result, sub, gain = "DEALER WINS", f"{dv} beats {pv}  \u2013  you lose ${self.bet}", 0
        else:
            result, sub, gain = "PUSH", f"Tie at {pv}  \u2013  bet returned", self.bet

        self.balance    += gain
        self.result_text = result
        self.result_sub  = sub
        self.state       = self.STATE_RESULT

        win_result = gain > self.bet or "BLACKJACK" in result
        if win_result:
            for _ in range(90):
                col = random.choice([(212,175,55),(255,215,0),(255,255,100),(200,150,0)])
                self.particles.append(Particle(SCREEN_W//2,
                                               SCREEN_H//2, col))

    # ── Place bet helpers ──────────────────────────────────────────────────────
    def place_bet(self, amount):
        total = self.bet + amount
        if total > self.balance:
            self.input_error = "Not enough balance!"
            return False
        if total > 500:
            self.input_error = "Maximum bet is $500"
            return False
        self.bet         = total
        self.input_error = ""
        return True

    def set_bet_from_input(self):
        try:
            val = int(self.bet_input)
        except ValueError:
            self.input_error = "Enter a valid number"
            return False
        if val < 1:
            self.input_error = "Minimum bet is $1"
            return False
        if val > 500:
            self.input_error = "Maximum bet is $500"
            return False
        if val > self.balance:
            self.input_error = "Not enough balance!"
            return False
        self.bet         = val
        self.input_error = ""
        return True

    # ── Draw helpers ──────────────────────────────────────────────────────────
    def draw_table(self):
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            r = int(CLR_FELT_DARK[0]+(CLR_FELT_LIGHT[0]-CLR_FELT_DARK[0])*t)
            g = int(CLR_FELT_DARK[1]+(CLR_FELT_LIGHT[1]-CLR_FELT_DARK[1])*t)
            b = int(CLR_FELT_DARK[2]+(CLR_FELT_LIGHT[2]-CLR_FELT_DARK[2])*t)
            pygame.draw.line(self.screen, (r,g,b), (0,y),(SCREEN_W,y))

        pygame.draw.ellipse(self.screen, (4,85,28),
                            (50,40,SCREEN_W-100,SCREEN_H-100))
        pygame.draw.ellipse(self.screen, CLR_GOLD,
                            (50,40,SCREEN_W-100,SCREEN_H-100), 3)

        lbl = fnt_tiny.render(
            "\u2660  BLACKJACK PAYS 2.5\u00d7  \u2660  DEALER MUST HIT SOFT 17  \u2660",
            True, CLR_GOLD)
        self.screen.blit(lbl, (SCREEN_W//2-lbl.get_width()//2, SCREEN_H//2-12))

        # Deck shoe
        for i in range(5, 0, -1):
            pygame.draw.rect(self.screen, (25,25,105),
                             (self.DECK_POS[0]+i, self.DECK_POS[1]+i,
                              CARD_W, CARD_H),
                             border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, (30,30,130),
                         (*self.DECK_POS, CARD_W, CARD_H),
                         border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, CLR_GOLD,
                         (*self.DECK_POS, CARD_W, CARD_H),
                         2, border_radius=CARD_RADIUS)
        shoe = fnt_tiny.render("SHOE", True, CLR_GOLD)
        self.screen.blit(shoe,
                         (self.DECK_POS[0]+CARD_W//2-shoe.get_width()//2,
                          self.DECK_POS[1]+CARD_H//2-shoe.get_height()//2))

    def draw_balance_bet(self):
        bal_bg = pygame.Surface((240, 50), pygame.SRCALPHA)
        pygame.draw.rect(bal_bg, (0,0,0,140), (0,0,240,50), border_radius=8)
        self.screen.blit(bal_bg, (18,18))
        lbl = fnt_med.render(f"Balance: ${self.balance}", True, CLR_GOLD)
        self.screen.blit(lbl, (28, 28))

        if self.bet > 0:
            bet_bg = pygame.Surface((190, 50), pygame.SRCALPHA)
            pygame.draw.rect(bet_bg,(0,0,0,140),(0,0,190,50),border_radius=8)
            self.screen.blit(bet_bg,(SCREEN_W-210,18))
            bl = fnt_med.render(f"Bet: ${self.bet}", True, CLR_GOLD)
            self.screen.blit(bl,(SCREEN_W-205, 28))

    def draw_hand_cards(self):
        for ac in self.anim_cards:
            ac.draw(self.screen)

    def draw_hand_value(self, hand, x, y, hide_one=False):
        if not hand:
            return
        if hide_one and not self.dealer_reveal:
            if len(hand) > 1:
                val  = hand_value([hand[1]])
                col  = CLR_WHITE
                text = f"Score: {val}"
            else:
                return
        else:
            val  = hand_value(hand)
            col  = CLR_RED_LIGHT if val > 21 else CLR_WHITE
            text = f"Score: {val}"
        lbl = fnt_small.render(text, True, col)
        bg  = pygame.Surface((lbl.get_width()+16, lbl.get_height()+8),
                              pygame.SRCALPHA)
        pygame.draw.rect(bg,(0,0,0,150),(0,0,bg.get_width(),bg.get_height()),
                         border_radius=6)
        self.screen.blit(bg, (x-8, y-4))
        self.screen.blit(lbl,(x, y))

    def draw_chips_in_bet_area(self):
        if self.bet <= 0:
            return
        remaining  = self.bet
        chip_stack = []
        for d in sorted(CHIP_DENOMINATIONS, reverse=True):
            while remaining >= d:
                chip_stack.append(d)
                remaining -= d

        cx, cy = SCREEN_W//2, 355
        for i, d in enumerate(chip_stack[:8]):
            draw_chip(self.screen, cx, cy - i*7, d, radius=20)

    # ── Betting UI ─────────────────────────────────────────────────────────────
    def draw_betting_ui(self, mouse_pos):
        t = fnt_large.render("PLACE YOUR BET", True, CLR_GOLD)
        self.screen.blit(t,(SCREEN_W//2-t.get_width()//2, 285))

        for d, rect in self.chip_btns:
            hov = rect.collidepoint(mouse_pos)
            cx, cy = rect.centerx, rect.centery
            draw_chip(self.screen, cx, cy, d, radius=26)
            if hov:
                pygame.draw.circle(self.screen, CLR_WHITE,(cx,cy),28,2)

        inp_rect = pygame.Rect(SCREEN_W//2-90, 490, 180, 42)
        pygame.draw.rect(self.screen,(20,20,20),inp_rect,border_radius=6)
        border = CLR_GOLD
        pygame.draw.rect(self.screen, border, inp_rect, 2, border_radius=6)
        cursor = "|" if pygame.time.get_ticks()%900 < 450 else ""
        inp_lbl = fnt_small.render("$"+self.bet_input+cursor, True, CLR_WHITE)
        self.screen.blit(inp_lbl,(inp_rect.x+10, inp_rect.y+10))

        hint = fnt_tiny.render("Type amount or click chips  |  ENTER to confirm",
                               True, CLR_GRAY)
        self.screen.blit(hint,(SCREEN_W//2-hint.get_width()//2, 538))

        if self.bet > 0:
            bl = fnt_med.render(f"Current bet: ${self.bet}", True, CLR_GOLD)
            self.screen.blit(bl,(SCREEN_W//2-bl.get_width()//2, 558))

        if self.input_error:
            err = fnt_small.render(self.input_error, True, CLR_RED_LIGHT)
            self.screen.blit(err,(SCREEN_W//2-err.get_width()//2, 612))

        self.btn_deal.draw(self.screen)

    # ── Result overlay ─────────────────────────────────────────────────────────
    def draw_result_overlay(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        pygame.draw.rect(overlay,(0,0,0,170),(0,0,SCREEN_W,SCREEN_H))
        self.screen.blit(overlay,(0,0))

        is_win  = "WIN" in self.result_text or "BLACKJACK" in self.result_text
        is_push = "PUSH" in self.result_text
        col     = (CLR_GOLD if "BLACKJACK" in self.result_text
                   else (CLR_WHITE if is_push
                         else (CLR_RED_LIGHT if not is_win else (100,230,100))))

        rt = fnt_huge.render(self.result_text, True, col)
        self.screen.blit(rt,(SCREEN_W//2-rt.get_width()//2,
                             SCREEN_H//2-rt.get_height()//2-40))

        rs = fnt_med.render(self.