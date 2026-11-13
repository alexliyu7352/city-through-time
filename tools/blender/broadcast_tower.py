"""Detailed television / observation tower: shared spheres and members, with equatorial glazing belts."""
import copy
import kit

DEFAULT = {}
def from_landmark(L): return copy.deepcopy(L)
def build(spec): return kit.tower({**DEFAULT, **spec}, 'broadcast_tower')
