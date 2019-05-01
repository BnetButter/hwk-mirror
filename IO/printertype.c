#include <time.h>
#include "_printertype.h"
#include "_object.h"

#define SELECTOR(_method, ...) \
        const struct PrinterType * class = type(_self); \
        assert(class->_method.method); \
        ((void (*)()) class->_method.method)(__VA_ARGS__)

/* nothing interesting here. */

void sleep(void * _self) {SELECTOR(sleep, _self);}
void wake(void * _self) {SELECTOR(wake, _self);}
void set_timeout(void * _self, long unsigned ms){SELECTOR(set_timeout, _self, ms);}
void wait_timeout(void * _self){SELECTOR(wait_timeout, _self);}
void feed(void * _self, unsigned row){SELECTOR(feed, _self, row);}
void test_page(void * _self){SELECTOR(test_page, _self);}
void reset(void * _self){SELECTOR(reset, _self);}
method_t configure(void * _self, const char * kwd) {SELECTOR(configure, _self, kwd);}

const void * const PrinterType(void);

static void * PrinterType_ctor(void * _self, va_list * app)
{
    struct PrinterType * self = _self;
    super(PrinterType(), ctor)(self, app);
    va_list ap; va_copy(ap, *app);
    method_t selector;
    while ((selector = va_arg(ap, method_t))) {
        method_t method = va_arg(ap, method_t);
        if (selector == (method_t) sleep) {
            self->sleep.selector = selector;
            self->sleep.method = method;
            continue;
        }
        
        if (selector == (method_t) wake) {
            self->wake.selector = selector;
            self->wake.method = method;
            continue;
        }
        
        if (selector == (method_t) reset) {
            self->reset.selector = selector;
            self->reset.method = method;
            continue;
        }
        
        if (selector == (method_t) set_timeout) {
            self->set_timeout.selector = selector;
            self->set_timeout.method = method;
            continue;
        }
        
        if (selector == (method_t) wait_timeout) {
            self->wait_timeout.selector = selector;
            self->wait_timeout.method = method;
            continue;
        }

        if (selector == (method_t) test_page) {
            self->test_page.selector = selector;
            self->test_page.method = method;
            continue;
        }
        
        if (selector == (method_t) feed) {
            self->feed.selector = selector;
            self->feed.method = method;
            continue;
        }

        if (selector == (method_t) configure) {
            self->configure.selector = selector;
            self->configure.method =method;
        }
        
    }
    va_end(ap);
    return self;
}

static const void * _PrinterType;
const void * const PrinterType(void)
{
    return _PrinterType ? _PrinterType : (_PrinterType = new(
        Type(), __func__,
        IOType(), sizeof(struct PrinterType),
        ctor, PrinterType_ctor,
        (void *) 0));
}

void delay(long unsigned delay_ms)
{   
    delay_ms /= 10;
    clock_t begin = clock();
    clock_t delta_ms;
    do {
        delta_ms = ((clock() - begin) * 1000) / CLOCKS_PER_SEC;
    } while (delta_ms < delay_ms);
}


