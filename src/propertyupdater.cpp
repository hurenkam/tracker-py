/*
 * propertyupdater.cpp
 *
 *  Created on: 2-jul-2009
 *      Author: Mark
 */

#include <hal.h>
#include <hwrmpowerstatesdkpskeys.h>
#include <e32base.h>
#include <e32property.h>
#include "symbian_python_ext_util.h"
#include "module.h"
#include "property.h"
#include "propertyupdater.h"

CPropertyUpdater::CPropertyUpdater():CActive(EPriorityStandard)
{
    CActiveScheduler::Add(this);
    RThread t;
    iOwnerThreadId = t.Id();
}

void CPropertyUpdater::ConstructL(RProperty *property, PyObject* callback)
{
    iProperty = property;
    SetPropertyCallback(callback);
    iProperty->Subscribe(iStatus);
    SetActive();
}

CPropertyUpdater::~CPropertyUpdater()
{
    Py_XDECREF(iPropertyCallback);
    iPropertyCallback = NULL;
}

void CPropertyUpdater::Stop()
{
    SafeCancel();
    Py_XDECREF(iPropertyCallback);
    iPropertyCallback = NULL;
}

void CPropertyUpdater::SafeCancel()
{
    RThread t;
    if (iOwnerThreadId == t.Id())
    {
        TRAPD(err, Cancel(); );
    }
}

void CPropertyUpdater::RunL()
{
    if (iStatus != KErrCancel) {
        PyGILState_STATE state = PyGILState_Ensure();
        //PyEval_RestoreThread(PYTHON_TLS->thread_state);
        InvokePropertyCallback(Py_BuildValue("()"));
        //PyEval_SaveThread();
        PyGILState_Release(state);
        iProperty->Subscribe(iStatus);
        SetActive();
    }
}

void CPropertyUpdater::DoCancel()
{
    iProperty->Cancel();
}

void CPropertyUpdater::SetPropertyCallback(PyObject *callback)
{
    Py_XDECREF(iPropertyCallback);
    iPropertyCallback = callback;
    Py_XINCREF(callback);
}

void CPropertyUpdater::InvokePropertyCallback(PyObject *arg)
{
    if (iPropertyCallback) {
        PyObject* rval = PyEval_CallObject(iPropertyCallback, (PyObject*)arg);
        Py_XDECREF(rval);
    }
    Py_XDECREF(arg);
}
