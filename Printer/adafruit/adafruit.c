#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdarg.h>
#include <stdbool.h>
#include "io.h"
#include "printertype.h"
#include "_adafruit.h"


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

#define write_bytes(self, ...)      (_write_bytes(self, ## __VA_ARGS__, & _StopIteration))
#define write_char(self, c)        (fwrite(&c, 1, 1, ((struct IOBase *) self)->stream))

static void  _write_bytes(void *, ...);
static void AdafruitPrinter_flush(void *);
static void AdafruitPrinter_set_timeout(void *, long unsigned);
static void AdafruitPrinter_wait_timeout(void *);
static void AdafruitPrinter_reset(void *);
static void AdafruitPrinter_sleep(void *);
static void AdafruitPrinter_wake(void *);
static void AdafruitPrinter_feed(void *, uint8_t);

static void unset_print_mode(struct AdafruitPrinter * self, uint8_t mask);
static void set_print_mode(struct AdafruitPrinter * self, uint8_t mask);
static void write_print_mode(struct AdafruitPrinter * self);
static void set_normal(void *);
static void set_justify(void *, char value);
static void set_size(void * self, char value);
static void set_line_height(void *, uint8_t x);
static void set_inverse(void *, bool);
static void set_upside_down(void *, bool);
static void set_double_height(void *, bool);
static void set_double_width(void *, bool);
static void set_strike(void *, bool);
static void set_bold(void *, bool);
static void set_underline(void *, uint8_t);
static void set_online(void *, bool);
static void set_default(void *);





/* va_arg sentinel */
static long unsigned _StopIteration;

/* 
  singleton instance.
  one printer per device.
  */
static void * _instance;
static void * AdafruitPrinter_new(const void * const _class, va_list * app)
{
    const struct PrinterType * class = _class;
    
    if (! _instance) {
        _instance = ((void * (*)()) super(class, new))(class, app);
        return _instance;
    }

    dtor(_instance); // cleanup before reinitializing
    ctor(_instance, app);
    return _instance;
}

static void * AdafruitPrinter_ctor(void * _self, va_list * app)
{
    struct AdafruitPrinter * self = _self;
    super(AdafruitPrinter(), ctor)(_self, app);
    set_timeout(self, 500000L);
    wake(self);
    reset(self);
    self->dot_print_time = 30000;
    self->dot_feed_time = 2100;
    self-> max_chunk_height = 255;
    return self;
}

static void AdafruitPrinter_set_timeout(void * _self, long unsigned ms)
{
    struct AdafruitPrinter * self = _self;
    self->resume_time = ms;
}

static void AdafruitPrinter_wait_timeout(void * _self)
{   
    struct AdafruitPrinter * self = _self;
    long unsigned x = 0;
    // RPI clocked at 1.4 ghz. close enough.
    while (x++, x < self->resume_time);
}

static void AdafruitPrinter_reset(void * _self)
{
    struct AdafruitPrinter * self = _self;
    write_bytes(self, ASCII_ESC, '@');
    self->prev_byte = '\n';
    self->column = 0;
    self->max_column = 32;
    self->char_height = 24;
    self->line_spacing = 6;
    write_bytes(self, ASCII_ESC, 'D');
    write_bytes(self, 4, 8, 12, 16);
    write_bytes(self, 20, 24, 28, 0);
}

static void AdafruitPrinter_feed(void * _self, uint8_t x) 
{   
    struct AdafruitPrinter * self = _self;
    write_bytes(self, ASCII_ESC, 'd', x);
    set_timeout(self, (self->dot_feed_time * self->char_height));
    self->prev_byte = '\n';
    self->column = 0;
}

void feed_rows(void * _self, uint8_t rows)
{   
    struct AdafruitPrinter * self = _self;
    write_bytes(self, ASCII_ESC, 'J');
    set_timeout(self, (rows * self->dot_feed_time));
    self->prev_byte = '\n';
    self->column = 0;
}

static void sleep_after(void * _self, long unsigned s)
{   
    write_bytes(_self, ASCII_ESC, '8', s, s >> 8);
}

static void AdafruitPrinter_sleep(void * _self)
{
    sleep_after(_self, 1);
}

static void AdafruitPrinter_wake(void * _self)
{
  set_timeout(_self, 0);   // Reset timeout counter
  write_bytes(_self, 255); // Wake
  write_bytes(_self, ASCII_ESC, '8', 0, 0);
}

static void set_line_height(void * _self, uint8_t size)
{   
    struct AdafruitPrinter * self = _self;
    if(size < 24) size = 24;
        self->line_spacing = size - 24;

    write_bytes(self, ASCII_ESC, '3', size);
}

static void AdafruitPrinter_flush(void * _self) {write_bytes(_self, ASCII_FF);}

static void Adafruitvoidest_page(void * _self)
{   
    struct AdafruitPrinter * self = _self;
    write_bytes(self, ASCII_DC2, 'T');
    set_timeout(self, self->dot_print_time * 24 * 26 + self->dot_feed_time * (6 * 26 + 30));
}

typedef void (*config_func)(void *, long unsigned);

struct key_func 
{
    const char * key;
    void (*func)();
};


#define func void (*)()

static const struct key_func config[] = {
    {JUSTIFY,       (func) set_justify},
    {SIZE,          (func) set_size},
    {NORMAL,        (func) set_normal},
    {LINE_HEIGHT,   (func) set_line_height},
    {INVERSE,       (func) set_inverse},
    {UPSIDE_DOWN,   (func) set_upside_down},
    {DOUBLE_HEIGHT, (func) set_double_height},
    {DOUBLE_WIDTH,  (func) set_double_width},
    {STRIKE,        (func) set_strike},
    {BOLD,          (func) set_bold},
    {UNDERLINE,     (func) set_underline},
    {DEFAULT,       (func) set_default},
    {ONLINE,        (func) set_online},
};

#undef func

static void AdafruitPrinter_configure(void * _self, kwargs_t kwargs)
{
    struct AdafruitPrinter * self = _self;
    reset(self);
    for (int i = 0; i < sizeof(config) / sizeof(struct key_func); i++)
        config[i].func(self, get(kwargs, (uintptr_t) config[i].key));
}



static void _write_bytes(void * _self, ...)
{   
    struct AdafruitPrinter * self = _self;
    AdafruitPrinter_wait_timeout(self);
    va_list ap; va_start(ap, _self);
    long unsigned byte; 
    int n_bytes = 0;
    while ((byte = va_arg(ap, long unsigned) != (long unsigned) & _StopIteration))
        n_bytes += write_char(self, byte);
     
    va_end(ap); 
    AdafruitPrinter_set_timeout(self, n_bytes * BYTE_TIME);
}

static const void * _AdafruitPrinter;
const void * const AdafruitPrinter(void)
{
    return _AdafruitPrinter ? _AdafruitPrinter : (_AdafruitPrinter = new(
            PrinterType(), __func__,
            IOBase(), sizeof(struct AdafruitPrinter),
            new, AdafruitPrinter_new,
            reset, AdafruitPrinter_reset,
            flush, AdafruitPrinter_flush,
            test_page, Adafruitvoidest_page,
            set_timeout, AdafruitPrinter_set_timeout,
            wait_timeout, AdafruitPrinter_wait_timeout,
            ctor, AdafruitPrinter_ctor,
            wake, AdafruitPrinter_wake,
            sleep, AdafruitPrinter_sleep,
            feed, AdafruitPrinter_feed,
            configure, AdafruitPrinter_configure,
            (void *) 0));
}

#define INVERSE_MASK       (1 << 1)
#define UPDOWN_MASK        (1 << 2)
#define BOLD_MASK          (1 << 3)
#define DOUBLE_HEIGHT_MASK (1 << 4)
#define DOUBLE_WIDTH_MASK  (1 << 5)
#define STRIKE_MASK        (1 << 6)



static void write_print_mode(struct AdafruitPrinter * self)
{
    write_bytes(self,
            ASCII_ESC,
            '!',
            self->print_mode);
}

static void set_print_mode(struct AdafruitPrinter * self, uint8_t mask)
{
    self->print_mode |= mask;
    write_print_mode(self);
    self->char_height = (self->print_mode & DOUBLE_HEIGHT_MASK) ? 48 : 24;
    self->max_column = (self->print_mode & DOUBLE_WIDTH_MASK) ? 16 : 32;
}

static void unset_print_mode(struct AdafruitPrinter * self, uint8_t mask)
{
    self->print_mode &= mask;
    write_print_mode(self);
    self->char_height = (self->print_mode & DOUBLE_HEIGHT_MASK) ? 48 : 24;
    self->max_column = (self->print_mode & DOUBLE_WIDTH_MASK) ? 16 : 32;
}

static void set_normal(void * _self)
{   
    struct AdafruitPrinter * self = _self;
    self->print_mode = 0;
    write_print_mode(self);
}


static void * set_unset[] = {unset_print_mode, set_print_mode};
#define set_unset(self, value, mask) ((void (*)()) set_unset[value])(self, mask);

static void set_upside_down(void * self, bool value) {set_unset(self, value, UPDOWN_MASK);}

static void set_inverse(void * self, bool value) { set_unset(self, value, INVERSE_MASK);}

static void set_double_height(void * self, bool value) {set_unset(self, value, DOUBLE_HEIGHT_MASK);}

static void set_double_width(void * self, bool value) {set_unset(self, value, DOUBLE_WIDTH_MASK);}

static void set_strike(void * self, bool value) {set_unset(self, value, DOUBLE_WIDTH_MASK);}

static void set_bold(void * self, bool value) {set_unset(self, value, BOLD_MASK);}

static void set_underline(void * self, uint8_t weight) {write_bytes(self, ASCII_ESC, '-', weight, StopIteration);}

static void set_online(void * self, bool value) {write_bytes(self, ASCII_ESC, '=', value, StopIteration);}



static void set_justify(void * self, char value)
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

static void set_default(void * self)
{
    set_online(self, true);
    set_justify(self, 'L');
    set_inverse(self, false);
    set_double_height(self, false);
    set_line_height(self, 30);
    set_bold(self, false);
    set_underline(self, 0);
    set_size(self, 'S');
}
static void set_size(void * _self, char value)
{
  struct AdafruitPrinter * self = _self;
  uint8_t size;
  switch(value) {
   default:  // Small: standard width and height
    size       = 0x00;
    self->char_height = 24;
    self->max_column  = 32;
    break;
   case 'M': // Medium: double height
    size       = 0x01;
    self->char_height = 48;
    self->max_column  = 32;
    break;
   case 'L': // Large: double width and height
    size       = 0x11;
    self->char_height = 48;
    self->max_column  = 16;
    break;
  }
  write_bytes(self, ASCII_GS, '!', size);
  self->prev_byte = '\n'; // Setting the size adds a linefeed
}
