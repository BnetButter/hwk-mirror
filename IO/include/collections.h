#ifndef COLLECTIONS_H
#define COLLECTIONS_H
#include <stdint.h>

#include "arraytype.h"
#include "object.h"


extern const void * const list(void);
extern const void * const dict(void);

extern const void * const Arguments(void);
extern const void * const KeywordArguments(void);
extern const void * const StopIteration;

typedef void * args_t[4];
typedef void * kwargs_t[5];

#define args(...)        *(args_t *)   new(Arguments(), (args_t) {}, ## __VA_ARGS__, StopIteration)
#define kwargs(...)      *(kwargs_t *) new(KeywordArguments(), (kwargs_t) {}, ## __VA_ARGS__, StopIteration)
#define ARGC_MAX         25

extern int insert(void * self, uintptr_t location, const void * item);
extern void * get(void * self, uintptr_t location);
extern void * pop(void * self, uintptr_t location);
extern long unsigned len(void * self);
extern int clear(void * self);
void append(void * self, void * item);

#endif