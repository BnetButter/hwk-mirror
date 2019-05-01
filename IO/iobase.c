#include "./include/object.h"
#include "./include/iobase.h"
#include "_iobase.h"
#include "./include/iotype.h"
#include <signal.h>
#include <string.h>
#include <stdlib.h>


/*  Since IOBase is meant to be subclassed,
    these methods simply wraps stdio's functions.
    ctor and dtor wraps fopen and fclose respectively.
 */

static void * IOBase_ctor(void * _self, va_list * app)
{
    struct IOBase * self = _self;
    const char * path = va_arg(*app, const char *);
    const char * mode = va_arg(*app, const char *);
    self->stream = fopen(path, mode);
    if (! self->stream)
        raise(2);
    return self;
}

static void * IOBase_dtor(void * _self)
{
    struct IOBase * self = _self;
    fclose(self->stream);
    return self;
}

static int IOBase_write(void * _self, int c)
{
    struct IOBase * self =  _self;
    return fputc(c, self->stream);
}

static size_t IOBase_read(void * _self, char * buf)
{
    struct IOBase * self = _self;
    fseek(self->stream, 0, SEEK_END);
    size_t size = ftell(self->stream) + 1;
    rewind(self->stream);

    if (! buf)
        buf = malloc(size);
    if (buf) // check malloc
        return fread(buf, 1, size, self->stream);
    return 0;
}

static int IOBase_flush(void * _self)
{
    struct IOBase * self = _self;
    return fflush(self->stream);
}

static int IOBase_seek(void * _self, size_t offset, int origin)
{
    struct IOBase * self = _self;
    return fseek(self->stream, offset, origin);
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
        seek, IOBase_seek,
        flush, IOBase_flush,
        (void *)0));
}