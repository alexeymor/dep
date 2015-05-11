""" 

INPUTS:
arg[1] - name of the file you want to parse. It will be parsed for assignment statements (find "=").

OUTPUTS:
(several files will be written:)
dot.gv - graph file understood by dot

DEPENDENCIES:
dot - not called inside this file, but you need to call afterwards to create an image

EXAMPLES: 
python dep_var_c.py hi.c #in terminal, in pycharm you have to edit Run->Edit Configurations
dot -Tsvg dot.gv -o dot.svg
"""

#the goal string for hierarchical edge d3.js plot is:
# [{"name":"analytics","size":3,"imports":["vis"]},{"name":"vis","size":3,"imports":[]}]


import subprocess #for using grep
import random
import sys #for getting command line args
import os # modified http://code.activestate.com/recipes/577027/


def dictinvert(d): #invert dictionary http://code.activestate.com/recipes/252143-invert-a-dictionary-one-liner/
    inv = {}
    for k, v in d.iteritems():
        keys = inv.setdefault(v, [])
        keys.append(k)
    return inv


def read_file(file, f):
    f = open(file, 'r')
    for line in f:
        if ('=' in line): #if a use statement
            line_trunc = line[line.find('=')+1 : line.find(',')].strip() #remove "use", anything after comma, any spaces
    f.close()
    return(f)


#contains (the imports and function definitions are over, so start the actual execution)

fn = sys.argv[1] #where do I start from

f = open(fn, 'r')
for line in f:
    if ('=' in line): #found use
        if ('//' not in line[:line.find('=')]): #this line is not commented out (FIXME doesn't handle multiline comments though)
            var = line[:line.find('=')] #just variable name
            var = var.strip() #remove extra spaces
            rhs = line[line.find('=')+1 : line.find(';')] #grab right hand side (from = to ;, FIXME need to deal with multiple assignments)
            rhs = rhs.split() #if space separated, we now have a list
f.close()


#merge the lists into a string understood by Graphviz's "dot"
#digraph G { main -> parse; main -> init; }
string = 'digraph G { size="7.75,10.25"; rankdir=LR; weight=1.2; nodesep=0.1; \n'
ranks = {fn:0} #dictionary of ranks for all files in files, first file gets rank of 0, every file used directly in the first file gets rank 1, every file used in file which is used in first file gets rank 2 and so on recursively
i=1 #number of edges
for f,d,s,c in zip(files, depends, size, color):
    for d1 in d: #flatten the dependencies first into "vis","hi" form
        string = string + '"'+f+'"' + '->' + '"'+d1+'"' + '[color="#' + c + '"];' 
        i=i+1
        if (d1 not in ranks): ranks[d1]=ranks[f]+1
    string = string + '\n' 

inv_ranks = dictinvert(ranks)
for r in inv_ranks:
    s=''
    for f in inv_ranks[r]:
        s = s + '"' + f + '" [color="#' + color[files.index(f)] + '"] '
    string = string + '{rank=same ' + s + '};\n'

string = string[:-2] + '}' #remove the last carriage return and semicolon and add the last bracket
f = open('dot.gv', 'w')
f.write(string)
f.close()
print 'number of nodes is', len(files) #print number of nodes
print 'number of edges is', i #print number of edges



#merge the lists into a JSON-like string: (for hierarchical edge layout like in http://mbostock.github.io/d3/talk/20111116/bundle.html 
# [{"name":"analytics","size":3,"imports":["vis"]},{"name":"vis","size":3,"imports":[]}]
string = '['
for f,d,s in zip(files, depends, size):
    df = ''
    for d1 in d: #flatten the dependencies first into "vis","hi" form
        df = df + '"' + d1 + '",'
    df = df[:-1] #remove the last comma
    string = string + '{"name":"' + f + '","size":' + str(s) + ',"imports":[' + df + ']},\n' 

string = string[:-2] + ']' #remove the last carriage return and comma and add the last bracket
#print string
f = open('d.json', 'w')
f.write(string)
f.close()


#merge the lists into a JSON-like string: (for hierarchical edge layout like in http://mbostock.github.io/d3/talk/20111116/bundle.html 
# [{"name":"analytics","size":3,"imports":["vis"]},{"name":"vis","size":3,"imports":[]}]
string = '['
for f,d,s in zip(files, depends, size):
    df = ''
    for d1 in d: #flatten the dependencies first into "vis","hi" form
        df = df + '"' + d1[:d1.find('.')] + '",'
    df = df[:-1] #remove the last comma
    string = string + '{"name":"' + f[:f.find('.')] + '","size":' + str(s) + ',"imports":[' + df + ']},\n' 

string = string[:-2] + ']' #remove the last carriage return and comma and add the last bracket
#print string
f = open('g.json', 'w')
f.write(string)
f.close()


#merge the lists into a more complex JSON-like string: (for hierarchical edge layout like in http://mbostock.github.io/d3/talk/20111116/bundle.html
# [{"name":"flare","size":3,"imports":["flare.vis"]},{"name":"flare.vis","size":3,"imports":[]}]
long_names={fn:fn[:fn.find('.')]} #store filenames in flare.vis.a.b.c format (flare depends on vis which depends on a, which depends on b ... on c and throw away all the ".f90" extensions.
string = '['
for f,d,s in zip(files, depends, size):
    df = ''
    for d1 in d: #flatten the dependencies first into "vis","hi" form
        if (d1 not in long_names): long_names[d1]=long_names[f]+'.'+d1[:d1.find('.')]
        df = df + '"' + long_names[d1] + '",'
    df = df[:-1] #remove the last comma
    string = string + '{"name":"' + long_names[f] + '","size":' + str(s) + ',"imports":[' + df + ']},\n' 

string = string[:-2] + ']' #remove the last carriage return and comma and add the last bracket
#print string
f = open('gl.json', 'w')
f.write(string)
f.close()


#merge the lists into another JSON-like string: (for forced layout like here http://bl.ocks.org/mbostock/1153292
# [{source: "main", target: "ModInputs"},{source: "main", target: "ModTime"}]
string = '['
for f,d,s,c in zip(files, depends, size, color):
    df = ''
    for d1 in d: #flatten the dependencies
        df = df + '{source: "' + f + '", target: "' + d1 + '", color: "#' + c + '"},\n'
    string = string + df 
string = string[:-2] + ']' #remove the last carriage return and comma and add the last bracket

#print string

f = open('forced.json', 'w')
f.write(string)
f.close()

# now create a css file for colors of nodes 
# .main {fill: #fdd700;} .ModInputs {fill: #fdd700;}
string = ''
for f, s, c in zip(files, size, color):
    string = string + '.' + f + ' {fill: #' + c + '; r: ' + str(s) + ';}\n' 

#print string

f = open('forced.css', 'w')
f.write(string)
f.close()


#mv he.json he1.json 
#mv dot.gv dot1.gv 
#mv forced.css forced1.css 
#mv forced.json forced1.json 
#dot -Teps dot1.gv -o gitm.eps

#mv he.json he2.json 
#mv dot.gv dot2.gv 
#mv forced.css forced2.css 
#mv forced.json forced2.json 
#dot -Teps dot2.gv -o dart.eps
