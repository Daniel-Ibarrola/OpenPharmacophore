import pyunitwizard as puw
import nglview as nv
from openpharmacophore._private_tools.exceptions import InvalidFeatureError, InvalidFileError
# from openpharmacophore.pharmacophoric_elements.features.color_palettes import get_color_from_palette_for_feature

from rdkit import Geometry, RDLogger
from rdkit.Chem import ChemicalFeatures
from rdkit.Chem.Pharm3D import Pharmacophore as rdkitPharmacophore
RDLogger.DisableLog('rdApp.*') # Disable rdkit warnings

class Pharmacophore():

    """ Native object for pharmacophores.

    Parent class of LigandBasedPharmacophore, StrucutredBasedPharmacophore and Dynophore
    Openpharmacophore native class to store pharmacophoric models.
    A pharmacophore can be constructed from a list of elements or from a file.

    Parameters
    ----------

    elements : :obj:`list` of :obj:`openpharmacophore.pharmacoforic_elements`
        List of pharmacophoric elements

    molecular_system : :obj:`molsysmt.MolSys`
        Molecular system from which this pharmacophore was extracted.
    
    fname : str (optional)
        Name of file with the pharmacophore object.

    Attributes
    ----------

    elements : :obj:`list` of :obj:`openpharmacophore.pharmacoforic_elements`
        List of pharmacophoric elements

    n_elements : int
        Number of pharmacophoric elements

    extractor : :obj:`openpharmacophore.extractors`
        Extractor object used to elucidate the pharmacophore

    molecular_system : :obj:`molsysmt.MolSys`
        Molecular system from which this pharmacophore was extracted.

    """
    def __init__(self, elements=[], molecular_system=None):

        self.elements = elements
        self.n_elements = len(elements)
        self.molecular_system = molecular_system
        self.extractor = None
    
    @classmethod
    def from_file(cls, file_name, **kwargs):
        """
        Class method to load a pharmacohpore from a file.
        Sets the Pharmacophore atributes according to the file.

        Parameters
        ---------
        file_name: str
            Name of the file containing the pharmacophore

        """
        fextension = file_name.split(".")[-1]
        if fextension == "json":
            from openpharmacophore.io import from_pharmer
            if kwargs:
                load_mol_sys = kwargs["load_mol_sys"]
            else:
                load_mol_sys = False
            points, mol_sys = from_pharmer(file_name, load_mol_sys)

        elif fextension == "ph4":
            from openpharmacophore.io.moe import from_moe
            points = from_moe(file_name)
            mol_sys = None

        elif fextension == "pml":
            from openpharmacophore.io import from_ligandscout
            points = from_ligandscout(file_name)
            mol_sys = None

        elif fextension == "mol2":
            from openpharmacophore.io.pharmagist import read_pharmagist
            if kwargs:
                ph_index = kwargs["index"]
            else:
                ph_index = 0
            points = read_pharmagist(file_name, pharmacophore_index=ph_index)
            mol_sys = None
        
        else:
            raise InvalidFileError(f"Invalid file type, \"{file_name}\" is not a supported file format")
        
        return cls(points, mol_sys)    
        
    def add_to_NGLView(self, view, palette='openpharmacophore'):

        """Adding the pharmacophore representation to a view (NGLWidget) from NGLView.

        Each pharmacophoric element is added to the NGLWidget as a new component.

        Parameters
        ----------
        view: :obj: `nglview.NGLWidget`
            View as NGLView widget where the representation of the pharmacophore is going to be
            added.
        palette: :obj: `str`, dict
            Color palette name or dictionary. (Default: 'openpharmacophore')

        Note
        ----
        Nothing is returned. The `view` object is modified in place.
        """

        if palette == "openpharmacophore":
            feature_colors = {
                'positive charge': (0.12, 0.36, 0.52), # Blue
                'negative charge': (0.90, 0.30, 0.24),  # Red
                'hb acceptor': (0.90, 0.30, 0.24),  # Red
                'hb donor': (0.13, 0.56, 0.30), # Green
                'included volume': (0, 0, 0), # Black,
                'excluded volume': (0, 0, 0), # Black
                'hydrophobicity': (1, 0.9, 0),  # Yellow
                'aromatic ring': (1, 0.9, 0),  # Yellow
            }
        else:
            raise NotImplementedError

        # TODO: Openpharmacophore palette is not working

        for i, element in enumerate(self.elements):
            # Add Spheres
            center = puw.get_value(element.center, to_unit="angstroms").tolist()
            radius = puw.get_value(element.radius, to_unit="angstroms")
            # feature_color = get_color_from_palette_for_feature(element.feature_name, color_palette=palette)
            feature_color = feature_colors[element.feature_name]
            label = f"{element.feature_name}_{i}"
            view.shape.add_sphere(center, feature_color, radius, label)
            # Add vectors
            if element.has_direction:
                label = f"{element.feature_name}_vector"
                if element.feature_name == "hb acceptor":
                    end_arrow = puw.get_value(element.center - 2 * radius * puw.quantity(element.direction, "angstroms"), to_unit='angstroms').tolist()
                    view.shape.add_arrow(end_arrow, center, feature_color, 0.2, label)
                else:
                    end_arrow = puw.get_value(element.center + 2 * radius * puw.quantity(element.direction, "angstroms"), to_unit='angstroms').tolist()
                    view.shape.add_arrow(center, end_arrow, feature_color, 0.2, label)
                   
    def show(self, palette='openpharmacophore'):

        """Showing the pharmacophore model together with the molecular system from with it was
        extracted as a new view (NGLWidget) from NGLView.

        Parameters
        ----------
        palette: :obj: `str`, dict
            Color palette name or dictionary. (Default: 'openpharmacophore')

        Returns
        -------
        nglview.NGLWidget
            An nglview.NGLWidget is returned with the 'view' of the pharmacophoric model and the
            molecular system used to elucidate it.

        """

        view = nv.NGLWidget()
        self.add_to_NGLView(view, palette=palette)

        return view

    def add_element(self, pharmacophoric_element):

        """Adding a new element to the pharmacophore.

        Parameters
        ----------
        pharmacophoric_element: :obj: `openpharmacohore.pharmacophoric_elements`
            Native object for pharmacophoric elements of any class defined in the module
            `openpharmacophore.pharmacophoric_elements`

        Returns
        -------

            The pharmacophoric element given as input argument is added to the pharmacophore
            as a new entry of the list `elements`.

        """

        self.elements.append(pharmacophoric_element)
        self.n_elements +=1
    
    def remove_element(self, element_indx):

        """Remove an element from the pharmacophore.

        Parameters
        ----------
        element_inx: int
            Index of the element to be removed

        Returns
        -------
            The pharmacophoric element given as input argument is removed from the pharmacophore.
        """

        self.elements.pop(element_indx)
        self.n_elements -=1

    def remove_feature(self, feat_type):

        """Remove an especific feature type from the pharmacophore elements list

        Parameters
        ----------
        feat_type: str
            Name or type of the feature to be removed

        Returns
        ------
            The pharmacophoric elements of the feature type given as input argument 
            are removed from the pharmacophore.
        """
        feats = [
            "aromatic ring",
            "hydrophobicity",
            "hb acceptor",
            "hb donor",
            "included volume",
            "excluded volume",
            "positive charge",
            "negative charge",
        ]    
        if feat_type not in feats:
            raise InvalidFeatureError(f"Cannot remove feature. \"{feat_type}\" is not a valid feature type")
        temp_elements = [element for element in self.elements if element.feature_name != feat_type]
        if len(temp_elements) == self.n_elements: # No element was removed
            raise InvalidFeatureError(f"Cannot remove feature. The pharmacophore does not contain any {feat_type}")
        self.elements = temp_elements
        self.n_elements = len(self.elements)

    def _reset(self):

        """Private method to reset all attributes to default values.

        Note
        ----

           Nothing is returned. All attributes are set to default values.

        """

        self.elements=[]
        self.n_elements=0
        self.extractor=None
        self.molecular_system=None

    def to_ligandscout(self, file_name):

        """Method to export the pharmacophore to the ligandscout compatible format.

        Parameters
        ----------
        file_name: str
            Name of file to be written with the ligandscout format of the pharmacophore.

        Note
        ----
        Nothing is returned. A new file is written.

        """
        from openpharmacophore.io import to_ligandscout as _to_ligandscout
        return _to_ligandscout(self, file_name=file_name)

    def to_pharmer(self, file_name):

        """Method to export the pharmacophore to the pharmer compatible format.

        Parameters
        ----------
        file_name: str
            Name of file to be written with the pharmer format of the pharmacophore.

        Note
        ----

            Nothing is returned. A new file is written.

        """
        from openpharmacophore.io import to_pharmer as _to_pharmer
        return _to_pharmer(self, file_name=file_name)

    def to_pharmagist(self, file_name):

        """Method to export the pharmacophore to the pharmagist compatible format.

        Parameters
        ----------
        file_name: str
            Name of file to be written with the pharmagist format of the pharmacophore.

        Note
        ----

            Nothing is returned. A new file is written.

        """
        from openpharmacophore.io.pharmagist import to_pharmagist as _to_pharmagist
        return _to_pharmagist(self, file_name=file_name)
    
    def to_moe(self, file_name):

        """Method to export the pharmacophore to the MOE compatible format.

        Parameters
        ----------
        file_name: str
            Name of file to be written with the MOE format of the pharmacophore.

        Note
        ----

            Nothing is returned. A new file is written.

        """
        from openpharmacophore.io.moe import to_moe as _to_moe
        return _to_moe(self, file_name=file_name)
    
    def to_rdkit(self):
        """ Returns an rdkit pharmacophore with the elements from the original
            pharmacophore. rdkit pharmacophores do not store the elements radii,
            so they are returned as well.

            Returns
            -------
            rdkit_pharmacophore: rdkit.Chem.Pharm3D.Pharmacophore
                The rdkit pharmacophore.

            radii: list of float
                List with the radius ina angstroms of each pharmacophoric point.
        """
        rdkit_element_name = { # dictionary to map openpharmacophore feature names to rdkit feature names
        "aromatic ring": "Aromatic",
        "hydrophobicity": "Hydrophobe",
        "hb acceptor": "Acceptor",
        "hb donor": "Donor",
        "positive charge": "PosIonizable",
        "negative charge": "NegIonizable",
        }

        points = []
        radii = []

        for element in self.elements:
            feat_name = rdkit_element_name[element.feature_name]
            center = puw.get_value(element.center, to_unit="angstroms")
            center = Geometry.Point3D(center[0], center[1], center[2])
            points.append(ChemicalFeatures.FreeChemicalFeature(
                feat_name,
                center
            ))
            radius = puw.get_value(element.radius, to_unit="angstroms")
            radii.append(radius)

        rdkit_pharmacophore = rdkitPharmacophore.Pharmacophore(points)
        return rdkit_pharmacophore, radii
    
    def __repr__(self):
        return f"{self.__class__.__name__}(n_elements: {self.n_elements})"

    