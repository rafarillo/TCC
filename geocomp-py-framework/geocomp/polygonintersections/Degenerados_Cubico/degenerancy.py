import random as rng
from threading import local
from time import time
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Point
import geocomp.common.prim as primitive
import math
import time

from geocomp.config import COLOR_LINE

EPS = 10e-6
class LinkedList:
    def __init__(self, vertex):
        self.vertex = vertex
        self.next = self
        self.prev = self
        self.nextPoly = None
        self.intersect = False #Falso significa que o ponto é de saida
        self.entryExit = False
        self.neighbor = None
        self.alpha = 0.0
        self.crossing = "Bouncing"

    def insert(self, new):#insere o new na lista em tempo O(k), onde k é o numero de intersecções.
        #Insere o nó new entre a aresta representada pelos pontos self e p. Repare que a inserção é ordenada pelo atributo alpha
        # p nem sempre será self.next, poís podem haver várias intersecções numa mesma aresta 
        p = self
        while p.next.alpha < new.alpha and p.next.alpha != 0.0:
            p = p.next
        aux = p.next
        p.next = new
        new.prev = p
        new.next = aux
        if aux: aux.prev = new
        return new

    def calculateAlpha(self, A, B):
        #Presume-se que as arestas A e B se intersectam
        #Calcula o alpha do ponto de intersecção entre as arestas A e B
        vertex = CalculateIntersectPoint(A, B)
        colinear = False
        if vertex is None:
            # print("Acho que to calculando errado aqui")
            vertex = A.to
            d1 = (B.to - A.init).x * (A.to - A.init).x + (B.to - A.init).y * (A.to - A.init).y 
            d2 = primitive.dist2(A.init, A.to)
            alpha = d1/d2
            colinear = True
        else:
            d1 = prim.area2(B.init, B.to, A.init) 
            d2 = d1 - prim.area2(B.init, B.to, A.to)
            alpha = d1/d2
        return alpha, vertex, colinear       

    def create_intersect_node(self, alpha, vertex):
        #cria nó de intersecção e adiciona ele na lista
        id = vertex.hilight(color='white')
        # print(vertex)
        new = LinkedList(vertex)
        new.intersect = True
        new.alpha = alpha
        return self.insert(new), id

    def print_polygon(self):
        p = self
        while True:
            # print(p.vertex, p.alpha)
            p = p.next
            if p is self:
                break


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
    if D == 0.0:
        return None
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
        # while nextP1.intersect: nextP1 = nextP1.next
        nextP1 = p1.next
        A = Segment(p1.vertex, nextP1.vertex)
        idA = A.hilight(color_line='blue')
        nextP2 = p2.next
        while True:
            while nextP2.alpha != 0.0: nextP2 = nextP2.next
            # print("p2:",p2.vertex)
            # print("p2.next:",nextP2.vertex)
            B = Segment(p2.vertex, nextP2.vertex)
            idB = B.hilight(color_line='green')
            if A.intersects(B):
                alpha, vertex, colinear = p1.calculateAlpha(A,B)
                beta = p2.calculateAlpha(B,A)[0]
                # print("alpha = {} beta = {}".format(alpha, beta))
                if abs(p1.vertex.distance_to(vertex))<EPS or abs(p2.vertex.distance_to(vertex)) < EPS: # half open edge, fechado na extremidade p2.next e p1.next
                    pass
                elif alpha > EPS and alpha < 1.0-EPS and beta < 1.0-EPS and beta > EPS: #Caso X alpha > 0 e beta < 1
                    # print("A = {} B = {}".format(A, B))
                    # print("Caso X A = {} B = {}".format(alpha, beta))
                    if colinear:
                        new1, id1 = p1.create_intersect_node(alpha, nextP2.vertex)
                        new2, id2 = p2.create_intersect_node(beta, nextP1.vertex)
                        new1.neighbor = nextP2
                        nextP2.neighbor = new1
                        new2.neighbor = nextP1
                        nextP1.neighbor = new2
                        nextP2.intersect = nextP1.intersect = True
                        # print("colinear")
                    else:
                        new1, id1 = p1.create_intersect_node(alpha, vertex)
                        new2, id2 = p2.create_intersect_node(beta, vertex)                        
                        new1.neighbor = new2
                        new2.neighbor = new1

                    # nextP2 = new2.next
                    # nextP1 = new1.next
                elif (alpha > 1 - EPS and beta < 1 and beta > 0) or ((alpha < EPS or alpha >= 1) and beta > 0 and beta < 1): #Caso T, com alpha = 1 e 0 < beta < 1
                    # print("Caso T1 A = {} B = {}".format(alpha, beta))
                    new2, id2 = p2.create_intersect_node(beta, nextP1.vertex)
                    new2.neighbor = nextP1
                    nextP1.neighbor = new2
                    nextP1.intersect = True
                    # nextP2 = nextP2.next
                    # p2 = p2.next
                elif (beta > 1 - EPS and alpha < 1 and alpha > 0) or ((beta < EPS or beta >= 1) and alpha > 0 and alpha < 1): # Caso T, com beta = 1 e 0 < alpha < 1
                    # print("Caso T2 A = {} B = {}".format(alpha, beta))
                    new1, id1 = p1.create_intersect_node(alpha, nextP2.vertex)
                    new1.neighbor = nextP2
                    nextP2.neighbor = new1
                    nextP2.intersect = True
                    # nextP1 = nextP1.next
                    # p1 = p1.next
                elif alpha > 1-EPS and beta > 1-EPS: #Caso V com alpha = 1 e beta = 1
                    # print("Caso V A = {} B = {}".format(alpha, beta))
                    nextP1.neighbor = nextP2
                    nextP2.neighbor = nextP1
                    nextP1.intersect = nextP2.intersect = True
                    nextP1.vertex.hilight("white")
                intersect = True
            atualiza([idB])
            p2 = nextP2
            nextP2 = nextP2.next
            
            # if id1 != None: control.plot_delete(id1)          
            # if id2 != None: control.plot_delete(id2)          
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
    c = 0
    d = 0
    p = P

    while True:
        if p.vertex.x == p0.x and p.vertex.y == p0.y: 
            # print("Evend odd dentro")
            return True # ponto está no vértice
        q = p.prev
        testeC = (p.vertex.y > p0.y) != (q.vertex.y > p0.y) #Interpretação 1
        testeD = (p.vertex.y < p0.y) != (q.vertex.y < p0.y) #Interpretação 2
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
    q - nó
    p1 - nó
    p2 - nó
    p3 - nó
Output:
    retorna se q está a esquerda da cadeia (p1, p2, p3) ou a direita
'''

def leftChain(q, p1, p2, p3):
    s1 = prim.area2(p1.vertex, p2.vertex, q.vertex)
    s2 = prim.area2(p2.vertex, p3.vertex, q.vertex)
    s3 = prim.area2(p1.vertex, p2.vertex, p3.vertex)
    if s3 >= 0:
        if s1 > 0 and s2 > 0: return "Left"
        return "Right"
            
    if s1 > 0 or s2 > 0:
        return "Left"
    
    return "Right"

'''
Input:
    I - vértice de intersecção
Output:
    retorna se o nó I é intersecção de bouncing ou crossing
'''
def crossing(I):
    p_minus = I.prev
    p_plus = I.next
    q_minus = I.neighbor.prev
    q_plus = I.neighbor.next

    if leftChain(q_minus, p_minus, I, p_plus) == leftChain(q_plus, p_minus, I, p_plus):
        return "Bouncing"

    return "Crossing"

'''
Input:
    I - vértice

Output:
    Retorna True se I faz parte de alguma cadeia
'''

def chain(I): 
    if not I.intersect:
        return False
    p_plus = I.next
    p_minus = I.prev
    q_plus = I.neighbor.next
    q_minus = I.neighbor.prev

    return p_plus.neighbor == q_plus or p_plus.neighbor == q_minus or p_minus.neighbor == q_plus or p_minus.neighbor == q_minus

    
'''
Input:
    I - vértice de intersecção

Output:
    Retorna a posição local de I
'''

def localPosition(I): 
    p_plus = I.next
    p_minus = I.prev
    q_plus = I.neighbor.next
    q_minus = I.neighbor.prev

    l1 = leftChain(q_minus, p_minus, I, p_plus)
    l2 = leftChain(q_plus, p_minus, I, p_plus)

    if p_plus.neighbor == q_plus:
        if l1 == "Right":
            return "Left", "On"
        return "Right", "On"
    elif p_plus.neighbor == q_minus:
        if l2 == "Right":
            return "Left", "On"
        return "Right", "On"

    
    elif (p_plus.neighbor == q_plus and p_minus.neighbor == q_minus) or (p_plus.neighbor == q_minus and p_minus.neighbor == q_plus):
        return "On", "On"
    
    elif p_minus.neighbor == q_minus:
        if l2 == "Right":
            return "On", "Left"
        return "On", "Right"

    elif p_minus.neighbor == q_plus:
        if l1 == "Right":
            return "On", "Left"
        return "On", "Right"
    
    

'''
Input:
    P1 - lista circular duplamente ligada representando o polígono
    P2 - lista circular duplamente ligada representando o polígono

Output:
    Marca os vértices de intersecção das lista P1 e P2 como de entrada ou de saída
'''

def CrossingBouncing(P1, P2):
    p1 = P1
    idC = []
    while p1.intersect:
        p1 = p1.next
        if p1 is P1:
            break
    p1_aux = p1
    while True:
        id = p1.vertex.hilight('magenta')
        if p1.intersect:
            q = p1
            I = []
            while chain(q):
                idC.append(q.vertex.hilight('indigo'))
                I.append(q)
                q = q.next
            if len(I) < 1:
                q.crossing = q.neighbor.crossing= crossing(q)
                if q.crossing == "Crossing":
                    idC.append(q.vertex.hilight('gold'))
                else: 
                    idC.append(q.vertex.hilight('indigo'))
                p1 = q.next
            else:
                x = localPosition(I[0])
                y = localPosition(I[-1])
                # print(x)
                # print(y)
                if x != None and y != None and x[0] != y[1]: #delayed crossing
                    idC.append(I[0].vertex.hilight('gold'))
                    I[0].crossing = I[0].neighbor.crossing = "Crossing"
                p1 = q


        else: p1 = p1.next
        atualiza([id])
        if p1 is p1_aux:
            break
    for element in idC:
        control.plot_delete(element)
    
def ChalkCart(P1, P2, intersection):
    p1 = P1
    while p1.intersect:
        p1 = p1.next
        if p1 is P1:
            break
    p1_aux = p1
    isInside = EvenOdd(p1.vertex, P2)

    if not intersection:
        isInside = not isInside
        
    idC = []
    while True:
        id = p1.vertex.hilight('magenta')
        if p1.intersect:
            if p1.crossing == "Crossing":
                isInside = not isInside
            p1.entryExit = isInside
            if p1.entryExit: idC.append(p1.vertex.hilight(color='blue'))
            else: idC.append(p1.vertex.hilight(color='yellow'))

        atualiza([id])
        p1 = p1.next
        if p1 is p1_aux:
            break
    for element in idC:
        control.plot_delete(element)
    


'''
Input:
    P1 - lista circular duplamente ligada representando o polígono

Output:
    Não retorna nada. Marca as arestas que são a intersecção entre o poligono P1 e P2 
'''

def MarkSegments(P1, intersection):
    q = P1
    newPolygon = None

        

    while True:
        p = q
        while not ( p.intersect and p.crossing == "Crossing"): #procurando pela primeira intersecção que seja de crossing
            p = p.next
            if p is P1:
                break
        if p is P1 and not ( p.intersect and p.crossing == "Crossing"): 
            break
        oldPolygon = newPolygon
        newPolygon = LinkedList(p.vertex)
        newPolygon.nextPoly = oldPolygon
        poly = newPolygon
        start = p
        while True:
            # print('start = ', start.vertex)
            p.intersect = False
            # print('p =', p.vertex, p.intersect)
            if p.entryExit:
                while True:
                    p = p.next
                    id = p.vertex.hilight('magenta')
                    # print(p.entryExit, p.crossing)
                    new = LinkedList(p.vertex)
                    poly.insert(new)
                    Segment(poly.vertex, new.vertex).hilight(color_line='white')
                    atualiza([id])
                    poly = poly.next
                    if p.intersect and not (p.crossing == "Bouncing") or p is start or p is start.neighbor: 
                        # trocamos de lista apenas quando encontramos um vértice de crossing
                        # ou então chegamos no final do polígono que está em construção
                        p.intersect = False
                        break
            else:
                while True:
                    p = p.prev
                    id = p.vertex.hilight('magenta')
                    # print(p.entryExit, p.crossing)
                    new = LinkedList(p.vertex)
                    poly.insert(new)
                    Segment(poly.vertex, new.vertex).hilight(color_line='white')
                    atualiza([id])
                    poly = poly.next
                    if p.intersect and not (p.crossing == "Bouncing") or p is start or p is start.neighbor:
                        # trocamos de lista apenas quando encontramos um vértice de crossing
                        # ou então chegamos no final do polígono que está em construção
                        p.intersect = False
                        break
            p = p.neighbor
            if p is start: #terminamos o primeiro poligono
                q = p
                break
        newPolygon.nextPoly = oldPolygon
        
        if q is P1:
            break
    # Caso degenerado quando não há nenhum vértice de crossing

    if newPolygon is None:
        while True:
            p = p.next
            # p.vertex.hilight('magenta')
            atualiza()
            if p.intersect: break
        while p.next.intersect:
            Segment(p.vertex, p.next.vertex).hilight('white')
            p = p.next

    
    return newPolygon
        

def PolygonArea(l): #Inverte o polígono caso ele esteja no sentido horário
    # print('inverti')
    area = 0.0
    i = 0
    while i < len(l):
        area = area + prim.area2(l[i], l[(i+1)%len(l)], l[(i+2)%len(l)])
        i += 1
    if area < 0.0: l.reverse()

def DegenerancyIntersection(l):
    t0 = time.time()
    P1 = ArrayToList(l[0].pts, False)
    P2 = ArrayToList(l[1].pts, False)
    PolygonArea(l[0].to_list())
    PolygonArea(l[1].to_list())
    l[1].plot(color='peru')
    atualiza()
    intersect = Intersect(P1, P2)
    if intersect:
        l[0].plot(color='green')
        CrossingBouncing(P1, P2) 
        ChalkCart(P1, P2, True)
        l[0].hide()
        l[1].plot(color='green')
        ChalkCart(P2, P1, True)
        l[1].hide()
        polList = MarkSegments(P1, False)
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
    tf = time.time()
    print("Tempo: ", tf-t0)

def DegenerancyUnion(l):
    P1 = ArrayToList(l[0].pts, False)
    P2 = ArrayToList(l[1].pts, False)
    PolygonArea(l[0].to_list())
    PolygonArea(l[1].to_list())
    l[1].plot(color='peru')
    atualiza()
    intersect = Intersect(P1, P2)
    if intersect:
        l[0].plot(color='green') 
        CrossingBouncing(P1, P2) 
        ChalkCart(P1, P2, False)
        l[0].hide()
        l[1].plot(color='green')
        ChalkCart(P2, P1, False)
        l[1].hide()
        MarkSegments(P1, True)
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

def DegenerancyDifference(l):
    P1 = ArrayToList(l[0].pts, False)
    P2 = ArrayToList(l[1].pts, False)
    PolygonArea(l[0].to_list())
    PolygonArea(l[1].to_list())
    l[1].plot(color='peru')
    atualiza()
    intersect = Intersect(P1, P2)
    if intersect:
        l[0].plot(color='green') 
        CrossingBouncing(P1, P2) 
        ChalkCart(P1, P2, False)
        l[0].hide()
        l[1].plot(color='green')
        ChalkCart(P2, P1, True)
        l[1].hide()
        MarkSegments(P1, True)
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