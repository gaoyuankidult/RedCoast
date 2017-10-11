###############################################################################
## PygameCross
##
## Copyright (C) 2010 Jorge Zilbermann ealdorj@gmail.com
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###############################################################################

import pygame
import os

def dibujar_menu(screen):
    fuente = pygame.font.Font(None, 40)
    fuente2 = pygame.font.Font(None, 25)
    
    fuente.set_underline(True)
    
    screen.blit(fuente.render("PygameCross 0.0.5", True, (0, 0, 0)), (10, 10))
    screen.blit(fuente2.render("- Select the size:", True, (0, 0, 0)), (10, 70))
    
    screen.blit(fuente2.render("7x7", True, (0, 0, 0)), (90, 110))
    pygame.draw.rect(screen, (0, 0, 0), (50, 110, 20, 20), 2)
    screen.blit(fuente2.render("8x8", True, (0, 0, 0)), (90, 140))
    pygame.draw.rect(screen, (0, 0, 0), (50, 140, 20, 20), 2)
    screen.blit(fuente2.render("10x10", True, (0, 0, 0)), (90, 170))
    pygame.draw.rect(screen, (0, 0, 0), (50, 170, 20, 20), 2)
    #screen.blit(fuente2.render("15x15", True, (0, 0, 0)), (90, 200))
    #pygame.draw.rect(screen, (0, 0, 0), (50, 200, 20, 20), 2)
    #screen.blit(fuente2.render("20x20", True, (0, 0, 0)), (90, 230))
    #pygame.draw.rect(screen, (0, 0, 0), (50, 230, 20, 20), 2)
    
    screen.blit(fuente2.render("- Instructions:", True, (0, 0, 0)), (10, 280))
    screen.blit(fuente2.render("Left-Click", True, (0, 0, 0)), (90, 320))
    screen.blit(fuente2.render("Right-Click", True, (0, 0, 0)), (90, 350))
    
    cuadrado = pygame.image.load(os.path.join("nonogram/images", "relleno.png")).convert_alpha()
    cruz = pygame.image.load(os.path.join("nonogram/images", "equis.png")).convert_alpha()
    
    screen.blit(cuadrado, (50, 320))
    screen.blit(cruz, (50, 350))
    
    screen.blit(fuente2.render("- Credits:", True, (0, 0, 0)), (10, 400))
    screen.blit(
        fuente2.render("Created by Alex Yuan Gao (gaoyuankidult@gmail.com) and Ealdor (ealdorj@gmail.com)", True, (0, 0, 0)), (50, 440))
    screen.blit(fuente2.render("Puzzles taken from www.griddler.co.uk", True, (0, 0, 0)), (50, 470))

def actualizar_menu():
    res = ''
    boton = pygame.mouse.get_pressed()
    menu = True
    x, y = pygame.mouse.get_pos()
    
    if boton[0] and x >= 50 and x <= 70 and y >= 230 and y <= 250:
        res += '20x20.txt'
        menu = False
    if boton[0] and x >= 50 and x <= 70 and y >= 200 and y <= 220:
        res += '15x15.txt'
        menu = False
    if boton[0] and x >= 50 and x <= 70 and y >= 170 and y <= 190:
        res += '10x10.txt'
        menu = False
    if boton[0] and x >= 50 and x <= 70 and y >= 140 and y <= 160:
        res += '08x08.txt'
        menu = False
    if boton[0] and x >= 50 and x <= 70 and y >= 110 and y <= 130:
        res += '07x07.txt'
        menu = False
    
    return menu, res

def dibujar_menu2(screen, size):
    fuente = pygame.font.Font(None, 25)
    aux = False
    titulo = ''
    titulos = []
        
    archivo = open(os.path.join('nonogram/size', size))
    for line in archivo:
        for e in line:
            if e != ":" and not aux:
                titulo = titulo + e
            if e == ":":
                aux = True
        titulos.append(titulo)
        titulo = ''
        aux = False
    archivo.close()
    
    screen.blit(fuente.render("- Select the game:", True, (0, 0, 0)), (10, 10))
    
    plus = 50
    for i in titulos:
        pygame.draw.rect(screen, (0, 0, 0), (50, plus, 20, 20), 2)
        screen.blit(fuente.render(i, True, (0, 0, 0)), (90, plus))
        plus += 30
    
    return titulos.__len__()

def actualizar_menu2(longitud):
    linea = 0
    boton = pygame.mouse.get_pressed()
    menu2 = True
    x, y = pygame.mouse.get_pos()
    lista = []
    aux = 50
    
    for i in xrange(longitud):
        lista.append(aux)
        aux += 30
    if boton[0] and x >= 50 and x <= 70 and y >= 50 and y <= 40 + longitud * 30:
        for j in xrange(20):
            if lista.__contains__(y-j):
                return False, y-j
    
    return menu2, linea

def extras(screen):
    fuente = pygame.font.Font(None, 25)
    screen.blit(fuente.render("Well done, press any button to", True, (0, 153, 0)), (10, 70))
    screen.blit(fuente.render("return to the main menu :)", True, (0, 153, 0)), (10, 100))
