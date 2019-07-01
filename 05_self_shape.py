
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_FILE = open('cfalls-stow.osm','r')
OSM_PATH = "cfalls-stow.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS, problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []

    tags = []  # Handle secondary tags the same way for both node and way elements
    
    if (element.tag != "node" and element.tag != "way"):
         return None

    if element.tag == 'node':
        for attr, val in element.attrib.items():
            if attr in node_attr_fields:
                node_attribs[attr] = val
                #pprint.pprint('setting '+attr+' to '+val)
        # Tag children from parent elem
        for child in element.iter("tag"):
            pprint.pprint(child)
            if child.tag == 'tag':
                if problem_chars.match(child.attrib['k']) is not None:
                    pprint.pprint(' not checking because')
                    continue
                else:
                    pprint.pprint(' about to check load_new_tag')
                    new = load_new_tag(element, child, default_tag_type)
                    if new is not None:
                        tags.append(new)
        if len(tags) > 0:
            pprint.pprint({'node': node_attribs, 'node_tags': tags})
        return {'node': node_attribs, 'node_tags': tags}


    return 


def load_new_tag(element, secondary, default_tag_type):
    pprint.pprint({element:element, secondary:secondary, default_tag_type:default_tag_type})
    """
    Load a new tag dict to go into the list of dicts for way_tags, node_tags
    """
    new = {}
    new['id'] = element.attrib['id']
    if ":" not in secondary.attrib['k']:
        new['key'] = secondary.attrib['k']
        new['type'] = default_tag_type
    else:
        post_colon = secondary.attrib['k'].index(":") + 1
        new['key'] = secondary.attrib['k'][post_colon:]
        new['type'] = secondary.attrib['k'][:post_colon - 1]

    # Cleaning and loading values of various keys
#    if is_street_name(secondary):
        # Why don't i need to use mapping, street_mapping,
        # and num_line_mapping dicts  as params?
#        street_name = update_name(secondary.attrib['v'])
#        new['value'] = street_name
    
#    elif new['key'] == 'phone':
#        phone_num = update_phone_num(secondary.attrib['v'])
#        if phone_num is not None:
#            new['value'] = phone_num
#        else:
 #           return None
    
 #   elif new['key'] == 'province':
        # Change Ontario to ON
 #       province = secondary.attrib['v']
 #       if province == 'Ontario':
 #           province = 'ON'
 #       new['value'] = province

 #   elif new['key'] == 'postcode':
 #       post_code = secondary.attrib['v'].strip()
 #       m = POSTCODE.match(post_code)
 #       if m is not None:
            # Add space in middle if there is none
 #           if " " not in post_code:
 #               post_code = post_code[:3] + " " + post_code[3:]
            # Convert to upper case
 #           new['value'] = post_code.upper()
 #       else:
            # Keep zip code revealed in postal code audit for document deletion purposes
  #          if post_code[:5] == "14174":
  #              new['value'] = post_code
            # Ignore tag if improper postal code format
 #           else:
 #               return None

#    else:
    new['value'] = secondary.attrib['v']
    return new




def getelements(filename_or_file, tag):
    context = iter(ET.iterparse(filename_or_file, events=('start', 'end')))
    _, root = next(context) # get root element
    for event, elem in context:
        if event == 'end' and elem.tag == tag:
            yield elem
            root.clear() # preserve memory

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator._errors.document_error_tree())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in iter(errors.document_error_tree())
        )
        pprint.pprint(message_string.format(field, "\n".join(error_strings)));
        


if __name__ == '__main__':
    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()
        elements = getelements(OSM_FILE, "node")
        for elem in elements:
            el = shape_element(elem)

            if elem.tag == 'node':
                validate_element(el, validator)
                nodes_writer.writerow(el['node'])
                node_tags_writer.writerows(el['node_tags'])
