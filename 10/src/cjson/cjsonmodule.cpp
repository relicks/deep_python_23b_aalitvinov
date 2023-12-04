#include <stdio.h>
#include <stdlib.h>

#include <Python.h>
#include <iostream>

PyObject *cjson_sum(PyObject *self, PyObject *args) {
    PyObject *list_obj;
    // long int elem_count;
    if (!PyArg_ParseTuple(args, "O", &list_obj)) {
        printf("Failed to parse arguments");
        return NULL;
    }

    long int list_len = PyList_Size(list_obj);
    int res = 0;
    for (int i = 0; i < list_len && i < list_len; ++i) {
        PyObject *tmp = PyList_GetItem(list_obj, i);
        int elem = PyLong_AsLong(tmp);
        res += elem;
    }
    return Py_BuildValue("i", res);
}

int fibonacci(int n) {
    if (n < 2) {
        return 1;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

PyObject *cjson_fibonacci(PyObject *self, PyObject *args) {
    int n = 0;
    if (!PyArg_ParseTuple(args, "i", &n)) {
        printf("Failed to parse arguments");
        return NULL;
    }
    int res = fibonacci(n);
    return Py_BuildValue("i", res);
}

static PyMethodDef methods[] = {
    {"sum", cjson_sum, METH_VARARGS, "sum of first n elements of our array"},
    {"fibonacci", cjson_fibonacci, METH_VARARGS, "returns i'th element of fibonacci sequance"},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef module_cjson = {
    PyModuleDef_HEAD_INIT, "cjson", NULL, -1, methods};

PyMODINIT_FUNC PyInit_cjson() {
    return PyModule_Create(&module_cjson);
}