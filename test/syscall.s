.code64

.global __SyscallEntry

.section .data
_param:
.skip 0x10

.section .text
__SyscallEntry:
    push %rbp

    lea 0x10(%rsp), %rbp

    mov  %rcx, (%rbp)
    mov  %rdx, 0x8(%rbp)
    mov  %r8, 0x10(%rbp)
    mov  %r9, 0x18(%rbp)

    mov %rcx, %r8

    push %rdi

    syscall

    pop %rdi

    pop %rbp

    ret
