add_library(maths STATIC
    fixc.c
    rand.c
    tables.c
    vecmat.c
    )

include_directories(../include ../arch/include ../main)
