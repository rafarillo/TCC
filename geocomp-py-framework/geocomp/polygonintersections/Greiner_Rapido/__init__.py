# -*- coding: utf-8 -*-
"""Algoritmos para o problema de operações booleanas em poligonos:

Dado dois poligonos encontrar a união, intersecção e diferença

Algoritmos disponveis:
- Greiner
"""
from . import greiner_rapido

children = [
	[ 'greiner_rapido', 'GreinerIntersection', 'Greiner Intersecção' ],
	[ 'greiner_rapido', 'GreinerUnion', 'Greiner União'],
	[ 'greiner_rapido', 'GreinerDifference', 'Greiner Diferença']
	
]

__all__ = [a[0] for a in children]
