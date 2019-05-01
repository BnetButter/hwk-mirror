#ifndef PRINTER_H
#define PRINTER_H
#include "io.h"
extern const void * const Printer(void); // new(Printer(), fcls);
int printline(void * self, const char * line, void * config);
int print(void * self, const char * text, void * config);

#endif