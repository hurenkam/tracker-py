/*
 ============================================================================
 Name		: properties.h
 Author	  : Mark Hurenkamp
 Copyright   : This software is licenced under GPL v2
 Description : properties.h - Cproperties class header
 ============================================================================
 */

// This file defines the API for properties.dll

#ifndef __PROPERTIES_H__
#define __PROPERTIES_H__

//  Include Files
/*
#include <e32base.h>	// CBase
#include <e32std.h>	 // TBuf

//  Constants

const TInt KpropertiesBufferLength = 15;
typedef TBuf<KpropertiesBufferLength> TpropertiesExampleString;

//  Class Definitions

class Cproperties : public CBase
	{
public:
	// new functions
	IMPORT_C static Cproperties* NewL();
	IMPORT_C static Cproperties* NewLC();
	IMPORT_C ~Cproperties();

public:
	// new functions, example API
	IMPORT_C TVersion Version() const;
	IMPORT_C void ExampleFuncAddCharL(const TChar& aChar);
	IMPORT_C void ExampleFuncRemoveLast();
	IMPORT_C const TPtrC ExampleFuncString() const;

private:
	// new functions
	Cproperties();
	void ConstructL();

private:
	// data
	TpropertiesExampleString* iString;
	};
*/
class CPropertyUpdater : public CActive 
{
    public:
        CPropertyUpdater();

        //void ConstructL(CPropertyRequestor *propertyRequestor, PyObject* callback);
        void ConstructL(RProperty *property, PyObject* callback);
        virtual ~CPropertyUpdater();
        void Stop();
        void RunL();
        void DoCancel();
        void SetPropertyCallback(PyObject *callback);
        void SafeCancel();
        
    private:
        void InvokePropertyCallback(PyObject *arg);
        PyObject *iPropertyCallback;
        RProperty *iProperty;
        TThreadId iOwnerThreadId;
};


#endif  // __PROPERTIES_H__

