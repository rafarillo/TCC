# -*- coding: utf-8 -*-
"""Algoritmos para o problema de operações booleanas em poligonos:

Dado dois poligonos encontrar a união, intersecção e diferença

Algoritmos disponveis:
- Greiner
"""
from . import degenerancy

children = [
	[ 'degenerancy', 'DegenerancyIntersection', 'Degenerancy Intersecção' ],
	[ 'degenerancy', 'DegenerancyUnion', 'Degenerancy União'],
	[ 'degenerancy', 'DegenerancyDifference', 'Degenerancy Diferença']
]

__all__ = [a[0] for a in children]
