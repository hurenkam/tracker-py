/*
 * module.cpp
 *
 *  Created on: 2-jul-2009
 *      Author: Mark Hurenkamp
 */

#include <hal.h>
#include <hwrmpowerstatesdkpskeys.h>
#include <e32base.h>
#include <e32property.h>
#include "symbian_python_ext_util.h"
#include "module.h"
#include "property.h"

TUint getsid()
{
    RProcess process;
    return process.SecureId();
}

static PyObject * GetSid(PyObject *self, PyObject */*args*/)
{
    return PyLong_FromUnsignedLong(getsid());
}

static const PyMethodDef module_methods[] =
{
    { "GetSid",     (PyCFunction)GetSid,                 METH_VARARGS, ""},
    { 0, 0 }
};

static sConstant module_constants[] =
{
    { 0, 0 }
};

void PyModule_AddConstants(PyObject *d, sConstant *c)
{
    while (c->name != 0)
    {
        PyDict_SetItemString(d,c->name,PyInt_FromLong(c->value));
        c++;
    };
};

static void inittype(char *name, PyObject *o, PyTypeObject *t, sConstant *c)
{
    if (PyType_Ready(t) < 0)
        return;
    if (c != NULL)
        PyModule_AddConstants(t->tp_dict,c);
    Py_INCREF(t);
    PyModule_AddObject(o, name, (PyObject *)t);
}

DL_EXPORT(void) initproperties()
{
    PyObject *m, *d;

    m = Py_InitModule("properties", (PyMethodDef*) module_methods);
    d = PyModule_GetDict(m);

    PyModule_AddConstants(d,&module_constants[0]);
    
    inittype("Property", m, &tProperty, &property_constants[0]);
}
