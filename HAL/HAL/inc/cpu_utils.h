#pragma once

#include "cal_annotate.h"
#include "cal_assembly.h"

ALWAYS_INLINE
extern
void
CpuClearDirectionFlag(
    void
    )
{
    __writeeflags(AsmReadEflags() & (~RFLAGS_DIRECTION_BIT));
}

ALWAYS_INLINE
extern
INTR_STATE
CpuIntrGetState(
    void
    )
{
    return IsBooleanFlagOn(AsmReadEflags(), RFLAGS_INTERRUPT_FLAG_BIT);
}

ALWAYS_INLINE
extern
INTR_STATE
CpuIntrSetState(
    const      INTR_STATE         IntrState
    )
{
    QWORD rFlags = AsmReadEflags();
    QWORD newFlags = IntrState ? ( rFlags | RFLAGS_INTERRUPT_FLAG_BIT ) : ( rFlags & ( ~RFLAGS_INTERRUPT_FLAG_BIT));

    __writeeflags(newFlags);

    return IsBooleanFlagOn(rFlags, RFLAGS_INTERRUPT_FLAG_BIT);
}

ALWAYS_INLINE
extern
INTR_STATE
CpuIntrDisable(
    void
    )
{
    return CpuIntrSetState(FALSE);
}

ALWAYS_INLINE
extern
INTR_STATE
CpuIntrEnable(
    void
    )
{
    return CpuIntrSetState(TRUE);
}

typedef BYTE APIC_ID;

ALWAYS_INLINE
extern
APIC_ID
CpuGetApicId(
    void
    )
{
    CPUID_INFO cpuId;

    AsmCpuid(cpuId.values, CpuidIdxFeatureInformation);

    return cpuId.FeatureInformation.ebx.ApicId;
}

ALWAYS_INLINE
extern
BOOLEAN
CpuIsIntel(
    void
    )
{
    CPUID_INFO cpuId;

    AsmCpuid(cpuId.values, CpuidIdxBasicInformation);

    return ( cpuId.ebx == 'uneG' &&
             cpuId.edx == 'Ieni' &&
             cpuId.ecx == 'letn' );
}
