/*
 * module.h
 *
 *  Created on: 2-jul-2009
 *      Author: Mark
 */

#ifndef MODULE_H_
#define MODULE_H_

struct sConstant
{
    char *name;
    TInt value;
};

extern TUint getsid();
extern void PyModule_AddConstants(PyObject *d, sConstant *c);

#endif /* MODULE_H_ */
