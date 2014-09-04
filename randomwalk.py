import numpy as np

#import networkx as nx
from random import choice, random
#import math

import pandas as pd
import vincent

get_ipython().run_cell_magic(u'html', u'', u'<div id="d3-example"></div>\n<style>\n.node {stroke: #fff; stroke-width: 1.5px;}\nmarker {stroke: #999;}\n.link {stroke: #999; stroke-opacity: .3;}\n</style>\n<script src="force.js"></script>')


def edgetokey(e):
    (u,v) = e
    return '(' + str(u) + ', ' + str(v) + ')'

def isexpensive(G,expensiveedges,e):
    if G.is_directed():
        return edgetokey(e) in expensiveedges
    else:
        (u,v) = e
        return edgetokey((u,v)) in expensiveedges or edgetokey((v,u)) in expensiveedges 

def dictcounter(d, k, v=1):
    try:
        d[k] += v
    except:
        d[k] = v

def plotrwresult(G):
    visits = [G.node[node]['visits'] for node in G.nodes_iter() ]
    norm_visits = np.array(visits)/float(G.graph['total_visits'])

    deaths = [G.node[node]['deaths'] for node in G.nodes_iter() ]
    norm_deaths = np.array(deaths)/float(sum(deaths))

    if G.is_directed():
        degrees = [ G.in_degree(node) for node in G.nodes_iter() ]
        norm_degrees = np.array(degrees)/float(G.size())
    else:
        degrees = [ G.degree(node) for node in G.nodes_iter() ]
        norm_degrees = np.array(degrees)/float(2*G.size())

    multi_iter1 = {'index':range(G.order()), 'Visits':norm_visits, 'Deaths':norm_deaths, 'Degree':norm_degrees}
    line = vincent.Scatter(multi_iter1, iter_idx='index')
    line.axis_titles(x='Vertex', y='Juice')
    line.legend(title='Results')
    line.width = 400
    line.height = 300
    line.marks[0].marks[0].properties.enter.opacity = vincent.ValueRef(value=1)
    
    line.marks[0].marks[0].properties.update = vincent.PropertySet()
    line.marks[0].marks[0].properties.update.size = vincent.ValueRef(value=100)
    line.marks[0].marks[0].properties.hover = vincent.PropertySet()
    line.marks[0].marks[0].properties.hover.size = vincent.ValueRef(value=200)
    line.marks[0].marks[0].properties.update.size = vincent.ValueRef(value=100)
    line.marks[0].marks[0].properties.hover = vincent.PropertySet()
    line.marks[0].marks[0].properties.hover.size = vincent.ValueRef(value=200)
    line.scales['shape'] = vincent.Scale(name='shape', type='ordinal',
                          domain=vincent.DataRef(data='table', field='data.col'),
                          range=["square", "circle", "triangle-down", "triangle-up"])
    line.marks[0].marks[0].properties.enter.shape = vincent.ValueRef(scale="shape", field="data.col")
    line.legends[0].shape = "shape" 
    
    return line

def randomwalk(G, frogs, P_die, T=10, expensiveedges = []):
    G.graph['teleportations'] = {}
    G.graph['waiting'] = {}
    for node in G.nodes_iter():
        G.node[node]['visits'] = 0
        G.node[node]['deaths'] = 0
        G.node[node]['frogs'] = 0
        G.node[node]['incomingfrogs'] = 0
    # Initialize edge traversal counters
    for e in G.edges_iter():
        G.edge[e[0]][e[1]]['timeline'] = {}
        if not G.is_directed():
            G.edge[e[0]][e[1]]['frogstosmall'] = 0
            G.edge[e[0]][e[1]]['frogstolarge'] = 0
        else:
            G.edge[e[0]][e[1]]['frogs'] = 0
        
    frogs_left = frogs
    time = 0
    G.graph['total_visits'] = 0
    G.graph['death_times_sum'] = 0
    
    frog_locations = np.random.randint(0, high = G.number_of_nodes(), size = frogs).tolist()
    for i in range(frogs):
        G.node[frog_locations[i]]['frogs'] += 1
    del frog_locations
    
    while frogs_left:
        time +=1
        
        # Deal with old node frogs
        for node in G.nodes_iter():
            if G.node[node]['frogs'] == 0:
                continue
            for f in range(G.node[node]['frogs']):
                # Flip coin to die
                if random() < P_die:
                    G.node[node]['deaths'] += 1
                    G.graph['death_times_sum'] += time
                    frogs_left -= 1
                    continue
                G.graph['total_visits'] +=1
                # Node has successors
                if len(G[node])>0:
                    loc = choice(G[node].keys())
                    if G.is_directed():
                        G.edge[node][loc]['frogs'] += 1
                    else:
                        if loc >= node:
                            G.edge[node][loc]['frogstolarge'] += 1
                        else:
                            G.edge[node][loc]['frogstosmall'] += 1
                # Node does not have successors - Teleport
                else:
                    loc = np.random.randint(0, high = G.number_of_nodes())
                    dictcounter(G.graph['teleportations'],time)
                    G.node[loc]['incomingfrogs'] += 1
                G.node[loc]['visits'] +=1
            G.node[node]['frogs'] = 0
            
        # Deal with edge frogs
        for (u,v) in G.edges_iter():
            # Don't process expensive edges unless time is multiple of T
            if isexpensive(G, expensiveedges, (u,v)) and not (time % T == ((u+v) % T)):
            #if isexpensive(G, expensiveedges, (u,v)) and not (time % T == 0):
                if G.is_directed():
                    dictcounter(G.graph['waiting'], time, G.edge[u][v]['frogs'])
                else:
                    dictcounter(G.graph['waiting'], time, G.edge[u][v]['frogstosmall'])
                    dictcounter(G.graph['waiting'], time, G.edge[u][v]['frogstolarge'])
                continue
            
            if G.is_directed():
                G.node[v]['incomingfrogs'] += G.edge[u][v]['frogs']
                dictcounter(G.edge[u][v]['timeline'], time, G.edge[u][v]['frogs'])
                G.edge[u][v]['frogs'] = 0
            else:
                if v >= u:
                    large = v
                    small = u
                else:
                    large = u
                    small = v
                    
                G.node[large]['incomingfrogs'] += G.edge[u][v]['frogstolarge']
                dictcounter(G.edge[u][v]['timeline'], time, G.edge[u][v]['frogstolarge'])
                G.edge[u][v]['frogstolarge'] = 0
                
                G.node[small]['incomingfrogs'] += G.edge[u][v]['frogstosmall']
                dictcounter(G.edge[u][v]['timeline'], time, G.edge[u][v]['frogstosmall'])
                G.edge[u][v]['frogstosmall'] = 0
                
        # Deal with node incoming frogs
        for node in G.nodes_iter():
            G.node[node]['frogs'] += G.node[node]['incomingfrogs']
            G.node[node]['incomingfrogs'] = 0

    G.graph['endtime'] = time

def plotrwtraversal(G, expensiveedges=[], time=None, countfrogs = False):
    data = []
    index = []

    for e in G.edges_iter():
        key = edgetokey((e[0], e[1]))
        sr = pd.Series(G.edge[e[0]][e[1]]['timeline'])
        if not countfrogs:
            sr[sr>0] = 1
        data.append(sr)
        index.append(key)
    
    if time:
        data.append(pd.Series(time*[0]))
        index.append('hack')
    
    df = pd.DataFrame(data, index=index).T
          
    if time:
        del df['hack']
        
    dfexp = df[expensiveedges].copy()
    dfcheap = df.copy()
    dfcheap.drop(expensiveedges, 1, inplace=True)
    
    dfexpcopy = dfexp.copy()
    dfexpcopy[dfexp>0] = 1
    cost = (dfexpcopy.sum(axis=1)).sum()
    
    G.graph['cost'] = cost
    
    if len(expensiveedges)>0:
        datacost = []
        indexcost = []
        datacost.append(dfexp.sum(axis=1))
        indexcost.append('Expensive')
        datacost.append(dfcheap.sum(axis=1))
        indexcost.append('Cheap')
        
        dfcost = pd.DataFrame(datacost, index=indexcost).T
        
        finaldf = dfcost
    else:
        finaldf = df

    showteleportations = (len(G.graph['teleportations'])>0) and countfrogs

    if showteleportations:
    # Count teleportations
        finaldf['Teleportation'] = pd.Series(G.graph['teleportations'])
    
    try:
        if countfrogs and len(G.graph['waiting'])>0:
            finaldf['Waiting'] = pd.Series(G.graph['waiting'])
    except:
        pass

    line = vincent.StackedArea(finaldf)
    if not countfrogs:
        line.axis_titles(x='Rounds', y='# edges traversed')
    else:
        line.axis_titles(x='Rounds', y='# frogs')
    
    line.legend(title='Edge')
    line.width = 400
    line.height = 300
    line.marks[0].marks[0].properties.enter.opacity = vincent.ValueRef(value=0.8)
   
    if len(expensiveedges)>0:
        if showteleportations:
            line.colors(range_=['#ff0000','#50aa50','#6060aa', '#eeeeee'])
        else:
            line.colors(range_=['#ff0000','#50aa50', '#eeeeee'])

    
    line.marks[0].marks[0].properties.update = vincent.PropertySet()
    line.marks[0].marks[0].properties.update.size = vincent.ValueRef(value=100)
    line.marks[0].marks[0].properties.hover = vincent.PropertySet()
    line.marks[0].marks[0].properties.hover.size = vincent.ValueRef(value=200)

    line.marks[0].marks[0].properties.update.opacity = vincent.ValueRef(value=0.8)
    line.marks[0].marks[0].properties.hover.opacity = vincent.ValueRef(value=1)
        
    return line, finaldf

# ------------------------------------------------------

def randomwalkold(G, frogs, P_die):
    frog_locations = np.random.randint(0, high = G.number_of_nodes(), size = frogs).tolist()
    G.graph['teleportations'] = {}
    for node in G.nodes_iter():
        G.node[node]['visits'] = 0
        G.node[node]['deaths'] = 0
    # Initialize edge traversal counters
    for e in G.edges_iter():
        G.edge[e[0]][e[1]]['timeline'] = {}
    frogs_left = frogs
    time = 0
    G.graph['total_visits'] = 0
    G.graph['death_times_sum'] = 0

    while frogs_left:
        time +=1
        for f in range(frogs):
            curloc = frog_locations[f]

            # Skip dead frogs
            if curloc == None:
                continue

            # Flip coin to die
            if random() < P_die:
                G.node[curloc]['deaths'] += 1
                G.graph['death_times_sum'] += time
                frog_locations[f] = None
                frogs_left -= 1
                continue

            G.graph['total_visits'] +=1

            # Node has successors
            if len(G[curloc])>0:
                frog_locations[f] = choice(G[curloc].keys())
                loc = frog_locations[f]

                dictcounter(G.edge[curloc][loc]['timeline'], time)

            # Node does not have successors - Teleport
            else:
                frog_locations[f] = np.random.randint(0, high = G.number_of_nodes())
                dictcounter(G.graph['teleportations'],time)


            G.node[frog_locations[f]]['visits'] +=1
            
        G.graph['endtime'] = time

