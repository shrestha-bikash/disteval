from math import sqrt
import numpy as np
import os
import sys
import seaborn as sns
import matplotlib.pyplot as plt


mynpy = sys.argv[1]
mypdb = sys.argv[2]
myimg = sys.argv[3]

valid_amino_acids = {
    'LLP': 'K', 'TPO': 'T', 'CSS': 'C', 'OCS': 'C', 'CSO': 'C', 'PCA': 'E', 'KCX': 'K', \
    'CME': 'C', 'MLY': 'K', 'SEP': 'S', 'CSX': 'C', 'CSD': 'C', 'MSE': 'M', \
    'ALA': 'A', 'ASN': 'N', 'CYS': 'C', 'GLN': 'Q', 'HIS': 'H', 'LEU': 'L', \
    'MET': 'M', 'MHO': 'M', 'PRO': 'P', 'THR': 'T', 'TYR': 'Y', 'ARG': 'R', 'ASP': 'D', \
    'GLU': 'E', 'GLY': 'G', 'ILE': 'I', 'LYS': 'K', 'PHE': 'F', 'SER': 'S', \
    'TRP': 'W', 'VAL': 'V', 'SEC': 'U'
    }

def check_pdb_valid_row(valid_amino_acids, l):
    if (get_pdb_rname(l) in valid_amino_acids.keys()) and (l.startswith('ATOM') or l.startswith('HETA')):
        return True
    return False

def get_pdb_atom_name(l):
    return l[12: 16].strip()

def get_pdb_rnum(l):
    return int(l[22: 27].strip())

def get_pdb_rname(l):
    return l[17: 20].strip()

def get_pdb_xyz_cb(lines):
    xyz = {}
    for l in lines:
        if get_pdb_atom_name(l) == 'CB':
            xyz[get_pdb_rnum(l)] = (float(l[30:38].strip()), float(l[38:46].strip()), float(l[46:54].strip()))
    for l in lines:
        if (get_pdb_rnum(l) not in xyz) and get_pdb_atom_name(l) == 'CA':
            xyz[get_pdb_rnum(l)] = (float(l[30:38].strip()), float(l[38:46].strip()), float(l[46:54].strip()))
    return xyz

def get_pdb_xyz_ca(lines):
    xyz = {}
    for l in lines:
        if get_pdb_atom_name(l) == 'CA':
            xyz[get_pdb_rnum(l)] = (float(l[30:38].strip()), float(l[38:46].strip()), float(l[46:54].strip()))
    return xyz

def get_dist_maps(valid_amino_acids, file_pdb):
    f = open(file_pdb, mode = 'r')
    flines = f.read()
    f.close()
    lines = flines.splitlines()
    templines = flines.splitlines()
    for l in templines:
        if not l.startswith('ATOM'):
            lines.remove(l)
    rnum_rnames = {}
    for l in lines:
        atom = get_pdb_atom_name(l)
        if atom != 'CA':
            continue
        #if int(get_pdb_rnum(l)) in rnum_rnames:
            #warnings.warn ('Warning!! ' + file_pdb + ' - multiple CA rows - rnum = ' + str(get_pdb_rnum(l)))
        if not get_pdb_rname(l) in valid_amino_acids.keys():
            print ('' + get_pdb_rname(l) + ' is unknown amino acid in ' + l)
            sys.exit(1)
        rnum_rnames[int(get_pdb_rnum(l))] = valid_amino_acids[get_pdb_rname(l)]
    seq = ""
    for i in range(max(rnum_rnames.keys())):
        if i+1 not in rnum_rnames:
            print (rnum_rnames)
            print ('Error! ' + file_pdb + ' ! residue not defined for rnum = ' + str(i+1))
            sys.exit (1)
        seq = seq + rnum_rnames[i+1]
    L = len(seq)
    xyz_cb = get_pdb_xyz_cb(lines)
    if len(xyz_cb) != L:
        print(rnum_rnames)
        for i in range(L):
            if i+1 not in xyz_cb:
                print('XYZ not defined for ' + str(i+1))
        print ('Error! ' + file_pdb + ' Something went wrong - len of cbxyz != seqlen!! ' + str(len(xyz_cb)) + ' ' +  str(L))
        sys.exit(1)
    cb_map = np.zeros((L, L))
    for r1 in sorted(xyz_cb):
        (a, b, c) = xyz_cb[r1]
        for r2 in sorted(xyz_cb):
            (p, q, r) = xyz_cb[r2]
            cb_map[r1 - 1, r2 - 1] = sqrt((a-p)**2+(b-q)**2+(c-r)**2)
    xyz_ca = get_pdb_xyz_ca(lines)
    if len(xyz_ca) != L:
        print ('Something went wrong - len of cbxyz != seqlen!! ' + str(len(xyz_ca)) + ' ' +  str(L))
        sys.exit(1)
    ca_map = np.zeros((L, L))
    for r1 in sorted(xyz_ca):
        (a, b, c) = xyz_ca[r1]
        for r2 in sorted(xyz_ca):
            (p, q, r) = xyz_ca[r2]
            ca_map[r1 - 1, r2 - 1] = sqrt((a-p)**2+(b-q)**2+(c-r)**2)
    
    return L, seq, cb_map, ca_map


def plot_dl_vs_3dmodel(mynpy, mypdb):
    # target = 'T1024'
    # ! wget http://deep.cs.umsl.edu/prayogrealdistance/jobs/T1025/T1025.realdist.npy
    # os.system('wget http://deep.cs.umsl.edu/prayogrealdistance/jobs/' + target + '/' + target + '.realdist.npy')

    # pdbFile = 'S_00000010.pdb'
    print ('both names: ', mynpy, mypdb)

    PredictedMAP = np.load(mynpy)
    PredictedMAP[PredictedMAP > 20] = 20
    for i in range(len(PredictedMAP)):
        for j in range(i, len(PredictedMAP)):
            PredictedMAP[j][i] = PredictedMAP[i][j]

    (L, seq, cb_map, ca_map) = get_dist_maps(valid_amino_acids, mypdb)
    cb_map[cb_map > 20] = 20

    for i in range(L):
        for j in range(i, L):
            PredictedMAP[i, j] = np.nan

    for i in range(L):
        for j in range(0, i):
            cb_map[i, j] = np.nan

    plt.figure(figsize=(6, 5))

    # 'PredictedMAP' is the output of the deep learning model that predicts distance map
    plt.imshow(PredictedMAP, cmap='Spectral')
    x = plt.colorbar()
    x.set_label('Distance map (output of DL model)')
    plt.title('DL output vs 3D model')
    # 'cb_map' is the distance map obtained from the 3D model
    plt.imshow(cb_map, cmap='RdYlGn')
    y = plt.colorbar()
    y.set_label('Distance obtained from predicted 3D model')
    plt.savefig(myimg)
    os.system(f'mv {myimg} static/images/')
    
    # path = f'static/images/{myimg}'
    # return path

plot_dl_vs_3dmodel(mynpy, mypdb)