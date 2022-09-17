# -*- coding: utf-8 -*-
"""Algoritmos para o problema de operações booleanas em poligonos:

Dado dois poligonos encontrar a união, intersecção e diferença

Algoritmos disponveis:
- SweepLine
"""
from . import SL

children = [
	[ 'SL', 'Intersection', 'Intersecção' ]
    
    ]

__all__ = [a[0] for a in children]
