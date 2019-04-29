#ifndef _IOTYPE_H
#define _IOTYPE_H
#include "_object.h"
#include "iotype.h"

struct IOType
{   
    const struct Type _;
    struct method write;
    struct method read;
    struct method seek;
    struct method flush;
};

#endif