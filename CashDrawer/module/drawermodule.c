#include "Python.h"
#include "drawermodule.h"


static PyObject *ErrorObject;
typedef struct {
    PyObject_HEAD
    PyObject            *x_attr;        /* Attributes dictionary */
} DrawerObject;

static PyTypeObject Drawer_Type;

#define DrawerObject_Check(v)      (Py_TYPE(v) == & Drawer_Type)

static DrawerObject * new_DrawerObject(PyObject *arg)
{
    DrawerObject *self;
    self = PyObject_New(DrawerObject, & Drawer_Type);
    if (self == NULL)
        return NULL;
    self->x_attr = NULL;
    return self;
}

/* Drawer methods */

static void Drawer_dealloc(DrawerObject *self)
{
    Py_XDECREF(self->x_attr);
    PyObject_Del(self);
}

static int Drawer_init(PyObject * self, PyObject * args, PyObject * kwds) 
{
    if (WiringPiSetup() == -1)
        return 0;
    pinMode(SIGNAL_PIN, OUTPUT);
}

static PyObject * Drawer_open(PyObject * self, PyObject * args)
{   
    
    if (!PyArg_ParseTuple(args, ":open"))
        return NULL;

    digitalWrite(SIGNAL_PIN, ON);
    delay(PULSE_WIDTH);
    digitalWrite(SIGNAL_PIN, OFF);
    Py_RETURN_NONE;
}


static PyMethodDef Drawer_methods[] = {
    {"open", (PyCFunction) Drawer_open, METH_VARARGS, PyDoc_STR(
            "open() -> None\n
             Open the cash drawer.\n
             Does nothing if already opened.")
    },

    /* sentinel */
    {NULL,              NULL}
};

static PyObject * Drawer_getattro(DrawerObject *self, PyObject *name)
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

static int Drawer_setattr(DrawerObject *self, const char *name, PyObject *v)
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
                "delete non-existing Drawer attribute");
        return rv;
    }
    else
        return PyDict_SetItemString(self->x_attr, name, v);
}

static PyTypeObject Drawer_Type = {
    /* The ob_type field must be initialized in the module init function
     * to be portable to Windows without using C++. */
    PyVarObject_HEAD_INIT(NULL, 0)
    "cashdrawermodule.Drawer",  /*tp_name*/
    sizeof(DrawerObject),       /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    /* methods */
    (destructor)Drawer_dealloc,    /*tp_dealloc*/
    0,                          /*tp_print*/
    (getattrfunc)0,             /*tp_getattr*/
    (setattrfunc)Drawer_setattr,/*tp_setattr*/
    0,                          /*tp_reserved*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number*/
    0,                          /*tp_as_sequence*/
    0,                          /*tp_as_mapping*/
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    (getattrofunc)Drawer_getattro, /*tp_getattro*/
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
    Drawer_methods,                /*tp_methods*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
    0,                          /*tp_base*/
    0,                          /*tp_dict*/
    0,                          /*tp_descr_get*/
    0,                          /*tp_descr_set*/
    0,                          /*tp_dictoffset*/
    Drawer_init,                /*tp_init*/
    0,                          /*tp_alloc*/
    0,                          /*tp_new*/
    0,                          /*tp_free*/
    0,                          /*tp_is_gc*/
};
/* --------------------------------------------------------------------- */

/* Function of two integers returning integer */

PyDoc_STRVAR(cashdrawer_foo_doc,
"foo(i,j)\n\
\n\
Return the sum of i and j.");

static PyObject *
cashdrawer_foo(PyObject *self, PyObject *args)
{
    long i, j;
    long res;
    if (!PyArg_ParseTuple(args, "ll:foo", &i, &j))
        return NULL;
    res = i+j; /* cashdrawerX Do something here */
    return PyLong_FromLong(res);
}


/* Function of no arguments returning new Drawer object */

static PyObject *
cashdrawer_new(PyObject *self, PyObject *args)
{
    DrawerObject *rv;

    if (!PyArg_ParseTuple(args, ":new"))
        return NULL;
    rv = new_DrawerObject(args);
    if (rv == NULL)
        return NULL;
    return (PyObject *)rv;
}

/* Example with subtle bug from extensions manual ("Thin Ice"). */

static PyObject *
cashdrawer_bug(PyObject *self, PyObject *args)
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
cashdrawer_roj(PyObject *self, PyObject *args)
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
    "cashdrawermodule.Str",             /*tp_name*/
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
    0, /* see PyInit_cashdrawer */      /*tp_base*/
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
    "cashdrawermodule.Null",            /*tp_name*/
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
    0, /* see PyInit_cashdrawer */      /*tp_base*/
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

static PyMethodDef cashdrawer_methods[] = {
    {"roj",             cashdrawer_roj,         METH_VARARGS,
        PyDoc_STR("roj(a,b) -> None")},
    {"foo",             cashdrawer_foo,         METH_VARARGS,
        cashdrawer_foo_doc},
    {"new",             cashdrawer_new,         METH_VARARGS,
        PyDoc_STR("new() -> new cashdrawer object")},
    {"bug",             cashdrawer_bug,         METH_VARARGS,
        PyDoc_STR("bug(o) -> None")},
    {NULL,              NULL}           /* sentinel */
};

PyDoc_STRVAR(module_doc, "A simple Cash Drawer interface.");

static int cashdrawer_exec(PyObject *m)
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
    if (PyType_Ready(&Drawer_Type) < 0)
        goto fail;

    /* Add some symbolic constants to the module */
    if (ErrorObject == NULL) {
        ErrorObject = PyErr_NewException("cashdrawer.error", NULL, NULL);
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

static struct PyModuleDef_Slot cashdrawer_slots[] = {
    {Py_mod_exec, cashdrawer_exec},
    {0, NULL},
};

static struct PyModuleDef cashdrawermodule = {
    PyModuleDef_HEAD_INIT,
    "cashdrawer",
    module_doc,
    0,
    cashdrawer_methods,
    cashdrawer_slots,
    NULL,
    NULL,
    NULL
};

/* Export function for the module (*must* be called PyInit_cashdrawer) */

PyMODINIT_FUNC
PyInit_cashdrawer(void)
{
    return PyModuleDef_Init(&cashdrawermodule);
}
