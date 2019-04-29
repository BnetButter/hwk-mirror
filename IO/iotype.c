#include <assert.h>
#include "object.h"
#include "_iotype.h"



static void * IOType_ctor(void * _self, va_list * app)
{
    struct IOType * self = _self;
    super(IOType(), ctor)(self, app);
    va_list ap; va_copy(ap, *app);
    method_t selector;
    while ((selector = va_arg(ap, method_t))) {
        method_t method = va_arg(ap, method_t);
        if (selector == (method_t) write) {
            self->write.selector = selector;
            self->write.method = method;
            continue;
        }

        if (selector == (method_t) read) {
            self->read.selector = selector;
            self->read.method = method;
            continue;
        }

        if (selector == (method_t) flush) {
            self->flush.selector = selector;
            self->flush.method = method;
            continue;
        }
        
        if (selector == (method_t) seek) {
            self->seek.selector = selector;
            self->seek.method = method;
            continue;
        }
        
    }
    va_end(ap);
    return self;
}

int read(void * _self, char * buffer)
{
    const struct IOType * class = type(_self);
    assert(class->read.method);
    return ((int (*)()) class->read.method)(_self, buffer);
}

int write(void * _self, const char * content)
{
    const struct IOType * class = type(_self);
    assert(class->read.method);
    return ((int (*)()) class->write.method)(_self, content);
}

int flush(void * _self)
{
    const struct IOType * class = type(_self);
    assert(class->flush.method);
    return ((int (*)()) class->flush.method)(_self);
}

int seek(void * _self, long offset, int origin)
{
    const struct IOType * class = type(_self);
    assert(class->seek.method);
    return ((int (*)())class->seek.method)(_self, offset, origin);
}



static const void * _IOType;
const void * const IOType(void)
{
    return _IOType ? _IOType : (_IOType = new(
        Type(), "IOType",
        Type(), sizeof(struct IOType),
        ctor, IOType_ctor,
        (void *) 0));
}