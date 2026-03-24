import pygame
import random
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
BG_COLOR = (0, 100, 0)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (255, 215, 0)

class GameState(Enum):
    BETTING = 1
    DEALING = 2
    PLAYING = 3
    DEALER_TURN = 4
    GAME_OVER = 5

class Card:
    SUITS = ['♠', '♥', '♦', '♣']
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    RANK_VALUES = {'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}
    
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
    
    def __repr__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in Card.SUITS for rank in Card.RANKS]
        random.shuffle(self.cards)
    
    def draw(self):
        if len(self.cards) < 10:
            self.__init__()  # Reshuffle when low
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        self.cards.append(card)
    
    def value(self):
        total = 0
        aces = 0
        for card in self.cards:
            total += Card.RANK_VALUES[card.rank]
            if card.rank == 'A':
                aces += 1
        
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.value() == 21
    
    def is_bust(self):
        return self.value() > 21

class BlackjackGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Blackjack")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.player_balance = 1000
        self.current_bet = 0
        self.state = GameState.BETTING
        self.message = "Enter bet amount (10-500) and press ENTER"
        self.bet_input = ""
        self.game_result = ""
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.BETTING:
                    if event.key == pygame.K_RETURN and self.bet_input:
                        try:
                            bet = int(self.bet_input)
                            if 10 <= bet <= min(500, self.player_balance):
                                self.current_bet = bet
                                self.bet_input = ""
                                self.start_round()
                            else:
                                self.message = f"Bet must be 10-{min(500, self.player_balance)}"
                        except:
                            self.message = "Invalid bet amount"
                    elif event.key == pygame.K_BACKSPACE:
                        self.bet_input = self.bet_input[:-1]
                    elif event.unicode.isdigit():
                        if len(self.bet_input) < 3:
                            self.bet_input += event.unicode
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_h:
                        self.player_hand.add_card(self.deck.draw())
                        if self.player_hand.is_bust():
                            self.end_round()
                    elif event.key == pygame.K_s:
                        self.state = GameState.DEALER_TURN
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.BETTING
                        self.message = "Enter bet amount (10-500) and press ENTER"
        
        return True
    
    def start_round(self):
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.player_hand.add_card(self.deck.draw())
        self.player_hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())
        self.game_result = ""
        
        if self.player_hand.is_blackjack():
            self.state = GameState.DEALER_TURN
        else:
            self.state = GameState.PLAYING
            self.message = "Hit (H) or Stand (S)?"
    
    def end_round(self):
        self.state = GameState.DEALER_TURN
    
    def dealer_play(self):
        while self.dealer_hand.value() < 17:
            self.dealer_hand.add_card(self.deck.draw())
        
        self.determine_winner()
        self.state = GameState.GAME_OVER
    
    def determine_winner(self):
        player_value = self.player_hand.value()
        dealer_value = self.dealer_hand.value()
        
        if self.player_hand.is_blackjack() and not self.dealer_hand.is_blackjack():
            self.player_balance += int(self.current_bet * 1.5)
            self.game_result = f"BLACKJACK! Won ${int(self.current_bet * 1.5)}"
        elif player_value > 21:
            self.player_balance -= self.current_bet
            self.game_result = f"BUST! Lost ${self.current_bet}"
        elif dealer_value > 21:
            self.player_balance += self.current_bet
            self.game_result = f"Dealer BUST! Won ${self.current_bet}"
        elif player_value > dealer_value:
            self.player_balance += self.current_bet
            self.game_result = f"You WIN! Won ${self.current_bet}"
        elif dealer_value > player_value:
            self.player_balance -= self.current_bet
            self.game_result = f"Dealer WINS! Lost ${self.current_bet}"
        else:
            self.game_result = "PUSH (Tie)"
        
        if self.player_balance <= 0:
            self.game_result += " - GAME OVER!"
    
    def draw_card(self, card, x, y):
        card_width, card_height = 80, 120
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, card_width, card_height))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, card_width, card_height), 2)
        
        color = (255, 0, 0) if card.suit in ['♥', '♦'] else (0, 0, 0)
        rank_text = self.font_medium.render(card.rank, True, color)
        suit_text = self.font_large.render(card.suit, True, color)
        
        self.screen.blit(rank_text, (x + 10, y + 10))
        self.screen.blit(suit_text, (x + 20, y + 60))
    
    def draw_back_card(self, x, y):
        card_width, card_height = 80, 120
        pygame.draw.rect(self.screen, (0, 50, 100), (x, y, card_width, card_height))
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, card_width, card_height), 3)
    
    def render(self):
        self.screen.fill(BG_COLOR)
        
        # Balance and bet
        balance_text = self.font_medium.render(f"Balance: ${self.player_balance}", True, ACCENT_COLOR)
        self.screen.blit(balance_text, (20, 20))
        
        if self.state == GameState.BETTING:
            title = self.font_large.render("BLACKJACK", True, ACCENT_COLOR)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
            
            msg = self.font_small.render(self.message, True, TEXT_COLOR)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 150))
            
            bet_display = self.font_medium.render(f"Bet: ${self.bet_input}", True, TEXT_COLOR)
            self.screen.blit(bet_display, (SCREEN_WIDTH // 2 - bet_display.get_width() // 2, 250))
            
            info = self.font_small.render("Press ENTER to confirm bet", True, TEXT_COLOR)
            self.screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, 350))
        
        else:
            # Dealer hand
            dealer_text = self.font_medium.render("DEALER", True, ACCENT_COLOR)
            self.screen.blit(dealer_text, (50, 50))
            for i, card in enumerate(self.dealer_hand.cards):
                if self.state == GameState.PLAYING and i == 1:
                    self.draw_back_card(50 + i * 100, 100)
                else:
                    self.draw_card(card, 50 + i * 100, 100)
            
            if self.state != GameState.PLAYING:
                dealer_value_text = self.font_medium.render(f"Value: {self.dealer_hand.value()}", True, TEXT_COLOR)
                self.screen.blit(dealer_value_text, (50, 240))
            
            # Player hand
            player_text = self.font_medium.render("YOUR HAND", True, ACCENT_COLOR)
            self.screen.blit(player_text, (50, 350))
            for i, card in enumerate(self.player_hand.cards):
                self.draw_card(card, 50 + i * 100, 400)
            
            player_value_text = self.font_medium.render(f"Value: {self.player_hand.value()}", True, TEXT_COLOR)
            self.screen.blit(player_value_text, (50, 540))
            
            # Message
            if self.state == GameState.PLAYING:
                msg = self.font_small.render(self.message, True, TEXT_COLOR)
                self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 600))
            
            elif self.state == GameState.GAME_OVER:
                result = self.font_large.render(self.game_result, True, ACCENT_COLOR)
                self.screen.blit(result, (SCREEN_WIDTH // 2 - result.get_width() // 2, 600))
                
                if self.player_balance > 0:
                    continue_text = self.font_small.render("Press SPACE to continue", True, TEXT_COLOR)
                    self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 650))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            if self.state == GameState.DEALER_TURN:
                self.dealer_play()
            
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = BlackjackGame()
    game.run()