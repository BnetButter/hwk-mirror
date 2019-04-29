#include "drawertype.h"
#include "_drawertype.h"

static void * DrawerType_ctor(void * _self, va_list * app)
{
    struct DrawerType * self = _self;
    super(DrawerType(), ctor)(self, app);
    va_list ap; va_copy(ap, *app);
    method_t selector;
    while ((selector = va_arg(ap, method_t))) {
        method_t method = va_arg(ap, method_t);
        if (selector == (method_t) dopen) {
            self->dopen.selector = selector;
            self->dopen.method = method;
            continue;
        }
        if (selector == (method_t) is_open) {
            self->is_open.selector = selector;
            self->is_open.method = method;
            continue;
        }

        if (selector == (method_t) lock) {
            self->lock.selector = selector;
            self->lock.method = method;
            continue;
        }

        if (selector == (method_t) unlock) {
            self->unlock.selector = selector;
            self->unlock.method = method;
            continue;
        }
                
    }
    va_end(ap);
    return self;
}

static const void * _DrawerType;
const void * const DrawerType(void)
{
    return _DrawerType ? _DrawerType : (_DrawerType = new(
            Type(), "DrawerType",
            IOType(), sizeof(struct DrawerType),
            ctor, DrawerType_ctor,
            (void *) 0));
}

#define SELECTOR(_method, ...) \
        const struct DrawerType * class = type(_self);\
        assert(class->_method.method); \
        return ((int (*)()) class->_method.method)(__VA_ARGS__)

bool is_open(void * _self){SELECTOR(is_open, _self);}

int dopen(void * _self){SELECTOR(dopen, _self);}

int lock(void * _self){SELECTOR(lock, _self);}

int unlock(void * _self){SELECTOR(unlock, _self);}



