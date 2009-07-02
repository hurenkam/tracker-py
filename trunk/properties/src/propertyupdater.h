/*
 * propertyupdater.h
 *
 *  Created on: 2-jul-2009
 *      Author: Mark
 */

#ifndef PROPERTYUPDATER_H_
#define PROPERTYUPDATER_H_

#include <e32base.h>
#include <e32property.h>
#include "symbian_python_ext_util.h"

class CPropertyUpdater : public CActive 
{
    public:
        CPropertyUpdater();

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

#endif /* PROPERTYUPDATER_H_ */
