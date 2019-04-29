#include "object.h"
#include "_object.h"
#include "_arraytype.h"
    
static void * ArrayType_ctor(void * _self, va_list * app)
{
    struct ArrayType * self = _self;
    super(ArrayType(), ctor)(self, app);
    va_list ap; va_copy(ap, *app);
    method_t selector;
    while ((selector = va_arg(ap, method_t))) {
        method_t method = va_arg(ap, method_t);
        if (selector == (method_t) len) {
            self->len.selector = selector;
            self->len.method = method;
            continue;
        }
        
        if (selector == (method_t) clear) {
            self->clear.selector = selector;
            self->clear.method = method;
            continue;
        }

        if (selector == (method_t) insert) {
            self->insert.selector = selector;
            self->insert.method = method;
            continue;
        }

        if (selector == (method_t) get) {
            self->get.selector = selector;
            self->get.method = method;
            continue;
        }

        if (selector == (method_t) pop) {
            self->pop.selector = selector;
            self->pop.method = method;
            continue;
        }
    }
    va_end(ap);
    return self;
}


#define SELECTOR(_return, _method, ...) \
        const struct ArrayType * class = type(_self);\
        assert(class->_method.method); \
        return ((_return (*)()) class->_method.method)(__VA_ARGS__);

int insert(void * _self, uintptr_t index, const void * item) {
    SELECTOR(int, insert, _self, index, item)
}

void * get(void * _self, uintptr_t index) {
    SELECTOR(void *, get, _self, index)
}

void * pop(void * _self, uintptr_t index) {
    SELECTOR(void *, pop, _self, index)
}

int clear(void * _self) {
    SELECTOR(int, clear, _self)
}

long unsigned len(void * _self) {
    SELECTOR(long unsigned, len, _self)
}

const void * _ArrayType;
const void * const ArrayType(void)
{
    return _ArrayType ? _ArrayType : (_ArrayType = new(
        Type(), "ArrayType",
        Type(), sizeof(struct ArrayType),
        ctor, ArrayType_ctor,
        (void *)0));
}
