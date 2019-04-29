#ifndef _DRAWERTYPE_H
#define _DRAWERTYPE_H

#include "_iotype.h"

struct DrawerType 
{
    const struct IOType _;
    struct method is_open;
    struct method dopen;
    struct method lock;
    struct method unlock;
};

const void * const DrawerType(void);


#endif