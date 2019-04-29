#ifndef _COLLECTIONS_H
#define _COLLECTIONS_H
#include "_object.h"
#include "_arraytype.h"

struct list
{
    const struct Object _;
    size_t count;
    size_t allocation_size;
    void ** array;
};

struct item
{
    char * key;
    void * value;
};
 
struct dict {
    const struct Object _;
    size_t count;
    size_t base_size;
    size_t size;
    struct item ** items;
};

#define PRIME_1 151
#define PRIME_2 163
#define DICT_BASE_SIZE 20
#define LIST_BASE_SIZE 10
#define ARGC_MAX       25
#define COUNT(self)  (((struct list *) (self))->count)


#endif