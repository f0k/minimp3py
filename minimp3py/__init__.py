# -*- coding: utf-8 -*-
from typing import Any

from . import backend
from .backend import Mp3Error

__all__ = ['probe', 'read', 'Mp3Error']


def probe(mp3: Any):
    """
    Returns information on an mp3 file.

    Parameters
    ----------
    mp3: str or bytes-like
        File name of the file to probe, or buffer holding mp3 file data

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
        return backend.probe_buffer(mp3)


def read(mp3: Any, start: int=0, length: int=None,
         out: Any=None):
    """
    Reads floating-point samples from an mp3 file.

    Parameters
    ----------
    mp3: str or bytes-like
        File name of the file to probe, or buffer holding mp3 file data
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
        available = max(0, total_length - (start or 0))
        out = np.empty((min(available, length) if length else available,
                        channels),
                       dtype=np.float32)
    if isinstance(mp3, str):
        read_fn = backend.read_file
    else:
        read_fn = backend.read_buffer
    read, channels, sample_rate = read_fn(mp3, start or 0, length or 0, out)
    # crop output if needed, agnostic to output type, dtype and shape
    bytes_read = read * channels * 4
    with memoryview(out) as m:
        bytes_out = m.nbytes
    if bytes_read < bytes_out:
        bytes_per_item = bytes_out // len(out)
        out = out[:bytes_read // bytes_per_item]
    return out, sample_rate
