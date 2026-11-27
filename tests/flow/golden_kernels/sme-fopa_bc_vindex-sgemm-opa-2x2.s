.text
.global bli_sgemm_ukrgen_sme_opa_2vx2v_asm
.type bli_sgemm_ukrgen_sme_opa_2vx2v_asm, %function
bli_sgemm_ukrgen_sme_opa_2vx2v_asm:
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
zero {za1.s}
zero {za2.s}
zero {za3.s}
cbz x0,.ukr7_done
ld1w {z0.s}, p0/z, [x1]
ld1w {z1.s}, p0/z, [x1, #1, MUL VL]
ld1w {z2.s}, p0/z, [x2]
ld1w {z3.s}, p0/z, [x2, #1, MUL VL]
incb x1, ALL, MUL #2
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
fmopa za0.s,p0/m,p0/m,z0.s,z2.s
fmopa za1.s,p0/m,p0/m,z0.s,z3.s
fmopa za2.s,p0/m,p0/m,z1.s,z2.s
fmopa za3.s,p0/m,p0/m,z1.s,z3.s
ld1w {z4.s}, p0/z, [x1]
ld1w {z5.s}, p0/z, [x2]
ld1w {z6.s}, p0/z, [x2, #1, MUL VL]
ld1w {z7.s}, p0/z, [x1, #1, MUL VL]
fmopa za0.s,p0/m,p0/m,z4.s,z5.s
fmopa za1.s,p0/m,p0/m,z4.s,z6.s
fmopa za2.s,p0/m,p0/m,z7.s,z5.s
fmopa za3.s,p0/m,p0/m,z7.s,z6.s
ld1w {z16.s}, p0/z, [x1, #2, MUL VL]
ld1w {z17.s}, p0/z, [x2, #2, MUL VL]
ld1w {z18.s}, p0/z, [x2, #3, MUL VL]
ld1w {z19.s}, p0/z, [x1, #3, MUL VL]
fmopa za0.s,p0/m,p0/m,z16.s,z17.s
fmopa za1.s,p0/m,p0/m,z16.s,z18.s
fmopa za2.s,p0/m,p0/m,z19.s,z17.s
fmopa za3.s,p0/m,p0/m,z19.s,z18.s
ld1w {z20.s}, p0/z, [x1, #4, MUL VL]
ld1w {z21.s}, p0/z, [x2, #4, MUL VL]
ld1w {z22.s}, p0/z, [x2, #5, MUL VL]
ld1w {z23.s}, p0/z, [x1, #5, MUL VL]
ld1w {z0.s}, p0/z, [x1, #6, MUL VL]
ld1w {z1.s}, p0/z, [x1, #7, MUL VL]
ld1w {z2.s}, p0/z, [x2, #6, MUL VL]
ld1w {z3.s}, p0/z, [x2, #7, MUL VL]
fmopa za0.s,p0/m,p0/m,z20.s,z21.s
fmopa za1.s,p0/m,p0/m,z20.s,z22.s
fmopa za2.s,p0/m,p0/m,z23.s,z21.s
fmopa za3.s,p0/m,p0/m,z23.s,z22.s
incb x1, ALL, MUL #8
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
fmopa za0.s,p0/m,p0/m,z0.s,z2.s
fmopa za1.s,p0/m,p0/m,z0.s,z3.s
fmopa za2.s,p0/m,p0/m,z1.s,z2.s
fmopa za3.s,p0/m,p0/m,z1.s,z3.s
ld1w {z4.s}, p0/z, [x1]
ld1w {z5.s}, p0/z, [x2]
ld1w {z6.s}, p0/z, [x2, #1, MUL VL]
ld1w {z7.s}, p0/z, [x1, #1, MUL VL]
fmopa za0.s,p0/m,p0/m,z4.s,z5.s
fmopa za1.s,p0/m,p0/m,z4.s,z6.s
fmopa za2.s,p0/m,p0/m,z7.s,z5.s
fmopa za3.s,p0/m,p0/m,z7.s,z6.s
ld1w {z16.s}, p0/z, [x1, #2, MUL VL]
ld1w {z17.s}, p0/z, [x2, #2, MUL VL]
ld1w {z18.s}, p0/z, [x2, #3, MUL VL]
ld1w {z19.s}, p0/z, [x1, #3, MUL VL]
fmopa za0.s,p0/m,p0/m,z16.s,z17.s
fmopa za1.s,p0/m,p0/m,z16.s,z18.s
fmopa za2.s,p0/m,p0/m,z19.s,z17.s
fmopa za3.s,p0/m,p0/m,z19.s,z18.s
ld1w {z20.s}, p0/z, [x1, #4, MUL VL]
ld1w {z21.s}, p0/z, [x2, #4, MUL VL]
ld1w {z22.s}, p0/z, [x2, #5, MUL VL]
ld1w {z23.s}, p0/z, [x1, #5, MUL VL]
fmopa za0.s,p0/m,p0/m,z20.s,z21.s
fmopa za1.s,p0/m,p0/m,z20.s,z22.s
fmopa za2.s,p0/m,p0/m,z23.s,z21.s
fmopa za3.s,p0/m,p0/m,z23.s,z22.s
incb x1, ALL, MUL #6
incb x2, ALL, MUL #6
.ukr7_done:
cbz x9,.ukr7_taildone
.ukr7_tail:
add x9,x9,#-1
ld1w {z0.s}, p0/z, [x1]
ld1w {z2.s}, p0/z, [x2]
ld1w {z3.s}, p0/z, [x2, #1, MUL VL]
ld1w {z1.s}, p0/z, [x1, #1, MUL VL]
fmopa za0.s,p0/m,p0/m,z0.s,z2.s
fmopa za1.s,p0/m,p0/m,z0.s,z3.s
fmopa za2.s,p0/m,p0/m,z1.s,z2.s
fmopa za3.s,p0/m,p0/m,z1.s,z3.s
incb x1, ALL, MUL #2
incb x2, ALL, MUL #2
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
mov x1,x7
mov x12,#0
.ukr1_slices:
add x1,x1,#-4
st1w {za0v.s[w12, 0]}, p0, [x0]
add x0,x0,x8
st1w {za1v.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
sub x0,x0,x8
st1w {za2v.s[w12, 0]}, p0, [x0]
add x0,x0,x8
st1w {za3v.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0v.s[w12, 1]}, p0, [x0]
add x0,x0,x8
st1w {za1v.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
sub x0,x0,x8
st1w {za2v.s[w12, 1]}, p0, [x0]
add x0,x0,x8
st1w {za3v.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0v.s[w12, 2]}, p0, [x0]
add x0,x0,x8
st1w {za1v.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
sub x0,x0,x8
st1w {za2v.s[w12, 2]}, p0, [x0]
add x0,x0,x8
st1w {za3v.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0v.s[w12, 3]}, p0, [x0]
add x0,x0,x8
st1w {za1v.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
sub x0,x0,x8
st1w {za2v.s[w12, 3]}, p0, [x0]
add x0,x0,x8
st1w {za3v.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr1_slices
sub x0,x0,x8
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z0.s}, p0/z, [x4]
.ukr2_slices:
add x1,x1,#-4
mova z1.s,p0/m,za0v.s[w12,0]
fmul z2.s,z1.s,z0.s
st1w {z2.s}, p0, [x0]
mova z3.s,p0/m,za1v.s[w12,0]
fmul z4.s,z3.s,z0.s
add x0,x0,x8
st1w {z4.s}, p0, [x0]
mova z5.s,p0/m,za2v.s[w12,0]
fmul z6.s,z5.s,z0.s
sub x0,x0,x8
st1w {z6.s}, p0, [x0, #1, MUL VL]
mova z7.s,p0/m,za3v.s[w12,0]
fmul z16.s,z7.s,z0.s
add x0,x0,x8
st1w {z16.s}, p0, [x0, #1, MUL VL]
mova z17.s,p0/m,za0v.s[w12,1]
sub x0,x0,x8
fmul z18.s,z17.s,z0.s
add x0,x0,x6
st1w {z18.s}, p0, [x0]
mova z19.s,p0/m,za1v.s[w12,1]
fmul z20.s,z19.s,z0.s
add x0,x0,x8
st1w {z20.s}, p0, [x0]
mova z21.s,p0/m,za2v.s[w12,1]
fmul z22.s,z21.s,z0.s
sub x0,x0,x8
st1w {z22.s}, p0, [x0, #1, MUL VL]
mova z23.s,p0/m,za3v.s[w12,1]
fmul z24.s,z23.s,z0.s
add x0,x0,x8
st1w {z24.s}, p0, [x0, #1, MUL VL]
mova z25.s,p0/m,za0v.s[w12,2]
sub x0,x0,x8
fmul z26.s,z25.s,z0.s
add x0,x0,x6
st1w {z26.s}, p0, [x0]
mova z27.s,p0/m,za1v.s[w12,2]
fmul z28.s,z27.s,z0.s
add x0,x0,x8
st1w {z28.s}, p0, [x0]
mova z29.s,p0/m,za2v.s[w12,2]
fmul z30.s,z29.s,z0.s
sub x0,x0,x8
st1w {z30.s}, p0, [x0, #1, MUL VL]
mova z31.s,p0/m,za3v.s[w12,2]
fmul z8.s,z31.s,z0.s
add x0,x0,x8
st1w {z8.s}, p0, [x0, #1, MUL VL]
mova z9.s,p0/m,za0v.s[w12,3]
sub x0,x0,x8
fmul z10.s,z9.s,z0.s
add x0,x0,x6
st1w {z10.s}, p0, [x0]
mova z11.s,p0/m,za1v.s[w12,3]
fmul z12.s,z11.s,z0.s
add x0,x0,x8
st1w {z12.s}, p0, [x0]
mova z13.s,p0/m,za2v.s[w12,3]
fmul z14.s,z13.s,z0.s
sub x0,x0,x8
st1w {z14.s}, p0, [x0, #1, MUL VL]
mova z15.s,p0/m,za3v.s[w12,3]
fmul z2.s,z15.s,z0.s
add x0,x0,x8
st1w {z2.s}, p0, [x0, #1, MUL VL]
sub x0,x0,x8
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr2_slices
sub x0,x0,x8
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
.ukr3_slices:
add x1,x1,#-4
mova z0.s,p0/m,za0v.s[w12,0]
ld1w {z1.s}, p0/z, [x0]
fadd z1.s,z0.s,z1.s
add x0,x0,x8
mova z2.s,p0/m,za1v.s[w12,0]
ld1w {z3.s}, p0/z, [x0]
st1w {z1.s}, p0, [x3]
fadd z3.s,z2.s,z3.s
sub x0,x0,x8
add x3,x3,x8
mova z4.s,p0/m,za2v.s[w12,0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
st1w {z3.s}, p0, [x3]
fadd z5.s,z4.s,z5.s
add x0,x0,x8
sub x3,x3,x8
mova z6.s,p0/m,za3v.s[w12,0]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
st1w {z5.s}, p0, [x3, #1, MUL VL]
fadd z7.s,z6.s,z7.s
add x3,x3,x8
sub x0,x0,x8
st1w {z7.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z16.s,p0/m,za0v.s[w12,1]
ld1w {z17.s}, p0/z, [x0]
sub x3,x3,x8
fadd z17.s,z16.s,z17.s
add x0,x0,x8
add x3,x3,x6
mova z18.s,p0/m,za1v.s[w12,1]
ld1w {z19.s}, p0/z, [x0]
st1w {z17.s}, p0, [x3]
fadd z19.s,z18.s,z19.s
sub x0,x0,x8
add x3,x3,x8
mova z20.s,p0/m,za2v.s[w12,1]
ld1w {z21.s}, p0/z, [x0, #1, MUL VL]
st1w {z19.s}, p0, [x3]
fadd z21.s,z20.s,z21.s
add x0,x0,x8
sub x3,x3,x8
mova z22.s,p0/m,za3v.s[w12,1]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
st1w {z21.s}, p0, [x3, #1, MUL VL]
fadd z23.s,z22.s,z23.s
add x3,x3,x8
sub x0,x0,x8
st1w {z23.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z24.s,p0/m,za0v.s[w12,2]
ld1w {z25.s}, p0/z, [x0]
sub x3,x3,x8
fadd z25.s,z24.s,z25.s
add x0,x0,x8
add x3,x3,x6
mova z26.s,p0/m,za1v.s[w12,2]
ld1w {z27.s}, p0/z, [x0]
st1w {z25.s}, p0, [x3]
fadd z27.s,z26.s,z27.s
sub x0,x0,x8
add x3,x3,x8
mova z28.s,p0/m,za2v.s[w12,2]
ld1w {z29.s}, p0/z, [x0, #1, MUL VL]
st1w {z27.s}, p0, [x3]
fadd z29.s,z28.s,z29.s
add x0,x0,x8
sub x3,x3,x8
mova z30.s,p0/m,za3v.s[w12,2]
ld1w {z31.s}, p0/z, [x0, #1, MUL VL]
st1w {z29.s}, p0, [x3, #1, MUL VL]
fadd z31.s,z30.s,z31.s
add x3,x3,x8
sub x0,x0,x8
st1w {z31.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z8.s,p0/m,za0v.s[w12,3]
ld1w {z9.s}, p0/z, [x0]
sub x3,x3,x8
fadd z9.s,z8.s,z9.s
add x0,x0,x8
add x3,x3,x6
mova z10.s,p0/m,za1v.s[w12,3]
ld1w {z11.s}, p0/z, [x0]
st1w {z9.s}, p0, [x3]
fadd z11.s,z10.s,z11.s
sub x0,x0,x8
add x3,x3,x8
mova z12.s,p0/m,za2v.s[w12,3]
ld1w {z13.s}, p0/z, [x0, #1, MUL VL]
st1w {z11.s}, p0, [x3]
fadd z13.s,z12.s,z13.s
add x0,x0,x8
sub x3,x3,x8
mova z14.s,p0/m,za3v.s[w12,3]
ld1w {z15.s}, p0/z, [x0, #1, MUL VL]
st1w {z13.s}, p0, [x3, #1, MUL VL]
fadd z15.s,z14.s,z15.s
add x3,x3,x8
st1w {z15.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr3_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z0.s}, p0/z, [x4]
.ukr4_slices:
add x1,x1,#-4
mova z1.s,p0/m,za0v.s[w12,0]
ld1w {z2.s}, p0/z, [x0]
fmla z2.s,p0/m,z1.s,z0.s
add x0,x0,x8
st1w {z2.s}, p0, [x3]
mova z3.s,p0/m,za1v.s[w12,0]
ld1w {z4.s}, p0/z, [x0]
fmla z4.s,p0/m,z3.s,z0.s
add x3,x3,x8
sub x0,x0,x8
st1w {z4.s}, p0, [x3]
mova z5.s,p0/m,za2v.s[w12,0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
fmla z6.s,p0/m,z5.s,z0.s
sub x3,x3,x8
add x0,x0,x8
st1w {z6.s}, p0, [x3, #1, MUL VL]
mova z7.s,p0/m,za3v.s[w12,0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
fmla z16.s,p0/m,z7.s,z0.s
add x3,x3,x8
sub x0,x0,x8
st1w {z16.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z17.s,p0/m,za0v.s[w12,1]
ld1w {z18.s}, p0/z, [x0]
sub x3,x3,x8
fmla z18.s,p0/m,z17.s,z0.s
add x3,x3,x6
add x0,x0,x8
st1w {z18.s}, p0, [x3]
mova z19.s,p0/m,za1v.s[w12,1]
ld1w {z20.s}, p0/z, [x0]
fmla z20.s,p0/m,z19.s,z0.s
add x3,x3,x8
sub x0,x0,x8
st1w {z20.s}, p0, [x3]
mova z21.s,p0/m,za2v.s[w12,1]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
fmla z22.s,p0/m,z21.s,z0.s
sub x3,x3,x8
add x0,x0,x8
st1w {z22.s}, p0, [x3, #1, MUL VL]
mova z23.s,p0/m,za3v.s[w12,1]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
fmla z24.s,p0/m,z23.s,z0.s
add x3,x3,x8
sub x0,x0,x8
st1w {z24.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z25.s,p0/m,za0v.s[w12,2]
ld1w {z26.s}, p0/z, [x0]
sub x3,x3,x8
fmla z26.s,p0/m,z25.s,z0.s
add x3,x3,x6
add x0,x0,x8
st1w {z26.s}, p0, [x3]
mova z27.s,p0/m,za1v.s[w12,2]
ld1w {z28.s}, p0/z, [x0]
fmla z28.s,p0/m,z27.s,z0.s
add x3,x3,x8
sub x0,x0,x8
st1w {z28.s}, p0, [x3]
mova z29.s,p0/m,za2v.s[w12,2]
ld1w {z30.s}, p0/z, [x0, #1, MUL VL]
fmla z30.s,p0/m,z29.s,z0.s
sub x3,x3,x8
add x0,x0,x8
st1w {z30.s}, p0, [x3, #1, MUL VL]
mova z31.s,p0/m,za3v.s[w12,2]
ld1w {z8.s}, p0/z, [x0, #1, MUL VL]
fmla z8.s,p0/m,z31.s,z0.s
add x3,x3,x8
sub x0,x0,x8
st1w {z8.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z9.s,p0/m,za0v.s[w12,3]
ld1w {z10.s}, p0/z, [x0]
sub x3,x3,x8
fmla z10.s,p0/m,z9.s,z0.s
add x3,x3,x6
add x0,x0,x8
st1w {z10.s}, p0, [x3]
mova z11.s,p0/m,za1v.s[w12,3]
ld1w {z12.s}, p0/z, [x0]
fmla z12.s,p0/m,z11.s,z0.s
add x3,x3,x8
sub x0,x0,x8
st1w {z12.s}, p0, [x3]
mova z13.s,p0/m,za2v.s[w12,3]
ld1w {z14.s}, p0/z, [x0, #1, MUL VL]
fmla z14.s,p0/m,z13.s,z0.s
sub x3,x3,x8
add x0,x0,x8
st1w {z14.s}, p0, [x3, #1, MUL VL]
mova z15.s,p0/m,za3v.s[w12,3]
ld1w {z2.s}, p0/z, [x0, #1, MUL VL]
fmla z2.s,p0/m,z15.s,z0.s
add x3,x3,x8
st1w {z2.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr4_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z0.s}, p0/z, [x5]
.ukr5_slices:
add x1,x1,#-4
mova z1.s,p0/m,za0v.s[w12,0]
ld1w {z2.s}, p0/z, [x0]
fmla z1.s,p0/m,z2.s,z0.s
add x0,x0,x8
st1w {z1.s}, p0, [x3]
mova z3.s,p0/m,za1v.s[w12,0]
ld1w {z4.s}, p0/z, [x0]
fmla z3.s,p0/m,z4.s,z0.s
add x3,x3,x8
sub x0,x0,x8
st1w {z3.s}, p0, [x3]
mova z5.s,p0/m,za2v.s[w12,0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
fmla z5.s,p0/m,z6.s,z0.s
sub x3,x3,x8
add x0,x0,x8
st1w {z5.s}, p0, [x3, #1, MUL VL]
mova z7.s,p0/m,za3v.s[w12,0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
fmla z7.s,p0/m,z16.s,z0.s
add x3,x3,x8
sub x0,x0,x8
st1w {z7.s}, p0, [x3, #1, MUL VL]
mova za0v.s[w12,0],p0/m,z1.s
add x0,x0,x6
mova z17.s,p0/m,za0v.s[w12,1]
ld1w {z18.s}, p0/z, [x0]
sub x3,x3,x8
fmla z17.s,p0/m,z18.s,z0.s
add x3,x3,x6
mova za1v.s[w12,0],p0/m,z3.s
add x0,x0,x8
st1w {z17.s}, p0, [x3]
mova z19.s,p0/m,za1v.s[w12,1]
ld1w {z20.s}, p0/z, [x0]
fmla z19.s,p0/m,z20.s,z0.s
add x3,x3,x8
mova za2v.s[w12,0],p0/m,z5.s
sub x0,x0,x8
st1w {z19.s}, p0, [x3]
mova z21.s,p0/m,za2v.s[w12,1]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
fmla z21.s,p0/m,z22.s,z0.s
sub x3,x3,x8
mova za3v.s[w12,0],p0/m,z7.s
add x0,x0,x8
st1w {z21.s}, p0, [x3, #1, MUL VL]
mova z23.s,p0/m,za3v.s[w12,1]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
fmla z23.s,p0/m,z24.s,z0.s
add x3,x3,x8
sub x0,x0,x8
st1w {z23.s}, p0, [x3, #1, MUL VL]
mova za0v.s[w12,1],p0/m,z17.s
add x0,x0,x6
mova z25.s,p0/m,za0v.s[w12,2]
ld1w {z26.s}, p0/z, [x0]
sub x3,x3,x8
fmla z25.s,p0/m,z26.s,z0.s
add x3,x3,x6
mova za1v.s[w12,1],p0/m,z19.s
add x0,x0,x8
st1w {z25.s}, p0, [x3]
mova z27.s,p0/m,za1v.s[w12,2]
ld1w {z28.s}, p0/z, [x0]
fmla z27.s,p0/m,z28.s,z0.s
add x3,x3,x8
mova za2v.s[w12,1],p0/m,z21.s
sub x0,x0,x8
st1w {z27.s}, p0, [x3]
mova z29.s,p0/m,za2v.s[w12,2]
ld1w {z30.s}, p0/z, [x0, #1, MUL VL]
fmla z29.s,p0/m,z30.s,z0.s
sub x3,x3,x8
mova za3v.s[w12,1],p0/m,z23.s
add x0,x0,x8
st1w {z29.s}, p0, [x3, #1, MUL VL]
mova z31.s,p0/m,za3v.s[w12,2]
ld1w {z8.s}, p0/z, [x0, #1, MUL VL]
fmla z31.s,p0/m,z8.s,z0.s
add x3,x3,x8
sub x0,x0,x8
st1w {z31.s}, p0, [x3, #1, MUL VL]
mova za0v.s[w12,2],p0/m,z25.s
add x0,x0,x6
mova z9.s,p0/m,za0v.s[w12,3]
ld1w {z10.s}, p0/z, [x0]
sub x3,x3,x8
fmla z9.s,p0/m,z10.s,z0.s
mova za1v.s[w12,2],p0/m,z27.s
add x0,x0,x8
add x3,x3,x6
mova z11.s,p0/m,za1v.s[w12,3]
ld1w {z12.s}, p0/z, [x0]
st1w {z9.s}, p0, [x3]
fmla z11.s,p0/m,z12.s,z0.s
mova za2v.s[w12,2],p0/m,z29.s
sub x0,x0,x8
add x3,x3,x8
mova z13.s,p0/m,za2v.s[w12,3]
ld1w {z14.s}, p0/z, [x0, #1, MUL VL]
st1w {z11.s}, p0, [x3]
fmla z13.s,p0/m,z14.s,z0.s
mova za3v.s[w12,2],p0/m,z31.s
add x0,x0,x8
sub x3,x3,x8
mova z15.s,p0/m,za3v.s[w12,3]
ld1w {z2.s}, p0/z, [x0, #1, MUL VL]
st1w {z13.s}, p0, [x3, #1, MUL VL]
fmla z15.s,p0/m,z2.s,z0.s
add x3,x3,x8
st1w {z15.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
mova za0v.s[w12,3],p0/m,z9.s
mova za1v.s[w12,3],p0/m,z11.s
mova za2v.s[w12,3],p0/m,z13.s
mova za3v.s[w12,3],p0/m,z15.s
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr5_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z0.s}, p0/z, [x5]
ld1rw {z1.s}, p0/z, [x4]
.ukr6_slices:
add x1,x1,#-4
ld1w {z2.s}, p0/z, [x0]
fmul z2.s,z2.s,z0.s
mova z3.s,p0/m,za0v.s[w12,0]
add x0,x0,x8
fmla z2.s,p0/m,z3.s,z1.s
ld1w {z4.s}, p0/z, [x0]
st1w {z2.s}, p0, [x3]
fmul z4.s,z4.s,z0.s
mova z5.s,p0/m,za1v.s[w12,0]
sub x0,x0,x8
fmla z4.s,p0/m,z5.s,z1.s
add x3,x3,x8
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
st1w {z4.s}, p0, [x3]
fmul z6.s,z6.s,z0.s
mova z7.s,p0/m,za2v.s[w12,0]
add x0,x0,x8
fmla z6.s,p0/m,z7.s,z1.s
sub x3,x3,x8
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
st1w {z6.s}, p0, [x3, #1, MUL VL]
fmul z16.s,z16.s,z0.s
mova z17.s,p0/m,za3v.s[w12,0]
sub x0,x0,x8
fmla z16.s,p0/m,z17.s,z1.s
add x3,x3,x8
add x0,x0,x6
st1w {z16.s}, p0, [x3, #1, MUL VL]
ld1w {z18.s}, p0/z, [x0]
fmul z18.s,z18.s,z0.s
mova z19.s,p0/m,za0v.s[w12,1]
sub x3,x3,x8
add x0,x0,x8
fmla z18.s,p0/m,z19.s,z1.s
add x3,x3,x6
ld1w {z20.s}, p0/z, [x0]
st1w {z18.s}, p0, [x3]
fmul z20.s,z20.s,z0.s
mova z21.s,p0/m,za1v.s[w12,1]
sub x0,x0,x8
fmla z20.s,p0/m,z21.s,z1.s
add x3,x3,x8
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
st1w {z20.s}, p0, [x3]
fmul z22.s,z22.s,z0.s
mova z23.s,p0/m,za2v.s[w12,1]
add x0,x0,x8
fmla z22.s,p0/m,z23.s,z1.s
sub x3,x3,x8
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
st1w {z22.s}, p0, [x3, #1, MUL VL]
fmul z24.s,z24.s,z0.s
mova z25.s,p0/m,za3v.s[w12,1]
sub x0,x0,x8
fmla z24.s,p0/m,z25.s,z1.s
add x3,x3,x8
add x0,x0,x6
st1w {z24.s}, p0, [x3, #1, MUL VL]
ld1w {z26.s}, p0/z, [x0]
fmul z26.s,z26.s,z0.s
mova z27.s,p0/m,za0v.s[w12,2]
sub x3,x3,x8
add x0,x0,x8
fmla z26.s,p0/m,z27.s,z1.s
add x3,x3,x6
ld1w {z28.s}, p0/z, [x0]
st1w {z26.s}, p0, [x3]
fmul z28.s,z28.s,z0.s
mova z29.s,p0/m,za1v.s[w12,2]
sub x0,x0,x8
fmla z28.s,p0/m,z29.s,z1.s
add x3,x3,x8
ld1w {z30.s}, p0/z, [x0, #1, MUL VL]
st1w {z28.s}, p0, [x3]
fmul z30.s,z30.s,z0.s
mova z31.s,p0/m,za2v.s[w12,2]
add x0,x0,x8
fmla z30.s,p0/m,z31.s,z1.s
sub x3,x3,x8
ld1w {z8.s}, p0/z, [x0, #1, MUL VL]
st1w {z30.s}, p0, [x3, #1, MUL VL]
fmul z8.s,z8.s,z0.s
mova z9.s,p0/m,za3v.s[w12,2]
sub x0,x0,x8
fmla z8.s,p0/m,z9.s,z1.s
add x3,x3,x8
add x0,x0,x6
st1w {z8.s}, p0, [x3, #1, MUL VL]
ld1w {z10.s}, p0/z, [x0]
fmul z10.s,z10.s,z0.s
mova z11.s,p0/m,za0v.s[w12,3]
sub x3,x3,x8
add x0,x0,x8
fmla z10.s,p0/m,z11.s,z1.s
add x3,x3,x6
ld1w {z12.s}, p0/z, [x0]
st1w {z10.s}, p0, [x3]
fmul z12.s,z12.s,z0.s
mova z13.s,p0/m,za1v.s[w12,3]
sub x0,x0,x8
fmla z12.s,p0/m,z13.s,z1.s
add x3,x3,x8
ld1w {z14.s}, p0/z, [x0, #1, MUL VL]
st1w {z12.s}, p0, [x3]
fmul z14.s,z14.s,z0.s
mova z15.s,p0/m,za2v.s[w12,3]
add x0,x0,x8
fmla z14.s,p0/m,z15.s,z1.s
sub x3,x3,x8
ld1w {z2.s}, p0/z, [x0, #1, MUL VL]
st1w {z14.s}, p0, [x3, #1, MUL VL]
fmul z2.s,z2.s,z0.s
mova z3.s,p0/m,za3v.s[w12,3]
fmla z2.s,p0/m,z3.s,z1.s
add x3,x3,x8
st1w {z2.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
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
.size bli_sgemm_ukrgen_sme_opa_2vx2v_asm, .-bli_sgemm_ukrgen_sme_opa_2vx2v_asm
.section .note.GNU-stack,"",%progbits
