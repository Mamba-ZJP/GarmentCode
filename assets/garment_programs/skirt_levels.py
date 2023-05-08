
from copy import deepcopy

# Custom
import pypattern as pyp
from .skirt_paneled import *
from .circle_skirt import *

class SkirtLevels(pyp.Component):
    """Skirt constiting of multuple stitched skirts"""

    def __init__(self, body, design) -> None:
        super().__init__(f'{self.__class__.__name__}')

        ldesign = design['levels-skirt']
        lbody = deepcopy(body)  # We will modify the values, so need a copy
        n_levels = ldesign['num_levels']['v']
        ruffle = ldesign['level_ruffle']['v']

        base_skirt = globals()[ldesign['base']['v']]
        self.subs.append(base_skirt(body, design))

        level_skirt = globals()[ldesign['level']['v']]

        # Place the levels
        for i in range(n_levels):
            top_width = self.subs[-1].interfaces['bottom'].edges.length()
            top_width *= ruffle

            # TODO Warnings for the subs with the same names!

            # Adjust the mesurement to trick skirts into producing correct width
            lbody['waist'] = top_width
            self.subs.append(level_skirt(lbody, design, tag=i))

            # Placement
            # TODO Rotation if base is assymetric
            self.subs[-1].place_by_interface(
                self.subs[-1].interfaces['top'],
                self.subs[-2].interfaces['bottom'], 
                gap=5
            )
            # Stitch
            self.stitching_rules.append((
                self.subs[-2].interfaces['bottom'], 
                self.subs[-1].interfaces['top']
            ))

        self.interfaces = {
            'top': self.subs[0].interfaces['top']
        }