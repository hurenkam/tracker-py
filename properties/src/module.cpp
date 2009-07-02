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
    // e32property defines
        { "EInt",                               RProperty::EInt },
        { "EByteArray",                         RProperty::EByteArray },
        { "ELargeByteArray",                    RProperty::ELargeByteArray },
        { "EText",                              RProperty::EText },
        { "ELargeText",                         RProperty::ELargeText },

    // hwrmpowerstate defines
        { "KPSUidHWRMPowerState",               KPSUidHWRMPowerState.iUid },
        { "KHWRMBatteryLevel",                  KHWRMBatteryLevel },
        { "KHWRMBatteryStatus",                 KHWRMBatteryStatus },
        { "KHWRMChargingStatus",                KHWRMChargingStatus },

        { "EBatteryLevelUnknown",               EBatteryLevelUnknown },
        { "EBatteryLevelLevel0",                EBatteryLevelLevel0 },
        { "EBatteryLevelLevel1",                EBatteryLevelLevel1 },
        { "EBatteryLevelLevel2",                EBatteryLevelLevel2 },
        { "EBatteryLevelLevel3",                EBatteryLevelLevel3 },
        { "EBatteryLevelLevel4",                EBatteryLevelLevel4 },
        { "EBatteryLevelLevel5",                EBatteryLevelLevel5 },
        { "EBatteryLevelLevel6",                EBatteryLevelLevel6 },
        { "EBatteryLevelLevel7",                EBatteryLevelLevel7 },

        { "EBatteryStatusUnknown",              EBatteryStatusUnknown },
        { "EBatteryStatusOk",                   EBatteryStatusOk },
        { "EBatteryStatusLow",                  EBatteryStatusLow },
        { "EBatteryStatusEmpty",                EBatteryStatusEmpty },

        { "EChargingStatusError",               EChargingStatusError },
        { "EChargingStatusNotConnected",        EChargingStatusNotConnected },
        { "EChargingStatusCharging",            EChargingStatusCharging },
        { "EChargingStatusNotCharging",         EChargingStatusNotCharging },
        { "EChargingStatusAlmostComplete",      EChargingStatusAlmostComplete },
        { "EChargingStatusChargingComplete",    EChargingStatusChargingComplete },
        { "EChargingStatusChargingContinued",   EChargingStatusChargingContinued },

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
