#ifndef ARRAYTYPE_H
#define ARRAYTYPE_H

extern const void * const ArrayType(void);

extern int insert(void * self, uintptr_t index, const void * item);
extern int clear(void * self);
extern void * pop(void * self, uintptr_t index);
extern void * get(void * self, uintptr_t index);
extern size_t len(void * self);


#endif