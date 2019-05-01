#ifndef IOTYPE_H
#define IOTYPE_H
#include "object.h"

extern const void * const IOType(void);

size_t write(void * self, const char * string);
size_t writeline(void * self, const char * line);
int read(void * self, char * buf);
int seek(void * self, long offset, int origin);
int flush(void * self);

#endif