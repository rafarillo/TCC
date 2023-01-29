from gettext import find
from sqlite3 import PrepareProtocol
from urllib.request import CacheFTPHandler

from numpy import insert
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Point
import geocomp.common.prim as primitive
import math
import time
from queue import PriorityQueue, Queue
import functools
import random as rng
import time

EPS = 10e-6
n_intersection = 0

def atualiza(delete=None):
    control.freeze_update ()
    control.thaw_update() 
    control.update()
    control.sleep()
    if delete:
        for element in delete:
            control.plot_delete(element)

def compareSweepEvent(i, j):
    if i.point.x != j.point.x:
        return i.point.x - j.point.x
    # return i.point.y - j.point.y
    if i.point.y != j.point.y:
        return i.point.y - j.point.y
    
    # os pontos são coincidentes

    if i.left != j.left: #coincidente mas, um é left e o outro não
        if i.left: return 1
        return -1
    
    if below(i, j.otherEvent): #coincidentes, desempata pelo outro ponto
        return -1
    return 1


def below(i, j):
    if i.left:
        return prim.left(i.point, i.otherEvent.point, j.point)
    return prim.left(i.otherEvent.point, i.point, j.point)

def above(i, j):
    return not below(i, j)

def compareBST(event, root):
    if event == root: return 0 #0 é igual, 1 é subarvore esquerda e -1 é subarvore direita
    
    if not prim.collinear(event.point, event.otherEvent.point, root.point) or \
    not prim.collinear(event.point, event.otherEvent.point, root.otherEvent.point): #se nao for colinear
        if event.point == root.point: #pontos iguais
            # x = 1 if below(event, root.otherEvent) else -1
            return 1 if below(event, root.otherEvent) else -1
        #pontos distintos
        if compareSweepEvent(event, root) > 0:
            # x = 1 if above(root, event) else -1
            return 1 if above(root, event) else -1
        return 1 if below(event, root) else -1

    if event.point == root.point: #os segmentos são colineares, vamos usar um criterio consistente 
        d1 = prim.dist2(event.point, event.otherEvent.point)
        d2 = prim.dist2(root.point, root.otherEvent.point)
        if d1 != d2:
            return 1 if d1 < d2 else -1
        return 1 if event.pol < root.pol else -1
        # return 1 if event.point < root.point else -1
    return 1 if compareSweepEvent(event, root) > 0 else -1        



        




class SweepEvent:
    #Os paramentros são a coordenada, se é o extremo esquerdo da aresta, proximo evento da aresta, se é subj ou clip, o poligono a qual pertencia, e o segmento a qual pertencia  
    def __init__(self, point, left, otherEvent, polType, pol, segment):
        self.point = point
        self.left = left
        self.otherEvent = otherEvent
        self.polType = polType
        self.pol = pol
        self.segment = segment
        self.crossOther = 0
        self.crossSelf = 0   
        self.inside = False 
    def __lt__(self, other):
        return compareSweepEvent(self, other) < 0

    def __repr__(self) -> str:
        return '{} {} {} {} {} crossO={} crossS={}|'.format(self.segment, self.otherEvent.segment, self.pol, self.point, self.otherEvent.point, self.crossOther, self.crossSelf) + str(id(self))[-5:-1]

class AVL:
    def __init__(self, data, left=None, right=None, draw_id=None) -> None:
        self.data = data
        self.height = 1
        self.left = left
        self.right = right
        self.draw_id = draw_id  

# pre-processamento para criar a fila de prioridade
def CreateQeue(l):
    i = 0
    subject = True
    Q = []
    event2 = None
    Nvertex = 0
    for polygon in l:
        R = rng.randint(0, 255)
        G = rng.randint(0, 255)
        B = rng.randint(0, 255)
        polygon.hilight('#%02x%02x%02x' % (R, G, B))
        j = 0
        vertices = polygon.vertices()
        n = len(vertices)
        while j < n:
            event1 = SweepEvent(vertices[j], None, None, subject, i, j)
            j += 1
            event2 = SweepEvent(vertices[j%n], None, event1, subject, i, j%n)
            event1.otherEvent = event2
            Q.append(event1)
            Q.append(event2)
        subject = False
        Nvertex += n
        i += 1
    
    Q = sorted(Q, key=functools.cmp_to_key(compareSweepEvent))
    q = PriorityQueue()
    for element in Q:
        if element.left == None:
            element.left = True
            element.otherEvent.left = False
        q.put(element)
 

    return q

# calcula a altura da arvore AVL
def avlHeight(root):
    if root == None: return 0
    return root.height

# verifica a diferença entre a altura da subárvore a esquerda e a direita
def balance(root):
    if root == None: return 0

    return avlHeight(root.left) - avlHeight(root.right)

# operador para rotacionar a árvore para esquerda
def rotateLeft(root):
    new_root = root.right
    root.right = new_root.left
    new_root.left = root

    root.height = 1 + max(avlHeight(root.left), avlHeight(root.right))
    new_root.height = 1 + max(avlHeight(new_root.left), avlHeight(new_root.right))

    # precisamos agora acertar o campo crossSelf e crossOther
    if new_root.data.pol == root.data.pol:
        new_root.data.crossOther += root.data.crossOther
        new_root.data.crossSelf += root.data.crossSelf + 1
    else:
        new_root.data.crossOther += root.data.crossSelf + 1
        new_root.data.crossSelf += root.data.crossOther


    return new_root

# operador para rotacionar a árvore para direita
def rotateRight(root):
    new_root = root.left
    root.left = new_root.right
    new_root.right = root

    root.height = 1 + max(avlHeight(root.left), avlHeight(root.right))
    new_root.height = 1 + max(avlHeight(new_root.left), avlHeight(new_root.right))

    #agora precisamos acertar o campo crossSelf e crossOther
    if root.left:
        if root.data.pol == new_root.data.pol:
            root.data.crossSelf -= (new_root.data.crossSelf + 1)
            root.data.crossOther -= new_root.data.crossOther
        else:
            root.data.crossSelf -= new_root.data.crossOther
            root.data.crossOther -= (new_root.data.crossSelf + 1)

    else:
        root.data.crossSelf = root.data.crossOther = 0
        

    return new_root

# insere o evento event na raíz da árvore root
def insertNode(root, event):

    if root == None:
        new = AVL(event)

        return new

    cmp = compareBST(event,root.data)
    
    if cmp == 1:
        if event.pol != root.data.pol:
            root.data.crossOther += 1
        else:
            if event.point != root.data.point:
                root.data.crossSelf += 1
        root.left = insertNode(root.left, event)

    elif cmp == -1:
        root.right = insertNode(root.right, event)
    

    root.height = 1 + max(avlHeight(root.left), avlHeight(root.right))
    bal = balance(root)

    if bal > 1:
        cmp = compareBST(event, root.left.data)
        if cmp == 1:
            return rotateRight(root)
        elif cmp == -1:
            root.left = rotateLeft(root.left)
            return rotateRight(root)
        
    if bal < -1:
        cmp = compareBST(event, root.right.data)
        if cmp == -1:
            return rotateLeft(root)
        elif cmp == 1:
            root.right = rotateRight(root.right)
            return rotateLeft(root)
    
    return root

# deleta o evento event da árvore root    
def deleteNode(root, event):

    if root == None:
        return root
    
    cmp = compareBST(event, root.data)
    if cmp == 1:
        if event.pol != root.data.pol and root.data.crossOther > 0:
            root.data.crossOther -= 1
        elif event.pol == root.data.pol and root.data.crossSelf > 0:
            root.data.crossSelf -= 1
        root.left = deleteNode(root.left, event)
    elif cmp == -1:
        root.right = deleteNode(root.right, event)
    
    else:
        if root.left == None: #sem subarvore a esquerda
            r = root.right
            root = None
            return r
        elif root.right == None: #sem subarvore a direita
            l = root.left
            root = None
            return l
        p = root.right
        while p.left: #minimo da subarvore a direita
            if p.left.data.pol != p.data.pol:
                p.data.crossOther -= 1
            else:
                p.data.crossSelf -= 1
            p = p.left
        if root.data.pol != p.data.pol:
            cs = root.data.crossSelf
            co = root.data.crossOther
            root.data = p.data
            root.data.crossSelf = co
            root.data.crossOther = cs
        else:
            cs = root.data.crossSelf
            co = root.data.crossOther
            root.data = p.data
            root.data.crossSelf = cs
            root.data.crossOther = co
        root.right = deleteNode(root.right, p.data)
    
    if root == None:
        return root

    root.height = 1 + max(avlHeight(root.left), avlHeight(root.right))
    bal = balance(root)

    if bal > 1:
        if balance(root.left) >= 0:
            return rotateRight(root)
        else:
            root.left = rotateLeft(root.left)
            return rotateRight(root)
    
    if bal < -1:
        if balance(root.right) <= 0:
            return rotateLeft(root)
        else:
            root.right = rotateRight(root.right)
            return rotateLeft(root)
    return root   

# printa a AVL 
def printAVL(root):
    if root != None:
        printAVL(root.left)
        print(root.data)
        printAVL(root.right)

# encontra o predecessor e o sucessor de event na árvore root
def findPredSuc(root, event):
    if root == None:
        return 
    cmp = compareBST(event, root.data)
    if cmp == 0:
        #maximo da subarvore esquerda é o predecessor
        if root.left != None:
            p = root.left
            while p.right: 
                if p.data.pol != event.pol:
                    # findPredSuc.preOther = p
                    findPredSuc.cross += (p.data.crossSelf + 1)
                else:
                    findPredSuc.cross += p.data.crossOther
                p = p.right
            
            if p.data.pol != event.pol:
                # findPredSuc.preOther = p
                findPredSuc.cross += (p.data.crossSelf + 1)

            findPredSuc.pre = p

        #minimo da subárvore direita é o sucessor 
        if root.right != None:
            p = root.right
            while p.left: 
                if p.data.pol != event.pol:
                    findPredSuc.sucOther = p
                p = p.left
                
            if p.data.pol != event.pol:
                findPredSuc.sucOther = p
            findPredSuc.suc = p
        return 
    
    # o sucessor é o pai de algum nó
    if cmp == 1:
        findPredSuc.suc = root
        findPredSuc(root.left, event)
    # o predecessor é o pai de algum nó
    else:
        findPredSuc.pre = root
        if root.data.pol != event.pol:
            findPredSuc.cross += (root.data.crossSelf + 1)
        else:
            findPredSuc.cross += root.data.crossOther 
        findPredSuc(root.right, event)
    
    
# calcula o ponto de interseção entre os segmentos A e B
def calculateIntersectPoint(A, B):
    p1 = A.init
    p2 = A.to
    p3 = B.init
    p4 = B.to

    D = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
    if D == 0.0:
        return A.to
    x = ((p1.x * p2.y - p1.y * p2.x) * (p3.x - p4.x) - (p1.x - p2.x) * (p3.x * p4.y - p3.y * p4.x))/D 
    y = ((p1.x * p2.y - p1.y * p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x * p4.y - p3.y * p4.x))/D 

    return Point(x, y)

# divide o segmento seg em dois, sendo p um extremo desse segmento e Q a fila de evento 
def divideSegment(p, seg, Q):
    left = SweepEvent(p, True, seg.otherEvent, seg.polType, seg.pol, 'I' + str(n_intersection))
    right = SweepEvent(p, False, seg, seg.polType, seg.pol, 'I' + str(n_intersection))

    seg.otherEvent.otherEvent = left
    seg.otherEvent = right

    Q.put(left)
    Q.put(right)

# verifica se os eventos curr e other se intersectam, se se intersectam então insere na fila Q
def possibleInter(curr, other, Q):
    if not other or not curr: return
    A = Segment(curr.point, curr.otherEvent.point)
    B = Segment(other.point, other.otherEvent.point)
    inter = A.intersects(B)
    # se os eventos se intersectam impropriamente retorne
    if inter and (curr.point == other.point or curr.otherEvent.point == other.otherEvent.point \
    or curr.otherEvent.point == other.point or curr.point == other.otherEvent.point):
        return
    if inter:
        global n_intersection
        n_intersection += 1
        p = calculateIntersectPoint(A, B)
        p.hilight('magenta')

        divideSegment(p, curr, Q)
        divideSegment(p, other, Q)

# verifica se o evento está dentro ou fora do outro polígono
def setInformation(pre, event, cross):
    if pre == None:
        event.inside = False
        return
    if pre.pol != event.pol:
        if cross%2 == 1:
            event.inside = True
    else:
        event.inside = pre.inside



def Intersection(l):
    t0 = time.time()
    global n_intersection
    n_intersection = 0
    Q = CreateQeue(l)
    S = None
    res = []
    while not Q.empty():
        event = Q.get()
        findPredSuc.pre = None
        findPredSuc.suc = None
        findPredSuc.cross = 0
        id1 = None
        id2 = None
        id11 = None
        idE = Segment(event.point, event.otherEvent.point).hilight('white')
        if event.left:
            # print('Inserindo ', event)
            S = insertNode(S, event)
            
            findPredSuc(S, event)
            pre = findPredSuc.pre
            suc = findPredSuc.suc
            cross = findPredSuc.cross
            
            if pre:
                pre = pre.data
                # print('pre = ', pre, 'cross = ', cross)
                # pres = findPredSuc.pre.data
                # id11 = Segment(pres.point, pres.otherEvent.point).hilight('orange')
                id1 = Segment(pre.point, pre.otherEvent.point).hilight('yellow')
            if suc:
                suc = suc.data
                # print('suc = ', suc, 'cross = ', cross)
                id2 = Segment(suc.point, suc.otherEvent.point).hilight('green')
            
            setInformation(pre, event, cross)
            # inside = setInformation(pre, cross)
            
            if event.inside:
                # print(event.segment, event.otherEvent.segment, "is inside")
                res.append(event)
            possibleInter(event, suc, Q)
            possibleInter(event, pre, Q)

    
        else:
            # print('Deletando ', event.otherEvent)            
            

            findPredSuc(S, event)
            
            pre = findPredSuc.pre
            suc = findPredSuc.suc
            if pre:
                pre = pre.data
                # print('pre = ', pre)
                id1 = Segment(pre.point, pre.otherEvent.point).hilight('yellow')

            if suc:
                suc = suc.data
                # print('suc = ', suc)
                id2 = Segment(suc.point, suc.otherEvent.point).hilight('green')


            S = deleteNode(S, event.otherEvent)
            possibleInter(pre, suc, Q)

        # if S: print('r = ', S.data)
        # printAVL(S)
        # print('--------------------------------')
        id = control.plot_vert_line(event.point.x, 'blue', 2)
        pid = event.point.hilight('white')
        atualiza([pid, id1, id2, idE, id11, id])
    # printAVL(S)
    for i in res:
        Segment(i.point, i.otherEvent.point).hilight('blue')
        atualiza([])
    tf = time.time()
    print("Tempo: ", tf-t0)    
