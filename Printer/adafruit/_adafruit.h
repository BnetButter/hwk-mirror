#ifndef _ADAFRUIT_H
#define _ADAFRUIT_H
#include <stdint.h>
#include "_iobase.h"

const void * const AdafruitPrinter(void);

struct AdafruitPrinter
{
    const struct IOBase _;
    unsigned long resume_time;
    unsigned long dot_print_time;
    unsigned long dot_feed_time;
    uint8_t print_mode;
    uint8_t prev_byte;
    uint8_t column;
    uint8_t max_column;
    uint8_t max_height;
    uint8_t max_chunk_height;
    uint8_t char_height;
    uint8_t line_spacing;
};

/* configuration keywords              values */
#define JUSTIFY         "justify"      // bool
#define SIZE            "size"         // 'S', 'L', 'M'
#define NORMAL          "normal"       // bool
#define LINE_HEIGHT     "line height"  // uint8_t
#define INVERSE         "inverse"      // bool
#define UPSIDE_DOWN      "upside down"  // bool
#define DOUBLE_HEIGHT   "double height"// bool
#define DOUBLE_WIDTH    "double width" // bool
#define STRIKE          "strike"       // bool
#define BOLD            "bold"         // bool
#define UNDERLINE       "underline"    // uint8_t 0-3
#define ONLINE          "online"       // bool
#define DEFAULT         "default"      // bool



#endif