#include <stdlib.h>
#include "adafruit/printer.h"


struct printer * Printer(void)
{
    struct printer * p = calloc(1, sizeof(struct printer));
    printer_ctor(p, "/dev/serial0");
    return p;
}

#define writeline(self, line, ...) \
        printer_writeline(self, line, (struct line_option ) {\
        .justify='L', .bold=0, .underline=0, .size='S', __VA_ARGS__})


int main(void)
{
    const char * receipt[] = {
        "001",
        "Cheeseburger",
        "    + Onions",
        "    + Lettuce",
        "    + Tomatoes",
        "    + Pickles",
        "  French Fries",
        "  Coffee",
        "    + Large",
        "Total: $00.00",
    };

    struct printer * p = Printer();
    writeline(p, receipt[0], .size='L', .bold=1, .justify='C');
    writeline(p, receipt[1], .size='M');
    for (int i = 0; i < 4; i++)
        writeline(p, receipt[2 + i]);
    for (int i = 0; i < 2; i++)
        writeline(p, receipt[6 + i], .size='M');
    writeline(p, receipt[8]);
    writeline(p, receipt[9], .size='L', .justify='C');
}