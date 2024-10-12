#pragma once

#include "cal_compiler.h"

#ifdef CAL_MSVC

#define AtomicAnd8(value, mask) _InterlockedAnd8((__int8 volatile *) (value), (__int8) (mask))
#define AtomicAnd16(value, mask) _InterlockedAnd16((__int16 volatile *) (value), (__int16) (mask))
#define AtomicAnd32(value, mask) _InterlockedAnd((__int32 volatile *) (value), (__int32) (mask))
#define AtomicAnd64(value, mask) _InterlockedAnd64((__int64 volatile *) (value), (__int64) (mask))

#define AtomicCompareExchange8(destination, exchange, comparand) _InterlockedCompareExchange8((__int8 volatile *) (destination), (__int8) (exchange), (__int8) (comparand))
#define AtomicCompareExchange16(destination, exchange, comparand) _InterlockedCompareExchange16((__int16 volatile *) (destination), (__int16) (exchange), (__int16) (comparand))
#define AtomicCompareExchange32(destination, exchange, comparand) _InterlockedCompareExchange((__int32 volatile *) (destination), (__int32) (exchange), (__int32) (comparand))
#define AtomicCompareExchange64(destination, exchange, comparand) _InterlockedCompareExchange64((__int64 volatile *) (destination), (__int64) (exchange), (__int64) (comparand))

#define AtomicCompareExchangePointer(destination, exchange, comparand) _InterlockedCompareExchangePointer((void * volatile *) (destination), (void *) (exchange), (void *) (comparand))

#define AtomicDecrement16(ptr) _InterlockedDecrement16((__int16 volatile *) (ptr))
#define AtomicDecrement32(ptr) _InterlockedDecrement((__int32 volatile *) (ptr))
#define AtomicDecrement64(ptr) _InterlockedDecrement64((__int64 volatile *) (ptr))

#define AtomicExchange8(target, value) _InterlockedExchange8((__int8 volatile *) (target), (__int8) (value))
#define AtomicExchange16(target, value) _InterlockedExchange16((__int16 volatile *) (target), (__int16) (value))
#define AtomicExchange32(target, value) _InterlockedExchange((__int32 volatile *) (target), (__int32) (value))
#define AtomicExchange64(target, value) _InterlockedExchange64((__int64 volatile *) (target), (__int64) (value))

#define AtomicExchangeAdd8(addend, value) _InterlockedExchangeAdd8((__int8 volatile *) (addend), (__int8) (value))
#define AtomicExchangeAdd16(addend, value) _InterlockedExchangeAdd16((__int16 volatile *) (addend), (__int16) (value))
#define AtomicExchangeAdd32(addend, value) _InterlockedExchangeAdd((__int32 volatile *) (addend), (__int32) (value))
#define AtomicExchangeAdd64(addend, value) _InterlockedExchangeAdd64((__int64 volatile *) (addend), (__int64) (value))

#define AtomicExchangePointer(target, value) _InterlockedExchangePointer((void * volatile *) (target), (void *) (value))

#define AtomicIncrement16(ptr) _InterlockedIncrement16((__int16 volatile *) (ptr))
#define AtomicIncrement32(ptr) _InterlockedIncrement((__int32 volatile *) (ptr))
#define AtomicIncrement64(ptr) _InterlockedIncrement64((__int64 volatile *) (ptr))

#define AtomicOr8(value, mask) _InterlockedOr8((__int8 volatile *) (value), (__int8) (mask))
#define AtomicOr16(value, mask) _InterlockedOr16((__int16 volatile *) (value), (__int16) (mask))
#define AtomicOr32(value, mask) _InterlockedOr((__int32 volatile *) (value), (__int32) (mask))
#define AtomicOr64(value, mask) _InterlockedOr64((__int64 volatile *) (value), (__int64) (mask))

#define AtomicXor8(value, mask) _InterlockedXor8((__int8 volatile *) (value), (__int8) (mask)) 
#define AtomicXor16(value, mask) _InterlockedXor16((__int16 volatile *) (value), (__int16) (mask)) 
#define AtomicXor32(value, mask) _InterlockedXor((__int32 volatile *) (value), (__int32) (mask)) 
#define AtomicXor64(value, mask) _InterlockedXor64((__int64 volatile *) (value), (__int64) (mask)) 

#define AtomicReadWriteBarrier _ReadWriteBarrier


#else

#define AtomicAnd8(value, mask) __atomic_fetch_and((__int8_t volatile *) (value), (__int8_t) (mask), __ATOMIC_SEQ_CST)
#define AtomicAnd16(value, mask) __atomic_fetch_and((__int16_t volatile *) (value), (__int16_t) (mask), __ATOMIC_SEQ_CST)
#define AtomicAnd32(value, mask) __atomic_fetch_and((__int32_t volatile *) (value), (__int32_t) (mask), __ATOMIC_SEQ_CST)
#define AtomicAnd64(value, mask) __atomic_fetch_and((__int64_t volatile *) (value), (__int64_t) (mask), __ATOMIC_SEQ_CST)

#define AtomicCompareExchange8(destination, exchange, comparand) __sync_val_compare_and_swap((__int8_t volatile *) (destination), (__int8_t) (comparand), (__int8_t) (exchange))
#define AtomicCompareExchange16(destination, exchange, comparand) __sync_val_compare_and_swap((__int16_t volatile *) (destination), (__int16_t) (comparand), (__int16_t) (exchange))
#define AtomicCompareExchange32(destination, exchange, comparand) __sync_val_compare_and_swap((__int32_t volatile *) (destination), (__int32_t) (comparand), (__int32_t) (exchange))
#define AtomicCompareExchange64(destination, exchange, comparand) __sync_val_compare_and_swap((__int64_t volatile *) (destination), (__int64_t) (comparand), (__int64_t) (exchange))

#define AtomicCompareExchangePointer(destination, exchange, comparand) __sync_val_compare_and_swap((void * volatile *) (destination), (void *) (comparand), (void *) (exchange))

#define AtomicDecrement16(ptr) __atomic_add_fetch((__int16_t volatile *) (ptr), (__int16_t) -1, __ATOMIC_SEQ_CST)
#define AtomicDecrement32(ptr) __atomic_add_fetch((__int32_t volatile *) (ptr), (__int32_t) -1, __ATOMIC_SEQ_CST)
#define AtomicDecrement64(ptr) __atomic_add_fetch((__int64_t volatile *) (ptr), (__int64_t) -1, __ATOMIC_SEQ_CST)

#define AtomicExchange8(target, value) __atomic_exchange_n((__int8_t volatile *) (target), (__int8_t) value, __ATOMIC_SEQ_CST)
#define AtomicExchange16(target, value) __atomic_exchange_n((__int16_t volatile *) (target), (__int16_t) value, __ATOMIC_SEQ_CST)
#define AtomicExchange32(target, value) __atomic_exchange_n((__int32_t volatile *) (target), (__int32_t) value, __ATOMIC_SEQ_CST)
#define AtomicExchange64(target, value) __atomic_exchange_n((__int64_t volatile *) (target), (__int64_t) value, __ATOMIC_SEQ_CST)

#define AtomicExchangeAdd8(ptr, val) __atomic_fetch_add((__int8_t volatile *) (ptr), (__int8_t) (val), __ATOMIC_SEQ_CST)
#define AtomicExchangeAdd16(ptr, val) __atomic_fetch_add((__int16_t volatile *) (ptr), (__int16_t) (val), __ATOMIC_SEQ_CST)
#define AtomicExchangeAdd32(ptr, val) __atomic_fetch_add((__int32_t volatile *) (ptr), (__int32_t) (val), __ATOMIC_SEQ_CST)
#define AtomicExchangeAdd64(ptr, val) __atomic_fetch_add((__int64_t volatile *) (ptr), (__int64_t) (val), __ATOMIC_SEQ_CST)

#define AtomicExchangePointer(target, value) __atomic_exchange_n((void * volatile *) (target), (void *) (value), __ATOMIC_SEQ_CST)

#define AtomicIncrement16(ptr) __atomic_add_fetch((__int16_t volatile *) (ptr), (__int16_t) 1, __ATOMIC_SEQ_CST)
#define AtomicIncrement32(ptr) __atomic_add_fetch((__int32_t volatile *) (ptr), (__int32_t) 1, __ATOMIC_SEQ_CST)
#define AtomicIncrement64(ptr) __atomic_add_fetch((__int64_t volatile *) (ptr), (__int64_t) 1, __ATOMIC_SEQ_CST)

#define AtomicOr8(value, mask) __atomic_fetch_or((__int8_t volatile *) (value), (__int8_t) (mask), __ATOMIC_SEQ_CST)
#define AtomicOr16(value, mask) __atomic_fetch_or((__int16_t volatile *) (value), (__int16_t) (mask), __ATOMIC_SEQ_CST)
#define AtomicOr32(value, mask) __atomic_fetch_or((__int32_t volatile *) (value), (__int32_t) (mask), __ATOMIC_SEQ_CST)
#define AtomicOr64(value, mask) __atomic_fetch_or((__int64_t volatile *) (value), (__int64_t) (mask), __ATOMIC_SEQ_CST)

#define AtomicXor8(value, mask) __atomic_fetch_or((__int8_t volatile *) (value), (__int8_t) (mask), __ATOMIC_SEQ_CST)
#define AtomicXor16(value, mask) __atomic_fetch_or((__int16_t volatile *) (value), (__int16_t) (mask), __ATOMIC_SEQ_CST)
#define AtomicXor32(value, mask) __atomic_fetch_or((__int32_t volatile *) (value), (__int32_t) (mask), __ATOMIC_SEQ_CST)
#define AtomicXor64(value, mask) __atomic_fetch_or((__int64_t volatile *) (value), (__int64_t) (mask), __ATOMIC_SEQ_CST)

#define AtomicReadWriteBarrier __sync_synchronize

#endif
