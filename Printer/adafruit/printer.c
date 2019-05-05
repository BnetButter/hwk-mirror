/* 
 * adapted from C++ code
 * https://github.com/adafruit/Adafruit-Thermal-Printer-Library
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdarg.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>
#include "printer.h"

#define BAUDRATE 19200
#define BYTE_TIME (((11L * 1000000L) + (BAUDRATE / 2)) / BAUDRATE)
#define ASCII_TAB '\t' // Horizontal tab
#define ASCII_LF  '\n' // Line feed
#define ASCII_FF  '\f' // Form feed
#define ASCII_CR  '\r' // Carriage return
#define ASCII_DC2  18  // Device control 2
#define ASCII_ESC  27  // Escape
#define ASCII_FS   28  // Field separator
#define ASCII_GS   29  // Group separator

static int write_bytes(struct printer *, ...);

/* va_arg sentinel */
static long unsigned _StopIteration = 0;
const void * StopIteration = & _StopIteration;

#define write_char(self, c) (fputc(c, self->stream) != EOF)

void printer_ctor(struct printer * self, const char * serial) 
{
    self->stream = fopen(serial, "wb");
    set_timeout(self, 500000L);
    wake(self);
    reset(self);
    self->dot_print_time = 30000;
    self->dot_feed_time = 2100;
    self-> max_chunk_height = 255;
}

void printer_dtor(struct printer * self) 
{
    fclose(self->stream);
}

void delay(long unsigned ms)
{
    ms /= 10;
    long unsigned diff, start;
    start = clock();
    do {
        diff = ((clock() - start) * 100) / CLOCKS_PER_SEC;
    } while (diff < ms);
}


static int write_bytes(struct printer * self, ...)
{
    wait_timeout(self);
    va_list ap; va_start(ap, self);
    long unsigned byte; 
    int n_bytes = 0;
    while ((byte = va_arg(ap, long unsigned)) != (long unsigned) StopIteration)
        n_bytes += write_char(self, byte);
    
    va_end(ap);
    set_timeout(self, n_bytes * BYTE_TIME);
    return n_bytes;
}

int printer_write(struct printer * self, char c)
{   
    int result = 0;
    if (c != 0x13) {
        wait_timeout(self);
        result = write_char(self, c);
        long unsigned d = BYTE_TIME;
        if (c != '\n' 
                || self->column == self->max_column) {
            
            d += (self->prev_byte == '\n') ? (
                    self->char_height + self->line_spacing * self->dot_feed_time) : ( // Feed line
                    self->char_height * self->dot_print_time) + (self->line_spacing * self->dot_feed_time); // Text line
            
            self->column = 0;
            c = '\n';    
        }
        else 
            self->column ++;
        
        set_timeout(self, d);
        self->prev_byte = c;
    }
    return result;
}



size_t printer_writeline(struct printer * self, const char * line, struct line_option conf)
{
    set_justify(self, conf.justify);
    set_bold(self, conf.bold);
    set_underline(self, conf.underline);
    set_size(self, conf.size); // must be last

    size_t result = 0;
    while (*line)
        result += printer_write(self, *line ++);
    feed_line(self, 1);
    reset(self);
    return result;
}

void set_timeout(struct printer * self, long unsigned x)
{
    self->resume_time = x;
}

void wait_timeout(struct printer * self)
{   
    delay(self->resume_time / 1000);
}

void reset(struct printer * self)
{
    write_bytes(self, ASCII_ESC, '@', StopIteration);
    self->prev_byte = '\n';
    self->column = 0;
    self->max_column = 32;
    self->char_height = 24;
    self->line_spacing = 6;

    write_bytes(self, ASCII_ESC, 'D', StopIteration);
    write_bytes(self, 4, 8, 12, 16, StopIteration);
    write_bytes(self, 20, 24, 28, 0, StopIteration);
}

void test_page(struct printer * self)
{
    write_bytes(self, ASCII_DC2, 'T', StopIteration);
    set_timeout(self, self->dot_print_time * 24 * 26 + self->dot_feed_time * (6 * 26 + 30));
}



#define INVERSE_MASK       (1 << 1)
#define UPDOWN_MASK        (1 << 2)
#define BOLD_MASK          (1 << 3)
#define DOUBLE_HEIGHT_MASK (1 << 4)
#define DOUBLE_WIDTH_MASK  (1 << 5)
#define STRIKE_MASK        (1 << 6)



static void write_print_mode(struct printer * self)
{
    write_bytes(self,
            ASCII_ESC,
            '!',
            self->print_mode,
            StopIteration);
}

static void set_print_mode(struct printer * self, uint8_t mask)
{
    self->print_mode |= mask;
    write_print_mode(self);
    self->char_height = (self->print_mode & DOUBLE_HEIGHT_MASK) ? 48 : 24;
    self->max_column = (self->print_mode & DOUBLE_WIDTH_MASK) ? 16 : 32;
}

static void unset_print_mode(struct printer * self, uint8_t mask)
{
    self->print_mode &= mask;
    write_print_mode(self);
    self->char_height = (self->print_mode & DOUBLE_HEIGHT_MASK) ? 48 : 24;
    self->max_column = (self->print_mode & DOUBLE_WIDTH_MASK) ? 16 : 32;
}

static void * set_unset[] = {unset_print_mode, set_print_mode};
#define set_unset(self, value, mask) ((void (*)()) set_unset[value])(self, mask);

void set_bold(struct printer * self, bool value) {set_unset(self, value, BOLD_MASK);}

void set_underline(struct printer * self, uint8_t weight) {write_bytes(self, ASCII_ESC, '-', weight, StopIteration);}

void set_justify(struct printer * self, char value)
{
    uint8_t pos = 0;
    switch (value) {
        case 'L':
            pos = 0; 
            break;
        case 'C':
            pos = 1;
            break;
        case 'R':
            pos = 2;
            break;
    }

    write_bytes(self, ASCII_ESC, 'a', pos, StopIteration);
}

void set_default(struct printer * self)
{
    set_justify(self, 'L');
    set_bold(self, false);
    set_underline(self, 0);
    set_size(self, 'S');
}


static void sleep_after(struct printer * self, uint16_t seconds)
{
    write_bytes(self, ASCII_ESC, '8', seconds, seconds >> 8, StopIteration);
}

void printer_sleep(struct printer * self)
{
    sleep_after(self, 1);
}

void wake(struct printer * self)
{
    set_timeout(self, 0);
    write_bytes(self, 255, StopIteration);
    write_bytes(self, ASCII_ESC, '8', 0, 0, StopIteration);

    for (int i = 0; i < 10; i++) {
        write_bytes(self, 0, StopIteration);
        set_timeout(self, 10000L);
    }
}

void feed_line(struct printer * self, uint8_t x) 
{
    write_bytes(self, ASCII_ESC, 'd', x, StopIteration);
    set_timeout(self, (self->dot_feed_time * self->char_height));
    self->prev_byte = '\n';
    self->column = 0;
}

void printer_flush(struct printer * self)
{
    write_bytes(self, ASCII_FF, StopIteration);
}

void set_size(struct printer * self, char value)
{
    uint8_t size;
    switch (value) {
        
        default: // 'S'
            size = 0x00;
            self->char_height = 24;
            self->max_column = 32;
            break;

        case 'M':
            size = 0x01;
            self->char_height = 48;
            self->max_column = 32;
            break;
        
        case 'L':
            size = 0x11;
            self->char_height = 48;
            self->max_column = 16;
            break;
    }

    write_bytes(self, ASCII_GS, '!', size, StopIteration);
    self->prev_byte = '\n';
}
