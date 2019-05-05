#ifndef PRINTER_H
#define PRINTER_H

#include <stdio.h>   // FILE
#include <stdint.h>  // uint8_t
#include <stdbool.h>


#define ADAFRUIT_PRINTER_ATTR       \
    FILE * stream;                  \
    unsigned long resume_time;      \
    unsigned long dot_print_time;   \
    unsigned long dot_feed_time;    \
    uint8_t print_mode;             \
    uint8_t prev_byte;              \
    uint8_t column;                 \
    uint8_t max_column;             \
    uint8_t max_height;             \
    uint8_t max_chunk_height;       \
    uint8_t char_height;            \
    uint8_t line_spacing;           \


struct printer {ADAFRUIT_PRINTER_ATTR};

struct line_option
{
    uint8_t bold,
        justify,
        size,
        underline;
};

size_t printer_writeline(struct printer *, const char *, struct line_option);
int printer_write(struct printer *, char);
void printer_ctor(struct printer *, const char *);
void printer_dtor(struct printer *);
void printer_sleep(struct printer *);
void printer_flush(struct printer *);
void wait_timeout(struct printer *);
void feed_line(struct printer *, uint8_t lines);
void reset(struct printer *);
void wake(struct printer *);
void set_justify(struct printer * p, char value);
void set_size(struct printer * self, char value);
void set_timeout(struct printer *, long unsigned x);
void set_bold(struct printer *, bool);
void set_underline(struct printer *, uint8_t);
void set_default(struct printer *);


#endif