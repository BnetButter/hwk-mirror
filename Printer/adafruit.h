#ifndef ADAFRUIT_H
#define ADAFRUIT_H
#include "object.h"
#include "collections.h"
#include "printertype.h"

extern const void * const AdafruitPrinter(void);

#define AdafruitPrinter_t AdafruitPrinter()

/* configuration keywords */
#define JUSTIFY         "justify"
#define SIZE            "size"
#define NORMAL          "normal"
#define LINE_HEIGHT     "line height"
#define INVERSE         "inverse"
#define UPSIDEDOWN      "upside down"
#define DOUBLE_HEIGHT   "double height"
#define DOUBLE_WIDTH    "double width"
#define STRIKE          "strike"
#define BOLD            "bold"
#define UNDERLINE       "underline"
#define ONLINE          "online"
#define DEFAULT         "default"

#endif