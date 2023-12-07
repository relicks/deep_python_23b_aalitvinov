#include <Python.h>

#include <algorithm>
#include <nlohmann/json.hpp>
#include <string>

using json = nlohmann::json;


PyObject* cjson_loads(PyObject* self, PyObject* args) {
    char* json_str;
    if (!PyArg_ParseTuple(args, "s", &json_str)) {
        return NULL;
    }
    if (!json::accept(json_str)) {
        PyErr_SetString(PyExc_ValueError, "String must conform to JSON format");
        return NULL;
    } else {
        json j = json::parse(json_str);

        // Convert the JSON object to a Python dictionary
        PyObject* dict = PyDict_New();
        for (auto& element : j.items()) {
            PyObject* value;
            if (element.value().is_number_integer()) {  //? int
                value = PyLong_FromLong(element.value().get<long>());
            } else if (element.value().is_number_float()) {  //? float
                value = PyFloat_FromDouble(element.value().get<double>());
            } else if (element.value().is_boolean()) {  //? bool
                value = PyBool_FromLong(element.value().get<bool>());
            } else if (element.value().is_string()) {  //? str
                value = PyUnicode_FromString(
                    element.value().get<std::string>().c_str()
                );
            } else if (element.value().is_array()) {  //? list
                value = PyList_New(element.value().size());
                for (size_t i = 0; i < element.value().size(); i++) {
                    PyList_SetItem(
                        value,
                        i,
                        PyUnicode_FromString(element.value()[i].dump().c_str())
                    );
                }
            } else if (element.value().is_object()) {  //? dict
                PyErr_SetString(
                    PyExc_NotImplementedError,
                    "Parsing of JSON objects is not yet implemented"
                );
                return NULL;

            } else {
                value = Py_None;
            }

            PyDict_SetItemString(dict, element.key().c_str(), value);
        }

        return dict;
    }
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
        if (PyLong_Check(value)) {
            j[PyUnicode_AsUTF8(key)] = PyLong_AsLong(value);
        } else if (PyFloat_Check(value)) {
            j[PyUnicode_AsUTF8(key)] = PyFloat_AsDouble(value);
        } else if (PyBool_Check(value)) {
            j[PyUnicode_AsUTF8(key)] = PyObject_IsTrue(value);
        } else if (PyUnicode_Check(value)) {
            j[PyUnicode_AsUTF8(key)] = PyUnicode_AsUTF8(value);
        } else if (PyList_Check(value)) {
            j[PyUnicode_AsUTF8(key)] = json::array();
            for (Py_ssize_t i = 0; i < PyList_Size(value); i++) {
                PyObject* item = PyList_GetItem(value, i);
                if (PyLong_Check(item)) {
                    j[PyUnicode_AsUTF8(key)].push_back(PyLong_AsLong(item));
                } else if (PyFloat_Check(item)) {
                    j[PyUnicode_AsUTF8(key)].push_back(PyFloat_AsDouble(item));
                } else if (PyBool_Check(item)) {
                    j[PyUnicode_AsUTF8(key)].push_back(PyObject_IsTrue(item));
                } else if (PyUnicode_Check(item)) {
                    j[PyUnicode_AsUTF8(key)].push_back(PyUnicode_AsUTF8(item));
                } else if (PyDict_Check(value)) {
                    PyErr_SetString(
                        PyExc_NotImplementedError,
                        "Serialization of nested Python dicts is not implemented yet"
                    );
                    return NULL;
                }
            }
        } else if (PyDict_Check(value)) {
            PyErr_SetString(
                PyExc_NotImplementedError,
                "Serialization of nested Python dicts is not implemented yet"
            );
            return NULL;
        }
    }

    // Convert the JSON object to a string
    std::string str = j.dump(1, ' ');
    str.erase(std::remove(str.begin(), str.end(), '\n'), str.end());
    str.erase(1, 1);
    return PyUnicode_FromString(str.c_str());
}

static PyMethodDef methods[] = {
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