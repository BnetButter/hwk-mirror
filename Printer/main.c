#include "io.h"
#include <stdio.h>
#include <assert.h>
#include "adafruit.h"

void test_list(void)
{   
    printf("** test list **\n");
    void * lst = new(list_t);
    int items[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0};

    for (int i = 0; i < 10; i++)
        append(lst, items + i);

    printf("append pass\n");
    for (int i = 0; i < 10; i++) 
        assert(i + 1 == *(int *)get(lst, (uintptr_t) i));
    printf("get passed\n");

    int popped[5];

    for (int i = 0; i < 5; i++) {
        int result = *(int *) get(lst, (uintptr_t) i);
        if (result & 1)
            popped[i] = *(int *) pop(lst, (uintptr_t) i);
    }

    for (int i = 0; i < 5; i++) {
        
        int odd =  popped[i];
        int even = *(int *) get(lst, i);
        assert(items[i * 2] == odd && items[(i * 2) + 1] == even);
    }
    printf("pop passed\n"); 

    insert(lst, 0, popped);
    insert(lst, 2, popped + 1);
    insert(lst, 4, popped + 2);
    insert(lst, 6, popped + 3);
    insert(lst, 8, popped + 4);

    for (int i = 0; i < 10; i++)
        assert(*(int *) get(lst, i) == i+1);    
    printf("insert passed\n");

    clear(lst);
    assert(! len(lst));
    printf("clear passed\n");
    delete(lst);

    printf("** list passed **\n");
}

void test_dict(void)
{
    printf("** test_dict **\n");

    const char * keys[] = {"hello", "this", "a"};
    const char * values[] = {"world", "is", "test"};
    void * d = new(dict_t);

    for (int i = 0; i < 3; i++)
        insert(d, (uintptr_t) keys[i], values[i]);
    printf("insert passed\n");

    char * results[3];
    for (int i = 0; i < 3; i++) {
        results[i] = get(d, (uintptr_t) keys[i]);
        assert(results[i] == values[i]);
    }
    printf("get passed\n");

    const char * buf[10];
    int result = dict_keys(d, buf) == 3;
    assert (result);
    for (int i = 0; i < 3; i++)
        printf("dict_key: %s\n", buf[i]);

    for (int i = 0; i < 3; i++) {
        assert(results[i] == pop(d, (uintptr_t) keys[i]));
        assert(! pop(d, (uintptr_t) keys[i]));
    }

    printf("pop passed\n");

    for (int i = 0; i < 3; i++)
        insert(d, (uintptr_t) keys[i], values[i]);

    clear(d);
    assert (! len(d));
    printf("clear passed\n");
    printf("** dict passed **\n");
}

void func_args(void * args);
void func_kwargs(void * kwargs);

void test_args(void) 
{
    printf("** test args **\n");
    char * argv[] = {"hello", "world", "!"};
    void * _args = args(argv[0], argv[1]);
    assert(len(_args) == 2);
    assert(get(_args, 0) == argv[0] && get(_args, 1) == argv[1]);
    append(_args, argv[2]);
    assert(len(_args) == 3);
    assert(pop(_args, 2) == argv[2]);
    clear(_args);
    assert(!(len(_args)));
    delete(_args);
    printf("** args passed **\n");
}

void test_kwargs(void)
{
    printf("** test kwargs **\n");
    const char * keys[] = {"hello", "this", "a", "and"};
    const char * values[] = {"world", "is", "test", "something"};
    
    void * _args = kwargs(
            keys[0], values[0],
            keys[1],  values[1],
            keys[2],     values[2]);
    for (int i = 0; i < 3; i++) 
        assert(get(_args, (uintptr_t)keys[i]) == values[i]);
    
    insert(_args, keys[3], values[3]);
    assert(get(_args, keys[3]) == values[3]);

    for (int i = 0; i < 4; i++)
        assert(pop(_args, keys[i]) == values[i]);
    
    assert(! len(_args));
    delete(_args);
    printf("** kwargs passed **\n");

}


void test_printer(void)
{   
    printf("** test_printer **\n");
    void * printer = new(AdafruitPrinter(), "./testfile", "wb");
    feed(printer, 10);
    sleep(printer);
    wake(printer);
    write(printer, "hello\n");
    write(printer, "this is a test\n");

}


int main(void)
{
    return 0;
}