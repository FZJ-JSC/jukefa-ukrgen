.text
.global bli_dgemm_ukrgen_sve_vn_4x2v_asm
.type bli_dgemm_ukrgen_sve_vn_4x2v_asm, %function
bli_dgemm_ukrgen_sve_vn_4x2v_asm:
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
# x6 = stride(C,m)
# x7 = stride(C,n)
ptrue p0.d
lsr x8,x6,#3
cntd x9
mul x10,x9,x7
and x11,x0,#3
lsr x0,x0,#2
dup z0.d,#0
dup z1.d,#0
dup z2.d,#0
dup z3.d,#0
dup z4.d,#0
dup z5.d,#0
dup z6.d,#0
dup z7.d,#0
cbz x0,.ukr1_done
ld1rd {z16.d}, p0/z, [x1]
ld1rd {z17.d}, p0/z, [x1, #8]
ld1rd {z18.d}, p0/z, [x1, #16]
ld1rd {z19.d}, p0/z, [x1, #24]
ld1d {z20.d}, p0/z, [x2]
ld1d {z21.d}, p0/z, [x2, #1, MUL VL]
add x1,x1,#32
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr1_last
.ukr1_loop:
add x0,x0,#-1
fmla z0.d,p0/m,z20.d,z16.d
fmla z1.d,p0/m,z21.d,z16.d
fmla z2.d,p0/m,z20.d,z17.d
fmla z3.d,p0/m,z21.d,z17.d
fmla z4.d,p0/m,z20.d,z18.d
fmla z5.d,p0/m,z21.d,z18.d
fmla z6.d,p0/m,z20.d,z19.d
fmla z7.d,p0/m,z21.d,z19.d
ld1rd {z22.d}, p0/z, [x1]
ld1d {z23.d}, p0/z, [x2]
ld1d {z24.d}, p0/z, [x2, #1, MUL VL]
ld1rd {z25.d}, p0/z, [x1, #8]
ld1rd {z26.d}, p0/z, [x1, #16]
ld1rd {z27.d}, p0/z, [x1, #24]
fmla z0.d,p0/m,z23.d,z22.d
fmla z1.d,p0/m,z24.d,z22.d
fmla z2.d,p0/m,z23.d,z25.d
fmla z3.d,p0/m,z24.d,z25.d
fmla z4.d,p0/m,z23.d,z26.d
fmla z5.d,p0/m,z24.d,z26.d
fmla z6.d,p0/m,z23.d,z27.d
fmla z7.d,p0/m,z24.d,z27.d
ld1rd {z28.d}, p0/z, [x1, #32]
ld1d {z29.d}, p0/z, [x2, #2, MUL VL]
ld1d {z30.d}, p0/z, [x2, #3, MUL VL]
ld1rd {z31.d}, p0/z, [x1, #40]
ld1rd {z8.d}, p0/z, [x1, #48]
ld1rd {z9.d}, p0/z, [x1, #56]
fmla z0.d,p0/m,z29.d,z28.d
fmla z1.d,p0/m,z30.d,z28.d
fmla z2.d,p0/m,z29.d,z31.d
fmla z3.d,p0/m,z30.d,z31.d
fmla z4.d,p0/m,z29.d,z8.d
fmla z5.d,p0/m,z30.d,z8.d
fmla z6.d,p0/m,z29.d,z9.d
fmla z7.d,p0/m,z30.d,z9.d
ld1rd {z10.d}, p0/z, [x1, #64]
ld1d {z11.d}, p0/z, [x2, #4, MUL VL]
ld1d {z12.d}, p0/z, [x2, #5, MUL VL]
ld1rd {z13.d}, p0/z, [x1, #72]
ld1rd {z14.d}, p0/z, [x1, #80]
ld1rd {z15.d}, p0/z, [x1, #88]
ld1rd {z16.d}, p0/z, [x1, #96]
ld1rd {z17.d}, p0/z, [x1, #104]
ld1rd {z18.d}, p0/z, [x1, #112]
ld1rd {z19.d}, p0/z, [x1, #120]
ld1d {z20.d}, p0/z, [x2, #6, MUL VL]
ld1d {z21.d}, p0/z, [x2, #7, MUL VL]
fmla z0.d,p0/m,z11.d,z10.d
fmla z1.d,p0/m,z12.d,z10.d
fmla z2.d,p0/m,z11.d,z13.d
fmla z3.d,p0/m,z12.d,z13.d
fmla z4.d,p0/m,z11.d,z14.d
fmla z5.d,p0/m,z12.d,z14.d
fmla z6.d,p0/m,z11.d,z15.d
fmla z7.d,p0/m,z12.d,z15.d
add x1,x1,#128
incb x2, ALL, MUL #8
cbnz x0,.ukr1_loop
.ukr1_last:
fmla z0.d,p0/m,z20.d,z16.d
fmla z1.d,p0/m,z21.d,z16.d
fmla z2.d,p0/m,z20.d,z17.d
fmla z3.d,p0/m,z21.d,z17.d
fmla z4.d,p0/m,z20.d,z18.d
fmla z5.d,p0/m,z21.d,z18.d
fmla z6.d,p0/m,z20.d,z19.d
fmla z7.d,p0/m,z21.d,z19.d
ld1rd {z22.d}, p0/z, [x1]
ld1d {z23.d}, p0/z, [x2]
ld1d {z24.d}, p0/z, [x2, #1, MUL VL]
ld1rd {z25.d}, p0/z, [x1, #8]
ld1rd {z26.d}, p0/z, [x1, #16]
ld1rd {z27.d}, p0/z, [x1, #24]
fmla z0.d,p0/m,z23.d,z22.d
fmla z1.d,p0/m,z24.d,z22.d
fmla z2.d,p0/m,z23.d,z25.d
fmla z3.d,p0/m,z24.d,z25.d
fmla z4.d,p0/m,z23.d,z26.d
fmla z5.d,p0/m,z24.d,z26.d
fmla z6.d,p0/m,z23.d,z27.d
fmla z7.d,p0/m,z24.d,z27.d
ld1rd {z28.d}, p0/z, [x1, #32]
ld1d {z29.d}, p0/z, [x2, #2, MUL VL]
ld1d {z30.d}, p0/z, [x2, #3, MUL VL]
ld1rd {z31.d}, p0/z, [x1, #40]
ld1rd {z8.d}, p0/z, [x1, #48]
ld1rd {z9.d}, p0/z, [x1, #56]
fmla z0.d,p0/m,z29.d,z28.d
fmla z1.d,p0/m,z30.d,z28.d
fmla z2.d,p0/m,z29.d,z31.d
fmla z3.d,p0/m,z30.d,z31.d
fmla z4.d,p0/m,z29.d,z8.d
fmla z5.d,p0/m,z30.d,z8.d
fmla z6.d,p0/m,z29.d,z9.d
fmla z7.d,p0/m,z30.d,z9.d
ld1rd {z10.d}, p0/z, [x1, #64]
ld1d {z11.d}, p0/z, [x2, #4, MUL VL]
ld1d {z12.d}, p0/z, [x2, #5, MUL VL]
ld1rd {z13.d}, p0/z, [x1, #72]
ld1rd {z14.d}, p0/z, [x1, #80]
ld1rd {z15.d}, p0/z, [x1, #88]
fmla z0.d,p0/m,z11.d,z10.d
fmla z1.d,p0/m,z12.d,z10.d
fmla z2.d,p0/m,z11.d,z13.d
fmla z3.d,p0/m,z12.d,z13.d
fmla z4.d,p0/m,z11.d,z14.d
fmla z5.d,p0/m,z12.d,z14.d
fmla z6.d,p0/m,z11.d,z15.d
fmla z7.d,p0/m,z12.d,z15.d
add x1,x1,#96
incb x2, ALL, MUL #6
.ukr1_done:
cbz x11,.ukr1_taildone
.ukr1_tail:
add x11,x11,#-1
ld1rd {z16.d}, p0/z, [x1]
ld1d {z20.d}, p0/z, [x2]
ld1d {z21.d}, p0/z, [x2, #1, MUL VL]
ld1rd {z17.d}, p0/z, [x1, #8]
ld1rd {z18.d}, p0/z, [x1, #16]
ld1rd {z19.d}, p0/z, [x1, #24]
fmla z0.d,p0/m,z20.d,z16.d
fmla z1.d,p0/m,z21.d,z16.d
fmla z2.d,p0/m,z20.d,z17.d
fmla z3.d,p0/m,z21.d,z17.d
fmla z4.d,p0/m,z20.d,z18.d
fmla z5.d,p0/m,z21.d,z18.d
fmla z6.d,p0/m,z20.d,z19.d
fmla z7.d,p0/m,z21.d,z19.d
add x1,x1,#32
incb x2, ALL, MUL #2
cbnz x11,.ukr1_tail
.ukr1_taildone:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok0_0
b .ukr0_try1
.ukr0_ok0_0:
ldr d16, [x5]
fmov d17,xzr
fcmp d16,d17
b.ne .ukr0_try1
ldr d16, [x4]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok1_0
b .ukr0_try2
.ukr0_ok1_0:
ldr d16, [x5]
fmov d17,xzr
fcmp d16,d17
b.ne .ukr0_try2
b .ukr0_case1
.ukr0_try2:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok2_0
b .ukr0_try3
.ukr0_ok2_0:
ldr d16, [x5]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try3
ldr d16, [x4]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok3_0
b .ukr0_try4
.ukr0_ok3_0:
ldr d16, [x5]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try4
b .ukr0_case3
.ukr0_try4:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok4_0
b .ukr0_try5
.ukr0_ok4_0:
ldr d16, [x4]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
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
ldr d16, [x5]
fmov d17,xzr
fcmp d16,d17
b.ne .ukr0_try7
ldr d16, [x4]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try7
b .ukr0_case6
.ukr0_try7:
ldr d16, [x5]
fmov d17,xzr
fcmp d16,d17
b.ne .ukr0_try8
b .ukr0_case7
.ukr0_try8:
ldr d16, [x5]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try9
ldr d16, [x4]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try9
b .ukr0_case8
.ukr0_try9:
ldr d16, [x5]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try10
b .ukr0_case9
.ukr0_try10:
ldr d16, [x4]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try11
b .ukr0_case10
.ukr0_try11:
b .ukr0_case11
.ukr0_try12:
b .ukr0_cases_end
.ukr0_case0:
mov x0,x3
mov x1,x3
st1d {z0.d}, p0, [x0]
st1d {z1.d}, p0, [x0, #1, MUL VL]
st1d {z2.d}, p0, [x0, x8, lsl #3]
add x0,x0,x6
st1d {z3.d}, p0, [x0, #1, MUL VL]
st1d {z4.d}, p0, [x0, x8, lsl #3]
add x0,x0,x6
st1d {z5.d}, p0, [x0, #1, MUL VL]
st1d {z6.d}, p0, [x0, x8, lsl #3]
add x0,x0,x6
st1d {z7.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
mov x1,x3
ld1rd {z16.d}, p0/z, [x4]
fmul z17.d,z0.d,z16.d
fmul z0.d,z1.d,z16.d
fmul z1.d,z2.d,z16.d
fmul z2.d,z3.d,z16.d
fmul z3.d,z4.d,z16.d
st1d {z17.d}, p0, [x0]
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x8, lsl #3]
fmul z0.d,z5.d,z16.d
fmul z1.d,z6.d,z16.d
add x0,x0,x6
st1d {z2.d}, p0, [x0, #1, MUL VL]
st1d {z3.d}, p0, [x0, x8, lsl #3]
fmul z2.d,z7.d,z16.d
add x0,x0,x6
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x8, lsl #3]
add x0,x0,x6
st1d {z2.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x3
ld1d {z16.d}, p0/z, [x0]
ld1d {z17.d}, p0/z, [x0, #1, MUL VL]
ld1d {z18.d}, p0/z, [x0, x8, lsl #3]
add x0,x0,x6
ld1d {z19.d}, p0/z, [x0, #1, MUL VL]
fadd z16.d,z0.d,z16.d
fadd z17.d,z1.d,z17.d
fadd z18.d,z2.d,z18.d
fadd z19.d,z3.d,z19.d
st1d {z16.d}, p0, [x1]
ld1d {z0.d}, p0/z, [x0, x8, lsl #3]
st1d {z17.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6
ld1d {z1.d}, p0/z, [x0, #1, MUL VL]
fadd z0.d,z4.d,z0.d
st1d {z18.d}, p0, [x1, x8, lsl #3]
ld1d {z2.d}, p0/z, [x0, x8, lsl #3]
fadd z1.d,z5.d,z1.d
add x1,x1,x6
st1d {z19.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6
ld1d {z3.d}, p0/z, [x0, #1, MUL VL]
fadd z2.d,z6.d,z2.d
st1d {z0.d}, p0, [x1, x8, lsl #3]
add x1,x1,x6
fadd z3.d,z7.d,z3.d
st1d {z1.d}, p0, [x1, #1, MUL VL]
st1d {z2.d}, p0, [x1, x8, lsl #3]
add x1,x1,x6
st1d {z3.d}, p0, [x1, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
mov x1,x3
ld1rd {z16.d}, p0/z, [x4]
ld1d {z17.d}, p0/z, [x0]
ld1d {z18.d}, p0/z, [x0, #1, MUL VL]
ld1d {z19.d}, p0/z, [x0, x8, lsl #3]
add x0,x0,x6
ld1d {z20.d}, p0/z, [x0, #1, MUL VL]
fmla z17.d,p0/m,z0.d,z16.d
fmla z18.d,p0/m,z1.d,z16.d
fmla z19.d,p0/m,z2.d,z16.d
fmla z20.d,p0/m,z3.d,z16.d
st1d {z17.d}, p0, [x1]
ld1d {z0.d}, p0/z, [x0, x8, lsl #3]
st1d {z18.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6
ld1d {z1.d}, p0/z, [x0, #1, MUL VL]
fmla z0.d,p0/m,z4.d,z16.d
st1d {z19.d}, p0, [x1, x8, lsl #3]
ld1d {z2.d}, p0/z, [x0, x8, lsl #3]
fmla z1.d,p0/m,z5.d,z16.d
add x1,x1,x6
st1d {z20.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6
ld1d {z3.d}, p0/z, [x0, #1, MUL VL]
fmla z2.d,p0/m,z6.d,z16.d
st1d {z0.d}, p0, [x1, x8, lsl #3]
add x1,x1,x6
fmla z3.d,p0/m,z7.d,z16.d
st1d {z1.d}, p0, [x1, #1, MUL VL]
st1d {z2.d}, p0, [x1, x8, lsl #3]
add x1,x1,x6
st1d {z3.d}, p0, [x1, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
mov x1,x3
ld1rd {z16.d}, p0/z, [x5]
ld1d {z17.d}, p0/z, [x0]
ld1d {z18.d}, p0/z, [x0, #1, MUL VL]
ld1d {z19.d}, p0/z, [x0, x8, lsl #3]
add x0,x0,x6
ld1d {z20.d}, p0/z, [x0, #1, MUL VL]
fmla z0.d,p0/m,z17.d,z16.d
fmla z1.d,p0/m,z18.d,z16.d
fmla z2.d,p0/m,z19.d,z16.d
fmla z3.d,p0/m,z20.d,z16.d
st1d {z0.d}, p0, [x1]
ld1d {z0.d}, p0/z, [x0, x8, lsl #3]
st1d {z1.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6
ld1d {z1.d}, p0/z, [x0, #1, MUL VL]
fmla z4.d,p0/m,z0.d,z16.d
st1d {z2.d}, p0, [x1, x8, lsl #3]
ld1d {z0.d}, p0/z, [x0, x8, lsl #3]
fmla z5.d,p0/m,z1.d,z16.d
add x1,x1,x6
st1d {z3.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6
ld1d {z1.d}, p0/z, [x0, #1, MUL VL]
fmla z6.d,p0/m,z0.d,z16.d
st1d {z4.d}, p0, [x1, x8, lsl #3]
add x1,x1,x6
fmla z7.d,p0/m,z1.d,z16.d
st1d {z5.d}, p0, [x1, #1, MUL VL]
st1d {z6.d}, p0, [x1, x8, lsl #3]
add x1,x1,x6
st1d {z7.d}, p0, [x1, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
mov x1,x3
ld1rd {z16.d}, p0/z, [x5]
ld1d {z17.d}, p0/z, [x0]
ld1d {z18.d}, p0/z, [x0, #1, MUL VL]
ld1d {z19.d}, p0/z, [x0, x8, lsl #3]
ld1rd {z20.d}, p0/z, [x4]
fmul z17.d,z17.d,z16.d
add x0,x0,x6
ld1d {z21.d}, p0/z, [x0, #1, MUL VL]
fmul z18.d,z18.d,z16.d
fmul z19.d,z19.d,z16.d
fmla z17.d,p0/m,z0.d,z20.d
fmul z21.d,z21.d,z16.d
fmla z18.d,p0/m,z1.d,z20.d
fmla z19.d,p0/m,z2.d,z20.d
st1d {z17.d}, p0, [x1]
ld1d {z0.d}, p0/z, [x0, x8, lsl #3]
fmla z21.d,p0/m,z3.d,z20.d
st1d {z18.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6
fmul z0.d,z0.d,z16.d
st1d {z19.d}, p0, [x1, x8, lsl #3]
ld1d {z1.d}, p0/z, [x0, #1, MUL VL]
add x1,x1,x6
ld1d {z2.d}, p0/z, [x0, x8, lsl #3]
fmla z0.d,p0/m,z4.d,z20.d
fmul z1.d,z1.d,z16.d
st1d {z21.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6
fmul z2.d,z2.d,z16.d
fmla z1.d,p0/m,z5.d,z20.d
st1d {z0.d}, p0, [x1, x8, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fmla z2.d,p0/m,z6.d,z20.d
add x1,x1,x6
st1d {z1.d}, p0, [x1, #1, MUL VL]
fmul z0.d,z0.d,z16.d
st1d {z2.d}, p0, [x1, x8, lsl #3]
add x1,x1,x6
fmla z0.d,p0/m,z7.d,z20.d
st1d {z0.d}, p0, [x1, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case6:
mov x0,x3
index z16.d,#0,x7
st1d {z0.d}, p0, [x0, z16.d]
add x0,x0,x10
st1d {z1.d}, p0, [x0, z16.d]
sub x0,x0,x10
add x0,x0,x6
st1d {z2.d}, p0, [x0, z16.d]
add x0,x0,x10
st1d {z3.d}, p0, [x0, z16.d]
sub x0,x0,x10
add x0,x0,x6
st1d {z4.d}, p0, [x0, z16.d]
add x0,x0,x10
st1d {z5.d}, p0, [x0, z16.d]
sub x0,x0,x10
add x0,x0,x6
st1d {z6.d}, p0, [x0, z16.d]
add x0,x0,x10
st1d {z7.d}, p0, [x0, z16.d]
b .ukr0_cases_end
.ukr0_case7:
mov x0,x3
index z16.d,#0,x7
ld1rd {z17.d}, p0/z, [x4]
fmul z18.d,z0.d,z17.d
fmul z0.d,z1.d,z17.d
fmul z1.d,z2.d,z17.d
fmul z2.d,z3.d,z17.d
st1d {z18.d}, p0, [x0, z16.d]
add x0,x0,x10
st1d {z0.d}, p0, [x0, z16.d]
sub x0,x0,x10
add x0,x0,x6
st1d {z1.d}, p0, [x0, z16.d]
add x0,x0,x10
fmul z0.d,z4.d,z17.d
st1d {z2.d}, p0, [x0, z16.d]
sub x0,x0,x10
fmul z1.d,z5.d,z17.d
add x0,x0,x6
st1d {z0.d}, p0, [x0, z16.d]
add x0,x0,x10
fmul z0.d,z6.d,z17.d
st1d {z1.d}, p0, [x0, z16.d]
sub x0,x0,x10
fmul z1.d,z7.d,z17.d
add x0,x0,x6
st1d {z0.d}, p0, [x0, z16.d]
add x0,x0,x10
st1d {z1.d}, p0, [x0, z16.d]
b .ukr0_cases_end
.ukr0_case8:
mov x0,x3
index z16.d,#0,x7
ld1d {z17.d}, p0/z, [x0, z16.d]
add x0,x0,x10
ld1d {z18.d}, p0/z, [x0, z16.d]
sub x0,x0,x10
fadd z17.d,z0.d,z17.d
add x0,x0,x6
fadd z18.d,z1.d,z18.d
ld1d {z0.d}, p0/z, [x0, z16.d]
st1d {z17.d}, p0, [x3, z16.d]
add x3,x3,x10
st1d {z18.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z1.d}, p0/z, [x0, z16.d]
fadd z0.d,z2.d,z0.d
sub x0,x0,x10
add x0,x0,x6
fadd z1.d,z3.d,z1.d
st1d {z0.d}, p0, [x3, z16.d]
add x3,x3,x10
ld1d {z0.d}, p0/z, [x0, z16.d]
st1d {z1.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z1.d}, p0/z, [x0, z16.d]
fadd z0.d,z4.d,z0.d
sub x0,x0,x10
add x0,x0,x6
fadd z1.d,z5.d,z1.d
st1d {z0.d}, p0, [x3, z16.d]
add x3,x3,x10
ld1d {z0.d}, p0/z, [x0, z16.d]
st1d {z1.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z1.d}, p0/z, [x0, z16.d]
fadd z0.d,z6.d,z0.d
fadd z1.d,z7.d,z1.d
st1d {z0.d}, p0, [x3, z16.d]
add x3,x3,x10
st1d {z1.d}, p0, [x3, z16.d]
b .ukr0_cases_end
.ukr0_case9:
mov x0,x3
index z16.d,#0,x7
ld1d {z17.d}, p0/z, [x0, z16.d]
ld1rd {z18.d}, p0/z, [x4]
add x0,x0,x10
ld1d {z19.d}, p0/z, [x0, z16.d]
sub x0,x0,x10
fmla z17.d,p0/m,z0.d,z18.d
add x0,x0,x6
fmla z19.d,p0/m,z1.d,z18.d
ld1d {z0.d}, p0/z, [x0, z16.d]
st1d {z17.d}, p0, [x3, z16.d]
add x3,x3,x10
st1d {z19.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z1.d}, p0/z, [x0, z16.d]
fmla z0.d,p0/m,z2.d,z18.d
sub x0,x0,x10
add x0,x0,x6
fmla z1.d,p0/m,z3.d,z18.d
st1d {z0.d}, p0, [x3, z16.d]
add x3,x3,x10
ld1d {z0.d}, p0/z, [x0, z16.d]
st1d {z1.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z1.d}, p0/z, [x0, z16.d]
fmla z0.d,p0/m,z4.d,z18.d
sub x0,x0,x10
add x0,x0,x6
fmla z1.d,p0/m,z5.d,z18.d
st1d {z0.d}, p0, [x3, z16.d]
add x3,x3,x10
ld1d {z0.d}, p0/z, [x0, z16.d]
st1d {z1.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z1.d}, p0/z, [x0, z16.d]
fmla z0.d,p0/m,z6.d,z18.d
fmla z1.d,p0/m,z7.d,z18.d
st1d {z0.d}, p0, [x3, z16.d]
add x3,x3,x10
st1d {z1.d}, p0, [x3, z16.d]
b .ukr0_cases_end
.ukr0_case10:
mov x0,x3
index z16.d,#0,x7
ld1d {z17.d}, p0/z, [x0, z16.d]
ld1rd {z18.d}, p0/z, [x5]
add x0,x0,x10
ld1d {z19.d}, p0/z, [x0, z16.d]
sub x0,x0,x10
fmla z0.d,p0/m,z17.d,z18.d
add x0,x0,x6
fmla z1.d,p0/m,z19.d,z18.d
ld1d {z17.d}, p0/z, [x0, z16.d]
st1d {z0.d}, p0, [x3, z16.d]
add x3,x3,x10
st1d {z1.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z0.d}, p0/z, [x0, z16.d]
fmla z2.d,p0/m,z17.d,z18.d
sub x0,x0,x10
add x0,x0,x6
fmla z3.d,p0/m,z0.d,z18.d
st1d {z2.d}, p0, [x3, z16.d]
add x3,x3,x10
ld1d {z0.d}, p0/z, [x0, z16.d]
st1d {z3.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z1.d}, p0/z, [x0, z16.d]
fmla z4.d,p0/m,z0.d,z18.d
sub x0,x0,x10
add x0,x0,x6
fmla z5.d,p0/m,z1.d,z18.d
st1d {z4.d}, p0, [x3, z16.d]
add x3,x3,x10
ld1d {z0.d}, p0/z, [x0, z16.d]
st1d {z5.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z1.d}, p0/z, [x0, z16.d]
fmla z6.d,p0/m,z0.d,z18.d
fmla z7.d,p0/m,z1.d,z18.d
st1d {z6.d}, p0, [x3, z16.d]
add x3,x3,x10
st1d {z7.d}, p0, [x3, z16.d]
b .ukr0_cases_end
.ukr0_case11:
mov x0,x3
index z16.d,#0,x7
ld1d {z17.d}, p0/z, [x0, z16.d]
ld1rd {z18.d}, p0/z, [x5]
add x0,x0,x10
ld1d {z19.d}, p0/z, [x0, z16.d]
ld1rd {z20.d}, p0/z, [x4]
fmul z17.d,z17.d,z18.d
sub x0,x0,x10
fmul z19.d,z19.d,z18.d
add x0,x0,x6
fmla z17.d,p0/m,z0.d,z20.d
ld1d {z0.d}, p0/z, [x0, z16.d]
fmla z19.d,p0/m,z1.d,z20.d
st1d {z17.d}, p0, [x3, z16.d]
add x3,x3,x10
fmul z0.d,z0.d,z18.d
st1d {z19.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z1.d}, p0/z, [x0, z16.d]
fmla z0.d,p0/m,z2.d,z20.d
sub x0,x0,x10
add x0,x0,x6
fmul z1.d,z1.d,z18.d
st1d {z0.d}, p0, [x3, z16.d]
add x3,x3,x10
ld1d {z0.d}, p0/z, [x0, z16.d]
fmla z1.d,p0/m,z3.d,z20.d
fmul z0.d,z0.d,z18.d
st1d {z1.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z1.d}, p0/z, [x0, z16.d]
fmla z0.d,p0/m,z4.d,z20.d
sub x0,x0,x10
add x0,x0,x6
fmul z1.d,z1.d,z18.d
st1d {z0.d}, p0, [x3, z16.d]
add x3,x3,x10
ld1d {z0.d}, p0/z, [x0, z16.d]
fmla z1.d,p0/m,z5.d,z20.d
fmul z0.d,z0.d,z18.d
st1d {z1.d}, p0, [x3, z16.d]
mov x3,x0
add x0,x0,x10
ld1d {z1.d}, p0/z, [x0, z16.d]
fmla z0.d,p0/m,z6.d,z20.d
fmul z1.d,z1.d,z18.d
st1d {z0.d}, p0, [x3, z16.d]
add x3,x3,x10
fmla z1.d,p0/m,z7.d,z20.d
st1d {z1.d}, p0, [x3, z16.d]
.ukr0_cases_end:
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
.size bli_dgemm_ukrgen_sve_vn_4x2v_asm, .-bli_dgemm_ukrgen_sve_vn_4x2v_asm
.section .note.GNU-stack,"",%progbits
