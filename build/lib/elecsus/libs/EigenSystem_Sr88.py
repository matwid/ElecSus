# Copyright 2014 M. A. Zentile, J. Keaveney, L. Weller, D. Whiting,
# C. S. Adams and I. G. Hughes.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Calculates the atomic Hamiltonian for a given Isotope and magnetic field

Modules called:

FundamentalConstants -- fundamental physical constants from CODATA
AtomConstants        -- All isotope and D-line specific constants
sz_lsi               -- 
"""

# Calulates the ground state manifold and the excited state manifold.
# Is called by spectra.py

from scipy.linalg import eig
from numpy import pi, append, transpose, identity

from AtomConstants import *
from FundamentalConstants import *
from sz_lsi import sz, lz, Iz
from fs_hfs import Hfs,Hhfs,Bbhfs

Sg=0
Se=0

class Hamiltonian(object):
    """Functions to create the atomic hamiltonian."""

    def __init__(self, atom, atom_transition, gL, Bfield):
        """Ground and excited state Hamiltonian for an isotope"""


        #Useful quantities to return
        self.ds=int((2*Sg+1)*(2*atom.I+1)) #Dimension of S-term matrix
        self.dp=int(3*(2*Se+1)*(2*atom.I+1)) #Dimension of P-term matrix

        self.groundManifold = self.groundStateManifold(atom.gI,atom.I,atom.As,
                                atom_transition.IsotopeShift,Bfield)
        self.excitedManifold = self.excitedStateManifold(gL,atom.gI,atom.I,
                                atom_transition.Ap,atom_transition.Bp,Bfield)
    
    def groundStateManifold(self,gI,I,A_hyp_coeff,IsotopeShift,Bfield):
        """Function to produce the ground state manifold"""
        As = A_hyp_coeff
        # Add the S-term hyperfine interaction
        S_StateHamiltonian = As*Hhfs(0.0,Sg,I)+IsotopeShift*identity(self.ds)
        Ez = muB*Bfield*1.e-4/(hbar*2.0*pi*1.0e6)
        S_StateHamiltonian += Ez*(gs*sz(0.0,Sg,I)+gI*Iz(0.0,Sg,I)) # Add Zeeman
        EigenSystem = eig(S_StateHamiltonian)
        EigenValues = EigenSystem[0].real
        EigenVectors = EigenSystem[1]
        stateManifold = append([EigenValues],EigenVectors,axis=0)
        sortedManifold = sorted(transpose(stateManifold),key=(lambda i:i[0]))
        return sortedManifold

    def excitedStateManifold(self,gL,gI,I,A_hyp_coeff,B_hyp_coeff,Bfield):
        """Function to produce the excited state manifold"""
        ## S=1 -- full structure
        # The actual value of FS is unimportant.
        FS = 0   # Fine structure splitting, useful for debugging
        Ap = A_hyp_coeff
        Bp = B_hyp_coeff
        # Add P-term fine and hyperfine interactions
        if Bp==0.0:
            P_StateHamiltonian=FS*Hfs(1.0,Se,I)+FS*identity(self.dp)+Ap*Hhfs(1.0,Se,I)
        if Bp!=0.0:
            P_StateHamiltonian=FS*Hfs(1.0,Se,I)-(FS/2.0)*identity(self.dp)+Ap*Hhfs(1.0,Se,I)
            P_StateHamiltonian+=Bp*Bbhfs(1.0,Se,I) # add p state quadrupole
        E=muB*(Bfield*1.0e-4)/(hbar*2.0*pi*1.0e6)
        # Add magnetic interaction
        P_StateHamiltonian+=E*(gL*lz(1.0,Se,I)+gs*sz(1.0,Se,I)+gI*Iz(1.0,Se,I))
        ep=eig(P_StateHamiltonian)
        EigenValues=ep[0].real
        EigenVectors=ep[1]
        stateManifold=append([EigenValues],EigenVectors,axis=0)
        sortedManifold=sorted(transpose(stateManifold),key=(lambda i:i[0]))
        return sortedManifold
