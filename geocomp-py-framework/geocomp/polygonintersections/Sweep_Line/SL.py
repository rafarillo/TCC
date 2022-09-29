
import random as rng
from urllib.request import CacheFTPHandler
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

EPS = 10e-6

def atualiza(delete=None):
    control.freeze_update ()
    control.thaw_update() 
    control.update()
    control.sleep()
    if delete:
        for element in delete:
            control.plot_delete(element)

def compare(i, j):
    if abs(i.point.x-j.point.x) < EPS:
        return i.point.y - j.point.y
    return i.point.x - j.point.x

def compareBST(event, root):
    # if abs(root.otherEvent.point.x - root.point.x) < EPS:
    #     y = root.point.y
    # else:
    #     m = (root.otherEvent.point.y - root.point.y)/(root.otherEvent.point.x - root.point.x)
    #     y = m * (event.point.x - root.point.x) + root.point.y
    # Point(event.point.x, y).hilight('red')
    if abs(event.point.y - root.point.y) < EPS: #os nós tem mesma coordenada y
        if root == event: return 0 #os nós de fato são iguais
        return 1 #não são iguais

    elif event.point.y - root.point.y < 0: #subarvore a esquerda
        return 1
    
    elif event.point.y - root.point.y > 0: #subarvore a direita
        return -1



class SweepEvent:
    #Os paramentros são a coordenada, se é o extremo esquerdo da aresta, proximo evento da aresta, se é subj ou clip, o poligono a qual pertencia, e o segmento a qual pertencia  
    def __init__(self, point, left, otherEvent, polType, pol, segment):
        self.point = point
        self.left = left
        self.otherEvent = otherEvent
        self.polType = polType
        self.pol = pol
        self.segment = segment
        self.inOut = None
        self.otherInOut = None
        self.inResult = None
        self.prevInResult = None
    
    def __lt__(self, other):
        return compare(self, other) < 0

class AVL:
    def __init__(self, data, left=None, right=None, draw_id=None) -> None:
        self.data = data
        self.height = 1
        self.left = left
        self.right = right
        self.draw_id = draw_id  

def CreateQeue(l):
    i = 0
    subject = True
    Q = []
    event2 = None
    Nvertex = 0
    for polygon in l:
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
    
    Q = sorted(Q, key=functools.cmp_to_key(compare))
    q = PriorityQueue()
    print("Fila inicial")
    for element in Q:
        if element.left == None:
            element.left = True
            element.otherEvent.left = False
        print(element.pol, element.segment, end=' ', sep='')
        q.put(element)
    print()
    for element in Q:
        print(element.left, end=' ')
    print()
    # i = 0
    # while i < Nvertex:
    #     print(Q[i], Q[i].otherEvent, sep='->')
    #     i += 1

    return q


def avlHeight(root):
    if root == None: return 0
    return root.height

def balance(root):
    if root == None: return 0

    return avlHeight(root.left) - avlHeight(root.right)

def rotateLeft(root):
    new_root = root.right
    root.right = new_root.left
    new_root.left = root

    root.height = 1 + max(avlHeight(root.left), avlHeight(root.right))
    new_root.height = 1 + max(avlHeight(new_root.left), avlHeight(new_root.right))

    return new_root

def rotateRight(root):
    new_root = root.left
    root.left = new_root.right
    new_root.right = root

    root.height = 1 + max(avlHeight(root.left), avlHeight(root.right))
    new_root.height = 1 + max(avlHeight(new_root.left), avlHeight(new_root.right))


    return new_root

def insertNode(root, event):

    if root == None:
        return AVL(event)

    cmp = compareBST(event,root.data)
    if cmp == 1:
        root.left = insertNode(root.left, event)
    
    elif cmp == -1:
        root.right = insertNode(root.right, event)
    
    if cmp == 0: print("Igual mentira isso kkkkkkk"); return

    root.height = 1 + max(avlHeight(root.left), avlHeight(root.right))
    bal = balance(root)

    if bal > 1:
        cmp = compareBST(event, root.left.data)
        if cmp == 0: print("Igual mentira isso kkkkkkk"); return
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
    
def deleteNode(root, event):

    if root == None:
        return root
    
    cmp = compareBST(event, root.data)
    if cmp == 1:
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
        while p.left: p = p.left #minimo da subarvore a direita
        root.data = p.data
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

def printAVL(root):
    if root != None:
        printAVL(root.left)
        # root.id = Segment(root.data.point, root.data.otherEvent.point).hilight('magenta')
        # root.data.draw_id = Segment(root.data.point, root.data.otherEvent)
        print(root.data.segment, root.data.pol)
        printAVL(root.right)

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
                    findPredSuc.preOther = p
                p = p.right
            findPredSuc.pre = p
            # print('pre p.pol=', p.data.pol)

        #minimo da subárvore direita é o sucessor 
        if root.right != None:
            p = root.right
            while p.left: 
                if p.data.pol != event.pol:
                    findPredSuc.sucOther = p
                p = p.left
            findPredSuc.suc = p
            # print('suc p.pol=', p.data.pol)

        return
    
    if cmp == 1:
        findPredSuc.suc = root
        if root.data.pol != event.pol:
            findPredSuc.sucOther = root
        findPredSuc(root.left, event)
    
    else:
        findPredSuc.pre = root
        if root.data.pol != event.pol:
            findPredSuc.preOther = root
        findPredSuc(root.right, event)

def setInformation(event, pre):
    pass

def calculateIntersectPoint(A, B):
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

def possibleInter(curr, other, Q):
    if not other or not curr: return
    A = Segment(curr.point, curr.otherEvent.point)
    B = Segment(other.point, other.otherEvent.point)

    if A.intersects(B):
        p = calculateIntersectPoint(A, B)
        p.hilight('magenta')
        I1 = SweepEvent(p, False, curr, curr.polType, curr.pol, curr.segment)
        I2 = SweepEvent(p, True, other, other.polType, other.pol, other.segment)

        curr.otherEvent = I1
        other.otherEvent = I2

        Q.put(I1)
        Q.put(I2)


def Intersection(l):
    # print(l[0].vertices()[0])
    Q = CreateQeue(l)
    S = None
    while not Q.empty():
        event = Q.get()
        findPredSuc.pre = None
        findPredSuc.suc = None
        findPredSuc.preOther = None
        findPredSuc.sucOther = None
        id1 = None
        id2 = None
        idE = Segment(event.point, event.otherEvent.point).hilight('white')
        if event.left:
            print('left')
            print('Inserindo ', event.segment, event.pol)
            S = insertNode(S, event)
            findPredSuc(S, event)
            pre = findPredSuc.preOther
            suc = findPredSuc.sucOther
            print(pre, suc)
            if pre:
                pre = pre.data
                print('pre = ', pre.segment, ' ', pre.pol)
                id1 = Segment(pre.point, pre.otherEvent.point).hilight('yellow')
            if suc:
                suc = suc.data
                print('suc = ', suc.segment, ' ', suc.pol)
                id2 = Segment(suc.point, suc.otherEvent.point).hilight('green')
            
            possibleInter(event, suc, Q)
            possibleInter(event, pre, Q)
            
    
        else:
            print('right')
            print('Deletando ', event.otherEvent.segment, event.otherEvent.pol)
            findPredSuc(S, event)
            pre = findPredSuc.preOther
            suc = findPredSuc.sucOther
            print(pre, suc)

            if pre:
                pre = pre.data
                print('pre = ', pre.segment, ' ', pre.pol)
                id1 = Segment(pre.point, pre.otherEvent.point).hilight('yellow')

            if suc:
                suc = suc.data
                print('suc = ', suc.segment, ' ', suc.pol)
                id2 = Segment(suc.point, suc.otherEvent.point).hilight('green')


            S = deleteNode(S, event.otherEvent)
            possibleInter(pre, suc, Q)

        
        printAVL(S)
        print('--------------------------------')
        id = control.plot_vert_line(event.point.x, 'blue', 2)
        pid = event.point.hilight('white')
        atualiza([id, pid, id1, id2, idE])
    printAVL(S)

