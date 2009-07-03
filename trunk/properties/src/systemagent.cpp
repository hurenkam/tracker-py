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
#include "systemagent.h"

struct sSystemAgent
{
    PyObject_HEAD;
};

static PyMethodDef systemagent_methods[] =
{
    { 0, 0 }
};

sConstant systemagent_constants[] =
{
    { "KUidProfile",                   KUidProfileValue },

    { "KUidPhonePwr",                  KUidPhonePwrValue },
    {     "ESAPhoneOff",               ESAPhoneOff },
    {     "ESAPhoneOn",                ESAPhoneOn },

    { "KUidSIMStatus",                 KUidSIMStatusValue },
    {     "ESASimOk",                  ESASimOk },
    {     "ESASimNotPresent",          ESASimNotPresent },
    {     "ESASimRejected",            ESASimRejected },

    { "KUidNetworkStatus",             KUidNetworkStatusValue },
    {     "ESANetworkAvailable",       ESANetworkAvailable },
    {     "ESANetworkUnAvailable",     ESANetworkUnAvailable },

    { "KUidNetworkStrength",           KUidNetworkStrengthValue },
    {     "ESANetworkStrengthNone",    ESANetworkStrengthNone },
    {     "ESANetworkStrengthLow",     ESANetworkStrengthLow },
    {     "ESANetworkStrengthMedium",  ESANetworkStrengthMedium },
    {     "ESANetworkStrengthHigh",    ESANetworkStrengthHigh },
    {     "ESANetworkStrengthUnknown", ESANetworkStrengthUnknown },

    { "KUidChargerStatus",             KUidChargerStatusValue },
    {     "ESAChargerConnected",       ESAChargerConnected },
    {     "ESAChargerDisconnected",    ESAChargerDisconnected },
    {     "ESAChargerNotCharging",     ESAChargerNotCharging },

    { "KUidBatteryStrength",           KUidBatteryStrengthValue },
    {     "ESABatteryAlmostEmpty",     ESABatteryAlmostEmpty },
    {     "ESABatteryLow",             ESABatteryLow },
    {     "ESABatteryFull",            ESABatteryFull },

    { "KUidCurrentCall",               KUidCurrentCallValue },
    {     "ESACallNone",               ESACallNone },
    {     "ESACallVoice",              ESACallVoice },
    {     "ESACallFax",                ESACallFax },
    {     "ESACallData",               ESACallData },
    {     "ESACallAlerting",           ESACallAlerting },
    {     "ESACallRinging",            ESACallRinging },
    {     "ESACallAlternating",        ESACallAlternating },
    {     "ESACallDialling",           ESACallDialling },
    {     "ESACallAnswering",          ESACallAnswering },
    {     "ESACallDisconnecting",      ESACallDisconnecting },

    { "KUidDataPort",                  KUidDataPortValue },
    {     "ESADataPortIdle",           ESADataPortIdle },
    {     "ESADataPortBusy",           ESADataPortBusy },

    { "KUidInboxStatus",               KUidInboxStatusValue },
    {     "ESAInboxEmpty",             ESAInboxEmpty, },
    {     "ESADocumentsInInbox",       ESADocumentsInInbox },

    { "KUidOutboxStatus",              KUidOutboxStatusValue },
    {     "ESAOutboxEmpty",            ESAOutboxEmpty, },
    {     "ESADocumentsInOutbox",      ESADocumentsInOutbox },

    { "KUidClock",                     KUidClockValue },
    {     "ESAAm",                     ESAAm },
    {     "ESAPm",                     ESAPm },

    { "KUidAlarm",                     KUidAlarmValue },
    {     "ESAAlarmOff",               ESAAlarmOff },
    {     "ESAAlarmOn",                ESAAlarmOn },

    { "KUidIrdaStatus",                KUidIrdaStatusValue },
    {     "ESAIrLoaded",               ESAIrLoaded, },
    {     "ESAIrDiscoveredPeer",       ESAIrDiscoveredPeer, },
    {     "ESAIrLostPeer",             ESAIrLostPeer, },
    {     "ESAIrConnected",            ESAIrConnected, },
    {     "ESAIrBlocked",              ESAIrBlocked, },
    {     "ESAIrDisConnected",         ESAIrDisConnected, },
    {     "ESAIrUnloaded",             ESAIrUnloaded, },

    { "KSAUidSoftwareInstallKeyValue", KSAUidSoftwareInstallKeyValue },
    { "KSAUidJavaInstallKeyValue",     KSAUidJavaInstallKeyValue },
    { "KUidSwiLatestInstallation",     KUidSwiLatestInstallation },
    { "KUidJmiLatestInstallation",     KUidJmiLatestInstallation },
    { "KUidUnifiedCertstoreFlag",      KUidUnifiedCertstoreFlag },
    { "KUidBackupRestoreKey",          KUidBackupRestoreKey },

    { 0, 0 }
};

static PyObject *
systemagent_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    sSystemAgent *self;
    self = (sSystemAgent *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int
systemagent_init(sSystemAgent *self, PyObject *args, PyObject *kwds)
{
    return 0;
}

static void
systemagent_dealloc(sSystemAgent* self)
{
    self->ob_type->tp_free((PyObject*)self);
}

PyTypeObject tSystemAgent = {
    PyObject_HEAD_INIT(NULL)
    0,                                                 // ob_size
    "properties.SystemAgent",                          // tp_name
    sizeof(sSystemAgent),                              // tp_basicsize
    0,                                                 // tp_itemsize
    (destructor)systemagent_dealloc,                   // tp_dealloc
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
    "SystemAgent objects",                             // tp_doc
    0,                                                 // tp_traverse
    0,                                                 // tp_clear
    0,                                                 // tp_richcompare
    0,                                                 // tp_weaklistoffset
    0,                                                 // tp_iter
    0,                                                 // tp_iternext
    systemagent_methods,                               // tp_methods
    0, //property_members,                             // tp_members
    0,                                                 // tp_getset
    0,                                                 // tp_base
    0,                                                 // tp_dict
    0,                                                 // tp_descr_get
    0,                                                 // tp_descr_set
    0,                                                 // tp_dictoffset
    (initproc)systemagent_init,                        // tp_init
    0,                                                 // tp_alloc
    systemagent_new,                                   // tp_new
};

