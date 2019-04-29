#ifndef _PRINTERTYPE_H
#define _PRINTERTYPE_H
#include "_iotype.h"

struct PrinterType
{
    const struct IOType _;
    struct method sleep;
    struct method wake;
    struct method reset;
    struct method set_timeout;
    struct method wait_timeout;
    struct method test_page;
    struct method feed;
    struct method configure;
};

#endif