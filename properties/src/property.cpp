/*
 ============================================================================
 Name           : properties.cpp
 Author         : Mark Hurenkamp
 Copyright      : Licensed under GPL v2
 Description    : Property class source, python interface to S60
                  Publish & Subscribe interface
 ============================================================================
 */

#include <hal.h>
#include <hwrmpowerstatesdkpskeys.h>
#include <e32base.h>
#include <e32property.h>
#include "symbian_python_ext_util.h"
#include "module.h"
#include "property.h"
#include "propertyupdater.h"

struct sProperty
{
    PyObject_HEAD;
    RProperty property;
    CPropertyUpdater *updater;
    TUint t;
};

static PyObject* property_define(PyObject* /*self*/, PyObject* args)
{
    TInt error;
    TUid uid;
    TUint key;
    TUint t;

    if (!PyArg_ParseTuple(args, "kkk", &uid.iUid, &key, &t))
        return NULL;

    TRAP(error, RProperty::Define(uid,key,t));

    if (error)
        return SPyErr_SetFromSymbianOSErr(error);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* property_delete(PyObject* /*self*/, PyObject* args)
{
    TInt error;
    TUid uid;
    TUint key;

    if (!PyArg_ParseTuple(args, "kk", &uid.iUid, &key))
        return NULL;

    TRAP(error, RProperty::Delete(uid,key));

    if (error)
        return SPyErr_SetFromSymbianOSErr(error);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* property_attach(sProperty* self, PyObject* args)
{
    TInt error;
    TUid uid;
    TUint key;
    TUint t;

    if (!PyArg_ParseTuple(args, "kkk", &uid.iUid, &key, &t))
        return NULL;

    TRAP(error, self->property.Attach(uid,key));

    if (error)
        return SPyErr_SetFromSymbianOSErr(error);

    self->t = t;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* property_subscribe(sProperty* self, PyObject* args)
{
    TInt error;
    PyObject *callback;

    if (!PyArg_ParseTuple(args, "O", &callback))
        return NULL;

    TRAP(error, {
        CPropertyUpdater* updater = new (ELeave)CPropertyUpdater();
        CleanupStack::PushL(updater);
        updater->ConstructL(&self->property, callback);
        CleanupStack::Pop();

        self->updater = updater;
    });
    if (error)
        return SPyErr_SetFromSymbianOSErr(error);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* property_cancel(sProperty* self, PyObject* /*args*/)
{
    TInt error;

    if (self->updater != NULL)
    {
		TRAP(error, {
			self->updater->Stop();
			delete self->updater;
			self->updater = NULL;
		});
		if (error)
			return SPyErr_SetFromSymbianOSErr(error);
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* property_setint(sProperty* self, PyObject* args)
{
    TInt error;
    TInt value;

    if (!PyArg_ParseTuple(args, "i", &value))
        return NULL;

    TRAP(error, self->property.Set(value));

    if (error)
        return SPyErr_SetFromSymbianOSErr(error);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* property_settext(sProperty* self, PyObject* args)
{
    TInt error;
    TText8 *buf;
    TInt len;

    if (!PyArg_ParseTuple(args, "s#", &buf, &len))
        return NULL;

    TPtr8 ptr(buf,len,len);
    TRAP(error, self->property.Set(ptr));

    if (error)
        return SPyErr_SetFromSymbianOSErr(error);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* property_set(sProperty* self, PyObject* args)
{
    switch(self->t)
    {
        case RProperty::EInt:
            return property_setint(self,args);
        case RProperty::EText:
            return property_settext(self,args);
        case RProperty::ELargeText:
            return property_settext(self,args);
    }
    return NULL;
}

static PyObject* property_getint(sProperty* self, PyObject* args)
{
    TInt error;
    TInt value;

    TRAP(error, self->property.Get(value));

    if (error)
        return SPyErr_SetFromSymbianOSErr(error);

    return Py_BuildValue("i",value);
}

static PyObject* property_gettext(sProperty* self, TInt len)
{
    TInt error;
    RBuf8 buf;
    PyObject* result;

    buf.CreateMaxL(len);
    TRAP(error, self->property.Get(buf));

    if (error)
    {
        buf.Close();
        return SPyErr_SetFromSymbianOSErr(error);
    }

    result = Py_BuildValue("s#",buf.Ptr(),buf.Length());
    buf.Close();
    return result;
}

static PyObject* property_get(sProperty* self, PyObject* args)
{
    TInt len;
    switch(self->t)
    {
        case RProperty::EInt:
            return property_getint(self,args);
        case RProperty::EText:
            if (!PyArg_ParseTuple(args, "|i", &len))
                len=64;
            return property_gettext(self,len);
        case RProperty::ELargeText:
            if (!PyArg_ParseTuple(args, "|i", &len))
                len=2048;
            return property_gettext(self,len);
    }
    return NULL;
}

static void property_del(sProperty* self)
{
    self->property.Cancel();
    PyObject_Del(self);
}

static PyMethodDef property_methods[] =
{
    { "_dummy_",    (PyCFunction)property_define,         METH_VARARGS, "" },
    { "Define",     (PyCFunction)property_define,         METH_STATIC,  "" },
    { "Delete",     (PyCFunction)property_delete,         METH_STATIC,  "" },
    { "Attach",     (PyCFunction)property_attach,         METH_VARARGS, "" },
    { "Subscribe",  (PyCFunction)property_subscribe,      METH_VARARGS, "" },
    { "Cancel",     (PyCFunction)property_cancel,         METH_VARARGS, "" },
    { "Get",        (PyCFunction)property_get,            METH_VARARGS, "" },
    { "Set",        (PyCFunction)property_set,            METH_VARARGS, "" },
    { 0, 0 }
};

sConstant property_constants[] =
{
	{ "EInt",                               RProperty::EInt },
	{ "EByteArray",                         RProperty::EByteArray },
	{ "ELargeByteArray",                    RProperty::ELargeByteArray },
	{ "EText",                              RProperty::EText },
	{ "ELargeText",                         RProperty::ELargeText },

	{ 0, 0 }
};

static PyObject *
property_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    sProperty *self;

    self = (sProperty *)type->tp_alloc(type, 0);
    if (self != NULL) {
    }

    return (PyObject *)self;
}

static int
property_init(sProperty *self, PyObject *args, PyObject *kwds)
{
    return 0;
}

static void
property_dealloc(sProperty* self)
{
	property_cancel(self,NULL);
    self->ob_type->tp_free((PyObject*)self);
}
/*
static PyMemberDef property_members[] = {
    {"first", T_OBJECT_EX, offsetof(Noddy, first), 	0, "first name"},
    {"last", T_OBJECT_EX, offsetof(Noddy, last), 		0, "last name"},
    {"number", T_INT, offsetof(Noddy, number), 		0, "noddy number"},
    {NULL}
};
*/

PyTypeObject tProperty = {
    PyObject_HEAD_INIT(NULL)
    0,                                                 // ob_size
    "properties.Property",                             // tp_name
    sizeof(sProperty),                                 // tp_basicsize
    0,                                                 // tp_itemsize
    (destructor)property_dealloc,                      // tp_dealloc
    0,                                                 // tp_print
    0,                                                 // tp_getattr
    0,                                                 // tp_setattr
    0,                                                 // tp_compare
    0,                                                 // tp_repr
    0,                                                 // tp_as_number
    0,                                                 // tp_as_sequence
    0,                                                 // tp_as_mapping
    0,                                                 // tp_hash
    0,                                                 // tp_call
    0,                                                 // tp_str
    0,                                                 // tp_getattro
    0,                                                 // tp_setattro
    0,                                                 // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,          // tp_flags
    "Property objects",                                // tp_doc
    0,                                                 // tp_traverse
    0,                                                 // tp_clear
    0,                                                 // tp_richcompare
    0,                                                 // tp_weaklistoffset
    0,                                                 // tp_iter
    0,                                                 // tp_iternext
    property_methods,                                  // tp_methods
    0, //property_members,                             // tp_members
    0,                                                 // tp_getset
    0,                                                 // tp_base
    0,                                                 // tp_dict
    0,                                                 // tp_descr_get
    0,                                                 // tp_descr_set
    0,                                                 // tp_dictoffset
    (initproc)property_init,                           // tp_init
    0,                                                 // tp_alloc
    property_new,                                      // tp_new
};
