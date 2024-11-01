#include "cal_compiler.h"
#include "cal_annotate.h"

// Dummy __stack_chk_fail we just halt for now as it is just a quick solution
#ifdef CAL_GNU

NO_RETURN
void
__stack_chk_fail(
    void
    )
{
    __asm__ __volatile__ ("hlt" : : : "memory");
}

#endif