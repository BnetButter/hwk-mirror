#ifndef _OBJECT_H
#define _OBJECT_H

#include <stddef.h>
#include <stdio.h>
#include <assert.h>

#include "./include/object.h"

/* private io base definitions. use for subclassing */

struct Object {const void * class;};

struct method
{
    void (*method)();
    void (*selector)();
};

struct Type
{   
    /* superclass */
    const struct Object _;

    /* attributes */
    const char * name;
    const void * super;
    size_t size;
    
    /* class specific implementation*/
    struct method ctor;
    struct method dtor;
    struct method new;
    struct method delete;
};
#endif