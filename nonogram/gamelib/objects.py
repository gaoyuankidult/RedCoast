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

import os
import sys
import zmq
sys.path.insert(0, "..")

from constants import *
from pygame.locals import *
import pygame

import copy

class Tablero:
    ''' '''
    def __init__(self, num_fil, num_col, linea, archivo):
        ''' '''
        self.sol = []
        self.conf = []
        lista = []
        cadena = ''
        abre = aux = False
        self.titulo = ''
        count = 50

        print linea
        self.archivo = open(os.path.join('nonogram/size', archivo))
        for line in self.archivo:
            self.conf.append(line)
            if count == linea:
                for e in line:
                    if e == "[":
                        abre = True
                    if e == "]":
                        for i in cadena.split(","):
                            lista.append(int(i))
                        self.sol.append(lista)
                        lista = []
                        abre = False
                        cadena = ''
                    if abre and e != "[":
                        cadena = cadena + e
                    if e != ":" and not aux:
                        self.titulo = self.titulo + e
                    if e == ":":
                        aux = True
            count += 30
        self.archivo.close()
        
        # modify the original code here
        # if the random 
        # self.archivo = open(os.path.join('nonogram/size', archivo))
        # num_line = 
        # for line in self.archivo:
        #     self.conf.append(line)
        #     if count == linea:
        #         for e in line:
        #             if e == "[":
        #                 abre = True
        #             if e == "]":
        #                 for i in cadena.split(","):
        #                     lista.append(int(i))
        #                 self.sol.append(lista)
        #                 lista = []
        #                 abre = False
        #                 cadena = ''
        #             if abre and e != "[":
        #                 cadena = cadena + e
        #             if e != ":" and not aux:
        #                 self.titulo = self.titulo + e
        #             if e == ":":
        #                 aux = True
        #     count += 30



        self.celdas = self.crear_celdas(num_fil, num_col, VACIO)
        self.tipos = self.agregar_tipos()
        self.columnas = num_col
        self.filas = num_fil
        
        self.fuente = pygame.font.Font(None, 25)
        
        uno = False
        sum = 0
        list = []
        self.listoflists = []
        for i in xrange(self.filas):
            for j in xrange(self.columnas):
                if self.sol[i][j] == 1:
                    uno = True
                    if uno:
                        sum += 1
                if self.sol[i][j] == 0:
                    if uno:
                        list.append(sum)
                    uno = False
                    sum = 0
                    list.append(sum)
                if uno and j == self.columnas-1:
                    list.append(sum) 
            self.listoflists.append(list)
            uno = False
            sum = 0
            list = []
            
        uno = False
        sum = 0
        list = []
        self.listoflists2 = []
        for i in xrange(self.columnas):
            for j in xrange(self.filas):
                if self.sol[j][i] == 1:
                    uno = True
                    if uno:
                        sum += 1
                if self.sol[j][i] == 0:
                    if uno:
                        list.append(sum)
                    uno = False
                    sum = 0
                    list.append(sum)
                if uno and j == self.filas-1:
                    list.append(sum) 
            self.listoflists2.append(list)
            uno = False
            sum = 0
            list = []


        print self.listoflists
        print self.listoflists2
        # communication method
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:%s" % "5556")
        self.communicate = True

        if self.communicate:
            # send size information

            self.socket.send("%d, %d" %(num_fil,num_col))
            print self.socket.recv()

            # send game configurations
            self.socket.send_json([self.listoflists, self.listoflists2])  # row columns information
            print self.socket.recv()

        #solver.read_board()

    def check_and_confirm(self, message):
        """
        This methods comfirm information received from nonogram process.
        :param message: message thats needs to be received from nonogram
        :param func:  function that needs to be excuted before comformation
        :return: true
        """
        received = self.socket.recv()
        if message == received:
            self.socket.send(message + "_confirmed")
        else:
            raise Exception("The process expects to receive message %s, however, message: %s is received." % (message, received))
        return True

    def check_confirm(self, message):
        """
        This methods comfirm information received from nonogram process.
        :param message: message thats needs to be received from nonogram
        :param func:  function that needs to be excuted before comformation
        :return: true
        """
        received = self.socket.recv()
        if message+"_confirmed" == received:
            pass
        else:
            raise Exception("The process expects to receive message %s, however, message: %s is received." %
                            (message + "_confirmed", received))
        return True

    def reset(self):
        ''' '''
        self.celdas = self.crear_celdas(self.filas, self.columnas, VACIO)
        
    def completar(self):
        ''' '''
        for i in xrange(self.filas):
            for j in xrange(self.columnas):
                if self.celdas[i][j] == VACIO:
                    self.celdas[i][j] = EQUIS
                
    def crear_celdas(self, num_fil, num_col, tipo):
        ''' '''
        celdas = []
        for i in xrange(num_fil):
            celdas.append([tipo for i in xrange(num_col)])
        return celdas
    
    def agregar_tipos(self):
        ''' '''
        tipos = []
        tipos.append(Tipo(os.path.join("nonogram/images", "relleno.png")))
        tipos.append(Tipo(os.path.join("nonogram/images", "equis.png")))
        return tipos
    
    def dibujar_tablero(self, surface, color):
        ''' '''
        tamano = self.tipos[0].get_width()
        
        for i in xrange(len(self.celdas) + 1):
            pygame.draw.line(surface, (0, 0, 0), (ANCHO / 2 - 20, i * tamano + ALTO / 2 - 120), (self.columnas * tamano + ANCHO / 2 - 20, i * tamano + ALTO / 2 - 120), 2)
        for i in xrange(len(self.celdas[0]) + 1):
            pygame.draw.line(surface, (0, 0, 0), (i * tamano + ANCHO / 2 - 20, ALTO / 2 - 120), (i * tamano + ANCHO / 2 - 20, self.filas * tamano + ALTO / 2 - 120), 2)
        
        x = y = 0
        for fila in self.celdas:
            for ele in fila:
                if ele != VACIO:
                    self.tipos[ele - 1].drawn(surface, x + 2, y + 2)
                x += tamano
            x = 0
            y += tamano  
        
        aux, aux2 = 0, 140
        for i in range(self.columnas):
            for j in self.listoflists2[i].__reversed__():
                if j > 9:
                    surface.blit(self.fuente.render(str(j), True, color), (ANCHO / 2 - 20 + aux, ALTO / 2 - aux2))
                else:
                    surface.blit(self.fuente.render(str(j).replace("0", "  "), True, color), (ANCHO / 2 - 15 + aux, ALTO / 2 - aux2))
                aux2 += 20
                if j == 0:
                    aux2 -=20
            aux2 = 140
            aux += 20 
        
        aux, aux2 = 0, 40
        for i in xrange(self.filas):
            for j in self.listoflists[i].__reversed__():
                if j > 9:
                    surface.blit(self.fuente.render(str(j), True, color), (ANCHO / 2 - aux2 - 5, ALTO / 2 + 1 + aux - 120))
                else:
                    surface.blit(self.fuente.render(str(j).replace("0", "  "), True, color), (ANCHO / 2 - aux2, ALTO / 2 + 1 + aux - 120))
                aux2 += 20
                if j == 0:
                    aux2 -=20
            aux2 = 40
            aux += 20
        
        posx, posy = pygame.mouse.get_pos()
        if posx > ANCHO / 2 - 20 and posx < self.columnas * tamano + ANCHO / 2 -20 and posy > ALTO / 2 - 120 and posy < i * tamano + ALTO / 2 - 100:
            pygame.draw.line(surface, (238, 0, 255), (ANCHO / 2 - 20, posy), (posx, posy), 2)     
            pygame.draw.line(surface, (238, 0, 255), (posx, ALTO / 2 - 120), (posx, posy), 2)
        
        surface.blit(self.fuente.render("Size: " + str(self.filas) + " x " + str(self.columnas), True, (0, 0, 0)), (10, 10))
        surface.blit(self.fuente.render("Title: " + self.titulo, True, (0, 0, 0)), (10, 40))
        
    def actualizar(self):
        ''' '''
        boton = pygame.mouse.get_pressed()
        positionx = positiony = -1
        actualizar = False

        previous_board = copy.deepcopy(self.celdas)

        if boton[0] or boton[2]:
            x, y = pygame.mouse.get_pos() 
            positionx = (x / self.tipos[0].get_width()) - 19
            positiony = (y / self.tipos[0].get_width()) - 9


            if (positionx < self.columnas and positionx >= 0) and (positiony < self.filas and positiony >= 0):
                if self.celdas[positiony][positionx] == RELLENO or self.celdas[positiony][positionx] == EQUIS:
                    self.celdas[positiony][positionx] = VACIO
                else:
                    if boton[0]:
                        self.celdas[positiony][positionx] = RELLENO
                    if boton[2]:
                        self.celdas[positiony][positionx] = EQUIS
                actualizar = True
            else:
                positionx = positiony = -1

            # send information to robot.
            if (positionx < self.columnas and positionx >= 0) and (positiony < self.filas and positiony >= 0): # if the position is not out of boundary
                if self.celdas[positiony][positionx] == RELLENO or self.celdas[positiony][positionx] == EQUIS: # after selection, if the position is filled in with block or cross
                    if boton[0]:
                        click = 0
                    if boton[2]:
                        click = 1
                else:
                    if boton[0]:
                        click = 0
                    if boton[2]:
                        click = 1

                # send current board of the game
                self.socket.send_json([self.sol, self.celdas, previous_board])
                print self.socket.recv()

                # send position and click information
                self.socket.send_json([positiony, positionx, click])
                print self.socket.recv()


        return actualizar

    def analisis(self):
        ''' '''        
        res = True
        
        for i in xrange(self.filas):
            for j in xrange(self.columnas):
                if (self.sol[i][j] == self.celdas[i][j] or self.sol[i][j] + 2 == self.celdas[i][j]) and res:
                    res = True

                else:
                    res = False
        if res == True:
            self.socket.send("game_finished")
            print self.socket.recv()
        return res
    
class Tipo:
    ''' '''
    def __init__(self, imagen):
        ''' '''
        self.imagen = pygame.image.load(imagen).convert_alpha()
        
    def get_width(self):
        ''' '''
        return self.imagen.get_width()
    
    def drawn(self, surface, x, y):
        ''' '''
        surface.blit(pygame.transform.scale(self.imagen, (18, 18)), (x + ANCHO / 2 - 20, y + ALTO / 2 - 120))
