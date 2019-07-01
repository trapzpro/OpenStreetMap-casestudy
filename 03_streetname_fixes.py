#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
Fill out the count_tags function. It should return a dictionary with the 
tag name as the key and number of times this tag can be encountered in 
the map as value.

Note that your code will be tested with a different data file than the 'example.osm'
"""
from collections import defaultdict
import xml.etree.cElementTree as ET
import pprint
import re
import datetime
print(datetime.datetime.now())
osm_file = open('cfalls-stow.osm','r')
#13,5
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_types = defaultdict(set)

expected = ["Street","Avenue","Boulevard","Drive","Court","Place","Lane","Road","Trail","Circle","Way","Parkway","Path","Plaza","Square","Terrace"]

mapping = { "St": "Street",
            "St.": "Street",
            "Blvd": "Boulevard",
            "Ave": "Avenue",
            "Rd.": "Road",
            "Rd":"Road",

            }

def update_name(name, mapping):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        # https://stackoverflow.com/questions/10116518/im-getting-key-error-in-python#10116540
        # Added check to only update if mapping exists - avoids key error
        if (street_type not in expected and street_type in mapping):
            name = re.sub(street_type_re, mapping[street_type], name)
    return name

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")
    #return (elem.attrib['k'] == "name")
    #return (elem.attrib['k'] == "tiger:name_type")


def getelements(filename_or_file, tag):
    context = iter(ET.iterparse(filename_or_file, events=('start', 'end')))
    _, root = next(context) # get root element
    for event, elem in context:
        if event == 'end' and elem.tag == tag:
            yield elem
            root.clear() # preserve memory

def audit():
    print(datetime.datetime.now())
    elements = getelements(osm_file, "way")
    counter = 0
    for elem in elements:
    #for event, elem in  ET.iterparse(osm_file,events=("start",)):
    #    if elem.tag == "way":
        #pprint.pprint(elem.attrib)
            #attrList = elem.items()
            #print(len(attrList), " : [", attrList, "]" )
            #print(elem.tostring() )
        for tag in elem.iter("tag"):
            if is_street_name(tag):
                #pprint.pprint("Checking " + tag.attrib['v']) 
                audit_street_type(street_types, tag.attrib['v'])
        counter += 1

    pprint.pprint(dict(street_types))
    print(datetime.datetime.now())
    return street_types

if __name__ == '__main__':
    #print('about to get elements')
    #elements = getelements(osm_file, "way")
    #print('got elements')
    #for elem in elements:
    #    print(elem)
    audit()
    st_types = street_types
    pprint.pprint(dict(street_types))
    pprint.pprint(dict(st_types))
    #Python 3 renamed dict.iteritems -> dict.items
    #https://stackoverflow.com/questions/30418481/error-dict-object-has-no-attribute-iteritems
    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
            print(name, "=>", better_name)




def count_tags(filename):
    tags = defaultdict(int)
    for event, elem in  ET.iterparse(filename):
        tags[elem.tag] += 1
    return tags
            



def test():
    tags = count_tags('ohio-latest.osm')
    pprint.pprint(tags)
    #assert tags == {'bounds': 1,
     #                'member': 3,
      #               'node': 20,
       #              'osm': 1,
        #             'relation': 1,
         #            'tag': 7,
          #           'way': 1}

    

