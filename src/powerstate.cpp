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
#include "powerstate.h"

struct sPowerState
{
    PyObject_HEAD;
};

static PyMethodDef powerstate_methods[] =
{
    { 0, 0 }
};

sConstant powerstate_constants[] =
{
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

static PyObject *
powerstate_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    sPowerState *self;
    self = (sPowerState *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int
powerstate_init(sPowerState *self, PyObject *args, PyObject *kwds)
{
    return 0;
}

static void
powerstate_dealloc(sPowerState* self)
{
    self->ob_type->tp_free((PyObject*)self);
}

PyTypeObject tPowerState = {
    PyObject_HEAD_INIT(NULL)
    0,                                                 // ob_size
    "properties.PowerState",                           // tp_name
    sizeof(sPowerState),                               // tp_basicsize
    0,                                                 // tp_itemsize
    (destructor)powerstate_dealloc,                    // tp_dealloc
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
    "PowerState objects",                              // tp_doc
    0,                                                 // tp_traverse
    0,                                                 // tp_clear
    0,                                                 // tp_richcompare
    0,                                                 // tp_weaklistoffset
    0,                                                 // tp_iter
    0,                                                 // tp_iternext
    powerstate_methods,                                // tp_methods
    0, //property_members,                             // tp_members
    0,                                                 // tp_getset
    0,                                                 // tp_base
    0,                                                 // tp_dict
    0,                                                 // tp_descr_get
    0,                                                 // tp_descr_set
    0,                                                 // tp_dictoffset
    (initproc)powerstate_init,                         // tp_init
    0,                                                 // tp_alloc
    powerstate_new,                                    // tp_new
};

