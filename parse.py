__author__ = 'jerzy'
import lxml
import lxml.objectify


def get_string():
    return open('TERC.xml', 'rb').read()
o = lxml.objectify.fromstring(get_string())


def row_level(row):
    for col in row.col:
        if col.get('name') == 'NAZDOD':
            if str(col).count('miasto na prawach powiatu') >= 1:
                return 'miastopowiat'
            if str(col).count('gmina') >= 1:
                return 'gmina'
            return str(col)
    return None


def row_name(row):
    for col in row.col:
        if col.get('name') == 'NAZWA':
            return str(col)
    return None


def row_region(row):
    for col in row.col:
        if col.get('name') == 'WOJ':
            return int(col)
    return None


def row_subregion(row):
    for col in row.col:
        if col.get('name') == 'POW':
            return int(col)
    return None


def row_community(row):
    for col in row.col:
        if col.get('name') == 'GMI':
            return int(col)
    return None


class Region:

    def __init__(self, name):
        self.name = name
        self.subregions = []
        self.id = None
        for row in o.catalog.row:
            if row_level(row) == 'województwo' and row_name(row) == name:
                self.id = row_region(row)
                self.level = row_level(row)
        self.find_subregions()

    def find_subregions(self):
        for row in o.catalog.row:
            if row_region(row) == self.id and (row_level(row) == 'powiat' or \
                                               row_level(row) == 'miastopowiat'):
                self.subregions.append(SubRegion(row_name(row), self))

    def __repr__(self):
        return "<Region: {}".format(self.name)

    def __getitem__(self, name):
        for subregion in self.subregions:
            if subregion.name == name:
                return subregion
        return None


class SubRegion:
    def __init__(self, name, region):
        self.name, self.region = name, region
        self.id = None
        for row in o.catalog.row:
            if row_region(row) == region.id and row_name(row) == name:
                self.id = row_subregion(row)
                self.level = row_level(row)
        self.communities = []
        self.find_communities()

    def find_communities(self):
        for row in o.catalog.row:
            if row_level(row) == 'gmina' and row_region(row) == self.region.id\
                    and row_subregion(row) == self.id:
                com = Community(row_name(row), self, self.region)
                self.communities.append(com)

    def __repr__(self):
        return "<SubRegion: {}>".format(self.name)

    def __getitem__(self, name):
        for community in self.communities:
            if community.name == name:
                return community
        return None


class Community:
    def __init__(self, name, subregion, region):
        self.name, self.subregion, self.region = name, subregion, region
        self.id = None
        for row in o.catalog.row:
            if row_level(row) == 'gmina' and row_region(row) == self.region.id and row_subregion(row) == self.subregion.id:
                self.id = row_community(row)
        if self.subregion.name == self.name:
            self.level = 'miastopowiat'
        else:
            self.level = 'gmina'

    def __repr__(self):
        return "<Community: {}>".format(self.name)


class Map:
    def __init__(self):
        self.regions = []
        self._init_regions()

    def _init_regions(self):

        def region_saved(region_name):
            for region in self.regions:
                if region.name == region_name:
                    return True
            return False

        for row in o.catalog.row:
            if row_level(row) == 'województwo' and not region_saved(row_name(row)):
                self.regions.append(Region(row_name(row)))
                print('saved',row_name(row))
