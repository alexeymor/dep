""" 

INPUTS:
arg[1] - name of the file you want to parse. It will be parsed for assignment statements (find "=").

OUTPUTS:
(several files will be written:)
dot.gv - graph file understood by dot
d.json - graph file understood by hierarchical edge d3.js plot:
# [{"name":"analytics","size":3,"imports":["vis"]},{"name":"vis","size":3,"imports":[]}]

DEPENDENCIES:
dot - not called inside this file, but you need to call afterwards to create an image

EXAMPLES: 
python dep_var_c.py hi.c     #this is in terminal, if you want pycharm you have to edit Run->Edit Configurations
dot -Tpng dot.gv -o dot.png  #to render text file to a graph in png file
"""

import sys #for getting command line args

def is_float(s):  #http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float-in-python
    try:
        float(s)
        return True
    except ValueError:
        return False

def dictinvert(d): #invert dictionary http://code.activestate.com/recipes/252143-invert-a-dictionary-one-liner/
    inv = {}
    for k, v in d.iteritems():
        keys = inv.setdefault(v, [])
        keys.append(k)
    return inv


#contains (the imports and function definitions are over, so start the actual execution)

fn = sys.argv[1] #file name

links = {} #dictionary of the form variable:source (ie b=a is represented by b:a)


f = open(fn, 'r')
for line in f:
    if ('=' in line):  #found assignment
        if ('//' not in line[:line.find('=')]):  #this line is not a comment (FIXME doesn't handle multiline comments though)
            var = line[:line.find('=')]  #variable name
            var = var.strip()  #remove extra spaces
            rhs = line[line.find('=')+1 : line.find(';')]  #grab right hand side (from = to ;, FIXME need to deal with multiple assignments)
            rhs = rhs.replace('+', ' ')  #remove all algebraic operations
            rhs = rhs.replace('-', ' ')
            rhs = rhs.replace('*', ' ')
            rhs = rhs.replace('/', ' ')
            rhs = rhs.replace('(', ' ')  #remove all brackets FIXME - this kinda makes all function names into variables
            rhs = rhs.replace(')', ' ')
            rhs = rhs.split()
            for i in rhs:  #loop over all source variables
                if (not is_float(i)):  #ignore constants
                    try:  #if this is the first source, the appending will fail
                        links[var] = [links[var], i]
                    except:
                        links[var] = i
f.close()


#merge the lists into a string understood by Graphviz's "dot"
#digraph G { main -> parse; main -> init; }
string = 'digraph G { size="7.75,10.25"; rankdir=LR; weight=1.2; nodesep=0.1; \n'
for sink in links:
    for source in links[sink]: #flatten the dependencies first into "vis","hi" form
        string = string + '"'+source+'"' + '->' + '"'+sink+'";'
    string = string + '\n' 

string = string[:-2] + '}' #remove the last carriage return and semicolon and add the last bracket
f = open('dot.gv', 'w')
f.write(string)
f.close()
print 'number of vars is', len(links) #print number of nodes
#print 'number of edges is', i #print number of edges #how'd you compute this?