from abc import ABCMeta, abstractmethod


class Pharmacophore(metaclass=ABCMeta):
    """ Abstract base class for pharmacophores.

        Parent class of LigandBasedPharmacophore and StructureBasedPharmacophore.
    """

    @property
    @abstractmethod
    def pharmacophoric_points(self):
        pass

    @property
    @abstractmethod
    def num_points(self, *args, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def from_file(cls, file_name):
        pass

    @abstractmethod
    def add_point(self, *args, **kwargs):
        pass

    @abstractmethod
    def remove_point(self, *args, **kwargs):
        pass

    @abstractmethod
    def remove_picked_point(self, *args, **kwargs):
        pass

    @abstractmethod
    def edit_picked_point(self, *args, **kwargs):
        pass

    @abstractmethod
    def add_point_in_picked_location(self, *args, **kwargs):
        pass

    @abstractmethod
    def to_json(self, *args, **kwargs):
        pass

    @abstractmethod
    def add_to_view(self, *args, **kwargs):
        pass

    @abstractmethod
    def show(self, *args, **kwargs):
        pass

    @classmethod
    def from_pharmacophoric_point_list(cls, points):
        pass

    def to_ligand_scout(self, file_name):
        pass

    def to_moe(self, file_name):
        pass

    def to_pharmagist(self, file_name):
        pass

    def to_rdkit(self):
        pass

    def distance_matrix(self):
        pass
