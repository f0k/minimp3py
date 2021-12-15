minimp3py
=========

Python bindings for [minimp3](https://github.com/lieff/minimp3).

Installation
------------
```bash
CFLAGS='-O3 -march=native' pip install https://github.com/f0k/minimp3py/archive/master.zip
```
The `CFLAGS` are important to compile with SSE/NEON support if your CPU has it.

Usage
-----
```python
import minimp3py

# query file information
length, channels, sample_rate = minimp3py.probe('somefile.mp3')

# read a full file as a float32 numpy array
wav, sample_rate = minimp3py.read('somefile.mp3')

# read the eleventh second of a 48 kHz stereo file into an existing numpy array
import numpy as np
wav = np.empty((48000, 2), dtype=np.float32)
wav, sample_rate = minimp3py.read('somefile.mp3', start=48000 * 10,
                                  length=48000, out=wav)
```

Status
------
This is just a quick stab at it. In the long run I'd like to add support for
reading from a memory buffer and a file-like Python object, and an `open()`
call to open an mp3 file with `seek()` and `read()` methods for streaming in
arbitrary-sized chunks. It is already useable and 2-5 times faster than ffmpeg.

Why
---
The existing Python bindings [pyminimp3](https://github.com/pyminimp3/pyminimp3)
and [pyfastmp3decoder](https://github.com/neonbjb/pyfastmp3decoder) do not work
correctly and do not support seeking, respectively.
