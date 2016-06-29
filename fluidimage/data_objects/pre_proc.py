"""Preprocessing data objects
=============================

.. autoclass:: ArraySeries
   :members:
   :private-members:

.. autoclass:: PreprocResults
   :members:
   :private-members:

"""

import os
import h5py
import logging

from fluidimage import imsave, imsave_h5
from .piv import ArrayCouple, LightPIVResults
from .. import ParamContainer


logger = logging.getLogger('fluidimage')


class ArraySerie(ArrayCouple):
    def __init__(
            self, names=None, arrays=None, serie=None,
            ind_serie=0, nb_series=1,
            str_path=None, hdf5_parent=None):

        if str_path is not None:
            self._load(path=str_path)
            return

        if hdf5_parent is not None:
            self._load(hdf5_object=hdf5_parent['serie'])
            return

        if serie is not None:
            names = serie.get_name_files()
            paths = serie.get_path_files()
            self.paths = tuple(os.path.abspath(p) for p in paths)

            if arrays is None:
                arrays = serie.get_arrays()

        self.ind_serie = ind_serie
        self.nb_series = nb_series
        self.names = tuple(names)
        self.arrays = tuple(arrays)
        self.serie = serie

    def _clear_data(self):
        self.arrays = tuple()

    def save(self, path=None, hdf5_parent=None):
        if path is not None:
            raise NotImplementedError

        if not isinstance(hdf5_parent, (h5py.File,)):
            raise NotImplementedError

        hdf5_parent.create_group('serie')
        group = hdf5_parent['serie']
        group.attrs['names'] = self.names
        group.attrs['paths'] = self.paths


class PreprocResults(LightPIVResults):

    def __init__(self, serie=None, params=None,
                 str_path=None, hdf5_object=None):

        self._keys_to_be_saved = ['data']
        if hdf5_object is not None:
            if serie is not None:
                self.serie = serie

            if params is not None:
                self.params = params

            self._load_from_hdf5_object(hdf5_object)
            return

        if str_path is not None:
            self._load(str_path)
            return

        self.serie = serie
        self.params = params
        self.data = {}

    def _clear_data(self):
        self.data = {}

    def save(self, path=None):
        out_format = self.params.saving.format

        for k, v in self.data.items():
            path_file = os.path.join(path, k)
            if out_format == 'img':
                imsave(path_file, v, as_int=True)
            elif out_format == 'h5':
                attrs = {'class_name': 'PreprocResults',
                         'module_name': self.__module__}
                imsave_h5(path_file, v, self.params, attrs, as_int=True)
            else:
                # Try to save in formats supported by PIL.Image
                imsave(path_file, v, format=out_format, as_int=True)

        self._clear_data()
        return self
