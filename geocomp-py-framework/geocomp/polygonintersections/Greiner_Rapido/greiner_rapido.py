import random as rng
from urllib.request import CacheFTPHandler
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Edge, Point
import geocomp.common.prim as primitive
import math

from geocomp.config import COLOR_LINE

VertexP = [] #lista de vertices, cada elemento é um nó da lista ligada
VertexQ = [] #lista de vertices, cada elemento é um nó da lista ligada

class LinkedList:
    def __init__(self, vertex):
        self.vertex = vertex
        self.next = self
        self.prev = self
        self.nextPoly = None
        self.intersect = False #Falso significa que o ponto é de saida
        self.entryExit = False
        self.neighbor = False
        self.alpha = 0.0

    def vertices(self): #Retorna uma lista de vertices
        p = self
        v = []
        while True:
            v.append(p)
            p = p.next
            if p is self: break
        return v

    def insert(self, new): #insere em O(1)
        new.next = self.next
        new.prev = self
        self.next = new
        new.next.prev = new

        return new       

    def create_intersect_node(self, A, alpha): #Cria nó de intersecção
        vertex = CalculateIntersectPoint(A, alpha)
        # id = vertex.hilight(color='white')
        new = LinkedList(vertex)
        new.intersect = True
        new.alpha = alpha
        return self.insert(new)

    def print_polygon(self):
        p = self
        while True:
            print(p.vertex)
            p = p.next
            if p is self:
                break


'''
Atualiza a interface gráfica 
'''

def atualiza(delete=None):
    control.freeze_update ()
    control.thaw_update() 
    control.update()
    control.sleep()
    if delete:
        for element in delete:
            control.plot_delete(element)
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
    alpha - posição relativa no segmento A

Output:
    Devolve o par (x,y) onde ocorre alpha
'''


def CalculateIntersectPoint(A, alpha):
    x = (1 - alpha) * (A.init.x - A.to.x) + A.to.x
    y = (1 - alpha) * (A.init.y - A.to.y) + A.to.y
    return Point(x, y)

'''
A - Segmento
B - Segmento
Calcula a posição relativa da intersecção entre A e B
'''

def CalculateAlpha(A, B):
    d1 = prim.area2(B.init, B.to, A.init) 
    d2 = d1 - prim.area2(B.init, B.to, A.to)
    return d1/d2

'''
P1 - polígono 
P2 - polígono

Encontra todas as intersecções entre P1 e P2
'''
def FindAllIntersections(P1, P2):# Consumo de tempo tamanho de P1 vezes otamanho de P2
    intersect = False
    alphasP = []
    p1 = P1
    i = 0
    while True:
        A = Segment(p1.vertex, p1.next.vertex)
        idA = A.hilight("blue")
        j = 0
        p2 = P2
        while True:
            B = Segment(p2.vertex, p2.next.vertex)
            idB = B.hilight("green")
            if A.intersects(B):
                intersect = True
                alpha = CalculateAlpha(A, B)
                beta = CalculateAlpha(B, A)
                CalculateIntersectPoint(A, alpha).hilight('white')
                alphasP.append([alpha, beta, i, j])
            atualiza([idB])
            j += 1
            p2 = p2.next
            if p2 is P2: break
        control.plot_delete(idA)
        p1 = p1.next
        i += 1
        if p1 is P1: break
    return alphasP, intersect


'''
Input:
    P1 - lista circular duplamente ligada representando o polígono
    P2 - lista circular duplamente ligada representando o polígono


Output:
    Devolve true se há alguma intersecção entre P1 e P2. Além disso, insere os pontos de intersecção nas listas de P1 e P2
'''

def Intersect(P1, P2):
    alphasP, intersect = FindAllIntersections(P1, P2)
    if not intersect: return False
    alphasP = sorted(alphasP, key=lambda l: l[0], reverse=True)
    print(alphasP)
    for element in alphasP:
        curr_edge = Segment(VertexP[element[2]].vertex, VertexP[(element[2]+1)%len(VertexP)].vertex) 
        element[2] = VertexP[element[2]].create_intersect_node(curr_edge, element[0])

    alphasP = sorted(alphasP, key=lambda l: l[1], reverse=True)
    print(alphasP)
    for element in alphasP:
        curr_edge = Segment(VertexQ[element[3]].vertex, VertexQ[(element[3]+1)%len(VertexQ)].vertex)
        new = VertexQ[element[3]].create_intersect_node(curr_edge, element[1])
        new.neighbor = element[2]
        element[2].neighbor = new    

    
    return True

'''
Input:
    P1 - polígono
    P2 - polígono

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
    Marca os vértices de intersecção das lista P1 e P2 como de entrada ou de saída e altera alguns atributos das listas P1 e P2
'''

def ChalkCart(P1, P2, intersection):
    p1 = P1
    isInside = EvenOdd(p1.vertex, P2)
    if not intersection:
        isInside = not isInside
    idC = []
    while True:
        id = p1.vertex.hilight(color='magenta')
        if p1.intersect:
            p1.entryExit = not isInside            
            if p1.entryExit: idC.append(p1.vertex.hilight(color='blue'))
            else: idC.append(p1.vertex.hilight(color='yellow'))
            isInside = not isInside
        atualiza([id])
        p1 = p1.next
        if p1 is P1: break
    for element in idC:
        control.plot_delete(element)

'''
Input:
    P1 - lista circular duplamente ligada representando o polígono

Output:
    Marca as arestas que são a intersecção entre o poligono P1 e P2 
'''

def MarkSegments(P1):
    q = P1
    newPolygon = None
    while True:
        p = q
        while not p.intersect:
            p = p.next
            if p is P1:
                break
        
        if p is P1:
            break
        oldPolygon = newPolygon
        newPolygon = LinkedList(p.vertex)
        newPolygon.nextPoly = oldPolygon
        poly = newPolygon
        start = p
        while True:
            p.intersect = False
            if p.entryExit:
                while True:
                    p = p.next
                    new = LinkedList(p.vertex)
                    poly.next = new
                    Segment(poly.vertex, new.vertex).hilight(color_line='white')
                    poly = poly.next
                    if p.intersect:
                        p.intersect = False
                        break
            else:
                while True:
                    p = p.prev
                    new = LinkedList(p.vertex)
                    poly.next = new
                    Segment(poly.vertex, new.vertex).hilight(color_line='white')
                    poly = poly.next
                    if p.intersect:
                        p.intersect = False
                        break
            atualiza()
            p = p.neighbor
            if p is start: #terminamos o primeiro poligono
                q = p
                break
        
        newPolygon.nextPoly = oldPolygon
        if q is P1:
            break
    return newPolygon
        

    

def GreinerIntersection(l):
    P1 = ArrayToList(l[0].pts, True)
    P2 = ArrayToList(l[1].pts, False)
    global VertexP
    global VertexQ
    VertexP = P1.vertices()
    VertexQ = P2.vertices()
    l[1].plot(color='peru')
    atualiza()
    intersect = Intersect(P1, P2)
    if intersect:
        l[0].plot(color='green') 
        ChalkCart(P1, P2, True)
        l[0].hide()
        l[1].plot(color='green')
        ChalkCart(P2, P1, True)
        l[1].hide()
        polList = MarkSegments(P1)
        p = polList
        while p is not None:
            # p.print_polygon()
            p = p.nextPoly
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
    global VertexP
    global VertexQ
    VertexP = P1.vertices()
    VertexQ = P2.vertices()
    l[1].plot(color='peru')
    atualiza()
    intersect = Intersect(P1, P2)
    if intersect:
        l[0].plot(color='green') 
        ChalkCart(P1, P2, False)
        l[0].hide()
        l[1].plot(color='green')
        ChalkCart(P2, P1, False)
        l[1].hide()
        MarkSegments(P1)
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
    global VertexP
    global VertexQ
    VertexP = P1.vertices()
    VertexQ = P2.vertices()
    l[1].plot(color='peru')
    atualiza()
    intersect = Intersect(P1, P2)
    if intersect:
        l[0].plot(color='green') 
        ChalkCart(P1, P2, True)
        l[0].hide()
        l[1].plot(color='green')
        ChalkCart(P2, P1, False)
        l[1].hide()
        MarkSegments(P1)
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