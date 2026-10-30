.text
.global bli_dgemm_ukrgen_sve_vm_1vx4_asm
.type bli_dgemm_ukrgen_sve_vm_1vx4_asm, %function
bli_dgemm_ukrgen_sve_vm_1vx4_asm:
.cfi_startproc
# x0 = k
# x1 = base(A)
# x2 = base(B)
# x3 = base(C)
# x4 = base(alpha)
# x5 = base(beta)
# x6 = stride(C,n)
ptrue p0.d
and x7,x0,#3
lsr x0,x0,#2
dup z0.d,#0
dup z1.d,#0
dup z2.d,#0
dup z3.d,#0
cbz x0,.ukr1_done
ld1d {z4.d}, p0/z, [x1]
ld1rd {z5.d}, p0/z, [x2]
ld1rd {z6.d}, p0/z, [x2, #8]
ld1rd {z7.d}, p0/z, [x2, #16]
ld1rd {z16.d}, p0/z, [x2, #24]
incb x1, ALL, MUL #1
add x2,x2,#32
add x0,x0,#-1
cbz x0,.ukr1_last
.ukr1_loop:
add x0,x0,#-1
fmla z0.d,p0/m,z4.d,z5.d
fmla z1.d,p0/m,z4.d,z6.d
fmla z2.d,p0/m,z4.d,z7.d
fmla z3.d,p0/m,z4.d,z16.d
ld1d {z17.d}, p0/z, [x1]
ld1rd {z18.d}, p0/z, [x2]
ld1rd {z19.d}, p0/z, [x2, #8]
ld1rd {z20.d}, p0/z, [x2, #16]
ld1rd {z21.d}, p0/z, [x2, #24]
fmla z0.d,p0/m,z17.d,z18.d
fmla z1.d,p0/m,z17.d,z19.d
fmla z2.d,p0/m,z17.d,z20.d
fmla z3.d,p0/m,z17.d,z21.d
ld1d {z22.d}, p0/z, [x1, #1, MUL VL]
ld1rd {z23.d}, p0/z, [x2, #32]
ld1rd {z24.d}, p0/z, [x2, #40]
ld1rd {z25.d}, p0/z, [x2, #48]
ld1rd {z26.d}, p0/z, [x2, #56]
fmla z0.d,p0/m,z22.d,z23.d
fmla z1.d,p0/m,z22.d,z24.d
fmla z2.d,p0/m,z22.d,z25.d
fmla z3.d,p0/m,z22.d,z26.d
ld1d {z27.d}, p0/z, [x1, #2, MUL VL]
ld1rd {z28.d}, p0/z, [x2, #64]
ld1rd {z29.d}, p0/z, [x2, #72]
ld1rd {z30.d}, p0/z, [x2, #80]
ld1rd {z31.d}, p0/z, [x2, #88]
ld1d {z4.d}, p0/z, [x1, #3, MUL VL]
ld1rd {z5.d}, p0/z, [x2, #96]
ld1rd {z6.d}, p0/z, [x2, #104]
ld1rd {z7.d}, p0/z, [x2, #112]
ld1rd {z16.d}, p0/z, [x2, #120]
fmla z0.d,p0/m,z27.d,z28.d
fmla z1.d,p0/m,z27.d,z29.d
fmla z2.d,p0/m,z27.d,z30.d
fmla z3.d,p0/m,z27.d,z31.d
incb x1, ALL, MUL #4
add x2,x2,#128
cbnz x0,.ukr1_loop
.ukr1_last:
fmla z0.d,p0/m,z4.d,z5.d
fmla z1.d,p0/m,z4.d,z6.d
fmla z2.d,p0/m,z4.d,z7.d
fmla z3.d,p0/m,z4.d,z16.d
ld1d {z17.d}, p0/z, [x1]
ld1rd {z18.d}, p0/z, [x2]
ld1rd {z19.d}, p0/z, [x2, #8]
ld1rd {z20.d}, p0/z, [x2, #16]
ld1rd {z21.d}, p0/z, [x2, #24]
fmla z0.d,p0/m,z17.d,z18.d
fmla z1.d,p0/m,z17.d,z19.d
fmla z2.d,p0/m,z17.d,z20.d
fmla z3.d,p0/m,z17.d,z21.d
ld1d {z22.d}, p0/z, [x1, #1, MUL VL]
ld1rd {z23.d}, p0/z, [x2, #32]
ld1rd {z24.d}, p0/z, [x2, #40]
ld1rd {z25.d}, p0/z, [x2, #48]
ld1rd {z26.d}, p0/z, [x2, #56]
fmla z0.d,p0/m,z22.d,z23.d
fmla z1.d,p0/m,z22.d,z24.d
fmla z2.d,p0/m,z22.d,z25.d
fmla z3.d,p0/m,z22.d,z26.d
ld1d {z27.d}, p0/z, [x1, #2, MUL VL]
ld1rd {z28.d}, p0/z, [x2, #64]
ld1rd {z29.d}, p0/z, [x2, #72]
ld1rd {z30.d}, p0/z, [x2, #80]
ld1rd {z31.d}, p0/z, [x2, #88]
fmla z0.d,p0/m,z27.d,z28.d
fmla z1.d,p0/m,z27.d,z29.d
fmla z2.d,p0/m,z27.d,z30.d
fmla z3.d,p0/m,z27.d,z31.d
incb x1, ALL, MUL #3
add x2,x2,#96
.ukr1_done:
cbz x7,.ukr1_taildone
.ukr1_tail:
add x7,x7,#-1
ld1d {z4.d}, p0/z, [x1]
ld1rd {z5.d}, p0/z, [x2]
ld1rd {z6.d}, p0/z, [x2, #8]
ld1rd {z7.d}, p0/z, [x2, #16]
ld1rd {z16.d}, p0/z, [x2, #24]
fmla z0.d,p0/m,z4.d,z5.d
fmla z1.d,p0/m,z4.d,z6.d
fmla z2.d,p0/m,z4.d,z7.d
fmla z3.d,p0/m,z4.d,z16.d
incb x1, ALL, MUL #1
add x2,x2,#32
cbnz x7,.ukr1_tail
.ukr1_taildone:
ldr d4, [x5]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try1
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
ldr d4, [x5]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try2
b .ukr0_case1
.ukr0_try2:
ldr d4, [x5]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try3
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
ldr d4, [x5]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try4
b .ukr0_case3
.ukr0_try4:
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try5
b .ukr0_case4
.ukr0_try5:
b .ukr0_case5
.ukr0_try6:
b .ukr0_cases_end
.ukr0_case0:
mov x0,x3
mov x1,x0
add x1,x1,x6
mov x2,x0
add x2,x2,x6, LSL #1
mov x7,x0
add x7,x7,x6
add x7,x7,x6, LSL #1
st1d {z0.d}, p0, [x0]
st1d {z1.d}, p0, [x1]
st1d {z2.d}, p0, [x2]
st1d {z3.d}, p0, [x7]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
ld1rd {z4.d}, p0/z, [x4]
mov x1,x0
add x1,x1,x6
mov x2,x0
add x2,x2,x6, LSL #1
mov x7,x0
add x7,x7,x6
add x7,x7,x6, LSL #1
fmul z5.d,z0.d,z4.d
fmul z0.d,z1.d,z4.d
fmul z1.d,z2.d,z4.d
fmul z2.d,z3.d,z4.d
st1d {z5.d}, p0, [x0]
st1d {z0.d}, p0, [x1]
st1d {z1.d}, p0, [x2]
st1d {z2.d}, p0, [x7]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x0
add x1,x1,x6
mov x2,x0
add x2,x2,x6, LSL #1
ld1d {z4.d}, p0/z, [x0]
ld1d {z5.d}, p0/z, [x1]
ld1d {z6.d}, p0/z, [x2]
mov x7,x3
add x7,x7,x6
fadd z4.d,z0.d,z4.d
mov x8,x0
add x8,x8,x6
add x8,x8,x6, LSL #1
fadd z5.d,z1.d,z5.d
fadd z6.d,z2.d,z6.d
mov x9,x3
add x9,x9,x6, LSL #1
st1d {z4.d}, p0, [x3]
ld1d {z0.d}, p0/z, [x8]
mov x10,x3
add x10,x10,x6
add x10,x10,x6, LSL #1
st1d {z5.d}, p0, [x7]
st1d {z6.d}, p0, [x9]
fadd z0.d,z3.d,z0.d
st1d {z0.d}, p0, [x10]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
mov x1,x0
add x1,x1,x6
mov x2,x0
add x2,x2,x6, LSL #1
ld1d {z4.d}, p0/z, [x0]
ld1rd {z5.d}, p0/z, [x4]
ld1d {z6.d}, p0/z, [x1]
ld1d {z7.d}, p0/z, [x2]
mov x7,x3
add x7,x7,x6
fmla z4.d,p0/m,z0.d,z5.d
mov x8,x0
add x8,x8,x6
add x8,x8,x6, LSL #1
fmla z6.d,p0/m,z1.d,z5.d
fmla z7.d,p0/m,z2.d,z5.d
mov x9,x3
add x9,x9,x6, LSL #1
st1d {z4.d}, p0, [x3]
ld1d {z0.d}, p0/z, [x8]
mov x10,x3
add x10,x10,x6
add x10,x10,x6, LSL #1
st1d {z6.d}, p0, [x7]
st1d {z7.d}, p0, [x9]
fmla z0.d,p0/m,z3.d,z5.d
st1d {z0.d}, p0, [x10]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
mov x1,x0
add x1,x1,x6
mov x2,x0
add x2,x2,x6, LSL #1
ld1d {z4.d}, p0/z, [x0]
ld1rd {z5.d}, p0/z, [x5]
ld1d {z6.d}, p0/z, [x1]
ld1d {z7.d}, p0/z, [x2]
mov x7,x3
add x7,x7,x6
fmla z0.d,p0/m,z4.d,z5.d
mov x8,x0
add x8,x8,x6
add x8,x8,x6, LSL #1
fmla z1.d,p0/m,z6.d,z5.d
fmla z2.d,p0/m,z7.d,z5.d
mov x9,x3
add x9,x9,x6, LSL #1
st1d {z0.d}, p0, [x3]
ld1d {z0.d}, p0/z, [x8]
mov x10,x3
add x10,x10,x6
add x10,x10,x6, LSL #1
st1d {z1.d}, p0, [x7]
st1d {z2.d}, p0, [x9]
fmla z3.d,p0/m,z0.d,z5.d
st1d {z3.d}, p0, [x10]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
mov x1,x0
add x1,x1,x6
ld1d {z4.d}, p0/z, [x0]
mov x2,x0
add x2,x2,x6, LSL #1
ld1rd {z5.d}, p0/z, [x5]
ld1d {z6.d}, p0/z, [x1]
ld1d {z7.d}, p0/z, [x2]
ld1rd {z16.d}, p0/z, [x4]
fmul z4.d,z4.d,z5.d
fmul z6.d,z6.d,z5.d
fmul z7.d,z7.d,z5.d
mov x7,x3
add x7,x7,x6
fmla z4.d,p0/m,z0.d,z16.d
fmla z6.d,p0/m,z1.d,z16.d
fmla z7.d,p0/m,z2.d,z16.d
mov x8,x3
add x8,x8,x6, LSL #1
st1d {z4.d}, p0, [x3]
mov x9,x0
add x9,x9,x6
add x9,x9,x6, LSL #1
ld1d {z0.d}, p0/z, [x9]
mov x10,x3
add x10,x10,x6
add x10,x10,x6, LSL #1
st1d {z6.d}, p0, [x7]
st1d {z7.d}, p0, [x8]
fmul z0.d,z0.d,z5.d
fmla z0.d,p0/m,z3.d,z16.d
st1d {z0.d}, p0, [x10]
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dgemm_ukrgen_sve_vm_1vx4_asm, .-bli_dgemm_ukrgen_sve_vm_1vx4_asm
.section .note.GNU-stack,"",%progbits
