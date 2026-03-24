import pygame
import random
from enum import Enum
from collections import namedtuple

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
FPS = 60

# Colors
COLOR_GREEN = (34, 139, 34)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (220, 20, 60)
COLOR_GOLD = (255, 215, 0)
COLOR_GRAY = (200, 200, 200)
COLOR_DARK_GRAY = (100, 100, 100)

# Card
Card = namedtuple('Card', ['suit', 'rank'])

class GameState(Enum):
    BETTING = 1
    DEALING = 2
    PLAYING = 3
    DEALER_TURN = 4
    GAME_OVER = 5

class BlackjackGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Blackjack")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        self.reset_game()
    
    def reset_game(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.player_balance = 1000
        self.current_bet = 0
        self.state = GameState.BETTING
        self.bet_input = ""
        self.message = "Enter bet amount (10-500):"
        self.result = ""
    
    def create_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        deck = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(deck)
        return deck
    
    def reshuffle_if_needed(self):
        if len(self.deck) < 10:
            self.deck = self.create_deck()
    
    def deal_card(self):
        self.reshuffle_if_needed()
        return self.deck.pop()
    
    def card_value(self, rank):
        if rank in ['J', 'Q', 'K']:
            return 10
        elif rank == 'A':
            return 11
        else:
            return int(rank)
    
    def hand_value(self, hand):
        total = sum(self.card_value(card.rank) for card in hand)
        aces = sum(1 for card in hand if card.rank == 'A')
        
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def is_blackjack(self, hand):
        return len(hand) == 2 and self.hand_value(hand) == 21
    
    def handle_betting_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.bet_input:
                try:
                    bet = int(self.bet_input)
                    if 10 <= bet <= min(500, self.player_balance):
                        self.current_bet = bet
                        self.player_balance -= bet
                        self.state = GameState.DEALING
                        self.deal_initial_hands()
                        self.message = ""
                    else:
                        self.message = f"Bet must be 10-{min(500, self.player_balance)}"
                        self.bet_input = ""
                except ValueError:
                    self.message = "Invalid input. Enter a number."
                    self.bet_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.bet_input = self.bet_input[:-1]
            elif event.unicode.isdigit():
                if len(self.bet_input) < 3:
                    self.bet_input += event.unicode
    
    def deal_initial_hands(self):
        self.player_hand = [self.deal_card(), self.deal_card()]
        self.dealer_hand = [self.deal_card(), self.deal_card()]
        self.state = GameState.PLAYING
        self.result = ""
        
        if self.is_blackjack(self.player_hand):
            self.state = GameState.GAME_OVER
            self.result = "BLACKJACK! You win!"
            self.player_balance += self.current_bet * 2.5
    
    def handle_playing_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:  # Hit
                self.player_hand.append(self.deal_card())
                if self.hand_value(self.player_hand) > 21:
                    self.state = GameState.GAME_OVER
                    self.result = "BUST! You lose."
            elif event.key == pygame.K_s:  # Stand
                self.state = GameState.DEALER_TURN
                self.play_dealer()
    
    def play_dealer(self):
        while self.hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deal_card())
        
        self.determine_winner()
        self.state = GameState.GAME_OVER
    
    def determine_winner(self):
        player_value = self.hand_value(self.player_hand)
        dealer_value = self.hand_value(self.dealer_hand)
        
        if dealer_value > 21:
            self.result = "Dealer busts! You win!"
            self.player_balance += self.current_bet * 2
        elif player_value > dealer_value:
            self.result = "You win!"
            self.player_balance += self.current_bet * 2
        elif dealer_value > player_value:
            self.result = "Dealer wins."
        else:
            self.result = "Push (Tie)."
            self.player_balance += self.current_bet
    
    def handle_game_over_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.player_balance > 0:
                self.reset_game()
            else:
                self.message = "Game Over! No balance left."
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.state == GameState.BETTING:
                self.handle_betting_input(event)
            elif self.state == GameState.PLAYING:
                self.handle_playing_input(event)
            elif self.state == GameState.GAME_OVER:
                self.handle_game_over_input(event)
        
        return True
    
    def draw_card(self, card, x, y):
        card_width, card_height = 80, 120
        pygame.draw.rect(self.screen, COLOR_WHITE, (x, y, card_width, card_height))
        pygame.draw.rect(self.screen, COLOR_BLACK, (x, y, card_width, card_height), 2)
        
        is_red = card.suit in ['♥', '♦']
        color = COLOR_RED if is_red else COLOR_BLACK
        
        rank_text = self.font_medium.render(card.rank, True, color)
        suit_text = self.font_large.render(card.suit, True, color)
        
        self.screen.blit(rank_text, (x + 10, y + 10))
        self.screen.blit(suit_text, (x + 20, y + 50))
    
    def draw_card_back(self, x, y):
        card_width, card_height = 80, 120
        pygame.draw.rect(self.screen, COLOR_DARK_GRAY, (x, y, card_width, card_height))
        pygame.draw.rect(self.screen, COLOR_GOLD, (x, y, card_width, card_height), 3)
    
    def draw(self):
        self.screen.fill(COLOR_GREEN)
        
        # Title
        title = self.font_large.render("BLACKJACK", True, COLOR_GOLD)
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Balance
        balance_text = self.font_small.render(f"Balance: ${self.player_balance}", True, COLOR_WHITE)
        self.screen.blit(balance_text, (20, 20))
        
        if self.state == GameState.BETTING:
            self.draw_betting_screen()
        else:
            self.draw_game_screen()
        
        pygame.display.flip()
    
    def draw_betting_screen(self):
        prompt = self.font_medium.render(self.message, True, COLOR_WHITE)
        self.screen.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, 150))
        
        input_box_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 280, 200, 50)
        pygame.draw.rect(self.screen, COLOR_WHITE, input_box_rect)
        pygame.draw.rect(self.screen, COLOR_GOLD, input_box_rect, 3)
        
        input_text = self.font_medium.render(self.bet_input, True, COLOR_BLACK)
        self.screen.blit(input_text, (input_box_rect.x + 10, input_box_rect.y + 5))
        
        instructions = self.font_small.render("Press ENTER to confirm", True, COLOR_WHITE)
        self.screen.blit(instructions, (WINDOW_WIDTH // 2 - instructions.get_width() // 2, 380))
    
    def draw_game_screen(self):
        # Dealer section
        dealer_label = self.font_small.render("Dealer", True, COLOR_WHITE)
        self.screen.blit(dealer_label, (50, 100))
        
        for i, card in enumerate(self.dealer_hand):
            if self.state == GameState.DEALER_TURN or len(self.dealer_hand) == 2 and i > 0:
                self.draw_card(card, 50 + i * 100, 140)
            else:
                if i == 0:
                    self.draw_card(card, 50, 140)
                else:
                    self.draw_card_back(50 + i * 100, 140)
        
        if self.state == GameState.GAME_OVER:
            dealer_value = self.hand_value(self.dealer_hand)
            dealer_score = self.font_small.render(f"Value: {dealer_value}", True, COLOR_GOLD)
            self.screen.blit(dealer_score, (50, 280))
        
        # Player section
        player_label = self.font_small.render("Player", True, COLOR_WHITE)
        self.screen.blit(player_label, (50, 350))
        
        for i, card in enumerate(self.player_hand):
            self.draw_card(card, 50 + i * 100, 390)
        
        player_value = self.hand_value(self.player_hand)
        player_score = self.font_small.render(f"Value: {player_value}", True, COLOR_GOLD)
        self.screen.blit(player_score, (50, 530))
        
        # Bet info
        bet_text = self.font_small.render(f"Current Bet: ${self.current_bet}", True, COLOR_WHITE)
        self.screen.blit(bet_text, (WINDOW_WIDTH - 300, 100))
        
        # Controls or result
        if self.state == GameState.PLAYING:
            controls = self.font_small.render("H (Hit)  S (Stand)", True, COLOR_WHITE)
            self.screen.blit(controls, (WINDOW_WIDTH // 2 - controls.get_width() // 2, 600))
        elif self.state == GameState.GAME_OVER:
            result = self.font_medium.render(self.result, True, COLOR_GOLD)
            self.screen.blit(result, (WINDOW_WIDTH // 2 - result.get_width() // 2, 580))
            
            if self.player_balance > 0:
                continue_text = self.font_small.render("Press SPACE to continue", True, COLOR_WHITE)
                self.screen.blit(continue_text, (WINDOW_WIDTH // 2 - continue_text.get_width() // 2, 640))
            else:
                game_over = self.font_medium.render("Game Over!", True, COLOR_RED)
                self.screen.blit(game_over, (WINDOW_WIDTH // 2 - game_over.get_width() // 2, 640))
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = BlackjackGame()
    game.run()