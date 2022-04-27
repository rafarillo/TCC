from copyreg import constructor
from turtle import color
from geocomp.common.segment import Segment
from geocomp.common import control
from geocomp.common.guiprim import *
from geocomp.common.point import Point
import geocomp.common.prim as primitive
import math

class LinkedList:
    def __init__(self, vertex):
        self.vertex = vertex
        self.next = None
        self.prev = None
        self.nextPoly = None
        self.intersect = False
        self.entryExit = False
        self.neighbor = False
        self.alpha = 1.0

    def insert(self, new):
        if self.next is None:
            self.next = new
            new.prev = self
        else:
            p = self
            while p is not None and p.next.alpha < new.alpha:
                p = p.next
            aux = p.next
            p.next = new
            new.prev = p
            new.next = aux
            aux.prev = new

    def create_intersect_node(self, A, B):
        vertex = CalculateIntersectPoint(A, B)
        vertex.hilight(color='white')
        new = LinkedList(vertex)
        new.intersect = True
        d1 = primitive.dist2(A.init, A.to)
        d2 = primitive.dist2(A.init, new.vertex)
        new.alpha = d2/d1
        self.insert(new)

def ArrayToList(P):
    first = LinkedList(P)
    p = P.next
    q = first
    while p is not P:
        new = LinkedList(p)
        q.next = new
        new.prev = q
        q = new
        p = p.next
    return first

def CalculateIntersectPoint(A, B):
    p1 = A.init
    p2 = A.to
    p3 = B.init
    p4 = B.to

    D = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
    x = ((p1.x * p2.y - p1.y * p2.x) * (p3.x - p4.x) - (p1.x - p2.x) * (p3.x * p4.y - p3.y * p4.x))/D 
    y = ((p1.x * p2.y - p1.y * p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x * p4.y - p3.y * p4.x))/D 

    return Point(x, y)


def Intersect(P1, P2):
    p1 = P1
    intersect = False

    while p1 is not None:
        p2 = P2
        if p1.next is not None: A = Segment(p1.vertex, p1.next.vertex)
        else: A = Segment(p1.vertex, P1.vertex) #corner case
        A.hilight(color_line='blue')
        while not p1.intersect and p2 is not None:
            if p2.next is not None: B = Segment(p2.vertex, p2.next.vertex) 
            else: B = Segment(p2.vertex, P2.vertex) #corner case
            B.hilight(color_line='green')
            if not p2.intersect and A.intersects(B):
                p1.create_intersect_node(A, B)
                p2.create_intersect_node(B, A)
                p1.next.neighbor = p2.next
                p2.next.neighbor = p1.next
            control.freeze_update ()
            control.thaw_update() 
            control.update()
            control.sleep()
            B.hilight(color_line='red')
            p2 = p2.next
        A.hilight(color_line='red')
        p1 = p1.next



def Greiner(l):
    P1 = ArrayToList(l[0].pts)
    P2 = ArrayToList(l[1].pts)
    Intersect(P1, P2)
    #Teste para verificar a ordem dos ponto
    p1 = P1
    while p1 is not None:
        p1.vertex.hilight(color='white')
        print('vertice = ', p1.vertex, 'alpha = ', p1.alpha)
        control.freeze_update ()
        control.thaw_update() 
        control.update()
        control.sleep()
        p1.vertex.hilight(color='red')
        p1 = p1.next
