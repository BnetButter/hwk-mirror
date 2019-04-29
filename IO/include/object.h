#ifndef OBJECT_H
#define OBJECT_H

/* public Object() and Type() class interface */

#include <stddef.h>
#include <stdarg.h>
#include <stdio.h>

typedef void (*method_t)();

extern const void * const Object(void); 
extern const void * const Type(void);   // metaclass

/* methods */
extern void * new(const void * const class, ...);
extern void  delete(void * self);
extern void * ctor(void * self, va_list * app);   // initializer
extern void * dtor(void * self);                  // destructor
extern void * allocate(const void * const class);
extern void * vctor(void * _self, ...);           // ctor wrapper

/* attributes */
extern size_t sizeOf(const void * self);
extern const void * const type(const void * self);
extern method_t super(const void * const class, const void * method);
#endif