"""Detailed skyscraper on any sectioned footprint: the same shape as the highrise landmark, plus declared facade bays."""
import copy
import kit

DEFAULT = {}
def from_landmark(L): return copy.deepcopy(L)
def build(spec): return kit.tower({**DEFAULT, **spec}, 'highrise')
