#define PY_SSIZE_T_CLEAN
#include <Python.h>
#define MINIMP3_IMPLEMENTATION
#define MINIMP3_FLOAT_OUTPUT
#include "minimp3_ex.h"

static PyObject *
probe_file(PyObject *self, PyObject *args)
{
    const char *filename;
    mp3dec_ex_t dec;
    PyObject *result;

    if (!PyArg_ParseTuple(args, "s", &filename))
    {
        return NULL;
    }
    if (mp3dec_ex_open(&dec, filename, MP3D_SEEK_TO_SAMPLE))
    {
        // possibly use different exception type,
        // see https://docs.python.org/3/extending/extending.html#intermezzo-errors-and-exceptions
        PyErr_SetString(PyExc_RuntimeError, "File could not be opened or understood");
        return NULL;
    }
    result = PyTuple_Pack(3,
                          PyLong_FromLong(dec.samples / dec.info.channels),
                          PyLong_FromLong(dec.info.channels),
                          PyLong_FromLong(dec.info.hz));
    mp3dec_ex_close(&dec);
    return result;
}

static PyObject *
read_file(PyObject *self, PyObject *args)
{
    const char *filename;
    long long start, length;
    PyObject *outobj;
    Py_buffer out;
    mp3dec_ex_t dec;
    size_t max_read;
    size_t read;
    PyObject *result;

    if (!PyArg_ParseTuple(args, "sLLO", &filename, &start, &length, &outobj))
    {
        return NULL;
    }
    if (PyObject_GetBuffer(outobj, &out, PyBUF_WRITABLE | PyBUF_C_CONTIGUOUS) == -1)
    {
        return NULL;
    }

    if (mp3dec_ex_open(&dec, filename, MP3D_SEEK_TO_SAMPLE | MP3D_DO_NOT_SCAN))
    {
        PyErr_SetString(PyExc_RuntimeError, "File could not be opened or understood");
        PyBuffer_Release(&out);
        return NULL;
    }

    if (start)
    {
        if (mp3dec_ex_seek(&dec, start * dec.info.channels))
        {
            PyErr_SetString(PyExc_RuntimeError, "Could not seek to start position");
            PyBuffer_Release(&out);
            mp3dec_ex_close(&dec);
            return NULL;
        }
    }

    max_read = out.len / sizeof(mp3d_sample_t);
    if (length)
    {
        if (length * dec.info.channels < max_read)
        {
            max_read = length * dec.info.channels;
        }
    }
    read = mp3dec_ex_read(&dec, out.buf, max_read);
    PyBuffer_Release(&out);
    if (read != max_read)
    {
        if (dec.last_error)
        {
            PyErr_Format(PyExc_RuntimeError, "Decoding error %d", dec.last_error);
            mp3dec_ex_close(&dec);
            return NULL;
        }
    }

    result = PyTuple_Pack(3,
                          PyLong_FromLong(read),
                          PyLong_FromLong(dec.info.channels),
                          PyLong_FromLong(dec.info.hz));
    mp3dec_ex_close(&dec);
    return result;
}

static PyMethodDef methods[] = {
    {"probe_file", probe_file, METH_VARARGS,
     "probe_file(file_name: str) -> (length: int, channels: int, sample_rate: int)\n\n"
     "Open the file of the given name, return its length, channels, and sample rate."},
    {"read_file", read_file, METH_VARARGS,
     "read_file(file_name: str, start: int, length: int, out: bytes_like) -> (length: int, channels: int, sample_rate: int)\n\n"
     "Open the file of the given name, seek to the given starting position, "
     "and read the given number of samples into the given output buffer. "
     "Returns the number of samples read, the number of channels, and the sample rate."},
     {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "backend",
    "Backend of minimp3 Python bindings.",
    -1,
    methods
};

PyMODINIT_FUNC
PyInit_backend(void)
{
    return PyModule_Create(&module);
}
