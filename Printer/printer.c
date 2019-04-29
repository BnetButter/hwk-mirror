#include "_io.h"
#include "printer.h"


struct Printer
{
    const struct Object _;
    void * delegate;    
};

#define CAST    struct Printer * self = _self

static void * Printer_ctor(void * _self, va_list * app)
{
    CAST;
    const void * (*fcls)(void) = va_arg(*app, const void * (*)());
    self->delegate = new(fcls(), "/dev/serial0", "wb");
    return self;
}

static void * Printer_dtor(void * _self)
{   
    CAST;
    delete(self->delegate);
    return self;
}

static const void * _Printer;
const void * const Printer(void)
{
    return _Printer ? _Printer : (_Printer = new(
        type_t, "Printer",
        object_t, sizeof(struct Printer),
        ctor, Printer_ctor,
        dtor, Printer_dtor,
    (void *) 0));
}


int printline(void * _self, const char * line, kwargs_t line_configuration)
{
    CAST;
    configure(self->delegate, line_configuration);
    write(self->delegate, line);
}

