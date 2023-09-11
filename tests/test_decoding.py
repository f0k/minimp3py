import os
import wave

import pytest
import numpy as np

import minimp3py


@pytest.fixture(params=["48000_1.mp3", "32000_2.mp3", "empty.mp3"],
                scope="module")
def filename(request):
    """Returns one of three possible mp3 file names"""
    return os.path.join(os.path.dirname(__file__), request.param)


@pytest.fixture(params=["filename", "bytes", "memmap"],
                scope="module")
def mp3(filename, request):
    """Returns mp3 data for the given file in one of three possible forms"""
    if request.param == "filename":
        return filename
    elif request.param == "bytes":
        with open(filename, mode='rb') as f:
            return f.read()
    elif request.param == "memmap":
        return np.memmap(filename, mode='r')


@pytest.fixture(scope="module")
def wav(filename):
    """Returns reference int16 samples and sample rate for the given file"""
    with wave.open(filename[:-3] + 'wav', mode='r') as f:
        samples = f.getnframes()
        sample_rate = f.getframerate()
        channels = f.getnchannels()
        data = f.readframes(-1)
    pcm = np.frombuffer(data, dtype=np.int16).reshape(samples, channels)
    return pcm, sample_rate


def f32_to_int16(pcm):
    """Converts float32 samples to int16 samples"""
    return np.clip(pcm * 32768, -32767, 32768).astype(np.int16)


def almost_same(pcm1, pcm2, max_diff=1, max_count=6):
    """
    Tells whether two int16 arrays differ by at most `max_diff` in at most
    `max_count` samples. Required to cater for differences in SSE version.
    """
    diff = abs(pcm1 - pcm2)
    return ((diff.max(initial=0) <= max_diff) and
            (np.count_nonzero(diff) <= max_count))


def test_probe(mp3, wav):
    """Tests whether minimp3py.probe() returns the correct information"""
    samples, channels, sample_rate = minimp3py.probe(mp3)
    ref_pcm, ref_rate = wav
    assert samples == len(ref_pcm)
    assert channels == ref_pcm.shape[1]
    assert sample_rate == ref_rate


@pytest.mark.parametrize("prealloc", [False, np.ndarray, memoryview])
@pytest.mark.parametrize("length", [None, 0, 16000, 100000])
@pytest.mark.parametrize("start", [None, 0, 24000, 100000])
def test_read(mp3, wav, start, length, prealloc):
    """
    Tests whether minimp3py.read() works as intended for different ways of
    passing MP3 data, different excerpts, and different output allocations
    """
    ref_pcm, ref_rate = wav
    ref_channels = ref_pcm.shape[1]
    # prepare or skip keyword arguments start, length, and out
    kwargs = {}
    if start is not None:
        kwargs['start'] = start
        ref_pcm = ref_pcm[start:]
    if length is not None:
        kwargs['length'] = length
        ref_pcm = ref_pcm[:length or None]
    if prealloc:
        # prepare an output large enough to hold the expected results
        prealloc_length = (length or len(ref_pcm))
        if prealloc is np.ndarray:
            kwargs['out'] = np.empty((prealloc_length, ref_channels),
                                     dtype=np.float32)
        elif prealloc is memoryview:
            kwargs['out'] = memoryview(bytearray(prealloc_length * ref_channels
                                                 * 4))
    # decode the mp3
    pcm, rate = minimp3py.read(mp3, **kwargs)
    # verify the results
    if prealloc:
        if prealloc_length <= len(ref_pcm):
            # should directly return out
            assert pcm is kwargs['out']
        else:
            # should return a view into the beginning of out
            pcm_ptr = np.byte_bounds(np.frombuffer(pcm,
                                                   dtype=np.uint8))[0]
            out_ptr = np.byte_bounds(np.frombuffer(kwargs['out'],
                                                   dtype=np.uint8))[0]
            assert pcm_ptr == out_ptr
    assert rate == ref_rate
    if not isinstance(pcm, np.ndarray):
        # if we preallocated a non-numpy-array, convert it so we can compare it
        pcm = np.frombuffer(pcm, dtype=np.float32).reshape(ref_pcm.shape)
    assert pcm.shape == ref_pcm.shape
    assert almost_same(f32_to_int16(pcm), ref_pcm)


def test_read_shortbuffer(mp3, wav, start=1500, length=1000, out_length=500):
    """Test providing a shorter buffer than required to fulfil the request"""
    # expected result: decoding does not fail, but fill the available buffer
    ref_pcm, ref_rate = wav
    ref_channels = ref_pcm.shape[1]
    ref_pcm = ref_pcm[start:start + out_length]
    out = bytearray(out_length * ref_channels * 4)
    pcm, rate = minimp3py.read(mp3, start=start, length=length, out=out)
    if out_length <= len(ref_pcm):
        assert pcm is out
    assert rate == ref_rate
    pcm = np.frombuffer(pcm, dtype=np.float32).reshape(ref_pcm.shape)
    assert almost_same(f32_to_int16(pcm), ref_pcm)


@pytest.fixture(params=["id3v2-only.mp3", "notexisting.mp3"])
def mp3_fail(request):
    """Returns one of two possible broken mp3 file names"""
    return os.path.join(os.path.dirname(__file__), request.param)


def test_probe_fail(mp3_fail):
    """Test whether minimp3py.probe() fails for a broken mp3"""
    with pytest.raises(minimp3py.Mp3Error):
        minimp3py.probe(mp3_fail)


def test_read_fail(mp3_fail):
    """Test whether minimp3py.read() fails for a broken mp3"""
    with pytest.raises(minimp3py.Mp3Error):
        minimp3py.read(mp3_fail)
