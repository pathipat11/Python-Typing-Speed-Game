import pygame
from pygame.locals import *
import sys
import time
import random
import json
import os

class Game:
    def __init__(self):
        self.w = 750
        self.h = 500
        self.active = False
        self.word = ''
        self.input_text = ''
        self.time_start = 0
        self.total_time = 0
        self.accuracy = 0
        self.wpm = 0
        self.end = False

        # colors
        self.HEAD_C = (255, 213, 102)
        self.TEXT_C = (200, 200, 200)
        self.RESULT_C = (255, 70, 70)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 80, 80)
        self.GRAY = (150, 150, 150)

        pygame.init()
        self.open_img = pygame.image.load('type-speed-open.png')
        self.open_img = pygame.transform.scale(self.open_img, (self.w, self.h))

        self.bg = pygame.image.load('background.jpg')
        self.bg = pygame.transform.scale(self.bg, (self.w, self.h))

        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Type Speed Test')

        # stats
        self.best_wpm = 0
        self.best_accuracy = 0
        self.load_stats()

    def draw_text(self, screen, msg, y, fsize, color, center=True, x=None):
        font = pygame.font.Font(None, fsize)
        text = font.render(msg, True, color)
        if center:
            text_rect = text.get_rect(center=(self.w/2, y))
        else:
            text_rect = text.get_rect(topleft=(x, y))
        screen.blit(text, text_rect)

    def get_sentence(self):
        f = open('sentences.txt').read()
        sentences = f.split('\n')
        return random.choice(sentences).strip()

    def load_stats(self):
        if os.path.exists("stats.json"):
            with open("stats.json", "r") as f:
                data = json.load(f)
                self.best_wpm = data.get("best_wpm", 0)
                self.best_accuracy = data.get("best_accuracy", 0)

    def save_stats(self):
        if self.wpm > self.best_wpm:
            self.best_wpm = self.wpm
        if self.accuracy > self.best_accuracy:
            self.best_accuracy = self.accuracy
        with open("stats.json", "w") as f:
            json.dump({
                "best_wpm": self.best_wpm,
                "best_accuracy": self.best_accuracy
            }, f)
            
    def update_wpm(self):
        if self.active and not self.end:
            elapsed = time.time() - self.time_start
            if elapsed > 0:
                correct_chars = sum(
                    1 for i, c in enumerate(self.input_text)
                    if i < len(self.word) and self.input_text[i] == self.word[i]
                )
                self.wpm = (correct_chars / 5) / (elapsed / 60)
                self.accuracy = (correct_chars / max(len(self.input_text),1)) * 100

    def show_results(self):
        if not self.end:
            self.total_time = time.time() - self.time_start
            correct_chars = sum(
                1 for i, c in enumerate(self.input_text)
                if i < len(self.word) and self.input_text[i] == self.word[i]
            )
            self.accuracy = (correct_chars / len(self.word)) * 100
            self.wpm = (correct_chars / 5) / (self.total_time / 60)
            self.end = True
            self.save_stats()

    def draw_sentence(self):
        x = 60
        y = 200
        font = pygame.font.Font(None, 36)
        cursor_x = x
        cursor_y = y
        max_width = self.w - 100

        for i, c in enumerate(self.word):
            if i < len(self.input_text):
                if self.input_text[i] == c:
                    color = self.GREEN
                else:
                    color = self.RED
            else:
                color = self.TEXT_C

            ch = font.render(c, True, color)
            
            if x + ch.get_width() > max_width and c == " ":
                x = 60
                y += 40
            
            self.screen.blit(ch, (x, y))

            if i < len(self.input_text):
                cursor_x = x + ch.get_width()
                cursor_y = y
            elif i == len(self.input_text):
                cursor_x = x
                cursor_y = y

            x += ch.get_width()

        if not self.end and self.active:
            cursor_time = pygame.time.get_ticks() // 500 % 2
            if cursor_time == 0:
                pygame.draw.line(self.screen, self.GRAY, (cursor_x, cursor_y), (cursor_x, cursor_y + 28), 2)
                
        self.update_wpm()
        if self.active and not self.end:
            self.draw_text(self.screen, f"WPM: {round(self.wpm)}  Accuracy: {round(self.accuracy)}%", 150, 36, self.HEAD_C)

    def draw_reset_button(self):
        pygame.draw.rect(self.screen, (80, 80, 80), (self.w/2 - 60, self.h - 80, 120, 40), border_radius=8)
        self.draw_text(self.screen, "Reset", self.h - 60, 28, (255, 255, 255))

    def run(self):
        self.reset_game()
        self.running = True
        while self.running:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.bg, (0, 0))

            # heading
            self.draw_text(self.screen, "Typing Speed Test", 80, 60, self.HEAD_C)
            self.draw_sentence()

            if self.end:
                results = f"Time: {round(self.total_time)}s   Accuracy: {round(self.accuracy)}%   WPM: {round(self.wpm)}"
                self.draw_text(self.screen, results, 350, 28, self.RESULT_C)
                best = f"🏆 Best WPM: {round(self.best_wpm)}   Best Accuracy: {round(self.best_accuracy)}%"
                self.draw_text(self.screen, best, 400, 26, self.HEAD_C)
                self.draw_reset_button()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    sys.exit()
                elif event.type == KEYDOWN:
                    if not self.end:
                        if not self.active:
                            self.active = True
                            self.time_start = time.time()
                        if event.key == pygame.K_RETURN:
                            self.show_results()
                        elif event.key == pygame.K_BACKSPACE:
                            if len(self.input_text) > 0:
                                self.input_text = self.input_text[:-1]
                        else:
                            try:
                                self.input_text += event.unicode
                            except:
                                pass
                    else:
                        if event.key == pygame.K_ESCAPE:
                            self.reset_game()
                elif event.type == MOUSEBUTTONUP and self.end:
                    x, y = pygame.mouse.get_pos()
                    if self.w/2 - 60 <= x <= self.w/2 + 60 and self.h - 80 <= y <= self.h - 40:
                        self.reset_game()

    def reset_game(self):
        self.screen.blit(self.open_img, (0, 0))
        pygame.display.update()
        time.sleep(1)

        self.end = False
        self.active = False
        self.input_text = ''
        self.word = self.get_sentence()
        self.time_start = 0
        self.total_time = 0
        self.wpm = 0
        self.accuracy = 0


Game().run()
