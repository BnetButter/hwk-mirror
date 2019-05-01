#ifndef PRINTERTYPE_H
#define PRINTERTYEP_H
#include "iotype.h"
#include "collections.h"

/* metaclass */

extern const void * const PrinterType(void);
extern void sleep(void * self);
extern void wake(void * self);
extern void feed(void * self, unsigned rows);
extern void reset(void * self);
extern void set_timeout(void * self, long unsigned ms);
extern void wait_timeout(void * self);
extern void test_page(void * self);
extern method_t configure(void * self, const char * kwd);
extern void delay(long unsigned delay_ms);


#endif
