.text
.global bli_dgemm_ukrgen_sve_vn_4x1v_asm
.type bli_dgemm_ukrgen_sve_vn_4x1v_asm, %function
bli_dgemm_ukrgen_sve_vn_4x1v_asm:
.cfi_startproc
# x0 = k
# x1 = base(A)
# x2 = base(B)
# x3 = base(C)
# x4 = base(alpha)
# x5 = base(beta)
# x6 = stride(C,m)
# x7 = stride(C,n)
ptrue p0.d
and x8,x0,#3
lsr x0,x0,#2
dup z0.d,#0
dup z1.d,#0
dup z2.d,#0
dup z3.d,#0
cbz x0,.ukr1_done
ld1rd {z4.d}, p0/z, [x1]
ld1rd {z5.d}, p0/z, [x1, #8]
ld1rd {z6.d}, p0/z, [x1, #16]
ld1rd {z7.d}, p0/z, [x1, #24]
ld1d {z16.d}, p0/z, [x2]
add x1,x1,#32
incb x2, ALL, MUL #1
add x0,x0,#-1
cbz x0,.ukr1_last
.ukr1_loop:
add x0,x0,#-1
fmla z0.d,p0/m,z16.d,z4.d
fmla z1.d,p0/m,z16.d,z5.d
fmla z2.d,p0/m,z16.d,z6.d
fmla z3.d,p0/m,z16.d,z7.d
ld1rd {z17.d}, p0/z, [x1]
ld1d {z18.d}, p0/z, [x2]
ld1rd {z19.d}, p0/z, [x1, #8]
ld1rd {z20.d}, p0/z, [x1, #16]
ld1rd {z21.d}, p0/z, [x1, #24]
fmla z0.d,p0/m,z18.d,z17.d
fmla z1.d,p0/m,z18.d,z19.d
fmla z2.d,p0/m,z18.d,z20.d
fmla z3.d,p0/m,z18.d,z21.d
ld1rd {z22.d}, p0/z, [x1, #32]
ld1d {z23.d}, p0/z, [x2, #1, MUL VL]
ld1rd {z24.d}, p0/z, [x1, #40]
ld1rd {z25.d}, p0/z, [x1, #48]
ld1rd {z26.d}, p0/z, [x1, #56]
fmla z0.d,p0/m,z23.d,z22.d
fmla z1.d,p0/m,z23.d,z24.d
fmla z2.d,p0/m,z23.d,z25.d
fmla z3.d,p0/m,z23.d,z26.d
ld1rd {z27.d}, p0/z, [x1, #64]
ld1d {z28.d}, p0/z, [x2, #2, MUL VL]
ld1rd {z29.d}, p0/z, [x1, #72]
ld1rd {z30.d}, p0/z, [x1, #80]
ld1rd {z31.d}, p0/z, [x1, #88]
ld1rd {z4.d}, p0/z, [x1, #96]
ld1rd {z5.d}, p0/z, [x1, #104]
ld1rd {z6.d}, p0/z, [x1, #112]
ld1rd {z7.d}, p0/z, [x1, #120]
ld1d {z16.d}, p0/z, [x2, #3, MUL VL]
fmla z0.d,p0/m,z28.d,z27.d
fmla z1.d,p0/m,z28.d,z29.d
fmla z2.d,p0/m,z28.d,z30.d
fmla z3.d,p0/m,z28.d,z31.d
add x1,x1,#128
incb x2, ALL, MUL #4
cbnz x0,.ukr1_loop
.ukr1_last:
fmla z0.d,p0/m,z16.d,z4.d
fmla z1.d,p0/m,z16.d,z5.d
fmla z2.d,p0/m,z16.d,z6.d
fmla z3.d,p0/m,z16.d,z7.d
ld1rd {z17.d}, p0/z, [x1]
ld1d {z18.d}, p0/z, [x2]
ld1rd {z19.d}, p0/z, [x1, #8]
ld1rd {z20.d}, p0/z, [x1, #16]
ld1rd {z21.d}, p0/z, [x1, #24]
fmla z0.d,p0/m,z18.d,z17.d
fmla z1.d,p0/m,z18.d,z19.d
fmla z2.d,p0/m,z18.d,z20.d
fmla z3.d,p0/m,z18.d,z21.d
ld1rd {z22.d}, p0/z, [x1, #32]
ld1d {z23.d}, p0/z, [x2, #1, MUL VL]
ld1rd {z24.d}, p0/z, [x1, #40]
ld1rd {z25.d}, p0/z, [x1, #48]
ld1rd {z26.d}, p0/z, [x1, #56]
fmla z0.d,p0/m,z23.d,z22.d
fmla z1.d,p0/m,z23.d,z24.d
fmla z2.d,p0/m,z23.d,z25.d
fmla z3.d,p0/m,z23.d,z26.d
ld1rd {z27.d}, p0/z, [x1, #64]
ld1d {z28.d}, p0/z, [x2, #2, MUL VL]
ld1rd {z29.d}, p0/z, [x1, #72]
ld1rd {z30.d}, p0/z, [x1, #80]
ld1rd {z31.d}, p0/z, [x1, #88]
fmla z0.d,p0/m,z28.d,z27.d
fmla z1.d,p0/m,z28.d,z29.d
fmla z2.d,p0/m,z28.d,z30.d
fmla z3.d,p0/m,z28.d,z31.d
add x1,x1,#96
incb x2, ALL, MUL #3
.ukr1_done:
cbz x8,.ukr1_taildone
.ukr1_tail:
add x8,x8,#-1
ld1rd {z4.d}, p0/z, [x1]
ld1d {z16.d}, p0/z, [x2]
ld1rd {z5.d}, p0/z, [x1, #8]
ld1rd {z6.d}, p0/z, [x1, #16]
ld1rd {z7.d}, p0/z, [x1, #24]
fmla z0.d,p0/m,z16.d,z4.d
fmla z1.d,p0/m,z16.d,z5.d
fmla z2.d,p0/m,z16.d,z6.d
fmla z3.d,p0/m,z16.d,z7.d
add x1,x1,#32
incb x2, ALL, MUL #1
cbnz x8,.ukr1_tail
.ukr1_taildone:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok0_0
b .ukr0_try1
.ukr0_ok0_0:
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
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok1_0
b .ukr0_try2
.ukr0_ok1_0:
ldr d4, [x5]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try2
b .ukr0_case1
.ukr0_try2:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok2_0
b .ukr0_try3
.ukr0_ok2_0:
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
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok3_0
b .ukr0_try4
.ukr0_ok3_0:
ldr d4, [x5]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try4
b .ukr0_case3
.ukr0_try4:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok4_0
b .ukr0_try5
.ukr0_ok4_0:
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try5
b .ukr0_case4
.ukr0_try5:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok5_0
b .ukr0_try6
.ukr0_ok5_0:
b .ukr0_case5
.ukr0_try6:
ldr d4, [x5]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try7
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try7
b .ukr0_case6
.ukr0_try7:
ldr d4, [x5]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try8
b .ukr0_case7
.ukr0_try8:
ldr d4, [x5]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try9
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try9
b .ukr0_case8
.ukr0_try9:
ldr d4, [x5]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try10
b .ukr0_case9
.ukr0_try10:
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try11
b .ukr0_case10
.ukr0_try11:
b .ukr0_case11
.ukr0_try12:
b .ukr0_cases_end
.ukr0_case0:
mov x0,x3
mov x1,x3
add x2,x0,x6
mov x8,x0
add x8,x8,x6, LSL #1
mov x9,x0
add x9,x9,x6
add x9,x9,x6, LSL #1
st1d {z0.d}, p0, [x0]
st1d {z1.d}, p0, [x2]
st1d {z2.d}, p0, [x8]
st1d {z3.d}, p0, [x9]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
mov x1,x3
ld1rd {z4.d}, p0/z, [x4]
add x2,x0,x6
mov x8,x0
add x8,x8,x6, LSL #1
mov x9,x0
add x9,x9,x6
add x9,x9,x6, LSL #1
fmul z5.d,z0.d,z4.d
fmul z0.d,z1.d,z4.d
fmul z1.d,z2.d,z4.d
fmul z2.d,z3.d,z4.d
st1d {z5.d}, p0, [x0]
st1d {z0.d}, p0, [x2]
st1d {z1.d}, p0, [x8]
st1d {z2.d}, p0, [x9]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x3
add x2,x0,x6
mov x8,x0
add x8,x8,x6, LSL #1
ld1d {z4.d}, p0/z, [x0]
ld1d {z5.d}, p0/z, [x2]
ld1d {z6.d}, p0/z, [x8]
add x9,x1,x6
fadd z4.d,z0.d,z4.d
mov x10,x0
add x10,x10,x6
add x10,x10,x6, LSL #1
fadd z5.d,z1.d,z5.d
fadd z6.d,z2.d,z6.d
mov x11,x1
add x11,x11,x6, LSL #1
st1d {z4.d}, p0, [x1]
ld1d {z0.d}, p0/z, [x10]
mov x12,x1
add x12,x12,x6
add x12,x12,x6, LSL #1
st1d {z5.d}, p0, [x9]
st1d {z6.d}, p0, [x11]
fadd z0.d,z3.d,z0.d
st1d {z0.d}, p0, [x12]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
mov x1,x3
add x2,x0,x6
mov x8,x0
add x8,x8,x6, LSL #1
ld1rd {z4.d}, p0/z, [x4]
ld1d {z5.d}, p0/z, [x0]
ld1d {z6.d}, p0/z, [x2]
ld1d {z7.d}, p0/z, [x8]
add x9,x1,x6
fmla z5.d,p0/m,z0.d,z4.d
mov x10,x0
add x10,x10,x6
add x10,x10,x6, LSL #1
fmla z6.d,p0/m,z1.d,z4.d
fmla z7.d,p0/m,z2.d,z4.d
mov x11,x1
add x11,x11,x6, LSL #1
st1d {z5.d}, p0, [x1]
ld1d {z0.d}, p0/z, [x10]
mov x12,x1
add x12,x12,x6
add x12,x12,x6, LSL #1
st1d {z6.d}, p0, [x9]
st1d {z7.d}, p0, [x11]
fmla z0.d,p0/m,z3.d,z4.d
st1d {z0.d}, p0, [x12]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
mov x1,x3
add x2,x0,x6
mov x8,x0
add x8,x8,x6, LSL #1
ld1rd {z4.d}, p0/z, [x5]
ld1d {z5.d}, p0/z, [x0]
ld1d {z6.d}, p0/z, [x2]
ld1d {z7.d}, p0/z, [x8]
add x9,x1,x6
fmla z0.d,p0/m,z5.d,z4.d
mov x10,x0
add x10,x10,x6
add x10,x10,x6, LSL #1
fmla z1.d,p0/m,z6.d,z4.d
fmla z2.d,p0/m,z7.d,z4.d
mov x11,x1
add x11,x11,x6, LSL #1
st1d {z0.d}, p0, [x1]
ld1d {z0.d}, p0/z, [x10]
mov x12,x1
add x12,x12,x6
add x12,x12,x6, LSL #1
st1d {z1.d}, p0, [x9]
st1d {z2.d}, p0, [x11]
fmla z3.d,p0/m,z0.d,z4.d
st1d {z3.d}, p0, [x12]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
mov x1,x3
add x2,x0,x6
ld1rd {z4.d}, p0/z, [x5]
mov x8,x0
add x8,x8,x6, LSL #1
ld1d {z5.d}, p0/z, [x0]
ld1d {z6.d}, p0/z, [x2]
ld1d {z7.d}, p0/z, [x8]
ld1rd {z16.d}, p0/z, [x4]
fmul z5.d,z5.d,z4.d
fmul z6.d,z6.d,z4.d
fmul z7.d,z7.d,z4.d
add x9,x1,x6
fmla z5.d,p0/m,z0.d,z16.d
fmla z6.d,p0/m,z1.d,z16.d
fmla z7.d,p0/m,z2.d,z16.d
mov x10,x1
add x10,x10,x6, LSL #1
st1d {z5.d}, p0, [x1]
mov x11,x0
add x11,x11,x6
add x11,x11,x6, LSL #1
ld1d {z0.d}, p0/z, [x11]
mov x12,x1
add x12,x12,x6
add x12,x12,x6, LSL #1
st1d {z6.d}, p0, [x9]
st1d {z7.d}, p0, [x10]
fmul z0.d,z0.d,z4.d
fmla z0.d,p0/m,z3.d,z16.d
st1d {z0.d}, p0, [x12]
b .ukr0_cases_end
.ukr0_case6:
mov x0,x3
index z4.d,#0,x7
add x1,x0,x6
mov x2,x0
add x2,x2,x6, LSL #1
mov x8,x0
add x8,x8,x6
add x8,x8,x6, LSL #1
st1d {z0.d}, p0, [x0, z4.d]
st1d {z1.d}, p0, [x1, z4.d]
st1d {z2.d}, p0, [x2, z4.d]
st1d {z3.d}, p0, [x8, z4.d]
b .ukr0_cases_end
.ukr0_case7:
mov x0,x3
index z4.d,#0,x7
ld1rd {z5.d}, p0/z, [x4]
add x1,x0,x6
mov x2,x0
add x2,x2,x6, LSL #1
mov x8,x0
add x8,x8,x6
add x8,x8,x6, LSL #1
fmul z6.d,z0.d,z5.d
fmul z0.d,z1.d,z5.d
fmul z1.d,z2.d,z5.d
fmul z2.d,z3.d,z5.d
st1d {z6.d}, p0, [x0, z4.d]
st1d {z0.d}, p0, [x1, z4.d]
st1d {z1.d}, p0, [x2, z4.d]
st1d {z2.d}, p0, [x8, z4.d]
b .ukr0_cases_end
.ukr0_case8:
mov x0,x3
index z4.d,#0,x7
add x1,x0,x6
mov x2,x0
add x2,x2,x6, LSL #1
ld1d {z5.d}, p0/z, [x0, z4.d]
ld1d {z6.d}, p0/z, [x1, z4.d]
ld1d {z7.d}, p0/z, [x2, z4.d]
add x8,x3,x6
fadd z5.d,z0.d,z5.d
mov x9,x0
add x9,x9,x6
add x9,x9,x6, LSL #1
fadd z6.d,z1.d,z6.d
fadd z7.d,z2.d,z7.d
mov x10,x3
add x10,x10,x6, LSL #1
st1d {z5.d}, p0, [x3, z4.d]
ld1d {z0.d}, p0/z, [x9, z4.d]
mov x11,x3
add x11,x11,x6
add x11,x11,x6, LSL #1
st1d {z6.d}, p0, [x8, z4.d]
st1d {z7.d}, p0, [x10, z4.d]
fadd z0.d,z3.d,z0.d
st1d {z0.d}, p0, [x11, z4.d]
b .ukr0_cases_end
.ukr0_case9:
mov x0,x3
index z4.d,#0,x7
add x1,x0,x6
mov x2,x0
add x2,x2,x6, LSL #1
ld1d {z5.d}, p0/z, [x0, z4.d]
ld1rd {z6.d}, p0/z, [x4]
ld1d {z7.d}, p0/z, [x1, z4.d]
ld1d {z16.d}, p0/z, [x2, z4.d]
add x8,x3,x6
fmla z5.d,p0/m,z0.d,z6.d
mov x9,x0
add x9,x9,x6
add x9,x9,x6, LSL #1
fmla z7.d,p0/m,z1.d,z6.d
fmla z16.d,p0/m,z2.d,z6.d
mov x10,x3
add x10,x10,x6, LSL #1
st1d {z5.d}, p0, [x3, z4.d]
ld1d {z0.d}, p0/z, [x9, z4.d]
mov x11,x3
add x11,x11,x6
add x11,x11,x6, LSL #1
st1d {z7.d}, p0, [x8, z4.d]
st1d {z16.d}, p0, [x10, z4.d]
fmla z0.d,p0/m,z3.d,z6.d
st1d {z0.d}, p0, [x11, z4.d]
b .ukr0_cases_end
.ukr0_case10:
mov x0,x3
index z4.d,#0,x7
add x1,x0,x6
mov x2,x0
add x2,x2,x6, LSL #1
ld1d {z5.d}, p0/z, [x0, z4.d]
ld1rd {z6.d}, p0/z, [x5]
ld1d {z7.d}, p0/z, [x1, z4.d]
ld1d {z16.d}, p0/z, [x2, z4.d]
add x8,x3,x6
fmla z0.d,p0/m,z5.d,z6.d
mov x9,x0
add x9,x9,x6
add x9,x9,x6, LSL #1
fmla z1.d,p0/m,z7.d,z6.d
fmla z2.d,p0/m,z16.d,z6.d
mov x10,x3
add x10,x10,x6, LSL #1
st1d {z0.d}, p0, [x3, z4.d]
ld1d {z0.d}, p0/z, [x9, z4.d]
mov x11,x3
add x11,x11,x6
add x11,x11,x6, LSL #1
st1d {z1.d}, p0, [x8, z4.d]
st1d {z2.d}, p0, [x10, z4.d]
fmla z3.d,p0/m,z0.d,z6.d
st1d {z3.d}, p0, [x11, z4.d]
b .ukr0_cases_end
.ukr0_case11:
mov x0,x3
index z4.d,#0,x7
add x1,x0,x6
ld1d {z5.d}, p0/z, [x0, z4.d]
mov x2,x0
add x2,x2,x6, LSL #1
ld1rd {z6.d}, p0/z, [x5]
ld1d {z7.d}, p0/z, [x1, z4.d]
ld1d {z16.d}, p0/z, [x2, z4.d]
ld1rd {z17.d}, p0/z, [x4]
fmul z5.d,z5.d,z6.d
fmul z7.d,z7.d,z6.d
fmul z16.d,z16.d,z6.d
add x8,x3,x6
fmla z5.d,p0/m,z0.d,z17.d
fmla z7.d,p0/m,z1.d,z17.d
fmla z16.d,p0/m,z2.d,z17.d
mov x9,x3
add x9,x9,x6, LSL #1
st1d {z5.d}, p0, [x3, z4.d]
mov x10,x0
add x10,x10,x6
add x10,x10,x6, LSL #1
ld1d {z0.d}, p0/z, [x10, z4.d]
mov x11,x3
add x11,x11,x6
add x11,x11,x6, LSL #1
st1d {z7.d}, p0, [x8, z4.d]
st1d {z16.d}, p0, [x9, z4.d]
fmul z0.d,z0.d,z6.d
fmla z0.d,p0/m,z3.d,z17.d
st1d {z0.d}, p0, [x11, z4.d]
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dgemm_ukrgen_sve_vn_4x1v_asm, .-bli_dgemm_ukrgen_sve_vn_4x1v_asm
.section .note.GNU-stack,"",%progbits
