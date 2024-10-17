/*
    Linker script for HAL9000
*/
OUTPUT_FORMAT("elf64-x86-64")
ENTRY(__HalEntry)

PHDRS
{
    headers PT_LOAD FILEHDR PHDRS ;
    text PT_LOAD ;
    data PT_LOAD ;
    rodata PT_LOAD ;
}

SECTIONS
{
    /*
        HAL9000 Physical Base
        HAL will add the virtual difference
    */
    . = 0x1000000;

    .text 0x400 : ALIGN(0x200)
    {
        *(.halboot)
        *(.text)
    } :text

    .data : ALIGN(0x200)
    {
        *(.data)
        *(.data1)
        *(.bss)
    } :data

    .rodata : ALIGN(0x200)
    {
        *(.rodata)
        *(.rodata1)
    } :rodata

    /DISCARD/ :
    {
        *(.symtab)
        *(.strtab)
        *(.shstrtab)
        *(.comment)
    }
}
