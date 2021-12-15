# -*- coding: utf-8 -*-
from typing import Any

from . import backend

__all__ = ['probe', 'read']


def probe(mp3: str):
    """
    Returns information on an mp3 file.

    Parameters
    ----------
    mp3: str
        File name of the file to probe

    Returns
    -------
    length: int
        file length in samples
    channels: int
        number of channels
    sample_rate: int
        sample rate in Hz
    """
    if isinstance(mp3, str):
        return backend.probe_file(mp3)
    else:
        raise TypeError("mp3 must be str")


def read(mp3: str, start: int=0, length: int=None,
         out: Any=None):
    """
    Reads floating-point samples from an mp3 file.

    Parameters
    ----------
    mp3: str
        File name of the file to read from
    start: int, optional
        Starting position in samples (default: start at beginning)
    length: int, optional
        Number of samples to read (default: read to end)
    out: bytes-like, optional
        Buffer to write to (default: allocates new numpy array)

    Returns
    -------
    samples: bytes-like or ndarray
        `out` or new ndarray of shape (length, channels) and dtype float32
    """
    if out is None:
        # TODO: move this into backend to avoid opening the file twice,
        # or change the backend to return the opened decoder state
        import numpy as np
        total_length, channels, _ = probe(mp3)
        out = np.empty((length or total_length, channels),
                       dtype=np.float32)
    if isinstance(mp3, str):
        read, channels, sample_rate = backend.read_file(
                mp3, start or 0, length or 0, out)
    else:
        raise TypeError("mp3 must be str")
    if read < len(out):
        out = out[:read]
    return out, sample_rate
