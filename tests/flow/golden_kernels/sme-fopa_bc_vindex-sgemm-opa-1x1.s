.text
.global bli_sgemm_ukrgen_sme_opa_1vx1v_asm
.type bli_sgemm_ukrgen_sme_opa_1vx1v_asm, %function
bli_sgemm_ukrgen_sme_opa_1vx1v_asm:
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
ptrue p0.s
cntw x7
mul x8,x7,x6
and x9,x0,#3
lsr x0,x0,#2
zero {za0.s}
cbz x0,.ukr7_done
ld1w {z0.s}, p0/z, [x1]
ld1w {z1.s}, p0/z, [x2]
incb x1, ALL, MUL #1
incb x2, ALL, MUL #1
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
fmopa za0.s,p0/m,p0/m,z0.s,z1.s
ld1w {z2.s}, p0/z, [x1]
ld1w {z3.s}, p0/z, [x2]
fmopa za0.s,p0/m,p0/m,z2.s,z3.s
ld1w {z4.s}, p0/z, [x1, #1, MUL VL]
ld1w {z5.s}, p0/z, [x2, #1, MUL VL]
fmopa za0.s,p0/m,p0/m,z4.s,z5.s
ld1w {z6.s}, p0/z, [x1, #2, MUL VL]
ld1w {z7.s}, p0/z, [x2, #2, MUL VL]
ld1w {z0.s}, p0/z, [x1, #3, MUL VL]
ld1w {z1.s}, p0/z, [x2, #3, MUL VL]
fmopa za0.s,p0/m,p0/m,z6.s,z7.s
incb x1, ALL, MUL #4
incb x2, ALL, MUL #4
cbnz x0,.ukr7_loop
.ukr7_last:
fmopa za0.s,p0/m,p0/m,z0.s,z1.s
ld1w {z2.s}, p0/z, [x1]
ld1w {z3.s}, p0/z, [x2]
fmopa za0.s,p0/m,p0/m,z2.s,z3.s
ld1w {z4.s}, p0/z, [x1, #1, MUL VL]
ld1w {z5.s}, p0/z, [x2, #1, MUL VL]
fmopa za0.s,p0/m,p0/m,z4.s,z5.s
ld1w {z6.s}, p0/z, [x1, #2, MUL VL]
ld1w {z7.s}, p0/z, [x2, #2, MUL VL]
fmopa za0.s,p0/m,p0/m,z6.s,z7.s
incb x1, ALL, MUL #3
incb x2, ALL, MUL #3
.ukr7_done:
cbz x9,.ukr7_taildone
.ukr7_tail:
add x9,x9,#-1
ld1w {z0.s}, p0/z, [x1]
ld1w {z1.s}, p0/z, [x2]
fmopa za0.s,p0/m,p0/m,z0.s,z1.s
incb x1, ALL, MUL #1
incb x2, ALL, MUL #1
cbnz x9,.ukr7_tail
.ukr7_taildone:
ldr s0, [x5]
fmov s1,wzr
fcmp s0,s1
b.ne .ukr0_try0
ldr s0, [x4]
mov x0,#1065353216
fmov s1,w0
fcmp s0,s1
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr s0, [x5]
mov x0,#1065353216
fmov s1,w0
fcmp s0,s1
b.ne .ukr0_try2
ldr s0, [x4]
mov x0,#1065353216
fmov s1,w0
fcmp s0,s1
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr s0, [x4]
mov x0,#1065353216
fmov s1,w0
fcmp s0,s1
b.ne .ukr0_try4
b .ukr0_case4
.ukr0_try4:
b .ukr0_case5
b .ukr0_cases_end
.ukr0_case0:
mov x0,x3
add x1,x0,x6
mov x2,x7
mov x12,#0
add x9,x0,x6
add x10,x0,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr1_slices:
add x2,x2,#-4
st1w {za0v.s[w12, 0]}, p0, [x0]
st1w {za0v.s[w12, 1]}, p0, [x9]
st1w {za0v.s[w12, 2]}, p0, [x10]
st1w {za0v.s[w12, 3]}, p0, [x1]
add x0,x0,x6, LSL #2
add x9,x9,x6, LSL #2
add x10,x10,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
cbnz x2,.ukr1_slices
sub x0,x0,x8
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
add x1,x0,x6
ld1rw {z0.s}, p0/z, [x4]
mov x2,x7
mov x12,#0
add x9,x0,x6
add x10,x0,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr2_slices:
add x2,x2,#-4
mova z1.s,p0/m,za0v.s[w12,0]
mova z2.s,p0/m,za0v.s[w12,1]
mova z3.s,p0/m,za0v.s[w12,2]
mova z4.s,p0/m,za0v.s[w12,3]
fmul z5.s,z1.s,z0.s
fmul z1.s,z2.s,z0.s
fmul z2.s,z3.s,z0.s
fmul z3.s,z4.s,z0.s
st1w {z5.s}, p0, [x0]
st1w {z1.s}, p0, [x9]
st1w {z2.s}, p0, [x10]
st1w {z3.s}, p0, [x1]
add x0,x0,x6, LSL #2
add x9,x9,x6, LSL #2
add x10,x10,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
cbnz x2,.ukr2_slices
sub x0,x0,x8
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
add x1,x0,x6
add x2,x3,x6
mov x9,x7
mov x12,#0
add x10,x0,x6
add x11,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x16,x3,x6
add x17,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr3_slices:
add x9,x9,#-4
mova z0.s,p0/m,za0v.s[w12,0]
ld1w {z1.s}, p0/z, [x0]
mova z2.s,p0/m,za0v.s[w12,1]
ld1w {z3.s}, p0/z, [x10]
mova z4.s,p0/m,za0v.s[w12,2]
ld1w {z5.s}, p0/z, [x11]
mova z6.s,p0/m,za0v.s[w12,3]
ld1w {z7.s}, p0/z, [x1]
fadd z1.s,z0.s,z1.s
fadd z3.s,z2.s,z3.s
fadd z5.s,z4.s,z5.s
fadd z7.s,z6.s,z7.s
st1w {z1.s}, p0, [x3]
st1w {z3.s}, p0, [x16]
st1w {z5.s}, p0, [x17]
st1w {z7.s}, p0, [x2]
add x0,x0,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
cbnz x9,.ukr3_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
add x1,x0,x6
add x2,x3,x6
ld1rw {z0.s}, p0/z, [x4]
mov x9,x7
mov x12,#0
add x10,x0,x6
add x11,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x16,x3,x6
add x17,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr4_slices:
add x9,x9,#-4
mova z1.s,p0/m,za0v.s[w12,0]
ld1w {z2.s}, p0/z, [x0]
mova z3.s,p0/m,za0v.s[w12,1]
ld1w {z4.s}, p0/z, [x10]
mova z5.s,p0/m,za0v.s[w12,2]
ld1w {z6.s}, p0/z, [x11]
mova z7.s,p0/m,za0v.s[w12,3]
ld1w {z16.s}, p0/z, [x1]
fmla z2.s,p0/m,z1.s,z0.s
fmla z4.s,p0/m,z3.s,z0.s
fmla z6.s,p0/m,z5.s,z0.s
fmla z16.s,p0/m,z7.s,z0.s
st1w {z2.s}, p0, [x3]
st1w {z4.s}, p0, [x16]
st1w {z6.s}, p0, [x17]
st1w {z16.s}, p0, [x2]
add x0,x0,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
cbnz x9,.ukr4_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
add x1,x0,x6
add x2,x3,x6
ld1rw {z0.s}, p0/z, [x5]
mov x9,x7
mov x12,#0
add x10,x0,x6
add x11,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x16,x3,x6
add x17,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr5_slices:
add x9,x9,#-4
mova z1.s,p0/m,za0v.s[w12,0]
ld1w {z2.s}, p0/z, [x0]
fmla z1.s,p0/m,z2.s,z0.s
mova za0v.s[w12,0],p0/m,z1.s
mova z2.s,p0/m,za0v.s[w12,1]
ld1w {z3.s}, p0/z, [x10]
fmla z2.s,p0/m,z3.s,z0.s
mova za0v.s[w12,1],p0/m,z2.s
mova z3.s,p0/m,za0v.s[w12,2]
ld1w {z4.s}, p0/z, [x11]
fmla z3.s,p0/m,z4.s,z0.s
mova za0v.s[w12,2],p0/m,z3.s
mova z4.s,p0/m,za0v.s[w12,3]
ld1w {z5.s}, p0/z, [x1]
fmla z4.s,p0/m,z5.s,z0.s
st1w {z1.s}, p0, [x3]
st1w {z2.s}, p0, [x16]
st1w {z3.s}, p0, [x17]
st1w {z4.s}, p0, [x2]
mova za0v.s[w12,3],p0/m,z4.s
add x0,x0,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
cbnz x9,.ukr5_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
add x1,x0,x6
add x2,x3,x6
ld1rw {z0.s}, p0/z, [x5]
ld1rw {z1.s}, p0/z, [x4]
mov x9,x7
mov x12,#0
add x10,x0,x6
add x11,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x16,x3,x6
add x17,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr6_slices:
add x9,x9,#-4
ld1w {z2.s}, p0/z, [x0]
ld1w {z3.s}, p0/z, [x10]
ld1w {z4.s}, p0/z, [x11]
ld1w {z5.s}, p0/z, [x1]
fmul z2.s,z2.s,z0.s
mova z6.s,p0/m,za0v.s[w12,0]
fmul z3.s,z3.s,z0.s
mova z7.s,p0/m,za0v.s[w12,1]
fmul z4.s,z4.s,z0.s
mova z16.s,p0/m,za0v.s[w12,2]
fmul z5.s,z5.s,z0.s
mova z17.s,p0/m,za0v.s[w12,3]
fmla z2.s,p0/m,z6.s,z1.s
fmla z3.s,p0/m,z7.s,z1.s
fmla z4.s,p0/m,z16.s,z1.s
fmla z5.s,p0/m,z17.s,z1.s
st1w {z2.s}, p0, [x3]
st1w {z3.s}, p0, [x16]
st1w {z4.s}, p0, [x17]
st1w {z5.s}, p0, [x2]
add x0,x0,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
cbnz x9,.ukr6_slices
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
.size bli_sgemm_ukrgen_sme_opa_1vx1v_asm, .-bli_sgemm_ukrgen_sme_opa_1vx1v_asm
.section .note.GNU-stack,"",%progbits
