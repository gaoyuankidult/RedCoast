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

from objects import *
from constants import RESOLUCION
from pygame.locals import KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN
from menus import actualizar_menu, dibujar_menu, extras, dibujar_menu2, actualizar_menu2

def main():
    ''' '''
    screen = pygame.display.set_mode(RESOLUCION)
    pygame.display.set_caption("PygameCross 0.0.5")
    
    reloj = pygame.time.Clock()
    color = (0, 0, 0)
    size = ''
    empezado = terminado = res = False
    loop = menu = menu2 = True
    longitud = 0
    linea = 0
    
    while loop:
        reloj.tick(50)
        screen.fill((255,233,165))
        
        if menu:
            dibujar_menu(screen)
        elif menu2:
            longitud = dibujar_menu2(screen, size)
        else:
            if not empezado:
                tablero = Tablero(int(size[0:2]), int(size[3:5]), linea, size) ##change change change
            if res:
                extras(screen)
                tablero.completar()
                color = (0, 153, 0)
                terminado = True
                
            empezado = True
            tablero.dibujar_tablero(screen, color)       
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                loop = False
            elif evento.type == KEYDOWN and evento.key == K_ESCAPE:
                loop = False
            elif evento.type == MOUSEBUTTONDOWN:
                if menu:
                    menu, size = actualizar_menu()
                elif menu2:
                    menu2, linea = actualizar_menu2(longitud)
                elif not terminado:
                    if tablero.actualizar():
                        res = tablero.analisis()
                elif terminado:
                    menu = menu2 = True
                    res = terminado = empezado = False
                    tablero.reset()
                    color = (0, 0, 0)
