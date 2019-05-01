#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>
#include <stdint.h>

#include "_object.h"
#include "object.h"
#include "_arraytype.h"
#include "_collections.h"


/* forward declarations */
const void * const list(void);
const void * const dict(void);
const void * const Arguments(void);
const void * const KeywordArguments(void);

static void expand(void *);
static void shrink(void *);
static char * stringcopy(char *, const char *);
static void * new_item(char *, void *);
static void del_item(struct item *);
static int ht_hash(const char *, const int, const int);
static int ht_get_hash(const char *, const int, int);
static int is_prime(const int);
static int next_prime(int); 
static void resize_up(struct dict *);
static void resize_down(struct dict *);
static void list_resize(struct list *);


/* list class */



static void * list_ctor(void * _self, va_list * app)
{
    struct list * self = _self;
    self->allocation_size = LIST_BASE_SIZE;
    self->array = calloc(LIST_BASE_SIZE, sizeof(void *));
    return self;
}
static void * list_dtor(void * _self)
{
    struct list * self = _self;
    free(self->array), self->array = NULL;
    return self;
}

void append(void * _self, void * element)
{
    struct list * self = _self;
    assert(self);
    if (COUNT(self) + 1 > self->allocation_size)
        expand(self);
    self->array[COUNT(self)] = element;
    COUNT(self) += 1;
}

static void * list_pop(void * _self, long unsigned index)
{
    struct list * self = _self;
    assert(index < COUNT(self));
    void * retval = self->array[index];
    if (index == COUNT(self) - 1) {
        COUNT(self) -= 1;
        list_resize(self);
        return retval;
    }
    for (int i = index; i < COUNT(self); i++)
        self->array[i] = self->array[i + 1];
    COUNT(self) -= 1;
    list_resize(self);
    return retval;
}
static void list_insert(void * _self, long unsigned index, void * element)
{
    struct list * self = _self;
    assert(index <= COUNT(self));
    list_resize(self);

    for (long unsigned i = COUNT(self); i-- > index;) {
        self->array[i + 1] = self->array[i];
    }
    
    self->array[index] = element;
    COUNT(self) += 1;
}
static void * list_get(void * _self, long unsigned index)
{   
    struct list * self = _self;
    assert(self);
    assert(index < COUNT(self));
    return self->array[index];
}

static int list_clear(void * _self)
{
    struct list * self = _self;
    memset(self->array, 0, self->allocation_size);
    self->count = 0;
    return self->array ? 1 : 0;
}

static long unsigned list_len(void * _self) {return COUNT(_self);}


static const void * _list;
const void * const list(void)
{
    return _list ? _list : (_list = new(
        ArrayType(), "list",
        Object(), sizeof(struct list),
        ctor, list_ctor,
        dtor, list_dtor,
        pop, list_pop,
        insert, list_insert,
        get, list_get,
        clear, list_clear,
        len, list_len,
        (void *) 0));
}

static void expand(void * _self)
{   
    struct list * self = _self;
    size_t new_size = self->allocation_size * 2 * sizeof(void *);
    self->array = realloc(self->array, new_size);
    assert(self->array);
    self->allocation_size = self->allocation_size * 2;
}

static void shrink(void * _self)
{  
    struct list * self = _self;
    size_t new_size = sizeof(void *) * (self->allocation_size / 2);
    assert(COUNT(self) < self->allocation_size / 4);
    self->array = realloc(self->array, new_size);
    assert(self->array);
    self->allocation_size = self->allocation_size / 2;
}

static void list_resize(struct list * self)
{
    if (self->count + 1 > self->allocation_size)
        expand(self);
    else if (! ((self->allocation_size / 4) < LIST_BASE_SIZE))
        if (COUNT(self) < self->allocation_size / 4)
            shrink(self);
}
/* dict class */

static const struct item dct_null_item = {NULL, NULL};
const void * NULL_ITEM =  & dct_null_item;
#define occupancy(n, d) (n * 100) / d

static void * dict_ctor(void * _self, va_list * app)
{
    struct dict * self = _self;
    super(dict(), ctor)(self, app);

    self->base_size = DICT_BASE_SIZE;
    self->size = next_prime(self->base_size);
    COUNT(self) = 0;
    self->items = calloc(self->size, sizeof(void *));
    return self;
}

static void * dict_dtor(void * _self)
{
    struct dict * self = _self;
    for (int i = 0; i < self->size; i++) {
        struct item * item = self->items[i];
        if (item != NULL)
            del_item(item);
    }
    free(self->items), self->items = NULL;
    return self;
}


static int dict_insert(void * _self, char * key, void * value)
{   
    struct dict * self = _self;
    const int occupancy = COUNT(self) * 100 / self->size;
    if (occupancy > 70)
        resize_up(self);
    
    struct item * item = new_item(key, value);
    int index = ht_get_hash(item->key, self->size, 0);
    struct item * cur_item = self->items[index];
    int i = 1;
    while (cur_item != NULL && cur_item != (void *) NULL_ITEM)
    {
        if (strcmp(cur_item->key, key) == 0)
        {
            del_item(cur_item);
            self->items[index] = item;
            return 1;
        }
        index = ht_get_hash(item->key, self->size, i);
        cur_item = self->items[index];
        i++;
    }
    self->items[index] = item;
    COUNT(self) ++;
    return 1;
}

static void * dict_get(void * _self, char * key) 
{
    struct dict * self = _self;
    int index = ht_get_hash(key, self->size, 0);
    struct item * item = self->items[index];
    int i = 1;
    while (item != NULL) {
        if (item != (void *) NULL_ITEM) {
            if (strcmp(item->key, key) == 0) {
            return item->value;
            }
        }
        index = ht_get_hash(key, self->size, i);
        item = self->items[index];
        i++;
    } 
    return NULL;
}

static void * dict_pop(void * _self, char * key)
{
    struct dict * self = _self;
    int occupied = COUNT(self) * 100 / self->size;
    if (occupied < 10)
        resize_down(self);
   
    int index = ht_get_hash(key, self->size, 0);
    struct item * item = self->items[index];
    int i = 1;
    while (item != NULL) {
        if (item != (void *) NULL_ITEM) {
            if (strcmp(item->key, key) == 0) {
                void * retval = item->value;
                del_item(item);
                self->items[index] = (void *) NULL_ITEM;
                COUNT(self) --;
                return retval;
            }
        }
        index = ht_get_hash(key, self->size, i);
        item = self->items[index];
        i++;
    } 
    return NULL;
}


static int dict_clear(void * _self)
{
    struct dict * self = _self;
    for (int i = 0; i < self->size; i++)
        if (self->items[i] != NULL && self->items[i] != NULL_ITEM)
            del_item(self->items[i]);
    memset(self->items, 0, self->size);
    self->count = 0;
    return 1;
}

static const void * _dict;
const void * const dict(void)
{
    return _dict ? _dict :(_dict = new(
        ArrayType(), "dict",
        Object(), sizeof(struct dict),
        ctor, dict_ctor,
        dtor, dict_dtor,
        insert, dict_insert,
        pop, dict_pop,
        get, dict_get,
        clear, dict_clear,
        len, list_len,
        (void *) 0));
}

size_t dict_keys(void * _self, const char ** buf)
{
    struct dict * self = _self;
    size_t keycount = 0;
    for (int i =0; i < self->size; i++)
        if (self->items[i] && self->items[i] != NULL_ITEM)
            buf[keycount] = self->items[i]->key,
            keycount ++;
    return keycount;
}

static char * stringcopy(char * d, const char * s)
{
    d = malloc(strlen(s) + 1);
    memcpy(d, s, strlen(s) + 1);
    return d;
} 

static void * new_item(char * key, void * value)
{
    struct item * self = malloc(sizeof(struct item));
    self->key = stringcopy(self->key, key);
    self->value = value;
    return self;
}

static void del_item(struct item * item)
{   
    if (item != (void *) NULL_ITEM) {
        free(item->key), item->key = NULL;
        free(item);
    }
}

static int ht_hash(const char* s, const int a, const int m) {
    long hash = 0;
    const int len_s = strlen(s);
    for (int i = 0; i < len_s; i++) {
        hash += (long)pow(a, len_s - (i+1)) * s[i];
        hash = hash % m;
    }
    return (int)hash;
}
static int ht_get_hash(const char* s,
        const int num_buckets, const int attempt)
{
    const int hash_a = ht_hash(s, PRIME_1, num_buckets);
    const int hash_b = ht_hash(s, PRIME_2, num_buckets);
    return (hash_a + (attempt * (hash_b + 1))) % num_buckets;
}

static int is_prime(const int x) 
{
    if (x < 2) { return -1; }
    if (x < 4) { return 1; }
    if ((x % 2) == 0) { return 0; }
    for (int i = 3; i <= floor(sqrt((double) x)); i += 2) {
        if ((x % i) == 0) {
            return 0;
        }
    }
    return 1;
}

static int next_prime(int x) 
{
    while (is_prime(x) != 1) {
        x++;
    }
    return x;
}

static void resize(void * _self, const int base_size) {
    
    if (base_size < DICT_BASE_SIZE) {
        return;
    }
    struct dict * self = _self;

    struct dict * new_ht = new(dict());
    for (int i = 0; i < self->size; i++) {
        struct item * item = self->items[i];
        if (item != NULL && item != (void *) NULL_ITEM) {
            dict_insert(new_ht, item->key, item->value);
        }
    }

    self->base_size = new_ht->base_size;
    COUNT(self) = COUNT(new_ht);

    // To delete new_ht, we give it ht's size and items 
    const int tmp_size = self->size;
    self->size = new_ht->size;
    new_ht->size = tmp_size;

    struct item ** tmp_items = self->items;
    self->items = new_ht->items;
    new_ht->items = tmp_items;
    delete(new_ht);
}

static void resize_up(struct dict * self) {
    const int new_size = self->base_size * 2;
    resize(self, new_size);
}

static void resize_down(struct dict * self) {
    const int new_size = self->base_size / 2;
    resize(self, new_size);
}


/* Arguments class*/
static char _stopiteration;
const void * StopIteration = & _stopiteration;
static void * _args[ARGC_MAX];
static size_t allocation_size = ARGC_MAX;

static void * Arguments_new(const void * const _class, va_list * app)
{
    
    struct Object * result = va_arg(*app, void *); // initialized on the stack
    memset(result, 0, ((const struct Type *) _class)->size);
    memset(_args, 0, allocation_size);
    result->class = _class;
    return ctor(result, app);
}

static void * Arguments_dtor(void * _self) {return NULL;}

static void * Arguments_ctor(void * _self, va_list * app)
{
    struct list * self = _self;
    self->allocation_size = allocation_size;
    self->array = _args;
    void * arg;
    while ((arg = va_arg(*app, void *)) != StopIteration)
        append(self, arg);
    return self;
}


static const void * _Arguments;
const void * const Arguments(void)
{
    return _Arguments ? _Arguments : (_Arguments = new(
            ArrayType(), "Arguments",
            list(), sizeof(struct list),
            ctor, Arguments_ctor,
            dtor, Arguments_dtor,
            new, Arguments_new,
            (void *) 0));
}


/* keyword arguments class */

static const void * _KeywordArguments;

static void * KeywordArguments_ctor(void * _self, va_list * app)
{
    struct dict * self = _self;
    super(KeywordArguments(), ctor)(_self, app);
    const char * key;
    while ((key = va_arg(*app, const char *))!= StopIteration)
            insert(self, (char *) key, va_arg(*app, void *));
    return self;
}

const void * const KeywordArguments(void)
{
    return _KeywordArguments ? _KeywordArguments : (_KeywordArguments = new(
            ArrayType(), "KeywordArguments",
            dict(), sizeof(struct dict),
            ctor, KeywordArguments_ctor,
            (void *) 0));
}