from dataclasses import dataclass
from pathlib import Path
from typing import List, Union
import mrcfile
import os
import numpy as np
import logging

from Smartscope.lib.generic_position import parse_mdoc
from Smartscope.lib.Finders.basic_finders import *
from Smartscope.lib.image_manipulations import save_mrc
from .base_image import BaseImage
from .target import Target

logger = logging.getLogger(__name__)




@dataclass
class Montage(BaseImage):

    def __post_init__(self):
        super().__post_init__()
        self.directory.mkdir(exist_ok=True)

    # TODO deprecated in the future
    def load_or_process(self, check_AWS=False, force_process=False):
        if not force_process and self.check_metadata(check_AWS=check_AWS):
            return
        self.metadata = parse_mdoc(self.mdoc, self.is_movie)
        self.build_montage()
        self.read_image()
        self.save_metadata()

    def build_montage(self):

        def piece_pos(piece):
            piece_coord = np.array(piece.PieceCoordinates[0: -1])
            piece_coord_end = piece_coord + np.array([self.header.mx, self.header.my])
            piece_pos = np.array([
                piece_coord, [piece_coord[0], piece_coord_end[1]], 
                piece_coord_end, [piece_coord_end[0], piece_coord[1]]
            ])
            return piece_pos

        def piece_center(piece):
            return np.array([
                np.sum(piece[:, 0]) / piece.shape[0],
                np.sum(piece[:, 1]) / piece.shape[0],
            ])

        with mrcfile.open(self.raw) as mrc:
            self.header = mrc.header
            img = mrc.data
        if int(self.header.mz) == 1:
            self.metadata['PieceCoordinates'] = [[0, 0, 0]]
            self.metadata['piece_limits'] = self.metadata.apply(piece_pos, axis=1)
            self.metadata['piece_center'] = self.metadata.piece_limits.apply(piece_center)
            self._image = img
            self.make_symlink()
            return

        self.metadata['piece_limits'] = self.metadata.apply(piece_pos, axis=1)
        self.metadata['piece_center'] = self.metadata.piece_limits.apply(piece_center)
        montsize = np.array([0, 0])
        for _, piece in enumerate(self.metadata.piece_limits):
            for ind, i in enumerate(piece[2]):
                if i > montsize[ind]:
                    montsize[ind] = i
        montage = np.empty(np.flip(montsize), dtype='int16')
        for ind, piece in enumerate(self.metadata.piece_limits):
            montage[piece[0, 1]: piece[-2, 1], piece[0, 0]: piece[-2, 0]] = img[ind, :, :]
        montage = montage[~np.all(montage == 0, axis=1)]
        montage = montage[:, ~(montage == 0).all(0)]

        self._image = montage

        save_mrc(self.image_path, self._image, self.pixel_size, [0, 0])



def create_targets_from_box(targets: List, montage: BaseImage, target_type: str = 'square'):
    output_targets = []
    if isinstance(targets, tuple):
        targets, labels = targets
    else:
        labels = [None] * len(targets)
    for target, label in zip(targets, labels):
        t = Target(target, quality=label)
        t.convert_image_coords_to_stage(montage)
        t.set_area_radius(target_type)
        output_targets.append(t)

    output_targets.sort(key=lambda x: (x.stage_x, x.stage_y))

    return output_targets

def create_targets_from_center(targets: List, montage: BaseImage):
    output_targets = []

    for target in targets:
        t = Target(target,from_center=True)
        t.convert_image_coords_to_stage(montage)
        output_targets.append(t)

    output_targets.sort(key=lambda x: (x.stage_x, x.stage_y))

    return output_targets



