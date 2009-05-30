// ======================================
// Properties extension for python
// --------------------------------------
// (c) Copyright 2009 Mark Hurenkamp
// 
// This software is licensed under GPL v2
// ======================================

#include "symbian_python_ext_util.h"
#include <hal.h>
#include <hwrmpowerstatesdkpskeys.h>
#include <e32base.h>
#include <e32property.h>
#include <aknappui.h>

class CPropertyNotifier: public CActive
{
public:
    static CPropertyNotifier* NewL(); 
	~CPropertyNotifier();
	void Subscribe(TUid aUid, TInt aKey,PyObject *aCallback);
protected:
    CPropertyNotifier();
	void ConstructL();
	virtual void RunL();
	virtual void DoCancel();
	//virtual TInt RunError(TInt aError);
	
	RProperty iProperty;
	PyObject *iCallback;
};

CPropertyNotifier* CPropertyNotifier::NewL() 
{
    CPropertyNotifier* self = new (ELeave) CPropertyNotifier();
	CleanupStack::PushL(self);
	self->ConstructL();
	CleanupStack::Pop(self);
	return self;
} 

CPropertyNotifier::~CPropertyNotifier() 
{
    Cancel();
}

void CPropertyNotifier::Subscribe(TUid aUid, TInt aKey, PyObject *aCallback) 
{
    iProperty.Attach(aUid,aKey);
	iProperty.Subscribe(iStatus);
	iCallback = aCallback;
	Py_XINCREF(aCallback);
	SetActive();
}

CPropertyNotifier::CPropertyNotifier()
:CActive(CActive::EPriorityStandard) 
{
}

void CPropertyNotifier::ConstructL()
{
    CActiveScheduler::Add(this);
}

void CPropertyNotifier::RunL()
{
    // Call the python callback function

    PyGILState_STATE state;
	state = PyGILState_Ensure();
    PyObject *rslt = PyObject_CallObject(iCallback, NULL);
    if (rslt) 
    {
		Py_XDECREF(rslt);
	}
	Py_XDECREF(iCallback);
	iCallback = NULL;
	PyGILState_Release(state);
}

void CPropertyNotifier::DoCancel()
{
    iProperty.Cancel();
}




extern "C" PyObject *
DefineInt(PyObject *self, PyObject *args)
{
	RProperty myProperty;
	TUid uid;
	TInt key;

    if (PyArg_ParseTuple(args, "ii", &uid, &key)) 
	{
		TRAPD(error,
			myProperty.Define( uid, key, RProperty::EInt);
		);
		RETURN_ERROR_OR_PYNONE(error);
    }	
    return NULL;
}

extern "C" PyObject *
GetInt(PyObject *self, PyObject *args)
{
	RProperty myProperty;
	TUid uid;
	TInt key;
	TInt result;
    if (PyArg_ParseTuple(args, "ii", &uid, &key)) 
	{
		myProperty.Get( uid, key, result);
    }	
	return Py_BuildValue("i", result);
}

extern "C" PyObject *
SetInt(PyObject *self, PyObject *args)
{
	RProperty myProperty;
	TUid uid;
	TInt key;
	TInt value;
    if (PyArg_ParseTuple(args, "iii", &uid, &key, &value)) 
	{
		TRAPD(error,
			myProperty.Set( uid, key, value);
		);
		RETURN_ERROR_OR_PYNONE(error);
    }	
    return NULL;
}

extern "C" PyObject *
DeleteInt(PyObject *self, PyObject *args)
{
	RProperty myProperty;
	TUid uid;
	TInt key;
    if (PyArg_ParseTuple(args, "ii", &uid, &key)) 
	{
		TRAPD(error,
			myProperty.Delete( uid, key);
		);
		RETURN_ERROR_OR_PYNONE(error);
	}	
    return NULL;
}

extern "C" PyObject * 
SubscribeInt(PyObject* self, PyObject* args) 
{
    PyObject* callback = NULL;
	TUid uid;
	TInt key;
	CPropertyNotifier *notifier = CPropertyNotifier::NewL();
	
    if (!PyArg_ParseTuple(args, "iiO:SubscribeInt", &uid, &key, &callback)) 
        return NULL;  

    if (!PyCallable_Check(callback))
	{
        PyErr_SetString(PyExc_TypeError, "Callback must be a callable method");
	    return NULL;
	}
	
    TRAPD(error,
        notifier->Subscribe(uid,key,callback);
    );
    RETURN_ERROR_OR_PYNONE(error);
}

extern "C" {

  static const PyMethodDef properties_methods[] = {
    {"DefineInt",         (PyCFunction)DefineInt,         METH_VARARGS, "void DefineInt(uid,key,value)"},
    {"GetInt",            (PyCFunction)GetInt,            METH_VARARGS, "int  GetInt(uid,key)"},
    {"SetInt",            (PyCFunction)SetInt,            METH_VARARGS, "void SetInt(uid,key,value)"},
    {"DeleteInt",         (PyCFunction)DeleteInt,         METH_VARARGS, "void DeleteInt(uid,key)"},
    {"SubscribeInt",      (PyCFunction)SubscribeInt,      METH_VARARGS, "void SubscribeInt(uid,key,callback)"},
	
    {NULL,NULL}           /* sentinel */
  };

  DL_EXPORT(void) init_properties(void)
  {
    Py_InitModule("_properties", (PyMethodDef*)properties_methods);
  }
} // Extern "C"


