from copyreg import constructor
from turtle import color
import random as rng
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Point
import geocomp.common.prim as primitive
import math

from geocomp.config import COLOR_LINE

class LinkedList:
    def __init__(self, vertex):
        self.vertex = vertex
        self.next = None
        self.prev = None
        self.nextPoly = None
        self.intersect = False #Falso significa que o ponto é de saida
        self.entryExit = False
        self.neighbor = False
        self.alpha = 0.0

    def insert(self, new):
        p = self
        while p.next and p.next.intersect:
            if p.next.alpha < new.alpha:
                p = p.next
            else:
                break
        aux = p.next
        p.next = new
        new.prev = p
        new.next = aux
        if aux: aux.prev = new
        return new       

    def create_intersect_node(self, A, B):
        vertex = CalculateIntersectPoint(A, B)
        id = vertex.hilight(color='white')
        new = LinkedList(vertex)
        new.intersect = True
        d1 = primitive.dist2(A.init, A.to)
        d2 = primitive.dist2(A.init, new.vertex)
        new.alpha = d2/d1
        return self.insert(new), id

'''
Recebe uma lista de ligada de polígonos e devolve uma outra lista circular duplamente ligada, mas com outros atributos
'''

def ArrayToList(P, pertubate):
    x = 0.0
    y = 0.0
    if pertubate:
        theta = rng.uniform(0, 2*math.pi)
        x = 0.001*math.cos(theta)
        y = 0.001*math.sin(theta)
    first = LinkedList(P + Point(x, y))
    p = P.next
    q = first
    while p is not P:
        new = LinkedList(p + Point(x, y))
        q.next = new
        new.prev = q
        q = new
        p = p.next
    q.next = first
    first.prev = q
    return first

'''
Input: 
    A - Segmento
    B - Segmento

Output:
    Devolve o par (x,y) onde ocorre a intersecção entre os segmentos A e B
'''

def CalculateIntersectPoint(A, B):
    p1 = A.init
    p2 = A.to
    p3 = B.init
    p4 = B.to

    D = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
    x = ((p1.x * p2.y - p1.y * p2.x) * (p3.x - p4.x) - (p1.x - p2.x) * (p3.x * p4.y - p3.y * p4.x))/D 
    y = ((p1.x * p2.y - p1.y * p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x * p4.y - p3.y * p4.x))/D 

    return Point(x, y)

'''
Input:
    P1 - lista circular duplamente ligada representando o polígono
    P2 - lista circular duplamente ligada representando o polígono


Output:
    Devolve true se há alguma intersecção entre P1 e P2. Além disso, insere os pontos de intersecção nas listas de P1 e P2 conforme o algoritmo de Greiner
'''

def Intersect(P1, P2):
    p1 = P1
    intersect = False
    id1 = id2 = None
    while True:
        p2 = P2
        nextP1 = p1.next
        A = Segment(p1.vertex, nextP1.vertex)
        idA = A.hilight(color_line='blue')
        while True:
            nextP2 = p2.next
            while nextP2.intersect: nextP2 = nextP2.next 
            B = Segment(p2.vertex, nextP2.vertex)
            idB = B.hilight(color_line='green')
            if A.intersects(B):
                new1, id1 = p1.create_intersect_node(A, B)
                new2, id2 = p2.create_intersect_node(B, A)
                new1.neighbor = new2
                new2.neighbor = new1
                intersect = True
            control.freeze_update ()
            control.thaw_update() 
            control.update()
            control.sleep()
            control.plot_delete(idB)
            if id1 != None: control.plot_delete(id1)          
            if id2 != None: control.plot_delete(id2)          
            p2 = nextP2
            if p2 is P2: break
        control.plot_delete(idA)
        p1 = nextP1
        if p1 is P1: break
    return intersect

'''
Input:
    P1 - lista circular duplamente ligada representando o polígono
    P2 - lista circular duplamente ligada representando o polígono

Output:
    Devolve P1 se P1 está contido em P2, devolve P2 se P2 está contido em P1 e retorna None se os poligonos são disjuntos
'''

def Inside(P1, P2):
    dp1 = EvenOdd(P1.vertex, P2)
    if dp1: return P1 #poligono P1 é o interno
    dp2 = EvenOdd(P2.vertex, P1)
    if dp2: return P2 #poligono P2 é o interno
    
    return None #Poligonos são disjuntos

'''
Input:
    p0 - ponto no plano
    P - poligono

output: retorna True se p0 está dentro de P
'''

def EvenOdd(p0, P):
    # p = P
    # q = P.prev
    # c = False
    # while True:
    #     if(p0.x == p.vertex.x and p0.y == p.vertex.y): # ponto está no vertice
    #         return True
    #     if (p.vertex.y > p0.y) != (q.vertex.y > p0.y):
    #         slope = (p0.x - p.vertex.x) * (q.vertex.y - p.vertex.y) - (q.vertex.x - p.vertex.x) * (p0.y - p.vertex.y)
    #         if slope == 0:
    #             return True
    #         if (slope < 0) != (q.vertex.y < p.vertex.y):
    #             c = not c 
    #     q = p
    #     p = p.next
    #     if p is P: break
    
    # if c: return c    
    
    # while True:
    #     if(p0.x == p.vertex.x and p0.y == p.vertex.y): # ponto está no vertice
    #         return True
    #     if (p.vertex.y < p0.y) != (q.vertex.y < p0.y):
    #         slope = (p0.x - p.vertex.x) * (q.vertex.y - p.vertex.y) - (q.vertex.x - p.vertex.x) * (p0.y - p.vertex.y)
    #         if slope == 0:
    #             return True
    #         if (slope < 0) != (q.vertex.y < p.vertex.y):
    #             c = not c 
    #     q = p
    #     p = p.next
    #     if p is P: break

    c = 0
    d = 0
    p = P

    while True:
        if p.vertex.x == p0.x and p.vertex.y == p0.y: return True # ponto está no vértice
        q = p.prev
        testeC = (p.vertex.y > p0.y) != (q.vertex.y > p0.y)
        testeD = (p.vertex.y < p0.y) != (q.vertex.y < p0.y)
        if testeC or testeD:
            x = (p0.y * p.vertex.x - p0.y * q.vertex.x - q.vertex.y * p.vertex.x + p.vertex.y * q.vertex.x)/(p.vertex.y - q.vertex.y)
            if testeC and x > p0.x: c += 1
            if testeD and x < p0.x: d += 1
        p = p.next
        if p is P:
            break
    if c%2 != d%2:
        return True
    if c%2 == 1:
        return True
    else:
        return False
'''
Input:
    P1 - lista circular duplamente ligada representando o polígono
    P2 - lista circular duplamente ligada representando o polígono

Output:
    Não retorna nada, no entanto marca os vértices de intersecção das lista P1 e P2 como de entrada ou de saída
'''

def ChalkCart(P1, P2, intersection):
    p1 = P1
    isInside = EvenOdd(p1.vertex, P2)
    if not intersection:
        isInside = not isInside
    idC = []
    while True:
        id = p1.vertex.hilight(color='white')
        if p1.intersect:
            p1.entryExit = not isInside            
            if p1.entryExit: idC.append(p1.vertex.hilight(color='blue'))
            else: idC.append(p1.vertex.hilight(color='yellow'))
            isInside = not isInside
        control.freeze_update ()
        control.thaw_update() 
        control.update()
        control.sleep()
        control.plot_delete(id)
        p1 = p1.next
        if p1 is P1: break
    for element in idC:
        control.plot_delete(element)

'''
Input:
    P1 - lista circular duplamente ligada representando o polígono

Output:
    Não retorna nada. Marca as arestas que são a intersecção entre o poligono P1 e P2 
'''

def MarkSegments(P1):
    q = P1
    while True:
        p = q
        while not p.intersect:
            p = p.next
            if p is P1:
                break
        
        if p is P1:
            break
        newPolygon = LinkedList(p.vertex)
        poly = newPolygon
        start = p
        while True:
            p.intersect = False
            if p.entryExit:
                while True:
                    p = p.next
                    new = LinkedList(p.vertex)
                    poly.insert(new)
                    Segment(poly.vertex, new.vertex).hilight(color_line='white')
                    poly = poly.next
                    if p.intersect:
                        p.intersect = False
                        break
            else:
                while True:
                    p = p.prev
                    new = LinkedList(p.vertex)
                    poly.insert(new)
                    Segment(poly.vertex, new.vertex).hilight(color_line='white')
                    poly = poly.next
                    if p.intersect:
                        p.intersect = False
                        break
            control.freeze_update ()
            control.thaw_update() 
            control.update()
            control.sleep()
            p = p.neighbor
            if p is start: #terminamos o primeiro poligono
                q = p
                break
        
        if q is P1:
            break
        

    

def GreinerIntersection(l):
    P1 = ArrayToList(l[0].pts, True)
    P2 = ArrayToList(l[1].pts, False)
    intersect = Intersect(P1, P2)
    if intersect:
        l[0].plot(color='green') 
        ChalkCart(P1, P2, True)
        l[0].hide()
        l[1].plot(color='green')
        ChalkCart(P2, P1, True)
        l[1].hide()
        MarkSegments(P2)
        l[0].hide()
        l[1].hide()
    else:
        Pres = Inside(P1, P2)
        if Pres:
            p = Pres
            while True:
                A = Segment(p.vertex, p.next.vertex)
                A.hilight(color_line='white')
                p = p.next
                if p is Pres: break

def GreinerUnion(l):
    P1 = ArrayToList(l[0].pts, True)
    P2 = ArrayToList(l[1].pts, False)
    intersect = Intersect(P1, P2)
    if intersect:
        l[0].plot(color='green') 
        ChalkCart(P1, P2, False)
        l[0].hide()
        l[1].plot(color='green')
        ChalkCart(P2, P1, False)
        l[1].hide()
        MarkSegments(P2)
        l[0].hide()
        l[1].hide()
    else: 
        Pres = Inside(P1, P2)
        Pres = P2 if Pres == P1 else P1
        if Pres:
            p = Pres
            while True:
                A = Segment(p.vertex, p.next.vertex)
                A.hilight(color_line='white')
                p = p.next
                if p is Pres: break

def GreinerDifference(l):
    P1 = ArrayToList(l[0].pts, True)
    P2 = ArrayToList(l[1].pts, False)
    intersect = Intersect(P1, P2)
    if intersect:
        l[0].plot(color='green') 
        ChalkCart(P1, P2, True)
        l[0].hide()
        l[1].plot(color='green')
        ChalkCart(P2, P1, False)
        l[1].hide()
        MarkSegments(P2)
        l[0].hide()
        l[1].hide()
    else:
        Pres = Inside(P1, P2)
        if Pres:
            p = Pres
            while True:
                A = Segment(p.vertex, p.next.vertex)
                A.hilight(color_line='white')
                p = p.next
                if p is Pres: break