#ifndef IOTYPE_H
#define IOTYPE_H
#include "object.h"

extern const void * const IOType(void);

int write(void * self, const char * content);
int read(void * self, char * buf);
int seek(void * self, long offset, int origin);
int flush(void * self);

#endif