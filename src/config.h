#ifndef __CONFIG_H__
#define __CONFIG_H__

#include "mbed.h"

// To compile without DEBUG mode add `-c -DDEBUG=0` to compiler
#define DEBUG 1

#if DEBUG
    #define DEBUGP(x) pc.printf x
#else
    #define DEBUGP(x) do {} while (0)
#endif

extern Serial pc;

#endif // __CONFIG_H__
