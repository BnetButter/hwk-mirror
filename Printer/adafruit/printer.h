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

void printer_ctor(struct printer *, const char *);
void printer_dtor(struct printer *);

size_t printer_writeline(struct printer *, const char *, struct line_option);

void printer_delete(struct printer *);
void printer_sleep(struct printer *);
void printer_flush(struct printer *);
int printer_write(struct printer *, char);
void wait_timeout(struct printer *);
void feed_line(struct printer *, uint8_t lines);
void feed_rows(struct printer *, uint8_t rows);
void reset(struct printer *);
void sleep_after(struct printer *, uint16_t seconds);
void wake(struct printer *);
void tab(struct printer *);
void set_justify(struct printer * p, char value);
void set_size(struct printer * self, char value);
void set_line_height(struct printer *, uint8_t x);
void set_timeout(struct printer *, long unsigned x);
void set_times(struct printer *, long unsigned print_time, long unsigned feed_time);
void set_inverse(struct printer *, bool);
void set_upside_down(struct printer *, bool);
void set_double_height(struct printer *, bool);
void set_double_width(struct printer *, bool);
void set_strike(struct printer *, bool);
void set_bold(struct printer *, bool);
void set_underline(struct printer *, uint8_t);
void set_online(struct printer *, bool);
void set_default(struct printer *);


#endif