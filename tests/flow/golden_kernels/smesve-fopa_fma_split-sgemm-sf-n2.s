### bli_sgemm_ukrgen_sme_sf_1vx2v_1x2v
.text
.global bli_sgemm_ukrgen_sme_sf_1vx2v_1x2v_asm
.type bli_sgemm_ukrgen_sme_sf_1vx2v_1x2v_asm, %function
bli_sgemm_ukrgen_sme_sf_1vx2v_1x2v_asm:
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
smstart
ptrue p0.s
cntw x7
mul x8,x7,x6
and x9,x0,#3
lsr x0,x0,#2
zero {za0.s}
zero {za1.s}
dup z0.s,#0
dup z1.s,#0
cbz x0,.ukr7_done
add x10,x1,#4
ld1w {z2.s}, p0/z, [x2]
ld1w {z3.s}, p0/z, [x2, #1, MUL VL]
ld1w {z4.s}, p0/z, [x1]
ld1w {z5.s}, p0/z, [x10, #1, MUL VL]
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x10,x1,#8
ld1w {z6.s}, p0/z, [x10, #2, MUL VL]
add x10,x10,#4
ld1w {z7.s}, p0/z, [x10, #3, MUL VL]
add x10,x10,#-12
incb x10, ALL, MUL #1
ld1rw {z16.s}, p0/z, [x10]
add x10,x10,#4
incb x10, ALL, MUL #1
ld1rw {z17.s}, p0/z, [x10]
add x10,x10,#4
incb x10, ALL, MUL #1
ld1rw {z18.s}, p0/z, [x10]
add x10,x10,#4
incb x10, ALL, MUL #1
ld1rw {z19.s}, p0/z, [x10]
add x10,x10,#4
fmopa za0.s,p0/m,p0/m,z4.s,z2.s
fmopa za1.s,p0/m,p0/m,z4.s,z3.s
ld1w {z20.s}, p0/z, [x2]
ld1w {z21.s}, p0/z, [x2, #1, MUL VL]
fmla z0.s,p0/m,z2.s,z16.s
fmla z1.s,p0/m,z3.s,z16.s
decb x10, ALL, MUL #4
fmopa za0.s,p0/m,p0/m,z5.s,z20.s
fmopa za1.s,p0/m,p0/m,z5.s,z21.s
ld1w {z22.s}, p0/z, [x2, #2, MUL VL]
ld1w {z23.s}, p0/z, [x2, #3, MUL VL]
fmla z0.s,p0/m,z20.s,z17.s
fmla z1.s,p0/m,z21.s,z17.s
ld1w {z4.s}, p0/z, [x10, #4, MUL VL]
fmopa za0.s,p0/m,p0/m,z6.s,z22.s
fmopa za1.s,p0/m,p0/m,z6.s,z23.s
ld1w {z24.s}, p0/z, [x2, #4, MUL VL]
ld1w {z25.s}, p0/z, [x2, #5, MUL VL]
fmla z0.s,p0/m,z22.s,z18.s
fmla z1.s,p0/m,z23.s,z18.s
add x10,x10,#4
ld1w {z2.s}, p0/z, [x2, #6, MUL VL]
ld1w {z3.s}, p0/z, [x2, #7, MUL VL]
add x1,x1,#16
fmopa za0.s,p0/m,p0/m,z7.s,z24.s
fmopa za1.s,p0/m,p0/m,z7.s,z25.s
fmla z0.s,p0/m,z24.s,z19.s
fmla z1.s,p0/m,z25.s,z19.s
ld1w {z5.s}, p0/z, [x10, #5, MUL VL]
incb x1, ALL, MUL #4
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x10,x1,#8
ld1w {z6.s}, p0/z, [x10, #2, MUL VL]
add x10,x10,#4
ld1w {z7.s}, p0/z, [x10, #3, MUL VL]
add x10,x10,#-12
incb x10, ALL, MUL #1
ld1rw {z16.s}, p0/z, [x10]
add x10,x10,#4
incb x10, ALL, MUL #1
ld1rw {z17.s}, p0/z, [x10]
add x10,x10,#4
incb x10, ALL, MUL #1
ld1rw {z18.s}, p0/z, [x10]
fmopa za0.s,p0/m,p0/m,z4.s,z2.s
fmopa za1.s,p0/m,p0/m,z4.s,z3.s
ld1w {z20.s}, p0/z, [x2]
ld1w {z21.s}, p0/z, [x2, #1, MUL VL]
fmla z0.s,p0/m,z2.s,z16.s
fmla z1.s,p0/m,z3.s,z16.s
add x10,x10,#4
fmopa za0.s,p0/m,p0/m,z5.s,z20.s
fmopa za1.s,p0/m,p0/m,z5.s,z21.s
ld1w {z22.s}, p0/z, [x2, #2, MUL VL]
ld1w {z23.s}, p0/z, [x2, #3, MUL VL]
fmla z0.s,p0/m,z20.s,z17.s
fmla z1.s,p0/m,z21.s,z17.s
incb x10, ALL, MUL #1
fmopa za0.s,p0/m,p0/m,z6.s,z22.s
fmopa za1.s,p0/m,p0/m,z6.s,z23.s
ld1w {z24.s}, p0/z, [x2, #4, MUL VL]
ld1w {z25.s}, p0/z, [x2, #5, MUL VL]
fmla z0.s,p0/m,z22.s,z18.s
fmla z1.s,p0/m,z23.s,z18.s
ld1rw {z19.s}, p0/z, [x10]
add x1,x1,#16
fmopa za0.s,p0/m,p0/m,z7.s,z24.s
fmopa za1.s,p0/m,p0/m,z7.s,z25.s
fmla z0.s,p0/m,z24.s,z19.s
fmla z1.s,p0/m,z25.s,z19.s
incb x1, ALL, MUL #4
incb x2, ALL, MUL #6
.ukr7_done:
cbz x9,.ukr7_taildone
.ukr7_tail:
add x9,x9,#-1
mov x10,x1
incb x10, ALL, MUL #1
ld1w {z4.s}, p0/z, [x1]
ld1w {z2.s}, p0/z, [x2]
ld1w {z3.s}, p0/z, [x2, #1, MUL VL]
ld1rw {z16.s}, p0/z, [x10]
fmopa za0.s,p0/m,p0/m,z4.s,z2.s
fmopa za1.s,p0/m,p0/m,z4.s,z3.s
fmla z0.s,p0/m,z2.s,z16.s
fmla z1.s,p0/m,z3.s,z16.s
add x1,x1,#4
incb x1, ALL, MUL #1
incb x2, ALL, MUL #2
cbnz x9,.ukr7_tail
.ukr7_taildone:
ldr s2, [x5]
fmov s3,wzr
fcmp s2,s3
b.ne .ukr0_try0
ldr s2, [x4]
mov x0,#1065353216
fmov s3,w0
fcmp s2,s3
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr s2, [x5]
mov x0,#1065353216
fmov s3,w0
fcmp s2,s3
b.ne .ukr0_try2
ldr s2, [x4]
mov x0,#1065353216
fmov s3,w0
fcmp s2,s3
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr s2, [x4]
mov x0,#1065353216
fmov s3,w0
fcmp s2,s3
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
st1w {za0h.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
st1w {za0h.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
st1w {za0h.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
st1w {za0h.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr1_slices
st1w {z0.s}, p0, [x0]
st1w {z1.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
ld1rw {z2.s}, p0/z, [x4]
mov x1,x7
mov x12,#0
.ukr2_slices:
add x1,x1,#-4
mova z3.s,p0/m,za0h.s[w12,0]
mova z4.s,p0/m,za1h.s[w12,0]
fmul z5.s,z3.s,z2.s
fmul z6.s,z4.s,z2.s
st1w {z5.s}, p0, [x0]
st1w {z6.s}, p0, [x0, #1, MUL VL]
mova z7.s,p0/m,za0h.s[w12,1]
mova z16.s,p0/m,za1h.s[w12,1]
fmul z17.s,z7.s,z2.s
add x0,x0,x6
fmul z18.s,z16.s,z2.s
st1w {z17.s}, p0, [x0]
st1w {z18.s}, p0, [x0, #1, MUL VL]
mova z19.s,p0/m,za0h.s[w12,2]
mova z20.s,p0/m,za1h.s[w12,2]
fmul z21.s,z19.s,z2.s
add x0,x0,x6
fmul z22.s,z20.s,z2.s
st1w {z21.s}, p0, [x0]
st1w {z22.s}, p0, [x0, #1, MUL VL]
mova z23.s,p0/m,za0h.s[w12,3]
mova z24.s,p0/m,za1h.s[w12,3]
fmul z25.s,z23.s,z2.s
add x0,x0,x6
fmul z26.s,z24.s,z2.s
st1w {z25.s}, p0, [x0]
st1w {z26.s}, p0, [x0, #1, MUL VL]
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr2_slices
sub x0,x0,x8
fmul z3.s,z0.s,z2.s
add x0,x0,x8
fmul z0.s,z1.s,z2.s
st1w {z3.s}, p0, [x0]
st1w {z0.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
.ukr3_slices:
add x1,x1,#-4
mova z2.s,p0/m,za0h.s[w12,0]
ld1w {z3.s}, p0/z, [x0]
mova z4.s,p0/m,za1h.s[w12,0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
fadd z3.s,z2.s,z3.s
fadd z5.s,z4.s,z5.s
add x0,x0,x6
st1w {z3.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
mova z6.s,p0/m,za0h.s[w12,1]
ld1w {z7.s}, p0/z, [x0]
mova z16.s,p0/m,za1h.s[w12,1]
ld1w {z17.s}, p0/z, [x0, #1, MUL VL]
fadd z7.s,z6.s,z7.s
add x3,x3,x6
fadd z17.s,z16.s,z17.s
add x0,x0,x6
st1w {z7.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
mova z18.s,p0/m,za0h.s[w12,2]
ld1w {z19.s}, p0/z, [x0]
mova z20.s,p0/m,za1h.s[w12,2]
ld1w {z21.s}, p0/z, [x0, #1, MUL VL]
fadd z19.s,z18.s,z19.s
add x3,x3,x6
fadd z21.s,z20.s,z21.s
add x0,x0,x6
st1w {z19.s}, p0, [x3]
st1w {z21.s}, p0, [x3, #1, MUL VL]
mova z22.s,p0/m,za0h.s[w12,3]
ld1w {z23.s}, p0/z, [x0]
mova z24.s,p0/m,za1h.s[w12,3]
ld1w {z25.s}, p0/z, [x0, #1, MUL VL]
fadd z23.s,z22.s,z23.s
add x3,x3,x6
fadd z25.s,z24.s,z25.s
st1w {z23.s}, p0, [x3]
st1w {z25.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr3_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1w {z2.s}, p0/z, [x0]
ld1w {z3.s}, p0/z, [x0, #1, MUL VL]
fadd z2.s,z0.s,z2.s
add x3,x3,x8
fadd z3.s,z1.s,z3.s
st1w {z2.s}, p0, [x3]
st1w {z3.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
ld1rw {z2.s}, p0/z, [x4]
mov x1,x7
mov x12,#0
.ukr4_slices:
add x1,x1,#-4
mova z3.s,p0/m,za0h.s[w12,0]
ld1w {z4.s}, p0/z, [x0]
mova z5.s,p0/m,za1h.s[w12,0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
fmla z4.s,p0/m,z3.s,z2.s
fmla z6.s,p0/m,z5.s,z2.s
add x0,x0,x6
st1w {z4.s}, p0, [x3]
st1w {z6.s}, p0, [x3, #1, MUL VL]
mova z7.s,p0/m,za0h.s[w12,1]
ld1w {z16.s}, p0/z, [x0]
mova z17.s,p0/m,za1h.s[w12,1]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
fmla z16.s,p0/m,z7.s,z2.s
add x3,x3,x6
fmla z18.s,p0/m,z17.s,z2.s
add x0,x0,x6
st1w {z16.s}, p0, [x3]
st1w {z18.s}, p0, [x3, #1, MUL VL]
mova z19.s,p0/m,za0h.s[w12,2]
ld1w {z20.s}, p0/z, [x0]
mova z21.s,p0/m,za1h.s[w12,2]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
fmla z20.s,p0/m,z19.s,z2.s
add x3,x3,x6
fmla z22.s,p0/m,z21.s,z2.s
add x0,x0,x6
st1w {z20.s}, p0, [x3]
st1w {z22.s}, p0, [x3, #1, MUL VL]
mova z23.s,p0/m,za0h.s[w12,3]
ld1w {z24.s}, p0/z, [x0]
mova z25.s,p0/m,za1h.s[w12,3]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
fmla z24.s,p0/m,z23.s,z2.s
add x3,x3,x6
fmla z26.s,p0/m,z25.s,z2.s
st1w {z24.s}, p0, [x3]
st1w {z26.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr4_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1w {z3.s}, p0/z, [x0]
ld1w {z4.s}, p0/z, [x0, #1, MUL VL]
fmla z3.s,p0/m,z0.s,z2.s
add x3,x3,x8
fmla z4.s,p0/m,z1.s,z2.s
st1w {z3.s}, p0, [x3]
st1w {z4.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
ld1rw {z2.s}, p0/z, [x5]
mov x1,x7
mov x12,#0
.ukr5_slices:
add x1,x1,#-4
mova z3.s,p0/m,za0h.s[w12,0]
ld1w {z4.s}, p0/z, [x0]
mova z5.s,p0/m,za1h.s[w12,0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
fmla z3.s,p0/m,z4.s,z2.s
fmla z5.s,p0/m,z6.s,z2.s
mova za0h.s[w12,0],p0/m,z3.s
add x0,x0,x6
mova za1h.s[w12,0],p0/m,z5.s
mova z7.s,p0/m,za0h.s[w12,1]
ld1w {z16.s}, p0/z, [x0]
mova z17.s,p0/m,za1h.s[w12,1]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
fmla z7.s,p0/m,z16.s,z2.s
fmla z17.s,p0/m,z18.s,z2.s
st1w {z3.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,1],p0/m,z7.s
add x0,x0,x6
mova za1h.s[w12,1],p0/m,z17.s
add x3,x3,x6
mova z19.s,p0/m,za0h.s[w12,2]
ld1w {z20.s}, p0/z, [x0]
mova z21.s,p0/m,za1h.s[w12,2]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
st1w {z7.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
fmla z19.s,p0/m,z20.s,z2.s
fmla z21.s,p0/m,z22.s,z2.s
add x3,x3,x6
mova za0h.s[w12,2],p0/m,z19.s
add x0,x0,x6
mova za1h.s[w12,2],p0/m,z21.s
st1w {z19.s}, p0, [x3]
st1w {z21.s}, p0, [x3, #1, MUL VL]
mova z23.s,p0/m,za0h.s[w12,3]
ld1w {z24.s}, p0/z, [x0]
mova z25.s,p0/m,za1h.s[w12,3]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
fmla z23.s,p0/m,z24.s,z2.s
fmla z25.s,p0/m,z26.s,z2.s
add x3,x3,x6
st1w {z23.s}, p0, [x3]
st1w {z25.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,3],p0/m,z23.s
mova za1h.s[w12,3],p0/m,z25.s
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr5_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1w {z3.s}, p0/z, [x0]
ld1w {z4.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z3.s,z2.s
add x3,x3,x8
fmla z1.s,p0/m,z4.s,z2.s
st1w {z0.s}, p0, [x3]
st1w {z1.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
ld1rw {z2.s}, p0/z, [x5]
ld1rw {z3.s}, p0/z, [x4]
mov x1,x7
mov x12,#0
.ukr6_slices:
add x1,x1,#-4
ld1w {z4.s}, p0/z, [x0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
fmul z4.s,z4.s,z2.s
mova z6.s,p0/m,za0h.s[w12,0]
fmul z5.s,z5.s,z2.s
mova z7.s,p0/m,za1h.s[w12,0]
add x0,x0,x6
fmla z4.s,p0/m,z6.s,z3.s
fmla z5.s,p0/m,z7.s,z3.s
ld1w {z16.s}, p0/z, [x0]
ld1w {z17.s}, p0/z, [x0, #1, MUL VL]
st1w {z4.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
fmul z16.s,z16.s,z2.s
mova z18.s,p0/m,za0h.s[w12,1]
fmul z17.s,z17.s,z2.s
mova z19.s,p0/m,za1h.s[w12,1]
add x0,x0,x6
fmla z16.s,p0/m,z18.s,z3.s
add x3,x3,x6
fmla z17.s,p0/m,z19.s,z3.s
ld1w {z20.s}, p0/z, [x0]
ld1w {z21.s}, p0/z, [x0, #1, MUL VL]
st1w {z16.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
fmul z20.s,z20.s,z2.s
mova z22.s,p0/m,za0h.s[w12,2]
fmul z21.s,z21.s,z2.s
mova z23.s,p0/m,za1h.s[w12,2]
add x0,x0,x6
fmla z20.s,p0/m,z22.s,z3.s
add x3,x3,x6
fmla z21.s,p0/m,z23.s,z3.s
ld1w {z24.s}, p0/z, [x0]
ld1w {z25.s}, p0/z, [x0, #1, MUL VL]
st1w {z20.s}, p0, [x3]
st1w {z21.s}, p0, [x3, #1, MUL VL]
fmul z24.s,z24.s,z2.s
mova z26.s,p0/m,za0h.s[w12,3]
fmul z25.s,z25.s,z2.s
mova z27.s,p0/m,za1h.s[w12,3]
fmla z24.s,p0/m,z26.s,z3.s
add x3,x3,x6
fmla z25.s,p0/m,z27.s,z3.s
st1w {z24.s}, p0, [x3]
st1w {z25.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr6_slices
sub x0,x0,x8
add x0,x0,x8
ld1w {z4.s}, p0/z, [x0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
sub x3,x3,x8
fmul z4.s,z4.s,z2.s
fmul z5.s,z5.s,z2.s
fmla z4.s,p0/m,z0.s,z3.s
add x3,x3,x8
fmla z5.s,p0/m,z1.s,z3.s
st1w {z4.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
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
.size bli_sgemm_ukrgen_sme_sf_1vx2v_1x2v_asm, .-bli_sgemm_ukrgen_sme_sf_1vx2v_1x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_sgemm_ukrgen_sme_sf_1vx2v_2x2v
.text
.global bli_sgemm_ukrgen_sme_sf_1vx2v_2x2v_asm
.type bli_sgemm_ukrgen_sme_sf_1vx2v_2x2v_asm, %function
bli_sgemm_ukrgen_sme_sf_1vx2v_2x2v_asm:
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
smstart
ptrue p0.s
cntw x7
mul x8,x7,x6
lsr x9,x6,#2
and x10,x0,#3
lsr x0,x0,#2
zero {za0.s}
zero {za1.s}
dup z0.s,#0
dup z1.s,#0
dup z2.s,#0
dup z3.s,#0
cbz x0,.ukr7_done
add x11,x1,#8
ld1w {z4.s}, p0/z, [x11, #1, MUL VL]
add x11,x11,#8
ld1w {z5.s}, p0/z, [x2]
ld1w {z6.s}, p0/z, [x2, #1, MUL VL]
ld1w {z7.s}, p0/z, [x1]
ld1w {z16.s}, p0/z, [x11, #2, MUL VL]
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x11,x1,#24
ld1w {z17.s}, p0/z, [x11, #3, MUL VL]
add x11,x11,#-24
incb x11, ALL, MUL #1
ld1rw {z18.s}, p0/z, [x11]
ld1rw {z19.s}, p0/z, [x11, #4]
add x11,x11,#8
incb x11, ALL, MUL #1
ld1rw {z20.s}, p0/z, [x11]
ld1rw {z21.s}, p0/z, [x11, #4]
add x11,x11,#8
incb x11, ALL, MUL #1
ld1rw {z22.s}, p0/z, [x11]
ld1rw {z23.s}, p0/z, [x11, #4]
add x11,x11,#8
incb x11, ALL, MUL #1
ld1rw {z24.s}, p0/z, [x11]
ld1rw {z25.s}, p0/z, [x11, #4]
add x11,x11,#8
fmopa za0.s,p0/m,p0/m,z7.s,z5.s
fmopa za1.s,p0/m,p0/m,z7.s,z6.s
decb x11, ALL, MUL #4
ld1w {z26.s}, p0/z, [x2]
ld1w {z27.s}, p0/z, [x2, #1, MUL VL]
ld1w {z7.s}, p0/z, [x11, #4, MUL VL]
fmopa za0.s,p0/m,p0/m,z4.s,z26.s
fmopa za1.s,p0/m,p0/m,z4.s,z27.s
fmla z0.s,p0/m,z5.s,z18.s
fmla z1.s,p0/m,z6.s,z18.s
fmla z2.s,p0/m,z5.s,z19.s
fmla z3.s,p0/m,z6.s,z19.s
add x11,x11,#8
ld1w {z28.s}, p0/z, [x2, #2, MUL VL]
ld1w {z29.s}, p0/z, [x2, #3, MUL VL]
fmla z0.s,p0/m,z26.s,z20.s
fmla z1.s,p0/m,z27.s,z20.s
fmla z2.s,p0/m,z26.s,z21.s
fmla z3.s,p0/m,z27.s,z21.s
ld1w {z4.s}, p0/z, [x11, #5, MUL VL]
fmopa za0.s,p0/m,p0/m,z16.s,z28.s
fmopa za1.s,p0/m,p0/m,z16.s,z29.s
ld1w {z30.s}, p0/z, [x2, #4, MUL VL]
ld1w {z31.s}, p0/z, [x2, #5, MUL VL]
fmla z0.s,p0/m,z28.s,z22.s
fmla z1.s,p0/m,z29.s,z22.s
fmla z2.s,p0/m,z28.s,z23.s
fmla z3.s,p0/m,z29.s,z23.s
add x11,x11,#8
ld1w {z5.s}, p0/z, [x2, #6, MUL VL]
ld1w {z6.s}, p0/z, [x2, #7, MUL VL]
add x1,x1,#32
fmopa za0.s,p0/m,p0/m,z17.s,z30.s
fmopa za1.s,p0/m,p0/m,z17.s,z31.s
fmla z0.s,p0/m,z30.s,z24.s
fmla z1.s,p0/m,z31.s,z24.s
fmla z2.s,p0/m,z30.s,z25.s
fmla z3.s,p0/m,z31.s,z25.s
ld1w {z16.s}, p0/z, [x11, #6, MUL VL]
incb x1, ALL, MUL #4
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x11,x1,#24
ld1w {z17.s}, p0/z, [x11, #3, MUL VL]
add x11,x11,#-24
incb x11, ALL, MUL #1
ld1rw {z18.s}, p0/z, [x11]
ld1rw {z19.s}, p0/z, [x11, #4]
add x11,x11,#8
incb x11, ALL, MUL #1
ld1rw {z20.s}, p0/z, [x11]
ld1rw {z21.s}, p0/z, [x11, #4]
add x11,x11,#8
incb x11, ALL, MUL #1
ld1rw {z22.s}, p0/z, [x11]
ld1rw {z23.s}, p0/z, [x11, #4]
fmopa za0.s,p0/m,p0/m,z7.s,z5.s
fmopa za1.s,p0/m,p0/m,z7.s,z6.s
ld1w {z26.s}, p0/z, [x2]
ld1w {z27.s}, p0/z, [x2, #1, MUL VL]
fmla z0.s,p0/m,z5.s,z18.s
fmla z1.s,p0/m,z6.s,z18.s
fmla z2.s,p0/m,z5.s,z19.s
fmla z3.s,p0/m,z6.s,z19.s
add x11,x11,#8
fmopa za0.s,p0/m,p0/m,z4.s,z26.s
fmopa za1.s,p0/m,p0/m,z4.s,z27.s
ld1w {z28.s}, p0/z, [x2, #2, MUL VL]
ld1w {z29.s}, p0/z, [x2, #3, MUL VL]
fmla z0.s,p0/m,z26.s,z20.s
fmla z1.s,p0/m,z27.s,z20.s
fmla z2.s,p0/m,z26.s,z21.s
fmla z3.s,p0/m,z27.s,z21.s
incb x11, ALL, MUL #1
fmopa za0.s,p0/m,p0/m,z16.s,z28.s
fmopa za1.s,p0/m,p0/m,z16.s,z29.s
ld1w {z30.s}, p0/z, [x2, #4, MUL VL]
ld1w {z31.s}, p0/z, [x2, #5, MUL VL]
fmla z0.s,p0/m,z28.s,z22.s
fmla z1.s,p0/m,z29.s,z22.s
fmla z2.s,p0/m,z28.s,z23.s
fmla z3.s,p0/m,z29.s,z23.s
ld1rw {z24.s}, p0/z, [x11]
ld1rw {z25.s}, p0/z, [x11, #4]
add x1,x1,#32
fmopa za0.s,p0/m,p0/m,z17.s,z30.s
fmopa za1.s,p0/m,p0/m,z17.s,z31.s
fmla z0.s,p0/m,z30.s,z24.s
fmla z1.s,p0/m,z31.s,z24.s
fmla z2.s,p0/m,z30.s,z25.s
fmla z3.s,p0/m,z31.s,z25.s
incb x1, ALL, MUL #4
incb x2, ALL, MUL #6
.ukr7_done:
cbz x10,.ukr7_taildone
.ukr7_tail:
add x10,x10,#-1
mov x11,x1
incb x11, ALL, MUL #1
ld1w {z7.s}, p0/z, [x1]
ld1w {z5.s}, p0/z, [x2]
ld1w {z6.s}, p0/z, [x2, #1, MUL VL]
ld1rw {z18.s}, p0/z, [x11]
ld1rw {z19.s}, p0/z, [x11, #4]
fmopa za0.s,p0/m,p0/m,z7.s,z5.s
fmopa za1.s,p0/m,p0/m,z7.s,z6.s
fmla z0.s,p0/m,z5.s,z18.s
fmla z1.s,p0/m,z6.s,z18.s
fmla z2.s,p0/m,z5.s,z19.s
fmla z3.s,p0/m,z6.s,z19.s
add x1,x1,#8
incb x1, ALL, MUL #1
incb x2, ALL, MUL #2
cbnz x10,.ukr7_tail
.ukr7_taildone:
ldr s4, [x5]
fmov s5,wzr
fcmp s4,s5
b.ne .ukr0_try0
ldr s4, [x4]
mov x0,#1065353216
fmov s5,w0
fcmp s4,s5
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr s4, [x5]
mov x0,#1065353216
fmov s5,w0
fcmp s4,s5
b.ne .ukr0_try2
ldr s4, [x4]
mov x0,#1065353216
fmov s5,w0
fcmp s4,s5
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr s4, [x4]
mov x0,#1065353216
fmov s5,w0
fcmp s4,s5
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
st1w {za0h.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
st1w {za0h.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
st1w {za0h.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
st1w {za0h.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr1_slices
st1w {z0.s}, p0, [x0]
st1w {z1.s}, p0, [x0, #1, MUL VL]
st1w {z2.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z3.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
ld1rw {z4.s}, p0/z, [x4]
mov x1,x7
mov x12,#0
.ukr2_slices:
add x1,x1,#-4
mova z5.s,p0/m,za0h.s[w12,0]
mova z6.s,p0/m,za1h.s[w12,0]
fmul z7.s,z5.s,z4.s
fmul z16.s,z6.s,z4.s
st1w {z7.s}, p0, [x0]
st1w {z16.s}, p0, [x0, #1, MUL VL]
mova z17.s,p0/m,za0h.s[w12,1]
mova z18.s,p0/m,za1h.s[w12,1]
fmul z19.s,z17.s,z4.s
add x0,x0,x6
fmul z20.s,z18.s,z4.s
st1w {z19.s}, p0, [x0]
st1w {z20.s}, p0, [x0, #1, MUL VL]
mova z21.s,p0/m,za0h.s[w12,2]
mova z22.s,p0/m,za1h.s[w12,2]
fmul z23.s,z21.s,z4.s
add x0,x0,x6
fmul z24.s,z22.s,z4.s
st1w {z23.s}, p0, [x0]
st1w {z24.s}, p0, [x0, #1, MUL VL]
mova z25.s,p0/m,za0h.s[w12,3]
mova z26.s,p0/m,za1h.s[w12,3]
fmul z27.s,z25.s,z4.s
add x0,x0,x6
fmul z28.s,z26.s,z4.s
st1w {z27.s}, p0, [x0]
st1w {z28.s}, p0, [x0, #1, MUL VL]
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr2_slices
sub x0,x0,x8
fmul z5.s,z0.s,z4.s
add x0,x0,x8
fmul z0.s,z1.s,z4.s
fmul z1.s,z2.s,z4.s
st1w {z5.s}, p0, [x0]
st1w {z0.s}, p0, [x0, #1, MUL VL]
st1w {z1.s}, p0, [x0, x9, lsl #2]
fmul z0.s,z3.s,z4.s
add x0,x0,x6
st1w {z0.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
.ukr3_slices:
add x1,x1,#-4
mova z4.s,p0/m,za0h.s[w12,0]
ld1w {z5.s}, p0/z, [x0]
mova z6.s,p0/m,za1h.s[w12,0]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
fadd z5.s,z4.s,z5.s
fadd z7.s,z6.s,z7.s
add x0,x0,x6
st1w {z5.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
mova z16.s,p0/m,za0h.s[w12,1]
ld1w {z17.s}, p0/z, [x0]
mova z18.s,p0/m,za1h.s[w12,1]
ld1w {z19.s}, p0/z, [x0, #1, MUL VL]
fadd z17.s,z16.s,z17.s
add x3,x3,x6
fadd z19.s,z18.s,z19.s
add x0,x0,x6
st1w {z17.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
mova z20.s,p0/m,za0h.s[w12,2]
ld1w {z21.s}, p0/z, [x0]
mova z22.s,p0/m,za1h.s[w12,2]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
fadd z21.s,z20.s,z21.s
add x3,x3,x6
fadd z23.s,z22.s,z23.s
add x0,x0,x6
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
mova z24.s,p0/m,za0h.s[w12,3]
ld1w {z25.s}, p0/z, [x0]
mova z26.s,p0/m,za1h.s[w12,3]
ld1w {z27.s}, p0/z, [x0, #1, MUL VL]
fadd z25.s,z24.s,z25.s
add x3,x3,x6
fadd z27.s,z26.s,z27.s
st1w {z25.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr3_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1w {z4.s}, p0/z, [x0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
ld1w {z6.s}, p0/z, [x0, x9, lsl #2]
fadd z4.s,z0.s,z4.s
add x3,x3,x8
fadd z5.s,z1.s,z5.s
fadd z6.s,z2.s,z6.s
add x0,x0,x6
st1w {z4.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
st1w {z6.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z3.s,z0.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
ld1rw {z4.s}, p0/z, [x4]
mov x1,x7
mov x12,#0
.ukr4_slices:
add x1,x1,#-4
mova z5.s,p0/m,za0h.s[w12,0]
ld1w {z6.s}, p0/z, [x0]
mova z7.s,p0/m,za1h.s[w12,0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
fmla z6.s,p0/m,z5.s,z4.s
fmla z16.s,p0/m,z7.s,z4.s
add x0,x0,x6
st1w {z6.s}, p0, [x3]
st1w {z16.s}, p0, [x3, #1, MUL VL]
mova z17.s,p0/m,za0h.s[w12,1]
ld1w {z18.s}, p0/z, [x0]
mova z19.s,p0/m,za1h.s[w12,1]
ld1w {z20.s}, p0/z, [x0, #1, MUL VL]
fmla z18.s,p0/m,z17.s,z4.s
add x3,x3,x6
fmla z20.s,p0/m,z19.s,z4.s
add x0,x0,x6
st1w {z18.s}, p0, [x3]
st1w {z20.s}, p0, [x3, #1, MUL VL]
mova z21.s,p0/m,za0h.s[w12,2]
ld1w {z22.s}, p0/z, [x0]
mova z23.s,p0/m,za1h.s[w12,2]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
fmla z22.s,p0/m,z21.s,z4.s
add x3,x3,x6
fmla z24.s,p0/m,z23.s,z4.s
add x0,x0,x6
st1w {z22.s}, p0, [x3]
st1w {z24.s}, p0, [x3, #1, MUL VL]
mova z25.s,p0/m,za0h.s[w12,3]
ld1w {z26.s}, p0/z, [x0]
mova z27.s,p0/m,za1h.s[w12,3]
ld1w {z28.s}, p0/z, [x0, #1, MUL VL]
fmla z26.s,p0/m,z25.s,z4.s
add x3,x3,x6
fmla z28.s,p0/m,z27.s,z4.s
st1w {z26.s}, p0, [x3]
st1w {z28.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr4_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1w {z5.s}, p0/z, [x0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
ld1w {z7.s}, p0/z, [x0, x9, lsl #2]
fmla z5.s,p0/m,z0.s,z4.s
add x3,x3,x8
fmla z6.s,p0/m,z1.s,z4.s
fmla z7.s,p0/m,z2.s,z4.s
add x0,x0,x6
st1w {z5.s}, p0, [x3]
st1w {z6.s}, p0, [x3, #1, MUL VL]
st1w {z7.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z3.s,z4.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
ld1rw {z4.s}, p0/z, [x5]
mov x1,x7
mov x12,#0
.ukr5_slices:
add x1,x1,#-4
mova z5.s,p0/m,za0h.s[w12,0]
ld1w {z6.s}, p0/z, [x0]
mova z7.s,p0/m,za1h.s[w12,0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
fmla z5.s,p0/m,z6.s,z4.s
fmla z7.s,p0/m,z16.s,z4.s
mova za0h.s[w12,0],p0/m,z5.s
add x0,x0,x6
mova za1h.s[w12,0],p0/m,z7.s
mova z17.s,p0/m,za0h.s[w12,1]
ld1w {z18.s}, p0/z, [x0]
mova z19.s,p0/m,za1h.s[w12,1]
ld1w {z20.s}, p0/z, [x0, #1, MUL VL]
fmla z17.s,p0/m,z18.s,z4.s
fmla z19.s,p0/m,z20.s,z4.s
st1w {z5.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,1],p0/m,z17.s
add x0,x0,x6
mova za1h.s[w12,1],p0/m,z19.s
add x3,x3,x6
mova z21.s,p0/m,za0h.s[w12,2]
ld1w {z22.s}, p0/z, [x0]
mova z23.s,p0/m,za1h.s[w12,2]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
st1w {z17.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
fmla z21.s,p0/m,z22.s,z4.s
fmla z23.s,p0/m,z24.s,z4.s
add x3,x3,x6
mova za0h.s[w12,2],p0/m,z21.s
add x0,x0,x6
mova za1h.s[w12,2],p0/m,z23.s
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
mova z25.s,p0/m,za0h.s[w12,3]
ld1w {z26.s}, p0/z, [x0]
mova z27.s,p0/m,za1h.s[w12,3]
ld1w {z28.s}, p0/z, [x0, #1, MUL VL]
fmla z25.s,p0/m,z26.s,z4.s
fmla z27.s,p0/m,z28.s,z4.s
add x3,x3,x6
st1w {z25.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,3],p0/m,z25.s
mova za1h.s[w12,3],p0/m,z27.s
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr5_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1w {z5.s}, p0/z, [x0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
ld1w {z7.s}, p0/z, [x0, x9, lsl #2]
fmla z0.s,p0/m,z5.s,z4.s
add x3,x3,x8
fmla z1.s,p0/m,z6.s,z4.s
fmla z2.s,p0/m,z7.s,z4.s
add x0,x0,x6
st1w {z0.s}, p0, [x3]
st1w {z1.s}, p0, [x3, #1, MUL VL]
st1w {z2.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z3.s,p0/m,z0.s,z4.s
add x3,x3,x6
st1w {z3.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
ld1rw {z4.s}, p0/z, [x5]
ld1rw {z5.s}, p0/z, [x4]
mov x1,x7
mov x12,#0
.ukr6_slices:
add x1,x1,#-4
ld1w {z6.s}, p0/z, [x0]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
fmul z6.s,z6.s,z4.s
mova z16.s,p0/m,za0h.s[w12,0]
fmul z7.s,z7.s,z4.s
mova z17.s,p0/m,za1h.s[w12,0]
add x0,x0,x6
fmla z6.s,p0/m,z16.s,z5.s
fmla z7.s,p0/m,z17.s,z5.s
ld1w {z18.s}, p0/z, [x0]
ld1w {z19.s}, p0/z, [x0, #1, MUL VL]
st1w {z6.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
fmul z18.s,z18.s,z4.s
mova z20.s,p0/m,za0h.s[w12,1]
fmul z19.s,z19.s,z4.s
mova z21.s,p0/m,za1h.s[w12,1]
add x0,x0,x6
fmla z18.s,p0/m,z20.s,z5.s
add x3,x3,x6
fmla z19.s,p0/m,z21.s,z5.s
ld1w {z22.s}, p0/z, [x0]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
st1w {z18.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
fmul z22.s,z22.s,z4.s
mova z24.s,p0/m,za0h.s[w12,2]
fmul z23.s,z23.s,z4.s
mova z25.s,p0/m,za1h.s[w12,2]
add x0,x0,x6
fmla z22.s,p0/m,z24.s,z5.s
add x3,x3,x6
fmla z23.s,p0/m,z25.s,z5.s
ld1w {z26.s}, p0/z, [x0]
ld1w {z27.s}, p0/z, [x0, #1, MUL VL]
st1w {z22.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
fmul z26.s,z26.s,z4.s
mova z28.s,p0/m,za0h.s[w12,3]
fmul z27.s,z27.s,z4.s
mova z29.s,p0/m,za1h.s[w12,3]
fmla z26.s,p0/m,z28.s,z5.s
add x3,x3,x6
fmla z27.s,p0/m,z29.s,z5.s
st1w {z26.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr6_slices
sub x0,x0,x8
add x0,x0,x8
ld1w {z6.s}, p0/z, [x0]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
ld1w {z16.s}, p0/z, [x0, x9, lsl #2]
sub x3,x3,x8
fmul z6.s,z6.s,z4.s
fmul z7.s,z7.s,z4.s
fmul z16.s,z16.s,z4.s
add x0,x0,x6
fmla z6.s,p0/m,z0.s,z5.s
add x3,x3,x8
fmla z7.s,p0/m,z1.s,z5.s
fmla z16.s,p0/m,z2.s,z5.s
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
st1w {z6.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
st1w {z16.s}, p0, [x3, x9, lsl #2]
fmul z0.s,z0.s,z4.s
fmla z0.s,p0/m,z3.s,z5.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
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
.size bli_sgemm_ukrgen_sme_sf_1vx2v_2x2v_asm, .-bli_sgemm_ukrgen_sme_sf_1vx2v_2x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_sgemm_ukrgen_sme_sf_1vx2v_3x2v
.text
.global bli_sgemm_ukrgen_sme_sf_1vx2v_3x2v_asm
.type bli_sgemm_ukrgen_sme_sf_1vx2v_3x2v_asm, %function
bli_sgemm_ukrgen_sme_sf_1vx2v_3x2v_asm:
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
smstart
ptrue p0.s
cntw x7
mul x8,x7,x6
lsr x9,x6,#2
and x10,x0,#3
lsr x0,x0,#2
zero {za0.s}
zero {za1.s}
dup z0.s,#0
dup z1.s,#0
dup z2.s,#0
dup z3.s,#0
dup z4.s,#0
dup z5.s,#0
cbz x0,.ukr7_done
add x11,x1,#12
ld1w {z6.s}, p0/z, [x11, #1, MUL VL]
add x11,x11,#12
ld1w {z7.s}, p0/z, [x11, #2, MUL VL]
ld1w {z16.s}, p0/z, [x1]
add x11,x11,#12
ld1w {z17.s}, p0/z, [x2]
ld1w {z18.s}, p0/z, [x2, #1, MUL VL]
ld1w {z19.s}, p0/z, [x11, #3, MUL VL]
incb x2, ALL, MUL #2
incb x1, ALL, MUL #1
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x11,x1,#12
incb x11, ALL, MUL #1
ld1rw {z20.s}, p0/z, [x11]
ld1rw {z21.s}, p0/z, [x11, #4]
ld1rw {z22.s}, p0/z, [x11, #8]
add x11,x11,#12
incb x11, ALL, MUL #1
ld1rw {z23.s}, p0/z, [x11]
ld1rw {z24.s}, p0/z, [x11, #4]
ld1rw {z25.s}, p0/z, [x11, #8]
add x11,x11,#12
incb x11, ALL, MUL #1
ld1rw {z26.s}, p0/z, [x11]
ld1rw {z27.s}, p0/z, [x11, #4]
ld1rw {z28.s}, p0/z, [x11, #8]
add x11,x11,#12
fmopa za0.s,p0/m,p0/m,z16.s,z17.s
fmopa za1.s,p0/m,p0/m,z16.s,z18.s
decb x11, ALL, MUL #3
ld1w {z29.s}, p0/z, [x2]
ld1w {z30.s}, p0/z, [x2, #1, MUL VL]
ld1w {z16.s}, p0/z, [x11, #3, MUL VL]
fmopa za0.s,p0/m,p0/m,z6.s,z29.s
fmopa za1.s,p0/m,p0/m,z6.s,z30.s
add x11,x11,#12
ld1w {z31.s}, p0/z, [x2, #2, MUL VL]
ld1w {z8.s}, p0/z, [x2, #3, MUL VL]
ld1rw {z9.s}, p0/z, [x1]
ld1rw {z10.s}, p0/z, [x1, #4]
ld1rw {z11.s}, p0/z, [x1, #8]
ld1w {z6.s}, p0/z, [x11, #4, MUL VL]
fmopa za0.s,p0/m,p0/m,z7.s,z31.s
fmopa za1.s,p0/m,p0/m,z7.s,z8.s
fmla z0.s,p0/m,z17.s,z9.s
fmla z1.s,p0/m,z18.s,z9.s
fmla z2.s,p0/m,z17.s,z10.s
fmla z3.s,p0/m,z18.s,z10.s
fmla z4.s,p0/m,z17.s,z11.s
fmla z5.s,p0/m,z18.s,z11.s
add x11,x11,#12
ld1w {z12.s}, p0/z, [x2, #4, MUL VL]
ld1w {z13.s}, p0/z, [x2, #5, MUL VL]
fmla z0.s,p0/m,z29.s,z20.s
fmla z1.s,p0/m,z30.s,z20.s
fmla z2.s,p0/m,z29.s,z21.s
fmla z3.s,p0/m,z30.s,z21.s
fmla z4.s,p0/m,z29.s,z22.s
fmla z5.s,p0/m,z30.s,z22.s
ld1w {z7.s}, p0/z, [x11, #5, MUL VL]
fmopa za0.s,p0/m,p0/m,z19.s,z12.s
fmopa za1.s,p0/m,p0/m,z19.s,z13.s
fmla z0.s,p0/m,z31.s,z23.s
fmla z1.s,p0/m,z8.s,z23.s
fmla z2.s,p0/m,z31.s,z24.s
fmla z3.s,p0/m,z8.s,z24.s
fmla z4.s,p0/m,z31.s,z25.s
fmla z5.s,p0/m,z8.s,z25.s
add x11,x11,#12
ld1w {z17.s}, p0/z, [x2, #6, MUL VL]
ld1w {z18.s}, p0/z, [x2, #7, MUL VL]
add x1,x1,#48
fmla z0.s,p0/m,z12.s,z26.s
fmla z1.s,p0/m,z13.s,z26.s
fmla z2.s,p0/m,z12.s,z27.s
fmla z3.s,p0/m,z13.s,z27.s
fmla z4.s,p0/m,z12.s,z28.s
fmla z5.s,p0/m,z13.s,z28.s
ld1w {z19.s}, p0/z, [x11, #6, MUL VL]
incb x1, ALL, MUL #4
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x11,x1,#12
incb x11, ALL, MUL #1
ld1rw {z20.s}, p0/z, [x11]
ld1rw {z21.s}, p0/z, [x11, #4]
ld1rw {z22.s}, p0/z, [x11, #8]
add x11,x11,#12
incb x11, ALL, MUL #1
ld1rw {z9.s}, p0/z, [x1]
ld1rw {z10.s}, p0/z, [x1, #4]
ld1rw {z11.s}, p0/z, [x1, #8]
ld1rw {z23.s}, p0/z, [x11]
ld1rw {z24.s}, p0/z, [x11, #4]
ld1rw {z25.s}, p0/z, [x11, #8]
fmopa za0.s,p0/m,p0/m,z16.s,z17.s
fmopa za1.s,p0/m,p0/m,z16.s,z18.s
ld1w {z29.s}, p0/z, [x2]
ld1w {z30.s}, p0/z, [x2, #1, MUL VL]
fmla z0.s,p0/m,z17.s,z9.s
fmla z1.s,p0/m,z18.s,z9.s
fmla z2.s,p0/m,z17.s,z10.s
fmla z3.s,p0/m,z18.s,z10.s
fmla z4.s,p0/m,z17.s,z11.s
fmla z5.s,p0/m,z18.s,z11.s
add x11,x11,#12
fmopa za0.s,p0/m,p0/m,z6.s,z29.s
fmopa za1.s,p0/m,p0/m,z6.s,z30.s
ld1w {z31.s}, p0/z, [x2, #2, MUL VL]
ld1w {z8.s}, p0/z, [x2, #3, MUL VL]
fmla z0.s,p0/m,z29.s,z20.s
fmla z1.s,p0/m,z30.s,z20.s
fmla z2.s,p0/m,z29.s,z21.s
fmla z3.s,p0/m,z30.s,z21.s
fmla z4.s,p0/m,z29.s,z22.s
fmla z5.s,p0/m,z30.s,z22.s
incb x11, ALL, MUL #1
add x1,x1,#48
fmopa za0.s,p0/m,p0/m,z7.s,z31.s
fmopa za1.s,p0/m,p0/m,z7.s,z8.s
ld1w {z12.s}, p0/z, [x2, #4, MUL VL]
ld1w {z13.s}, p0/z, [x2, #5, MUL VL]
fmla z0.s,p0/m,z31.s,z23.s
fmla z1.s,p0/m,z8.s,z23.s
fmla z2.s,p0/m,z31.s,z24.s
fmla z3.s,p0/m,z8.s,z24.s
fmla z4.s,p0/m,z31.s,z25.s
fmla z5.s,p0/m,z8.s,z25.s
ld1rw {z26.s}, p0/z, [x11]
ld1rw {z27.s}, p0/z, [x11, #4]
ld1rw {z28.s}, p0/z, [x11, #8]
incb x1, ALL, MUL #4
fmopa za0.s,p0/m,p0/m,z19.s,z12.s
fmopa za1.s,p0/m,p0/m,z19.s,z13.s
fmla z0.s,p0/m,z12.s,z26.s
fmla z1.s,p0/m,z13.s,z26.s
fmla z2.s,p0/m,z12.s,z27.s
fmla z3.s,p0/m,z13.s,z27.s
fmla z4.s,p0/m,z12.s,z28.s
fmla z5.s,p0/m,z13.s,z28.s
incb x2, ALL, MUL #6
decb x1, ALL, MUL #1
.ukr7_done:
cbz x10,.ukr7_taildone
.ukr7_tail:
add x10,x10,#-1
mov x11,x1
incb x11, ALL, MUL #1
ld1w {z16.s}, p0/z, [x1]
ld1w {z17.s}, p0/z, [x2]
ld1w {z18.s}, p0/z, [x2, #1, MUL VL]
ld1rw {z9.s}, p0/z, [x11]
ld1rw {z10.s}, p0/z, [x11, #4]
ld1rw {z11.s}, p0/z, [x11, #8]
fmopa za0.s,p0/m,p0/m,z16.s,z17.s
fmopa za1.s,p0/m,p0/m,z16.s,z18.s
fmla z0.s,p0/m,z17.s,z9.s
fmla z1.s,p0/m,z18.s,z9.s
fmla z2.s,p0/m,z17.s,z10.s
fmla z3.s,p0/m,z18.s,z10.s
fmla z4.s,p0/m,z17.s,z11.s
fmla z5.s,p0/m,z18.s,z11.s
add x1,x1,#12
incb x1, ALL, MUL #1
incb x2, ALL, MUL #2
cbnz x10,.ukr7_tail
.ukr7_taildone:
ldr s6, [x5]
fmov s7,wzr
fcmp s6,s7
b.ne .ukr0_try0
ldr s6, [x4]
mov x0,#1065353216
fmov s7,w0
fcmp s6,s7
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr s6, [x5]
mov x0,#1065353216
fmov s7,w0
fcmp s6,s7
b.ne .ukr0_try2
ldr s6, [x4]
mov x0,#1065353216
fmov s7,w0
fcmp s6,s7
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr s6, [x4]
mov x0,#1065353216
fmov s7,w0
fcmp s6,s7
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
st1w {za0h.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
st1w {za0h.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
st1w {za0h.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
st1w {za0h.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr1_slices
st1w {z0.s}, p0, [x0]
st1w {z1.s}, p0, [x0, #1, MUL VL]
st1w {z2.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z3.s}, p0, [x0, #1, MUL VL]
st1w {z4.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z5.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
ld1rw {z6.s}, p0/z, [x4]
mov x1,x7
mov x12,#0
.ukr2_slices:
add x1,x1,#-4
mova z7.s,p0/m,za0h.s[w12,0]
mova z16.s,p0/m,za1h.s[w12,0]
fmul z17.s,z7.s,z6.s
fmul z18.s,z16.s,z6.s
st1w {z17.s}, p0, [x0]
st1w {z18.s}, p0, [x0, #1, MUL VL]
mova z19.s,p0/m,za0h.s[w12,1]
mova z20.s,p0/m,za1h.s[w12,1]
fmul z21.s,z19.s,z6.s
add x0,x0,x6
fmul z22.s,z20.s,z6.s
st1w {z21.s}, p0, [x0]
st1w {z22.s}, p0, [x0, #1, MUL VL]
mova z23.s,p0/m,za0h.s[w12,2]
mova z24.s,p0/m,za1h.s[w12,2]
fmul z25.s,z23.s,z6.s
add x0,x0,x6
fmul z26.s,z24.s,z6.s
st1w {z25.s}, p0, [x0]
st1w {z26.s}, p0, [x0, #1, MUL VL]
mova z27.s,p0/m,za0h.s[w12,3]
mova z28.s,p0/m,za1h.s[w12,3]
fmul z29.s,z27.s,z6.s
add x0,x0,x6
fmul z30.s,z28.s,z6.s
st1w {z29.s}, p0, [x0]
st1w {z30.s}, p0, [x0, #1, MUL VL]
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr2_slices
sub x0,x0,x8
fmul z7.s,z0.s,z6.s
add x0,x0,x8
fmul z0.s,z1.s,z6.s
fmul z1.s,z2.s,z6.s
st1w {z7.s}, p0, [x0]
st1w {z0.s}, p0, [x0, #1, MUL VL]
st1w {z1.s}, p0, [x0, x9, lsl #2]
fmul z0.s,z3.s,z6.s
add x0,x0,x6
fmul z1.s,z4.s,z6.s
st1w {z0.s}, p0, [x0, #1, MUL VL]
st1w {z1.s}, p0, [x0, x9, lsl #2]
fmul z0.s,z5.s,z6.s
add x0,x0,x6
st1w {z0.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
.ukr3_slices:
add x1,x1,#-4
mova z6.s,p0/m,za0h.s[w12,0]
ld1w {z7.s}, p0/z, [x0]
mova z16.s,p0/m,za1h.s[w12,0]
ld1w {z17.s}, p0/z, [x0, #1, MUL VL]
fadd z7.s,z6.s,z7.s
fadd z17.s,z16.s,z17.s
add x0,x0,x6
st1w {z7.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
mova z18.s,p0/m,za0h.s[w12,1]
ld1w {z19.s}, p0/z, [x0]
mova z20.s,p0/m,za1h.s[w12,1]
ld1w {z21.s}, p0/z, [x0, #1, MUL VL]
fadd z19.s,z18.s,z19.s
add x3,x3,x6
fadd z21.s,z20.s,z21.s
add x0,x0,x6
st1w {z19.s}, p0, [x3]
st1w {z21.s}, p0, [x3, #1, MUL VL]
mova z22.s,p0/m,za0h.s[w12,2]
ld1w {z23.s}, p0/z, [x0]
mova z24.s,p0/m,za1h.s[w12,2]
ld1w {z25.s}, p0/z, [x0, #1, MUL VL]
fadd z23.s,z22.s,z23.s
add x3,x3,x6
fadd z25.s,z24.s,z25.s
add x0,x0,x6
st1w {z23.s}, p0, [x3]
st1w {z25.s}, p0, [x3, #1, MUL VL]
mova z26.s,p0/m,za0h.s[w12,3]
ld1w {z27.s}, p0/z, [x0]
mova z28.s,p0/m,za1h.s[w12,3]
ld1w {z29.s}, p0/z, [x0, #1, MUL VL]
fadd z27.s,z26.s,z27.s
add x3,x3,x6
fadd z29.s,z28.s,z29.s
st1w {z27.s}, p0, [x3]
st1w {z29.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr3_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1w {z6.s}, p0/z, [x0]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
ld1w {z16.s}, p0/z, [x0, x9, lsl #2]
fadd z6.s,z0.s,z6.s
add x3,x3,x8
fadd z7.s,z1.s,z7.s
fadd z16.s,z2.s,z16.s
add x0,x0,x6
st1w {z6.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
st1w {z16.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fadd z0.s,z3.s,z0.s
add x3,x3,x6
fadd z1.s,z4.s,z1.s
add x0,x0,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z5.s,z0.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
ld1rw {z6.s}, p0/z, [x4]
mov x1,x7
mov x12,#0
.ukr4_slices:
add x1,x1,#-4
mova z7.s,p0/m,za0h.s[w12,0]
ld1w {z16.s}, p0/z, [x0]
mova z17.s,p0/m,za1h.s[w12,0]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
fmla z16.s,p0/m,z7.s,z6.s
fmla z18.s,p0/m,z17.s,z6.s
add x0,x0,x6
st1w {z16.s}, p0, [x3]
st1w {z18.s}, p0, [x3, #1, MUL VL]
mova z19.s,p0/m,za0h.s[w12,1]
ld1w {z20.s}, p0/z, [x0]
mova z21.s,p0/m,za1h.s[w12,1]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
fmla z20.s,p0/m,z19.s,z6.s
add x3,x3,x6
fmla z22.s,p0/m,z21.s,z6.s
add x0,x0,x6
st1w {z20.s}, p0, [x3]
st1w {z22.s}, p0, [x3, #1, MUL VL]
mova z23.s,p0/m,za0h.s[w12,2]
ld1w {z24.s}, p0/z, [x0]
mova z25.s,p0/m,za1h.s[w12,2]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
fmla z24.s,p0/m,z23.s,z6.s
add x3,x3,x6
fmla z26.s,p0/m,z25.s,z6.s
add x0,x0,x6
st1w {z24.s}, p0, [x3]
st1w {z26.s}, p0, [x3, #1, MUL VL]
mova z27.s,p0/m,za0h.s[w12,3]
ld1w {z28.s}, p0/z, [x0]
mova z29.s,p0/m,za1h.s[w12,3]
ld1w {z30.s}, p0/z, [x0, #1, MUL VL]
fmla z28.s,p0/m,z27.s,z6.s
add x3,x3,x6
fmla z30.s,p0/m,z29.s,z6.s
st1w {z28.s}, p0, [x3]
st1w {z30.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr4_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1w {z7.s}, p0/z, [x0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
ld1w {z17.s}, p0/z, [x0, x9, lsl #2]
fmla z7.s,p0/m,z0.s,z6.s
add x3,x3,x8
fmla z16.s,p0/m,z1.s,z6.s
fmla z17.s,p0/m,z2.s,z6.s
add x0,x0,x6
st1w {z7.s}, p0, [x3]
st1w {z16.s}, p0, [x3, #1, MUL VL]
st1w {z17.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z0.s,p0/m,z3.s,z6.s
add x3,x3,x6
fmla z1.s,p0/m,z4.s,z6.s
add x0,x0,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z5.s,z6.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
ld1rw {z6.s}, p0/z, [x5]
mov x1,x7
mov x12,#0
.ukr5_slices:
add x1,x1,#-4
mova z7.s,p0/m,za0h.s[w12,0]
ld1w {z16.s}, p0/z, [x0]
mova z17.s,p0/m,za1h.s[w12,0]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
fmla z7.s,p0/m,z16.s,z6.s
fmla z17.s,p0/m,z18.s,z6.s
mova za0h.s[w12,0],p0/m,z7.s
add x0,x0,x6
mova za1h.s[w12,0],p0/m,z17.s
mova z19.s,p0/m,za0h.s[w12,1]
ld1w {z20.s}, p0/z, [x0]
mova z21.s,p0/m,za1h.s[w12,1]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
fmla z19.s,p0/m,z20.s,z6.s
fmla z21.s,p0/m,z22.s,z6.s
st1w {z7.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,1],p0/m,z19.s
add x0,x0,x6
mova za1h.s[w12,1],p0/m,z21.s
add x3,x3,x6
mova z23.s,p0/m,za0h.s[w12,2]
ld1w {z24.s}, p0/z, [x0]
mova z25.s,p0/m,za1h.s[w12,2]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
st1w {z19.s}, p0, [x3]
st1w {z21.s}, p0, [x3, #1, MUL VL]
fmla z23.s,p0/m,z24.s,z6.s
fmla z25.s,p0/m,z26.s,z6.s
add x3,x3,x6
mova za0h.s[w12,2],p0/m,z23.s
add x0,x0,x6
mova za1h.s[w12,2],p0/m,z25.s
st1w {z23.s}, p0, [x3]
st1w {z25.s}, p0, [x3, #1, MUL VL]
mova z27.s,p0/m,za0h.s[w12,3]
ld1w {z28.s}, p0/z, [x0]
mova z29.s,p0/m,za1h.s[w12,3]
ld1w {z30.s}, p0/z, [x0, #1, MUL VL]
fmla z27.s,p0/m,z28.s,z6.s
fmla z29.s,p0/m,z30.s,z6.s
add x3,x3,x6
st1w {z27.s}, p0, [x3]
st1w {z29.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,3],p0/m,z27.s
mova za1h.s[w12,3],p0/m,z29.s
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr5_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1w {z7.s}, p0/z, [x0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
ld1w {z17.s}, p0/z, [x0, x9, lsl #2]
fmla z0.s,p0/m,z7.s,z6.s
add x3,x3,x8
fmla z1.s,p0/m,z16.s,z6.s
fmla z2.s,p0/m,z17.s,z6.s
add x0,x0,x6
st1w {z0.s}, p0, [x3]
st1w {z1.s}, p0, [x3, #1, MUL VL]
st1w {z2.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z3.s,p0/m,z0.s,z6.s
add x3,x3,x6
fmla z4.s,p0/m,z1.s,z6.s
add x0,x0,x6
st1w {z3.s}, p0, [x3, #1, MUL VL]
st1w {z4.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z5.s,p0/m,z0.s,z6.s
add x3,x3,x6
st1w {z5.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
ld1rw {z6.s}, p0/z, [x5]
ld1rw {z7.s}, p0/z, [x4]
mov x1,x7
mov x12,#0
.ukr6_slices:
add x1,x1,#-4
ld1w {z16.s}, p0/z, [x0]
ld1w {z17.s}, p0/z, [x0, #1, MUL VL]
fmul z16.s,z16.s,z6.s
mova z18.s,p0/m,za0h.s[w12,0]
fmul z17.s,z17.s,z6.s
mova z19.s,p0/m,za1h.s[w12,0]
add x0,x0,x6
fmla z16.s,p0/m,z18.s,z7.s
fmla z17.s,p0/m,z19.s,z7.s
ld1w {z20.s}, p0/z, [x0]
ld1w {z21.s}, p0/z, [x0, #1, MUL VL]
st1w {z16.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
fmul z20.s,z20.s,z6.s
mova z22.s,p0/m,za0h.s[w12,1]
fmul z21.s,z21.s,z6.s
mova z23.s,p0/m,za1h.s[w12,1]
add x0,x0,x6
fmla z20.s,p0/m,z22.s,z7.s
add x3,x3,x6
fmla z21.s,p0/m,z23.s,z7.s
ld1w {z24.s}, p0/z, [x0]
ld1w {z25.s}, p0/z, [x0, #1, MUL VL]
st1w {z20.s}, p0, [x3]
st1w {z21.s}, p0, [x3, #1, MUL VL]
fmul z24.s,z24.s,z6.s
mova z26.s,p0/m,za0h.s[w12,2]
fmul z25.s,z25.s,z6.s
mova z27.s,p0/m,za1h.s[w12,2]
add x0,x0,x6
fmla z24.s,p0/m,z26.s,z7.s
add x3,x3,x6
fmla z25.s,p0/m,z27.s,z7.s
ld1w {z28.s}, p0/z, [x0]
ld1w {z29.s}, p0/z, [x0, #1, MUL VL]
st1w {z24.s}, p0, [x3]
st1w {z25.s}, p0, [x3, #1, MUL VL]
fmul z28.s,z28.s,z6.s
mova z30.s,p0/m,za0h.s[w12,3]
fmul z29.s,z29.s,z6.s
mova z31.s,p0/m,za1h.s[w12,3]
fmla z28.s,p0/m,z30.s,z7.s
add x3,x3,x6
fmla z29.s,p0/m,z31.s,z7.s
st1w {z28.s}, p0, [x3]
st1w {z29.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr6_slices
sub x0,x0,x8
add x0,x0,x8
ld1w {z16.s}, p0/z, [x0]
ld1w {z17.s}, p0/z, [x0, #1, MUL VL]
ld1w {z18.s}, p0/z, [x0, x9, lsl #2]
sub x3,x3,x8
fmul z16.s,z16.s,z6.s
fmul z17.s,z17.s,z6.s
fmul z18.s,z18.s,z6.s
add x0,x0,x6
fmla z16.s,p0/m,z0.s,z7.s
add x3,x3,x8
fmla z17.s,p0/m,z1.s,z7.s
fmla z18.s,p0/m,z2.s,z7.s
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
st1w {z16.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
st1w {z18.s}, p0, [x3, x9, lsl #2]
fmul z0.s,z0.s,z6.s
fmul z1.s,z1.s,z6.s
add x0,x0,x6
fmla z0.s,p0/m,z3.s,z7.s
add x3,x3,x6
fmla z1.s,p0/m,z4.s,z7.s
ld1w {z2.s}, p0/z, [x0, #1, MUL VL]
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
fmul z2.s,z2.s,z6.s
fmla z2.s,p0/m,z5.s,z7.s
add x3,x3,x6
st1w {z2.s}, p0, [x3, #1, MUL VL]
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
.size bli_sgemm_ukrgen_sme_sf_1vx2v_3x2v_asm, .-bli_sgemm_ukrgen_sme_sf_1vx2v_3x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_sgemm_ukrgen_sme_sf_2vx2v_2x2v
.text
.global bli_sgemm_ukrgen_sme_sf_2vx2v_2x2v_asm
.type bli_sgemm_ukrgen_sme_sf_2vx2v_2x2v_asm, %function
bli_sgemm_ukrgen_sme_sf_2vx2v_2x2v_asm:
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
smstart
ptrue p0.s
cntw x7
mul x8,x7,x6
lsr x9,x6,#2
and x10,x0,#3
lsr x0,x0,#2
zero {za0.s}
zero {za1.s}
zero {za2.s}
zero {za3.s}
dup z0.s,#0
dup z1.s,#0
dup z2.s,#0
dup z3.s,#0
cbz x0,.ukr7_done
add x11,x1,#8
ld1w {z4.s}, p0/z, [x2]
ld1w {z5.s}, p0/z, [x2, #1, MUL VL]
ld1w {z6.s}, p0/z, [x1]
ld1w {z7.s}, p0/z, [x1, #1, MUL VL]
ld1w {z16.s}, p0/z, [x11, #2, MUL VL]
ld1w {z17.s}, p0/z, [x11, #3, MUL VL]
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x11,x1,#16
ld1w {z18.s}, p0/z, [x11, #4, MUL VL]
ld1w {z19.s}, p0/z, [x11, #5, MUL VL]
add x11,x11,#8
ld1w {z20.s}, p0/z, [x11, #6, MUL VL]
ld1w {z21.s}, p0/z, [x11, #7, MUL VL]
add x11,x11,#-24
incb x11, ALL, MUL #2
ld1rw {z22.s}, p0/z, [x11]
ld1rw {z23.s}, p0/z, [x11, #4]
add x11,x11,#8
incb x11, ALL, MUL #2
ld1rw {z24.s}, p0/z, [x11]
ld1rw {z25.s}, p0/z, [x11, #4]
add x11,x11,#8
incb x11, ALL, MUL #2
ld1rw {z26.s}, p0/z, [x11]
ld1rw {z27.s}, p0/z, [x11, #4]
add x11,x11,#8
incb x11, ALL, MUL #2
ld1rw {z28.s}, p0/z, [x11]
ld1rw {z29.s}, p0/z, [x11, #4]
fmopa za0.s,p0/m,p0/m,z6.s,z4.s
fmopa za1.s,p0/m,p0/m,z6.s,z5.s
fmopa za2.s,p0/m,p0/m,z7.s,z4.s
fmopa za3.s,p0/m,p0/m,z7.s,z5.s
add x11,x11,#8
ld1w {z30.s}, p0/z, [x2]
ld1w {z31.s}, p0/z, [x2, #1, MUL VL]
fmla z0.s,p0/m,z4.s,z22.s
fmla z1.s,p0/m,z5.s,z22.s
fmla z2.s,p0/m,z4.s,z23.s
fmla z3.s,p0/m,z5.s,z23.s
ld1w {z6.s}, p0/z, [x11]
ld1w {z7.s}, p0/z, [x11, #1, MUL VL]
fmopa za0.s,p0/m,p0/m,z16.s,z30.s
fmopa za1.s,p0/m,p0/m,z16.s,z31.s
fmopa za2.s,p0/m,p0/m,z17.s,z30.s
fmopa za3.s,p0/m,p0/m,z17.s,z31.s
ld1w {z8.s}, p0/z, [x2, #2, MUL VL]
ld1w {z9.s}, p0/z, [x2, #3, MUL VL]
fmla z0.s,p0/m,z30.s,z24.s
fmla z1.s,p0/m,z31.s,z24.s
fmla z2.s,p0/m,z30.s,z25.s
fmla z3.s,p0/m,z31.s,z25.s
add x11,x11,#8
fmopa za0.s,p0/m,p0/m,z18.s,z8.s
fmopa za1.s,p0/m,p0/m,z18.s,z9.s
fmopa za2.s,p0/m,p0/m,z19.s,z8.s
fmopa za3.s,p0/m,p0/m,z19.s,z9.s
ld1w {z10.s}, p0/z, [x2, #4, MUL VL]
ld1w {z11.s}, p0/z, [x2, #5, MUL VL]
fmla z0.s,p0/m,z8.s,z26.s
fmla z1.s,p0/m,z9.s,z26.s
fmla z2.s,p0/m,z8.s,z27.s
fmla z3.s,p0/m,z9.s,z27.s
incb x11, ALL, MUL #2
ld1w {z4.s}, p0/z, [x2, #6, MUL VL]
ld1w {z5.s}, p0/z, [x2, #7, MUL VL]
add x1,x1,#32
fmopa za0.s,p0/m,p0/m,z20.s,z10.s
fmopa za1.s,p0/m,p0/m,z20.s,z11.s
fmopa za2.s,p0/m,p0/m,z21.s,z10.s
fmopa za3.s,p0/m,p0/m,z21.s,z11.s
fmla z0.s,p0/m,z10.s,z28.s
fmla z1.s,p0/m,z11.s,z28.s
fmla z2.s,p0/m,z10.s,z29.s
fmla z3.s,p0/m,z11.s,z29.s
ld1w {z16.s}, p0/z, [x11]
ld1w {z17.s}, p0/z, [x11, #1, MUL VL]
incb x1, ALL, MUL #8
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x11,x1,#16
ld1w {z18.s}, p0/z, [x11, #4, MUL VL]
ld1w {z19.s}, p0/z, [x11, #5, MUL VL]
add x11,x11,#8
ld1w {z20.s}, p0/z, [x11, #6, MUL VL]
ld1w {z21.s}, p0/z, [x11, #7, MUL VL]
add x11,x11,#-24
incb x11, ALL, MUL #2
ld1rw {z22.s}, p0/z, [x11]
ld1rw {z23.s}, p0/z, [x11, #4]
add x11,x11,#8
incb x11, ALL, MUL #2
ld1rw {z24.s}, p0/z, [x11]
ld1rw {z25.s}, p0/z, [x11, #4]
add x11,x11,#8
incb x11, ALL, MUL #2
ld1rw {z26.s}, p0/z, [x11]
ld1rw {z27.s}, p0/z, [x11, #4]
fmopa za0.s,p0/m,p0/m,z6.s,z4.s
fmopa za1.s,p0/m,p0/m,z6.s,z5.s
fmopa za2.s,p0/m,p0/m,z7.s,z4.s
fmopa za3.s,p0/m,p0/m,z7.s,z5.s
ld1w {z30.s}, p0/z, [x2]
ld1w {z31.s}, p0/z, [x2, #1, MUL VL]
fmla z0.s,p0/m,z4.s,z22.s
fmla z1.s,p0/m,z5.s,z22.s
fmla z2.s,p0/m,z4.s,z23.s
fmla z3.s,p0/m,z5.s,z23.s
add x11,x11,#8
fmopa za0.s,p0/m,p0/m,z16.s,z30.s
fmopa za1.s,p0/m,p0/m,z16.s,z31.s
fmopa za2.s,p0/m,p0/m,z17.s,z30.s
fmopa za3.s,p0/m,p0/m,z17.s,z31.s
ld1w {z8.s}, p0/z, [x2, #2, MUL VL]
ld1w {z9.s}, p0/z, [x2, #3, MUL VL]
fmla z0.s,p0/m,z30.s,z24.s
fmla z1.s,p0/m,z31.s,z24.s
fmla z2.s,p0/m,z30.s,z25.s
fmla z3.s,p0/m,z31.s,z25.s
incb x11, ALL, MUL #2
fmopa za0.s,p0/m,p0/m,z18.s,z8.s
fmopa za1.s,p0/m,p0/m,z18.s,z9.s
fmopa za2.s,p0/m,p0/m,z19.s,z8.s
fmopa za3.s,p0/m,p0/m,z19.s,z9.s
ld1w {z10.s}, p0/z, [x2, #4, MUL VL]
ld1w {z11.s}, p0/z, [x2, #5, MUL VL]
fmla z0.s,p0/m,z8.s,z26.s
fmla z1.s,p0/m,z9.s,z26.s
fmla z2.s,p0/m,z8.s,z27.s
fmla z3.s,p0/m,z9.s,z27.s
ld1rw {z28.s}, p0/z, [x11]
ld1rw {z29.s}, p0/z, [x11, #4]
add x1,x1,#32
fmopa za0.s,p0/m,p0/m,z20.s,z10.s
fmopa za1.s,p0/m,p0/m,z20.s,z11.s
fmopa za2.s,p0/m,p0/m,z21.s,z10.s
fmopa za3.s,p0/m,p0/m,z21.s,z11.s
fmla z0.s,p0/m,z10.s,z28.s
fmla z1.s,p0/m,z11.s,z28.s
fmla z2.s,p0/m,z10.s,z29.s
fmla z3.s,p0/m,z11.s,z29.s
incb x1, ALL, MUL #8
incb x2, ALL, MUL #6
.ukr7_done:
cbz x10,.ukr7_taildone
.ukr7_tail:
add x10,x10,#-1
mov x11,x1
incb x11, ALL, MUL #2
ld1w {z6.s}, p0/z, [x1]
ld1w {z4.s}, p0/z, [x2]
ld1w {z5.s}, p0/z, [x2, #1, MUL VL]
ld1w {z7.s}, p0/z, [x1, #1, MUL VL]
ld1rw {z22.s}, p0/z, [x11]
ld1rw {z23.s}, p0/z, [x11, #4]
fmopa za0.s,p0/m,p0/m,z6.s,z4.s
fmopa za1.s,p0/m,p0/m,z6.s,z5.s
fmopa za2.s,p0/m,p0/m,z7.s,z4.s
fmopa za3.s,p0/m,p0/m,z7.s,z5.s
fmla z0.s,p0/m,z4.s,z22.s
fmla z1.s,p0/m,z5.s,z22.s
fmla z2.s,p0/m,z4.s,z23.s
fmla z3.s,p0/m,z5.s,z23.s
add x1,x1,#8
incb x1, ALL, MUL #2
incb x2, ALL, MUL #2
cbnz x10,.ukr7_tail
.ukr7_taildone:
ldr s4, [x5]
fmov s5,wzr
fcmp s4,s5
b.ne .ukr0_try0
ldr s4, [x4]
mov x0,#1065353216
fmov s5,w0
fcmp s4,s5
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr s4, [x5]
mov x0,#1065353216
fmov s5,w0
fcmp s4,s5
b.ne .ukr0_try2
ldr s4, [x4]
mov x0,#1065353216
fmov s5,w0
fcmp s4,s5
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr s4, [x4]
mov x0,#1065353216
fmov s5,w0
fcmp s4,s5
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
st1w {za0h.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr1_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1w {z0.s}, p0, [x0]
st1w {z1.s}, p0, [x0, #1, MUL VL]
st1w {z2.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z3.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z4.s}, p0/z, [x4]
.ukr2_slices:
add x1,x1,#-4
mova z5.s,p0/m,za0h.s[w12,0]
mova z6.s,p0/m,za1h.s[w12,0]
fmul z7.s,z5.s,z4.s
fmul z16.s,z6.s,z4.s
st1w {z7.s}, p0, [x0]
st1w {z16.s}, p0, [x0, #1, MUL VL]
mova z17.s,p0/m,za2h.s[w12,0]
mova z18.s,p0/m,za3h.s[w12,0]
fmul z19.s,z17.s,z4.s
add x0,x0,x8
fmul z20.s,z18.s,z4.s
st1w {z19.s}, p0, [x0]
st1w {z20.s}, p0, [x0, #1, MUL VL]
mova z21.s,p0/m,za0h.s[w12,1]
sub x0,x0,x8
mova z22.s,p0/m,za1h.s[w12,1]
fmul z23.s,z21.s,z4.s
add x0,x0,x6
fmul z24.s,z22.s,z4.s
st1w {z23.s}, p0, [x0]
st1w {z24.s}, p0, [x0, #1, MUL VL]
mova z25.s,p0/m,za2h.s[w12,1]
mova z26.s,p0/m,za3h.s[w12,1]
fmul z27.s,z25.s,z4.s
add x0,x0,x8
fmul z28.s,z26.s,z4.s
st1w {z27.s}, p0, [x0]
st1w {z28.s}, p0, [x0, #1, MUL VL]
mova z29.s,p0/m,za0h.s[w12,2]
sub x0,x0,x8
mova z30.s,p0/m,za1h.s[w12,2]
fmul z31.s,z29.s,z4.s
add x0,x0,x6
fmul z8.s,z30.s,z4.s
st1w {z31.s}, p0, [x0]
st1w {z8.s}, p0, [x0, #1, MUL VL]
mova z9.s,p0/m,za2h.s[w12,2]
mova z10.s,p0/m,za3h.s[w12,2]
fmul z11.s,z9.s,z4.s
add x0,x0,x8
fmul z12.s,z10.s,z4.s
st1w {z11.s}, p0, [x0]
st1w {z12.s}, p0, [x0, #1, MUL VL]
mova z13.s,p0/m,za0h.s[w12,3]
sub x0,x0,x8
mova z14.s,p0/m,za1h.s[w12,3]
fmul z15.s,z13.s,z4.s
add x0,x0,x6
fmul z7.s,z14.s,z4.s
st1w {z15.s}, p0, [x0]
st1w {z7.s}, p0, [x0, #1, MUL VL]
mova z5.s,p0/m,za2h.s[w12,3]
mova z6.s,p0/m,za3h.s[w12,3]
fmul z16.s,z5.s,z4.s
add x0,x0,x8
fmul z19.s,z6.s,z4.s
st1w {z16.s}, p0, [x0]
st1w {z19.s}, p0, [x0, #1, MUL VL]
sub x0,x0,x8
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr2_slices
fmul z5.s,z0.s,z4.s
fmul z0.s,z1.s,z4.s
fmul z1.s,z2.s,z4.s
fmul z2.s,z3.s,z4.s
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1w {z5.s}, p0, [x0]
st1w {z0.s}, p0, [x0, #1, MUL VL]
st1w {z1.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z2.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
.ukr3_slices:
add x1,x1,#-4
mova z4.s,p0/m,za0h.s[w12,0]
ld1w {z5.s}, p0/z, [x0]
mova z6.s,p0/m,za1h.s[w12,0]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
fadd z5.s,z4.s,z5.s
fadd z7.s,z6.s,z7.s
add x0,x0,x8
st1w {z5.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
mova z16.s,p0/m,za2h.s[w12,0]
ld1w {z17.s}, p0/z, [x0]
mova z18.s,p0/m,za3h.s[w12,0]
ld1w {z19.s}, p0/z, [x0, #1, MUL VL]
fadd z17.s,z16.s,z17.s
add x3,x3,x8
fadd z19.s,z18.s,z19.s
sub x0,x0,x8
st1w {z17.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z20.s,p0/m,za0h.s[w12,1]
ld1w {z21.s}, p0/z, [x0]
sub x3,x3,x8
mova z22.s,p0/m,za1h.s[w12,1]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
fadd z21.s,z20.s,z21.s
add x3,x3,x6
fadd z23.s,z22.s,z23.s
add x0,x0,x8
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
mova z24.s,p0/m,za2h.s[w12,1]
ld1w {z25.s}, p0/z, [x0]
mova z26.s,p0/m,za3h.s[w12,1]
ld1w {z27.s}, p0/z, [x0, #1, MUL VL]
fadd z25.s,z24.s,z25.s
add x3,x3,x8
fadd z27.s,z26.s,z27.s
sub x0,x0,x8
st1w {z25.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z28.s,p0/m,za0h.s[w12,2]
ld1w {z29.s}, p0/z, [x0]
sub x3,x3,x8
mova z30.s,p0/m,za1h.s[w12,2]
ld1w {z31.s}, p0/z, [x0, #1, MUL VL]
fadd z29.s,z28.s,z29.s
add x3,x3,x6
fadd z31.s,z30.s,z31.s
add x0,x0,x8
st1w {z29.s}, p0, [x3]
st1w {z31.s}, p0, [x3, #1, MUL VL]
mova z8.s,p0/m,za2h.s[w12,2]
ld1w {z9.s}, p0/z, [x0]
mova z10.s,p0/m,za3h.s[w12,2]
ld1w {z11.s}, p0/z, [x0, #1, MUL VL]
fadd z9.s,z8.s,z9.s
add x3,x3,x8
fadd z11.s,z10.s,z11.s
sub x0,x0,x8
st1w {z9.s}, p0, [x3]
st1w {z11.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z12.s,p0/m,za0h.s[w12,3]
ld1w {z13.s}, p0/z, [x0]
sub x3,x3,x8
mova z14.s,p0/m,za1h.s[w12,3]
ld1w {z15.s}, p0/z, [x0, #1, MUL VL]
fadd z13.s,z12.s,z13.s
add x3,x3,x6
fadd z15.s,z14.s,z15.s
add x0,x0,x8
st1w {z13.s}, p0, [x3]
st1w {z15.s}, p0, [x3, #1, MUL VL]
mova z4.s,p0/m,za2h.s[w12,3]
ld1w {z5.s}, p0/z, [x0]
mova z6.s,p0/m,za3h.s[w12,3]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
fadd z5.s,z4.s,z5.s
add x3,x3,x8
fadd z7.s,z6.s,z7.s
st1w {z5.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr3_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z4.s}, p0/z, [x0]
fadd z4.s,z0.s,z4.s
mov x3,x0
st1w {z4.s}, p0, [x3]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z1.s,z0.s
st1w {z0.s}, p0, [x3, #1, MUL VL]
ld1w {z0.s}, p0/z, [x0, x9, lsl #2]
fadd z0.s,z2.s,z0.s
st1w {z0.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z3.s,z0.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z4.s}, p0/z, [x4]
.ukr4_slices:
add x1,x1,#-4
mova z5.s,p0/m,za0h.s[w12,0]
ld1w {z6.s}, p0/z, [x0]
mova z7.s,p0/m,za1h.s[w12,0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
fmla z6.s,p0/m,z5.s,z4.s
fmla z16.s,p0/m,z7.s,z4.s
add x0,x0,x8
st1w {z6.s}, p0, [x3]
st1w {z16.s}, p0, [x3, #1, MUL VL]
mova z17.s,p0/m,za2h.s[w12,0]
ld1w {z18.s}, p0/z, [x0]
mova z19.s,p0/m,za3h.s[w12,0]
ld1w {z20.s}, p0/z, [x0, #1, MUL VL]
fmla z18.s,p0/m,z17.s,z4.s
add x3,x3,x8
fmla z20.s,p0/m,z19.s,z4.s
sub x0,x0,x8
st1w {z18.s}, p0, [x3]
st1w {z20.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z21.s,p0/m,za0h.s[w12,1]
ld1w {z22.s}, p0/z, [x0]
sub x3,x3,x8
mova z23.s,p0/m,za1h.s[w12,1]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
fmla z22.s,p0/m,z21.s,z4.s
add x3,x3,x6
fmla z24.s,p0/m,z23.s,z4.s
add x0,x0,x8
st1w {z22.s}, p0, [x3]
st1w {z24.s}, p0, [x3, #1, MUL VL]
mova z25.s,p0/m,za2h.s[w12,1]
ld1w {z26.s}, p0/z, [x0]
mova z27.s,p0/m,za3h.s[w12,1]
ld1w {z28.s}, p0/z, [x0, #1, MUL VL]
fmla z26.s,p0/m,z25.s,z4.s
add x3,x3,x8
fmla z28.s,p0/m,z27.s,z4.s
sub x0,x0,x8
st1w {z26.s}, p0, [x3]
st1w {z28.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z29.s,p0/m,za0h.s[w12,2]
ld1w {z30.s}, p0/z, [x0]
sub x3,x3,x8
mova z31.s,p0/m,za1h.s[w12,2]
ld1w {z8.s}, p0/z, [x0, #1, MUL VL]
fmla z30.s,p0/m,z29.s,z4.s
add x3,x3,x6
fmla z8.s,p0/m,z31.s,z4.s
add x0,x0,x8
st1w {z30.s}, p0, [x3]
st1w {z8.s}, p0, [x3, #1, MUL VL]
mova z9.s,p0/m,za2h.s[w12,2]
ld1w {z10.s}, p0/z, [x0]
mova z11.s,p0/m,za3h.s[w12,2]
ld1w {z12.s}, p0/z, [x0, #1, MUL VL]
fmla z10.s,p0/m,z9.s,z4.s
add x3,x3,x8
fmla z12.s,p0/m,z11.s,z4.s
sub x0,x0,x8
st1w {z10.s}, p0, [x3]
st1w {z12.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z13.s,p0/m,za0h.s[w12,3]
ld1w {z14.s}, p0/z, [x0]
sub x3,x3,x8
mova z15.s,p0/m,za1h.s[w12,3]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
fmla z14.s,p0/m,z13.s,z4.s
add x3,x3,x6
fmla z6.s,p0/m,z15.s,z4.s
add x0,x0,x8
st1w {z14.s}, p0, [x3]
st1w {z6.s}, p0, [x3, #1, MUL VL]
mova z5.s,p0/m,za2h.s[w12,3]
ld1w {z16.s}, p0/z, [x0]
mova z7.s,p0/m,za3h.s[w12,3]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
fmla z16.s,p0/m,z5.s,z4.s
add x3,x3,x8
fmla z18.s,p0/m,z7.s,z4.s
st1w {z16.s}, p0, [x3]
st1w {z18.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr4_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z5.s}, p0/z, [x0]
fmla z5.s,p0/m,z0.s,z4.s
mov x3,x0
st1w {z5.s}, p0, [x3]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z1.s,z4.s
st1w {z0.s}, p0, [x3, #1, MUL VL]
ld1w {z0.s}, p0/z, [x0, x9, lsl #2]
fmla z0.s,p0/m,z2.s,z4.s
st1w {z0.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z3.s,z4.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z4.s}, p0/z, [x5]
.ukr5_slices:
add x1,x1,#-4
mova z5.s,p0/m,za0h.s[w12,0]
ld1w {z6.s}, p0/z, [x0]
mova z7.s,p0/m,za1h.s[w12,0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
fmla z5.s,p0/m,z6.s,z4.s
fmla z7.s,p0/m,z16.s,z4.s
add x0,x0,x8
st1w {z5.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
mova z17.s,p0/m,za2h.s[w12,0]
ld1w {z18.s}, p0/z, [x0]
mova z19.s,p0/m,za3h.s[w12,0]
ld1w {z20.s}, p0/z, [x0, #1, MUL VL]
fmla z17.s,p0/m,z18.s,z4.s
add x3,x3,x8
fmla z19.s,p0/m,z20.s,z4.s
sub x0,x0,x8
st1w {z17.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,0],p0/m,z5.s
add x0,x0,x6
mova za1h.s[w12,0],p0/m,z7.s
mova z21.s,p0/m,za0h.s[w12,1]
ld1w {z22.s}, p0/z, [x0]
sub x3,x3,x8
mova z23.s,p0/m,za1h.s[w12,1]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
fmla z21.s,p0/m,z22.s,z4.s
add x3,x3,x6
fmla z23.s,p0/m,z24.s,z4.s
mova za2h.s[w12,0],p0/m,z17.s
add x0,x0,x8
mova za3h.s[w12,0],p0/m,z19.s
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
mova z25.s,p0/m,za2h.s[w12,1]
ld1w {z26.s}, p0/z, [x0]
mova z27.s,p0/m,za3h.s[w12,1]
ld1w {z28.s}, p0/z, [x0, #1, MUL VL]
fmla z25.s,p0/m,z26.s,z4.s
add x3,x3,x8
fmla z27.s,p0/m,z28.s,z4.s
sub x0,x0,x8
st1w {z25.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,1],p0/m,z21.s
add x0,x0,x6
mova za1h.s[w12,1],p0/m,z23.s
mova z29.s,p0/m,za0h.s[w12,2]
ld1w {z30.s}, p0/z, [x0]
sub x3,x3,x8
mova z31.s,p0/m,za1h.s[w12,2]
ld1w {z8.s}, p0/z, [x0, #1, MUL VL]
fmla z29.s,p0/m,z30.s,z4.s
add x3,x3,x6
fmla z31.s,p0/m,z8.s,z4.s
mova za2h.s[w12,1],p0/m,z25.s
add x0,x0,x8
mova za3h.s[w12,1],p0/m,z27.s
st1w {z29.s}, p0, [x3]
st1w {z31.s}, p0, [x3, #1, MUL VL]
mova z9.s,p0/m,za2h.s[w12,2]
ld1w {z10.s}, p0/z, [x0]
mova z11.s,p0/m,za3h.s[w12,2]
ld1w {z12.s}, p0/z, [x0, #1, MUL VL]
fmla z9.s,p0/m,z10.s,z4.s
add x3,x3,x8
fmla z11.s,p0/m,z12.s,z4.s
sub x0,x0,x8
st1w {z9.s}, p0, [x3]
st1w {z11.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,2],p0/m,z29.s
add x0,x0,x6
mova za1h.s[w12,2],p0/m,z31.s
mova z13.s,p0/m,za0h.s[w12,3]
ld1w {z14.s}, p0/z, [x0]
mova z15.s,p0/m,za1h.s[w12,3]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
sub x3,x3,x8
fmla z13.s,p0/m,z14.s,z4.s
fmla z15.s,p0/m,z6.s,z4.s
mova za2h.s[w12,2],p0/m,z9.s
add x0,x0,x8
mova za3h.s[w12,2],p0/m,z11.s
add x3,x3,x6
mova z5.s,p0/m,za2h.s[w12,3]
ld1w {z16.s}, p0/z, [x0]
mova z7.s,p0/m,za3h.s[w12,3]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
st1w {z13.s}, p0, [x3]
st1w {z15.s}, p0, [x3, #1, MUL VL]
fmla z5.s,p0/m,z16.s,z4.s
fmla z7.s,p0/m,z18.s,z4.s
add x3,x3,x8
st1w {z5.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
mova za0h.s[w12,3],p0/m,z13.s
mova za1h.s[w12,3],p0/m,z15.s
mova za2h.s[w12,3],p0/m,z5.s
mova za3h.s[w12,3],p0/m,z7.s
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr5_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z5.s}, p0/z, [x0]
mov x3,x0
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
ld1w {z7.s}, p0/z, [x0, x9, lsl #2]
fmla z0.s,p0/m,z5.s,z4.s
st1w {z0.s}, p0, [x3]
fmla z1.s,p0/m,z6.s,z4.s
st1w {z1.s}, p0, [x3, #1, MUL VL]
fmla z2.s,p0/m,z7.s,z4.s
st1w {z2.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z3.s,p0/m,z0.s,z4.s
add x3,x3,x6
st1w {z3.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z4.s}, p0/z, [x5]
ld1rw {z5.s}, p0/z, [x4]
.ukr6_slices:
add x1,x1,#-4
ld1w {z6.s}, p0/z, [x0]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
fmul z6.s,z6.s,z4.s
mova z16.s,p0/m,za0h.s[w12,0]
fmul z7.s,z7.s,z4.s
mova z17.s,p0/m,za1h.s[w12,0]
add x0,x0,x8
fmla z6.s,p0/m,z16.s,z5.s
fmla z7.s,p0/m,z17.s,z5.s
ld1w {z18.s}, p0/z, [x0]
ld1w {z19.s}, p0/z, [x0, #1, MUL VL]
st1w {z6.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
fmul z18.s,z18.s,z4.s
mova z20.s,p0/m,za2h.s[w12,0]
fmul z19.s,z19.s,z4.s
mova z21.s,p0/m,za3h.s[w12,0]
sub x0,x0,x8
fmla z18.s,p0/m,z20.s,z5.s
add x3,x3,x8
fmla z19.s,p0/m,z21.s,z5.s
add x0,x0,x6
st1w {z18.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
ld1w {z22.s}, p0/z, [x0]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
fmul z22.s,z22.s,z4.s
mova z24.s,p0/m,za0h.s[w12,1]
sub x3,x3,x8
fmul z23.s,z23.s,z4.s
mova z25.s,p0/m,za1h.s[w12,1]
add x0,x0,x8
fmla z22.s,p0/m,z24.s,z5.s
add x3,x3,x6
fmla z23.s,p0/m,z25.s,z5.s
ld1w {z26.s}, p0/z, [x0]
ld1w {z27.s}, p0/z, [x0, #1, MUL VL]
st1w {z22.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
fmul z26.s,z26.s,z4.s
mova z28.s,p0/m,za2h.s[w12,1]
fmul z27.s,z27.s,z4.s
mova z29.s,p0/m,za3h.s[w12,1]
sub x0,x0,x8
fmla z26.s,p0/m,z28.s,z5.s
add x3,x3,x8
fmla z27.s,p0/m,z29.s,z5.s
add x0,x0,x6
st1w {z26.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
ld1w {z30.s}, p0/z, [x0]
ld1w {z31.s}, p0/z, [x0, #1, MUL VL]
fmul z30.s,z30.s,z4.s
mova z8.s,p0/m,za0h.s[w12,2]
sub x3,x3,x8
fmul z31.s,z31.s,z4.s
mova z9.s,p0/m,za1h.s[w12,2]
add x0,x0,x8
fmla z30.s,p0/m,z8.s,z5.s
add x3,x3,x6
fmla z31.s,p0/m,z9.s,z5.s
ld1w {z10.s}, p0/z, [x0]
ld1w {z11.s}, p0/z, [x0, #1, MUL VL]
st1w {z30.s}, p0, [x3]
st1w {z31.s}, p0, [x3, #1, MUL VL]
fmul z10.s,z10.s,z4.s
mova z12.s,p0/m,za2h.s[w12,2]
fmul z11.s,z11.s,z4.s
mova z13.s,p0/m,za3h.s[w12,2]
sub x0,x0,x8
fmla z10.s,p0/m,z12.s,z5.s
add x3,x3,x8
fmla z11.s,p0/m,z13.s,z5.s
add x0,x0,x6
st1w {z10.s}, p0, [x3]
st1w {z11.s}, p0, [x3, #1, MUL VL]
ld1w {z14.s}, p0/z, [x0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
fmul z14.s,z14.s,z4.s
mova z15.s,p0/m,za0h.s[w12,3]
sub x3,x3,x8
fmul z6.s,z6.s,z4.s
mova z16.s,p0/m,za1h.s[w12,3]
add x0,x0,x8
fmla z14.s,p0/m,z15.s,z5.s
add x3,x3,x6
fmla z6.s,p0/m,z16.s,z5.s
ld1w {z7.s}, p0/z, [x0]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
st1w {z14.s}, p0, [x3]
st1w {z6.s}, p0, [x3, #1, MUL VL]
fmul z7.s,z7.s,z4.s
mova z17.s,p0/m,za2h.s[w12,3]
fmul z18.s,z18.s,z4.s
mova z20.s,p0/m,za3h.s[w12,3]
fmla z7.s,p0/m,z17.s,z5.s
add x3,x3,x8
fmla z18.s,p0/m,z20.s,z5.s
st1w {z7.s}, p0, [x3]
st1w {z18.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr6_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z6.s}, p0/z, [x0]
mov x3,x0
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
ld1w {z16.s}, p0/z, [x0, x9, lsl #2]
fmul z6.s,z6.s,z4.s
fmla z6.s,p0/m,z0.s,z5.s
st1w {z6.s}, p0, [x3]
fmul z7.s,z7.s,z4.s
fmla z7.s,p0/m,z1.s,z5.s
st1w {z7.s}, p0, [x3, #1, MUL VL]
fmul z16.s,z16.s,z4.s
fmla z16.s,p0/m,z2.s,z5.s
st1w {z16.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmul z0.s,z0.s,z4.s
fmla z0.s,p0/m,z3.s,z5.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
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
.size bli_sgemm_ukrgen_sme_sf_2vx2v_2x2v_asm, .-bli_sgemm_ukrgen_sme_sf_2vx2v_2x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_sgemm_ukrgen_sme_sf_2vx2v_4x2v
.text
.global bli_sgemm_ukrgen_sme_sf_2vx2v_4x2v_asm
.type bli_sgemm_ukrgen_sme_sf_2vx2v_4x2v_asm, %function
bli_sgemm_ukrgen_sme_sf_2vx2v_4x2v_asm:
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
smstart
ptrue p0.s
cntw x7
mul x8,x7,x6
lsr x9,x6,#2
and x10,x0,#3
lsr x0,x0,#2
zero {za0.s}
zero {za1.s}
zero {za2.s}
zero {za3.s}
dup z0.s,#0
dup z1.s,#0
dup z2.s,#0
dup z3.s,#0
dup z4.s,#0
dup z5.s,#0
dup z6.s,#0
dup z7.s,#0
cbz x0,.ukr7_done
add x11,x1,#16
ld1w {z16.s}, p0/z, [x11, #2, MUL VL]
ld1w {z17.s}, p0/z, [x11, #3, MUL VL]
add x11,x11,#16
ld1w {z18.s}, p0/z, [x2]
ld1w {z19.s}, p0/z, [x2, #1, MUL VL]
ld1w {z20.s}, p0/z, [x1]
ld1w {z21.s}, p0/z, [x1, #1, MUL VL]
ld1w {z22.s}, p0/z, [x11, #4, MUL VL]
ld1w {z23.s}, p0/z, [x11, #5, MUL VL]
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x11,x1,#48
ld1w {z24.s}, p0/z, [x11, #6, MUL VL]
ld1w {z25.s}, p0/z, [x11, #7, MUL VL]
add x11,x11,#-48
incb x11, ALL, MUL #2
ld1rw {z26.s}, p0/z, [x11]
ld1rw {z27.s}, p0/z, [x11, #4]
ld1rw {z28.s}, p0/z, [x11, #8]
ld1rw {z29.s}, p0/z, [x11, #12]
fmopa za0.s,p0/m,p0/m,z20.s,z18.s
fmopa za1.s,p0/m,p0/m,z20.s,z19.s
fmopa za2.s,p0/m,p0/m,z21.s,z18.s
fmopa za3.s,p0/m,p0/m,z21.s,z19.s
ld1w {z30.s}, p0/z, [x2]
ld1w {z31.s}, p0/z, [x2, #1, MUL VL]
add x11,x11,#16
fmopa za0.s,p0/m,p0/m,z16.s,z30.s
fmopa za1.s,p0/m,p0/m,z16.s,z31.s
fmopa za2.s,p0/m,p0/m,z17.s,z30.s
fmopa za3.s,p0/m,p0/m,z17.s,z31.s
incb x11, ALL, MUL #2
ld1w {z8.s}, p0/z, [x2, #2, MUL VL]
ld1w {z9.s}, p0/z, [x2, #3, MUL VL]
ld1rw {z20.s}, p0/z, [x11]
ld1rw {z21.s}, p0/z, [x11, #4]
ld1rw {z16.s}, p0/z, [x11, #8]
ld1rw {z17.s}, p0/z, [x11, #12]
fmopa za0.s,p0/m,p0/m,z22.s,z8.s
fmopa za1.s,p0/m,p0/m,z22.s,z9.s
fmopa za2.s,p0/m,p0/m,z23.s,z8.s
fmopa za3.s,p0/m,p0/m,z23.s,z9.s
ld1w {z10.s}, p0/z, [x2, #4, MUL VL]
ld1w {z11.s}, p0/z, [x2, #5, MUL VL]
add x11,x11,#16
fmopa za0.s,p0/m,p0/m,z24.s,z10.s
fmopa za1.s,p0/m,p0/m,z24.s,z11.s
fmopa za2.s,p0/m,p0/m,z25.s,z10.s
fmopa za3.s,p0/m,p0/m,z25.s,z11.s
incb x11, ALL, MUL #2
ld1rw {z22.s}, p0/z, [x11]
ld1rw {z23.s}, p0/z, [x11, #4]
ld1rw {z24.s}, p0/z, [x11, #8]
ld1rw {z25.s}, p0/z, [x11, #12]
add x11,x11,#16
fmla z0.s,p0/m,z18.s,z26.s
fmla z1.s,p0/m,z19.s,z26.s
fmla z2.s,p0/m,z18.s,z27.s
fmla z3.s,p0/m,z19.s,z27.s
fmla z4.s,p0/m,z18.s,z28.s
fmla z5.s,p0/m,z19.s,z28.s
fmla z6.s,p0/m,z18.s,z29.s
fmla z7.s,p0/m,z19.s,z29.s
incb x11, ALL, MUL #2
ld1rw {z26.s}, p0/z, [x11]
ld1rw {z27.s}, p0/z, [x11, #4]
ld1rw {z28.s}, p0/z, [x11, #8]
ld1rw {z29.s}, p0/z, [x11, #12]
fmla z0.s,p0/m,z30.s,z20.s
fmla z1.s,p0/m,z31.s,z20.s
fmla z2.s,p0/m,z30.s,z21.s
fmla z3.s,p0/m,z31.s,z21.s
add x11,x11,#16
ld1w {z20.s}, p0/z, [x11]
ld1w {z21.s}, p0/z, [x11, #1, MUL VL]
add x11,x11,#16
fmla z4.s,p0/m,z30.s,z16.s
fmla z5.s,p0/m,z31.s,z16.s
fmla z6.s,p0/m,z30.s,z17.s
fmla z7.s,p0/m,z31.s,z17.s
incb x11, ALL, MUL #2
ld1w {z16.s}, p0/z, [x11]
ld1w {z17.s}, p0/z, [x11, #1, MUL VL]
add x11,x11,#16
fmla z0.s,p0/m,z8.s,z22.s
fmla z1.s,p0/m,z9.s,z22.s
fmla z2.s,p0/m,z8.s,z23.s
fmla z3.s,p0/m,z9.s,z23.s
fmla z4.s,p0/m,z8.s,z24.s
fmla z5.s,p0/m,z9.s,z24.s
fmla z6.s,p0/m,z8.s,z25.s
fmla z7.s,p0/m,z9.s,z25.s
incb x11, ALL, MUL #2
ld1w {z18.s}, p0/z, [x2, #6, MUL VL]
ld1w {z19.s}, p0/z, [x2, #7, MUL VL]
add x1,x1,#64
fmla z0.s,p0/m,z10.s,z26.s
fmla z1.s,p0/m,z11.s,z26.s
fmla z2.s,p0/m,z10.s,z27.s
fmla z3.s,p0/m,z11.s,z27.s
fmla z4.s,p0/m,z10.s,z28.s
fmla z5.s,p0/m,z11.s,z28.s
fmla z6.s,p0/m,z10.s,z29.s
fmla z7.s,p0/m,z11.s,z29.s
ld1w {z22.s}, p0/z, [x11]
ld1w {z23.s}, p0/z, [x11, #1, MUL VL]
incb x1, ALL, MUL #8
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x11,x1,#48
ld1w {z24.s}, p0/z, [x11, #6, MUL VL]
ld1w {z25.s}, p0/z, [x11, #7, MUL VL]
add x11,x11,#-48
incb x11, ALL, MUL #2
ld1rw {z26.s}, p0/z, [x11]
ld1rw {z27.s}, p0/z, [x11, #4]
ld1rw {z28.s}, p0/z, [x11, #8]
ld1rw {z29.s}, p0/z, [x11, #12]
fmopa za0.s,p0/m,p0/m,z20.s,z18.s
fmopa za1.s,p0/m,p0/m,z20.s,z19.s
fmopa za2.s,p0/m,p0/m,z21.s,z18.s
fmopa za3.s,p0/m,p0/m,z21.s,z19.s
ld1w {z30.s}, p0/z, [x2]
ld1w {z31.s}, p0/z, [x2, #1, MUL VL]
add x11,x11,#16
fmopa za0.s,p0/m,p0/m,z16.s,z30.s
fmopa za1.s,p0/m,p0/m,z16.s,z31.s
fmopa za2.s,p0/m,p0/m,z17.s,z30.s
fmopa za3.s,p0/m,p0/m,z17.s,z31.s
incb x11, ALL, MUL #2
ld1w {z8.s}, p0/z, [x2, #2, MUL VL]
ld1w {z9.s}, p0/z, [x2, #3, MUL VL]
ld1rw {z20.s}, p0/z, [x11]
ld1rw {z21.s}, p0/z, [x11, #4]
ld1rw {z16.s}, p0/z, [x11, #8]
ld1rw {z17.s}, p0/z, [x11, #12]
fmopa za0.s,p0/m,p0/m,z22.s,z8.s
fmopa za1.s,p0/m,p0/m,z22.s,z9.s
fmopa za2.s,p0/m,p0/m,z23.s,z8.s
fmopa za3.s,p0/m,p0/m,z23.s,z9.s
ld1w {z10.s}, p0/z, [x2, #4, MUL VL]
ld1w {z11.s}, p0/z, [x2, #5, MUL VL]
add x11,x11,#16
fmopa za0.s,p0/m,p0/m,z24.s,z10.s
fmopa za1.s,p0/m,p0/m,z24.s,z11.s
fmopa za2.s,p0/m,p0/m,z25.s,z10.s
fmopa za3.s,p0/m,p0/m,z25.s,z11.s
incb x11, ALL, MUL #2
ld1rw {z22.s}, p0/z, [x11]
ld1rw {z23.s}, p0/z, [x11, #4]
ld1rw {z24.s}, p0/z, [x11, #8]
ld1rw {z25.s}, p0/z, [x11, #12]
fmla z0.s,p0/m,z18.s,z26.s
fmla z1.s,p0/m,z19.s,z26.s
fmla z2.s,p0/m,z18.s,z27.s
fmla z3.s,p0/m,z19.s,z27.s
fmla z4.s,p0/m,z18.s,z28.s
fmla z5.s,p0/m,z19.s,z28.s
fmla z6.s,p0/m,z18.s,z29.s
fmla z7.s,p0/m,z19.s,z29.s
add x11,x11,#16
fmla z0.s,p0/m,z30.s,z20.s
fmla z1.s,p0/m,z31.s,z20.s
fmla z2.s,p0/m,z30.s,z21.s
fmla z3.s,p0/m,z31.s,z21.s
fmla z4.s,p0/m,z30.s,z16.s
fmla z5.s,p0/m,z31.s,z16.s
fmla z6.s,p0/m,z30.s,z17.s
fmla z7.s,p0/m,z31.s,z17.s
incb x11, ALL, MUL #2
fmla z0.s,p0/m,z8.s,z22.s
fmla z1.s,p0/m,z9.s,z22.s
fmla z2.s,p0/m,z8.s,z23.s
fmla z3.s,p0/m,z9.s,z23.s
fmla z4.s,p0/m,z8.s,z24.s
fmla z5.s,p0/m,z9.s,z24.s
fmla z6.s,p0/m,z8.s,z25.s
fmla z7.s,p0/m,z9.s,z25.s
ld1rw {z26.s}, p0/z, [x11]
ld1rw {z27.s}, p0/z, [x11, #4]
ld1rw {z28.s}, p0/z, [x11, #8]
ld1rw {z29.s}, p0/z, [x11, #12]
add x1,x1,#64
fmla z0.s,p0/m,z10.s,z26.s
fmla z1.s,p0/m,z11.s,z26.s
fmla z2.s,p0/m,z10.s,z27.s
fmla z3.s,p0/m,z11.s,z27.s
fmla z4.s,p0/m,z10.s,z28.s
fmla z5.s,p0/m,z11.s,z28.s
fmla z6.s,p0/m,z10.s,z29.s
fmla z7.s,p0/m,z11.s,z29.s
incb x1, ALL, MUL #8
incb x2, ALL, MUL #6
.ukr7_done:
cbz x10,.ukr7_taildone
.ukr7_tail:
add x10,x10,#-1
mov x11,x1
incb x11, ALL, MUL #2
ld1w {z20.s}, p0/z, [x1]
ld1w {z18.s}, p0/z, [x2]
ld1w {z19.s}, p0/z, [x2, #1, MUL VL]
ld1w {z21.s}, p0/z, [x1, #1, MUL VL]
ld1rw {z16.s}, p0/z, [x11]
ld1rw {z17.s}, p0/z, [x11, #4]
ld1rw {z22.s}, p0/z, [x11, #8]
ld1rw {z23.s}, p0/z, [x11, #12]
fmopa za0.s,p0/m,p0/m,z20.s,z18.s
fmopa za1.s,p0/m,p0/m,z20.s,z19.s
fmopa za2.s,p0/m,p0/m,z21.s,z18.s
fmopa za3.s,p0/m,p0/m,z21.s,z19.s
fmla z0.s,p0/m,z18.s,z16.s
fmla z1.s,p0/m,z19.s,z16.s
fmla z2.s,p0/m,z18.s,z17.s
fmla z3.s,p0/m,z19.s,z17.s
fmla z4.s,p0/m,z18.s,z22.s
fmla z5.s,p0/m,z19.s,z22.s
fmla z6.s,p0/m,z18.s,z23.s
fmla z7.s,p0/m,z19.s,z23.s
add x1,x1,#16
incb x1, ALL, MUL #2
incb x2, ALL, MUL #2
cbnz x10,.ukr7_tail
.ukr7_taildone:
ldr s16, [x5]
fmov s17,wzr
fcmp s16,s17
b.ne .ukr0_try0
ldr s16, [x4]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr s16, [x5]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
b.ne .ukr0_try2
ldr s16, [x4]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr s16, [x4]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
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
st1w {za0h.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr1_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1w {z0.s}, p0, [x0]
st1w {z1.s}, p0, [x0, #1, MUL VL]
st1w {z2.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z3.s}, p0, [x0, #1, MUL VL]
st1w {z4.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z5.s}, p0, [x0, #1, MUL VL]
st1w {z6.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z7.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z16.s}, p0/z, [x4]
.ukr2_slices:
add x1,x1,#-4
mova z17.s,p0/m,za0h.s[w12,0]
mova z18.s,p0/m,za1h.s[w12,0]
fmul z19.s,z17.s,z16.s
fmul z20.s,z18.s,z16.s
st1w {z19.s}, p0, [x0]
st1w {z20.s}, p0, [x0, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,0]
mova z22.s,p0/m,za3h.s[w12,0]
fmul z23.s,z21.s,z16.s
add x0,x0,x8
fmul z24.s,z22.s,z16.s
st1w {z23.s}, p0, [x0]
st1w {z24.s}, p0, [x0, #1, MUL VL]
mova z25.s,p0/m,za0h.s[w12,1]
sub x0,x0,x8
mova z26.s,p0/m,za1h.s[w12,1]
fmul z27.s,z25.s,z16.s
add x0,x0,x6
fmul z28.s,z26.s,z16.s
st1w {z27.s}, p0, [x0]
st1w {z28.s}, p0, [x0, #1, MUL VL]
mova z29.s,p0/m,za2h.s[w12,1]
mova z30.s,p0/m,za3h.s[w12,1]
fmul z31.s,z29.s,z16.s
add x0,x0,x8
fmul z8.s,z30.s,z16.s
st1w {z31.s}, p0, [x0]
st1w {z8.s}, p0, [x0, #1, MUL VL]
mova z9.s,p0/m,za0h.s[w12,2]
sub x0,x0,x8
mova z10.s,p0/m,za1h.s[w12,2]
fmul z11.s,z9.s,z16.s
add x0,x0,x6
fmul z12.s,z10.s,z16.s
st1w {z11.s}, p0, [x0]
st1w {z12.s}, p0, [x0, #1, MUL VL]
mova z13.s,p0/m,za2h.s[w12,2]
mova z14.s,p0/m,za3h.s[w12,2]
fmul z15.s,z13.s,z16.s
add x0,x0,x8
fmul z19.s,z14.s,z16.s
st1w {z15.s}, p0, [x0]
st1w {z19.s}, p0, [x0, #1, MUL VL]
mova z17.s,p0/m,za0h.s[w12,3]
sub x0,x0,x8
mova z18.s,p0/m,za1h.s[w12,3]
fmul z20.s,z17.s,z16.s
add x0,x0,x6
fmul z23.s,z18.s,z16.s
st1w {z20.s}, p0, [x0]
st1w {z23.s}, p0, [x0, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,3]
mova z22.s,p0/m,za3h.s[w12,3]
fmul z24.s,z21.s,z16.s
add x0,x0,x8
fmul z27.s,z22.s,z16.s
st1w {z24.s}, p0, [x0]
st1w {z27.s}, p0, [x0, #1, MUL VL]
sub x0,x0,x8
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr2_slices
fmul z17.s,z0.s,z16.s
fmul z0.s,z1.s,z16.s
fmul z1.s,z2.s,z16.s
fmul z2.s,z3.s,z16.s
fmul z3.s,z4.s,z16.s
sub x0,x0,x8
fmul z4.s,z5.s,z16.s
add x0,x0,x8, LSL #1
st1w {z17.s}, p0, [x0]
st1w {z0.s}, p0, [x0, #1, MUL VL]
st1w {z1.s}, p0, [x0, x9, lsl #2]
fmul z0.s,z6.s,z16.s
fmul z1.s,z7.s,z16.s
add x0,x0,x6
st1w {z2.s}, p0, [x0, #1, MUL VL]
st1w {z3.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z4.s}, p0, [x0, #1, MUL VL]
st1w {z0.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z1.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
.ukr3_slices:
add x1,x1,#-4
mova z16.s,p0/m,za0h.s[w12,0]
ld1w {z17.s}, p0/z, [x0]
mova z18.s,p0/m,za1h.s[w12,0]
ld1w {z19.s}, p0/z, [x0, #1, MUL VL]
fadd z17.s,z16.s,z17.s
fadd z19.s,z18.s,z19.s
add x0,x0,x8
st1w {z17.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
mova z20.s,p0/m,za2h.s[w12,0]
ld1w {z21.s}, p0/z, [x0]
mova z22.s,p0/m,za3h.s[w12,0]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
fadd z21.s,z20.s,z21.s
add x3,x3,x8
fadd z23.s,z22.s,z23.s
sub x0,x0,x8
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z24.s,p0/m,za0h.s[w12,1]
ld1w {z25.s}, p0/z, [x0]
sub x3,x3,x8
mova z26.s,p0/m,za1h.s[w12,1]
ld1w {z27.s}, p0/z, [x0, #1, MUL VL]
fadd z25.s,z24.s,z25.s
add x3,x3,x6
fadd z27.s,z26.s,z27.s
add x0,x0,x8
st1w {z25.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
mova z28.s,p0/m,za2h.s[w12,1]
ld1w {z29.s}, p0/z, [x0]
mova z30.s,p0/m,za3h.s[w12,1]
ld1w {z31.s}, p0/z, [x0, #1, MUL VL]
fadd z29.s,z28.s,z29.s
add x3,x3,x8
fadd z31.s,z30.s,z31.s
sub x0,x0,x8
st1w {z29.s}, p0, [x3]
st1w {z31.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z8.s,p0/m,za0h.s[w12,2]
ld1w {z9.s}, p0/z, [x0]
sub x3,x3,x8
mova z10.s,p0/m,za1h.s[w12,2]
ld1w {z11.s}, p0/z, [x0, #1, MUL VL]
fadd z9.s,z8.s,z9.s
add x3,x3,x6
fadd z11.s,z10.s,z11.s
add x0,x0,x8
st1w {z9.s}, p0, [x3]
st1w {z11.s}, p0, [x3, #1, MUL VL]
mova z12.s,p0/m,za2h.s[w12,2]
ld1w {z13.s}, p0/z, [x0]
mova z14.s,p0/m,za3h.s[w12,2]
ld1w {z15.s}, p0/z, [x0, #1, MUL VL]
fadd z13.s,z12.s,z13.s
add x3,x3,x8
fadd z15.s,z14.s,z15.s
sub x0,x0,x8
st1w {z13.s}, p0, [x3]
st1w {z15.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z16.s,p0/m,za0h.s[w12,3]
ld1w {z17.s}, p0/z, [x0]
sub x3,x3,x8
mova z18.s,p0/m,za1h.s[w12,3]
ld1w {z19.s}, p0/z, [x0, #1, MUL VL]
fadd z17.s,z16.s,z17.s
add x3,x3,x6
fadd z19.s,z18.s,z19.s
add x0,x0,x8
st1w {z17.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
mova z20.s,p0/m,za2h.s[w12,3]
ld1w {z21.s}, p0/z, [x0]
mova z22.s,p0/m,za3h.s[w12,3]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
fadd z21.s,z20.s,z21.s
add x3,x3,x8
fadd z23.s,z22.s,z23.s
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr3_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z16.s}, p0/z, [x0]
fadd z16.s,z0.s,z16.s
mov x3,x0
st1w {z16.s}, p0, [x3]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z1.s,z0.s
st1w {z0.s}, p0, [x3, #1, MUL VL]
ld1w {z0.s}, p0/z, [x0, x9, lsl #2]
fadd z0.s,z2.s,z0.s
st1w {z0.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z3.s,z0.s
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fadd z1.s,z4.s,z1.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fadd z0.s,z5.s,z0.s
add x3,x3,x6
fadd z1.s,z6.s,z1.s
add x0,x0,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z7.s,z0.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z16.s}, p0/z, [x4]
.ukr4_slices:
add x1,x1,#-4
mova z17.s,p0/m,za0h.s[w12,0]
ld1w {z18.s}, p0/z, [x0]
mova z19.s,p0/m,za1h.s[w12,0]
ld1w {z20.s}, p0/z, [x0, #1, MUL VL]
fmla z18.s,p0/m,z17.s,z16.s
fmla z20.s,p0/m,z19.s,z16.s
add x0,x0,x8
st1w {z18.s}, p0, [x3]
st1w {z20.s}, p0, [x3, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,0]
ld1w {z22.s}, p0/z, [x0]
mova z23.s,p0/m,za3h.s[w12,0]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
fmla z22.s,p0/m,z21.s,z16.s
add x3,x3,x8
fmla z24.s,p0/m,z23.s,z16.s
sub x0,x0,x8
st1w {z22.s}, p0, [x3]
st1w {z24.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z25.s,p0/m,za0h.s[w12,1]
ld1w {z26.s}, p0/z, [x0]
sub x3,x3,x8
mova z27.s,p0/m,za1h.s[w12,1]
ld1w {z28.s}, p0/z, [x0, #1, MUL VL]
fmla z26.s,p0/m,z25.s,z16.s
add x3,x3,x6
fmla z28.s,p0/m,z27.s,z16.s
add x0,x0,x8
st1w {z26.s}, p0, [x3]
st1w {z28.s}, p0, [x3, #1, MUL VL]
mova z29.s,p0/m,za2h.s[w12,1]
ld1w {z30.s}, p0/z, [x0]
mova z31.s,p0/m,za3h.s[w12,1]
ld1w {z8.s}, p0/z, [x0, #1, MUL VL]
fmla z30.s,p0/m,z29.s,z16.s
add x3,x3,x8
fmla z8.s,p0/m,z31.s,z16.s
sub x0,x0,x8
st1w {z30.s}, p0, [x3]
st1w {z8.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z9.s,p0/m,za0h.s[w12,2]
ld1w {z10.s}, p0/z, [x0]
sub x3,x3,x8
mova z11.s,p0/m,za1h.s[w12,2]
ld1w {z12.s}, p0/z, [x0, #1, MUL VL]
fmla z10.s,p0/m,z9.s,z16.s
add x3,x3,x6
fmla z12.s,p0/m,z11.s,z16.s
add x0,x0,x8
st1w {z10.s}, p0, [x3]
st1w {z12.s}, p0, [x3, #1, MUL VL]
mova z13.s,p0/m,za2h.s[w12,2]
ld1w {z14.s}, p0/z, [x0]
mova z15.s,p0/m,za3h.s[w12,2]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
fmla z14.s,p0/m,z13.s,z16.s
add x3,x3,x8
fmla z18.s,p0/m,z15.s,z16.s
sub x0,x0,x8
st1w {z14.s}, p0, [x3]
st1w {z18.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z17.s,p0/m,za0h.s[w12,3]
ld1w {z20.s}, p0/z, [x0]
sub x3,x3,x8
mova z19.s,p0/m,za1h.s[w12,3]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
fmla z20.s,p0/m,z17.s,z16.s
add x3,x3,x6
fmla z22.s,p0/m,z19.s,z16.s
add x0,x0,x8
st1w {z20.s}, p0, [x3]
st1w {z22.s}, p0, [x3, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,3]
ld1w {z24.s}, p0/z, [x0]
mova z23.s,p0/m,za3h.s[w12,3]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
fmla z24.s,p0/m,z21.s,z16.s
add x3,x3,x8
fmla z26.s,p0/m,z23.s,z16.s
st1w {z24.s}, p0, [x3]
st1w {z26.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr4_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z17.s}, p0/z, [x0]
fmla z17.s,p0/m,z0.s,z16.s
mov x3,x0
st1w {z17.s}, p0, [x3]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z1.s,z16.s
st1w {z0.s}, p0, [x3, #1, MUL VL]
ld1w {z0.s}, p0/z, [x0, x9, lsl #2]
fmla z0.s,p0/m,z2.s,z16.s
st1w {z0.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z3.s,z16.s
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z1.s,p0/m,z4.s,z16.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z5.s,z16.s
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
add x3,x3,x6
fmla z1.s,p0/m,z6.s,z16.s
add x0,x0,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z7.s,z16.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z16.s}, p0/z, [x5]
.ukr5_slices:
add x1,x1,#-4
mova z17.s,p0/m,za0h.s[w12,0]
ld1w {z18.s}, p0/z, [x0]
mova z19.s,p0/m,za1h.s[w12,0]
ld1w {z20.s}, p0/z, [x0, #1, MUL VL]
fmla z17.s,p0/m,z18.s,z16.s
fmla z19.s,p0/m,z20.s,z16.s
add x0,x0,x8
st1w {z17.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,0]
ld1w {z22.s}, p0/z, [x0]
mova z23.s,p0/m,za3h.s[w12,0]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
fmla z21.s,p0/m,z22.s,z16.s
add x3,x3,x8
fmla z23.s,p0/m,z24.s,z16.s
sub x0,x0,x8
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,0],p0/m,z17.s
add x0,x0,x6
mova za1h.s[w12,0],p0/m,z19.s
mova z25.s,p0/m,za0h.s[w12,1]
ld1w {z26.s}, p0/z, [x0]
sub x3,x3,x8
mova z27.s,p0/m,za1h.s[w12,1]
ld1w {z28.s}, p0/z, [x0, #1, MUL VL]
fmla z25.s,p0/m,z26.s,z16.s
add x3,x3,x6
fmla z27.s,p0/m,z28.s,z16.s
mova za2h.s[w12,0],p0/m,z21.s
add x0,x0,x8
mova za3h.s[w12,0],p0/m,z23.s
st1w {z25.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
mova z29.s,p0/m,za2h.s[w12,1]
ld1w {z30.s}, p0/z, [x0]
mova z31.s,p0/m,za3h.s[w12,1]
ld1w {z8.s}, p0/z, [x0, #1, MUL VL]
fmla z29.s,p0/m,z30.s,z16.s
add x3,x3,x8
fmla z31.s,p0/m,z8.s,z16.s
sub x0,x0,x8
st1w {z29.s}, p0, [x3]
st1w {z31.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,1],p0/m,z25.s
add x0,x0,x6
mova za1h.s[w12,1],p0/m,z27.s
mova z9.s,p0/m,za0h.s[w12,2]
ld1w {z10.s}, p0/z, [x0]
sub x3,x3,x8
mova z11.s,p0/m,za1h.s[w12,2]
ld1w {z12.s}, p0/z, [x0, #1, MUL VL]
fmla z9.s,p0/m,z10.s,z16.s
add x3,x3,x6
fmla z11.s,p0/m,z12.s,z16.s
mova za2h.s[w12,1],p0/m,z29.s
add x0,x0,x8
mova za3h.s[w12,1],p0/m,z31.s
st1w {z9.s}, p0, [x3]
st1w {z11.s}, p0, [x3, #1, MUL VL]
mova z13.s,p0/m,za2h.s[w12,2]
ld1w {z14.s}, p0/z, [x0]
mova z15.s,p0/m,za3h.s[w12,2]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
fmla z13.s,p0/m,z14.s,z16.s
add x3,x3,x8
fmla z15.s,p0/m,z18.s,z16.s
sub x0,x0,x8
st1w {z13.s}, p0, [x3]
st1w {z15.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,2],p0/m,z9.s
add x0,x0,x6
mova za1h.s[w12,2],p0/m,z11.s
mova z17.s,p0/m,za0h.s[w12,3]
ld1w {z20.s}, p0/z, [x0]
mova z19.s,p0/m,za1h.s[w12,3]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
sub x3,x3,x8
fmla z17.s,p0/m,z20.s,z16.s
fmla z19.s,p0/m,z22.s,z16.s
mova za2h.s[w12,2],p0/m,z13.s
add x0,x0,x8
mova za3h.s[w12,2],p0/m,z15.s
add x3,x3,x6
mova z21.s,p0/m,za2h.s[w12,3]
ld1w {z24.s}, p0/z, [x0]
mova z23.s,p0/m,za3h.s[w12,3]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
st1w {z17.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
fmla z21.s,p0/m,z24.s,z16.s
fmla z23.s,p0/m,z26.s,z16.s
add x3,x3,x8
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
mova za0h.s[w12,3],p0/m,z17.s
mova za1h.s[w12,3],p0/m,z19.s
mova za2h.s[w12,3],p0/m,z21.s
mova za3h.s[w12,3],p0/m,z23.s
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr5_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z17.s}, p0/z, [x0]
mov x3,x0
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
ld1w {z19.s}, p0/z, [x0, x9, lsl #2]
fmla z0.s,p0/m,z17.s,z16.s
st1w {z0.s}, p0, [x3]
fmla z1.s,p0/m,z18.s,z16.s
st1w {z1.s}, p0, [x3, #1, MUL VL]
fmla z2.s,p0/m,z19.s,z16.s
st1w {z2.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z3.s,p0/m,z0.s,z16.s
add x3,x3,x6
st1w {z3.s}, p0, [x3, #1, MUL VL]
fmla z4.s,p0/m,z1.s,z16.s
st1w {z4.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z5.s,p0/m,z0.s,z16.s
add x3,x3,x6
st1w {z5.s}, p0, [x3, #1, MUL VL]
fmla z6.s,p0/m,z1.s,z16.s
st1w {z6.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z7.s,p0/m,z0.s,z16.s
add x3,x3,x6
st1w {z7.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z16.s}, p0/z, [x5]
ld1rw {z17.s}, p0/z, [x4]
.ukr6_slices:
add x1,x1,#-4
ld1w {z18.s}, p0/z, [x0]
ld1w {z19.s}, p0/z, [x0, #1, MUL VL]
fmul z18.s,z18.s,z16.s
mova z20.s,p0/m,za0h.s[w12,0]
fmul z19.s,z19.s,z16.s
mova z21.s,p0/m,za1h.s[w12,0]
add x0,x0,x8
fmla z18.s,p0/m,z20.s,z17.s
fmla z19.s,p0/m,z21.s,z17.s
ld1w {z22.s}, p0/z, [x0]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
st1w {z18.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
fmul z22.s,z22.s,z16.s
mova z24.s,p0/m,za2h.s[w12,0]
fmul z23.s,z23.s,z16.s
mova z25.s,p0/m,za3h.s[w12,0]
sub x0,x0,x8
fmla z22.s,p0/m,z24.s,z17.s
add x3,x3,x8
fmla z23.s,p0/m,z25.s,z17.s
add x0,x0,x6
st1w {z22.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
ld1w {z26.s}, p0/z, [x0]
ld1w {z27.s}, p0/z, [x0, #1, MUL VL]
fmul z26.s,z26.s,z16.s
mova z28.s,p0/m,za0h.s[w12,1]
sub x3,x3,x8
fmul z27.s,z27.s,z16.s
mova z29.s,p0/m,za1h.s[w12,1]
add x0,x0,x8
fmla z26.s,p0/m,z28.s,z17.s
add x3,x3,x6
fmla z27.s,p0/m,z29.s,z17.s
ld1w {z30.s}, p0/z, [x0]
ld1w {z31.s}, p0/z, [x0, #1, MUL VL]
st1w {z26.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
fmul z30.s,z30.s,z16.s
mova z8.s,p0/m,za2h.s[w12,1]
fmul z31.s,z31.s,z16.s
mova z9.s,p0/m,za3h.s[w12,1]
sub x0,x0,x8
fmla z30.s,p0/m,z8.s,z17.s
add x3,x3,x8
fmla z31.s,p0/m,z9.s,z17.s
add x0,x0,x6
st1w {z30.s}, p0, [x3]
st1w {z31.s}, p0, [x3, #1, MUL VL]
ld1w {z10.s}, p0/z, [x0]
ld1w {z11.s}, p0/z, [x0, #1, MUL VL]
fmul z10.s,z10.s,z16.s
mova z12.s,p0/m,za0h.s[w12,2]
sub x3,x3,x8
fmul z11.s,z11.s,z16.s
mova z13.s,p0/m,za1h.s[w12,2]
add x0,x0,x8
fmla z10.s,p0/m,z12.s,z17.s
add x3,x3,x6
fmla z11.s,p0/m,z13.s,z17.s
ld1w {z14.s}, p0/z, [x0]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
st1w {z10.s}, p0, [x3]
st1w {z11.s}, p0, [x3, #1, MUL VL]
fmul z14.s,z14.s,z16.s
mova z15.s,p0/m,za2h.s[w12,2]
fmul z18.s,z18.s,z16.s
mova z20.s,p0/m,za3h.s[w12,2]
sub x0,x0,x8
fmla z14.s,p0/m,z15.s,z17.s
add x3,x3,x8
fmla z18.s,p0/m,z20.s,z17.s
add x0,x0,x6
st1w {z14.s}, p0, [x3]
st1w {z18.s}, p0, [x3, #1, MUL VL]
ld1w {z19.s}, p0/z, [x0]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
fmul z19.s,z19.s,z16.s
mova z21.s,p0/m,za0h.s[w12,3]
sub x3,x3,x8
fmul z22.s,z22.s,z16.s
mova z24.s,p0/m,za1h.s[w12,3]
add x0,x0,x8
fmla z19.s,p0/m,z21.s,z17.s
add x3,x3,x6
fmla z22.s,p0/m,z24.s,z17.s
ld1w {z23.s}, p0/z, [x0]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
st1w {z19.s}, p0, [x3]
st1w {z22.s}, p0, [x3, #1, MUL VL]
fmul z23.s,z23.s,z16.s
mova z25.s,p0/m,za2h.s[w12,3]
fmul z26.s,z26.s,z16.s
mova z28.s,p0/m,za3h.s[w12,3]
fmla z23.s,p0/m,z25.s,z17.s
add x3,x3,x8
fmla z26.s,p0/m,z28.s,z17.s
st1w {z23.s}, p0, [x3]
st1w {z26.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr6_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z18.s}, p0/z, [x0]
mov x3,x0
ld1w {z19.s}, p0/z, [x0, #1, MUL VL]
ld1w {z20.s}, p0/z, [x0, x9, lsl #2]
fmul z18.s,z18.s,z16.s
fmla z18.s,p0/m,z0.s,z17.s
st1w {z18.s}, p0, [x3]
fmul z19.s,z19.s,z16.s
fmla z19.s,p0/m,z1.s,z17.s
st1w {z19.s}, p0, [x3, #1, MUL VL]
fmul z20.s,z20.s,z16.s
fmla z20.s,p0/m,z2.s,z17.s
st1w {z20.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmul z0.s,z0.s,z16.s
fmla z0.s,p0/m,z3.s,z17.s
fmul z1.s,z1.s,z16.s
fmla z1.s,p0/m,z4.s,z17.s
add x0,x0,x6
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmul z0.s,z0.s,z16.s
fmla z0.s,p0/m,z5.s,z17.s
fmul z1.s,z1.s,z16.s
fmla z1.s,p0/m,z6.s,z17.s
add x0,x0,x6
add x3,x3,x6
ld1w {z2.s}, p0/z, [x0, #1, MUL VL]
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
fmul z2.s,z2.s,z16.s
fmla z2.s,p0/m,z7.s,z17.s
add x3,x3,x6
st1w {z2.s}, p0, [x3, #1, MUL VL]
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
.size bli_sgemm_ukrgen_sme_sf_2vx2v_4x2v_asm, .-bli_sgemm_ukrgen_sme_sf_2vx2v_4x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_sgemm_ukrgen_sme_sf_2vx2v_6x2v
.text
.global bli_sgemm_ukrgen_sme_sf_2vx2v_6x2v_asm
.type bli_sgemm_ukrgen_sme_sf_2vx2v_6x2v_asm, %function
bli_sgemm_ukrgen_sme_sf_2vx2v_6x2v_asm:
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
smstart
ptrue p0.s
cntw x7
mul x8,x7,x6
lsr x9,x6,#2
and x10,x0,#3
lsr x0,x0,#2
zero {za0.s}
zero {za1.s}
zero {za2.s}
zero {za3.s}
dup z0.s,#0
dup z1.s,#0
dup z2.s,#0
dup z3.s,#0
dup z4.s,#0
dup z5.s,#0
dup z6.s,#0
dup z7.s,#0
dup z16.s,#0
dup z17.s,#0
dup z18.s,#0
dup z19.s,#0
cbz x0,.ukr7_done
add x11,x1,#24
ld1w {z20.s}, p0/z, [x11, #2, MUL VL]
ld1w {z21.s}, p0/z, [x11, #3, MUL VL]
add x11,x11,#24
ld1w {z22.s}, p0/z, [x11, #4, MUL VL]
ld1w {z23.s}, p0/z, [x11, #5, MUL VL]
ld1w {z24.s}, p0/z, [x1]
ld1w {z25.s}, p0/z, [x1, #1, MUL VL]
add x11,x11,#24
ld1w {z26.s}, p0/z, [x2]
ld1w {z27.s}, p0/z, [x2, #1, MUL VL]
ld1w {z28.s}, p0/z, [x11, #6, MUL VL]
ld1w {z29.s}, p0/z, [x11, #7, MUL VL]
incb x2, ALL, MUL #2
incb x1, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
fmopa za0.s,p0/m,p0/m,z24.s,z26.s
fmopa za1.s,p0/m,p0/m,z24.s,z27.s
fmopa za2.s,p0/m,p0/m,z25.s,z26.s
fmopa za3.s,p0/m,p0/m,z25.s,z27.s
ld1w {z30.s}, p0/z, [x2]
ld1w {z31.s}, p0/z, [x2, #1, MUL VL]
fmopa za0.s,p0/m,p0/m,z20.s,z30.s
fmopa za1.s,p0/m,p0/m,z20.s,z31.s
fmopa za2.s,p0/m,p0/m,z21.s,z30.s
fmopa za3.s,p0/m,p0/m,z21.s,z31.s
ld1w {z8.s}, p0/z, [x2, #2, MUL VL]
ld1w {z9.s}, p0/z, [x2, #3, MUL VL]
fmopa za0.s,p0/m,p0/m,z22.s,z8.s
fmopa za1.s,p0/m,p0/m,z22.s,z9.s
fmopa za2.s,p0/m,p0/m,z23.s,z8.s
fmopa za3.s,p0/m,p0/m,z23.s,z9.s
ld1w {z10.s}, p0/z, [x2, #4, MUL VL]
ld1w {z11.s}, p0/z, [x2, #5, MUL VL]
ld1rw {z24.s}, p0/z, [x1]
ld1rw {z25.s}, p0/z, [x1, #4]
ld1rw {z20.s}, p0/z, [x1, #8]
ld1rw {z21.s}, p0/z, [x1, #12]
add x11,x1,#24
fmopa za0.s,p0/m,p0/m,z28.s,z10.s
fmopa za1.s,p0/m,p0/m,z28.s,z11.s
fmopa za2.s,p0/m,p0/m,z29.s,z10.s
fmopa za3.s,p0/m,p0/m,z29.s,z11.s
fmla z0.s,p0/m,z26.s,z24.s
fmla z1.s,p0/m,z27.s,z24.s
fmla z2.s,p0/m,z26.s,z25.s
fmla z3.s,p0/m,z27.s,z25.s
fmla z4.s,p0/m,z26.s,z20.s
fmla z5.s,p0/m,z27.s,z20.s
fmla z6.s,p0/m,z26.s,z21.s
fmla z7.s,p0/m,z27.s,z21.s
incb x11, ALL, MUL #2
ld1rw {z28.s}, p0/z, [x11]
ld1rw {z29.s}, p0/z, [x11, #4]
ld1rw {z24.s}, p0/z, [x11, #8]
ld1rw {z25.s}, p0/z, [x11, #12]
ld1rw {z20.s}, p0/z, [x11, #16]
ld1rw {z21.s}, p0/z, [x11, #20]
ld1rw {z22.s}, p0/z, [x1, #16]
ld1rw {z23.s}, p0/z, [x1, #20]
add x11,x11,#24
fmla z16.s,p0/m,z26.s,z22.s
fmla z17.s,p0/m,z27.s,z22.s
fmla z18.s,p0/m,z26.s,z23.s
fmla z19.s,p0/m,z27.s,z23.s
fmla z0.s,p0/m,z30.s,z28.s
fmla z1.s,p0/m,z31.s,z28.s
fmla z2.s,p0/m,z30.s,z29.s
fmla z3.s,p0/m,z31.s,z29.s
fmla z4.s,p0/m,z30.s,z24.s
fmla z5.s,p0/m,z31.s,z24.s
fmla z6.s,p0/m,z30.s,z25.s
fmla z7.s,p0/m,z31.s,z25.s
incb x11, ALL, MUL #2
ld1rw {z22.s}, p0/z, [x11]
ld1rw {z23.s}, p0/z, [x11, #4]
ld1rw {z28.s}, p0/z, [x11, #8]
ld1rw {z29.s}, p0/z, [x11, #12]
ld1rw {z24.s}, p0/z, [x11, #16]
ld1rw {z25.s}, p0/z, [x11, #20]
add x11,x11,#24
fmla z16.s,p0/m,z30.s,z20.s
fmla z17.s,p0/m,z31.s,z20.s
fmla z18.s,p0/m,z30.s,z21.s
fmla z19.s,p0/m,z31.s,z21.s
fmla z0.s,p0/m,z8.s,z22.s
fmla z1.s,p0/m,z9.s,z22.s
fmla z2.s,p0/m,z8.s,z23.s
fmla z3.s,p0/m,z9.s,z23.s
fmla z4.s,p0/m,z8.s,z28.s
fmla z5.s,p0/m,z9.s,z28.s
fmla z6.s,p0/m,z8.s,z29.s
fmla z7.s,p0/m,z9.s,z29.s
incb x11, ALL, MUL #2
ld1rw {z20.s}, p0/z, [x11]
ld1rw {z21.s}, p0/z, [x11, #4]
ld1rw {z22.s}, p0/z, [x11, #8]
ld1rw {z23.s}, p0/z, [x11, #12]
ld1rw {z28.s}, p0/z, [x11, #16]
ld1rw {z29.s}, p0/z, [x11, #20]
add x11,x11,#24
fmla z16.s,p0/m,z8.s,z24.s
fmla z17.s,p0/m,z9.s,z24.s
fmla z18.s,p0/m,z8.s,z25.s
fmla z19.s,p0/m,z9.s,z25.s
decb x11, ALL, MUL #6
ld1w {z24.s}, p0/z, [x11, #6, MUL VL]
ld1w {z25.s}, p0/z, [x11, #7, MUL VL]
add x11,x11,#24
fmla z0.s,p0/m,z10.s,z20.s
fmla z1.s,p0/m,z11.s,z20.s
fmla z2.s,p0/m,z10.s,z21.s
fmla z3.s,p0/m,z11.s,z21.s
incb x11, ALL, MUL #8
ld1w {z20.s}, p0/z, [x11]
ld1w {z21.s}, p0/z, [x11, #1, MUL VL]
add x11,x11,#24
fmla z4.s,p0/m,z10.s,z22.s
fmla z5.s,p0/m,z11.s,z22.s
fmla z6.s,p0/m,z10.s,z23.s
fmla z7.s,p0/m,z11.s,z23.s
incb x11, ALL, MUL #2
ld1w {z22.s}, p0/z, [x11]
ld1w {z23.s}, p0/z, [x11, #1, MUL VL]
add x11,x11,#24
fmla z16.s,p0/m,z10.s,z28.s
fmla z17.s,p0/m,z11.s,z28.s
fmla z18.s,p0/m,z10.s,z29.s
fmla z19.s,p0/m,z11.s,z29.s
incb x11, ALL, MUL #2
ld1w {z26.s}, p0/z, [x2, #6, MUL VL]
ld1w {z27.s}, p0/z, [x2, #7, MUL VL]
add x1,x1,#96
ld1w {z28.s}, p0/z, [x11]
ld1w {z29.s}, p0/z, [x11, #1, MUL VL]
incb x1, ALL, MUL #8
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
fmopa za0.s,p0/m,p0/m,z24.s,z26.s
fmopa za1.s,p0/m,p0/m,z24.s,z27.s
fmopa za2.s,p0/m,p0/m,z25.s,z26.s
fmopa za3.s,p0/m,p0/m,z25.s,z27.s
ld1w {z30.s}, p0/z, [x2]
ld1w {z31.s}, p0/z, [x2, #1, MUL VL]
fmopa za0.s,p0/m,p0/m,z20.s,z30.s
fmopa za1.s,p0/m,p0/m,z20.s,z31.s
fmopa za2.s,p0/m,p0/m,z21.s,z30.s
fmopa za3.s,p0/m,p0/m,z21.s,z31.s
ld1w {z8.s}, p0/z, [x2, #2, MUL VL]
ld1w {z9.s}, p0/z, [x2, #3, MUL VL]
fmopa za0.s,p0/m,p0/m,z22.s,z8.s
fmopa za1.s,p0/m,p0/m,z22.s,z9.s
fmopa za2.s,p0/m,p0/m,z23.s,z8.s
fmopa za3.s,p0/m,p0/m,z23.s,z9.s
ld1w {z10.s}, p0/z, [x2, #4, MUL VL]
ld1w {z11.s}, p0/z, [x2, #5, MUL VL]
ld1rw {z24.s}, p0/z, [x1]
ld1rw {z25.s}, p0/z, [x1, #4]
ld1rw {z20.s}, p0/z, [x1, #8]
ld1rw {z21.s}, p0/z, [x1, #12]
add x11,x1,#24
fmopa za0.s,p0/m,p0/m,z28.s,z10.s
fmopa za1.s,p0/m,p0/m,z28.s,z11.s
fmopa za2.s,p0/m,p0/m,z29.s,z10.s
fmopa za3.s,p0/m,p0/m,z29.s,z11.s
fmla z0.s,p0/m,z26.s,z24.s
fmla z1.s,p0/m,z27.s,z24.s
fmla z2.s,p0/m,z26.s,z25.s
fmla z3.s,p0/m,z27.s,z25.s
fmla z4.s,p0/m,z26.s,z20.s
fmla z5.s,p0/m,z27.s,z20.s
fmla z6.s,p0/m,z26.s,z21.s
fmla z7.s,p0/m,z27.s,z21.s
incb x11, ALL, MUL #2
ld1rw {z28.s}, p0/z, [x11]
ld1rw {z29.s}, p0/z, [x11, #4]
ld1rw {z24.s}, p0/z, [x11, #8]
ld1rw {z25.s}, p0/z, [x11, #12]
ld1rw {z20.s}, p0/z, [x11, #16]
ld1rw {z21.s}, p0/z, [x11, #20]
ld1rw {z22.s}, p0/z, [x1, #16]
ld1rw {z23.s}, p0/z, [x1, #20]
add x11,x11,#24
fmla z16.s,p0/m,z26.s,z22.s
fmla z17.s,p0/m,z27.s,z22.s
fmla z18.s,p0/m,z26.s,z23.s
fmla z19.s,p0/m,z27.s,z23.s
fmla z0.s,p0/m,z30.s,z28.s
fmla z1.s,p0/m,z31.s,z28.s
fmla z2.s,p0/m,z30.s,z29.s
fmla z3.s,p0/m,z31.s,z29.s
fmla z4.s,p0/m,z30.s,z24.s
fmla z5.s,p0/m,z31.s,z24.s
fmla z6.s,p0/m,z30.s,z25.s
fmla z7.s,p0/m,z31.s,z25.s
incb x11, ALL, MUL #2
ld1rw {z22.s}, p0/z, [x11]
ld1rw {z23.s}, p0/z, [x11, #4]
ld1rw {z28.s}, p0/z, [x11, #8]
ld1rw {z29.s}, p0/z, [x11, #12]
ld1rw {z24.s}, p0/z, [x11, #16]
ld1rw {z25.s}, p0/z, [x11, #20]
add x11,x11,#24
fmla z16.s,p0/m,z30.s,z20.s
fmla z17.s,p0/m,z31.s,z20.s
fmla z18.s,p0/m,z30.s,z21.s
fmla z19.s,p0/m,z31.s,z21.s
fmla z0.s,p0/m,z8.s,z22.s
fmla z1.s,p0/m,z9.s,z22.s
fmla z2.s,p0/m,z8.s,z23.s
fmla z3.s,p0/m,z9.s,z23.s
fmla z4.s,p0/m,z8.s,z28.s
fmla z5.s,p0/m,z9.s,z28.s
fmla z6.s,p0/m,z8.s,z29.s
fmla z7.s,p0/m,z9.s,z29.s
incb x11, ALL, MUL #2
add x1,x1,#96
fmla z16.s,p0/m,z8.s,z24.s
fmla z17.s,p0/m,z9.s,z24.s
fmla z18.s,p0/m,z8.s,z25.s
fmla z19.s,p0/m,z9.s,z25.s
ld1rw {z20.s}, p0/z, [x11]
ld1rw {z21.s}, p0/z, [x11, #4]
ld1rw {z22.s}, p0/z, [x11, #8]
ld1rw {z23.s}, p0/z, [x11, #12]
ld1rw {z28.s}, p0/z, [x11, #16]
ld1rw {z29.s}, p0/z, [x11, #20]
incb x1, ALL, MUL #8
fmla z0.s,p0/m,z10.s,z20.s
fmla z1.s,p0/m,z11.s,z20.s
fmla z2.s,p0/m,z10.s,z21.s
fmla z3.s,p0/m,z11.s,z21.s
fmla z4.s,p0/m,z10.s,z22.s
fmla z5.s,p0/m,z11.s,z22.s
fmla z6.s,p0/m,z10.s,z23.s
fmla z7.s,p0/m,z11.s,z23.s
fmla z16.s,p0/m,z10.s,z28.s
fmla z17.s,p0/m,z11.s,z28.s
fmla z18.s,p0/m,z10.s,z29.s
fmla z19.s,p0/m,z11.s,z29.s
incb x2, ALL, MUL #6
decb x1, ALL, MUL #2
.ukr7_done:
cbz x10,.ukr7_taildone
.ukr7_tail:
add x10,x10,#-1
mov x11,x1
incb x11, ALL, MUL #2
ld1w {z24.s}, p0/z, [x1]
ld1w {z26.s}, p0/z, [x2]
ld1w {z27.s}, p0/z, [x2, #1, MUL VL]
ld1w {z25.s}, p0/z, [x1, #1, MUL VL]
ld1rw {z20.s}, p0/z, [x11]
ld1rw {z21.s}, p0/z, [x11, #4]
ld1rw {z22.s}, p0/z, [x11, #8]
ld1rw {z23.s}, p0/z, [x11, #12]
ld1rw {z28.s}, p0/z, [x11, #16]
ld1rw {z29.s}, p0/z, [x11, #20]
fmopa za0.s,p0/m,p0/m,z24.s,z26.s
fmopa za1.s,p0/m,p0/m,z24.s,z27.s
fmopa za2.s,p0/m,p0/m,z25.s,z26.s
fmopa za3.s,p0/m,p0/m,z25.s,z27.s
fmla z0.s,p0/m,z26.s,z20.s
fmla z1.s,p0/m,z27.s,z20.s
fmla z2.s,p0/m,z26.s,z21.s
fmla z3.s,p0/m,z27.s,z21.s
fmla z4.s,p0/m,z26.s,z22.s
fmla z5.s,p0/m,z27.s,z22.s
fmla z6.s,p0/m,z26.s,z23.s
fmla z7.s,p0/m,z27.s,z23.s
fmla z16.s,p0/m,z26.s,z28.s
fmla z17.s,p0/m,z27.s,z28.s
fmla z18.s,p0/m,z26.s,z29.s
fmla z19.s,p0/m,z27.s,z29.s
add x1,x1,#24
incb x1, ALL, MUL #2
incb x2, ALL, MUL #2
cbnz x10,.ukr7_tail
.ukr7_taildone:
ldr s20, [x5]
fmov s21,wzr
fcmp s20,s21
b.ne .ukr0_try0
ldr s20, [x4]
mov x0,#1065353216
fmov s21,w0
fcmp s20,s21
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr s20, [x5]
mov x0,#1065353216
fmov s21,w0
fcmp s20,s21
b.ne .ukr0_try2
ldr s20, [x4]
mov x0,#1065353216
fmov s21,w0
fcmp s20,s21
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr s20, [x4]
mov x0,#1065353216
fmov s21,w0
fcmp s20,s21
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
st1w {za0h.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr1_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1w {z0.s}, p0, [x0]
st1w {z1.s}, p0, [x0, #1, MUL VL]
st1w {z2.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z3.s}, p0, [x0, #1, MUL VL]
st1w {z4.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z5.s}, p0, [x0, #1, MUL VL]
st1w {z6.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z7.s}, p0, [x0, #1, MUL VL]
st1w {z16.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z17.s}, p0, [x0, #1, MUL VL]
st1w {z18.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z19.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z20.s}, p0/z, [x4]
.ukr2_slices:
add x1,x1,#-4
mova z21.s,p0/m,za0h.s[w12,0]
mova z22.s,p0/m,za1h.s[w12,0]
fmul z23.s,z21.s,z20.s
fmul z24.s,z22.s,z20.s
st1w {z23.s}, p0, [x0]
st1w {z24.s}, p0, [x0, #1, MUL VL]
mova z25.s,p0/m,za2h.s[w12,0]
mova z26.s,p0/m,za3h.s[w12,0]
fmul z27.s,z25.s,z20.s
add x0,x0,x8
fmul z28.s,z26.s,z20.s
st1w {z27.s}, p0, [x0]
st1w {z28.s}, p0, [x0, #1, MUL VL]
mova z29.s,p0/m,za0h.s[w12,1]
sub x0,x0,x8
mova z30.s,p0/m,za1h.s[w12,1]
fmul z31.s,z29.s,z20.s
add x0,x0,x6
fmul z8.s,z30.s,z20.s
st1w {z31.s}, p0, [x0]
st1w {z8.s}, p0, [x0, #1, MUL VL]
mova z9.s,p0/m,za2h.s[w12,1]
mova z10.s,p0/m,za3h.s[w12,1]
fmul z11.s,z9.s,z20.s
add x0,x0,x8
fmul z12.s,z10.s,z20.s
st1w {z11.s}, p0, [x0]
st1w {z12.s}, p0, [x0, #1, MUL VL]
mova z13.s,p0/m,za0h.s[w12,2]
sub x0,x0,x8
mova z14.s,p0/m,za1h.s[w12,2]
fmul z15.s,z13.s,z20.s
add x0,x0,x6
fmul z23.s,z14.s,z20.s
st1w {z15.s}, p0, [x0]
st1w {z23.s}, p0, [x0, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,2]
mova z22.s,p0/m,za3h.s[w12,2]
fmul z24.s,z21.s,z20.s
add x0,x0,x8
fmul z27.s,z22.s,z20.s
st1w {z24.s}, p0, [x0]
st1w {z27.s}, p0, [x0, #1, MUL VL]
mova z25.s,p0/m,za0h.s[w12,3]
sub x0,x0,x8
mova z26.s,p0/m,za1h.s[w12,3]
fmul z28.s,z25.s,z20.s
add x0,x0,x6
fmul z31.s,z26.s,z20.s
st1w {z28.s}, p0, [x0]
st1w {z31.s}, p0, [x0, #1, MUL VL]
mova z29.s,p0/m,za2h.s[w12,3]
mova z30.s,p0/m,za3h.s[w12,3]
fmul z8.s,z29.s,z20.s
add x0,x0,x8
fmul z11.s,z30.s,z20.s
st1w {z8.s}, p0, [x0]
st1w {z11.s}, p0, [x0, #1, MUL VL]
sub x0,x0,x8
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr2_slices
fmul z21.s,z0.s,z20.s
fmul z0.s,z1.s,z20.s
fmul z1.s,z2.s,z20.s
fmul z2.s,z3.s,z20.s
fmul z3.s,z4.s,z20.s
sub x0,x0,x8
fmul z4.s,z5.s,z20.s
add x0,x0,x8, LSL #1
st1w {z21.s}, p0, [x0]
st1w {z0.s}, p0, [x0, #1, MUL VL]
st1w {z1.s}, p0, [x0, x9, lsl #2]
fmul z0.s,z6.s,z20.s
fmul z1.s,z7.s,z20.s
add x0,x0,x6
st1w {z2.s}, p0, [x0, #1, MUL VL]
st1w {z3.s}, p0, [x0, x9, lsl #2]
fmul z2.s,z16.s,z20.s
fmul z3.s,z17.s,z20.s
add x0,x0,x6
st1w {z4.s}, p0, [x0, #1, MUL VL]
st1w {z0.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z1.s}, p0, [x0, #1, MUL VL]
st1w {z2.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
fmul z0.s,z18.s,z20.s
st1w {z3.s}, p0, [x0, #1, MUL VL]
st1w {z0.s}, p0, [x0, x9, lsl #2]
fmul z0.s,z19.s,z20.s
add x0,x0,x6
st1w {z0.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
.ukr3_slices:
add x1,x1,#-4
mova z20.s,p0/m,za0h.s[w12,0]
ld1w {z21.s}, p0/z, [x0]
mova z22.s,p0/m,za1h.s[w12,0]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
fadd z21.s,z20.s,z21.s
fadd z23.s,z22.s,z23.s
add x0,x0,x8
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
mova z24.s,p0/m,za2h.s[w12,0]
ld1w {z25.s}, p0/z, [x0]
mova z26.s,p0/m,za3h.s[w12,0]
ld1w {z27.s}, p0/z, [x0, #1, MUL VL]
fadd z25.s,z24.s,z25.s
add x3,x3,x8
fadd z27.s,z26.s,z27.s
sub x0,x0,x8
st1w {z25.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z28.s,p0/m,za0h.s[w12,1]
ld1w {z29.s}, p0/z, [x0]
sub x3,x3,x8
mova z30.s,p0/m,za1h.s[w12,1]
ld1w {z31.s}, p0/z, [x0, #1, MUL VL]
fadd z29.s,z28.s,z29.s
add x3,x3,x6
fadd z31.s,z30.s,z31.s
add x0,x0,x8
st1w {z29.s}, p0, [x3]
st1w {z31.s}, p0, [x3, #1, MUL VL]
mova z8.s,p0/m,za2h.s[w12,1]
ld1w {z9.s}, p0/z, [x0]
mova z10.s,p0/m,za3h.s[w12,1]
ld1w {z11.s}, p0/z, [x0, #1, MUL VL]
fadd z9.s,z8.s,z9.s
add x3,x3,x8
fadd z11.s,z10.s,z11.s
sub x0,x0,x8
st1w {z9.s}, p0, [x3]
st1w {z11.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z12.s,p0/m,za0h.s[w12,2]
ld1w {z13.s}, p0/z, [x0]
sub x3,x3,x8
mova z14.s,p0/m,za1h.s[w12,2]
ld1w {z15.s}, p0/z, [x0, #1, MUL VL]
fadd z13.s,z12.s,z13.s
add x3,x3,x6
fadd z15.s,z14.s,z15.s
add x0,x0,x8
st1w {z13.s}, p0, [x3]
st1w {z15.s}, p0, [x3, #1, MUL VL]
mova z20.s,p0/m,za2h.s[w12,2]
ld1w {z21.s}, p0/z, [x0]
mova z22.s,p0/m,za3h.s[w12,2]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
fadd z21.s,z20.s,z21.s
add x3,x3,x8
fadd z23.s,z22.s,z23.s
sub x0,x0,x8
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z24.s,p0/m,za0h.s[w12,3]
ld1w {z25.s}, p0/z, [x0]
sub x3,x3,x8
mova z26.s,p0/m,za1h.s[w12,3]
ld1w {z27.s}, p0/z, [x0, #1, MUL VL]
fadd z25.s,z24.s,z25.s
add x3,x3,x6
fadd z27.s,z26.s,z27.s
add x0,x0,x8
st1w {z25.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
mova z28.s,p0/m,za2h.s[w12,3]
ld1w {z29.s}, p0/z, [x0]
mova z30.s,p0/m,za3h.s[w12,3]
ld1w {z31.s}, p0/z, [x0, #1, MUL VL]
fadd z29.s,z28.s,z29.s
add x3,x3,x8
fadd z31.s,z30.s,z31.s
st1w {z29.s}, p0, [x3]
st1w {z31.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr3_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z20.s}, p0/z, [x0]
fadd z20.s,z0.s,z20.s
mov x3,x0
st1w {z20.s}, p0, [x3]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z1.s,z0.s
st1w {z0.s}, p0, [x3, #1, MUL VL]
ld1w {z0.s}, p0/z, [x0, x9, lsl #2]
fadd z0.s,z2.s,z0.s
st1w {z0.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z3.s,z0.s
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fadd z1.s,z4.s,z1.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z5.s,z0.s
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fadd z1.s,z6.s,z1.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fadd z0.s,z7.s,z0.s
add x3,x3,x6
fadd z1.s,z16.s,z1.s
add x0,x0,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fadd z0.s,z17.s,z0.s
add x3,x3,x6
fadd z1.s,z18.s,z1.s
add x0,x0,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z19.s,z0.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z20.s}, p0/z, [x4]
.ukr4_slices:
add x1,x1,#-4
mova z21.s,p0/m,za0h.s[w12,0]
ld1w {z22.s}, p0/z, [x0]
mova z23.s,p0/m,za1h.s[w12,0]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
fmla z22.s,p0/m,z21.s,z20.s
fmla z24.s,p0/m,z23.s,z20.s
add x0,x0,x8
st1w {z22.s}, p0, [x3]
st1w {z24.s}, p0, [x3, #1, MUL VL]
mova z25.s,p0/m,za2h.s[w12,0]
ld1w {z26.s}, p0/z, [x0]
mova z27.s,p0/m,za3h.s[w12,0]
ld1w {z28.s}, p0/z, [x0, #1, MUL VL]
fmla z26.s,p0/m,z25.s,z20.s
add x3,x3,x8
fmla z28.s,p0/m,z27.s,z20.s
sub x0,x0,x8
st1w {z26.s}, p0, [x3]
st1w {z28.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z29.s,p0/m,za0h.s[w12,1]
ld1w {z30.s}, p0/z, [x0]
sub x3,x3,x8
mova z31.s,p0/m,za1h.s[w12,1]
ld1w {z8.s}, p0/z, [x0, #1, MUL VL]
fmla z30.s,p0/m,z29.s,z20.s
add x3,x3,x6
fmla z8.s,p0/m,z31.s,z20.s
add x0,x0,x8
st1w {z30.s}, p0, [x3]
st1w {z8.s}, p0, [x3, #1, MUL VL]
mova z9.s,p0/m,za2h.s[w12,1]
ld1w {z10.s}, p0/z, [x0]
mova z11.s,p0/m,za3h.s[w12,1]
ld1w {z12.s}, p0/z, [x0, #1, MUL VL]
fmla z10.s,p0/m,z9.s,z20.s
add x3,x3,x8
fmla z12.s,p0/m,z11.s,z20.s
sub x0,x0,x8
st1w {z10.s}, p0, [x3]
st1w {z12.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z13.s,p0/m,za0h.s[w12,2]
ld1w {z14.s}, p0/z, [x0]
sub x3,x3,x8
mova z15.s,p0/m,za1h.s[w12,2]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
fmla z14.s,p0/m,z13.s,z20.s
add x3,x3,x6
fmla z22.s,p0/m,z15.s,z20.s
add x0,x0,x8
st1w {z14.s}, p0, [x3]
st1w {z22.s}, p0, [x3, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,2]
ld1w {z24.s}, p0/z, [x0]
mova z23.s,p0/m,za3h.s[w12,2]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
fmla z24.s,p0/m,z21.s,z20.s
add x3,x3,x8
fmla z26.s,p0/m,z23.s,z20.s
sub x0,x0,x8
st1w {z24.s}, p0, [x3]
st1w {z26.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z25.s,p0/m,za0h.s[w12,3]
ld1w {z28.s}, p0/z, [x0]
sub x3,x3,x8
mova z27.s,p0/m,za1h.s[w12,3]
ld1w {z30.s}, p0/z, [x0, #1, MUL VL]
fmla z28.s,p0/m,z25.s,z20.s
add x3,x3,x6
fmla z30.s,p0/m,z27.s,z20.s
add x0,x0,x8
st1w {z28.s}, p0, [x3]
st1w {z30.s}, p0, [x3, #1, MUL VL]
mova z29.s,p0/m,za2h.s[w12,3]
ld1w {z8.s}, p0/z, [x0]
mova z31.s,p0/m,za3h.s[w12,3]
ld1w {z10.s}, p0/z, [x0, #1, MUL VL]
fmla z8.s,p0/m,z29.s,z20.s
add x3,x3,x8
fmla z10.s,p0/m,z31.s,z20.s
st1w {z8.s}, p0, [x3]
st1w {z10.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr4_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z21.s}, p0/z, [x0]
fmla z21.s,p0/m,z0.s,z20.s
mov x3,x0
st1w {z21.s}, p0, [x3]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z1.s,z20.s
st1w {z0.s}, p0, [x3, #1, MUL VL]
ld1w {z0.s}, p0/z, [x0, x9, lsl #2]
fmla z0.s,p0/m,z2.s,z20.s
st1w {z0.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z3.s,z20.s
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z1.s,p0/m,z4.s,z20.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z5.s,z20.s
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z1.s,p0/m,z6.s,z20.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z7.s,z20.s
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
add x3,x3,x6
fmla z1.s,p0/m,z16.s,z20.s
add x0,x0,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z0.s,p0/m,z17.s,z20.s
add x3,x3,x6
fmla z1.s,p0/m,z18.s,z20.s
add x0,x0,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z19.s,z20.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z20.s}, p0/z, [x5]
.ukr5_slices:
add x1,x1,#-4
mova z21.s,p0/m,za0h.s[w12,0]
ld1w {z22.s}, p0/z, [x0]
mova z23.s,p0/m,za1h.s[w12,0]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
fmla z21.s,p0/m,z22.s,z20.s
fmla z23.s,p0/m,z24.s,z20.s
add x0,x0,x8
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
mova z25.s,p0/m,za2h.s[w12,0]
ld1w {z26.s}, p0/z, [x0]
mova z27.s,p0/m,za3h.s[w12,0]
ld1w {z28.s}, p0/z, [x0, #1, MUL VL]
fmla z25.s,p0/m,z26.s,z20.s
add x3,x3,x8
fmla z27.s,p0/m,z28.s,z20.s
sub x0,x0,x8
st1w {z25.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,0],p0/m,z21.s
add x0,x0,x6
mova za1h.s[w12,0],p0/m,z23.s
mova z29.s,p0/m,za0h.s[w12,1]
ld1w {z30.s}, p0/z, [x0]
sub x3,x3,x8
mova z31.s,p0/m,za1h.s[w12,1]
ld1w {z8.s}, p0/z, [x0, #1, MUL VL]
fmla z29.s,p0/m,z30.s,z20.s
add x3,x3,x6
fmla z31.s,p0/m,z8.s,z20.s
mova za2h.s[w12,0],p0/m,z25.s
add x0,x0,x8
mova za3h.s[w12,0],p0/m,z27.s
st1w {z29.s}, p0, [x3]
st1w {z31.s}, p0, [x3, #1, MUL VL]
mova z9.s,p0/m,za2h.s[w12,1]
ld1w {z10.s}, p0/z, [x0]
mova z11.s,p0/m,za3h.s[w12,1]
ld1w {z12.s}, p0/z, [x0, #1, MUL VL]
fmla z9.s,p0/m,z10.s,z20.s
add x3,x3,x8
fmla z11.s,p0/m,z12.s,z20.s
sub x0,x0,x8
st1w {z9.s}, p0, [x3]
st1w {z11.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,1],p0/m,z29.s
add x0,x0,x6
mova za1h.s[w12,1],p0/m,z31.s
mova z13.s,p0/m,za0h.s[w12,2]
ld1w {z14.s}, p0/z, [x0]
sub x3,x3,x8
mova z15.s,p0/m,za1h.s[w12,2]
fmla z13.s,p0/m,z14.s,z20.s
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
add x3,x3,x6
fmla z15.s,p0/m,z22.s,z20.s
mova za2h.s[w12,1],p0/m,z9.s
add x0,x0,x8
mova za3h.s[w12,1],p0/m,z11.s
st1w {z13.s}, p0, [x3]
st1w {z15.s}, p0, [x3, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,2]
ld1w {z24.s}, p0/z, [x0]
mova z23.s,p0/m,za3h.s[w12,2]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
fmla z21.s,p0/m,z24.s,z20.s
add x3,x3,x8
fmla z23.s,p0/m,z26.s,z20.s
sub x0,x0,x8
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,2],p0/m,z13.s
add x0,x0,x6
mova za1h.s[w12,2],p0/m,z15.s
mova z25.s,p0/m,za0h.s[w12,3]
ld1w {z28.s}, p0/z, [x0]
mova z27.s,p0/m,za1h.s[w12,3]
ld1w {z30.s}, p0/z, [x0, #1, MUL VL]
sub x3,x3,x8
fmla z25.s,p0/m,z28.s,z20.s
fmla z27.s,p0/m,z30.s,z20.s
mova za2h.s[w12,2],p0/m,z21.s
add x0,x0,x8
mova za3h.s[w12,2],p0/m,z23.s
add x3,x3,x6
mova z29.s,p0/m,za2h.s[w12,3]
ld1w {z8.s}, p0/z, [x0]
mova z31.s,p0/m,za3h.s[w12,3]
ld1w {z10.s}, p0/z, [x0, #1, MUL VL]
st1w {z25.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
fmla z29.s,p0/m,z8.s,z20.s
fmla z31.s,p0/m,z10.s,z20.s
add x3,x3,x8
st1w {z29.s}, p0, [x3]
st1w {z31.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
mova za0h.s[w12,3],p0/m,z25.s
mova za1h.s[w12,3],p0/m,z27.s
mova za2h.s[w12,3],p0/m,z29.s
mova za3h.s[w12,3],p0/m,z31.s
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr5_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z21.s}, p0/z, [x0]
mov x3,x0
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
ld1w {z23.s}, p0/z, [x0, x9, lsl #2]
fmla z0.s,p0/m,z21.s,z20.s
st1w {z0.s}, p0, [x3]
fmla z1.s,p0/m,z22.s,z20.s
st1w {z1.s}, p0, [x3, #1, MUL VL]
fmla z2.s,p0/m,z23.s,z20.s
st1w {z2.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z3.s,p0/m,z0.s,z20.s
add x3,x3,x6
st1w {z3.s}, p0, [x3, #1, MUL VL]
fmla z4.s,p0/m,z1.s,z20.s
st1w {z4.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z5.s,p0/m,z0.s,z20.s
add x3,x3,x6
st1w {z5.s}, p0, [x3, #1, MUL VL]
fmla z6.s,p0/m,z1.s,z20.s
st1w {z6.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z7.s,p0/m,z0.s,z20.s
add x3,x3,x6
st1w {z7.s}, p0, [x3, #1, MUL VL]
fmla z16.s,p0/m,z1.s,z20.s
st1w {z16.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmla z17.s,p0/m,z0.s,z20.s
add x3,x3,x6
st1w {z17.s}, p0, [x3, #1, MUL VL]
fmla z18.s,p0/m,z1.s,z20.s
st1w {z18.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z19.s,p0/m,z0.s,z20.s
add x3,x3,x6
st1w {z19.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z20.s}, p0/z, [x5]
ld1rw {z21.s}, p0/z, [x4]
.ukr6_slices:
add x1,x1,#-4
ld1w {z22.s}, p0/z, [x0]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
fmul z22.s,z22.s,z20.s
mova z24.s,p0/m,za0h.s[w12,0]
fmul z23.s,z23.s,z20.s
mova z25.s,p0/m,za1h.s[w12,0]
add x0,x0,x8
fmla z22.s,p0/m,z24.s,z21.s
fmla z23.s,p0/m,z25.s,z21.s
ld1w {z26.s}, p0/z, [x0]
ld1w {z27.s}, p0/z, [x0, #1, MUL VL]
st1w {z22.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
fmul z26.s,z26.s,z20.s
mova z28.s,p0/m,za2h.s[w12,0]
fmul z27.s,z27.s,z20.s
mova z29.s,p0/m,za3h.s[w12,0]
sub x0,x0,x8
fmla z26.s,p0/m,z28.s,z21.s
add x3,x3,x8
fmla z27.s,p0/m,z29.s,z21.s
add x0,x0,x6
st1w {z26.s}, p0, [x3]
st1w {z27.s}, p0, [x3, #1, MUL VL]
ld1w {z30.s}, p0/z, [x0]
ld1w {z31.s}, p0/z, [x0, #1, MUL VL]
fmul z30.s,z30.s,z20.s
mova z8.s,p0/m,za0h.s[w12,1]
sub x3,x3,x8
fmul z31.s,z31.s,z20.s
mova z9.s,p0/m,za1h.s[w12,1]
add x0,x0,x8
fmla z30.s,p0/m,z8.s,z21.s
add x3,x3,x6
fmla z31.s,p0/m,z9.s,z21.s
ld1w {z10.s}, p0/z, [x0]
ld1w {z11.s}, p0/z, [x0, #1, MUL VL]
st1w {z30.s}, p0, [x3]
st1w {z31.s}, p0, [x3, #1, MUL VL]
fmul z10.s,z10.s,z20.s
mova z12.s,p0/m,za2h.s[w12,1]
fmul z11.s,z11.s,z20.s
mova z13.s,p0/m,za3h.s[w12,1]
sub x0,x0,x8
fmla z10.s,p0/m,z12.s,z21.s
add x3,x3,x8
fmla z11.s,p0/m,z13.s,z21.s
add x0,x0,x6
st1w {z10.s}, p0, [x3]
st1w {z11.s}, p0, [x3, #1, MUL VL]
ld1w {z14.s}, p0/z, [x0]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
fmul z14.s,z14.s,z20.s
mova z15.s,p0/m,za0h.s[w12,2]
sub x3,x3,x8
fmul z22.s,z22.s,z20.s
mova z24.s,p0/m,za1h.s[w12,2]
add x0,x0,x8
fmla z14.s,p0/m,z15.s,z21.s
add x3,x3,x6
fmla z22.s,p0/m,z24.s,z21.s
ld1w {z23.s}, p0/z, [x0]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
st1w {z14.s}, p0, [x3]
st1w {z22.s}, p0, [x3, #1, MUL VL]
fmul z23.s,z23.s,z20.s
mova z25.s,p0/m,za2h.s[w12,2]
fmul z26.s,z26.s,z20.s
mova z28.s,p0/m,za3h.s[w12,2]
sub x0,x0,x8
fmla z23.s,p0/m,z25.s,z21.s
add x3,x3,x8
fmla z26.s,p0/m,z28.s,z21.s
add x0,x0,x6
st1w {z23.s}, p0, [x3]
st1w {z26.s}, p0, [x3, #1, MUL VL]
ld1w {z27.s}, p0/z, [x0]
ld1w {z30.s}, p0/z, [x0, #1, MUL VL]
fmul z27.s,z27.s,z20.s
mova z29.s,p0/m,za0h.s[w12,3]
sub x3,x3,x8
fmul z30.s,z30.s,z20.s
mova z8.s,p0/m,za1h.s[w12,3]
add x0,x0,x8
fmla z27.s,p0/m,z29.s,z21.s
add x3,x3,x6
fmla z30.s,p0/m,z8.s,z21.s
ld1w {z31.s}, p0/z, [x0]
ld1w {z10.s}, p0/z, [x0, #1, MUL VL]
st1w {z27.s}, p0, [x3]
st1w {z30.s}, p0, [x3, #1, MUL VL]
fmul z31.s,z31.s,z20.s
mova z9.s,p0/m,za2h.s[w12,3]
fmul z10.s,z10.s,z20.s
mova z12.s,p0/m,za3h.s[w12,3]
fmla z31.s,p0/m,z9.s,z21.s
add x3,x3,x8
fmla z10.s,p0/m,z12.s,z21.s
st1w {z31.s}, p0, [x3]
st1w {z10.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr6_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1w {z22.s}, p0/z, [x0]
mov x3,x0
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
ld1w {z24.s}, p0/z, [x0, x9, lsl #2]
fmul z22.s,z22.s,z20.s
fmla z22.s,p0/m,z0.s,z21.s
st1w {z22.s}, p0, [x3]
fmul z23.s,z23.s,z20.s
fmla z23.s,p0/m,z1.s,z21.s
st1w {z23.s}, p0, [x3, #1, MUL VL]
fmul z24.s,z24.s,z20.s
fmla z24.s,p0/m,z2.s,z21.s
st1w {z24.s}, p0, [x3, x9, lsl #2]
add x0,x0,x6
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmul z0.s,z0.s,z20.s
fmla z0.s,p0/m,z3.s,z21.s
fmul z1.s,z1.s,z20.s
fmla z1.s,p0/m,z4.s,z21.s
add x0,x0,x6
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmul z0.s,z0.s,z20.s
fmla z0.s,p0/m,z5.s,z21.s
fmul z1.s,z1.s,z20.s
fmla z1.s,p0/m,z6.s,z21.s
add x0,x0,x6
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
ld1w {z1.s}, p0/z, [x0, x9, lsl #2]
fmul z0.s,z0.s,z20.s
fmla z0.s,p0/m,z7.s,z21.s
fmul z1.s,z1.s,z20.s
fmla z1.s,p0/m,z16.s,z21.s
add x0,x0,x6
add x3,x3,x6
ld1w {z2.s}, p0/z, [x0, #1, MUL VL]
ld1w {z3.s}, p0/z, [x0, x9, lsl #2]
st1w {z0.s}, p0, [x3, #1, MUL VL]
st1w {z1.s}, p0, [x3, x9, lsl #2]
fmul z2.s,z2.s,z20.s
fmul z3.s,z3.s,z20.s
add x0,x0,x6
fmla z2.s,p0/m,z17.s,z21.s
add x3,x3,x6
fmla z3.s,p0/m,z18.s,z21.s
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
st1w {z2.s}, p0, [x3, #1, MUL VL]
st1w {z3.s}, p0, [x3, x9, lsl #2]
fmul z0.s,z0.s,z20.s
fmla z0.s,p0/m,z19.s,z21.s
add x3,x3,x6
st1w {z0.s}, p0, [x3, #1, MUL VL]
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
.size bli_sgemm_ukrgen_sme_sf_2vx2v_6x2v_asm, .-bli_sgemm_ukrgen_sme_sf_2vx2v_6x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_sgemm_ukrgen_sme_sf_2vx2v_1x2v
.text
.global bli_sgemm_ukrgen_sme_sf_2vx2v_1x2v_asm
.type bli_sgemm_ukrgen_sme_sf_2vx2v_1x2v_asm, %function
bli_sgemm_ukrgen_sme_sf_2vx2v_1x2v_asm:
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
dup z0.s,#0
dup z1.s,#0
cbz x0,.ukr7_done
add x10,x1,#4
ld1w {z2.s}, p0/z, [x2]
ld1w {z3.s}, p0/z, [x2, #1, MUL VL]
ld1w {z4.s}, p0/z, [x1]
ld1w {z5.s}, p0/z, [x1, #1, MUL VL]
ld1w {z6.s}, p0/z, [x10, #2, MUL VL]
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x10,x1,#4
ld1w {z7.s}, p0/z, [x10, #3, MUL VL]
add x10,x10,#4
ld1w {z16.s}, p0/z, [x10, #4, MUL VL]
ld1w {z17.s}, p0/z, [x10, #5, MUL VL]
add x10,x10,#4
ld1w {z18.s}, p0/z, [x10, #6, MUL VL]
ld1w {z19.s}, p0/z, [x10, #7, MUL VL]
add x10,x10,#-12
incb x10, ALL, MUL #2
ld1rw {z20.s}, p0/z, [x10]
add x10,x10,#4
incb x10, ALL, MUL #2
ld1rw {z21.s}, p0/z, [x10]
add x10,x10,#4
incb x10, ALL, MUL #2
ld1rw {z22.s}, p0/z, [x10]
add x10,x10,#4
incb x10, ALL, MUL #2
ld1rw {z23.s}, p0/z, [x10]
fmopa za0.s,p0/m,p0/m,z4.s,z2.s
fmopa za1.s,p0/m,p0/m,z4.s,z3.s
fmopa za2.s,p0/m,p0/m,z5.s,z2.s
fmopa za3.s,p0/m,p0/m,z5.s,z3.s
add x10,x10,#4
ld1w {z24.s}, p0/z, [x2]
ld1w {z25.s}, p0/z, [x2, #1, MUL VL]
fmla z0.s,p0/m,z2.s,z20.s
fmla z1.s,p0/m,z3.s,z20.s
ld1w {z4.s}, p0/z, [x10]
ld1w {z5.s}, p0/z, [x10, #1, MUL VL]
fmopa za0.s,p0/m,p0/m,z6.s,z24.s
fmopa za1.s,p0/m,p0/m,z6.s,z25.s
fmopa za2.s,p0/m,p0/m,z7.s,z24.s
fmopa za3.s,p0/m,p0/m,z7.s,z25.s
ld1w {z26.s}, p0/z, [x2, #2, MUL VL]
ld1w {z27.s}, p0/z, [x2, #3, MUL VL]
fmla z0.s,p0/m,z24.s,z21.s
fmla z1.s,p0/m,z25.s,z21.s
add x10,x10,#4
fmopa za0.s,p0/m,p0/m,z16.s,z26.s
fmopa za1.s,p0/m,p0/m,z16.s,z27.s
fmopa za2.s,p0/m,p0/m,z17.s,z26.s
fmopa za3.s,p0/m,p0/m,z17.s,z27.s
ld1w {z28.s}, p0/z, [x2, #4, MUL VL]
ld1w {z29.s}, p0/z, [x2, #5, MUL VL]
fmla z0.s,p0/m,z26.s,z22.s
fmla z1.s,p0/m,z27.s,z22.s
incb x10, ALL, MUL #2
ld1w {z2.s}, p0/z, [x2, #6, MUL VL]
ld1w {z3.s}, p0/z, [x2, #7, MUL VL]
add x1,x1,#16
fmopa za0.s,p0/m,p0/m,z18.s,z28.s
fmopa za1.s,p0/m,p0/m,z18.s,z29.s
fmopa za2.s,p0/m,p0/m,z19.s,z28.s
fmopa za3.s,p0/m,p0/m,z19.s,z29.s
fmla z0.s,p0/m,z28.s,z23.s
fmla z1.s,p0/m,z29.s,z23.s
ld1w {z6.s}, p0/z, [x10]
incb x1, ALL, MUL #8
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x10,x1,#4
ld1w {z7.s}, p0/z, [x10, #3, MUL VL]
add x10,x10,#4
ld1w {z16.s}, p0/z, [x10, #4, MUL VL]
ld1w {z17.s}, p0/z, [x10, #5, MUL VL]
add x10,x10,#4
ld1w {z18.s}, p0/z, [x10, #6, MUL VL]
ld1w {z19.s}, p0/z, [x10, #7, MUL VL]
add x10,x10,#-12
incb x10, ALL, MUL #2
ld1rw {z20.s}, p0/z, [x10]
add x10,x10,#4
incb x10, ALL, MUL #2
ld1rw {z21.s}, p0/z, [x10]
add x10,x10,#4
incb x10, ALL, MUL #2
ld1rw {z22.s}, p0/z, [x10]
fmopa za0.s,p0/m,p0/m,z4.s,z2.s
fmopa za1.s,p0/m,p0/m,z4.s,z3.s
fmopa za2.s,p0/m,p0/m,z5.s,z2.s
fmopa za3.s,p0/m,p0/m,z5.s,z3.s
ld1w {z24.s}, p0/z, [x2]
ld1w {z25.s}, p0/z, [x2, #1, MUL VL]
fmla z0.s,p0/m,z2.s,z20.s
fmla z1.s,p0/m,z3.s,z20.s
add x10,x10,#4
fmopa za0.s,p0/m,p0/m,z6.s,z24.s
fmopa za1.s,p0/m,p0/m,z6.s,z25.s
fmopa za2.s,p0/m,p0/m,z7.s,z24.s
fmopa za3.s,p0/m,p0/m,z7.s,z25.s
ld1w {z26.s}, p0/z, [x2, #2, MUL VL]
ld1w {z27.s}, p0/z, [x2, #3, MUL VL]
fmla z0.s,p0/m,z24.s,z21.s
fmla z1.s,p0/m,z25.s,z21.s
incb x10, ALL, MUL #2
fmopa za0.s,p0/m,p0/m,z16.s,z26.s
fmopa za1.s,p0/m,p0/m,z16.s,z27.s
fmopa za2.s,p0/m,p0/m,z17.s,z26.s
fmopa za3.s,p0/m,p0/m,z17.s,z27.s
ld1w {z28.s}, p0/z, [x2, #4, MUL VL]
ld1w {z29.s}, p0/z, [x2, #5, MUL VL]
fmla z0.s,p0/m,z26.s,z22.s
fmla z1.s,p0/m,z27.s,z22.s
ld1rw {z23.s}, p0/z, [x10]
add x1,x1,#16
fmopa za0.s,p0/m,p0/m,z18.s,z28.s
fmopa za1.s,p0/m,p0/m,z18.s,z29.s
fmopa za2.s,p0/m,p0/m,z19.s,z28.s
fmopa za3.s,p0/m,p0/m,z19.s,z29.s
fmla z0.s,p0/m,z28.s,z23.s
fmla z1.s,p0/m,z29.s,z23.s
incb x1, ALL, MUL #8
incb x2, ALL, MUL #6
.ukr7_done:
cbz x9,.ukr7_taildone
.ukr7_tail:
add x9,x9,#-1
mov x10,x1
incb x10, ALL, MUL #2
ld1w {z4.s}, p0/z, [x1]
ld1w {z2.s}, p0/z, [x2]
ld1w {z3.s}, p0/z, [x2, #1, MUL VL]
ld1w {z5.s}, p0/z, [x1, #1, MUL VL]
ld1rw {z20.s}, p0/z, [x10]
fmopa za0.s,p0/m,p0/m,z4.s,z2.s
fmopa za1.s,p0/m,p0/m,z4.s,z3.s
fmopa za2.s,p0/m,p0/m,z5.s,z2.s
fmopa za3.s,p0/m,p0/m,z5.s,z3.s
fmla z0.s,p0/m,z2.s,z20.s
fmla z1.s,p0/m,z3.s,z20.s
add x1,x1,#4
incb x1, ALL, MUL #2
incb x2, ALL, MUL #2
cbnz x9,.ukr7_tail
.ukr7_taildone:
ldr s2, [x5]
fmov s3,wzr
fcmp s2,s3
b.ne .ukr0_try0
ldr s2, [x4]
mov x0,#1065353216
fmov s3,w0
fcmp s2,s3
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr s2, [x5]
mov x0,#1065353216
fmov s3,w0
fcmp s2,s3
b.ne .ukr0_try2
ldr s2, [x4]
mov x0,#1065353216
fmov s3,w0
fcmp s2,s3
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr s2, [x4]
mov x0,#1065353216
fmov s3,w0
fcmp s2,s3
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
st1w {za0h.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 0]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 0]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 1]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 1]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 2]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 2]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
st1w {za0h.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za1h.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
add x0,x0,x8
st1w {za2h.s[w12, 3]}, p0, [x0]
incb x0, ALL, MUL #1
st1w {za3h.s[w12, 3]}, p0, [x0]
decb x0, ALL, MUL #1
sub x0,x0,x8
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr1_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1w {z0.s}, p0, [x0]
st1w {z1.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z2.s}, p0/z, [x4]
.ukr2_slices:
add x1,x1,#-4
mova z3.s,p0/m,za0h.s[w12,0]
mova z4.s,p0/m,za1h.s[w12,0]
fmul z5.s,z3.s,z2.s
fmul z6.s,z4.s,z2.s
st1w {z5.s}, p0, [x0]
st1w {z6.s}, p0, [x0, #1, MUL VL]
mova z7.s,p0/m,za2h.s[w12,0]
mova z16.s,p0/m,za3h.s[w12,0]
fmul z17.s,z7.s,z2.s
add x0,x0,x8
fmul z18.s,z16.s,z2.s
st1w {z17.s}, p0, [x0]
st1w {z18.s}, p0, [x0, #1, MUL VL]
mova z19.s,p0/m,za0h.s[w12,1]
sub x0,x0,x8
mova z20.s,p0/m,za1h.s[w12,1]
fmul z21.s,z19.s,z2.s
add x0,x0,x6
fmul z22.s,z20.s,z2.s
st1w {z21.s}, p0, [x0]
st1w {z22.s}, p0, [x0, #1, MUL VL]
mova z23.s,p0/m,za2h.s[w12,1]
mova z24.s,p0/m,za3h.s[w12,1]
fmul z25.s,z23.s,z2.s
add x0,x0,x8
fmul z26.s,z24.s,z2.s
st1w {z25.s}, p0, [x0]
st1w {z26.s}, p0, [x0, #1, MUL VL]
mova z27.s,p0/m,za0h.s[w12,2]
sub x0,x0,x8
mova z28.s,p0/m,za1h.s[w12,2]
fmul z29.s,z27.s,z2.s
add x0,x0,x6
fmul z30.s,z28.s,z2.s
st1w {z29.s}, p0, [x0]
st1w {z30.s}, p0, [x0, #1, MUL VL]
mova z31.s,p0/m,za2h.s[w12,2]
mova z8.s,p0/m,za3h.s[w12,2]
fmul z9.s,z31.s,z2.s
add x0,x0,x8
fmul z10.s,z8.s,z2.s
st1w {z9.s}, p0, [x0]
st1w {z10.s}, p0, [x0, #1, MUL VL]
mova z11.s,p0/m,za0h.s[w12,3]
sub x0,x0,x8
mova z12.s,p0/m,za1h.s[w12,3]
fmul z13.s,z11.s,z2.s
add x0,x0,x6
fmul z14.s,z12.s,z2.s
st1w {z13.s}, p0, [x0]
st1w {z14.s}, p0, [x0, #1, MUL VL]
mova z15.s,p0/m,za2h.s[w12,3]
mova z3.s,p0/m,za3h.s[w12,3]
fmul z5.s,z15.s,z2.s
add x0,x0,x8
fmul z6.s,z3.s,z2.s
st1w {z5.s}, p0, [x0]
st1w {z6.s}, p0, [x0, #1, MUL VL]
sub x0,x0,x8
add x0,x0,x6
add x12,x12,#4
cbnz x1,.ukr2_slices
fmul z3.s,z0.s,z2.s
fmul z0.s,z1.s,z2.s
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1w {z3.s}, p0, [x0]
st1w {z0.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
.ukr3_slices:
add x1,x1,#-4
mova z2.s,p0/m,za0h.s[w12,0]
ld1w {z3.s}, p0/z, [x0]
mova z4.s,p0/m,za1h.s[w12,0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
fadd z3.s,z2.s,z3.s
fadd z5.s,z4.s,z5.s
add x0,x0,x8
st1w {z3.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
mova z6.s,p0/m,za2h.s[w12,0]
ld1w {z7.s}, p0/z, [x0]
mova z16.s,p0/m,za3h.s[w12,0]
ld1w {z17.s}, p0/z, [x0, #1, MUL VL]
fadd z7.s,z6.s,z7.s
add x3,x3,x8
fadd z17.s,z16.s,z17.s
sub x0,x0,x8
st1w {z7.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z18.s,p0/m,za0h.s[w12,1]
ld1w {z19.s}, p0/z, [x0]
sub x3,x3,x8
mova z20.s,p0/m,za1h.s[w12,1]
ld1w {z21.s}, p0/z, [x0, #1, MUL VL]
fadd z19.s,z18.s,z19.s
add x3,x3,x6
fadd z21.s,z20.s,z21.s
add x0,x0,x8
st1w {z19.s}, p0, [x3]
st1w {z21.s}, p0, [x3, #1, MUL VL]
mova z22.s,p0/m,za2h.s[w12,1]
ld1w {z23.s}, p0/z, [x0]
mova z24.s,p0/m,za3h.s[w12,1]
ld1w {z25.s}, p0/z, [x0, #1, MUL VL]
fadd z23.s,z22.s,z23.s
add x3,x3,x8
fadd z25.s,z24.s,z25.s
sub x0,x0,x8
st1w {z23.s}, p0, [x3]
st1w {z25.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z26.s,p0/m,za0h.s[w12,2]
ld1w {z27.s}, p0/z, [x0]
sub x3,x3,x8
mova z28.s,p0/m,za1h.s[w12,2]
ld1w {z29.s}, p0/z, [x0, #1, MUL VL]
fadd z27.s,z26.s,z27.s
add x3,x3,x6
fadd z29.s,z28.s,z29.s
add x0,x0,x8
st1w {z27.s}, p0, [x3]
st1w {z29.s}, p0, [x3, #1, MUL VL]
mova z30.s,p0/m,za2h.s[w12,2]
ld1w {z31.s}, p0/z, [x0]
mova z8.s,p0/m,za3h.s[w12,2]
ld1w {z9.s}, p0/z, [x0, #1, MUL VL]
fadd z31.s,z30.s,z31.s
add x3,x3,x8
fadd z9.s,z8.s,z9.s
sub x0,x0,x8
st1w {z31.s}, p0, [x3]
st1w {z9.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z10.s,p0/m,za0h.s[w12,3]
ld1w {z11.s}, p0/z, [x0]
sub x3,x3,x8
mova z12.s,p0/m,za1h.s[w12,3]
ld1w {z13.s}, p0/z, [x0, #1, MUL VL]
fadd z11.s,z10.s,z11.s
add x3,x3,x6
fadd z13.s,z12.s,z13.s
add x0,x0,x8
st1w {z11.s}, p0, [x3]
st1w {z13.s}, p0, [x3, #1, MUL VL]
mova z14.s,p0/m,za2h.s[w12,3]
ld1w {z15.s}, p0/z, [x0]
mova z2.s,p0/m,za3h.s[w12,3]
ld1w {z3.s}, p0/z, [x0, #1, MUL VL]
fadd z15.s,z14.s,z15.s
add x3,x3,x8
fadd z3.s,z2.s,z3.s
st1w {z15.s}, p0, [x3]
st1w {z3.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr3_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
sub x3,x3,x8
ld1w {z2.s}, p0/z, [x0]
fadd z2.s,z0.s,z2.s
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fadd z0.s,z1.s,z0.s
mov x3,x0
st1w {z2.s}, p0, [x3]
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z2.s}, p0/z, [x4]
.ukr4_slices:
add x1,x1,#-4
mova z3.s,p0/m,za0h.s[w12,0]
ld1w {z4.s}, p0/z, [x0]
mova z5.s,p0/m,za1h.s[w12,0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
fmla z4.s,p0/m,z3.s,z2.s
fmla z6.s,p0/m,z5.s,z2.s
add x0,x0,x8
st1w {z4.s}, p0, [x3]
st1w {z6.s}, p0, [x3, #1, MUL VL]
mova z7.s,p0/m,za2h.s[w12,0]
ld1w {z16.s}, p0/z, [x0]
mova z17.s,p0/m,za3h.s[w12,0]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
fmla z16.s,p0/m,z7.s,z2.s
add x3,x3,x8
fmla z18.s,p0/m,z17.s,z2.s
sub x0,x0,x8
st1w {z16.s}, p0, [x3]
st1w {z18.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z19.s,p0/m,za0h.s[w12,1]
ld1w {z20.s}, p0/z, [x0]
sub x3,x3,x8
mova z21.s,p0/m,za1h.s[w12,1]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
fmla z20.s,p0/m,z19.s,z2.s
add x3,x3,x6
fmla z22.s,p0/m,z21.s,z2.s
add x0,x0,x8
st1w {z20.s}, p0, [x3]
st1w {z22.s}, p0, [x3, #1, MUL VL]
mova z23.s,p0/m,za2h.s[w12,1]
ld1w {z24.s}, p0/z, [x0]
mova z25.s,p0/m,za3h.s[w12,1]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
fmla z24.s,p0/m,z23.s,z2.s
add x3,x3,x8
fmla z26.s,p0/m,z25.s,z2.s
sub x0,x0,x8
st1w {z24.s}, p0, [x3]
st1w {z26.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z27.s,p0/m,za0h.s[w12,2]
ld1w {z28.s}, p0/z, [x0]
sub x3,x3,x8
mova z29.s,p0/m,za1h.s[w12,2]
ld1w {z30.s}, p0/z, [x0, #1, MUL VL]
fmla z28.s,p0/m,z27.s,z2.s
add x3,x3,x6
fmla z30.s,p0/m,z29.s,z2.s
add x0,x0,x8
st1w {z28.s}, p0, [x3]
st1w {z30.s}, p0, [x3, #1, MUL VL]
mova z31.s,p0/m,za2h.s[w12,2]
ld1w {z8.s}, p0/z, [x0]
mova z9.s,p0/m,za3h.s[w12,2]
ld1w {z10.s}, p0/z, [x0, #1, MUL VL]
fmla z8.s,p0/m,z31.s,z2.s
add x3,x3,x8
fmla z10.s,p0/m,z9.s,z2.s
sub x0,x0,x8
st1w {z8.s}, p0, [x3]
st1w {z10.s}, p0, [x3, #1, MUL VL]
add x0,x0,x6
mova z11.s,p0/m,za0h.s[w12,3]
ld1w {z12.s}, p0/z, [x0]
sub x3,x3,x8
mova z13.s,p0/m,za1h.s[w12,3]
ld1w {z14.s}, p0/z, [x0, #1, MUL VL]
fmla z12.s,p0/m,z11.s,z2.s
add x3,x3,x6
fmla z14.s,p0/m,z13.s,z2.s
add x0,x0,x8
st1w {z12.s}, p0, [x3]
st1w {z14.s}, p0, [x3, #1, MUL VL]
mova z15.s,p0/m,za2h.s[w12,3]
ld1w {z4.s}, p0/z, [x0]
mova z3.s,p0/m,za3h.s[w12,3]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
fmla z4.s,p0/m,z15.s,z2.s
add x3,x3,x8
fmla z6.s,p0/m,z3.s,z2.s
st1w {z4.s}, p0, [x3]
st1w {z6.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr4_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
sub x3,x3,x8
ld1w {z3.s}, p0/z, [x0]
fmla z3.s,p0/m,z0.s,z2.s
ld1w {z0.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z1.s,z2.s
mov x3,x0
st1w {z3.s}, p0, [x3]
st1w {z0.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z2.s}, p0/z, [x5]
.ukr5_slices:
add x1,x1,#-4
mova z3.s,p0/m,za0h.s[w12,0]
ld1w {z4.s}, p0/z, [x0]
mova z5.s,p0/m,za1h.s[w12,0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
fmla z3.s,p0/m,z4.s,z2.s
fmla z5.s,p0/m,z6.s,z2.s
add x0,x0,x8
st1w {z3.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
mova z7.s,p0/m,za2h.s[w12,0]
ld1w {z16.s}, p0/z, [x0]
mova z17.s,p0/m,za3h.s[w12,0]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
fmla z7.s,p0/m,z16.s,z2.s
add x3,x3,x8
fmla z17.s,p0/m,z18.s,z2.s
sub x0,x0,x8
st1w {z7.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,0],p0/m,z3.s
add x0,x0,x6
mova za1h.s[w12,0],p0/m,z5.s
mova z19.s,p0/m,za0h.s[w12,1]
ld1w {z20.s}, p0/z, [x0]
sub x3,x3,x8
mova z21.s,p0/m,za1h.s[w12,1]
ld1w {z22.s}, p0/z, [x0, #1, MUL VL]
fmla z19.s,p0/m,z20.s,z2.s
add x3,x3,x6
fmla z21.s,p0/m,z22.s,z2.s
mova za2h.s[w12,0],p0/m,z7.s
add x0,x0,x8
mova za3h.s[w12,0],p0/m,z17.s
st1w {z19.s}, p0, [x3]
st1w {z21.s}, p0, [x3, #1, MUL VL]
mova z23.s,p0/m,za2h.s[w12,1]
ld1w {z24.s}, p0/z, [x0]
mova z25.s,p0/m,za3h.s[w12,1]
ld1w {z26.s}, p0/z, [x0, #1, MUL VL]
fmla z23.s,p0/m,z24.s,z2.s
add x3,x3,x8
fmla z25.s,p0/m,z26.s,z2.s
sub x0,x0,x8
st1w {z23.s}, p0, [x3]
st1w {z25.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,1],p0/m,z19.s
add x0,x0,x6
mova za1h.s[w12,1],p0/m,z21.s
mova z27.s,p0/m,za0h.s[w12,2]
ld1w {z28.s}, p0/z, [x0]
sub x3,x3,x8
mova z29.s,p0/m,za1h.s[w12,2]
ld1w {z30.s}, p0/z, [x0, #1, MUL VL]
fmla z27.s,p0/m,z28.s,z2.s
add x3,x3,x6
fmla z29.s,p0/m,z30.s,z2.s
mova za2h.s[w12,1],p0/m,z23.s
add x0,x0,x8
mova za3h.s[w12,1],p0/m,z25.s
st1w {z27.s}, p0, [x3]
st1w {z29.s}, p0, [x3, #1, MUL VL]
mova z31.s,p0/m,za2h.s[w12,2]
ld1w {z8.s}, p0/z, [x0]
mova z9.s,p0/m,za3h.s[w12,2]
ld1w {z10.s}, p0/z, [x0, #1, MUL VL]
fmla z31.s,p0/m,z8.s,z2.s
add x3,x3,x8
fmla z9.s,p0/m,z10.s,z2.s
sub x0,x0,x8
st1w {z31.s}, p0, [x3]
st1w {z9.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,2],p0/m,z27.s
add x0,x0,x6
mova za1h.s[w12,2],p0/m,z29.s
mova z11.s,p0/m,za0h.s[w12,3]
ld1w {z12.s}, p0/z, [x0]
mova z13.s,p0/m,za1h.s[w12,3]
ld1w {z14.s}, p0/z, [x0, #1, MUL VL]
sub x3,x3,x8
fmla z11.s,p0/m,z12.s,z2.s
fmla z13.s,p0/m,z14.s,z2.s
mova za2h.s[w12,2],p0/m,z31.s
add x0,x0,x8
mova za3h.s[w12,2],p0/m,z9.s
add x3,x3,x6
mova z15.s,p0/m,za2h.s[w12,3]
ld1w {z4.s}, p0/z, [x0]
mova z3.s,p0/m,za3h.s[w12,3]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
st1w {z11.s}, p0, [x3]
st1w {z13.s}, p0, [x3, #1, MUL VL]
fmla z15.s,p0/m,z4.s,z2.s
fmla z3.s,p0/m,z6.s,z2.s
add x3,x3,x8
st1w {z15.s}, p0, [x3]
st1w {z3.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
mova za0h.s[w12,3],p0/m,z11.s
mova za1h.s[w12,3],p0/m,z13.s
mova za2h.s[w12,3],p0/m,z15.s
mova za3h.s[w12,3],p0/m,z3.s
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr5_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
sub x3,x3,x8
ld1w {z3.s}, p0/z, [x0]
ld1w {z4.s}, p0/z, [x0, #1, MUL VL]
fmla z0.s,p0/m,z3.s,z2.s
mov x3,x0
st1w {z0.s}, p0, [x3]
fmla z1.s,p0/m,z4.s,z2.s
st1w {z1.s}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
mov x1,x7
mov x12,#0
ld1rw {z2.s}, p0/z, [x5]
ld1rw {z3.s}, p0/z, [x4]
.ukr6_slices:
add x1,x1,#-4
ld1w {z4.s}, p0/z, [x0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
fmul z4.s,z4.s,z2.s
mova z6.s,p0/m,za0h.s[w12,0]
fmul z5.s,z5.s,z2.s
mova z7.s,p0/m,za1h.s[w12,0]
add x0,x0,x8
fmla z4.s,p0/m,z6.s,z3.s
fmla z5.s,p0/m,z7.s,z3.s
ld1w {z16.s}, p0/z, [x0]
ld1w {z17.s}, p0/z, [x0, #1, MUL VL]
st1w {z4.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
fmul z16.s,z16.s,z2.s
mova z18.s,p0/m,za2h.s[w12,0]
fmul z17.s,z17.s,z2.s
mova z19.s,p0/m,za3h.s[w12,0]
sub x0,x0,x8
fmla z16.s,p0/m,z18.s,z3.s
add x3,x3,x8
fmla z17.s,p0/m,z19.s,z3.s
add x0,x0,x6
st1w {z16.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
ld1w {z20.s}, p0/z, [x0]
ld1w {z21.s}, p0/z, [x0, #1, MUL VL]
fmul z20.s,z20.s,z2.s
mova z22.s,p0/m,za0h.s[w12,1]
sub x3,x3,x8
fmul z21.s,z21.s,z2.s
mova z23.s,p0/m,za1h.s[w12,1]
add x0,x0,x8
fmla z20.s,p0/m,z22.s,z3.s
add x3,x3,x6
fmla z21.s,p0/m,z23.s,z3.s
ld1w {z24.s}, p0/z, [x0]
ld1w {z25.s}, p0/z, [x0, #1, MUL VL]
st1w {z20.s}, p0, [x3]
st1w {z21.s}, p0, [x3, #1, MUL VL]
fmul z24.s,z24.s,z2.s
mova z26.s,p0/m,za2h.s[w12,1]
fmul z25.s,z25.s,z2.s
mova z27.s,p0/m,za3h.s[w12,1]
sub x0,x0,x8
fmla z24.s,p0/m,z26.s,z3.s
add x3,x3,x8
fmla z25.s,p0/m,z27.s,z3.s
add x0,x0,x6
st1w {z24.s}, p0, [x3]
st1w {z25.s}, p0, [x3, #1, MUL VL]
ld1w {z28.s}, p0/z, [x0]
ld1w {z29.s}, p0/z, [x0, #1, MUL VL]
fmul z28.s,z28.s,z2.s
mova z30.s,p0/m,za0h.s[w12,2]
sub x3,x3,x8
fmul z29.s,z29.s,z2.s
mova z31.s,p0/m,za1h.s[w12,2]
add x0,x0,x8
fmla z28.s,p0/m,z30.s,z3.s
add x3,x3,x6
fmla z29.s,p0/m,z31.s,z3.s
ld1w {z8.s}, p0/z, [x0]
ld1w {z9.s}, p0/z, [x0, #1, MUL VL]
st1w {z28.s}, p0, [x3]
st1w {z29.s}, p0, [x3, #1, MUL VL]
fmul z8.s,z8.s,z2.s
mova z10.s,p0/m,za2h.s[w12,2]
fmul z9.s,z9.s,z2.s
mova z11.s,p0/m,za3h.s[w12,2]
sub x0,x0,x8
fmla z8.s,p0/m,z10.s,z3.s
add x3,x3,x8
fmla z9.s,p0/m,z11.s,z3.s
add x0,x0,x6
st1w {z8.s}, p0, [x3]
st1w {z9.s}, p0, [x3, #1, MUL VL]
ld1w {z12.s}, p0/z, [x0]
ld1w {z13.s}, p0/z, [x0, #1, MUL VL]
fmul z12.s,z12.s,z2.s
mova z14.s,p0/m,za0h.s[w12,3]
sub x3,x3,x8
fmul z13.s,z13.s,z2.s
mova z15.s,p0/m,za1h.s[w12,3]
add x0,x0,x8
fmla z12.s,p0/m,z14.s,z3.s
add x3,x3,x6
fmla z13.s,p0/m,z15.s,z3.s
ld1w {z4.s}, p0/z, [x0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
st1w {z12.s}, p0, [x3]
st1w {z13.s}, p0, [x3, #1, MUL VL]
fmul z4.s,z4.s,z2.s
mova z6.s,p0/m,za2h.s[w12,3]
fmul z5.s,z5.s,z2.s
mova z7.s,p0/m,za3h.s[w12,3]
fmla z4.s,p0/m,z6.s,z3.s
add x3,x3,x8
fmla z5.s,p0/m,z7.s,z3.s
st1w {z4.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x6
add x3,x3,x6
add x12,x12,#4
cbnz x1,.ukr6_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
ld1w {z4.s}, p0/z, [x0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
sub x3,x3,x8
fmul z4.s,z4.s,z2.s
fmla z4.s,p0/m,z0.s,z3.s
fmul z5.s,z5.s,z2.s
fmla z5.s,p0/m,z1.s,z3.s
mov x3,x0
st1w {z4.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
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
.size bli_sgemm_ukrgen_sme_sf_2vx2v_1x2v_asm, .-bli_sgemm_ukrgen_sme_sf_2vx2v_1x2v_asm
.section .note.GNU-stack,"",%progbits
