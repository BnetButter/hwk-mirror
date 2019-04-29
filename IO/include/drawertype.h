#ifndef DRAWERTYPE_H
#define DRAWERTYPE_H
#include <stdbool.h>

extern const void * const DrawerType(void);

bool is_open(void * _self);
int unlock(void * _self);
int lock(void * _self);
int dopen(void * _self);
#endif