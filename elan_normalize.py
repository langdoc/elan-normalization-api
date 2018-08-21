from flask import Flask
from flask import request
import re
from collections import OrderedDict
import xml.etree.ElementTree as ET

app = Flask(__name__)

# This is copied from here:
# https://stackoverflow.com/questions/13668829/replace-every-nth-letter-in-a-string

def replace_n(string, n, first=0):
    letters = (
        # i % n == 0 means this letter should be replaced
        "x" if i % n == 0 else char

        # iterate index/value pairs
        for i, char in enumerate(string, -first)
    )
    return ''.join(letters)

@app.route("/", methods=['POST'])
def elan_normalize():
    
    # This saves the input so it is easier to examine what is going on
    with open("examples/input_from_elan.xml","wb") as fo:
        fo.write(request.data)
    
    # The language tag is needed also here, but to make the normalization
    # patterns really relevant and interesting, there should be some info
    # about more nuanced dialects…
    # cg = Cg3("kpv")
    
    tree = ET.fromstring(request.data)

    xmlns = {'corpus': '{http://www.dspin.de/data/textcorpus}'}
    
    # The sentences are somehow tokenized, but this should be done better…
    
    tokens = []
    for token in tree.findall('.//{corpus}token'.format(**xmlns)):
        tokens.append(token.text)
    
    # I collect here everything into distinct lists so that I can later
    # loop over them. There is probably some better data structure in
    # Python -- maybe what comes out from uralicNLP is already something better?
    
    token_ids = []
    for token in tree.findall('.//{corpus}token'.format(**xmlns)):
        token_ids.append(token.attrib['ID'])
    
    tag_ids = []
    for token_id in token_ids:
        tag_ids.append(re.sub('t', 'pt', token_id))
    
    # This constructs the XML, the namespaces were bit tricky, but everything
    # seems to work now. First we create POStags node and then put it to the
    # right place.
    
    pos_tag = ET.Element("ns2:POStags", tagset="stts")
    
    textcorpus = tree.find('.//{corpus}TextCorpus'.format(**xmlns))
    textcorpus.append(pos_tag)
        
    # This modifies the content that is coming from tokens, but it
    # should be easy to modify the tokens themselves in this point,
    # one just has to find and replace them in TCF?
    
    tags = []
    
    for token in tokens:
        tags.append(replace_n(token, 2))
    
    for token_id, tag_id, tag in zip(token_ids, tag_ids, tags):
        current_tag = ET.Element("tag", tokenIDs=token_id, ID=tag_id)
        current_tag.text = tag
        textcorpus.append(current_tag)
   
   # This writes the output into file for examination
   
    with open("output.txt","wb") as fo:
        fo.write(ET.tostring(tree))
    
    return(ET.tostring(tree))

if __name__ == "__main__":
    app.run()
