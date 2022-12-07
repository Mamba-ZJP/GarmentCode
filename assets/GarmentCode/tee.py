from pathlib import Path
from datetime import datetime
from copy import deepcopy
from scipy.spatial.transform import Rotation as R

# Custom
import pypattern as pyp
from customconfig import Properties


class SleevePanel(pyp.Panel):
    """Simple panel for a sleeve"""

    def __init__(self, name, length=35, arm_width=30, ease=3) -> None:
        super().__init__(name)

        width = (arm_width + ease) / 2 
        self.edges = pyp.ops.simple_loop([0, width], [length, width], [length - 7, 0])

        # default placement
        self.translate_by([-length - 20, 15, 0])

        self.interfaces = [
            pyp.InterfaceInstance(self, self.edges[1]),
            pyp.InterfaceInstance(self, self.edges[2]),
            pyp.InterfaceInstance(self, self.edges[3]),
        ]

class TorsoPanel(pyp.Panel):
    """Panel for the front of upper garments"""

    def __init__(self, name, length=50, neck_w=15, sholder_w=40, c_depth=15, ease=3) -> None:
        super().__init__(name)

        width = sholder_w + ease
        sholder_top_l = (width - neck_w) / 2 
        self.edges = pyp.ops.simple_loop(
            [0, length], 
            [sholder_top_l, length], 
            [width / 2, length - c_depth], 
            [sholder_top_l + neck_w, length], 
            [width, length], 
            [width, 0], 
            )

        # default placement
        self.translate_by([-width / 2, 30 - length, 0])

        self.interfaces = [
            pyp.InterfaceInstance(self, self.edges[0]),
            pyp.InterfaceInstance(self, self.edges[1]),
            pyp.InterfaceInstance(self, self.edges[4]),
            pyp.InterfaceInstance(self, self.edges[5]),
        ]

class SimpleSleeve(pyp.Component):
    """Very simple sleeve"""
    # TODO Substitute T-Shirt sleeve with this one
    def __init__(self, tag) -> None:
        super().__init__(f'{self.__class__.__name__}_{tag}')

        # sleeves
        self.f_sleeve = SleevePanel(f'{tag}_f_sleeve').translate_by([0, 0, 15])
        self.b_sleeve = SleevePanel(f'{tag}_b_sleeve').translate_by([0, 0, -15])

        self.stitching_rules = [
            (self.f_sleeve.interfaces[0], self.b_sleeve.interfaces[0]),
            (self.f_sleeve.interfaces[2], self.b_sleeve.interfaces[2]),
        ]

        self.interfaces = [
            self.f_sleeve.interfaces[1],
            self.b_sleeve.interfaces[1],
        ]


class TShirt(pyp.Component):
    """Definition of a simple T-Shirt"""

    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

        # sleeves
        self.r_sleeve = SimpleSleeve('r')
        self.l_sleeve = SimpleSleeve('l').mirror()

        # Torso
        self.ftorso = TorsoPanel('ftorso').translate_by([0, 0, 20])
        self.btorso = TorsoPanel('btorso').translate_by([0, 0, -20])

        # Order of edges updated after (autonorm)..
        # TODO Simplify the choice of the edges to project from/to (regardless of autonorm)
        pyp.ops.cut_corner([self.r_sleeve.interfaces[0].edge], self.ftorso, 5, 6)
        pyp.ops.cut_corner([self.l_sleeve.interfaces[0].edge], self.ftorso, 1, 2)
        pyp.ops.cut_corner([self.r_sleeve.interfaces[1].edge], self.btorso, 0, 1)
        pyp.ops.cut_corner([self.l_sleeve.interfaces[0].edge], self.btorso, 5, 6)

        # DRAFT
        dart = pyp.ops.simple_sequence([0,0], [5, 10], [10, 0])
        eid = 1
        edges = pyp.ops.cut_into_edge(dart, self.ftorso.edges[eid], 0.3, right=False)

        self.ftorso.edges.pop(eid)
        for i, e in enumerate(edges):
            self.ftorso.edges.insert(eid + i, e)

        eid = 0
        edges = pyp.ops.cut_into_edge(dart, self.btorso.edges[eid], 0.3, right=True)
        self.btorso.edges.pop(eid)
        for i, e in enumerate(edges):
            self.btorso.edges.insert(eid + i, e)

        self.stitching_rules = [
            (self.ftorso.interfaces[-1], self.btorso.interfaces[-3]),
            (self.ftorso.interfaces[-3], self.btorso.interfaces[-1]),
            (self.ftorso.interfaces[-4], self.btorso.interfaces[-6]),
            (self.ftorso.interfaces[-6], self.btorso.interfaces[-4]),

            (self.r_sleeve.interfaces[0], self.ftorso.interfaces[-5]),
            (self.l_sleeve.interfaces[0], self.ftorso.interfaces[-2]),
            (self.r_sleeve.interfaces[1], self.btorso.interfaces[-5]),
            (self.l_sleeve.interfaces[1], self.btorso.interfaces[-2]),

        ]