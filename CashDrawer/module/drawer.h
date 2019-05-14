#ifndef DRAWER_H
#define DRAWER_H
#include <stdio.h>
#include <stdbool.h>
#include <wiringPi.h>


#define DRAWER_ATTR                 \
    FILE * fp;                      \
    int is_locked;                

typedef struct {DRAWER_ATTR} drawer_t;

void drawer_ctor(drawer_t *, const char *);
void drawer_open(drawer_t *);
bool is_open(drawer_t *);

#define is_locked(self) (((drawer_t *)(self))->is_locked)


#endif