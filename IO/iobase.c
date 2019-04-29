#include "./include/object.h"
#include "./include/iobase.h"
#include "_iobase.h"
#include "./include/iotype.h"
#include <signal.h>
#include <string.h>
#include <stdlib.h>


/* IOBase methods */
static void * IOBase_ctor(void * _self, va_list * app)
{
    struct IOBase * self = _self;
    // no need to call super.ctor
    const char * path = va_arg(*app, const char *);
    const char * mode = va_arg(*app, const char *);
    self->stream = fopen(path, mode);
    if (! self->stream)
        raise(1);
    return self;
}

static void * IOBase_dtor(void * _self)
{
    struct IOBase * self = _self;
    fclose(self->stream);
    return self;
}


static int IOBase_write(void * _self, const char * content)
{
    struct IOBase * self =  _self;
    return fwrite(content, 1, strlen(content), self->stream);
}

static size_t IOBase_read(void * _self, char * buf)
{
    struct IOBase * self = _self;
    fseek(self->stream, 0, SEEK_END);
    size_t size = ftell(self->stream) + 1;
    rewind(self->stream);
    buf = malloc(size);
    if (buf)
        return fread(buf, 1, size, self->stream);
    return 0;
}

static const void * _IOBase;
const void * const IOBase(void)
{
    return _IOBase ? _IOBase : (_IOBase = new(
        IOType(), "IOBase",
        Object(), sizeof(struct IOBase),
        ctor, IOBase_ctor,
        dtor, IOBase_dtor,
        read, IOBase_read,
        write, IOBase_write,
        (void *)0));
}