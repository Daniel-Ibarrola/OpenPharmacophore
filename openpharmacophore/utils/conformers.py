from rdkit import Chem
from rdkit.Chem import AllChem
from openpharmacophore._private_tools.exceptions import NoConformersError, OpenPharmacophoreTypeError, \
    OpenPharmacophoreValueError


def generate_conformers(molecule: Chem.Mol, n_conformers: int,
                        random_seed: int = -1, alignment: bool = False) -> Chem.Mol:
    """Generate conformers for a molecule
    
        Parameters
        ----------
        molecule : rdkit.Mol
            Molecule for which conformers will be generated.
        
        n_conformers: int
            Number of conformers to generate

        random_seed : float or int, optional 
            Random seed to use.

        alignment : bool, optional
            If true generated conformers will be aligned (Default: False).
        
        Returns
        -------
        molecule : rdkit.Mol
            Molecule with conformers.
    
    """
    molecule = Chem.AddHs(molecule)  # Add hydrogens to generate realistic geometries
    AllChem.EmbedMultipleConfs(molecule, numConfs=n_conformers, randomSeed=random_seed)

    if alignment:
        AllChem.AlignMolConformers(molecule)
    return molecule


def conformer_energy(molecule: Chem.Mol, conformer_id: int = 0,
                     forcefield: str = "UFF") -> float:
    """ Get the energy of a conformer in a molecule using the universal force-field (UFF) force-field
        or the merck molecular force-field (MMFF) force-field.

        Parameters
        ----------
        molecule : rdkit.Chem.Mol
            The molecule which energy will be calculated.

        conformer_id: int
            The id of the conformer whose energy will be computed,

        forcefield : {"UFF", "MMFF"}, optional.
            The force-field that will be used to calculate the energy
            (default="UFF").

        Returns
        -------
        float
            The energy of the molecule.
    """
    if molecule.GetNumConformers() == 0:
        raise NoConformersError("Molecule must have at least one conformer")

    if forcefield == "UFF":
        ff = AllChem.UFFGetMoleculeForceField(molecule, confId=conformer_id)
    elif forcefield == "MMFF":
        props = AllChem.MMFFGetMoleculeProperties(molecule)
        ff = AllChem.MMFFGetMoleculeForceField(molecule, props, confId=conformer_id)

    return ff.CalcEnergy()
