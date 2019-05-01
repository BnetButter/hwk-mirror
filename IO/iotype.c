#include <assert.h>
#include "object.h"
#include "_iotype.h"

typedef int (*write_c)(void *, int);

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

/* calls virtual methods */


int read(void * _self, char * buffer)
{
    const struct IOType * class = type(_self);
    assert(class->read.method);
    return ((int (*)()) class->read.method)(_self, buffer);
}

size_t write(void * _self, const char * content)
{
    const struct IOType * class = type(_self);
    assert(class->write.method && content);
    size_t written = 0;
    while (*content)
        if (((write_c) class->write.method)(_self, *content ++)
                != EOF)
            written ++;
    return written;
}

size_t writeline(void * _self, const char * line)
{
    size_t written = write(_self, line);
    return written += write(_self, & (char) {'\n'});
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