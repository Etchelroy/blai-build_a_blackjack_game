import pygame
import random
import sys

pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 750
FPS = 60

# Colours
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
CLR_SHADOW      = (0,   0,   0, 120)
CLR_OVERLAY     = (0,   0,   0, 170)
CLR_CYAN        = (0,  200, 220)

CARD_W, CARD_H  = 80, 115
CARD_RADIUS     = 8

# ── Fonts ──────────────────────────────────────────────────────────────────────
fnt_huge   = pygame.font.SysFont("Georgia",       64, bold=True)
fnt_large  = pygame.font.SysFont("Georgia",       36, bold=True)
fnt_med    = pygame.font.SysFont("Georgia",       26, bold=True)
fnt_small  = pygame.font.SysFont("Arial",         20)
fnt_tiny   = pygame.font.SysFont("Arial",         16)
fnt_card   = pygame.font.SysFont("Georgia",       22, bold=True)
fnt_card_s = pygame.font.SysFont("Georgia",       13, bold=True)
fnt_suit   = pygame.font.SysFont("Segoe UI Symbol", 28)

SUITS  = ["♠", "♥", "♦", "♣"]
RANKS  = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
RED_SUITS = {"♥", "♦"}

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

# ── Card drawing ───────────────────────────────────────────────────────────────
def draw_card_surface(rank, suit, face_up=True):
    surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    # Shadow
    shadow = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0,0,0,60), (4, 4, CARD_W, CARD_H), border_radius=CARD_RADIUS)
    surf.blit(shadow, (0,0))

    if not face_up:
        # Card back
        pygame.draw.rect(surf, (30, 30, 120), (0, 0, CARD_W, CARD_H), border_radius=CARD_RADIUS)
        pygame.draw.rect(surf, (50, 50, 160), (5, 5, CARD_W-10, CARD_H-10), border_radius=6)
        # Diagonal pattern
        for i in range(-CARD_H, CARD_W, 12):
            pygame.draw.line(surf, (40, 40, 140), (i, 0), (i+CARD_H, CARD_H), 1)
        pygame.draw.rect(surf, CLR_GOLD, (0, 0, CARD_W, CARD_H), 2, border_radius=CARD_RADIUS)
        return surf

    is_red = suit in RED_SUITS
    txt_colour = CLR_RED if is_red else (20, 20, 20)

    # Card face
    pygame.draw.rect(surf, CLR_WHITE, (0, 0, CARD_W, CARD_H), border_radius=CARD_RADIUS)
    pygame.draw.rect(surf, CLR_GRAY, (0, 0, CARD_W, CARD_H), 1, border_radius=CARD_RADIUS)

    # Top-left rank + suit
    r_surf = fnt_card_s.render(rank, True, txt_colour)
    s_surf = fnt_card_s.render(suit, True, txt_colour)
    surf.blit(r_surf, (5, 3))
    surf.blit(s_surf, (5, 3 + r_surf.get_height()))

    # Bottom-right (rotated 180°)
    r_surf2 = pygame.transform.rotate(r_surf, 180)
    s_surf2 = pygame.transform.rotate(s_surf, 180)
    surf.blit(r_surf2, (CARD_W - r_surf2.get_width() - 5, CARD_H - r_surf2.get_height() - 3))
    surf.blit(s_surf2, (CARD_W - s_surf2.get_width() - 5, CARD_H - r_surf2.get_height() - s_surf2.get_height() - 3))

    # Centre suit
    cs = pygame.font.SysFont("Segoe UI Symbol", 38).render(suit, True, txt_colour)
    surf.blit(cs, (CARD_W//2 - cs.get_width()//2, CARD_H//2 - cs.get_height()//2))

    return surf

# ── Chip drawing ───────────────────────────────────────────────────────────────
CHIP_DENOMINATIONS = [5, 25, 100, 500]
CHIP_COLOURS = {5: CLR_CHIP_RED, 25: CLR_CHIP_GREEN, 100: CLR_CHIP_BLUE, 500: CLR_CHIP_BLACK}

def draw_chip(surface, x, y, denom, radius=22, alpha=255):
    col = CHIP_COLOURS[denom]
    # Outer ring
    pygame.draw.circle(surface, col, (x, y), radius)
    pygame.draw.circle(surface, CLR_WHITE, (x, y), radius, 2)
    # Inner circle
    pygame.draw.circle(surface, col, (x, y), radius - 6)
    pygame.draw.circle(surface, CLR_WHITE, (x, y), radius - 6, 1)
    # Label
    lbl = fnt_tiny.render(f"${denom}", True, CLR_WHITE)
    surface.blit(lbl, (x - lbl.get_width()//2, y - lbl.get_height()//2))

# ── Button ─────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, text, colour, hover_colour, text_colour=CLR_WHITE, font=None):
        self.rect         = pygame.Rect(rect)
        self.text         = text
        self.colour       = colour
        self.hover_colour = hover_colour
        self.text_colour  = text_colour
        self.font         = font or fnt_med
        self.hovered      = False
        self.enabled      = True

    def draw(self, surface):
        col = self.hover_colour if (self.hovered and self.enabled) else self.colour
        if not self.enabled:
            col = CLR_GRAY_DARK
        pygame.draw.rect(surface, col, self.rect, border_radius=10)
        pygame.draw.rect(surface, CLR_WHITE if self.enabled else CLR_GRAY, self.rect, 2, border_radius=10)
        lbl = self.font.render(self.text, True, self.text_colour if self.enabled else CLR_GRAY)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()//2,
                            self.rect.centery - lbl.get_height()//2))

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, event):
        return (self.enabled and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1 and self.rect.collidepoint(event.pos))

# ── Animated card ──────────────────────────────────────────────────────────────
class AnimCard:
    def __init__(self, rank, suit, start, end, face_up=True, delay=0):
        self.rank    = rank
        self.suit    = suit
        self.start   = list(start)
        self.end     = list(end)
        self.pos     = list(start)
        self.face_up = face_up
        self.delay   = delay   # frames before moving
        self.t       = 0       # 0→1 progress
        self.speed   = 0.07
        self.done    = False

    def update(self):
        if self.delay > 0:
            self.delay -= 1
            return
        if self.done:
            return
        self.t = min(1.0, self.t + self.speed)
        # Ease-out cubic
        ease = 1 - (1 - self.t) ** 3
        self.pos[0] = self.start[0] + (self.end[0] - self.start[0]) * ease
        self.pos[1] = self.start[1] + (self.end[1] - self.start[1]) * ease
        if self.t >= 1.0:
            self.done = True

    def draw(self, surface):
        surf = draw_card_surface(self.rank, self.suit, self.face_up)
        surface.blit(surf, (int(self.pos[0]), int(self.pos[1])))

# ── Particle ───────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, colour):
        self.x   = x
        self.y   = y
        angle    = random.uniform(0, 6.28)
        speed    = random.uniform(2, 7)
        self.vx  = speed * random.uniform(-1,1)
        self.vy  = speed * random.uniform(-3, 0)
        self.col = colour
        self.life = random.randint(40, 80)
        self.r   = random.randint(4, 9)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.18
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, int(255 * self.life / 80))
        s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, alpha), (self.r, self.r), self.r)
        surface.blit(s, (int(self.x)-self.r, int(self.y)-self.r))

# ── Main Game ──────────────────────────────────────────────────────────────────
class BlackjackGame:
    STATE_BETTING     = "BETTING"
    STATE_DEALING     = "DEALING"
    STATE_PLAYER      = "PLAYER"
    STATE_DEALER      = "DEALER"
    STATE_RESULT      = "RESULT"
    STATE_GAMEOVER    = "GAMEOVER"

    DECK_POS   = (SCREEN_W//2 - CARD_W//2, 10)

    def __init__(self):
        self.screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("♠ Blackjack ♥")
        self.clock   = pygame.time.Clock()
        self.reset_game()

    # ── Full reset ─────────────────────────────────────────────────────────────
    def reset_game(self):
        self.balance  = 1000
        self.bet      = 0
        self.deck     = build_deck()
        self.state    = self.STATE_BETTING
        self.player_hand = []
        self.dealer_hand = []
        self.anim_cards  = []
        self.particles   = []
        self.result_text = ""
        self.result_sub  = ""
        self.message     = ""
        self.dealer_reveal = False
        self.dealer_timer  = 0
        self.result_timer  = 0
        self.bet_input     = ""
        self.input_active  = True
        self.input_error   = ""
        self._build_buttons()

    # ── Round reset ────────────────────────────────────────────────────────────
    def new_round(self):
        self.bet         = 0
        self.player_hand = []
        self.dealer_hand = []
        self.anim_cards  = []
        self.particles   = []
        self.result_text = ""
        self.result_sub  = ""
        self.message     = ""
        self.dealer_reveal = False
        self.dealer_timer  = 0
        self.result_timer  = 0
        self.bet_input     = ""
        self.input_active  = True
        self.input_error   = ""
        if len(self.deck) < 52:
            self.deck = build_deck()
        self.state = self.STATE_BETTING

    def _build_buttons(self):
        self.btn_deal  = Button((460, 630, 180, 52), "DEAL",  (20,120,50),  (30,160,70))
        self.btn_hit   = Button((320, 630, 160, 52), "HIT",   (20,120,50),  (30,160,70))
        self.btn_stand = Button((510, 630, 160, 52), "STAND", (160,30,30),  (200,50,50))
        self.btn_again = Button((420, 630, 260, 52), "NEW ROUND", (20,80,160),(30,110,200))

        # Chip buttons
        self.chip_btns = []
        cx_start = SCREEN_W//2 - (len(CHIP_DENOMINATIONS)*80)//2 + 20
        for i, d in enumerate(CHIP_DENOMINATIONS):
            rect = (cx_start + i*80 - 28, 565, 56, 56)
            self.chip_btns.append((d, pygame.Rect(rect)))

    # ── Card position helpers ──────────────────────────────────────────────────
    def _player_card_pos(self, idx):
        total = max(len(self.player_hand), idx+1)
        spread = min(total, 8)
        start_x = SCREEN_W//2 - (spread * (CARD_W - 20))//2
        return (start_x + idx * (CARD_W - 20), 420)

    def _dealer_card_pos(self, idx):
        total = max(len(self.dealer_hand), idx+1)
        spread = min(total, 8)
        start_x = SCREEN_W//2 - (spread * (CARD_W - 20))//2
        return (start_x + idx * (CARD_W - 20), 130)

    # ── Deal initial cards ─────────────────────────────────────────────────────
    def deal_initial(self):
        if not self.deck:
            self.deck = build_deck()
        self.state = self.STATE_DEALING
        self.player_hand = []
        self.dealer_hand = []
        self.anim_cards  = []

        order = [
            (True,  True),   # player card 1
            (False, False),  # dealer card 1 (face down)
            (True,  True),   # player card 2
            (False, True),   # dealer card 2 (face up)
        ]
        delay = 0
        for card_idx, (is_player, face_up) in enumerate(order):
            card = self.deck.pop()
            if is_player:
                dest_idx = len(self.player_hand)
                self.player_hand.append(card)
                dest = self._player_card_pos(dest_idx)
            else:
                dest_idx = len(self.dealer_hand)
                self.dealer_hand.append(card)
                dest = self._dealer_card_pos(dest_idx)
            ac = AnimCard(card[0], card[1], self.DECK_POS, dest, face_up=face_up, delay=delay)
            self.anim_cards.append(ac)
            delay += 12

    # ── Draw a card for player ─────────────────────────────────────────────────
    def player_draw(self):
        card = self.deck.pop()
        idx  = len(self.player_hand)
        self.player_hand.append(card)
        dest = self._player_card_pos(idx)
        ac = AnimCard(card[0], card[1], self.DECK_POS, dest, face_up=True)
        self.anim_cards.append(ac)

    # ── Draw a card for dealer ─────────────────────────────────────────────────
    def dealer_draw(self):
        card = self.deck.pop()
        idx  = len(self.dealer_hand)
        self.dealer_hand.append(card)
        dest = self._dealer_card_pos(idx)
        ac = AnimCard(card[0], card[1], self.DECK_POS, dest, face_up=True)
        self.anim_cards.append(ac)

    # ── Reveal dealer hole card ────────────────────────────────────────────────
    def reveal_hole_card(self):
        # Replace the face-down AnimCard with face-up version
        for ac in self.anim_cards:
            if not ac.face_up and ac.rank == self.dealer_hand[0][0] and ac.suit == self.dealer_hand[0][1]:
                ac.face_up = True
                break
        self.dealer_reveal = True

    # ── Resolve result ─────────────────────────────────────────────────────────
    def resolve(self):
        pv = hand_value(self.player_hand)
        dv = hand_value(self.dealer_hand)
        pBJ = is_blackjack(self.player_hand)
        dBJ = is_blackjack(self.dealer_hand)

        if bust(self.player_hand):
            result, sub, gain = "BUST", f"Dealer wins  –  you lose ${self.bet}", 0
        elif pBJ and dBJ:
            result, sub, gain = "PUSH", "Both Blackjack  –  bet returned", self.bet
        elif pBJ:
            win = int(self.bet * 2.5)
            result, sub, gain = "BLACKJACK!", f"♠ Blackjack pays 2.5x  +${win}", win
        elif dBJ:
            result, sub, gain = "DEALER BLACKJACK", f"Dealer wins  –  you lose ${self.bet}", 0
        elif bust(self.dealer_hand):
            win = self.bet * 2
            result, sub, gain = "DEALER BUSTS", f"You win  +${win}", win
        elif pv > dv:
            win = self.bet * 2
            result, sub, gain = "YOU WIN!", f"{pv} beats {dv}  –  +${win}", win
        elif dv > pv:
            result, sub, gain = "DEALER WINS", f"{dv} beats {pv}  –  you lose ${self.bet}", 0
        else:
            result, sub, gain = "PUSH", f"Tie at {pv}  –  bet returned", self.bet

        self.balance += gain
        self.result_text = result
        self.result_sub  = sub
        self.state = self.STATE_RESULT

        # Particles on win
        if gain > self.bet or "BLACKJACK" in result:
            for _ in range(80):
                col = random.choice([(212,175,55),(255,215,0),(255,255,100),(255,180,0)])
                self.particles.append(Particle(SCREEN_W//2, SCREEN_H//2, col))

    # ── Validate & place bet ───────────────────────────────────────────────────
    def place_bet(self, amount):
        total = self.bet + amount
        if total < 10:
            self.input_error = "Minimum bet is $10"
            return False
        if total > 500:
            self.input_error = "Maximum bet is $500"
            return False
        if total > self.balance:
            self.input_error = "Not enough balance!"
            return False
        self.bet = total
        self.input_error = ""
        return True

    def set_bet_from_input(self):
        try:
            val = int(self.bet_input)
        except ValueError:
            self.input_error = "Enter a valid number"
            return False
        if val < 10:
            self.input_error = "Minimum bet is $10"
            return False
        if val > 500:
            self.input_error = "Maximum bet is $500"
            return False
        if val > self.balance:
            self.input_error = "Not enough balance!"
            return False
        self.bet = val
        self.input_error = ""
        return True

    # ── Drawing helpers ────────────────────────────────────────────────────────
    def draw_table(self):
        # Felt gradient
        self.screen.fill(CLR_FELT)
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            r = int(CLR_FELT_DARK[0] + (CLR_FELT_LIGHT[0]-CLR_FELT_DARK[0])*t)
            g = int(CLR_FELT_DARK[1] + (CLR_FELT_LIGHT[1]-CLR_FELT_DARK[1])*t)
            b = int(CLR_FELT_DARK[2] + (CLR_FELT_LIGHT[2]-CLR_FELT_DARK[2])*t)
            pygame.draw.line(self.screen, (r,g,b), (0,y), (SCREEN_W,y))

        # Table oval
        pygame.draw.ellipse(self.screen, (4, 85, 28), (50, 40, SCREEN_W-100, SCREEN_H-100))
        pygame.draw.ellipse(self.screen, CLR_GOLD,     (50, 40, SCREEN_W-100, SCREEN_H-100), 3)

        # Centre divider text
        lbl = fnt_tiny.render("♠  BLACKJACK PAYS 2.5×  ♠  DEALER MUST HIT SOFT 17  ♠", True, CLR_GOLD)
        self.screen.blit(lbl, (SCREEN_W//2 - lbl.get_width()//2, SCREEN_H//2 - 12))

        # Deck stack (visual)
        for i in range(5, 0, -1):
            pygame.draw.rect(self.screen, (25, 25, 105),
                             (self.DECK_POS[0]+i, self.DECK_POS[1]+i, CARD_W, CARD_H),
                             border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, (30, 30, 130),
                         (self.DECK_POS[0], self.DECK_POS[1], CARD_W, CARD_H),
                         border_radius=CARD_RADIUS)
        pygame.draw.rect(self.screen, CLR_GOLD,
                         (self.DECK_POS[0], self.DECK_POS[1], CARD_W, CARD_H),
                         2, border_radius=CARD_RADIUS)
        dk = fnt_tiny.render("SHOE", True, CLR_GOLD)
        self.screen.blit(dk, (self.DECK_POS[0]+CARD_W//2-dk.get_width()//2,
                               self.DECK_POS[1]+CARD_H//2-dk.get_height()//2))

    def draw_balance_bet(self):
        # Balance
        bal_bg = pygame.Surface((220, 48), pygame.SRCALPHA)
        pygame.draw.rect(bal_bg, (0,0,0,130), (0,0,220,48), border_radius=8)
        self.screen.blit(bal_bg, (20, 20))
        lbl = fnt_med.render(f"Balance: ${self.balance}", True, CLR_GOLD)
        self.screen.blit(lbl, (30, 30))

        # Bet
        if self.bet > 0:
            bet_bg = pygame.Surface((180, 48), pygame.SRCALPHA)
            pygame.draw.rect(bet_bg, (0,0,0,130), (0,0,180,48), border_radius=8)
            self.screen.blit(bet_bg, (SCREEN_W-200, 20))
            blbl = fnt_med.render(f"Bet: ${self.bet}", True, CLR_GOLD)
            self.screen.blit(blbl, (SCREEN_W-200+10, 30))

    def draw_hand_cards(self):
        """Draw cards from anim_cards list (handles animation)."""
        for ac in self.anim_cards:
            ac.draw(self.screen)

    def draw_hand_value(self, hand, x, y, hide_one=False):
        if hide_one and not self.dealer_reveal:
            # Only show value of face-up card
            if len(hand) > 1:
                val = hand_value([hand[1]])
                lbl = fnt_small.render(f"Score: {val}", True, CLR_WHITE)
            else:
                return
        else:
            val = hand_value(hand)
            colour = CLR_RED_LIGHT if val > 21 else CLR_WHITE
            lbl = fnt_small.render(f"Score: {val}", True, colour)
        bg = pygame.Surface((lbl.get_width()+16, lbl.get_height()+8), pygame.SRCALPHA)
        pygame.draw.rect(bg, (0,0,0,140), (0,0,bg.get_width(),bg.get_height()), border_radius=6)
        self.screen.blit(bg, (x-8, y-4))
        self.screen.blit(lbl, (x, y))

    def draw_chips_in_bet_area(self):
        """Show stacked chips representing current bet."""
        if self.bet <= 0:
            return
        # Decompose bet into chips
        remaining = self.bet
        chip_stack = []
        for d in sorted(CHIP_DENOMINATIONS, reverse=True):
            while remaining >= d:
                chip_stack.append(d)
                remaining -= d

        cx = SCREEN_W//2
        cy = 345
        for i, d in enumerate(chip_stack[:8]):
            draw_chip(self.screen, cx, cy - i*6, d, radius=20)

    # ── Betting screen ─────────────────────────────────────────────────────────
    def draw_betting_ui(self, mouse_pos):
        # Title
        t = fnt_large.render("PLACE YOUR BET", True, CLR_GOLD)
        self.screen.blit(t, (SCREEN_W//2-t.get_width()//2, 280))

        # Chip buttons
        for d, rect in self.chip_btns:
            hovered = rect.collidepoint(mouse_pos)
            cx, cy = rect.centerx, rect.centery
            draw_chip(self.screen, cx, cy, d, radius=26)
            if hovered:
                pygame.draw.circle(self.screen, CLR_WHITE, (cx, cy), 28, 2)

        # Text input box
        inp_rect = pygame.Rect(SCREEN_W//2-90, 487, 180, 42)
        pygame.draw.rect(self.screen, (20,20,20), inp_rect, border_radius=6)
        border_col = CLR_GOLD if self.input_active else CLR_GRAY
        pygame.draw.rect(self.screen, border_col, inp_rect, 2, border_radius=6)
        inp_lbl = fnt_small.render("$"+self.bet_input + ("|" if pygame.time.get_ticks()%900<450 else ""),
                                   True, CLR_WHITE)
        self.screen.blit(inp_lbl, (inp_rect.x+10, inp_rect.y+10))
        hint = fnt_tiny.render("Type amount or click chips", True, CLR_GRAY)
        self.screen.blit(hint, (SCREEN_W//2-hint.get_width()//2, 535))

        # Current bet display
        if self.bet > 0:
            bl = fnt_med.render(f"Current bet: ${self.bet}", True