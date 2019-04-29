#ifndef _IOBASE_H
#define _IOBASE_H
#include "_object.h"

struct IOBase
{
    const struct Object _;
    FILE * stream;
};
#endif