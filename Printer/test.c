#include "printer.h"
#include "io.h"
#include "adafruit.h"

const char * lines[] = {
        "001",
        "Hamburger", 
        "    + Lettuce",
        "    + Onions",
        "    + Tomatoes",
        "    + Lettuce",
        "  FrenchFries",
        "  Coffee",
        "    + Large"
        "Total: 7.45"};


int main(void)
{
    void * printer = new(Printer(), AdafruitPrinter);
    printline(printer, lines[0], kwargs(
        "justify", 'C',
        "size",    'L',
        "bold",    true));
    
    printline(printer, lines[1], kwargs(
        "size", 'M',
        "underline", true));
    
    for (int i = 0; i < 4; i++) 
        printline(printer, lines[i + 2], kwargs("underline", false));
    
    printline(printer, lines[6], kwargs(
        "size", 'M',
        "underline", false));
    
    printline(printer, lines[7], kwargs("size", 'M'));
    printline(printer, lines[8], kwargs("size", 'S'));
    printline(printer, lines[9], kwargs(
        "justify", 'C',
        "size", 'L'));
    delete(printer);
}