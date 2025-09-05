import pygame
from pygame.locals import *
import sys
import time
import random
import json
import os

# 750 x 500    
class Game:
    def __init__(self):
        self.w=750
        self.h=500
        self.reset=True
        self.active = False
        self.input_text=''
        self.word = ''
        self.time_start = 0
        self.total_time = 0
        self.accuracy = '0%'
        self.results = 'Time:0 Accuracy:0 % Wpm:0 '
        self.wpm = 0
        self.end = False
        self.HEAD_C = (255,213,102)
        self.TEXT_C = (200,200,200)
        self.RESULT_C = (255,70,70)
        self.GREEN = (0,255,0)
        self.RED = (255,80,80)
        
        pygame.init()
        self.open_img = pygame.image.load('type-speed-open.png')
        self.open_img = pygame.transform.scale(self.open_img, (self.w,self.h))

        self.bg = pygame.image.load('background.jpg')
        self.bg = pygame.transform.scale(self.bg, (self.w,self.h))

        self.screen = pygame.display.set_mode((self.w,self.h))
        pygame.display.set_caption('Type Speed test')

        # โหลดสถิติ
        self.best_wpm = 0
        self.best_accuracy = 0
        self.load_stats()
        
    def draw_text(self, screen, msg, y ,fsize, color, center=True, x=None):
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
        sentence = random.choice(sentences)
        return sentence.strip()

    def load_stats(self):
        if os.path.exists("stats.json"):
            with open("stats.json","r") as f:
                data = json.load(f)
                self.best_wpm = data.get("best_wpm",0)
                self.best_accuracy = data.get("best_accuracy",0)

    def save_stats(self):
        if self.wpm > self.best_wpm:
            self.best_wpm = self.wpm
        if float(self.accuracy) > self.best_accuracy:
            self.best_accuracy = float(self.accuracy)
        with open("stats.json","w") as f:
            json.dump({
                "best_wpm": self.best_wpm,
                "best_accuracy": self.best_accuracy
            }, f)

    def show_results(self, screen):
        if(not self.end):
            self.total_time = time.time() - self.time_start
            count = 0
            for i,c in enumerate(self.word):
                try:
                    if self.input_text[i] == c:
                        count += 1
                except:
                    pass
            self.accuracy = count/len(self.word)*100
            self.wpm = len(self.input_text)*60/(5*self.total_time)
            self.end = True

            self.results = f"Time:{round(self.total_time)}s   Accuracy:{round(self.accuracy)}%   Wpm:{round(self.wpm)}"
            self.save_stats()

            self.draw_text(screen, self.results, 350, 28, self.RESULT_C)
            self.draw_text(screen, f"🏆 Best WPM: {round(self.best_wpm)}   Best Accuracy: {round(self.best_accuracy)}%", 400, 26, self.HEAD_C)
            pygame.display.update()

    def draw_sentence(self):
        # วาดประโยคพร้อม highlight
        x = 60
        y = 200
        font = pygame.font.Font(None, 32)
        for i, c in enumerate(self.word):
            if i < len(self.input_text):
                if self.input_text[i] == c:
                    color = self.GREEN
                else:
                    color = self.RED
            else:
                color = self.TEXT_C
            ch = font.render(c, True, color)
            self.screen.blit(ch, (x, y))
            x += ch.get_width()

    def run(self):
        self.reset_game()
        self.running=True
        while(self.running):
            clock = pygame.time.Clock()
            self.screen.fill((0,0,0), (50,250,650,50))
            pygame.draw.rect(self.screen,self.HEAD_C, (50,250,650,50), 2)

            self.draw_sentence()  # ✅ วาดประโยคแบบมีสี
            self.draw_text(self.screen, self.input_text, 274, 26,(250,250,250))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    x,y = pygame.mouse.get_pos()
                    if(x>=50 and x<=650 and y>=250 and y<=300):
                        self.active = True
                        self.input_text = ''
                        self.time_start = time.time() 
                    if(x>=310 and x<=510 and y>=390 and self.end):
                        self.reset_game()
                        
                elif event.type == pygame.KEYDOWN:
                    if self.active and not self.end:
                        if event.key == pygame.K_RETURN:
                            self.show_results(self.screen)
                            self.end = True
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            try:
                                self.input_text += event.unicode
                            except:
                                pass
            
            pygame.display.update()
            clock.tick(60)

    def reset_game(self):
        self.screen.blit(self.open_img, (0,0))
        pygame.display.update()
        time.sleep(1)
        
        self.reset=False
        self.end = False
        self.input_text=''
        self.word = self.get_sentence()
        self.time_start = 0
        self.total_time = 0
        self.wpm = 0

        self.screen.fill((0,0,0))
        self.screen.blit(self.bg,(0,0))
        msg = "Typing Speed Test"
        self.draw_text(self.screen, msg,80, 80,self.HEAD_C)  
        pygame.draw.rect(self.screen,(255,192,25), (50,250,650,50), 2)
        self.draw_sentence()
        pygame.display.update()


Game().run()
