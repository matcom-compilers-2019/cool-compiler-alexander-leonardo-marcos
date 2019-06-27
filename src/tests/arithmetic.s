.data
data_0: .asciiz 
_index_negative_msg: .asciiz "Index to substr is negative\n"
_index_out_msg: .asciiz "Index out range exception\n"
_abort_msg: .asciiz "Execution aborted\n"
_div_zero_msg: .asciiz "Division by zero exception\n"
Object: .word 0
Object_ctr_method: .word Object_ctr
IO: .word 1
IO_ctr_method: .word IO_ctr
IO_abort_method: .word Object_abort
IO_copy_method: .word Object_copy
IO_type_name_method: .word Object_type_name
IO_in_int_method: .word IO_in_int
IO_in_string_method: .word IO_in_string
IO_out_int_method: .word IO_out_int
IO_out_string_method: .word IO_out_string
Int: .word 2
Int_ctr_method: .word Int_ctr
Int_abort_method: .word Object_abort
Int_copy_method: .word Object_copy
Int_type_name_method: .word Object_type_name
Bool: .word 3
Bool_ctr_method: .word Bool_ctr
Bool_abort_method: .word Object_abort
Bool_copy_method: .word Object_copy
Bool_type_name_method: .word Object_type_name
String: .word 4
String_ctr_method: .word String_ctr
String_abort_method: .word Object_abort
String_copy_method: .word Object_copy
String_type_name_method: .word Object_type_name
String_length_method: .word String_length
String_concat_method: .word String_concat
String_substr_method: .word String_substr
Main: .word 5
Main_ctr_method: .word Main_ctr
Main_abort_method: .word Object_abort
Main_copy_method: .word Object_copy
Main_type_name_method: .word Object_type_name
Main_main_method: .word Main_main
Arith: .word 6
Arith_ctr_method: .word Arith_ctr
Arith_abort_method: .word Object_abort
Arith_copy_method: .word Object_copy
Arith_type_name_method: .word Object_type_name
Arith_sum_method: .word Arith_sum

# Program
.text

# Function start
Object_ctr:
move $fp, $sp
sw $ra, 0($sp)
addiu $sp, $sp, -4

# Return
lw $a0, 0($fp)
lw $ra, 4($sp)
addiu $sp, $sp, 12
lw $fp, 0($sp)

# Function end

# Function start
IO_ctr:
move $fp, $sp
sw $ra, 0($sp)
addiu $sp, $sp, -4

# Return
lw $a0, 0($fp)
lw $ra, 4($sp)
addiu $sp, $sp, 12
lw $fp, 0($sp)

# Function end

# Function start
Int_ctr:
move $fp, $sp
sw $ra, 0($sp)
addiu $sp, $sp, -4

# Allocate
lw $a0, 32($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy

# SetAttrib
lw $a1, 0($fp)
li $a0, 0
sw $a0, 12($a1)

# SetAttrib
lw $a1, 0($fp)
lw $a0, 0($fp)
sw $a0, 12($a1)

# Return
lw $a0, 0($fp)
lw $ra, 4($sp)
addiu $sp, $sp, 12
lw $fp, 0($sp)

# Function end

# Function start
Bool_ctr:
move $fp, $sp
sw $ra, 0($sp)
addiu $sp, $sp, -4

# Allocate
lw $a0, 48($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy

# SetAttrib
lw $a1, 4($fp)
li $a0, 0
sw $a0, 12($a1)

# SetAttrib
lw $a1, 0($fp)
lw $a0, 0($fp)
sw $a0, 12($a1)

# Return
lw $a0, 0($fp)
lw $ra, 4($sp)
addiu $sp, $sp, 12
lw $fp, 0($sp)

# Function end

# Function start
String_ctr:
move $fp, $sp
sw $ra, 0($sp)
addiu $sp, $sp, -4

# Allocate
lw $a0, 32($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy

# SetAttrib
lw $a1, 12($fp)
li $a0, 0
sw $a0, 12($a1)

# Allocate
lw $a0, 64($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy

# SetAttrib
lw $a1, 8($fp)
lw $a0, 4($fp)
sw $a0, 12($a1)

# SetAttrib
lw $a1, 8($fp)
la $a0, data_0
sw $a0, 16($a1)

# SetAttrib
lw $a1, 0($fp)
lw $a0, 0($fp)
sw $a0, 12($a1)

# Allocate
lw $a0, 32($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy

# SetAttrib
lw $a1, 16($fp)
li $a0, 0
sw $a0, 12($a1)

# SetAttrib
lw $a1, 0($fp)
lw $a0, 8($fp)
sw $a0, 16($a1)

# Return
lw $a0, 0($fp)
lw $ra, 4($sp)
addiu $sp, $sp, 12
lw $fp, 0($sp)

# Function end

# Function start
Main_ctr:
move $fp, $sp
sw $ra, 0($sp)
addiu $sp, $sp, -4

# Return
lw $a0, 0($fp)
lw $ra, 4($sp)
addiu $sp, $sp, 12
lw $fp, 0($sp)

# Function end

# Function start
Main_main:
move $fp, $sp
sw $ra, 0($sp)
addiu $sp, $sp, -4

# Allocate
lw $a0, 96($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy

# Arg
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Arith_ctr

# Assign
sw $a0, 0($sp)

# Allocate
lw $a0, 32($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy

# SetAttrib
lw $a1, 32($fp)
li $a0, 0
sw $a0, 12($a1)

# Assign
sw $a0, -8($sp)

# Arg
sw $a0, 0($sp)
addiu $sp, $sp, -4

# TypeOf
lw $a1, 20($fp)
lw $a0, 0($a1)
sw $a0, 36($fp)

# VCall
addiu $sp, $sp, -8
sw $ra, 4($sp)
sw $fp, 8($sp)
lw $a2, 36($fp)
mulu $a2, $a2, 4
addu $a2, $a2, $s0
lw $a1, 0($a2)
lw $a2, 8($a1)
jalr $a0
lw $fp, 8($sp)
lw $ra, 4($sp)
addiu $sp, $sp, 8
sw $a0, 40($fp)

# Assign
sw $a0, -8($sp)

# Return
lw $a0, 28($fp)
lw $ra, 4($sp)
addiu $sp, $sp, 8
lw $fp, 0($sp)

# Function end

# Function start
Arith_ctr:
move $fp, $sp
sw $ra, 0($sp)
addiu $sp, $sp, -4

# Allocate
lw $a0, 32($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy

# SetAttrib
lw $a1, 44($fp)
li $a0, 1
sw $a0, 12($a1)

# SetAttrib
lw $a1, 0($fp)
lw $a0, 0($fp)
sw $a0, 12($a1)

# Allocate
lw $a0, 32($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy

# SetAttrib
lw $a1, 48($fp)
li $a0, 2
sw $a0, 12($a1)

# SetAttrib
lw $a1, 0($fp)
lw $a0, 4($fp)
sw $a0, 16($a1)

# Return
lw $a0, 0($fp)
lw $ra, 4($sp)
addiu $sp, $sp, 12
lw $fp, 0($sp)

# Function end

# Function start
Arith_sum:
move $fp, $sp
sw $ra, 0($sp)
addiu $sp, $sp, -4

# Plus
sw $a0, 0($sp)
addiu $sp, $sp, -4
lw $t1, 16($sp)
addiu $sp, $sp, 4
add $a0 $t1 $a0

# Return
lw $a0, 60($fp)
lw $ra, 4($sp)
addiu $sp, $sp, 8
lw $fp, 0($sp)

# Function end

# Function start
entry:
move $fp, $sp
sw $ra, 0($sp)
addiu $sp, $sp, -4

# Allocate
lw $a0, 80($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy

# Arg
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Main_ctr

# Arg
sw $a0, 0($sp)
addiu $sp, $sp, -4

# VCall
addiu $sp, $sp, -8
sw $ra, 4($sp)
sw $fp, 8($sp)
li $a2, Main
mulu $a2, $a2, 4
addu $a2, $a2, $s0
lw $a1, 0($a2)
lw $a2, 8($a1)
jalr $a0
lw $fp, 8($sp)
lw $ra, 4($sp)
addiu $sp, $sp, 8
sw $a0, 68($fp)

# Return
li $a0, 0
lw $ra, 4($sp)
addiu $sp, $sp, 12
lw $fp, 0($sp)

# Function end
Object_abort:
li $v0, 10
syscall 
Object_type_name:
move $fp, $sp

# Allocate
lw $a0, 64($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy
move $v1, $v0

# Allocate
lw $a0, 32($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy
lw $a1, 12($fp)
lw $a1, 0($a1)
mulu $a1, $a1, 4
addu $a1, $a1, $s1
lw $a1, 0($a1)
move $a2, $0
move $t2, $a1
_str_len_clsname:
lb $a0, 0($t2)
beq $a0, $0, _end_clsname_len
addu $a2, $a2, 1
addu $t2, $t2, 1
j _str_len_clsname
_end_clsname_len:
sw $a2, 12($v0)
sw $v0, 12($v1)
sw $a1, 16($v1)
move $v0, $v1
jr $ra
Object_copy:
move $fp, $sp
lw $t0, 12($fp)
lw $a0, 4($t0)
move $t4, $a0
li $v0, 9
syscall 
move $t2, $v0
li $t2, 0
Object_copy_loop:
lw $t1, 0($t0)
sw $t1, 0($v0)
addiu $t0, $t0, 4
addiu $v0, $v0, 4
addiu $t3, $t3, 4
ble $t4, $t3, Object_copy_loop
Object_copy_end:
move $v0, $t2
jr $ra
IO_in_int:
li $v0, 5
syscall 
move $a0, $v0
jr $ra
IO_in_string:
li $a1, 1024
li $v0, 8
syscall 
jr $ra
IO_out_int:
lw $a0, 4($sp)
li $v0, 1
syscall 
jr $ra
IO_out_string:
lw $a0, 4($sp)
li $v0, 4
syscall 
jr $ra
String_length:
lw $a0, 4($sp)
li $a1, 0
length_main_loop:
lb $t1, 0($a0)
beqz $t1, length_end
addiu $a0, $a0, 1
addiu $a1, $a1, 1
j length_main_loop
length_end:
move $a0, $a1
jr $ra
String_concat:
move $fp, $sp

# Allocate
lw $a0, 32($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy
move $v1 $v0

# Allocate
lw $a0, 64($s0)
sw $a0, 0($sp)
addiu $sp, $sp, -4

# Call
jal Object_copy
move $t3 $v0
lw $a1 12($fp)
lw $a2 16($fp)
lw $t1 12($a1)
lw $t1 12($t1)
lw $t2 12($a2)
lw $t2 12($t2)
addu $t0 $t2 $t1
sw $t0 12($v1)
lw $a1 16($a1)
lw $a2 16($a2)
addiu $t0 $t0 1
move $a0, $t0
li $v0, 9
syscall 
move $t5 $v0
move $t4 $a1
addu $a1 $a1 $t1
_strcat_copy_:
beq $t4 $a1 _end_strcat_copy_
lb $a0 0($t4)
sb $a0 0($t5)
addiu $t5 $t5 1
addiu $t4 $t4 1
j _strcat_copy_
_end_strcat_copy_:
move $t4 $a2
addu $a2 $a2 $t2
_strcat_copy_snd_:
beq $t4 $a2 _end_strcat_copy_snd_
lb $a0 0($t4)
sb $a0 0($t5)
addiu $t5 $t5 1
addiu $t4 $t4 1
j _strcat_copy_snd_
_end_strcat_copy_snd_:
sb $0 0($t5)
sw $v1 12($t3)
sw $v0 16($t3)
move $v0 $t3
jr $ra

String_substr:
move $fp, $sp
lw $t5, 12($fp)
lw $a1, 16($fp)
lw $a1, 12($a1)
lw $a2, 20($fp)
lw $a2, 12($a2)
blt $a1, $0, _index_negative
blt $a2, $0, _index_negative
add $a2, $a1, $a2
lw $a3, 12($t5)
lw $a3, 12($a3)
bgt $a2, $a3, _index_out
move $v1, $a0
move $t0, $a0
sw $a2, 12($t0)
move $a0, $a2
li $v0, 9
syscall 
sw $t0, 12($v1)
sw $v0, 16($v1)
move $t1, $v0
lw $t5, 16($t5)
move $t4, $t5
addu $t4, $t4, $a1
addu $t5, $t5, $a2
_substr_copy:
bge $t4, $t5, _end_substr_copy
lb $a0, 0($t4)
sb $a0, 0($t1)
addiu $t1, $t1, 1
addiu $t4, $t4, 1
j _substr_copy
_index_negative:
la $a0, _index_negative_msg
b _subst_abort
_index_out:
la $a0, _index_out_msg
b _subst_abort
_subst_abort:
li $v0, 4
syscall 
la $a0, _abort_msg
li $v0, 4
syscall 
li $v0, 10
syscall 
_end_substr_copy:
move $a0, $v1
jr $ra