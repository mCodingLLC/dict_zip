/*
    Copyright 2022 MCODING, LLC.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    dict_zip module written and maintained
    by James Murphy <james@mcoding.io>
*/

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include <stddef.h>

typedef struct {  // clang-format off
    PyObject_HEAD           // clang-format on
    Py_ssize_t dict_count;  // len(dicts)
    Py_ssize_t pos;         // iteration position in first dict
    Py_ssize_t len;         // common length of dicts
    PyObject *dicts;        // tuple of dictionaries
} dict_zip_object;

static PyTypeObject dict_zip_type;

static PyObject *
dict_zip_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (kwds != NULL && PyDict_CheckExact(kwds) && PyDict_GET_SIZE(kwds) > 0) {
        PyErr_SetString(PyExc_TypeError, "dict_zip() got an unexpected keyword argument");
        return NULL;
    }

    // args must be a tuple
    assert(PyTuple_Check(args));
    Py_ssize_t dict_count = PyTuple_GET_SIZE(args);

    // args must be dicts
    for (Py_ssize_t i = 0; i < dict_count; i++) {
        PyObject *item = PyTuple_GET_ITEM(args, i);
        if (!PyDict_Check(item)) {
            PyErr_SetString(PyExc_TypeError,
                            "dict_zip() args must be dict subclass instances");
            return NULL;
        }
    }

    Py_ssize_t len = -1;

    // dicts must have the same length
    if (dict_count > 0) {
        PyObject *first_dict = PyTuple_GET_ITEM(args, 0);
        len = PyDict_GET_SIZE(first_dict);
        for (Py_ssize_t i = 1; i < dict_count; i++) {
            PyObject *item = PyTuple_GET_ITEM(args, i);
            if (PyDict_GET_SIZE(item) != len) {
                PyErr_SetString(PyExc_ValueError, "dict_zip() args must have the same length");
                return NULL;
            }
        }
    }

    // create the object
    dict_zip_object *self = (dict_zip_object *)type->tp_alloc(type, 0);
    self->dict_count = dict_count;
    self->pos = 0;
    self->len = len;

    // store the args in a tuple
    PyObject *dicts = PyTuple_New(dict_count);
    self->dicts = dicts;
    if (dicts == NULL) {
        return NULL;
    }
    for (Py_ssize_t i = 0; i < dict_count; i++) {
        PyObject *item = PyTuple_GET_ITEM(args, i);
        Py_INCREF(item);
        PyTuple_SET_ITEM(dicts, i, item);
    }

    return (PyObject *)self;
}

static void
dict_zip_dealloc(dict_zip_object *self)
{
    PyObject_GC_UnTrack(self);
    Py_XDECREF(self->dicts);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static int
dict_zip_traverse(dict_zip_object *self, visitproc visit, void *arg)
{
    Py_VISIT(self->dicts);
    return 0;
}

static PyObject *
dict_zip_next(dict_zip_object *self)
{
    Py_ssize_t dict_count = self->dict_count;
    if (dict_count == 0) {  // no args were passed, empty iter
        return NULL;
    }

    Py_ssize_t tuple_size = dict_count + 1;
    PyObject *result = PyTuple_New(tuple_size);
    if (result == NULL) {
        return NULL;
    }

    PyObject *dicts = self->dicts;
    Py_ssize_t len = self->len;
    PyObject *first_dict = PyTuple_GET_ITEM(dicts, 0);

    if (PyDict_GET_SIZE(first_dict) != len) {
        self->len = -1;  // make state sticky
        PyErr_SetString(PyExc_RuntimeError, "dictionary changed size during iteration");
        goto error;
    }

    PyObject *key;
    PyObject *value;
    Py_hash_t hash;
    if (!_PyDict_Next(first_dict, &(self->pos), &key, &value, &hash)) {
        return NULL;  // iteration done
    }

    Py_INCREF(key);
    Py_INCREF(value);
    PyTuple_SET_ITEM(result, 0, key);
    PyTuple_SET_ITEM(result, 1, value);

    for (Py_ssize_t i = 1; i < dict_count; i++) {
        PyObject *other_dict = PyTuple_GET_ITEM(dicts, i);

        if (PyDict_GET_SIZE(other_dict) != len) {
            self->len = -1;  // make state sticky
            PyErr_SetString(PyExc_RuntimeError, "dictionary changed size during iteration");
            goto error;
        }

        value = _PyDict_GetItem_KnownHash(other_dict, key, hash);
        if (value != NULL) {
            Py_INCREF(value);
            PyTuple_SET_ITEM(result, i + 1, value);
        }
        else {
            goto error;
        }
    }

    return result;

error:
    Py_DECREF(result);

    // value NULL without exception = KeyError from dict builtin
    if (!PyErr_Occurred() || PyErr_ExceptionMatches(PyExc_KeyError)) {
        PyErr_SetString(PyExc_KeyError, "dict_zip() dicts did not have the same keys");
    }

    // value NULL with exception = exception (probably from key.__eq__)
    // pass through the exception
    return NULL;
}

PyDoc_STRVAR(dict_zip_doc,  // clang-format off
"dict_zip(d1, d2, ...) --> dict_zip object\n\
\n\
Return a dict_zip object whose .__next__() method returns a tuple where\n\
the i-th element comes from the i-th dictionary argument. \n\
Throws a ValueError on construction if the dicts do not have the same sizes.\n\
Throws a KeyError during iteration if a the dicts do not have the same keys.\n\
Assumes the dicts are not modified during iteration.\n\
Throws a RuntimeError if a size change is detected during iteration.\n\
");  // clang-format on

static PyTypeObject dict_zip_type = {
    PyVarObject_HEAD_INIT(NULL, 0)  // clang-format off
    .tp_name = "_dict_zip.dict_zip",  // clang-format on
    .tp_basicsize = sizeof(dict_zip_object),
    .tp_dealloc = (destructor)dict_zip_dealloc,
    .tp_getattro = PyObject_GenericGetAttr,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE,
    .tp_doc = dict_zip_doc,
    .tp_traverse = (traverseproc)dict_zip_traverse,
    .tp_iter = PyObject_SelfIter,
    .tp_iternext = (iternextfunc)dict_zip_next,
    .tp_methods = NULL,
    .tp_new = dict_zip_new,
    .tp_free = PyObject_GC_Del,
};

/* module level code ********************************************************/

PyDoc_STRVAR(module_doc,  // clang-format off
"Functional tools iterating over corresponding dictionaries.\n\
\n\
dict_zip(d1, d2, ...) -> (k, v1, v2), ... corresponding key and values.\n\
");  // clang-format on

static struct PyModuleDef dict_zip_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_dict_zip",
    .m_doc = module_doc,
    .m_size = 0,
    .m_methods = NULL,
};

PyMODINIT_FUNC
PyInit__dict_zip(void)
{
    PyTypeObject *type_list[] = {&dict_zip_type, NULL};

    PyObject *module = PyModule_Create(&dict_zip_module);
    if (module == NULL) {
        return NULL;
    }

    for (size_t i = 0; type_list[i] != NULL; i++) {
        PyTypeObject *type = type_list[i];
        if (PyType_Ready(type) < 0) {
            return NULL;
        }

        const char *name = _PyType_Name(type);
        assert(name != NULL);

        Py_INCREF(type);
        if (PyModule_AddObject(module, name, (PyObject *)type) < 0) {
            Py_DECREF(type);
            Py_DECREF(module);
            return NULL;
        }
    }

    return module;
}