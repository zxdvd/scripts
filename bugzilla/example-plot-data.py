import sys

import matplotlib.pyplot as plt
from pymongo import MongoClient

client = MongoClient('mongodb://147.2.212.204:27017/')
prods = client.bz.prods

prod_all = [  'SUSE Linux Enterprise Desktop 12',
              'SUSE Linux Enterprise Desktop 11 SP3',
              'SUSE Linux Enterprise Desktop 11 SP4 (SLED 11 SP4)']
validreso = ['FIXED','UPSTEAM','NORESPONSE','---','MOVED']

#get ONLY wanted data to reduce size of the data
query_limit = {'product':1, 'component':1, 'creator':1, 'resolution':1,
               'severity':1, '_id':0}
result = prods.find({'product':{'$in':prod_all}}, query_limit)
data = [i for i in result]

print(sys.getsizeof(data))

#get all uniq components
comps = list(set([i['component'] for i in data]))

#get count of bug according combination of (product, component, resolution...)
#you can give partially of input args, like
#get_count(comps=['installer', 'kernel'], resolutions=['FIXED'])
def get_count(products=[], comps=[], resolutions=[], creators=[]):
    count = 0
    for d in data:
        if products:
            if d['product'] not in products:
                continue
        if comps:
            if d['component'] not in comps:
                continue
        if resolutions:
            if d['resolution'] not in resolutions:
                continue
        if creators:
            if d['creator'] not in creators:
                continue
        count += 1
    return count

def plt_comp():
    N = len(comps)
    count = 0
    colors = ['r', 'y', 'g']
    fig, ax = plt.subplots()
    for prod in prod_all:
        axis_y = []
        ind = [i*2+count*0.5 for i in range(N)]
        for comp in comps:
            allcomps = get_count([prod,], [comp,])
            if allcomps:
                validcomps = get_count([prod,], [comp,], validreso)
                axis_y.append(validcomps/allcomps)
            else:
                axis_y.append(0)
        
        rects = ax.bar(ind, axis_y, 0.5, color=colors[count])        
        count += 1
    plt.axis([0, 2*N+2, 0, 1.2])
    plt.savefig('foo.png')

if __name__ == '__main__':
    plt_comp()
