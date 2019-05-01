#ifndef IO_H
#define IO_H

#include "object.h"
#include "iobase.h"
#include "iotype.h"
#include "printertype.h"
#include "drawertype.h"
#include "arraytype.h"
#include "collections.h"

/* metaclass types */
#define type_t                      Type()
#define ArrayType_t                 ArrayType()
#define IOType_t                    IOType()
#define PrinterType_t               PrinterType()
#define DrawerType_t                DrawerType()

/* class types */
#define object_t                    Object()          // type_t
#define list_t                      list()            // ArrayType_t
#define Arguments_t                 Arguments()       // ArrayType_t
#define dict_t                      dict()            // ArrayType_t
#define KeywordArguments_t          KeywordArguments()// ArrayType_t
#define IOBase_t                    IOBase()          // IOType_t


#endif
