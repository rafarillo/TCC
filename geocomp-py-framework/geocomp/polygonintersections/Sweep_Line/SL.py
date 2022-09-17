
import random as rng
from urllib.request import CacheFTPHandler
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Point
import geocomp.common.prim as primitive
import math
import time
from queue import Queue
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

class SweepEvent:
    #Os paramentros são a coordenada, se é o extremo esquerdo da aresta, proximo evento da aresta, se é subj ou clip, o poligono a qual pertencia, e o segmento a qual pertencia  
    def __init__(self, point, left, otherEvent, polType, pol, segment):
        self.point = point
        self.left = left
        self.otherEvent = otherEvent
        self.polType = polType
        self.pol = pol
        self.segment = segment
    
    def __lt__(self, other):
        return compare(self, other)

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
    q = Queue()
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

    return q, Nvertex

class Treap:
    def __init__(self, data, priority, left=None, right=None, draw_id=None) -> None:
        self.data = data
        self.priority = rng.randrange(priority)
        self.left = left
        self.right = right
        self.draw_id = draw_id    

def rotateLeft(root):
    new_root = root.right
    root.right = new_root.left
    new_root.left = root

    return new_root

def rotateRight(root):
    new_root = root.left
    root.left = new_root.right
    new_root.right = root

    return new_root

def insertNode(root, event, N):

    if root == None:
        return Treap(event, N)
    # print(compare(event, root.data))
    if compare(event, root.data):
        root.left = insertNode(root.left, event, N)

        if root.left and root.left.priority > root.priority:
            root = rotateRight(root)
    
    else:
        root.right = insertNode(root.right, event, N)

        if root.right and root.right.priority > root.priority:
            root = rotateLeft(root)
    
    return root

def findNode(root, event):
    if root == None:
        return False
    
    if root == event:
        return root
    
    if compare(event, root.data):
        return findNode(root.left, event)
    
    return findNode(root.right, event)

def deleteNode(root, event):
    if root == None:
        return None
    # print('Root = ',root.data, 'Event', event, event == root.data)
    if root.data == event:
        if root.left == None and root.right == None: #apenas a raiz
            # print('Cai aqui')
            # atualiza([root.id])
            root = None
        
        elif root.left and root.right: #raiz com dois filhos

            if root.left.priority < root.right.priority:
                root = rotateLeft(root)
                root.left = deleteNode(root.left, event)
            else:
                root = rotateRight(root)
                root.right = deleteNode(root.right, event)
        
        else: #raiz com um filho
            c = root.left if (root.left) else root.right
            # atualiza([root.id])
            root = c
        
        return root

    if compare(event, root.data):
        root.left = deleteNode(root.left, event)
    
    else:
        root.right = deleteNode(root.right, event)
    
    return root

def printTreap(root):
    if root != None:
        printTreap(root.left)
        # root.id = Segment(root.data.point, root.data.otherEvent.point).hilight('magenta')
        root.data.draw_id = Segment(root.data.point, root.data.otherEven)
        print(root.data)
        printTreap(root.right)

def findPredSuc(root, event):
    if root == None:
        return
    
    if root.data == event:
        
        #maximo da subarvore esquerda é o predecessor
        if root.left != None:
            p = root.left
            while p.right: p = p.right
            findPredSuc.pre = p

        #minimo da subárvore direita é o sucessor 
        if root.right != None:
            p = root.right
            while p.left: p = p.left
            findPredSuc.suc = p
        
        return
    
    if compare(event, root.data):
        findPredSuc.suc = root
        findPredSuc(root.left, event)
    
    else:
        findPredSuc.pre = root
        findPredSuc(root.right, event)

def Intersection(l):
    # print(l[0].vertices()[0])
    Q, N = CreateQeue(l)
    S = None
    while not Q.empty():
        event = Q.get()
        findPredSuc.pre = None
        findPredSuc.suc = None
        id1 = None
        id2 = None
        idE = Segment(event.point, event.otherEvent.point).hilight('white')
        if event.left:
            print('Inserindo', event)
            S = insertNode(S, event, 2*N)
            findPredSuc(S, event)
            pre = findPredSuc.pre
            suc = findPredSuc.suc
            if pre:
                pre = pre.data
                id1 = Segment(pre.point, pre.otherEvent.point).hilight('yellow')
            if suc:
                suc = suc.data
                id2 = Segment(suc.point, suc.otherEvent.point).hilight('green')
            
    
        else:
            print('Deletando', event.otherEvent)
            S = deleteNode(S, event.otherEvent)
        
        printTreap(S)
        print('--------------------------------')
        id = control.plot_vert_line(event.point.x, 'blue', 2)
        pid = event.point.hilight('white')
        atualiza([id, pid, id1, id2, idE])