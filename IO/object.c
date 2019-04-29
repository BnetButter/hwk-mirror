#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <stddef.h>
#include <assert.h>
#include "_object.h"

/* attributes */
const void * const type(const void * _self)
{
    const struct Object  * self = _self;
    assert(self && self->class);
    return self->class;
}

size_t sizeOf(const void * _self)
{
    const struct Type * class = type(_self);
    return class->size;
}
 
method_t super(const void * const _class, const void * selector)
{
    const struct Type * class = _class;
    const struct Type * superclass = class->super;
    if (! selector)
        return (method_t) superclass;

    int nmeth = ((sizeOf(superclass)
            - offsetof(struct Type, new))
                / sizeof(struct method));
    
    const struct method * p = & superclass->ctor;
    do {
        if (p->selector == selector)
            return p->method;
    } while (++p, --nmeth);
    return (method_t) 0;
}

/* public methods  */
void * ctor(void * _self, va_list * app)
{
    const struct Type * class = type(_self);    
    assert(class->ctor.method);
    return ((void * (*)()) class->ctor.method)(_self, app);
}

void * dtor(void * _self)
{
    const struct Type * class = type(_self);
    assert(class->dtor.method);
    return ((void * (*)()) class->dtor.method)(_self);
}

void * allocate(const void * const _class)
{
    const struct Type * class = _class;
    assert(class->size);
    struct Object * result = calloc(1, class->size);
    result->class = class;
    return result;
}

void * new(const void * const _class, ...)
{
    const struct Type * class = _class;
    assert (class->new.method);
    va_list ap; va_start(ap, _class);
    void * result = ((void * (*)()) class->new.method)(_class, & ap);
    va_end(ap);
    return result;
}

void delete(void * _self)
{
    const struct Type * class = type(_self);
    assert (class->delete.method);
    ((void (*)()) class->delete.method)(_self);
}

static void * object_ctor(void * _self, va_list * app) {return _self;}

static void * object_dtor(void * _self) {return _self;}

static void * object_new(const void * const _class, va_list * app)
{
    const struct Type * class = _class;
    struct Object * result = calloc(1, class->size);
    result->class = class;
    if (! class->ctor.method)
        return result;
    return ((void * (*)()) class->ctor.method)(result, app);
}

static void object_delete(void * _self)
{
    const struct Type * class = type(_self);
    assert(class->dtor.method);
    free(((void * (*)()) class->dtor.method)(_self));
}


static void * Type_ctor(void * _self, va_list * app)
{
    struct Type * self = _self;
    /*
        new(type, "name", superclass, size, 
                ctor, name_ctor, // override superclass.ctor
                (void *)0);
    
        ask the metaclass 'type' to derive <class 'name'>
        from 'superclass' of size 'size' with '*methods'

        name, superclass, and size are not inherited.
    */

    self->name = va_arg(*app, const char *);
    self->super = va_arg(*app, const void *);
    self->size = va_arg(*app, size_t);

    /* inherit superclass methods */
    size_t offset = offsetof(struct Type, ctor);
    memcpy((char *) self + offset,
        (char *) self->super + offset,
        (size_t) sizeOf(self->super) - offset);

    /* override methods if passed to va_list.
       we make a copy of *app because the loop below
       will consume all arguments.

       we need *app to be intact so subclass constructor
       can perform its own initializations.
     */

    va_list ap; va_copy(ap, *app);
    method_t selector;
    while ((selector = va_arg(ap, method_t))) {
        method_t method = va_arg(ap, method_t);
        /* methods must be passed as selector-method pairs
           to decouple struct offset and the order the parameters
           are passed in.

           we also need the selector since it's how super looks up
           the method itself.
        */
        if (selector == (method_t) ctor) {
            self->ctor.selector = selector;
            self->ctor.method = method;
            continue;
        }

        if (selector == (method_t) dtor) {
            self->dtor.selector = selector;
            self->dtor.method = method;
            continue;
        }

        if (selector == (method_t) new) {
            self->new.selector = selector;
            self->new.method = method;
            continue;
        }

        if (selector == (method_t) delete) {
            self->delete.selector = selector;
            self->delete.method = method;
            continue;
        }
    }
    va_end(ap);
    return self;
}

static void * Type_dtor(void * _self)
{   
    /* nothing to do here.
    freeing a class is a bad idea.
    so we prevent that by returning NULL */
    return NULL;
}


/* static root classes */
static const struct Type _Object;
static const struct Type _Type;


static const struct Type _Object = {
    {& _Type},           // object.class
    "object",              // name
    & _Object,             // super
    sizeof(struct Object    ), // size
    {(method_t) object_ctor, (method_t) ctor},
    {(method_t) object_dtor, (method_t) dtor},
    {(method_t) object_new,  (method_t) new},
    {(method_t) object_delete, (method_t) delete}, 

};
 
static const struct Type _Type = {
    {& _Type},           // metaclass to itself
    "IOType",
    & _Object,
    sizeof(struct Type),
    {(method_t) Type_ctor,  (method_t) ctor},
    {(method_t) Type_dtor,  (method_t) dtor},
    {(method_t) object_new,   (method_t) new},
    {(method_t) object_delete,(method_t) delete},
};

const void * const Object(void){return & _Object;}
const void * const Type(void) {return & _Type;}