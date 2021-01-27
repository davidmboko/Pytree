"""Assignment 2: Modelling Population Data

=== CSC148 Fall 2020 ===
Diane Horton, David Liu, and Daniel Zingaro
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains a new class, PopulationTree, which is used to model
population data drawn from the World Bank.
Even though this data has a fixed hierarchical structure (only three levels:
world, region, and country), because we are able to model it using an
AbstractTree subclass, we can then run it through our treemap visualisation
tool to get a nice interactive graphical representation of this data.

Recommended steps:
1. Read through all docstrings in this file once. There's a lot to take in,
   so don't feel like you need to understand it all the first time.
   It may be helpful to draw a small diagram of how all the helper functions
   fit together - we've provided most of the structure for you already.
2. Complete the helpers _get_population_data and _get_region_data.
   Both of these can be completed without recursion or any use of trees
   at all: they are simply exercises in taking some complex JSON data,
   and extracting the necessary information from them.
3. Review the PopulationTree constructor docstring. Note that when the first
   parameter is set to False, this behaves exactly the same as the
   AbstractTree constructor.
4. Complete _load_data. Use the PopulationTree constructor, but you should
   only need to pass in False for the first argument (this allows you to
   create the region and country nodes directly, without trying to access
   the World Bank file again).
"""

from __future__ import annotations
import json
from typing import Optional, List, Dict

from tree_data import AbstractTree

# Constants for the World Bank population files
WORLD_BANK_POPULATIONS = 'populations.json'
WORLD_BANK_REGIONS = 'regions.json'


class PopulationTree(AbstractTree):
    """A tree representation of country population data.

    This tree always has three levels:
      - The root represents the entire world.
      - Each node in the second level is a region (defined by the World Bank).
      - Each node in the third level is a country.

    The data_size attribute corresponds to the 2019 population of the country,
    as reported by the World Bank.

    """

    def __init__(self: PopulationTree, world: bool,
                 root: Optional[object] = None,
                 subtrees: Optional[List[PopulationTree]] = None,
                 data_size: int = 0) -> None:
        """Initialize a new PopulationTree.

        If <world> is True, then this tree is the root of the population tree,
        and it should load data from the World Bank files.
        In this case, none of the other parameters are used.

        If <world> is False, pass the other arguments directly to the superclass
        constructor. Do NOT load new data from the World Bank files.
        """
        if world:
            region_trees = _load_data()
            AbstractTree.__init__(self, 'World', region_trees)
        else:
            if subtrees is None:
                subtrees = []
            AbstractTree.__init__(self, root, subtrees, data_size)

    def get_separator(self: PopulationTree) -> str:
        return " -> "


def _load_data() -> List[PopulationTree]:
    """Create a list of trees corresponding to different world regions.

    Each tree consists of a root node -- the region -- attached to one or
    more leaves -- the countries in that region.
    """
    # Get data from World Bank files.
    country_populations = _get_population_data()
    regions = _get_region_data()

    # Be sure to read the docstring of the PopulationTree constructor to see
    # how to call it.
    # You'll want to complete the two helpers called above first (otherwise
    # this function won't run).
    # You can complete this function *without* using recursion.
    # Remember that each region tree has only two levels:
    #   - a root storing the name of the region
    #   - zero or more leaves, each representing a country in the region
    lst = []
    for region, countries in regions.items():
        root = region
        subtrees = []
        for country in countries:
            if country in country_populations:
                population = country_populations[country]
                sub_tree = PopulationTree(False, country, None, population)
                subtrees.append(sub_tree)
        tree = PopulationTree(False, root, subtrees)
        lst.append(tree)
    return lst


def _get_population_data() -> Dict[str, int]:
    """Return country population data from the World Bank.

    The return value is a dictionary, where the keys are country names,
    and the values are the corresponding populations of those countries.

    Ignore all countries that do not have any population data,
    or population data that cannot be read as an int.
    """
    # We are doing some pre-processing of the data for you.
    # The first element returned is ignored because it's just metadata.
    # The second element's first 47 elements are ignored because they aren't
    # countries.
    _, population_data = _get_json_data(WORLD_BANK_POPULATIONS)
    population_data = population_data[47:]

    # The following line is a good place to put a breakpoint, so that you can
    # pause the program and use the debugger to inspect the contents of
    # population_data.
    countries = {}

    for i in population_data:
        country = i["country"]["value"]
        population = i["value"]
        if isinstance(population, int):
            countries[country] = int(population)
    return countries


def _get_region_data() -> Dict[str, List[str]]:
    """Return country region data from the World Bank.

    The return value is a dictionary, where the keys are region names,
    and the values a list of country names contained in that region.

    Ignore all regions that do not contain any countries.
    """
    # We ignore the first component of the returned JSON, which is metadata.
    _, country_data = _get_json_data(WORLD_BANK_REGIONS)

    # The following line is a good place to put a breakpoint to help inspect
    # the contents of country_data.
    regions = {}
    for i in country_data:
        region = i["region"]["value"]
        if i["region"]['id'] != "NA":
            if region not in regions:
                regions[region] = [i["name"]]
            else:
                regions[region].append(i["name"])
    return regions


def _get_json_data(fname: str) -> dict:
    """Return a dictionary representing the JSON data from file fname.

    You should not modify this function.
    """
    f = open(fname)
    return json.loads(f.read())


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(
        config={
            'allowed-io': ['_get_json_data'],
            'extra-imports': ['json', 'tree_data']})
