# -*- coding: utf-8 -*-
"""Algoritmos para o problema de operações booleanas em poligonos:

Dado dois poligonos encontrar a união, intersecção e diferença

Algoritmos disponveis:
- Greiner
"""
from . import greiner

children = [
	[ 'greiner', 'GreinerIntersection', 'Greiner Intersecção' ],
	[ 'greiner', 'GreinerUnion', 'Greiner União'],
	[ 'greiner', 'GreinerDifference', 'Greiner Diferença'],
]

__all__ = [a[0] for a in children]
