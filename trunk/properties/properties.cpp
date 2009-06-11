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

#define property_type_string "properties.PropertyType"
#define type_Property (*(PyTypeObject*)SPyGetGlobalString(property_type_string))

#define RETURN_PYNONE \
  Py_INCREF(Py_None);\
  return Py_None;

extern "C" {

    /* helper function */
	static TUint getsid()
	{
		RProcess process;
		return process.SecureId();
	}

	typedef struct
	{
		PyObject_HEAD;
		TUid uid;
		TUint key;
		TUint type;
		TInt size;
		RProperty property;
	} obj_Property;
		
	typedef struct
	{
		PyObject_HEAD;
		TInt size;
        TInt pos;
		RBuf8 buffer;
	} obj_Buffer;
/*	
	static PyObject * 
	Subscribe(PyObject* self, PyObject* args) 
	{
		PyObject* callback = NULL;
	
		if (!PyArg_ParseTuple(args, "O:SubscribeInt", &callback)) 
		{
			PyErr_SetString(PyExc_TypeError, "Subscribe requires a callback parameter");
			return NULL;  
		}
	
		if (!PyCallable_Check(callback))
		{
			PyErr_SetString(PyExc_TypeError, "Callback must be a callable method");
			return NULL;
		}
		
		return NULL;
	}
*/
	static PyObject *
	Buffer_Reset(obj_Buffer *self, PyObject *args)
	{
	    //self->ptr = self->buffer.Des();
	    self->pos = 0;
	    RETURN_PYNONE;
	}

	static PyObject *
	Buffer_WriteInt8(obj_Buffer *self, PyObject *args)
	{
	    TInt8 *ptr = (TInt8 *) &self->buffer[self->pos];
		if (PyArg_ParseTuple(args, "b", ptr)) 
		{
		    self->pos += 1;
		    RETURN_PYNONE;
		}	
		return NULL;
	}
	
	static PyObject *
	Buffer_ReadInt8(obj_Buffer *self, PyObject */*args*/)
	{
        TInt8 *ptr = (TInt8 *) &self->buffer[self->pos];
        self->pos += 1;
	    return Py_BuildValue("b",*ptr);
	}

	static PyObject *
	Buffer_WriteInt16(obj_Buffer *self, PyObject *args)
	{
	    TInt16 *ptr = (TInt16 *) &self->buffer[self->pos];
		if (PyArg_ParseTuple(args, "h", ptr)) 
		{
		    self->pos += 2;
		    RETURN_PYNONE;
		}	
		return NULL;
	}
	
	static PyObject *
	Buffer_ReadInt16(obj_Buffer *self, PyObject */*args*/)
	{
        TInt16 *ptr = (TInt16 *) &self->buffer[self->pos];
        self->pos += 2;
	    return Py_BuildValue("h",*ptr);
	}

	static PyObject *
	Buffer_WriteInt32(obj_Buffer *self, PyObject *args)
	{
	    TInt32 *ptr = (TInt32 *) &self->buffer[self->pos];
		if (PyArg_ParseTuple(args, "i", ptr)) 
		{
		    self->pos += 4;
		    RETURN_PYNONE;
		}	
		return NULL;
	}
	
	static PyObject *
	Buffer_ReadInt32(obj_Buffer *self, PyObject */*args*/)
	{
        TInt32 *ptr = (TInt32 *) &self->buffer[self->pos];
        self->pos += 4;
	    return Py_BuildValue("i",*ptr);
	}

	static PyObject *
	Buffer_WriteInt64(obj_Buffer *self, PyObject *args)
	{
	    TInt64 *ptr = (TInt64 *) &self->buffer[self->pos];
		if (PyArg_ParseTuple(args, "l", ptr)) 
		{
		    self->pos += 8;
		    RETURN_PYNONE;
		}	
		return NULL;
	}
	
	static PyObject *
	Buffer_ReadInt64(obj_Buffer *self, PyObject */*args*/)
	{
        TInt64 *ptr = (TInt64 *) &self->buffer[self->pos];
        self->pos += 8;
	    return Py_BuildValue("l",*ptr);
	}

	static PyObject *
	Buffer_WriteReal32(obj_Buffer *self, PyObject *args)
	{
	    TReal32 *ptr = (TReal32 *) &self->buffer[self->pos];
		if (PyArg_ParseTuple(args, "f", ptr)) 
		{
		    self->pos += 4;
		    RETURN_PYNONE;
		}	
		return NULL;
	}
	
	static PyObject *
	Buffer_ReadReal32(obj_Buffer *self, PyObject */*args*/)
	{
        TReal32 *ptr = (TReal32 *) &self->buffer[self->pos];
        self->pos += 4;
	    return Py_BuildValue("f",*ptr);
	}
	
	static PyObject *
	Buffer_WriteReal64(obj_Buffer *self, PyObject *args)
	{
	    TReal64 *ptr = (TReal64 *) &self->buffer[self->pos];
		if (PyArg_ParseTuple(args, "d", ptr)) 
		{
		    self->pos += 8;
		    RETURN_PYNONE;
		}	
		return NULL;
	}
	
	static PyObject *
	Buffer_ReadReal64(obj_Buffer *self, PyObject */*args*/)
	{
        TReal64 *ptr = (TReal64 *) &self->buffer[self->pos];
        self->pos += 8;
	    return Py_BuildValue("d",*ptr);
	}
	
	static PyObject *
	Buffer_WriteString(obj_Buffer *self, PyObject *args)
	{
	    char *buf;
	    int size;
	    TInt32 *psize = (TInt32 *) &self->buffer[self->pos];
	    TUint8 *pstring = &self->buffer[self->pos+4];
		if (PyArg_ParseTuple(args, "s#", &buf, &size)) 
		{
		    *psize = size;
		    memcpy( pstring, buf, size );
		    self->pos += (size+4);
		    RETURN_PYNONE;
		}	
		return NULL;
	}
	
	static PyObject *
	Buffer_ReadString(obj_Buffer *self, PyObject */*args*/)
	{
		TInt32 *psize = (TInt32 *) &self->buffer[self->pos];
		TUint8 *pstring = &self->buffer[self->pos+4];
        self->pos += (*psize+4);
	    return Py_BuildValue("s#",pstring,*psize);
	}
	
	static PyMethodDef buffer_methods[] = {		
		{"Reset",        (PyCFunction)Buffer_Reset,             METH_VARARGS, "void Reset()"},
		
		{"WriteInt8",    (PyCFunction)Buffer_WriteInt8,         METH_VARARGS, "int WriteInt8(int)"},
		{"WriteInt16",   (PyCFunction)Buffer_WriteInt16,        METH_VARARGS, "int WriteInt16(int)"},
		{"WriteInt32",   (PyCFunction)Buffer_WriteInt32,        METH_VARARGS, "int WriteInt32(int)"},
		{"WriteInt64",   (PyCFunction)Buffer_WriteInt64,        METH_VARARGS, "int WriteInt64(int)"},
		{"WriteReal32",  (PyCFunction)Buffer_WriteReal32,       METH_VARARGS, "int WriteReal32(float)"},
		{"WriteReal64",  (PyCFunction)Buffer_WriteReal64,       METH_VARARGS, "int WriteReal64(float)"},
		{"WriteString",  (PyCFunction)Buffer_WriteString,       METH_VARARGS, "int WriteString(string)"},

		{"ReadInt8",     (PyCFunction)Buffer_ReadInt8,          METH_VARARGS, "int ReadInt8(int)"},
		{"ReadInt16",    (PyCFunction)Buffer_ReadInt16,         METH_VARARGS, "int ReadInt16(int)"},
		{"ReadInt32",    (PyCFunction)Buffer_ReadInt32,         METH_VARARGS, "int ReadInt32(int)"},
		{"ReadInt64",    (PyCFunction)Buffer_ReadInt64,         METH_VARARGS, "int ReadInt64(int)"},
		{"ReadReal32",   (PyCFunction)Buffer_ReadReal32,        METH_VARARGS, "int ReadReal32(float)"},
		{"ReadReal64",   (PyCFunction)Buffer_ReadReal64,        METH_VARARGS, "int ReadReal64(float)"},
		{"ReadString",   (PyCFunction)Buffer_ReadString,        METH_VARARGS, "int ReadString(string)"},

		{NULL,NULL}           /* sentinel */
	};
	
	static PyObject *
	Buffer_new(PyTypeObject *type, PyObject */*args*/, PyObject */*kwds*/)
	{
		obj_Buffer *self;
		
		self = (obj_Buffer *)type->tp_alloc(type, 0);
		if (self != NULL) {
			self->size = 0;
			self->pos = 0;
		}
		
		return (PyObject *)self;
	}
	
	static int
	Buffer_init(obj_Buffer *self, PyObject *args, PyObject */*kwds*/)
	{
		if (! PyArg_ParseTuple(args, "i", &self->size))
			return -1;

        self->buffer.CreateMaxL(self->size);
        return 0;
	}
	
	static PyTypeObject BufferType = {
		PyObject_HEAD_INIT(0)
		0,                             /*ob_size*/
		"properties.Buffer",           /*tp_name*/
		sizeof(obj_Buffer),            /*tp_basicsize*/
		0,                             /*tp_itemsize*/
		0, //(destructor)Property_dealloc, /*tp_dealloc*/
		0,                             /*tp_print*/
		0,                             /*tp_getattr*/
		0,                             /*tp_setattr*/
		0,                             /*tp_compare*/
		0,                             /*tp_repr*/
		0,                             /*tp_as_number*/
		0,                             /*tp_as_sequence*/
		0,                             /*tp_as_mapping*/
		0,                             /*tp_hash */
		0,                             /*tp_call*/
		0,                             /*tp_str*/
		0,                             /*tp_getattro*/
		0,                             /*tp_setattro*/
		0,                             /*tp_as_buffer*/
		Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
		"Buffer objects",              /* tp_doc */
		0,    		                   /* tp_traverse */
		0,		                       /* tp_clear */
		0,		                       /* tp_richcompare */
		0,		                       /* tp_weaklistoffset */
		0,		                       /* tp_iter */
		0,		                       /* tp_iternext */
		buffer_methods,        		   /* tp_methods */
		0,                             /* tp_members */
		0,                             /* tp_getset */
		0,                             /* tp_base */
		0,                             /* tp_dict */
		0,                             /* tp_descr_get */
		0,                             /* tp_descr_set */
		0,                             /* tp_dictoffset */
		(initproc)Buffer_init,         /* tp_init */
		0,                             /* tp_alloc */
		Buffer_new,                    /* tp_new */
	};

	static PyObject *
	Property_Get(obj_Property *self, PyObject *args)
	{
		switch (self->type)
		{
			case RProperty::EInt:
			{
				TInt value = 0;
				TInt err = self->property.Get( value );
				if (err != KErrNone)
					return SPyErr_SetFromSymbianOSErr(err);
				
				return Py_BuildValue("i",value);
			}
			case RProperty::EByteArray:
			{
				obj_Buffer *b = (obj_Buffer *) Buffer_new(&BufferType,NULL,NULL);
				Buffer_init(b,Py_BuildValue("(i)",self->size),NULL);
				
				TInt err = self->property.Get( b->buffer );
				if (err != KErrNone)
					return SPyErr_SetFromSymbianOSErr(err);
				
				Py_INCREF(b);
				return (PyObject *) b;
			}
			case RProperty::ELargeByteArray:
				break;
			default:
				break;
		}
		RETURN_PYNONE;
	}
	
	static PyObject *
	Property_Set(obj_Property *self, PyObject *args)
	{
	    switch (self->type)
	    {
    	    case RProperty::EInt:
    			{
    				TInt value = 0;
    				if (!PyArg_ParseTuple(args, "i", &value))
    					return NULL;  
    			
    				TInt err = self->property.Set( value );
    				if (err != KErrNone)
    					return SPyErr_SetFromSymbianOSErr(err);
    				
    				break;
    			}
    	    case RProperty::EByteArray:
			{
				obj_Buffer *b;
				if (!PyArg_ParseTuple(args, "O!:SetBuffer", &BufferType, &b))
					return NULL;  
			
				TInt err = self->property.Set( b->buffer );
				if (err != KErrNone)
					return SPyErr_SetFromSymbianOSErr(err);
				
				break;
			}
    	    case RProperty::ELargeByteArray:
    	    	break;
    	    default:
    	    	break;
	    }
		
	    RETURN_PYNONE;
	}
	
	static PyObject *
	Property_new(PyTypeObject *type, PyObject */*args*/, PyObject */*kwds*/)
	{
		obj_Property *self;
		
		self = (obj_Property *)type->tp_alloc(type, 0);
		if (self != NULL) {
			self->uid.iUid = 0;
			self->key = 0;
			self->size = 128;
			self->type = 0;
		}
		
		return (PyObject *)self;
	}
	
	static int
	Property_init(obj_Property *self, PyObject *args, PyObject *kwds)
	{
		static char *kwlist[] = {"uid", "key", "type", "size", NULL};
		TInt err;
		
		if (! PyArg_ParseTupleAndKeywords(args, kwds, "kkk|k", kwlist,
										  &self->uid,
										  &self->key,
										  &self->type,
										  &self->size))
			return -1;

		err = RProperty::Define(self->uid, self->key, self->type); 
		if ((err != KErrNone) && (err != KErrAlreadyExists))
			return err;

		err = self->property.Attach(self->uid, self->key, EOwnerThread); 
		if (err != KErrNone)
			return err;

        return 0;
	}
	
	static PyMethodDef property_methods[] = {
		{"Get",            (PyCFunction)Property_Get,         METH_VARARGS, "void Get()"},
		{"Set",            (PyCFunction)Property_Set,         METH_VARARGS, "void Set()"},
		//{"Delete",         (PyCFunction)DeleteInt,         METH_VARARGS, "void Delete()"},
		//{"Subscribe",      (PyCFunction)Subscribe,         METH_VARARGS, "void Subscribe(callable)"},
		{NULL,NULL}           /* sentinel */
	};
	
	static PyTypeObject PropertyType = {
		PyObject_HEAD_INIT(0)
		0,                             /*ob_size*/
		"properties.Property",   /*tp_name*/
		sizeof(obj_Property),    /*tp_basicsize*/
		0,                             /*tp_itemsize*/
		0, //(destructor)Property_dealloc, /*tp_dealloc*/
		0,                             /*tp_print*/
		0,                             /*tp_getattr*/
		0,                             /*tp_setattr*/
		0,                             /*tp_compare*/
		0,                             /*tp_repr*/
		0,                             /*tp_as_number*/
		0,                             /*tp_as_sequence*/
		0,                             /*tp_as_mapping*/
		0,                             /*tp_hash */
		0,                             /*tp_call*/
		0,                             /*tp_str*/
		0,                             /*tp_getattro*/
		0,                             /*tp_setattro*/
		0,                             /*tp_as_buffer*/
		Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
		"Property objects",         /* tp_doc */
		0,    		                   /* tp_traverse */
		0,		                       /* tp_clear */
		0,		                       /* tp_richcompare */
		0,		                       /* tp_weaklistoffset */
		0,		                       /* tp_iter */
		0,		                       /* tp_iternext */
		property_methods,        /* tp_methods */
		0,                             /* tp_members */
		0,                             /* tp_getset */
		0,                             /* tp_base */
		0,                             /* tp_dict */
		0,                             /* tp_descr_get */
		0,                             /* tp_descr_set */
		0,                             /* tp_dictoffset */
		(initproc)Property_init, /* tp_init */
		0,                             /* tp_alloc */
		Property_new,            /* tp_new */
	};
	  
	static PyObject *
	GetSid(PyObject *self, PyObject */*args*/)
	{
		return PyLong_FromUnsignedLong(getsid());
	}
	
	static PyMethodDef properties_methods[] = {
		{"GetSid",            (PyCFunction)GetSid, METH_VARARGS, "int  GetSid()"},
		{NULL,NULL}           /* sentinel */
	};
	
	DL_EXPORT(void) init_properties(void)
	{
		PyObject* m;
		
		if (PyType_Ready(&BufferType) < 0)
			return;		
		if (PyType_Ready(&PropertyType) < 0)
			return;		
		
		m = Py_InitModule("_properties", properties_methods);
		
		if (m == NULL)
			return;
		  
		Py_INCREF(&BufferType);
		PyModule_AddObject(m, "Buffer", (PyObject *)&BufferType);
		Py_INCREF(&PropertyType);
		PyModule_AddObject(m, "Property", (PyObject *)&PropertyType);
	}
	
} // Extern "C"
