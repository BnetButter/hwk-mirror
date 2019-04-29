#ifndef _ARRAYTYPE_H
#define _ARRAYTYPE_H
#include "_object.h"
#include <stdint.h>

const void * const ArrayType(void);

struct ArrayType 
{
    const struct Type _;
    struct method len;
    struct method insert;
    struct method pop;
    struct method get;
    struct method clear;
};

long unsigned len(void *);
int clear(void *);
int insert(void *, uintptr_t, const void *);
void * pop(void *, uintptr_t);
void * get(void *, uintptr_t);

#endif