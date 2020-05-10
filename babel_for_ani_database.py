import h5py, os, re, argparse
import numpy as np

'''
class ani_molecule(object):

    def __init__(self, name, coords, species, smile=None, energies_dict = {}):
        self.name = name
        self.coords = coords
        self.species = species
        self.smile = smile
        self.energies_dict = energies_dict

    def output_xyz(self,indexes=[0]):
        
        
        if indexes == -1:
            os.mkdir(self.name)
            os.chdir(self.name)
            for i in range(len(self.coords)): 
                filename = '%s_c%d'%(self.name, i)
                comment = self.smile
                output_xyz(filename, self.species, self.coords[i], comment)
                
            os.chdir('..')
                
        else:
            os.mkdir(self.name)
            os.chdir(self.name)
            for i in indexes: 
                filename = '%s_c%d'%(self.name, i)
                comment = self.smile
                output_xyz(filename, self.species, self.coords[i], comment)
                
            os.chdir('..')
'''


def read_xyz(filename):
    #assume all atoms in the input file are in a same molecule
    #return species list in np.array, coordinates in 2d np.array ((n, 3))
    #comment(second line of the file)
    #if your input file actually contain multiple molecules, you need to
    #find some way to seperate them. Using re to garuantee things found are not crazy
    species = []
    coord = []
    with open(filename, 'r') as f:
        ls = f.readlines()
        for i in range(len(ls)):
            if i==1:
                comment = str(ls[i])
            elif re.match('[a-zA-Z]+\s+(\-|\+)?\d*\.\d+\s+(\-|\+)?\d*\.\d+\s+(\-|\+)?\d*\.\d+\n', ls[i]):
                a = re.split('\s+', ls[i])
                species.append(a.pop(0))
                coord.append(a[:-1])   #delete the last one which is '\n'
            i += 1
    species =  np.array(species).reshape(-1,)            
    coord = np.array(coord).reshape(-1,3).astype(float)
    return species, coord, comment
                

def output_xyz(filename, species, coord, comment=''):
    #filename: the filename of xyz file to be generate
    #species: list of atom species in np.array
    #coord: list of atom coordinates in 2d  np.array ((n, 3))
    #comment: comment you want to write in the second line of xyz file

    num = len(species.reshape(-1,))

    if not (num == coord.shape[0]):
        raise ValueError
    else:
        with open(filename, 'w') as f:
            f.write('%d\n'%(num))
            f.write('%s\n'%(comment))
            for s,l in zip(species,coord):
                f.write("%s          %.5f       %.5f       %.5f\n"%(s,l[0],l[1],l[2]))


def traverse_molecule(d,root=''):
    # some version of ani database have an extra layer of folder before molecules
    # so recursively found all molecules
    # a molecule folder must contain "coordinates"
    if 'coordinates' in list(d[list(d.keys())[0]].keys()):
        for m in list(d.keys()):
            os.mkdir(m)
            os.chdir(m)
            species = np.array(d[m]['species']).astype(str)
            smile = np.array(d[m]['smiles']).astype(str)
            smile = smile[0]
            coords = np.array(d[m]['coordinates'])
            for i in range(len(coords)):
                output_xyz(m+'_c%d.xyz'%(i), species, coords[i], comment = smile)
            os.chdir('..')
    else:
        for m in list(d.keys()):
            traverse_molecule(d[m],root = str(m)) 
            
def limit_recursion(d, remaining, root=''):
    #find all required molecule during traverse
    if 'coordinates' in list(d[list(d.keys())[0]].keys()):
        for m in list(d.keys()):
            if m in list(remaining.keys()):
                os.mkdir(m)
                os.chdir(m)
                species = np.array(d[m]['species']).astype(str)
                smile = np.array(d[m]['smiles']).astype(str)
                smile = smile[0]
                coords = np.array(d[m]['coordinates'])
                if remaining[m] == -1:
                    for i in range(len(coords)):
                        output_xyz(m+'_c%d.xyz'%(i), species, coords[i], comment = smile)
                else:
                    for i in remaining[m]:
                        i = int(i)
                        output_xyz(m+'_c%d.xyz'%(i), species, coords[i], comment = smile)
                        
                del remaining[m]
                os.chdir('..')
                if len(remaining)==0:
                    break
    else:
        for m in list(d.keys()):
            limit_recursion(d[m],remaining,root = str(m))         


def make_h5(filename, root):
    database = h5py.File(filename,"w")
    for item in os.listdir(root):
        if os.path.isdir(os.path.join(root,item)):
            g = database.create_group(item)
            coords = []
            for thing in os.listdir(os.path.join(root,item)):
                species, coord, comment = read_xyz(os.path.join(root,item, thing))
                coords.append(coord)
            species = np.array(species).astype('S1')   #h5py only support S1 for string
            g['species'] = species
            g['coordinates'] = np.array(coords)
    database.close()
            
if __name__ == "__main__":
    '''
    database = h5py.File('ani1_gdb10_ts.h5','r')
    m = ['gdb11_s10-044','gdb11_s10-047']
    indexes = [-1,'0 1 5']
    remaining = dict([(x,y) for x,y in zip(m,indexes)])
    '''
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--xyztoh5', action='store_true', help='change a folder of xyz files into a h5 database')
    parser.add_argument('--xyzfolder',type=str,
                        help=
                        '''
                        path of root folder, assume there are multiple folders inside this root folder
                        each folder consist of multiple xyz files for a same molecule(different conformations)
                        ''')
    parser.add_argument('--newh5name',type=str,help='name of new database')
    
    parser.add_argument('--h5toxyz', action='store_true', help='change some coordinates in a h5 database to xyz file')
    parser.add_argument('--h5path',type=str, help='path of the h5 database')
    
    parser.add_argument('--convertall', action='store_true', help='convert every coordinates inside the database into xyz file, seperately stored into different folders named by the molecule')
    
    parser.add_argument('--convertsingle', action='store_true', help='convert some conformations of one molecule into xyz file')
    parser.add_argument('--molecule', type=str, help='name of the molecule')
    parser.add_argument('--indexes',nargs='+', type=int, help='indexes of coordinates, seperate by space')

    parser.add_argument('--convertselected', action='store_true', help='convert some conformations of selected molecules into xyz files, a name list is required')
    parser.add_argument('--namelist', type=str, help='path of namelist file, each line in namelist should look like: name1;index1 index2 index3\n')

    
    

    args = parser.parse_args()
    
    if args.xyztoh5:
        make_h5(args.newh5name, args.xyzfolder)

    if args.h5toxyz:
        database = h5py.File(args.h5path,'r')
        if args.convertall:
            traverse_molecule(database)
            
        if args.convertsingle:
            ms = args.molecule
            indexes = args.indexes
            remaining = {ms:indexes}
            limit_recursion(database, remaining)
        if args.convertselected:
            remaining = {}
            with open(args.namelist,'r') as f:
                for l in f.readlines():
                    m = l.split(';')[0]
                    indexes = l.split(';')[1].split(' ')                  
                    remaining[m] = indexes
            limit_recursion(database, remaining)
