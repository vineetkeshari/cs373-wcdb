from xml.etree import ElementTree as ET

def read_xml (filename) :
    tree = ET.parse (filename)
    return tree.getroot()

def initialize_pages () :
    all_models = {}

    all_models['crises'] = {}
    all_models['people'] = {}
    all_models['orgs'] = {}

    return all_models

def create_model (node) :
    # TODO: create a corresponding model from the node element
    # and return it
    # <code here>

    return None

def parse_recurse (node, all_models, current_model_stack) :
    for child in node :
        child_model = create_model (child)
        # TODO: add child_model to all_models depending on
        #  where we currently are on the stack
        # <code here>

        # call recursively for each child element.
        # push the current model onto the stack before the call
        # and pop it afterwards.
        # this needs to be done only if the child XML element will
        # need a new model. we'll need to figure out how to decide
        # what to do once we know the django model structure better.
        current_model_stack.append (child_model)
        parse_recurse (child, all_models, current_model_stack)
        current_model_stack.pop()

def parse_xml (root) :
    all_models = initialize_pages ()
    current_model_stack = []
    parse_recurse (root, all_models, current_model_stack)
    return all_models

# Call this method
def process_xml (filename) :
    root = read_xml (filename)
    return parse_xml (root)

