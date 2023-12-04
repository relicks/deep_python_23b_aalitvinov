#include <Python.h>
#include <stdio.h>
#include <stdlib.h>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

PyObject* cjson_sum(PyObject* self, PyObject* args) {
    PyObject* list_obj;
    // long int elem_count;
    if (!PyArg_ParseTuple(args, "O", &list_obj)) {
        printf("Failed to parse arguments");
        return NULL;
    }

    long int list_len = PyList_Size(list_obj);
    int res = 0;
    for (int i = 0; i < list_len && i < list_len; ++i) {
        PyObject* tmp = PyList_GetItem(list_obj, i);
        int elem = PyLong_AsLong(tmp);
        res += elem;
    }
    return Py_BuildValue("i", res);
}

PyObject* cjson_loads(PyObject* self, PyObject* args) {
    char* json_str;
    if (!PyArg_ParseTuple(args, "s", &json_str)) {
        return NULL;
    }

    json j = json::parse(json_str);

    // Convert the JSON object to a Python dictionary
    PyObject* dict = PyDict_New();
    for (auto& element : j.items()) {
        PyDict_SetItemString(
            dict,
            element.key().c_str(),
            PyUnicode_FromString(element.value().dump().c_str())
        );
    }

    return dict;
}

PyObject* cjson_dumps(PyObject* self, PyObject* args) {
    PyObject* dict;
    if (!PyArg_ParseTuple(args, "O", &dict)) {
        return NULL;
    }

    // Convert the Python dictionary to a JSON object
    json j;
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(dict, &pos, &key, &value)) {
        j[PyUnicode_AsUTF8(key)] = PyUnicode_AsUTF8(value);
    }

    // Convert the JSON object to a string
    std::string str = j.dump();
    return PyUnicode_FromString(str.c_str());
}

static PyMethodDef methods[] = {
    {"sum", cjson_sum, METH_VARARGS, "sum of first n elements of our array"},
    {"loads",
     cjson_loads,
     METH_VARARGS,
     "Deserialize a str instance containing a JSON document to a Python object."
    },
    {"dumps",
     cjson_dumps,
     METH_VARARGS,
     "Serialize a Python dict to a JSON formatted str."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module_cjson =
    {PyModuleDef_HEAD_INIT, "cjson", NULL, -1, methods};

PyMODINIT_FUNC PyInit_cjson() {
    return PyModule_Create(&module_cjson);
}