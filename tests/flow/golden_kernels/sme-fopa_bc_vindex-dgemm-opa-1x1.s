.text
.global bli_dgemm_ukrgen_sme_opa_1vx1v_asm
.type bli_dgemm_ukrgen_sme_opa_1vx1v_asm, %function
bli_dgemm_ukrgen_sme_opa_1vx1v_asm:
.cfi_startproc
add sp,sp,#-64
.cfi_adjust_cfa_offset 64
str d8, [sp]
.cfi_rel_offset d8, 0
str d9, [sp, #8]
.cfi_rel_offset d9, 8
str d10, [sp, #16]
.cfi_rel_offset d10, 16
str d11, [sp, #24]
.cfi_rel_offset d11, 24
str d12, [sp, #32]
.cfi_rel_offset d12, 32
str d13, [sp, #40]
.cfi_rel_offset d13, 40
str d14, [sp, #48]
.cfi_rel_offset d14, 48
str d15, [sp, #56]
.cfi_rel_offset d15, 56
# x0 = k
# x1 = base(A)
# x2 = base(B)
# x3 = base(C)
# x4 = base(alpha)
# x5 = base(beta)
# x6 = stride(C,n)
smstart
ptrue p0.d
cntd x7
mul x8,x7,x6
and x9,x0,#3
lsr x0,x0,#2
zero {za0.d}
cbz x0,.ukr7_done
ld1d {z0.d}, p0/z, [x1]
ld1d {z1.d}, p0/z, [x2]
incb x1, ALL, MUL #1
incb x2, ALL, MUL #1
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
fmopa za0.d,p0/m,p0/m,z0.d,z1.d
ld1d {z2.d}, p0/z, [x1]
ld1d {z3.d}, p0/z, [x2]
fmopa za0.d,p0/m,p0/m,z2.d,z3.d
ld1d {z4.d}, p0/z, [x1, #1, MUL VL]
ld1d {z5.d}, p0/z, [x2, #1, MUL VL]
fmopa za0.d,p0/m,p0/m,z4.d,z5.d
ld1d {z6.d}, p0/z, [x1, #2, MUL VL]
ld1d {z7.d}, p0/z, [x2, #2, MUL VL]
ld1d {z0.d}, p0/z, [x1, #3, MUL VL]
ld1d {z1.d}, p0/z, [x2, #3, MUL VL]
fmopa za0.d,p0/m,p0/m,z6.d,z7.d
incb x1, ALL, MUL #4
incb x2, ALL, MUL #4
cbnz x0,.ukr7_loop
.ukr7_last:
fmopa za0.d,p0/m,p0/m,z0.d,z1.d
ld1d {z2.d}, p0/z, [x1]
ld1d {z3.d}, p0/z, [x2]
fmopa za0.d,p0/m,p0/m,z2.d,z3.d
ld1d {z4.d}, p0/z, [x1, #1, MUL VL]
ld1d {z5.d}, p0/z, [x2, #1, MUL VL]
fmopa za0.d,p0/m,p0/m,z4.d,z5.d
ld1d {z6.d}, p0/z, [x1, #2, MUL VL]
ld1d {z7.d}, p0/z, [x2, #2, MUL VL]
fmopa za0.d,p0/m,p0/m,z6.d,z7.d
incb x1, ALL, MUL #3
incb x2, ALL, MUL #3
.ukr7_done:
cbz x9,.ukr7_taildone
.ukr7_tail:
add x9,x9,#-1
ld1d {z0.d}, p0/z, [x1]
ld1d {z1.d}, p0/z, [x2]
fmopa za0.d,p0/m,p0/m,z0.d,z1.d
incb x1, ALL, MUL #1
incb x2, ALL, MUL #1
cbnz x9,.ukr7_tail
.ukr7_taildone:
ldr d0, [x5]
fmov d1,xzr
fcmp d0,d1
b.ne .ukr0_try0
ldr d0, [x4]
mov x0,#4607182418800017408
fmov d1,x0
fcmp d0,d1
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr d0, [x5]
mov x0,#4607182418800017408
fmov d1,x0
fcmp d0,d1
b.ne .ukr0_try2
ldr d0, [x4]
mov x0,#4607182418800017408
fmov d1,x0
fcmp d0,d1
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr d0, [x4]
mov x0,#4607182418800017408
fmov d1,x0
fcmp d0,d1
b.ne .ukr0_try4
b .ukr0_case4
.ukr0_try4:
b .ukr0_case5
b .ukr0_cases_end
.ukr0_case0:
mov x0,x3
mov x1,x7
mov x12,#0
add x2,x0,x6
.ukr1_slices:
st1d {za0v.d[w12, 0]}, p0, [x0]
st1d {za0v.d[w12, 1]}, p0, [x2]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
add x1,x1,#-2
cbnz x1,.ukr1_slices
sub x0,x0,x8
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
ld1rd {z0.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
.ukr2_slices:
mova z1.d,p0/m,za0v.d[w12,0]
mova z2.d,p0/m,za0v.d[w12,1]
fmul z3.d,z1.d,z0.d
fmul z1.d,z2.d,z0.d
st1d {z3.d}, p0, [x0]
st1d {z1.d}, p0, [x2]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
add x1,x1,#-2
cbnz x1,.ukr2_slices
sub x0,x0,x8
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
add x2,x0,x6
add x9,x3,x6
.ukr3_slices:
mova z0.d,p0/m,za0v.d[w12,0]
ld1d {z1.d}, p0/z, [x0]
mova z2.d,p0/m,za0v.d[w12,1]
ld1d {z3.d}, p0/z, [x2]
fadd z1.d,z0.d,z1.d
fadd z3.d,z2.d,z3.d
st1d {z1.d}, p0, [x3]
st1d {z3.d}, p0, [x9]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x9,x9,x6, LSL #1
add x12,x12,#2
add x1,x1,#-2
cbnz x1,.ukr3_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
ld1rd {z0.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x9,x3,x6
.ukr4_slices:
mova z1.d,p0/m,za0v.d[w12,0]
ld1d {z2.d}, p0/z, [x0]
mova z3.d,p0/m,za0v.d[w12,1]
ld1d {z4.d}, p0/z, [x2]
fmla z2.d,p0/m,z1.d,z0.d
fmla z4.d,p0/m,z3.d,z0.d
st1d {z2.d}, p0, [x3]
st1d {z4.d}, p0, [x9]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x9,x9,x6, LSL #1
add x12,x12,#2
add x1,x1,#-2
cbnz x1,.ukr4_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
ld1rd {z0.d}, p0/z, [x5]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x9,x3,x6
.ukr5_slices:
mova z1.d,p0/m,za0v.d[w12,0]
ld1d {z2.d}, p0/z, [x0]
fmla z1.d,p0/m,z2.d,z0.d
mova za0v.d[w12,0],p0/m,z1.d
mova z2.d,p0/m,za0v.d[w12,1]
ld1d {z3.d}, p0/z, [x2]
fmla z2.d,p0/m,z3.d,z0.d
st1d {z1.d}, p0, [x3]
st1d {z2.d}, p0, [x9]
mova za0v.d[w12,1],p0/m,z2.d
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x9,x9,x6, LSL #1
add x12,x12,#2
add x1,x1,#-2
cbnz x1,.ukr5_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
ld1rd {z0.d}, p0/z, [x5]
ld1rd {z1.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x9,x3,x6
.ukr6_slices:
ld1d {z2.d}, p0/z, [x0]
ld1d {z3.d}, p0/z, [x2]
fmul z2.d,z2.d,z0.d
mova z4.d,p0/m,za0v.d[w12,0]
fmul z3.d,z3.d,z0.d
mova z5.d,p0/m,za0v.d[w12,1]
fmla z2.d,p0/m,z4.d,z1.d
fmla z3.d,p0/m,z5.d,z1.d
st1d {z2.d}, p0, [x3]
st1d {z3.d}, p0, [x9]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x9,x9,x6, LSL #1
add x12,x12,#2
add x1,x1,#-2
cbnz x1,.ukr6_slices
sub x0,x0,x8
sub x3,x3,x8
.ukr0_cases_end:
smstop
ldr d8, [sp]
.cfi_restore d8
ldr d9, [sp, #8]
.cfi_restore d9
ldr d10, [sp, #16]
.cfi_restore d10
ldr d11, [sp, #24]
.cfi_restore d11
ldr d12, [sp, #32]
.cfi_restore d12
ldr d13, [sp, #40]
.cfi_restore d13
ldr d14, [sp, #48]
.cfi_restore d14
ldr d15, [sp, #56]
.cfi_restore d15
add sp,sp,#64
.cfi_adjust_cfa_offset -64
ret
.cfi_endproc
.size bli_dgemm_ukrgen_sme_opa_1vx1v_asm, .-bli_dgemm_ukrgen_sme_opa_1vx1v_asm
.section .note.GNU-stack,"",%progbits
