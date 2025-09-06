import pygame
import time
from tkinter import *
from tkinter import messagebox

pygame.init()
screen = pygame.display.set_mode((850, 150))
pygame.display.set_caption("Virus")
icon = pygame.image.load("images.png")
pygame.display.set_icon(icon)
font = pygame.font.SysFont("Lucida Console", 20)
label = font.render("YOU DOWNLOADED VIRUS", 1, (12,140,0,1))
screen.fill("black")
screen.blit(label, (50, 50))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            time.sleep(0.5)
            screen = pygame.display.set_mode((850, 150))
            screen.blit(label, (50, 50))
            pygame.display.update()
            pygame.display.set_icon(icon)
            messagebox.showerror("Error", "Encrypting your files")

    screen.blit(label, (50, 50))
    pygame.display.update()