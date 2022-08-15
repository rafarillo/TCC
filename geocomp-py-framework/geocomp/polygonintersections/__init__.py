# -*- coding: utf-8 -*-
"""Algoritmos para o problema de operações booleanas em poligonos:

Dado dois poligonos encontrar a união, intersecção e diferença

Algoritmos disponveis:
- Greiner
- Degenerados
"""

from . import Degenerados_Cubico
from . import Greiner_Cubico
from . import Greiner_Rapido
# from . import lineintersections
# from . import polygonintersections
# from .common.guicontrol import init_display
# from .common.guicontrol import plot_input
# from .common.guicontrol import run_algorithm
# from .common.prim import get_count
# from .common.prim import reset_count

children = (   ( 'Degenerados_Cubico',  None, 'Casos degenerados' ),
               ( 'Greiner_Cubico',  None, 'Greiner Vanilla' ),
               ( 'Greiner_Rapido', None, 'Greiner Rapido')

	)

__all__ = [p[0] for p in children]
