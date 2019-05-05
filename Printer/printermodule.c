#include <Python.h>
#include <stdlib.h>
#include <stddef.h>
#include "adafruit/printer.h"

static PyObject * ErrorObject;
static PyTypeObject Printer_Type;

typedef struct {
    PyObject_HEAD
    ADAFRUIT_PRINTER_ATTR
    PyObject * x_attr;
} PrinterObject;

#define cast(self) ((struct printer *) \
        ((char *) self + offsetof(PrinterObject, stream)))


#define PrinterObject_Check(v)      (Py_TYPE(v) == &Printer_Type)

static PrinterObject * newPrinterObject(PyObject *arg)
{
    PrinterObject *self;
    self = PyObject_New(PrinterObject, &Printer_Type);
    if (self == NULL)
        return NULL;
    self->x_attr = NULL;
    return self;
}

static PyObject * init_PrinterObject(PyObject * py_self, PyObject * args)
{
    struct printer * self = cast(py_self);
    char * serial;
    if (! PyArg_ParseTuple(args, "s:__init__", & serial))
        return NULL;
    printer_ctor(self, serial);
    Py_RETURN_NONE;
}

/* Printer methods */

static void Printer_dealloc(PrinterObject *self)
{   
    printer_dtor(cast(self));
    Py_XDECREF(self->x_attr);
    PyObject_Del(self);
}


static PyObject * Printer_write(PrinterObject * self, PyObject * args)
{    
    char * string;
    if (! PyArg_ParseTuple(args, "s:write", & string))
        return NULL;
    size_t counter = 0;
    while (*string)
        counter += printer_write(cast(self), *string ++);
    feed_line(cast(self), 1);
    reset(cast(self));
    return Py_BuildValue("i", counter);
}

static char * kwds[] = {
    "",
    "justify",
    "bold",
    "underline",
    "size",
    NULL,
};

static PyObject * Printer_writeline(PrinterObject * self, PyObject * args, PyObject * kwargs)
{
    char * string;
    /* default arguments */
    struct line_option options = {
            .justify='L',
            .bold=0,
            .underline=0,
            .size='S'
    };

    if (! PyArg_ParseTupleAndKeywords(args, kwargs, 
            "s|cccc", kwds,
            & string, & options.justify, & options.bold, & options.underline, & options.size))
        return NULL;
    size_t result = printer_writeline(cast(self), string, options);
    return Py_BuildValue("i", result);
}

static PyObject * Printer_set_size(PrinterObject * self, PyObject * args)
{
    char size;
    if (! PyArg_ParseTuple(args, "c:set_size", & size))
        return NULL;
    set_size(cast(self), size);
    Py_RETURN_NONE;
}

static PyObject * Printer_feed(PyObject * self, PyObject * args)
{
    int line;
    if (! PyArg_Parsetuple(args, "i:feed", & line))
        return NULL;
    feed_line(cast(self), (uint8_t) line);
    Py_RETURN_NONE;
}

static PyObject * Printer_set_justify(PrinterObject * self, PyObject * args)
{
    char justify;
    if (! PyArg_ParseTuple(args, "c:set_justify", & justify))
        return NULL;
    set_justify(cast(self), justify);
    Py_RETURN_NONE;
}

static PyObject * Printer_set_bold(PrinterObject * self, PyObject * args)
{
    int bold;
    if (! PyArg_ParseTuple(args, "i:set_bold", & bold))
        return NULL;
    set_bold(cast(self), bold);
    Py_RETURN_NONE;
}

static PyObject * Printer_set_underline(PrinterObject * self, PyObject * args)
{
    int weight;
    if (! PyArg_ParseTuple(args, "i:set_underline", & weight))
        return NULL;
    set_underline(cast(self), weight);
    Py_RETURN_NONE;
}

static PyMethodDef Printer_methods[] = {
    {"write", Printer_write, METH_VARARGS,
    PyDoc_STR("write() -> int")},
    {"__init__", init_PrinterObject, METH_VARARGS, NULL},
    {"set_size", Printer_set_size, METH_VARARGS, NULL},
    {"set_bold", Printer_set_bold, METH_VARARGS, NULL},
    {"set_justify", Printer_set_justify, METH_VARARGS, NULL},
    {"set_underline", Printer_set_justify, METH_VARARGS, NULL},
    {"writeline", Printer_writeline, METH_VARARGS | METH_KEYWORDS, NULL},
    {"feed", Printer_writeline, METH_VARARGS, NULL},
    {NULL,              NULL}           /* sentinel */
};

static PyObject * Printer_getattro(PrinterObject *self, PyObject *name)
{
    if (self->x_attr != NULL) {
        PyObject *v = PyDict_GetItemWithError(self->x_attr, name);
        if (v != NULL) {
            Py_INCREF(v);
            return v;
        }
        else if (PyErr_Occurred()) {
            return NULL;
        }
    }
    return PyObject_GenericGetAttr((PyObject *)self, name);
}

static int Printer_setattr(PrinterObject *self, const char *name, PyObject *v)
{
    if (self->x_attr == NULL) {
        self->x_attr = PyDict_New();
        if (self->x_attr == NULL)
            return -1;
    }
    if (v == NULL) {
        int rv = PyDict_DelItemString(self->x_attr, name);
        if (rv < 0 && PyErr_ExceptionMatches(PyExc_KeyError))
            PyErr_SetString(PyExc_AttributeError,
                "delete non-existing Printer attribute");
        return rv;
    }
    else
        return PyDict_SetItemString(self->x_attr, name, v);
}

static PyTypeObject Printer_Type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyVarObject_HEAD_INIT(NULL, 0)
    "printer.Printer",             /*tp_name*/
    sizeof(PrinterObject),          /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    /* methods */
    (destructor)Printer_dealloc,    /*tp_dealloc*/
    0,                          /*tp_print*/
    (getattrfunc)0,             /*tp_getattr*/
    (setattrfunc)Printer_setattr,   /*tp_setattr*/
    0,                          /*tp_reserved*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number*/
    0,                          /*tp_as_sequence*/
    0,                          /*tp_as_mapping*/
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    (getattrofunc)Printer_getattro, /*tp_getattro*/
    0,                          /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,         /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    Printer_methods,                /*tp_methods*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
    0,                          /*tp_base*/
    0,                          /*tp_dict*/
    0,                          /*tp_descr_get*/
    0,                          /*tp_descr_set*/
    0,                          /*tp_dictoffset*/
    0,                          /*tp_init*/
    0,                          /*tp_alloc*/
    0,                          /*tp_new*/
    0,                          /*tp_free*/
    0,                          /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/* Function of two integers returning integer */

PyDoc_STRVAR(printer_foo_doc,
"foo(i,j)\n\
\n\
Return the sum of i and j.");

static PyObject * printer_foo(PyObject *self, PyObject *args)
{
    long i, j;
    long res;
    if (!PyArg_ParseTuple(args, "ll:foo", &i, &j))
        return NULL;
    res = i+j; /* printerX Do something here */
    return PyLong_FromLong(res);
}


/* Function of no arguments returning new Printer object */

static PyObject * printer_new(PyObject *self, PyObject *args)
{
    PrinterObject *rv;

    if (!PyArg_ParseTuple(args, ":new"))
        return NULL;
    rv = newPrinterObject(args);
    if (rv == NULL)
        return NULL;
    return (PyObject *)rv;
}

/* Example with subtle bug from extensions manual ("Thin Ice"). */

static PyObject * printer_bug(PyObject *self, PyObject *args)
{
    PyObject *list, *item;

    if (!PyArg_ParseTuple(args, "O:bug", &list))
        return NULL;

    item = PyList_GetItem(list, 0);
    /* Py_INCREF(item); */
    PyList_SetItem(list, 1, PyLong_FromLong(0L));
    PyObject_Print(item, stdout, 0);
    printf("\n");
    /* Py_DECREF(item); */

    Py_INCREF(Py_None);
    return Py_None;
}

/* Test bad format character */

static PyObject *
printer_roj(PyObject *self, PyObject *args)
{
    PyObject *a;
    long b;
    if (!PyArg_ParseTuple(args, "O#:roj", &a, &b))
        return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}


/* ---------- */

static PyTypeObject Str_Type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyVarObject_HEAD_INIT(NULL, 0)
    "printermodule.Str",             /*tp_name*/
    0,                          /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    /* methods */
    0,                          /*tp_dealloc*/
    0,                          /*tp_print*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_reserved*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number*/
    0,                          /*tp_as_sequence*/
    0,                          /*tp_as_mapping*/
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    0,                          /*tp_getattro*/
    0,                          /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    0,                          /*tp_methods*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
    0, /* see PyInit_printer */      /*tp_base*/
    0,                          /*tp_dict*/
    0,                          /*tp_descr_get*/
    0,                          /*tp_descr_set*/
    0,                          /*tp_dictoffset*/
    0,                          /*tp_init*/
    0,                          /*tp_alloc*/
    0,                          /*tp_new*/
    0,                          /*tp_free*/
    0,                          /*tp_is_gc*/
};

/* ---------- */

static PyObject *
null_richcompare(PyObject *self, PyObject *other, int op)
{
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
}

static PyTypeObject Null_Type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyVarObject_HEAD_INIT(NULL, 0)
    "printermodule.Null",            /*tp_name*/
    0,                          /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    /* methods */
    0,                          /*tp_dealloc*/
    0,                          /*tp_print*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_reserved*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number*/
    0,                          /*tp_as_sequence*/
    0,                          /*tp_as_mapping*/
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    0,                          /*tp_getattro*/
    0,                          /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    null_richcompare,           /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    0,                          /*tp_methods*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
    0, /* see PyInit_printer */      /*tp_base*/
    0,                          /*tp_dict*/
    0,                          /*tp_descr_get*/
    0,                          /*tp_descr_set*/
    0,                          /*tp_dictoffset*/
    0,                          /*tp_init*/
    0,                          /*tp_alloc*/
    PyType_GenericNew,          /*tp_new*/
    0,                          /*tp_free*/
    0,                          /*tp_is_gc*/
};


/* ---------- */


/* List of functions defined in the module */

static PyMethodDef printer_methods[] = {
    {"roj",             printer_roj,         METH_VARARGS,
        PyDoc_STR("roj(a,b) -> None")},
    {"foo",             printer_foo,         METH_VARARGS,
        printer_foo_doc},
    {"new",             printer_new,         METH_VARARGS,
        PyDoc_STR("new() -> new printer object")},
    {"bug",             printer_bug,         METH_VARARGS,
        PyDoc_STR("bug(o) -> None")},
    {NULL,              NULL}           /* sentinel */
};

PyDoc_STRVAR(module_doc,
"Interface for Adafruit Thermal Printer");


static int printer_exec(PyObject *m)
{
    /* Slot initialization is subject to the rules of initializing globals.
       C99 requires the initializers to be "address constants".  Function
       designators like 'PyType_GenericNew', with implicit conversion to
       a pointer, are valid C99 address constants.
       However, the unary '&' operator applied to a non-static variable
       like 'PyBaseObject_Type' is not required to produce an address
       constant.  Compilers may support this (gcc does), MSVC does not.
       Both compilers are strictly standard conforming in this particular
       behavior.
    */
    Null_Type.tp_base = &PyBaseObject_Type;
    Str_Type.tp_base = &PyUnicode_Type;

    /* Finalize the type object including setting type of the new type
     * object; doing it here is required for portability, too. */
    if (PyType_Ready(&Printer_Type) < 0)
        goto fail;

    /* Add some symbolic constants to the module */
    if (ErrorObject == NULL) {
        ErrorObject = PyErr_NewException("printer.error", NULL, NULL);
        if (ErrorObject == NULL)
            goto fail;
    }
    Py_INCREF(ErrorObject);
    PyModule_AddObject(m, "error", ErrorObject);

    /* Add Str */
    if (PyType_Ready(&Str_Type) < 0)
        goto fail;
    PyModule_AddObject(m, "Str", (PyObject *)&Str_Type);

    /* Add Null */
    if (PyType_Ready(&Null_Type) < 0)
        goto fail;
    PyModule_AddObject(m, "Null", (PyObject *)&Null_Type);
    return 0;
 fail:
    Py_XDECREF(m);
    return -1;
}

static struct PyModuleDef_Slot printer_slots[] = {
    {Py_mod_exec, printer_exec},
    {0, NULL},
};

static struct PyModuleDef printermodule = {
    PyModuleDef_HEAD_INIT,
    "printer",
    module_doc,
    0,
    printer_methods,
    printer_slots,
    NULL,
    NULL,
    NULL
};

/* Export function for the module (*must* be called PyInit_printer) */

PyMODINIT_FUNC PyInit_printer(void)
{
    return PyModuleDef_Init(&printermodule);
}
