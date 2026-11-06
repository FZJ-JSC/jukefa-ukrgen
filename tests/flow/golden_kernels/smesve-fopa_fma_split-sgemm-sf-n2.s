### bli_sgemm_ukrgen_sme_sf_1vx2v_1x2v
.text
.global bli_sgemm_ukrgen_sme_sf_1vx2v_1x2v_asm
.type bli_sgemm_ukrgen_sme_sf_1vx2v_1x2v_asm, %function
bli_sgemm_ukrgen_sme_sf_1vx2v_1x2v_asm:
.cfi_startproc
add sp,sp,#-80
.cfi_adjust_cfa_offset 80
str x19, [sp]
.cfi_rel_offset x19, 0
str d8, [sp, #8]
.cfi_rel_offset d8, 8
str d9, [sp, #16]
.cfi_rel_offset d9, 16
str d10, [sp, #24]
.cfi_rel_offset d10, 24
str d11, [sp, #32]
.cfi_rel_offset d11, 32
str d12, [sp, #40]
.cfi_rel_offset d12, 40
str d13, [sp, #48]
.cfi_rel_offset d13, 48
str d14, [sp, #56]
.cfi_rel_offset d14, 56
str d15, [sp, #64]
.cfi_rel_offset d15, 64
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
mov x1,x0
mov x2,x0
mov x9,x0
incb x1, ALL, MUL #1
mov x10,x0
incb x2, ALL, MUL #1
incb x9, ALL, MUL #1
add x11,x0,x6
add x1,x1,x6
mov x16,x7
mov x12,#0
incb x10, ALL, MUL #1
add x17,x0,x6
add x2,x2,x6
add x19,x0,x6, LSL #1
add x9,x9,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr1_slices:
st1w {za0h.s[w12, 0]}, p0, [x0]
st1w {za1h.s[w12, 0]}, p0, [x10]
st1w {za0h.s[w12, 1]}, p0, [x17]
st1w {za1h.s[w12, 1]}, p0, [x2]
st1w {za0h.s[w12, 2]}, p0, [x19]
st1w {za1h.s[w12, 2]}, p0, [x9]
st1w {za0h.s[w12, 3]}, p0, [x11]
st1w {za1h.s[w12, 3]}, p0, [x1]
add x0,x0,x6, LSL #2
add x10,x10,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x19,x19,x6, LSL #2
add x9,x9,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr1_slices
st1w {z0.s}, p0, [x0]
st1w {z1.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
add x1,x0,x6
ld1rw {z2.s}, p0/z, [x4]
mov x2,x7
mov x12,#0
add x9,x0,x6
add x10,x0,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr2_slices:
mova z3.s,p0/m,za0h.s[w12,0]
mova z4.s,p0/m,za1h.s[w12,0]
mova z5.s,p0/m,za0h.s[w12,1]
mova z6.s,p0/m,za1h.s[w12,1]
mova z7.s,p0/m,za0h.s[w12,2]
mova z16.s,p0/m,za1h.s[w12,2]
mova z17.s,p0/m,za0h.s[w12,3]
mova z18.s,p0/m,za1h.s[w12,3]
fmul z19.s,z3.s,z2.s
fmul z3.s,z4.s,z2.s
fmul z4.s,z5.s,z2.s
fmul z5.s,z6.s,z2.s
fmul z6.s,z7.s,z2.s
fmul z7.s,z16.s,z2.s
fmul z16.s,z17.s,z2.s
fmul z17.s,z18.s,z2.s
st1w {z19.s}, p0, [x0]
st1w {z3.s}, p0, [x0, #1, MUL VL]
st1w {z4.s}, p0, [x9]
st1w {z5.s}, p0, [x9, #1, MUL VL]
st1w {z6.s}, p0, [x10]
st1w {z7.s}, p0, [x10, #1, MUL VL]
st1w {z16.s}, p0, [x1]
st1w {z17.s}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #2
add x9,x9,x6, LSL #2
add x10,x10,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x2,x2,#-4
cbnz x2,.ukr2_slices
sub x0,x0,x8
fmul z3.s,z0.s,z2.s
add x0,x0,x8
fmul z0.s,z1.s,z2.s
st1w {z3.s}, p0, [x0]
st1w {z0.s}, p0, [x0, #1, MUL VL]
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
mova z2.s,p0/m,za0h.s[w12,0]
ld1w {z3.s}, p0/z, [x0]
mova z4.s,p0/m,za1h.s[w12,0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
mova z6.s,p0/m,za0h.s[w12,1]
ld1w {z7.s}, p0/z, [x10]
mova z16.s,p0/m,za1h.s[w12,1]
ld1w {z17.s}, p0/z, [x10, #1, MUL VL]
mova z18.s,p0/m,za0h.s[w12,2]
ld1w {z19.s}, p0/z, [x11]
mova z20.s,p0/m,za1h.s[w12,2]
ld1w {z21.s}, p0/z, [x11, #1, MUL VL]
mova z22.s,p0/m,za0h.s[w12,3]
ld1w {z23.s}, p0/z, [x1]
mova z24.s,p0/m,za1h.s[w12,3]
ld1w {z25.s}, p0/z, [x1, #1, MUL VL]
fadd z3.s,z2.s,z3.s
fadd z5.s,z4.s,z5.s
fadd z7.s,z6.s,z7.s
fadd z17.s,z16.s,z17.s
fadd z19.s,z18.s,z19.s
fadd z21.s,z20.s,z21.s
fadd z23.s,z22.s,z23.s
fadd z25.s,z24.s,z25.s
st1w {z3.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
st1w {z7.s}, p0, [x16]
st1w {z17.s}, p0, [x16, #1, MUL VL]
st1w {z19.s}, p0, [x17]
st1w {z21.s}, p0, [x17, #1, MUL VL]
st1w {z23.s}, p0, [x2]
st1w {z25.s}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x9,x9,#-4
cbnz x9,.ukr3_slices
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
add x1,x0,x6
add x2,x3,x6
ld1rw {z2.s}, p0/z, [x4]
mov x9,x7
mov x12,#0
add x10,x0,x6
add x11,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x16,x3,x6
add x17,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr4_slices:
mova z3.s,p0/m,za0h.s[w12,0]
ld1w {z4.s}, p0/z, [x0]
mova z5.s,p0/m,za1h.s[w12,0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
mova z7.s,p0/m,za0h.s[w12,1]
ld1w {z16.s}, p0/z, [x10]
mova z17.s,p0/m,za1h.s[w12,1]
ld1w {z18.s}, p0/z, [x10, #1, MUL VL]
mova z19.s,p0/m,za0h.s[w12,2]
ld1w {z20.s}, p0/z, [x11]
mova z21.s,p0/m,za1h.s[w12,2]
ld1w {z22.s}, p0/z, [x11, #1, MUL VL]
mova z23.s,p0/m,za0h.s[w12,3]
ld1w {z24.s}, p0/z, [x1]
mova z25.s,p0/m,za1h.s[w12,3]
ld1w {z26.s}, p0/z, [x1, #1, MUL VL]
fmla z4.s,p0/m,z3.s,z2.s
fmla z6.s,p0/m,z5.s,z2.s
fmla z16.s,p0/m,z7.s,z2.s
fmla z18.s,p0/m,z17.s,z2.s
fmla z20.s,p0/m,z19.s,z2.s
fmla z22.s,p0/m,z21.s,z2.s
fmla z24.s,p0/m,z23.s,z2.s
fmla z26.s,p0/m,z25.s,z2.s
st1w {z4.s}, p0, [x3]
st1w {z6.s}, p0, [x3, #1, MUL VL]
st1w {z16.s}, p0, [x16]
st1w {z18.s}, p0, [x16, #1, MUL VL]
st1w {z20.s}, p0, [x17]
st1w {z22.s}, p0, [x17, #1, MUL VL]
st1w {z24.s}, p0, [x2]
st1w {z26.s}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x9,x9,#-4
cbnz x9,.ukr4_slices
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
add x1,x0,x6
add x2,x3,x6
ld1rw {z2.s}, p0/z, [x5]
mov x9,x7
mov x12,#0
add x10,x0,x6
add x11,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x16,x3,x6
add x17,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr5_slices:
mova z3.s,p0/m,za0h.s[w12,0]
ld1w {z4.s}, p0/z, [x0]
mova z5.s,p0/m,za1h.s[w12,0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
fmla z3.s,p0/m,z4.s,z2.s
fmla z5.s,p0/m,z6.s,z2.s
mova za0h.s[w12,0],p0/m,z3.s
mova za1h.s[w12,0],p0/m,z5.s
mova z4.s,p0/m,za0h.s[w12,1]
ld1w {z6.s}, p0/z, [x10]
mova z7.s,p0/m,za1h.s[w12,1]
ld1w {z16.s}, p0/z, [x10, #1, MUL VL]
fmla z4.s,p0/m,z6.s,z2.s
fmla z7.s,p0/m,z16.s,z2.s
mova za0h.s[w12,1],p0/m,z4.s
mova za1h.s[w12,1],p0/m,z7.s
mova z6.s,p0/m,za0h.s[w12,2]
ld1w {z16.s}, p0/z, [x11]
mova z17.s,p0/m,za1h.s[w12,2]
ld1w {z18.s}, p0/z, [x11, #1, MUL VL]
fmla z6.s,p0/m,z16.s,z2.s
fmla z17.s,p0/m,z18.s,z2.s
mova za0h.s[w12,2],p0/m,z6.s
mova za1h.s[w12,2],p0/m,z17.s
mova z16.s,p0/m,za0h.s[w12,3]
ld1w {z18.s}, p0/z, [x1]
mova z19.s,p0/m,za1h.s[w12,3]
ld1w {z20.s}, p0/z, [x1, #1, MUL VL]
fmla z16.s,p0/m,z18.s,z2.s
fmla z19.s,p0/m,z20.s,z2.s
st1w {z3.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
st1w {z4.s}, p0, [x16]
st1w {z7.s}, p0, [x16, #1, MUL VL]
st1w {z6.s}, p0, [x17]
st1w {z17.s}, p0, [x17, #1, MUL VL]
st1w {z16.s}, p0, [x2]
st1w {z19.s}, p0, [x2, #1, MUL VL]
mova za0h.s[w12,3],p0/m,z16.s
mova za1h.s[w12,3],p0/m,z19.s
add x0,x0,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x9,x9,#-4
cbnz x9,.ukr5_slices
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
add x1,x0,x6
add x2,x3,x6
ld1rw {z2.s}, p0/z, [x5]
ld1rw {z3.s}, p0/z, [x4]
mov x9,x7
mov x12,#0
add x10,x0,x6
add x11,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x16,x3,x6
add x17,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr6_slices:
ld1w {z4.s}, p0/z, [x0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
ld1w {z6.s}, p0/z, [x10]
ld1w {z7.s}, p0/z, [x10, #1, MUL VL]
ld1w {z16.s}, p0/z, [x11]
ld1w {z17.s}, p0/z, [x11, #1, MUL VL]
ld1w {z18.s}, p0/z, [x1]
ld1w {z19.s}, p0/z, [x1, #1, MUL VL]
fmul z4.s,z4.s,z2.s
mova z20.s,p0/m,za0h.s[w12,0]
fmul z5.s,z5.s,z2.s
mova z21.s,p0/m,za1h.s[w12,0]
fmul z6.s,z6.s,z2.s
mova z22.s,p0/m,za0h.s[w12,1]
fmul z7.s,z7.s,z2.s
mova z23.s,p0/m,za1h.s[w12,1]
fmul z16.s,z16.s,z2.s
mova z24.s,p0/m,za0h.s[w12,2]
fmul z17.s,z17.s,z2.s
mova z25.s,p0/m,za1h.s[w12,2]
fmul z18.s,z18.s,z2.s
mova z26.s,p0/m,za0h.s[w12,3]
fmul z19.s,z19.s,z2.s
mova z27.s,p0/m,za1h.s[w12,3]
fmla z4.s,p0/m,z20.s,z3.s
fmla z5.s,p0/m,z21.s,z3.s
fmla z6.s,p0/m,z22.s,z3.s
fmla z7.s,p0/m,z23.s,z3.s
fmla z16.s,p0/m,z24.s,z3.s
fmla z17.s,p0/m,z25.s,z3.s
fmla z18.s,p0/m,z26.s,z3.s
fmla z19.s,p0/m,z27.s,z3.s
st1w {z4.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
st1w {z6.s}, p0, [x16]
st1w {z7.s}, p0, [x16, #1, MUL VL]
st1w {z16.s}, p0, [x17]
st1w {z17.s}, p0, [x17, #1, MUL VL]
st1w {z18.s}, p0, [x2]
st1w {z19.s}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x9,x9,#-4
cbnz x9,.ukr6_slices
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
ldr x19, [sp]
.cfi_restore x19
ldr d8, [sp, #8]
.cfi_restore d8
ldr d9, [sp, #16]
.cfi_restore d9
ldr d10, [sp, #24]
.cfi_restore d10
ldr d11, [sp, #32]
.cfi_restore d11
ldr d12, [sp, #40]
.cfi_restore d12
ldr d13, [sp, #48]
.cfi_restore d13
ldr d14, [sp, #56]
.cfi_restore d14
ldr d15, [sp, #64]
.cfi_restore d15
add sp,sp,#80
.cfi_adjust_cfa_offset -80
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
add sp,sp,#-80
.cfi_adjust_cfa_offset 80
str x19, [sp]
.cfi_rel_offset x19, 0
str x20, [sp, #8]
.cfi_rel_offset x20, 8
str d8, [sp, #16]
.cfi_rel_offset d8, 16
str d9, [sp, #24]
.cfi_rel_offset d9, 24
str d10, [sp, #32]
.cfi_rel_offset d10, 32
str d11, [sp, #40]
.cfi_rel_offset d11, 40
str d12, [sp, #48]
.cfi_rel_offset d12, 48
str d13, [sp, #56]
.cfi_rel_offset d13, 56
str d14, [sp, #64]
.cfi_rel_offset d14, 64
str d15, [sp, #72]
.cfi_rel_offset d15, 72
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
mov x1,x0
mov x2,x0
mov x10,x0
incb x1, ALL, MUL #1
mov x11,x0
incb x2, ALL, MUL #1
incb x10, ALL, MUL #1
add x16,x0,x6
add x1,x1,x6
mov x17,x7
mov x12,#0
incb x11, ALL, MUL #1
add x19,x0,x6
add x2,x2,x6
add x20,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr1_slices:
st1w {za0h.s[w12, 0]}, p0, [x0]
st1w {za1h.s[w12, 0]}, p0, [x11]
st1w {za0h.s[w12, 1]}, p0, [x19]
st1w {za1h.s[w12, 1]}, p0, [x2]
st1w {za0h.s[w12, 2]}, p0, [x20]
st1w {za1h.s[w12, 2]}, p0, [x10]
st1w {za0h.s[w12, 3]}, p0, [x16]
st1w {za1h.s[w12, 3]}, p0, [x1]
add x0,x0,x6, LSL #2
add x11,x11,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x10,x10,x6, LSL #2
add x16,x16,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x17,x17,#-4
cbnz x17,.ukr1_slices
st1w {z0.s}, p0, [x0]
st1w {z1.s}, p0, [x0, #1, MUL VL]
st1w {z2.s}, p0, [x0, x9, lsl #2]
add x0,x0,x6
st1w {z3.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
add x1,x0,x6
ld1rw {z4.s}, p0/z, [x4]
mov x2,x7
mov x12,#0
add x10,x0,x6
add x11,x0,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr2_slices:
mova z5.s,p0/m,za0h.s[w12,0]
mova z6.s,p0/m,za1h.s[w12,0]
mova z7.s,p0/m,za0h.s[w12,1]
mova z16.s,p0/m,za1h.s[w12,1]
mova z17.s,p0/m,za0h.s[w12,2]
mova z18.s,p0/m,za1h.s[w12,2]
mova z19.s,p0/m,za0h.s[w12,3]
mova z20.s,p0/m,za1h.s[w12,3]
fmul z21.s,z5.s,z4.s
fmul z5.s,z6.s,z4.s
fmul z6.s,z7.s,z4.s
fmul z7.s,z16.s,z4.s
fmul z16.s,z17.s,z4.s
fmul z17.s,z18.s,z4.s
fmul z18.s,z19.s,z4.s
fmul z19.s,z20.s,z4.s
st1w {z21.s}, p0, [x0]
st1w {z5.s}, p0, [x0, #1, MUL VL]
st1w {z6.s}, p0, [x10]
st1w {z7.s}, p0, [x10, #1, MUL VL]
st1w {z16.s}, p0, [x11]
st1w {z17.s}, p0, [x11, #1, MUL VL]
st1w {z18.s}, p0, [x1]
st1w {z19.s}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x2,x2,#-4
cbnz x2,.ukr2_slices
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
add x1,x0,x6
add x2,x3,x6
mov x10,x7
mov x12,#0
add x11,x0,x6
add x16,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x17,x3,x6
add x19,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr3_slices:
mova z4.s,p0/m,za0h.s[w12,0]
ld1w {z5.s}, p0/z, [x0]
mova z6.s,p0/m,za1h.s[w12,0]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
mova z16.s,p0/m,za0h.s[w12,1]
ld1w {z17.s}, p0/z, [x11]
mova z18.s,p0/m,za1h.s[w12,1]
ld1w {z19.s}, p0/z, [x11, #1, MUL VL]
mova z20.s,p0/m,za0h.s[w12,2]
ld1w {z21.s}, p0/z, [x16]
mova z22.s,p0/m,za1h.s[w12,2]
ld1w {z23.s}, p0/z, [x16, #1, MUL VL]
mova z24.s,p0/m,za0h.s[w12,3]
ld1w {z25.s}, p0/z, [x1]
mova z26.s,p0/m,za1h.s[w12,3]
ld1w {z27.s}, p0/z, [x1, #1, MUL VL]
fadd z5.s,z4.s,z5.s
fadd z7.s,z6.s,z7.s
fadd z17.s,z16.s,z17.s
fadd z19.s,z18.s,z19.s
fadd z21.s,z20.s,z21.s
fadd z23.s,z22.s,z23.s
fadd z25.s,z24.s,z25.s
fadd z27.s,z26.s,z27.s
st1w {z5.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
st1w {z17.s}, p0, [x17]
st1w {z19.s}, p0, [x17, #1, MUL VL]
st1w {z21.s}, p0, [x19]
st1w {z23.s}, p0, [x19, #1, MUL VL]
st1w {z25.s}, p0, [x2]
st1w {z27.s}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x10,x10,#-4
cbnz x10,.ukr3_slices
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
add x1,x0,x6
add x2,x3,x6
ld1rw {z4.s}, p0/z, [x4]
mov x10,x7
mov x12,#0
add x11,x0,x6
add x16,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x17,x3,x6
add x19,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr4_slices:
mova z5.s,p0/m,za0h.s[w12,0]
ld1w {z6.s}, p0/z, [x0]
mova z7.s,p0/m,za1h.s[w12,0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
mova z17.s,p0/m,za0h.s[w12,1]
ld1w {z18.s}, p0/z, [x11]
mova z19.s,p0/m,za1h.s[w12,1]
ld1w {z20.s}, p0/z, [x11, #1, MUL VL]
mova z21.s,p0/m,za0h.s[w12,2]
ld1w {z22.s}, p0/z, [x16]
mova z23.s,p0/m,za1h.s[w12,2]
ld1w {z24.s}, p0/z, [x16, #1, MUL VL]
mova z25.s,p0/m,za0h.s[w12,3]
ld1w {z26.s}, p0/z, [x1]
mova z27.s,p0/m,za1h.s[w12,3]
ld1w {z28.s}, p0/z, [x1, #1, MUL VL]
fmla z6.s,p0/m,z5.s,z4.s
fmla z16.s,p0/m,z7.s,z4.s
fmla z18.s,p0/m,z17.s,z4.s
fmla z20.s,p0/m,z19.s,z4.s
fmla z22.s,p0/m,z21.s,z4.s
fmla z24.s,p0/m,z23.s,z4.s
fmla z26.s,p0/m,z25.s,z4.s
fmla z28.s,p0/m,z27.s,z4.s
st1w {z6.s}, p0, [x3]
st1w {z16.s}, p0, [x3, #1, MUL VL]
st1w {z18.s}, p0, [x17]
st1w {z20.s}, p0, [x17, #1, MUL VL]
st1w {z22.s}, p0, [x19]
st1w {z24.s}, p0, [x19, #1, MUL VL]
st1w {z26.s}, p0, [x2]
st1w {z28.s}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x10,x10,#-4
cbnz x10,.ukr4_slices
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
add x1,x0,x6
add x2,x3,x6
ld1rw {z4.s}, p0/z, [x5]
mov x10,x7
mov x12,#0
add x11,x0,x6
add x16,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x17,x3,x6
add x19,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr5_slices:
mova z5.s,p0/m,za0h.s[w12,0]
ld1w {z6.s}, p0/z, [x0]
mova z7.s,p0/m,za1h.s[w12,0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
fmla z5.s,p0/m,z6.s,z4.s
fmla z7.s,p0/m,z16.s,z4.s
mova za0h.s[w12,0],p0/m,z5.s
mova za1h.s[w12,0],p0/m,z7.s
mova z6.s,p0/m,za0h.s[w12,1]
ld1w {z16.s}, p0/z, [x11]
mova z17.s,p0/m,za1h.s[w12,1]
ld1w {z18.s}, p0/z, [x11, #1, MUL VL]
fmla z6.s,p0/m,z16.s,z4.s
fmla z17.s,p0/m,z18.s,z4.s
mova za0h.s[w12,1],p0/m,z6.s
mova za1h.s[w12,1],p0/m,z17.s
mova z16.s,p0/m,za0h.s[w12,2]
ld1w {z18.s}, p0/z, [x16]
mova z19.s,p0/m,za1h.s[w12,2]
ld1w {z20.s}, p0/z, [x16, #1, MUL VL]
fmla z16.s,p0/m,z18.s,z4.s
fmla z19.s,p0/m,z20.s,z4.s
mova za0h.s[w12,2],p0/m,z16.s
mova za1h.s[w12,2],p0/m,z19.s
mova z18.s,p0/m,za0h.s[w12,3]
ld1w {z20.s}, p0/z, [x1]
mova z21.s,p0/m,za1h.s[w12,3]
ld1w {z22.s}, p0/z, [x1, #1, MUL VL]
fmla z18.s,p0/m,z20.s,z4.s
fmla z21.s,p0/m,z22.s,z4.s
st1w {z5.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
st1w {z6.s}, p0, [x17]
st1w {z17.s}, p0, [x17, #1, MUL VL]
st1w {z16.s}, p0, [x19]
st1w {z19.s}, p0, [x19, #1, MUL VL]
st1w {z18.s}, p0, [x2]
st1w {z21.s}, p0, [x2, #1, MUL VL]
mova za0h.s[w12,3],p0/m,z18.s
mova za1h.s[w12,3],p0/m,z21.s
add x0,x0,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x10,x10,#-4
cbnz x10,.ukr5_slices
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
add x1,x0,x6
add x2,x3,x6
ld1rw {z4.s}, p0/z, [x5]
ld1rw {z5.s}, p0/z, [x4]
mov x10,x7
mov x12,#0
add x11,x0,x6
add x16,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x17,x3,x6
add x19,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr6_slices:
ld1w {z6.s}, p0/z, [x0]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
ld1w {z16.s}, p0/z, [x11]
ld1w {z17.s}, p0/z, [x11, #1, MUL VL]
ld1w {z18.s}, p0/z, [x16]
ld1w {z19.s}, p0/z, [x16, #1, MUL VL]
ld1w {z20.s}, p0/z, [x1]
ld1w {z21.s}, p0/z, [x1, #1, MUL VL]
fmul z6.s,z6.s,z4.s
mova z22.s,p0/m,za0h.s[w12,0]
fmul z7.s,z7.s,z4.s
mova z23.s,p0/m,za1h.s[w12,0]
fmul z16.s,z16.s,z4.s
mova z24.s,p0/m,za0h.s[w12,1]
fmul z17.s,z17.s,z4.s
mova z25.s,p0/m,za1h.s[w12,1]
fmul z18.s,z18.s,z4.s
mova z26.s,p0/m,za0h.s[w12,2]
fmul z19.s,z19.s,z4.s
mova z27.s,p0/m,za1h.s[w12,2]
fmul z20.s,z20.s,z4.s
mova z28.s,p0/m,za0h.s[w12,3]
fmul z21.s,z21.s,z4.s
mova z29.s,p0/m,za1h.s[w12,3]
fmla z6.s,p0/m,z22.s,z5.s
fmla z7.s,p0/m,z23.s,z5.s
fmla z16.s,p0/m,z24.s,z5.s
fmla z17.s,p0/m,z25.s,z5.s
fmla z18.s,p0/m,z26.s,z5.s
fmla z19.s,p0/m,z27.s,z5.s
fmla z20.s,p0/m,z28.s,z5.s
fmla z21.s,p0/m,z29.s,z5.s
st1w {z6.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
st1w {z16.s}, p0, [x17]
st1w {z17.s}, p0, [x17, #1, MUL VL]
st1w {z18.s}, p0, [x19]
st1w {z19.s}, p0, [x19, #1, MUL VL]
st1w {z20.s}, p0, [x2]
st1w {z21.s}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x10,x10,#-4
cbnz x10,.ukr6_slices
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
ldr x19, [sp]
.cfi_restore x19
ldr x20, [sp, #8]
.cfi_restore x20
ldr d8, [sp, #16]
.cfi_restore d8
ldr d9, [sp, #24]
.cfi_restore d9
ldr d10, [sp, #32]
.cfi_restore d10
ldr d11, [sp, #40]
.cfi_restore d11
ldr d12, [sp, #48]
.cfi_restore d12
ldr d13, [sp, #56]
.cfi_restore d13
ldr d14, [sp, #64]
.cfi_restore d14
ldr d15, [sp, #72]
.cfi_restore d15
add sp,sp,#80
.cfi_adjust_cfa_offset -80
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
add sp,sp,#-80
.cfi_adjust_cfa_offset 80
str x19, [sp]
.cfi_rel_offset x19, 0
str x20, [sp, #8]
.cfi_rel_offset x20, 8
str d8, [sp, #16]
.cfi_rel_offset d8, 16
str d9, [sp, #24]
.cfi_rel_offset d9, 24
str d10, [sp, #32]
.cfi_rel_offset d10, 32
str d11, [sp, #40]
.cfi_rel_offset d11, 40
str d12, [sp, #48]
.cfi_rel_offset d12, 48
str d13, [sp, #56]
.cfi_rel_offset d13, 56
str d14, [sp, #64]
.cfi_rel_offset d14, 64
str d15, [sp, #72]
.cfi_rel_offset d15, 72
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
mov x1,x0
mov x2,x0
mov x10,x0
incb x1, ALL, MUL #1
mov x11,x0
incb x2, ALL, MUL #1
incb x10, ALL, MUL #1
add x16,x0,x6
add x1,x1,x6
mov x17,x7
mov x12,#0
incb x11, ALL, MUL #1
add x19,x0,x6
add x2,x2,x6
add x20,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr1_slices:
st1w {za0h.s[w12, 0]}, p0, [x0]
st1w {za1h.s[w12, 0]}, p0, [x11]
st1w {za0h.s[w12, 1]}, p0, [x19]
st1w {za1h.s[w12, 1]}, p0, [x2]
st1w {za0h.s[w12, 2]}, p0, [x20]
st1w {za1h.s[w12, 2]}, p0, [x10]
st1w {za0h.s[w12, 3]}, p0, [x16]
st1w {za1h.s[w12, 3]}, p0, [x1]
add x0,x0,x6, LSL #2
add x11,x11,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x10,x10,x6, LSL #2
add x16,x16,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x17,x17,#-4
cbnz x17,.ukr1_slices
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
add x1,x0,x6
ld1rw {z6.s}, p0/z, [x4]
mov x2,x7
mov x12,#0
add x10,x0,x6
add x11,x0,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr2_slices:
mova z7.s,p0/m,za0h.s[w12,0]
mova z16.s,p0/m,za1h.s[w12,0]
mova z17.s,p0/m,za0h.s[w12,1]
mova z18.s,p0/m,za1h.s[w12,1]
mova z19.s,p0/m,za0h.s[w12,2]
mova z20.s,p0/m,za1h.s[w12,2]
mova z21.s,p0/m,za0h.s[w12,3]
mova z22.s,p0/m,za1h.s[w12,3]
fmul z23.s,z7.s,z6.s
fmul z7.s,z16.s,z6.s
fmul z16.s,z17.s,z6.s
fmul z17.s,z18.s,z6.s
fmul z18.s,z19.s,z6.s
fmul z19.s,z20.s,z6.s
fmul z20.s,z21.s,z6.s
fmul z21.s,z22.s,z6.s
st1w {z23.s}, p0, [x0]
st1w {z7.s}, p0, [x0, #1, MUL VL]
st1w {z16.s}, p0, [x10]
st1w {z17.s}, p0, [x10, #1, MUL VL]
st1w {z18.s}, p0, [x11]
st1w {z19.s}, p0, [x11, #1, MUL VL]
st1w {z20.s}, p0, [x1]
st1w {z21.s}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x2,x2,#-4
cbnz x2,.ukr2_slices
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
add x1,x0,x6
add x2,x3,x6
mov x10,x7
mov x12,#0
add x11,x0,x6
add x16,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x17,x3,x6
add x19,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr3_slices:
mova z6.s,p0/m,za0h.s[w12,0]
ld1w {z7.s}, p0/z, [x0]
mova z16.s,p0/m,za1h.s[w12,0]
ld1w {z17.s}, p0/z, [x0, #1, MUL VL]
mova z18.s,p0/m,za0h.s[w12,1]
ld1w {z19.s}, p0/z, [x11]
mova z20.s,p0/m,za1h.s[w12,1]
ld1w {z21.s}, p0/z, [x11, #1, MUL VL]
mova z22.s,p0/m,za0h.s[w12,2]
ld1w {z23.s}, p0/z, [x16]
mova z24.s,p0/m,za1h.s[w12,2]
ld1w {z25.s}, p0/z, [x16, #1, MUL VL]
mova z26.s,p0/m,za0h.s[w12,3]
ld1w {z27.s}, p0/z, [x1]
mova z28.s,p0/m,za1h.s[w12,3]
ld1w {z29.s}, p0/z, [x1, #1, MUL VL]
fadd z7.s,z6.s,z7.s
fadd z17.s,z16.s,z17.s
fadd z19.s,z18.s,z19.s
fadd z21.s,z20.s,z21.s
fadd z23.s,z22.s,z23.s
fadd z25.s,z24.s,z25.s
fadd z27.s,z26.s,z27.s
fadd z29.s,z28.s,z29.s
st1w {z7.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
st1w {z19.s}, p0, [x17]
st1w {z21.s}, p0, [x17, #1, MUL VL]
st1w {z23.s}, p0, [x19]
st1w {z25.s}, p0, [x19, #1, MUL VL]
st1w {z27.s}, p0, [x2]
st1w {z29.s}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x10,x10,#-4
cbnz x10,.ukr3_slices
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
add x1,x0,x6
add x2,x3,x6
ld1rw {z6.s}, p0/z, [x4]
mov x10,x7
mov x12,#0
add x11,x0,x6
add x16,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x17,x3,x6
add x19,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr4_slices:
mova z7.s,p0/m,za0h.s[w12,0]
ld1w {z16.s}, p0/z, [x0]
mova z17.s,p0/m,za1h.s[w12,0]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
mova z19.s,p0/m,za0h.s[w12,1]
ld1w {z20.s}, p0/z, [x11]
mova z21.s,p0/m,za1h.s[w12,1]
ld1w {z22.s}, p0/z, [x11, #1, MUL VL]
mova z23.s,p0/m,za0h.s[w12,2]
ld1w {z24.s}, p0/z, [x16]
mova z25.s,p0/m,za1h.s[w12,2]
ld1w {z26.s}, p0/z, [x16, #1, MUL VL]
mova z27.s,p0/m,za0h.s[w12,3]
ld1w {z28.s}, p0/z, [x1]
mova z29.s,p0/m,za1h.s[w12,3]
ld1w {z30.s}, p0/z, [x1, #1, MUL VL]
fmla z16.s,p0/m,z7.s,z6.s
fmla z18.s,p0/m,z17.s,z6.s
fmla z20.s,p0/m,z19.s,z6.s
fmla z22.s,p0/m,z21.s,z6.s
fmla z24.s,p0/m,z23.s,z6.s
fmla z26.s,p0/m,z25.s,z6.s
fmla z28.s,p0/m,z27.s,z6.s
fmla z30.s,p0/m,z29.s,z6.s
st1w {z16.s}, p0, [x3]
st1w {z18.s}, p0, [x3, #1, MUL VL]
st1w {z20.s}, p0, [x17]
st1w {z22.s}, p0, [x17, #1, MUL VL]
st1w {z24.s}, p0, [x19]
st1w {z26.s}, p0, [x19, #1, MUL VL]
st1w {z28.s}, p0, [x2]
st1w {z30.s}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x10,x10,#-4
cbnz x10,.ukr4_slices
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
add x1,x0,x6
add x2,x3,x6
ld1rw {z6.s}, p0/z, [x5]
mov x10,x7
mov x12,#0
add x11,x0,x6
add x16,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x17,x3,x6
add x19,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr5_slices:
mova z7.s,p0/m,za0h.s[w12,0]
ld1w {z16.s}, p0/z, [x0]
mova z17.s,p0/m,za1h.s[w12,0]
ld1w {z18.s}, p0/z, [x0, #1, MUL VL]
fmla z7.s,p0/m,z16.s,z6.s
fmla z17.s,p0/m,z18.s,z6.s
mova za0h.s[w12,0],p0/m,z7.s
mova za1h.s[w12,0],p0/m,z17.s
mova z16.s,p0/m,za0h.s[w12,1]
ld1w {z18.s}, p0/z, [x11]
mova z19.s,p0/m,za1h.s[w12,1]
ld1w {z20.s}, p0/z, [x11, #1, MUL VL]
fmla z16.s,p0/m,z18.s,z6.s
fmla z19.s,p0/m,z20.s,z6.s
mova za0h.s[w12,1],p0/m,z16.s
mova za1h.s[w12,1],p0/m,z19.s
mova z18.s,p0/m,za0h.s[w12,2]
ld1w {z20.s}, p0/z, [x16]
mova z21.s,p0/m,za1h.s[w12,2]
ld1w {z22.s}, p0/z, [x16, #1, MUL VL]
fmla z18.s,p0/m,z20.s,z6.s
fmla z21.s,p0/m,z22.s,z6.s
mova za0h.s[w12,2],p0/m,z18.s
mova za1h.s[w12,2],p0/m,z21.s
mova z20.s,p0/m,za0h.s[w12,3]
ld1w {z22.s}, p0/z, [x1]
mova z23.s,p0/m,za1h.s[w12,3]
ld1w {z24.s}, p0/z, [x1, #1, MUL VL]
fmla z20.s,p0/m,z22.s,z6.s
fmla z23.s,p0/m,z24.s,z6.s
st1w {z7.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
st1w {z16.s}, p0, [x17]
st1w {z19.s}, p0, [x17, #1, MUL VL]
st1w {z18.s}, p0, [x19]
st1w {z21.s}, p0, [x19, #1, MUL VL]
st1w {z20.s}, p0, [x2]
st1w {z23.s}, p0, [x2, #1, MUL VL]
mova za0h.s[w12,3],p0/m,z20.s
mova za1h.s[w12,3],p0/m,z23.s
add x0,x0,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x10,x10,#-4
cbnz x10,.ukr5_slices
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
add x1,x0,x6
add x2,x3,x6
ld1rw {z6.s}, p0/z, [x5]
ld1rw {z7.s}, p0/z, [x4]
mov x10,x7
mov x12,#0
add x11,x0,x6
add x16,x0,x6, LSL #1
add x1,x1,x6, LSL #1
add x17,x3,x6
add x19,x3,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr6_slices:
ld1w {z16.s}, p0/z, [x0]
ld1w {z17.s}, p0/z, [x0, #1, MUL VL]
ld1w {z18.s}, p0/z, [x11]
ld1w {z19.s}, p0/z, [x11, #1, MUL VL]
ld1w {z20.s}, p0/z, [x16]
ld1w {z21.s}, p0/z, [x16, #1, MUL VL]
ld1w {z22.s}, p0/z, [x1]
ld1w {z23.s}, p0/z, [x1, #1, MUL VL]
fmul z16.s,z16.s,z6.s
mova z24.s,p0/m,za0h.s[w12,0]
fmul z17.s,z17.s,z6.s
mova z25.s,p0/m,za1h.s[w12,0]
fmul z18.s,z18.s,z6.s
mova z26.s,p0/m,za0h.s[w12,1]
fmul z19.s,z19.s,z6.s
mova z27.s,p0/m,za1h.s[w12,1]
fmul z20.s,z20.s,z6.s
mova z28.s,p0/m,za0h.s[w12,2]
fmul z21.s,z21.s,z6.s
mova z29.s,p0/m,za1h.s[w12,2]
fmul z22.s,z22.s,z6.s
mova z30.s,p0/m,za0h.s[w12,3]
fmul z23.s,z23.s,z6.s
mova z31.s,p0/m,za1h.s[w12,3]
fmla z16.s,p0/m,z24.s,z7.s
fmla z17.s,p0/m,z25.s,z7.s
fmla z18.s,p0/m,z26.s,z7.s
fmla z19.s,p0/m,z27.s,z7.s
fmla z20.s,p0/m,z28.s,z7.s
fmla z21.s,p0/m,z29.s,z7.s
fmla z22.s,p0/m,z30.s,z7.s
fmla z23.s,p0/m,z31.s,z7.s
st1w {z16.s}, p0, [x3]
st1w {z17.s}, p0, [x3, #1, MUL VL]
st1w {z18.s}, p0, [x17]
st1w {z19.s}, p0, [x17, #1, MUL VL]
st1w {z20.s}, p0, [x19]
st1w {z21.s}, p0, [x19, #1, MUL VL]
st1w {z22.s}, p0, [x2]
st1w {z23.s}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
add x10,x10,#-4
cbnz x10,.ukr6_slices
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
ldr x19, [sp]
.cfi_restore x19
ldr x20, [sp, #8]
.cfi_restore x20
ldr d8, [sp, #16]
.cfi_restore d8
ldr d9, [sp, #24]
.cfi_restore d9
ldr d10, [sp, #32]
.cfi_restore d10
ldr d11, [sp, #40]
.cfi_restore d11
ldr d12, [sp, #48]
.cfi_restore d12
ldr d13, [sp, #56]
.cfi_restore d13
ldr d14, [sp, #64]
.cfi_restore d14
ldr d15, [sp, #72]
.cfi_restore d15
add sp,sp,#80
.cfi_adjust_cfa_offset -80
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
add sp,sp,#-144
.cfi_adjust_cfa_offset 144
str x19, [sp]
.cfi_rel_offset x19, 0
str x20, [sp, #8]
.cfi_rel_offset x20, 8
str x21, [sp, #16]
.cfi_rel_offset x21, 16
str x22, [sp, #24]
.cfi_rel_offset x22, 24
str x23, [sp, #32]
.cfi_rel_offset x23, 32
str x24, [sp, #40]
.cfi_rel_offset x24, 40
str x25, [sp, #48]
.cfi_rel_offset x25, 48
str x26, [sp, #56]
.cfi_rel_offset x26, 56
str x27, [sp, #64]
.cfi_rel_offset x27, 64
str x28, [sp, #72]
.cfi_rel_offset x28, 72
str d8, [sp, #80]
.cfi_rel_offset d8, 80
str d9, [sp, #88]
.cfi_rel_offset d9, 88
str d10, [sp, #96]
.cfi_rel_offset d10, 96
str d11, [sp, #104]
.cfi_rel_offset d11, 104
str d12, [sp, #112]
.cfi_rel_offset d12, 112
str d13, [sp, #120]
.cfi_rel_offset d13, 120
str d14, [sp, #128]
.cfi_rel_offset d14, 128
str d15, [sp, #136]
.cfi_rel_offset d15, 136
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
mov x1,x0
mov x2,x0
mov x10,x0
mov x11,x0
incb x1, ALL, MUL #1
mov x16,x0
mov x17,x0
incb x2, ALL, MUL #1
mov x19,x0
incb x10, ALL, MUL #1
incb x11, ALL, MUL #1
add x20,x0,x8
add x1,x1,x8
mov x21,x0
incb x16, ALL, MUL #1
incb x17, ALL, MUL #1
add x22,x0,x8
add x2,x2,x8
incb x19, ALL, MUL #1
add x23,x0,x8
add x10,x10,x8
add x24,x0,x6
add x11,x11,x6
add x20,x20,x6
add x1,x1,x6
mov x25,x7
mov x12,#0
incb x21, ALL, MUL #1
add x26,x0,x8
add x16,x16,x8
add x27,x0,x6
add x17,x17,x6
add x22,x22,x6
add x2,x2,x6
add x28,x0,x6, LSL #1
add x19,x19,x6, LSL #1
add x23,x23,x6, LSL #1
add x10,x10,x6, LSL #1
add x24,x24,x6, LSL #1
add x11,x11,x6, LSL #1
add x20,x20,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr1_slices:
st1w {za0h.s[w12, 0]}, p0, [x0]
st1w {za1h.s[w12, 0]}, p0, [x21]
st1w {za2h.s[w12, 0]}, p0, [x26]
st1w {za3h.s[w12, 0]}, p0, [x16]
st1w {za0h.s[w12, 1]}, p0, [x27]
st1w {za1h.s[w12, 1]}, p0, [x17]
st1w {za2h.s[w12, 1]}, p0, [x22]
st1w {za3h.s[w12, 1]}, p0, [x2]
st1w {za0h.s[w12, 2]}, p0, [x28]
st1w {za1h.s[w12, 2]}, p0, [x19]
st1w {za2h.s[w12, 2]}, p0, [x23]
st1w {za3h.s[w12, 2]}, p0, [x10]
st1w {za0h.s[w12, 3]}, p0, [x24]
st1w {za1h.s[w12, 3]}, p0, [x11]
st1w {za2h.s[w12, 3]}, p0, [x20]
st1w {za3h.s[w12, 3]}, p0, [x1]
add x0,x0,x6, LSL #2
add x21,x21,x6, LSL #2
add x26,x26,x6, LSL #2
add x16,x16,x6, LSL #2
add x27,x27,x6, LSL #2
add x17,x17,x6, LSL #2
add x22,x22,x6, LSL #2
add x2,x2,x6, LSL #2
add x28,x28,x6, LSL #2
add x19,x19,x6, LSL #2
add x23,x23,x6, LSL #2
add x10,x10,x6, LSL #2
add x24,x24,x6, LSL #2
add x11,x11,x6, LSL #2
add x20,x20,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x25,x25,#-4
cbnz x25,.ukr1_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x2,x2,x6
add x20,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
ld1rw {z4.s}, p0/z, [x4]
add x1,x1,x6
add x1,x1,x6, LSL #1
.ukr2_slices:
mova z5.s,p0/m,za0h.s[w12,0]
mova z6.s,p0/m,za1h.s[w12,0]
mova z7.s,p0/m,za2h.s[w12,0]
fmul z16.s,z5.s,z4.s
fmul z17.s,z6.s,z4.s
fmul z18.s,z7.s,z4.s
st1w {z16.s}, p0, [x0]
st1w {z17.s}, p0, [x0, #1, MUL VL]
st1w {z18.s}, p0, [x17]
mova z7.s,p0/m,za3h.s[w12,0]
mova z19.s,p0/m,za0h.s[w12,1]
mova z20.s,p0/m,za1h.s[w12,1]
mova z21.s,p0/m,za2h.s[w12,1]
mova z22.s,p0/m,za3h.s[w12,1]
mova z23.s,p0/m,za0h.s[w12,2]
mova z24.s,p0/m,za1h.s[w12,2]
mova z25.s,p0/m,za2h.s[w12,2]
mova z26.s,p0/m,za3h.s[w12,2]
mova z27.s,p0/m,za0h.s[w12,3]
mova z28.s,p0/m,za1h.s[w12,3]
mova z5.s,p0/m,za2h.s[w12,3]
mova z6.s,p0/m,za3h.s[w12,3]
fmul z29.s,z7.s,z4.s
fmul z7.s,z19.s,z4.s
fmul z19.s,z20.s,z4.s
fmul z20.s,z21.s,z4.s
fmul z21.s,z22.s,z4.s
fmul z22.s,z23.s,z4.s
fmul z23.s,z24.s,z4.s
fmul z24.s,z25.s,z4.s
fmul z25.s,z26.s,z4.s
fmul z26.s,z27.s,z4.s
fmul z16.s,z28.s,z4.s
fmul z17.s,z5.s,z4.s
fmul z18.s,z6.s,z4.s
st1w {z29.s}, p0, [x17, #1, MUL VL]
st1w {z7.s}, p0, [x19]
st1w {z19.s}, p0, [x19, #1, MUL VL]
st1w {z20.s}, p0, [x2]
st1w {z21.s}, p0, [x2, #1, MUL VL]
st1w {z22.s}, p0, [x20]
st1w {z23.s}, p0, [x20, #1, MUL VL]
st1w {z24.s}, p0, [x10]
st1w {z25.s}, p0, [x10, #1, MUL VL]
st1w {z26.s}, p0, [x11]
st1w {z16.s}, p0, [x11, #1, MUL VL]
st1w {z17.s}, p0, [x1]
st1w {z18.s}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr2_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
add x1,x1,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x20,x3,x8
add x2,x2,x6
add x21,x0,x6, LSL #1
add x22,x3,x8
add x10,x10,x6, LSL #1
add x23,x3,x6
add x11,x11,x6, LSL #1
add x24,x3,x8
add x24,x24,x6
add x1,x1,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x20,x20,x6
add x27,x3,x6, LSL #1
add x22,x22,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
.ukr3_slices:
mova z4.s,p0/m,za0h.s[w12,0]
ld1w {z5.s}, p0/z, [x0]
mova z6.s,p0/m,za1h.s[w12,0]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
fadd z5.s,z4.s,z5.s
fadd z7.s,z6.s,z7.s
st1w {z5.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
mova z16.s,p0/m,za2h.s[w12,0]
ld1w {z17.s}, p0/z, [x17]
mova z18.s,p0/m,za3h.s[w12,0]
ld1w {z19.s}, p0/z, [x17, #1, MUL VL]
mova z20.s,p0/m,za0h.s[w12,1]
ld1w {z21.s}, p0/z, [x19]
mova z22.s,p0/m,za1h.s[w12,1]
ld1w {z23.s}, p0/z, [x19, #1, MUL VL]
mova z24.s,p0/m,za2h.s[w12,1]
ld1w {z25.s}, p0/z, [x2]
mova z26.s,p0/m,za3h.s[w12,1]
ld1w {z27.s}, p0/z, [x2, #1, MUL VL]
mova z28.s,p0/m,za0h.s[w12,2]
ld1w {z29.s}, p0/z, [x21]
mova z30.s,p0/m,za1h.s[w12,2]
ld1w {z31.s}, p0/z, [x21, #1, MUL VL]
mova z8.s,p0/m,za2h.s[w12,2]
ld1w {z9.s}, p0/z, [x10]
mova z10.s,p0/m,za3h.s[w12,2]
ld1w {z11.s}, p0/z, [x10, #1, MUL VL]
mova z12.s,p0/m,za0h.s[w12,3]
ld1w {z13.s}, p0/z, [x11]
mova z14.s,p0/m,za1h.s[w12,3]
mova z4.s,p0/m,za2h.s[w12,3]
mova z6.s,p0/m,za3h.s[w12,3]
fadd z17.s,z16.s,z17.s
ld1w {z16.s}, p0/z, [x11, #1, MUL VL]
fadd z19.s,z18.s,z19.s
ld1w {z5.s}, p0/z, [x1]
ld1w {z7.s}, p0/z, [x1, #1, MUL VL]
fadd z21.s,z20.s,z21.s
fadd z23.s,z22.s,z23.s
fadd z25.s,z24.s,z25.s
fadd z27.s,z26.s,z27.s
fadd z29.s,z28.s,z29.s
fadd z31.s,z30.s,z31.s
fadd z9.s,z8.s,z9.s
fadd z11.s,z10.s,z11.s
fadd z13.s,z12.s,z13.s
fadd z16.s,z14.s,z16.s
fadd z5.s,z4.s,z5.s
fadd z7.s,z6.s,z7.s
st1w {z17.s}, p0, [x25]
st1w {z19.s}, p0, [x25, #1, MUL VL]
st1w {z21.s}, p0, [x26]
st1w {z23.s}, p0, [x26, #1, MUL VL]
st1w {z25.s}, p0, [x20]
st1w {z27.s}, p0, [x20, #1, MUL VL]
st1w {z29.s}, p0, [x27]
st1w {z31.s}, p0, [x27, #1, MUL VL]
st1w {z9.s}, p0, [x22]
st1w {z11.s}, p0, [x22, #1, MUL VL]
st1w {z13.s}, p0, [x23]
st1w {z16.s}, p0, [x23, #1, MUL VL]
st1w {z5.s}, p0, [x24]
st1w {z7.s}, p0, [x24, #1, MUL VL]
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x21,x21,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x20,x20,x6, LSL #2
add x27,x27,x6, LSL #2
add x22,x22,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr3_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x2,x2,x6
add x20,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
ld1rw {z4.s}, p0/z, [x4]
add x21,x3,x8
add x1,x1,x6
add x22,x3,x8
add x23,x3,x8
add x24,x3,x6
add x21,x21,x6
add x1,x1,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x22,x22,x6
add x27,x3,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
add x21,x21,x6, LSL #1
.ukr4_slices:
mova z5.s,p0/m,za0h.s[w12,0]
ld1w {z6.s}, p0/z, [x0]
mova z7.s,p0/m,za1h.s[w12,0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
mova z17.s,p0/m,za2h.s[w12,0]
ld1w {z18.s}, p0/z, [x17]
fmla z6.s,p0/m,z5.s,z4.s
fmla z16.s,p0/m,z7.s,z4.s
fmla z18.s,p0/m,z17.s,z4.s
st1w {z6.s}, p0, [x3]
st1w {z16.s}, p0, [x3, #1, MUL VL]
st1w {z18.s}, p0, [x25]
mova z17.s,p0/m,za3h.s[w12,0]
ld1w {z19.s}, p0/z, [x17, #1, MUL VL]
mova z20.s,p0/m,za0h.s[w12,1]
ld1w {z21.s}, p0/z, [x19]
mova z22.s,p0/m,za1h.s[w12,1]
ld1w {z23.s}, p0/z, [x19, #1, MUL VL]
mova z24.s,p0/m,za2h.s[w12,1]
ld1w {z25.s}, p0/z, [x2]
mova z26.s,p0/m,za3h.s[w12,1]
ld1w {z27.s}, p0/z, [x2, #1, MUL VL]
mova z28.s,p0/m,za0h.s[w12,2]
ld1w {z29.s}, p0/z, [x20]
mova z30.s,p0/m,za1h.s[w12,2]
ld1w {z31.s}, p0/z, [x20, #1, MUL VL]
mova z8.s,p0/m,za2h.s[w12,2]
ld1w {z9.s}, p0/z, [x10]
mova z10.s,p0/m,za3h.s[w12,2]
ld1w {z11.s}, p0/z, [x10, #1, MUL VL]
mova z12.s,p0/m,za0h.s[w12,3]
ld1w {z13.s}, p0/z, [x11]
mova z14.s,p0/m,za1h.s[w12,3]
mova z5.s,p0/m,za2h.s[w12,3]
mova z7.s,p0/m,za3h.s[w12,3]
fmla z19.s,p0/m,z17.s,z4.s
ld1w {z6.s}, p0/z, [x11, #1, MUL VL]
ld1w {z16.s}, p0/z, [x1]
ld1w {z18.s}, p0/z, [x1, #1, MUL VL]
fmla z21.s,p0/m,z20.s,z4.s
fmla z23.s,p0/m,z22.s,z4.s
fmla z25.s,p0/m,z24.s,z4.s
fmla z27.s,p0/m,z26.s,z4.s
fmla z29.s,p0/m,z28.s,z4.s
fmla z31.s,p0/m,z30.s,z4.s
fmla z9.s,p0/m,z8.s,z4.s
fmla z11.s,p0/m,z10.s,z4.s
fmla z13.s,p0/m,z12.s,z4.s
fmla z6.s,p0/m,z14.s,z4.s
fmla z16.s,p0/m,z5.s,z4.s
fmla z18.s,p0/m,z7.s,z4.s
st1w {z19.s}, p0, [x25, #1, MUL VL]
st1w {z21.s}, p0, [x26]
st1w {z23.s}, p0, [x26, #1, MUL VL]
st1w {z25.s}, p0, [x22]
st1w {z27.s}, p0, [x22, #1, MUL VL]
st1w {z29.s}, p0, [x27]
st1w {z31.s}, p0, [x27, #1, MUL VL]
st1w {z9.s}, p0, [x23]
st1w {z11.s}, p0, [x23, #1, MUL VL]
st1w {z13.s}, p0, [x24]
st1w {z6.s}, p0, [x24, #1, MUL VL]
st1w {z16.s}, p0, [x21]
st1w {z18.s}, p0, [x21, #1, MUL VL]
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x27,x27,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x21,x21,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr4_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x2,x2,x6
add x20,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
ld1rw {z4.s}, p0/z, [x5]
add x21,x3,x8
add x1,x1,x6
add x22,x3,x8
add x23,x3,x8
add x24,x3,x6
add x21,x21,x6
add x1,x1,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x22,x22,x6
add x27,x3,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
add x21,x21,x6, LSL #1
.ukr5_slices:
mova z5.s,p0/m,za0h.s[w12,0]
ld1w {z6.s}, p0/z, [x0]
mova z7.s,p0/m,za1h.s[w12,0]
ld1w {z16.s}, p0/z, [x0, #1, MUL VL]
mova z17.s,p0/m,za2h.s[w12,0]
ld1w {z18.s}, p0/z, [x17]
mova z19.s,p0/m,za3h.s[w12,0]
ld1w {z20.s}, p0/z, [x17, #1, MUL VL]
fmla z5.s,p0/m,z6.s,z4.s
fmla z7.s,p0/m,z16.s,z4.s
fmla z17.s,p0/m,z18.s,z4.s
fmla z19.s,p0/m,z20.s,z4.s
mova za0h.s[w12,0],p0/m,z5.s
mova za1h.s[w12,0],p0/m,z7.s
mova za2h.s[w12,0],p0/m,z17.s
mova za3h.s[w12,0],p0/m,z19.s
mova z20.s,p0/m,za0h.s[w12,1]
ld1w {z21.s}, p0/z, [x19]
mova z22.s,p0/m,za1h.s[w12,1]
ld1w {z23.s}, p0/z, [x19, #1, MUL VL]
mova z24.s,p0/m,za2h.s[w12,1]
ld1w {z25.s}, p0/z, [x2]
mova z26.s,p0/m,za3h.s[w12,1]
ld1w {z27.s}, p0/z, [x2, #1, MUL VL]
fmla z20.s,p0/m,z21.s,z4.s
fmla z22.s,p0/m,z23.s,z4.s
fmla z24.s,p0/m,z25.s,z4.s
fmla z26.s,p0/m,z27.s,z4.s
mova za0h.s[w12,1],p0/m,z20.s
mova za1h.s[w12,1],p0/m,z22.s
mova za2h.s[w12,1],p0/m,z24.s
mova za3h.s[w12,1],p0/m,z26.s
mova z21.s,p0/m,za0h.s[w12,2]
ld1w {z23.s}, p0/z, [x20]
mova z25.s,p0/m,za1h.s[w12,2]
ld1w {z27.s}, p0/z, [x20, #1, MUL VL]
mova z28.s,p0/m,za2h.s[w12,2]
ld1w {z29.s}, p0/z, [x10]
mova z30.s,p0/m,za3h.s[w12,2]
ld1w {z31.s}, p0/z, [x10, #1, MUL VL]
fmla z21.s,p0/m,z23.s,z4.s
fmla z25.s,p0/m,z27.s,z4.s
fmla z28.s,p0/m,z29.s,z4.s
fmla z30.s,p0/m,z31.s,z4.s
st1w {z5.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,2],p0/m,z21.s
mova za1h.s[w12,2],p0/m,z25.s
mova za2h.s[w12,2],p0/m,z28.s
mova za3h.s[w12,2],p0/m,z30.s
mova z23.s,p0/m,za0h.s[w12,3]
ld1w {z27.s}, p0/z, [x11]
mova z29.s,p0/m,za1h.s[w12,3]
ld1w {z6.s}, p0/z, [x11, #1, MUL VL]
mova z5.s,p0/m,za2h.s[w12,3]
ld1w {z16.s}, p0/z, [x1]
mova z7.s,p0/m,za3h.s[w12,3]
ld1w {z18.s}, p0/z, [x1, #1, MUL VL]
fmla z23.s,p0/m,z27.s,z4.s
fmla z29.s,p0/m,z6.s,z4.s
fmla z5.s,p0/m,z16.s,z4.s
fmla z7.s,p0/m,z18.s,z4.s
st1w {z17.s}, p0, [x25]
st1w {z19.s}, p0, [x25, #1, MUL VL]
st1w {z20.s}, p0, [x26]
st1w {z22.s}, p0, [x26, #1, MUL VL]
st1w {z24.s}, p0, [x22]
st1w {z26.s}, p0, [x22, #1, MUL VL]
st1w {z21.s}, p0, [x27]
st1w {z25.s}, p0, [x27, #1, MUL VL]
st1w {z28.s}, p0, [x23]
st1w {z30.s}, p0, [x23, #1, MUL VL]
st1w {z23.s}, p0, [x24]
st1w {z29.s}, p0, [x24, #1, MUL VL]
st1w {z5.s}, p0, [x21]
st1w {z7.s}, p0, [x21, #1, MUL VL]
mova za0h.s[w12,3],p0/m,z23.s
mova za1h.s[w12,3],p0/m,z29.s
mova za2h.s[w12,3],p0/m,z5.s
mova za3h.s[w12,3],p0/m,z7.s
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x27,x27,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x21,x21,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr5_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x6
mov x11,x7
mov x12,#0
add x16,x0,x8
add x17,x0,x6
add x1,x1,x6
add x19,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x10,x10,x6, LSL #1
ld1rw {z4.s}, p0/z, [x5]
add x20,x0,x8
ld1rw {z5.s}, p0/z, [x4]
add x21,x3,x8
add x20,x20,x6
add x22,x3,x8
add x23,x3,x8
add x24,x3,x6
add x21,x21,x6
add x20,x20,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x22,x22,x6
add x27,x3,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
add x21,x21,x6, LSL #1
.ukr6_slices:
ld1w {z6.s}, p0/z, [x0]
ld1w {z7.s}, p0/z, [x0, #1, MUL VL]
ld1w {z16.s}, p0/z, [x16]
fmul z6.s,z6.s,z4.s
mova z17.s,p0/m,za0h.s[w12,0]
fmul z7.s,z7.s,z4.s
mova z18.s,p0/m,za1h.s[w12,0]
fmul z16.s,z16.s,z4.s
mova z19.s,p0/m,za2h.s[w12,0]
fmla z6.s,p0/m,z17.s,z5.s
fmla z7.s,p0/m,z18.s,z5.s
fmla z16.s,p0/m,z19.s,z5.s
st1w {z6.s}, p0, [x3]
st1w {z7.s}, p0, [x3, #1, MUL VL]
st1w {z16.s}, p0, [x25]
ld1w {z20.s}, p0/z, [x16, #1, MUL VL]
ld1w {z21.s}, p0/z, [x17]
ld1w {z22.s}, p0/z, [x17, #1, MUL VL]
ld1w {z23.s}, p0/z, [x1]
ld1w {z24.s}, p0/z, [x1, #1, MUL VL]
ld1w {z25.s}, p0/z, [x19]
ld1w {z26.s}, p0/z, [x19, #1, MUL VL]
ld1w {z27.s}, p0/z, [x2]
ld1w {z28.s}, p0/z, [x2, #1, MUL VL]
ld1w {z29.s}, p0/z, [x10]
ld1w {z6.s}, p0/z, [x10, #1, MUL VL]
ld1w {z7.s}, p0/z, [x20]
ld1w {z16.s}, p0/z, [x20, #1, MUL VL]
fmul z20.s,z20.s,z4.s
mova z30.s,p0/m,za3h.s[w12,0]
fmul z21.s,z21.s,z4.s
mova z31.s,p0/m,za0h.s[w12,1]
fmul z22.s,z22.s,z4.s
mova z8.s,p0/m,za1h.s[w12,1]
fmul z23.s,z23.s,z4.s
mova z9.s,p0/m,za2h.s[w12,1]
fmul z24.s,z24.s,z4.s
mova z10.s,p0/m,za3h.s[w12,1]
fmul z25.s,z25.s,z4.s
mova z11.s,p0/m,za0h.s[w12,2]
fmul z26.s,z26.s,z4.s
mova z12.s,p0/m,za1h.s[w12,2]
fmul z27.s,z27.s,z4.s
mova z13.s,p0/m,za2h.s[w12,2]
fmul z28.s,z28.s,z4.s
mova z14.s,p0/m,za3h.s[w12,2]
mova z17.s,p0/m,za1h.s[w12,3]
mova z18.s,p0/m,za2h.s[w12,3]
mova z19.s,p0/m,za3h.s[w12,3]
fmla z20.s,p0/m,z30.s,z5.s
fmul z29.s,z29.s,z4.s
mova z30.s,p0/m,za0h.s[w12,3]
fmla z21.s,p0/m,z31.s,z5.s
fmul z6.s,z6.s,z4.s
fmul z7.s,z7.s,z4.s
fmul z16.s,z16.s,z4.s
fmla z22.s,p0/m,z8.s,z5.s
fmla z23.s,p0/m,z9.s,z5.s
fmla z24.s,p0/m,z10.s,z5.s
fmla z25.s,p0/m,z11.s,z5.s
fmla z26.s,p0/m,z12.s,z5.s
fmla z27.s,p0/m,z13.s,z5.s
fmla z28.s,p0/m,z14.s,z5.s
fmla z29.s,p0/m,z30.s,z5.s
fmla z6.s,p0/m,z17.s,z5.s
fmla z7.s,p0/m,z18.s,z5.s
fmla z16.s,p0/m,z19.s,z5.s
st1w {z20.s}, p0, [x25, #1, MUL VL]
st1w {z21.s}, p0, [x26]
st1w {z22.s}, p0, [x26, #1, MUL VL]
st1w {z23.s}, p0, [x22]
st1w {z24.s}, p0, [x22, #1, MUL VL]
st1w {z25.s}, p0, [x27]
st1w {z26.s}, p0, [x27, #1, MUL VL]
st1w {z27.s}, p0, [x23]
st1w {z28.s}, p0, [x23, #1, MUL VL]
st1w {z29.s}, p0, [x24]
st1w {z6.s}, p0, [x24, #1, MUL VL]
st1w {z7.s}, p0, [x21]
st1w {z16.s}, p0, [x21, #1, MUL VL]
add x0,x0,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x1,x1,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x10,x10,x6, LSL #2
add x20,x20,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x27,x27,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x21,x21,x6, LSL #2
add x12,x12,#4
add x11,x11,#-4
cbnz x11,.ukr6_slices
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
ldr x19, [sp]
.cfi_restore x19
ldr x20, [sp, #8]
.cfi_restore x20
ldr x21, [sp, #16]
.cfi_restore x21
ldr x22, [sp, #24]
.cfi_restore x22
ldr x23, [sp, #32]
.cfi_restore x23
ldr x24, [sp, #40]
.cfi_restore x24
ldr x25, [sp, #48]
.cfi_restore x25
ldr x26, [sp, #56]
.cfi_restore x26
ldr x27, [sp, #64]
.cfi_restore x27
ldr x28, [sp, #72]
.cfi_restore x28
ldr d8, [sp, #80]
.cfi_restore d8
ldr d9, [sp, #88]
.cfi_restore d9
ldr d10, [sp, #96]
.cfi_restore d10
ldr d11, [sp, #104]
.cfi_restore d11
ldr d12, [sp, #112]
.cfi_restore d12
ldr d13, [sp, #120]
.cfi_restore d13
ldr d14, [sp, #128]
.cfi_restore d14
ldr d15, [sp, #136]
.cfi_restore d15
add sp,sp,#144
.cfi_adjust_cfa_offset -144
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
add sp,sp,#-144
.cfi_adjust_cfa_offset 144
str x19, [sp]
.cfi_rel_offset x19, 0
str x20, [sp, #8]
.cfi_rel_offset x20, 8
str x21, [sp, #16]
.cfi_rel_offset x21, 16
str x22, [sp, #24]
.cfi_rel_offset x22, 24
str x23, [sp, #32]
.cfi_rel_offset x23, 32
str x24, [sp, #40]
.cfi_rel_offset x24, 40
str x25, [sp, #48]
.cfi_rel_offset x25, 48
str x26, [sp, #56]
.cfi_rel_offset x26, 56
str x27, [sp, #64]
.cfi_rel_offset x27, 64
str x28, [sp, #72]
.cfi_rel_offset x28, 72
str d8, [sp, #80]
.cfi_rel_offset d8, 80
str d9, [sp, #88]
.cfi_rel_offset d9, 88
str d10, [sp, #96]
.cfi_rel_offset d10, 96
str d11, [sp, #104]
.cfi_rel_offset d11, 104
str d12, [sp, #112]
.cfi_rel_offset d12, 112
str d13, [sp, #120]
.cfi_rel_offset d13, 120
str d14, [sp, #128]
.cfi_rel_offset d14, 128
str d15, [sp, #136]
.cfi_rel_offset d15, 136
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
mov x1,x0
mov x2,x0
mov x10,x0
mov x11,x0
incb x1, ALL, MUL #1
mov x16,x0
mov x17,x0
incb x2, ALL, MUL #1
mov x19,x0
incb x10, ALL, MUL #1
incb x11, ALL, MUL #1
add x20,x0,x8
add x1,x1,x8
mov x21,x0
incb x16, ALL, MUL #1
incb x17, ALL, MUL #1
add x22,x0,x8
add x2,x2,x8
incb x19, ALL, MUL #1
add x23,x0,x8
add x10,x10,x8
add x24,x0,x6
add x11,x11,x6
add x20,x20,x6
add x1,x1,x6
mov x25,x7
mov x12,#0
incb x21, ALL, MUL #1
add x26,x0,x8
add x16,x16,x8
add x27,x0,x6
add x17,x17,x6
add x22,x22,x6
add x2,x2,x6
add x28,x0,x6, LSL #1
add x19,x19,x6, LSL #1
add x23,x23,x6, LSL #1
add x10,x10,x6, LSL #1
add x24,x24,x6, LSL #1
add x11,x11,x6, LSL #1
add x20,x20,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr1_slices:
st1w {za0h.s[w12, 0]}, p0, [x0]
st1w {za1h.s[w12, 0]}, p0, [x21]
st1w {za2h.s[w12, 0]}, p0, [x26]
st1w {za3h.s[w12, 0]}, p0, [x16]
st1w {za0h.s[w12, 1]}, p0, [x27]
st1w {za1h.s[w12, 1]}, p0, [x17]
st1w {za2h.s[w12, 1]}, p0, [x22]
st1w {za3h.s[w12, 1]}, p0, [x2]
st1w {za0h.s[w12, 2]}, p0, [x28]
st1w {za1h.s[w12, 2]}, p0, [x19]
st1w {za2h.s[w12, 2]}, p0, [x23]
st1w {za3h.s[w12, 2]}, p0, [x10]
st1w {za0h.s[w12, 3]}, p0, [x24]
st1w {za1h.s[w12, 3]}, p0, [x11]
st1w {za2h.s[w12, 3]}, p0, [x20]
st1w {za3h.s[w12, 3]}, p0, [x1]
add x0,x0,x6, LSL #2
add x21,x21,x6, LSL #2
add x26,x26,x6, LSL #2
add x16,x16,x6, LSL #2
add x27,x27,x6, LSL #2
add x17,x17,x6, LSL #2
add x22,x22,x6, LSL #2
add x2,x2,x6, LSL #2
add x28,x28,x6, LSL #2
add x19,x19,x6, LSL #2
add x23,x23,x6, LSL #2
add x10,x10,x6, LSL #2
add x24,x24,x6, LSL #2
add x11,x11,x6, LSL #2
add x20,x20,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x25,x25,#-4
cbnz x25,.ukr1_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x2,x2,x6
add x20,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
ld1rw {z16.s}, p0/z, [x4]
add x1,x1,x6
add x1,x1,x6, LSL #1
.ukr2_slices:
mova z17.s,p0/m,za0h.s[w12,0]
mova z18.s,p0/m,za1h.s[w12,0]
mova z19.s,p0/m,za2h.s[w12,0]
mova z20.s,p0/m,za3h.s[w12,0]
mova z21.s,p0/m,za0h.s[w12,1]
fmul z22.s,z17.s,z16.s
fmul z23.s,z18.s,z16.s
fmul z24.s,z19.s,z16.s
fmul z25.s,z20.s,z16.s
fmul z26.s,z21.s,z16.s
st1w {z22.s}, p0, [x0]
st1w {z23.s}, p0, [x0, #1, MUL VL]
st1w {z24.s}, p0, [x17]
st1w {z25.s}, p0, [x17, #1, MUL VL]
st1w {z26.s}, p0, [x19]
mova z21.s,p0/m,za1h.s[w12,1]
mova z27.s,p0/m,za2h.s[w12,1]
mova z28.s,p0/m,za3h.s[w12,1]
mova z29.s,p0/m,za0h.s[w12,2]
mova z30.s,p0/m,za1h.s[w12,2]
mova z31.s,p0/m,za2h.s[w12,2]
mova z8.s,p0/m,za3h.s[w12,2]
mova z17.s,p0/m,za0h.s[w12,3]
mova z18.s,p0/m,za1h.s[w12,3]
mova z19.s,p0/m,za2h.s[w12,3]
mova z20.s,p0/m,za3h.s[w12,3]
fmul z9.s,z21.s,z16.s
fmul z21.s,z27.s,z16.s
fmul z27.s,z28.s,z16.s
fmul z28.s,z29.s,z16.s
fmul z29.s,z30.s,z16.s
fmul z30.s,z31.s,z16.s
fmul z22.s,z8.s,z16.s
fmul z23.s,z17.s,z16.s
fmul z24.s,z18.s,z16.s
fmul z25.s,z19.s,z16.s
fmul z26.s,z20.s,z16.s
st1w {z9.s}, p0, [x19, #1, MUL VL]
st1w {z21.s}, p0, [x2]
st1w {z27.s}, p0, [x2, #1, MUL VL]
st1w {z28.s}, p0, [x20]
st1w {z29.s}, p0, [x20, #1, MUL VL]
st1w {z30.s}, p0, [x10]
st1w {z22.s}, p0, [x10, #1, MUL VL]
st1w {z23.s}, p0, [x11]
st1w {z24.s}, p0, [x11, #1, MUL VL]
st1w {z25.s}, p0, [x1]
st1w {z26.s}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr2_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
add x1,x1,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x20,x3,x8
add x2,x2,x6
add x21,x0,x6, LSL #1
add x22,x3,x8
add x10,x10,x6, LSL #1
add x23,x3,x6
add x11,x11,x6, LSL #1
add x24,x3,x8
add x24,x24,x6
add x1,x1,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x20,x20,x6
add x27,x3,x6, LSL #1
add x22,x22,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
.ukr3_slices:
mova z16.s,p0/m,za0h.s[w12,0]
ld1w {z17.s}, p0/z, [x0]
mova z18.s,p0/m,za1h.s[w12,0]
ld1w {z19.s}, p0/z, [x0, #1, MUL VL]
mova z20.s,p0/m,za2h.s[w12,0]
ld1w {z21.s}, p0/z, [x17]
mova z22.s,p0/m,za3h.s[w12,0]
ld1w {z23.s}, p0/z, [x17, #1, MUL VL]
fadd z17.s,z16.s,z17.s
fadd z19.s,z18.s,z19.s
fadd z21.s,z20.s,z21.s
fadd z23.s,z22.s,z23.s
st1w {z17.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
st1w {z21.s}, p0, [x25]
st1w {z23.s}, p0, [x25, #1, MUL VL]
mova z24.s,p0/m,za0h.s[w12,1]
ld1w {z25.s}, p0/z, [x19]
mova z26.s,p0/m,za1h.s[w12,1]
ld1w {z27.s}, p0/z, [x19, #1, MUL VL]
mova z28.s,p0/m,za2h.s[w12,1]
ld1w {z29.s}, p0/z, [x2]
mova z30.s,p0/m,za3h.s[w12,1]
ld1w {z31.s}, p0/z, [x2, #1, MUL VL]
mova z8.s,p0/m,za0h.s[w12,2]
ld1w {z9.s}, p0/z, [x21]
mova z10.s,p0/m,za1h.s[w12,2]
ld1w {z11.s}, p0/z, [x21, #1, MUL VL]
mova z12.s,p0/m,za2h.s[w12,2]
ld1w {z13.s}, p0/z, [x10]
mova z14.s,p0/m,za3h.s[w12,2]
mova z16.s,p0/m,za0h.s[w12,3]
mova z18.s,p0/m,za1h.s[w12,3]
mova z20.s,p0/m,za2h.s[w12,3]
mova z22.s,p0/m,za3h.s[w12,3]
fadd z25.s,z24.s,z25.s
ld1w {z24.s}, p0/z, [x10, #1, MUL VL]
fadd z27.s,z26.s,z27.s
ld1w {z17.s}, p0/z, [x11]
ld1w {z19.s}, p0/z, [x11, #1, MUL VL]
ld1w {z21.s}, p0/z, [x1]
ld1w {z23.s}, p0/z, [x1, #1, MUL VL]
fadd z29.s,z28.s,z29.s
fadd z31.s,z30.s,z31.s
fadd z9.s,z8.s,z9.s
fadd z11.s,z10.s,z11.s
fadd z13.s,z12.s,z13.s
fadd z24.s,z14.s,z24.s
fadd z17.s,z16.s,z17.s
fadd z19.s,z18.s,z19.s
fadd z21.s,z20.s,z21.s
fadd z23.s,z22.s,z23.s
st1w {z25.s}, p0, [x26]
st1w {z27.s}, p0, [x26, #1, MUL VL]
st1w {z29.s}, p0, [x20]
st1w {z31.s}, p0, [x20, #1, MUL VL]
st1w {z9.s}, p0, [x27]
st1w {z11.s}, p0, [x27, #1, MUL VL]
st1w {z13.s}, p0, [x22]
st1w {z24.s}, p0, [x22, #1, MUL VL]
st1w {z17.s}, p0, [x23]
st1w {z19.s}, p0, [x23, #1, MUL VL]
st1w {z21.s}, p0, [x24]
st1w {z23.s}, p0, [x24, #1, MUL VL]
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x21,x21,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x20,x20,x6, LSL #2
add x27,x27,x6, LSL #2
add x22,x22,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr3_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x2,x2,x6
add x20,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
ld1rw {z16.s}, p0/z, [x4]
add x21,x3,x8
add x1,x1,x6
add x22,x3,x8
add x23,x3,x8
add x24,x3,x6
add x21,x21,x6
add x1,x1,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x22,x22,x6
add x27,x3,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
add x21,x21,x6, LSL #1
.ukr4_slices:
mova z17.s,p0/m,za0h.s[w12,0]
ld1w {z18.s}, p0/z, [x0]
mova z19.s,p0/m,za1h.s[w12,0]
ld1w {z20.s}, p0/z, [x0, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,0]
ld1w {z22.s}, p0/z, [x17]
mova z23.s,p0/m,za3h.s[w12,0]
ld1w {z24.s}, p0/z, [x17, #1, MUL VL]
mova z25.s,p0/m,za0h.s[w12,1]
ld1w {z26.s}, p0/z, [x19]
fmla z18.s,p0/m,z17.s,z16.s
fmla z20.s,p0/m,z19.s,z16.s
fmla z22.s,p0/m,z21.s,z16.s
fmla z24.s,p0/m,z23.s,z16.s
fmla z26.s,p0/m,z25.s,z16.s
st1w {z18.s}, p0, [x3]
st1w {z20.s}, p0, [x3, #1, MUL VL]
st1w {z22.s}, p0, [x25]
st1w {z24.s}, p0, [x25, #1, MUL VL]
st1w {z26.s}, p0, [x26]
mova z25.s,p0/m,za1h.s[w12,1]
ld1w {z27.s}, p0/z, [x19, #1, MUL VL]
mova z28.s,p0/m,za2h.s[w12,1]
ld1w {z29.s}, p0/z, [x2]
mova z30.s,p0/m,za3h.s[w12,1]
ld1w {z31.s}, p0/z, [x2, #1, MUL VL]
mova z8.s,p0/m,za0h.s[w12,2]
ld1w {z9.s}, p0/z, [x20]
mova z10.s,p0/m,za1h.s[w12,2]
ld1w {z11.s}, p0/z, [x20, #1, MUL VL]
mova z12.s,p0/m,za2h.s[w12,2]
ld1w {z13.s}, p0/z, [x10]
mova z14.s,p0/m,za3h.s[w12,2]
mova z17.s,p0/m,za0h.s[w12,3]
mova z19.s,p0/m,za1h.s[w12,3]
mova z21.s,p0/m,za2h.s[w12,3]
mova z23.s,p0/m,za3h.s[w12,3]
fmla z27.s,p0/m,z25.s,z16.s
ld1w {z18.s}, p0/z, [x10, #1, MUL VL]
ld1w {z20.s}, p0/z, [x11]
ld1w {z22.s}, p0/z, [x11, #1, MUL VL]
ld1w {z24.s}, p0/z, [x1]
ld1w {z26.s}, p0/z, [x1, #1, MUL VL]
fmla z29.s,p0/m,z28.s,z16.s
fmla z31.s,p0/m,z30.s,z16.s
fmla z9.s,p0/m,z8.s,z16.s
fmla z11.s,p0/m,z10.s,z16.s
fmla z13.s,p0/m,z12.s,z16.s
fmla z18.s,p0/m,z14.s,z16.s
fmla z20.s,p0/m,z17.s,z16.s
fmla z22.s,p0/m,z19.s,z16.s
fmla z24.s,p0/m,z21.s,z16.s
fmla z26.s,p0/m,z23.s,z16.s
st1w {z27.s}, p0, [x26, #1, MUL VL]
st1w {z29.s}, p0, [x22]
st1w {z31.s}, p0, [x22, #1, MUL VL]
st1w {z9.s}, p0, [x27]
st1w {z11.s}, p0, [x27, #1, MUL VL]
st1w {z13.s}, p0, [x23]
st1w {z18.s}, p0, [x23, #1, MUL VL]
st1w {z20.s}, p0, [x24]
st1w {z22.s}, p0, [x24, #1, MUL VL]
st1w {z24.s}, p0, [x21]
st1w {z26.s}, p0, [x21, #1, MUL VL]
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x27,x27,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x21,x21,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr4_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x2,x2,x6
add x20,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
ld1rw {z16.s}, p0/z, [x5]
add x21,x3,x8
add x1,x1,x6
add x22,x3,x8
add x23,x3,x8
add x24,x3,x6
add x21,x21,x6
add x1,x1,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x22,x22,x6
add x27,x3,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
add x21,x21,x6, LSL #1
.ukr5_slices:
mova z17.s,p0/m,za0h.s[w12,0]
ld1w {z18.s}, p0/z, [x0]
mova z19.s,p0/m,za1h.s[w12,0]
ld1w {z20.s}, p0/z, [x0, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,0]
ld1w {z22.s}, p0/z, [x17]
mova z23.s,p0/m,za3h.s[w12,0]
ld1w {z24.s}, p0/z, [x17, #1, MUL VL]
fmla z17.s,p0/m,z18.s,z16.s
fmla z19.s,p0/m,z20.s,z16.s
fmla z21.s,p0/m,z22.s,z16.s
fmla z23.s,p0/m,z24.s,z16.s
mova za0h.s[w12,0],p0/m,z17.s
mova za1h.s[w12,0],p0/m,z19.s
mova za2h.s[w12,0],p0/m,z21.s
mova za3h.s[w12,0],p0/m,z23.s
mova z25.s,p0/m,za0h.s[w12,1]
ld1w {z26.s}, p0/z, [x19]
mova z27.s,p0/m,za1h.s[w12,1]
ld1w {z28.s}, p0/z, [x19, #1, MUL VL]
mova z29.s,p0/m,za2h.s[w12,1]
ld1w {z30.s}, p0/z, [x2]
mova z31.s,p0/m,za3h.s[w12,1]
ld1w {z8.s}, p0/z, [x2, #1, MUL VL]
fmla z25.s,p0/m,z26.s,z16.s
fmla z27.s,p0/m,z28.s,z16.s
fmla z29.s,p0/m,z30.s,z16.s
fmla z31.s,p0/m,z8.s,z16.s
mova za0h.s[w12,1],p0/m,z25.s
mova za1h.s[w12,1],p0/m,z27.s
mova za2h.s[w12,1],p0/m,z29.s
mova za3h.s[w12,1],p0/m,z31.s
mova z28.s,p0/m,za0h.s[w12,2]
ld1w {z30.s}, p0/z, [x20]
mova z8.s,p0/m,za1h.s[w12,2]
ld1w {z9.s}, p0/z, [x20, #1, MUL VL]
mova z10.s,p0/m,za2h.s[w12,2]
ld1w {z11.s}, p0/z, [x10]
mova z12.s,p0/m,za3h.s[w12,2]
ld1w {z18.s}, p0/z, [x10, #1, MUL VL]
fmla z28.s,p0/m,z30.s,z16.s
fmla z8.s,p0/m,z9.s,z16.s
fmla z10.s,p0/m,z11.s,z16.s
fmla z12.s,p0/m,z18.s,z16.s
st1w {z17.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
st1w {z21.s}, p0, [x25]
st1w {z23.s}, p0, [x25, #1, MUL VL]
mova za0h.s[w12,2],p0/m,z28.s
mova za1h.s[w12,2],p0/m,z8.s
mova za2h.s[w12,2],p0/m,z10.s
mova za3h.s[w12,2],p0/m,z12.s
mova z17.s,p0/m,za0h.s[w12,3]
ld1w {z20.s}, p0/z, [x11]
mova z19.s,p0/m,za1h.s[w12,3]
ld1w {z22.s}, p0/z, [x11, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,3]
ld1w {z24.s}, p0/z, [x1]
mova z23.s,p0/m,za3h.s[w12,3]
ld1w {z26.s}, p0/z, [x1, #1, MUL VL]
fmla z17.s,p0/m,z20.s,z16.s
fmla z19.s,p0/m,z22.s,z16.s
fmla z21.s,p0/m,z24.s,z16.s
fmla z23.s,p0/m,z26.s,z16.s
st1w {z25.s}, p0, [x26]
st1w {z27.s}, p0, [x26, #1, MUL VL]
st1w {z29.s}, p0, [x22]
st1w {z31.s}, p0, [x22, #1, MUL VL]
st1w {z28.s}, p0, [x27]
st1w {z8.s}, p0, [x27, #1, MUL VL]
st1w {z10.s}, p0, [x23]
st1w {z12.s}, p0, [x23, #1, MUL VL]
st1w {z17.s}, p0, [x24]
st1w {z19.s}, p0, [x24, #1, MUL VL]
st1w {z21.s}, p0, [x21]
st1w {z23.s}, p0, [x21, #1, MUL VL]
mova za0h.s[w12,3],p0/m,z17.s
mova za1h.s[w12,3],p0/m,z19.s
mova za2h.s[w12,3],p0/m,z21.s
mova za3h.s[w12,3],p0/m,z23.s
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x27,x27,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x21,x21,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr5_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x6
mov x11,x7
mov x12,#0
add x16,x0,x8
add x17,x0,x6
add x1,x1,x6
add x19,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x10,x10,x6, LSL #1
ld1rw {z16.s}, p0/z, [x5]
add x20,x0,x8
ld1rw {z17.s}, p0/z, [x4]
add x21,x3,x8
add x20,x20,x6
add x22,x3,x8
add x23,x3,x8
add x24,x3,x6
add x21,x21,x6
add x20,x20,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x22,x22,x6
add x27,x3,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
add x21,x21,x6, LSL #1
.ukr6_slices:
ld1w {z18.s}, p0/z, [x0]
ld1w {z19.s}, p0/z, [x0, #1, MUL VL]
ld1w {z20.s}, p0/z, [x16]
ld1w {z21.s}, p0/z, [x16, #1, MUL VL]
ld1w {z22.s}, p0/z, [x17]
fmul z18.s,z18.s,z16.s
mova z23.s,p0/m,za0h.s[w12,0]
fmul z19.s,z19.s,z16.s
mova z24.s,p0/m,za1h.s[w12,0]
fmul z20.s,z20.s,z16.s
mova z25.s,p0/m,za2h.s[w12,0]
fmul z21.s,z21.s,z16.s
mova z26.s,p0/m,za3h.s[w12,0]
fmul z22.s,z22.s,z16.s
mova z27.s,p0/m,za0h.s[w12,1]
fmla z18.s,p0/m,z23.s,z17.s
fmla z19.s,p0/m,z24.s,z17.s
fmla z20.s,p0/m,z25.s,z17.s
fmla z21.s,p0/m,z26.s,z17.s
fmla z22.s,p0/m,z27.s,z17.s
st1w {z18.s}, p0, [x3]
st1w {z19.s}, p0, [x3, #1, MUL VL]
st1w {z20.s}, p0, [x25]
st1w {z21.s}, p0, [x25, #1, MUL VL]
st1w {z22.s}, p0, [x26]
ld1w {z28.s}, p0/z, [x17, #1, MUL VL]
ld1w {z29.s}, p0/z, [x1]
ld1w {z30.s}, p0/z, [x1, #1, MUL VL]
ld1w {z31.s}, p0/z, [x19]
ld1w {z8.s}, p0/z, [x19, #1, MUL VL]
ld1w {z9.s}, p0/z, [x2]
ld1w {z18.s}, p0/z, [x2, #1, MUL VL]
ld1w {z19.s}, p0/z, [x10]
ld1w {z20.s}, p0/z, [x10, #1, MUL VL]
ld1w {z21.s}, p0/z, [x20]
ld1w {z22.s}, p0/z, [x20, #1, MUL VL]
fmul z28.s,z28.s,z16.s
mova z10.s,p0/m,za1h.s[w12,1]
fmul z29.s,z29.s,z16.s
mova z11.s,p0/m,za2h.s[w12,1]
fmul z30.s,z30.s,z16.s
mova z12.s,p0/m,za3h.s[w12,1]
fmul z31.s,z31.s,z16.s
mova z13.s,p0/m,za0h.s[w12,2]
fmul z8.s,z8.s,z16.s
mova z14.s,p0/m,za1h.s[w12,2]
mova z24.s,p0/m,za0h.s[w12,3]
mova z25.s,p0/m,za1h.s[w12,3]
fmla z28.s,p0/m,z10.s,z17.s
fmul z9.s,z9.s,z16.s
mova z10.s,p0/m,za2h.s[w12,2]
mova z26.s,p0/m,za2h.s[w12,3]
fmla z29.s,p0/m,z11.s,z17.s
fmul z18.s,z18.s,z16.s
mova z23.s,p0/m,za3h.s[w12,2]
fmul z19.s,z19.s,z16.s
fmul z20.s,z20.s,z16.s
fmul z21.s,z21.s,z16.s
fmul z22.s,z22.s,z16.s
mova z27.s,p0/m,za3h.s[w12,3]
fmla z30.s,p0/m,z12.s,z17.s
fmla z31.s,p0/m,z13.s,z17.s
fmla z8.s,p0/m,z14.s,z17.s
fmla z9.s,p0/m,z10.s,z17.s
fmla z18.s,p0/m,z23.s,z17.s
fmla z19.s,p0/m,z24.s,z17.s
fmla z20.s,p0/m,z25.s,z17.s
fmla z21.s,p0/m,z26.s,z17.s
fmla z22.s,p0/m,z27.s,z17.s
st1w {z28.s}, p0, [x26, #1, MUL VL]
st1w {z29.s}, p0, [x22]
st1w {z30.s}, p0, [x22, #1, MUL VL]
st1w {z31.s}, p0, [x27]
st1w {z8.s}, p0, [x27, #1, MUL VL]
st1w {z9.s}, p0, [x23]
st1w {z18.s}, p0, [x23, #1, MUL VL]
st1w {z19.s}, p0, [x24]
st1w {z20.s}, p0, [x24, #1, MUL VL]
st1w {z21.s}, p0, [x21]
st1w {z22.s}, p0, [x21, #1, MUL VL]
add x0,x0,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x1,x1,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x10,x10,x6, LSL #2
add x20,x20,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x27,x27,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x21,x21,x6, LSL #2
add x12,x12,#4
add x11,x11,#-4
cbnz x11,.ukr6_slices
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
ldr x19, [sp]
.cfi_restore x19
ldr x20, [sp, #8]
.cfi_restore x20
ldr x21, [sp, #16]
.cfi_restore x21
ldr x22, [sp, #24]
.cfi_restore x22
ldr x23, [sp, #32]
.cfi_restore x23
ldr x24, [sp, #40]
.cfi_restore x24
ldr x25, [sp, #48]
.cfi_restore x25
ldr x26, [sp, #56]
.cfi_restore x26
ldr x27, [sp, #64]
.cfi_restore x27
ldr x28, [sp, #72]
.cfi_restore x28
ldr d8, [sp, #80]
.cfi_restore d8
ldr d9, [sp, #88]
.cfi_restore d9
ldr d10, [sp, #96]
.cfi_restore d10
ldr d11, [sp, #104]
.cfi_restore d11
ldr d12, [sp, #112]
.cfi_restore d12
ldr d13, [sp, #120]
.cfi_restore d13
ldr d14, [sp, #128]
.cfi_restore d14
ldr d15, [sp, #136]
.cfi_restore d15
add sp,sp,#144
.cfi_adjust_cfa_offset -144
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
add sp,sp,#-144
.cfi_adjust_cfa_offset 144
str x19, [sp]
.cfi_rel_offset x19, 0
str x20, [sp, #8]
.cfi_rel_offset x20, 8
str x21, [sp, #16]
.cfi_rel_offset x21, 16
str x22, [sp, #24]
.cfi_rel_offset x22, 24
str x23, [sp, #32]
.cfi_rel_offset x23, 32
str x24, [sp, #40]
.cfi_rel_offset x24, 40
str x25, [sp, #48]
.cfi_rel_offset x25, 48
str x26, [sp, #56]
.cfi_rel_offset x26, 56
str x27, [sp, #64]
.cfi_rel_offset x27, 64
str x28, [sp, #72]
.cfi_rel_offset x28, 72
str d8, [sp, #80]
.cfi_rel_offset d8, 80
str d9, [sp, #88]
.cfi_rel_offset d9, 88
str d10, [sp, #96]
.cfi_rel_offset d10, 96
str d11, [sp, #104]
.cfi_rel_offset d11, 104
str d12, [sp, #112]
.cfi_rel_offset d12, 112
str d13, [sp, #120]
.cfi_rel_offset d13, 120
str d14, [sp, #128]
.cfi_rel_offset d14, 128
str d15, [sp, #136]
.cfi_rel_offset d15, 136
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
mov x1,x0
mov x2,x0
mov x10,x0
mov x11,x0
incb x1, ALL, MUL #1
mov x16,x0
mov x17,x0
incb x2, ALL, MUL #1
mov x19,x0
incb x10, ALL, MUL #1
incb x11, ALL, MUL #1
add x20,x0,x8
add x1,x1,x8
mov x21,x0
incb x16, ALL, MUL #1
incb x17, ALL, MUL #1
add x22,x0,x8
add x2,x2,x8
incb x19, ALL, MUL #1
add x23,x0,x8
add x10,x10,x8
add x24,x0,x6
add x11,x11,x6
add x20,x20,x6
add x1,x1,x6
mov x25,x7
mov x12,#0
incb x21, ALL, MUL #1
add x26,x0,x8
add x16,x16,x8
add x27,x0,x6
add x17,x17,x6
add x22,x22,x6
add x2,x2,x6
add x28,x0,x6, LSL #1
add x19,x19,x6, LSL #1
add x23,x23,x6, LSL #1
add x10,x10,x6, LSL #1
add x24,x24,x6, LSL #1
add x11,x11,x6, LSL #1
add x20,x20,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr1_slices:
st1w {za0h.s[w12, 0]}, p0, [x0]
st1w {za1h.s[w12, 0]}, p0, [x21]
st1w {za2h.s[w12, 0]}, p0, [x26]
st1w {za3h.s[w12, 0]}, p0, [x16]
st1w {za0h.s[w12, 1]}, p0, [x27]
st1w {za1h.s[w12, 1]}, p0, [x17]
st1w {za2h.s[w12, 1]}, p0, [x22]
st1w {za3h.s[w12, 1]}, p0, [x2]
st1w {za0h.s[w12, 2]}, p0, [x28]
st1w {za1h.s[w12, 2]}, p0, [x19]
st1w {za2h.s[w12, 2]}, p0, [x23]
st1w {za3h.s[w12, 2]}, p0, [x10]
st1w {za0h.s[w12, 3]}, p0, [x24]
st1w {za1h.s[w12, 3]}, p0, [x11]
st1w {za2h.s[w12, 3]}, p0, [x20]
st1w {za3h.s[w12, 3]}, p0, [x1]
add x0,x0,x6, LSL #2
add x21,x21,x6, LSL #2
add x26,x26,x6, LSL #2
add x16,x16,x6, LSL #2
add x27,x27,x6, LSL #2
add x17,x17,x6, LSL #2
add x22,x22,x6, LSL #2
add x2,x2,x6, LSL #2
add x28,x28,x6, LSL #2
add x19,x19,x6, LSL #2
add x23,x23,x6, LSL #2
add x10,x10,x6, LSL #2
add x24,x24,x6, LSL #2
add x11,x11,x6, LSL #2
add x20,x20,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x25,x25,#-4
cbnz x25,.ukr1_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x2,x2,x6
add x20,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
ld1rw {z20.s}, p0/z, [x4]
add x1,x1,x6
add x1,x1,x6, LSL #1
.ukr2_slices:
mova z21.s,p0/m,za0h.s[w12,0]
mova z22.s,p0/m,za1h.s[w12,0]
mova z23.s,p0/m,za2h.s[w12,0]
mova z24.s,p0/m,za3h.s[w12,0]
mova z25.s,p0/m,za0h.s[w12,1]
mova z26.s,p0/m,za1h.s[w12,1]
mova z27.s,p0/m,za2h.s[w12,1]
fmul z28.s,z21.s,z20.s
fmul z29.s,z22.s,z20.s
fmul z30.s,z23.s,z20.s
fmul z31.s,z24.s,z20.s
fmul z8.s,z25.s,z20.s
fmul z9.s,z26.s,z20.s
fmul z10.s,z27.s,z20.s
st1w {z28.s}, p0, [x0]
st1w {z29.s}, p0, [x0, #1, MUL VL]
st1w {z30.s}, p0, [x17]
st1w {z31.s}, p0, [x17, #1, MUL VL]
st1w {z8.s}, p0, [x19]
st1w {z9.s}, p0, [x19, #1, MUL VL]
st1w {z10.s}, p0, [x2]
mova z27.s,p0/m,za3h.s[w12,1]
mova z11.s,p0/m,za0h.s[w12,2]
mova z12.s,p0/m,za1h.s[w12,2]
mova z21.s,p0/m,za2h.s[w12,2]
mova z22.s,p0/m,za3h.s[w12,2]
mova z23.s,p0/m,za0h.s[w12,3]
mova z24.s,p0/m,za1h.s[w12,3]
mova z25.s,p0/m,za2h.s[w12,3]
mova z26.s,p0/m,za3h.s[w12,3]
fmul z13.s,z27.s,z20.s
fmul z27.s,z11.s,z20.s
fmul z28.s,z12.s,z20.s
fmul z29.s,z21.s,z20.s
fmul z30.s,z22.s,z20.s
fmul z31.s,z23.s,z20.s
fmul z8.s,z24.s,z20.s
fmul z9.s,z25.s,z20.s
fmul z10.s,z26.s,z20.s
st1w {z13.s}, p0, [x2, #1, MUL VL]
st1w {z27.s}, p0, [x20]
st1w {z28.s}, p0, [x20, #1, MUL VL]
st1w {z29.s}, p0, [x10]
st1w {z30.s}, p0, [x10, #1, MUL VL]
st1w {z31.s}, p0, [x11]
st1w {z8.s}, p0, [x11, #1, MUL VL]
st1w {z9.s}, p0, [x1]
st1w {z10.s}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr2_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
add x1,x1,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x20,x3,x8
add x2,x2,x6
add x21,x0,x6, LSL #1
add x22,x3,x8
add x10,x10,x6, LSL #1
add x23,x3,x6
add x11,x11,x6, LSL #1
add x24,x3,x8
add x24,x24,x6
add x1,x1,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x20,x20,x6
add x27,x3,x6, LSL #1
add x22,x22,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
.ukr3_slices:
mova z20.s,p0/m,za0h.s[w12,0]
ld1w {z21.s}, p0/z, [x0]
mova z22.s,p0/m,za1h.s[w12,0]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
mova z24.s,p0/m,za2h.s[w12,0]
ld1w {z25.s}, p0/z, [x17]
mova z26.s,p0/m,za3h.s[w12,0]
ld1w {z27.s}, p0/z, [x17, #1, MUL VL]
mova z28.s,p0/m,za0h.s[w12,1]
ld1w {z29.s}, p0/z, [x19]
mova z30.s,p0/m,za1h.s[w12,1]
ld1w {z31.s}, p0/z, [x19, #1, MUL VL]
fadd z21.s,z20.s,z21.s
fadd z23.s,z22.s,z23.s
fadd z25.s,z24.s,z25.s
fadd z27.s,z26.s,z27.s
fadd z29.s,z28.s,z29.s
fadd z31.s,z30.s,z31.s
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
st1w {z25.s}, p0, [x25]
st1w {z27.s}, p0, [x25, #1, MUL VL]
st1w {z29.s}, p0, [x26]
st1w {z31.s}, p0, [x26, #1, MUL VL]
mova z8.s,p0/m,za2h.s[w12,1]
ld1w {z9.s}, p0/z, [x2]
mova z10.s,p0/m,za3h.s[w12,1]
ld1w {z11.s}, p0/z, [x2, #1, MUL VL]
mova z12.s,p0/m,za0h.s[w12,2]
ld1w {z13.s}, p0/z, [x21]
mova z14.s,p0/m,za1h.s[w12,2]
mova z24.s,p0/m,za0h.s[w12,3]
mova z26.s,p0/m,za1h.s[w12,3]
fadd z9.s,z8.s,z9.s
ld1w {z8.s}, p0/z, [x21, #1, MUL VL]
fadd z11.s,z10.s,z11.s
mova z20.s,p0/m,za2h.s[w12,2]
ld1w {z21.s}, p0/z, [x10]
mova z22.s,p0/m,za3h.s[w12,2]
ld1w {z23.s}, p0/z, [x10, #1, MUL VL]
ld1w {z25.s}, p0/z, [x11]
ld1w {z27.s}, p0/z, [x11, #1, MUL VL]
mova z28.s,p0/m,za2h.s[w12,3]
ld1w {z29.s}, p0/z, [x1]
mova z30.s,p0/m,za3h.s[w12,3]
ld1w {z31.s}, p0/z, [x1, #1, MUL VL]
fadd z13.s,z12.s,z13.s
fadd z8.s,z14.s,z8.s
fadd z21.s,z20.s,z21.s
fadd z23.s,z22.s,z23.s
fadd z25.s,z24.s,z25.s
fadd z27.s,z26.s,z27.s
fadd z29.s,z28.s,z29.s
fadd z31.s,z30.s,z31.s
st1w {z9.s}, p0, [x20]
st1w {z11.s}, p0, [x20, #1, MUL VL]
st1w {z13.s}, p0, [x27]
st1w {z8.s}, p0, [x27, #1, MUL VL]
st1w {z21.s}, p0, [x22]
st1w {z23.s}, p0, [x22, #1, MUL VL]
st1w {z25.s}, p0, [x23]
st1w {z27.s}, p0, [x23, #1, MUL VL]
st1w {z29.s}, p0, [x24]
st1w {z31.s}, p0, [x24, #1, MUL VL]
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x21,x21,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x20,x20,x6, LSL #2
add x27,x27,x6, LSL #2
add x22,x22,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr3_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x2,x2,x6
add x20,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
ld1rw {z20.s}, p0/z, [x4]
add x21,x3,x8
add x1,x1,x6
add x22,x3,x8
add x23,x3,x8
add x24,x3,x6
add x21,x21,x6
add x1,x1,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x22,x22,x6
add x27,x3,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
add x21,x21,x6, LSL #1
.ukr4_slices:
mova z21.s,p0/m,za0h.s[w12,0]
ld1w {z22.s}, p0/z, [x0]
mova z23.s,p0/m,za1h.s[w12,0]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
mova z25.s,p0/m,za2h.s[w12,0]
ld1w {z26.s}, p0/z, [x17]
mova z27.s,p0/m,za3h.s[w12,0]
ld1w {z28.s}, p0/z, [x17, #1, MUL VL]
mova z29.s,p0/m,za0h.s[w12,1]
ld1w {z30.s}, p0/z, [x19]
mova z31.s,p0/m,za1h.s[w12,1]
ld1w {z8.s}, p0/z, [x19, #1, MUL VL]
mova z9.s,p0/m,za2h.s[w12,1]
ld1w {z10.s}, p0/z, [x2]
fmla z22.s,p0/m,z21.s,z20.s
fmla z24.s,p0/m,z23.s,z20.s
fmla z26.s,p0/m,z25.s,z20.s
fmla z28.s,p0/m,z27.s,z20.s
fmla z30.s,p0/m,z29.s,z20.s
fmla z8.s,p0/m,z31.s,z20.s
fmla z10.s,p0/m,z9.s,z20.s
st1w {z22.s}, p0, [x3]
st1w {z24.s}, p0, [x3, #1, MUL VL]
st1w {z26.s}, p0, [x25]
st1w {z28.s}, p0, [x25, #1, MUL VL]
st1w {z30.s}, p0, [x26]
st1w {z8.s}, p0, [x26, #1, MUL VL]
st1w {z10.s}, p0, [x22]
mova z9.s,p0/m,za3h.s[w12,1]
ld1w {z11.s}, p0/z, [x2, #1, MUL VL]
mova z12.s,p0/m,za0h.s[w12,2]
ld1w {z13.s}, p0/z, [x20]
mova z14.s,p0/m,za1h.s[w12,2]
mova z25.s,p0/m,za0h.s[w12,3]
mova z27.s,p0/m,za1h.s[w12,3]
fmla z11.s,p0/m,z9.s,z20.s
ld1w {z22.s}, p0/z, [x20, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,2]
ld1w {z24.s}, p0/z, [x10]
mova z23.s,p0/m,za3h.s[w12,2]
ld1w {z26.s}, p0/z, [x10, #1, MUL VL]
ld1w {z28.s}, p0/z, [x11]
ld1w {z30.s}, p0/z, [x11, #1, MUL VL]
mova z29.s,p0/m,za2h.s[w12,3]
ld1w {z8.s}, p0/z, [x1]
mova z31.s,p0/m,za3h.s[w12,3]
ld1w {z10.s}, p0/z, [x1, #1, MUL VL]
fmla z13.s,p0/m,z12.s,z20.s
fmla z22.s,p0/m,z14.s,z20.s
fmla z24.s,p0/m,z21.s,z20.s
fmla z26.s,p0/m,z23.s,z20.s
fmla z28.s,p0/m,z25.s,z20.s
fmla z30.s,p0/m,z27.s,z20.s
fmla z8.s,p0/m,z29.s,z20.s
fmla z10.s,p0/m,z31.s,z20.s
st1w {z11.s}, p0, [x22, #1, MUL VL]
st1w {z13.s}, p0, [x27]
st1w {z22.s}, p0, [x27, #1, MUL VL]
st1w {z24.s}, p0, [x23]
st1w {z26.s}, p0, [x23, #1, MUL VL]
st1w {z28.s}, p0, [x24]
st1w {z30.s}, p0, [x24, #1, MUL VL]
st1w {z8.s}, p0, [x21]
st1w {z10.s}, p0, [x21, #1, MUL VL]
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x27,x27,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x21,x21,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr4_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x8
add x11,x0,x6
mov x16,x7
mov x12,#0
add x17,x0,x8
add x19,x0,x6
add x2,x2,x6
add x20,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
ld1rw {z20.s}, p0/z, [x5]
add x21,x3,x8
add x1,x1,x6
add x22,x3,x8
add x23,x3,x8
add x24,x3,x6
add x21,x21,x6
add x1,x1,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x22,x22,x6
add x27,x3,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
add x21,x21,x6, LSL #1
.ukr5_slices:
mova z21.s,p0/m,za0h.s[w12,0]
ld1w {z22.s}, p0/z, [x0]
mova z23.s,p0/m,za1h.s[w12,0]
ld1w {z24.s}, p0/z, [x0, #1, MUL VL]
mova z25.s,p0/m,za2h.s[w12,0]
ld1w {z26.s}, p0/z, [x17]
mova z27.s,p0/m,za3h.s[w12,0]
ld1w {z28.s}, p0/z, [x17, #1, MUL VL]
fmla z21.s,p0/m,z22.s,z20.s
fmla z23.s,p0/m,z24.s,z20.s
fmla z25.s,p0/m,z26.s,z20.s
fmla z27.s,p0/m,z28.s,z20.s
mova za0h.s[w12,0],p0/m,z21.s
mova za1h.s[w12,0],p0/m,z23.s
mova za2h.s[w12,0],p0/m,z25.s
mova za3h.s[w12,0],p0/m,z27.s
mova z29.s,p0/m,za0h.s[w12,1]
ld1w {z30.s}, p0/z, [x19]
mova z31.s,p0/m,za1h.s[w12,1]
ld1w {z8.s}, p0/z, [x19, #1, MUL VL]
mova z9.s,p0/m,za2h.s[w12,1]
ld1w {z10.s}, p0/z, [x2]
mova z11.s,p0/m,za3h.s[w12,1]
ld1w {z12.s}, p0/z, [x2, #1, MUL VL]
fmla z29.s,p0/m,z30.s,z20.s
fmla z31.s,p0/m,z8.s,z20.s
fmla z9.s,p0/m,z10.s,z20.s
fmla z11.s,p0/m,z12.s,z20.s
st1w {z21.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
mova za0h.s[w12,1],p0/m,z29.s
mova za1h.s[w12,1],p0/m,z31.s
mova za2h.s[w12,1],p0/m,z9.s
mova za3h.s[w12,1],p0/m,z11.s
mova z12.s,p0/m,za0h.s[w12,2]
ld1w {z13.s}, p0/z, [x20]
mova z14.s,p0/m,za1h.s[w12,2]
fmla z12.s,p0/m,z13.s,z20.s
ld1w {z22.s}, p0/z, [x20, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,2]
ld1w {z24.s}, p0/z, [x10]
mova z23.s,p0/m,za3h.s[w12,2]
ld1w {z26.s}, p0/z, [x10, #1, MUL VL]
fmla z14.s,p0/m,z22.s,z20.s
fmla z21.s,p0/m,z24.s,z20.s
fmla z23.s,p0/m,z26.s,z20.s
st1w {z25.s}, p0, [x25]
st1w {z27.s}, p0, [x25, #1, MUL VL]
st1w {z29.s}, p0, [x26]
st1w {z31.s}, p0, [x26, #1, MUL VL]
mova za0h.s[w12,2],p0/m,z12.s
mova za1h.s[w12,2],p0/m,z14.s
mova za2h.s[w12,2],p0/m,z21.s
mova za3h.s[w12,2],p0/m,z23.s
mova z25.s,p0/m,za0h.s[w12,3]
ld1w {z28.s}, p0/z, [x11]
mova z27.s,p0/m,za1h.s[w12,3]
ld1w {z30.s}, p0/z, [x11, #1, MUL VL]
mova z29.s,p0/m,za2h.s[w12,3]
ld1w {z8.s}, p0/z, [x1]
mova z31.s,p0/m,za3h.s[w12,3]
ld1w {z10.s}, p0/z, [x1, #1, MUL VL]
fmla z25.s,p0/m,z28.s,z20.s
fmla z27.s,p0/m,z30.s,z20.s
fmla z29.s,p0/m,z8.s,z20.s
fmla z31.s,p0/m,z10.s,z20.s
st1w {z9.s}, p0, [x22]
st1w {z11.s}, p0, [x22, #1, MUL VL]
st1w {z12.s}, p0, [x27]
st1w {z14.s}, p0, [x27, #1, MUL VL]
st1w {z21.s}, p0, [x23]
st1w {z23.s}, p0, [x23, #1, MUL VL]
st1w {z25.s}, p0, [x24]
st1w {z27.s}, p0, [x24, #1, MUL VL]
st1w {z29.s}, p0, [x21]
st1w {z31.s}, p0, [x21, #1, MUL VL]
mova za0h.s[w12,3],p0/m,z25.s
mova za1h.s[w12,3],p0/m,z27.s
mova za2h.s[w12,3],p0/m,z29.s
mova za3h.s[w12,3],p0/m,z31.s
add x0,x0,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x27,x27,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x21,x21,x6, LSL #2
add x12,x12,#4
add x16,x16,#-4
cbnz x16,.ukr5_slices
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
add x1,x0,x8
add x2,x0,x8
add x10,x0,x6
mov x11,x7
mov x12,#0
add x16,x0,x8
add x17,x0,x6
add x1,x1,x6
add x19,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x10,x10,x6, LSL #1
ld1rw {z20.s}, p0/z, [x5]
add x20,x0,x8
ld1rw {z21.s}, p0/z, [x4]
add x21,x3,x8
add x20,x20,x6
add x22,x3,x8
add x23,x3,x8
add x24,x3,x6
add x21,x21,x6
add x20,x20,x6, LSL #1
add x25,x3,x8
add x26,x3,x6
add x22,x22,x6
add x27,x3,x6, LSL #1
add x23,x23,x6, LSL #1
add x24,x24,x6, LSL #1
add x21,x21,x6, LSL #1
.ukr6_slices:
ld1w {z22.s}, p0/z, [x0]
ld1w {z23.s}, p0/z, [x0, #1, MUL VL]
ld1w {z24.s}, p0/z, [x16]
ld1w {z25.s}, p0/z, [x16, #1, MUL VL]
ld1w {z26.s}, p0/z, [x17]
ld1w {z27.s}, p0/z, [x17, #1, MUL VL]
ld1w {z28.s}, p0/z, [x1]
fmul z22.s,z22.s,z20.s
mova z29.s,p0/m,za0h.s[w12,0]
fmul z23.s,z23.s,z20.s
mova z30.s,p0/m,za1h.s[w12,0]
fmul z24.s,z24.s,z20.s
mova z31.s,p0/m,za2h.s[w12,0]
fmul z25.s,z25.s,z20.s
mova z8.s,p0/m,za3h.s[w12,0]
fmul z26.s,z26.s,z20.s
mova z9.s,p0/m,za0h.s[w12,1]
fmul z27.s,z27.s,z20.s
mova z10.s,p0/m,za1h.s[w12,1]
fmul z28.s,z28.s,z20.s
mova z11.s,p0/m,za2h.s[w12,1]
fmla z22.s,p0/m,z29.s,z21.s
fmla z23.s,p0/m,z30.s,z21.s
fmla z24.s,p0/m,z31.s,z21.s
fmla z25.s,p0/m,z8.s,z21.s
fmla z26.s,p0/m,z9.s,z21.s
fmla z27.s,p0/m,z10.s,z21.s
fmla z28.s,p0/m,z11.s,z21.s
st1w {z22.s}, p0, [x3]
st1w {z23.s}, p0, [x3, #1, MUL VL]
st1w {z24.s}, p0, [x25]
st1w {z25.s}, p0, [x25, #1, MUL VL]
st1w {z26.s}, p0, [x26]
st1w {z27.s}, p0, [x26, #1, MUL VL]
st1w {z28.s}, p0, [x22]
ld1w {z12.s}, p0/z, [x1, #1, MUL VL]
ld1w {z13.s}, p0/z, [x19]
ld1w {z22.s}, p0/z, [x19, #1, MUL VL]
ld1w {z23.s}, p0/z, [x2]
ld1w {z24.s}, p0/z, [x2, #1, MUL VL]
ld1w {z25.s}, p0/z, [x10]
ld1w {z26.s}, p0/z, [x10, #1, MUL VL]
ld1w {z27.s}, p0/z, [x20]
ld1w {z28.s}, p0/z, [x20, #1, MUL VL]
fmul z12.s,z12.s,z20.s
mova z14.s,p0/m,za3h.s[w12,1]
fmla z12.s,p0/m,z14.s,z21.s
fmul z13.s,z13.s,z20.s
mova z14.s,p0/m,za0h.s[w12,2]
mova z8.s,p0/m,za0h.s[w12,3]
fmla z13.s,p0/m,z14.s,z21.s
fmul z22.s,z22.s,z20.s
mova z29.s,p0/m,za1h.s[w12,2]
fmul z23.s,z23.s,z20.s
mova z30.s,p0/m,za2h.s[w12,2]
fmul z24.s,z24.s,z20.s
mova z31.s,p0/m,za3h.s[w12,2]
fmul z25.s,z25.s,z20.s
fmul z26.s,z26.s,z20.s
mova z9.s,p0/m,za1h.s[w12,3]
fmul z27.s,z27.s,z20.s
mova z10.s,p0/m,za2h.s[w12,3]
fmul z28.s,z28.s,z20.s
mova z11.s,p0/m,za3h.s[w12,3]
fmla z22.s,p0/m,z29.s,z21.s
fmla z23.s,p0/m,z30.s,z21.s
fmla z24.s,p0/m,z31.s,z21.s
fmla z25.s,p0/m,z8.s,z21.s
fmla z26.s,p0/m,z9.s,z21.s
fmla z27.s,p0/m,z10.s,z21.s
fmla z28.s,p0/m,z11.s,z21.s
st1w {z12.s}, p0, [x22, #1, MUL VL]
st1w {z13.s}, p0, [x27]
st1w {z22.s}, p0, [x27, #1, MUL VL]
st1w {z23.s}, p0, [x23]
st1w {z24.s}, p0, [x23, #1, MUL VL]
st1w {z25.s}, p0, [x24]
st1w {z26.s}, p0, [x24, #1, MUL VL]
st1w {z27.s}, p0, [x21]
st1w {z28.s}, p0, [x21, #1, MUL VL]
add x0,x0,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x1,x1,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x10,x10,x6, LSL #2
add x20,x20,x6, LSL #2
add x3,x3,x6, LSL #2
add x25,x25,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x27,x27,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x21,x21,x6, LSL #2
add x12,x12,#4
add x11,x11,#-4
cbnz x11,.ukr6_slices
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
ldr x19, [sp]
.cfi_restore x19
ldr x20, [sp, #8]
.cfi_restore x20
ldr x21, [sp, #16]
.cfi_restore x21
ldr x22, [sp, #24]
.cfi_restore x22
ldr x23, [sp, #32]
.cfi_restore x23
ldr x24, [sp, #40]
.cfi_restore x24
ldr x25, [sp, #48]
.cfi_restore x25
ldr x26, [sp, #56]
.cfi_restore x26
ldr x27, [sp, #64]
.cfi_restore x27
ldr x28, [sp, #72]
.cfi_restore x28
ldr d8, [sp, #80]
.cfi_restore d8
ldr d9, [sp, #88]
.cfi_restore d9
ldr d10, [sp, #96]
.cfi_restore d10
ldr d11, [sp, #104]
.cfi_restore d11
ldr d12, [sp, #112]
.cfi_restore d12
ldr d13, [sp, #120]
.cfi_restore d13
ldr d14, [sp, #128]
.cfi_restore d14
ldr d15, [sp, #136]
.cfi_restore d15
add sp,sp,#144
.cfi_adjust_cfa_offset -144
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
add sp,sp,#-144
.cfi_adjust_cfa_offset 144
str x19, [sp]
.cfi_rel_offset x19, 0
str x20, [sp, #8]
.cfi_rel_offset x20, 8
str x21, [sp, #16]
.cfi_rel_offset x21, 16
str x22, [sp, #24]
.cfi_rel_offset x22, 24
str x23, [sp, #32]
.cfi_rel_offset x23, 32
str x24, [sp, #40]
.cfi_rel_offset x24, 40
str x25, [sp, #48]
.cfi_rel_offset x25, 48
str x26, [sp, #56]
.cfi_rel_offset x26, 56
str x27, [sp, #64]
.cfi_rel_offset x27, 64
str d8, [sp, #72]
.cfi_rel_offset d8, 72
str d9, [sp, #80]
.cfi_rel_offset d9, 80
str d10, [sp, #88]
.cfi_rel_offset d10, 88
str d11, [sp, #96]
.cfi_rel_offset d11, 96
str d12, [sp, #104]
.cfi_rel_offset d12, 104
str d13, [sp, #112]
.cfi_rel_offset d13, 112
str d14, [sp, #120]
.cfi_rel_offset d14, 120
str d15, [sp, #128]
.cfi_rel_offset d15, 128
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
mov x1,x0
mov x2,x0
mov x9,x0
mov x10,x0
incb x1, ALL, MUL #1
mov x11,x0
mov x16,x0
incb x2, ALL, MUL #1
mov x17,x0
incb x9, ALL, MUL #1
incb x10, ALL, MUL #1
add x19,x0,x8
add x1,x1,x8
mov x20,x0
incb x11, ALL, MUL #1
incb x16, ALL, MUL #1
add x21,x0,x8
add x2,x2,x8
incb x17, ALL, MUL #1
add x22,x0,x8
add x9,x9,x8
add x23,x0,x6
add x10,x10,x6
add x19,x19,x6
add x1,x1,x6
mov x24,x7
mov x12,#0
incb x20, ALL, MUL #1
add x25,x0,x8
add x11,x11,x8
add x26,x0,x6
add x16,x16,x6
add x21,x21,x6
add x2,x2,x6
add x27,x0,x6, LSL #1
add x17,x17,x6, LSL #1
add x22,x22,x6, LSL #1
add x9,x9,x6, LSL #1
add x23,x23,x6, LSL #1
add x10,x10,x6, LSL #1
add x19,x19,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr1_slices:
st1w {za0h.s[w12, 0]}, p0, [x0]
st1w {za1h.s[w12, 0]}, p0, [x20]
st1w {za2h.s[w12, 0]}, p0, [x25]
st1w {za3h.s[w12, 0]}, p0, [x11]
st1w {za0h.s[w12, 1]}, p0, [x26]
st1w {za1h.s[w12, 1]}, p0, [x16]
st1w {za2h.s[w12, 1]}, p0, [x21]
st1w {za3h.s[w12, 1]}, p0, [x2]
st1w {za0h.s[w12, 2]}, p0, [x27]
st1w {za1h.s[w12, 2]}, p0, [x17]
st1w {za2h.s[w12, 2]}, p0, [x22]
st1w {za3h.s[w12, 2]}, p0, [x9]
st1w {za0h.s[w12, 3]}, p0, [x23]
st1w {za1h.s[w12, 3]}, p0, [x10]
st1w {za2h.s[w12, 3]}, p0, [x19]
st1w {za3h.s[w12, 3]}, p0, [x1]
add x0,x0,x6, LSL #2
add x20,x20,x6, LSL #2
add x25,x25,x6, LSL #2
add x11,x11,x6, LSL #2
add x26,x26,x6, LSL #2
add x16,x16,x6, LSL #2
add x21,x21,x6, LSL #2
add x2,x2,x6, LSL #2
add x27,x27,x6, LSL #2
add x17,x17,x6, LSL #2
add x22,x22,x6, LSL #2
add x9,x9,x6, LSL #2
add x23,x23,x6, LSL #2
add x10,x10,x6, LSL #2
add x19,x19,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x24,x24,#-4
cbnz x24,.ukr1_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1w {z0.s}, p0, [x0]
st1w {z1.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
add x1,x0,x8
add x2,x0,x8
add x9,x0,x8
add x10,x0,x6
mov x11,x7
mov x12,#0
add x16,x0,x8
add x17,x0,x6
add x2,x2,x6
add x19,x0,x6, LSL #1
add x9,x9,x6, LSL #1
add x10,x10,x6, LSL #1
ld1rw {z2.s}, p0/z, [x4]
add x1,x1,x6
add x1,x1,x6, LSL #1
.ukr2_slices:
mova z3.s,p0/m,za0h.s[w12,0]
mova z4.s,p0/m,za1h.s[w12,0]
fmul z5.s,z3.s,z2.s
fmul z6.s,z4.s,z2.s
st1w {z5.s}, p0, [x0]
st1w {z6.s}, p0, [x0, #1, MUL VL]
mova z4.s,p0/m,za2h.s[w12,0]
mova z7.s,p0/m,za3h.s[w12,0]
mova z16.s,p0/m,za0h.s[w12,1]
mova z17.s,p0/m,za1h.s[w12,1]
mova z18.s,p0/m,za2h.s[w12,1]
mova z19.s,p0/m,za3h.s[w12,1]
mova z20.s,p0/m,za0h.s[w12,2]
mova z21.s,p0/m,za1h.s[w12,2]
mova z22.s,p0/m,za2h.s[w12,2]
mova z23.s,p0/m,za3h.s[w12,2]
mova z24.s,p0/m,za0h.s[w12,3]
mova z25.s,p0/m,za1h.s[w12,3]
mova z26.s,p0/m,za2h.s[w12,3]
mova z3.s,p0/m,za3h.s[w12,3]
fmul z27.s,z4.s,z2.s
fmul z4.s,z7.s,z2.s
fmul z7.s,z16.s,z2.s
fmul z16.s,z17.s,z2.s
fmul z17.s,z18.s,z2.s
fmul z18.s,z19.s,z2.s
fmul z19.s,z20.s,z2.s
fmul z20.s,z21.s,z2.s
fmul z21.s,z22.s,z2.s
fmul z22.s,z23.s,z2.s
fmul z23.s,z24.s,z2.s
fmul z24.s,z25.s,z2.s
fmul z5.s,z26.s,z2.s
fmul z6.s,z3.s,z2.s
st1w {z27.s}, p0, [x16]
st1w {z4.s}, p0, [x16, #1, MUL VL]
st1w {z7.s}, p0, [x17]
st1w {z16.s}, p0, [x17, #1, MUL VL]
st1w {z17.s}, p0, [x2]
st1w {z18.s}, p0, [x2, #1, MUL VL]
st1w {z19.s}, p0, [x19]
st1w {z20.s}, p0, [x19, #1, MUL VL]
st1w {z21.s}, p0, [x9]
st1w {z22.s}, p0, [x9, #1, MUL VL]
st1w {z23.s}, p0, [x10]
st1w {z24.s}, p0, [x10, #1, MUL VL]
st1w {z5.s}, p0, [x1]
st1w {z6.s}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x19,x19,x6, LSL #2
add x9,x9,x6, LSL #2
add x10,x10,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
add x11,x11,#-4
cbnz x11,.ukr2_slices
fmul z3.s,z0.s,z2.s
fmul z0.s,z1.s,z2.s
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1w {z3.s}, p0, [x0]
st1w {z0.s}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
add x1,x0,x8
add x2,x0,x8
add x9,x0,x8
add x10,x0,x6
add x1,x1,x6
mov x11,x7
mov x12,#0
add x16,x0,x8
add x17,x0,x6
add x19,x3,x8
add x2,x2,x6
add x20,x0,x6, LSL #1
add x21,x3,x8
add x9,x9,x6, LSL #1
add x22,x3,x6
add x10,x10,x6, LSL #1
add x23,x3,x8
add x23,x23,x6
add x1,x1,x6, LSL #1
add x24,x3,x8
add x25,x3,x6
add x19,x19,x6
add x26,x3,x6, LSL #1
add x21,x21,x6, LSL #1
add x22,x22,x6, LSL #1
add x23,x23,x6, LSL #1
.ukr3_slices:
mova z2.s,p0/m,za0h.s[w12,0]
ld1w {z3.s}, p0/z, [x0]
fadd z3.s,z2.s,z3.s
st1w {z3.s}, p0, [x3]
mova z4.s,p0/m,za1h.s[w12,0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
mova z6.s,p0/m,za2h.s[w12,0]
ld1w {z7.s}, p0/z, [x16]
mova z16.s,p0/m,za3h.s[w12,0]
ld1w {z17.s}, p0/z, [x16, #1, MUL VL]
mova z18.s,p0/m,za0h.s[w12,1]
ld1w {z19.s}, p0/z, [x17]
mova z20.s,p0/m,za1h.s[w12,1]
ld1w {z21.s}, p0/z, [x17, #1, MUL VL]
mova z22.s,p0/m,za2h.s[w12,1]
ld1w {z23.s}, p0/z, [x2]
mova z24.s,p0/m,za3h.s[w12,1]
ld1w {z25.s}, p0/z, [x2, #1, MUL VL]
mova z26.s,p0/m,za0h.s[w12,2]
ld1w {z27.s}, p0/z, [x20]
mova z28.s,p0/m,za1h.s[w12,2]
ld1w {z29.s}, p0/z, [x20, #1, MUL VL]
mova z30.s,p0/m,za2h.s[w12,2]
ld1w {z31.s}, p0/z, [x9]
mova z8.s,p0/m,za3h.s[w12,2]
ld1w {z9.s}, p0/z, [x9, #1, MUL VL]
mova z10.s,p0/m,za0h.s[w12,3]
ld1w {z11.s}, p0/z, [x10]
mova z12.s,p0/m,za1h.s[w12,3]
ld1w {z13.s}, p0/z, [x10, #1, MUL VL]
mova z14.s,p0/m,za2h.s[w12,3]
mova z2.s,p0/m,za3h.s[w12,3]
fadd z5.s,z4.s,z5.s
ld1w {z4.s}, p0/z, [x1]
fadd z7.s,z6.s,z7.s
ld1w {z3.s}, p0/z, [x1, #1, MUL VL]
fadd z17.s,z16.s,z17.s
fadd z19.s,z18.s,z19.s
fadd z21.s,z20.s,z21.s
fadd z23.s,z22.s,z23.s
fadd z25.s,z24.s,z25.s
fadd z27.s,z26.s,z27.s
fadd z29.s,z28.s,z29.s
fadd z31.s,z30.s,z31.s
fadd z9.s,z8.s,z9.s
fadd z11.s,z10.s,z11.s
fadd z13.s,z12.s,z13.s
fadd z4.s,z14.s,z4.s
fadd z3.s,z2.s,z3.s
st1w {z5.s}, p0, [x3, #1, MUL VL]
st1w {z7.s}, p0, [x24]
st1w {z17.s}, p0, [x24, #1, MUL VL]
st1w {z19.s}, p0, [x25]
st1w {z21.s}, p0, [x25, #1, MUL VL]
st1w {z23.s}, p0, [x19]
st1w {z25.s}, p0, [x19, #1, MUL VL]
st1w {z27.s}, p0, [x26]
st1w {z29.s}, p0, [x26, #1, MUL VL]
st1w {z31.s}, p0, [x21]
st1w {z9.s}, p0, [x21, #1, MUL VL]
st1w {z11.s}, p0, [x22]
st1w {z13.s}, p0, [x22, #1, MUL VL]
st1w {z4.s}, p0, [x23]
st1w {z3.s}, p0, [x23, #1, MUL VL]
add x0,x0,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x9,x9,x6, LSL #2
add x10,x10,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x24,x24,x6, LSL #2
add x25,x25,x6, LSL #2
add x19,x19,x6, LSL #2
add x26,x26,x6, LSL #2
add x21,x21,x6, LSL #2
add x22,x22,x6, LSL #2
add x23,x23,x6, LSL #2
add x12,x12,#4
add x11,x11,#-4
cbnz x11,.ukr3_slices
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
add x1,x0,x8
add x2,x0,x8
add x9,x0,x8
add x10,x0,x6
mov x11,x7
mov x12,#0
add x16,x0,x8
add x17,x0,x6
add x2,x2,x6
add x19,x0,x6, LSL #1
add x9,x9,x6, LSL #1
add x10,x10,x6, LSL #1
ld1rw {z2.s}, p0/z, [x4]
add x20,x3,x8
add x1,x1,x6
add x21,x3,x8
add x22,x3,x8
add x23,x3,x6
add x20,x20,x6
add x1,x1,x6, LSL #1
add x24,x3,x8
add x25,x3,x6
add x21,x21,x6
add x26,x3,x6, LSL #1
add x22,x22,x6, LSL #1
add x23,x23,x6, LSL #1
add x20,x20,x6, LSL #1
.ukr4_slices:
mova z3.s,p0/m,za0h.s[w12,0]
ld1w {z4.s}, p0/z, [x0]
mova z5.s,p0/m,za1h.s[w12,0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
fmla z4.s,p0/m,z3.s,z2.s
fmla z6.s,p0/m,z5.s,z2.s
st1w {z4.s}, p0, [x3]
st1w {z6.s}, p0, [x3, #1, MUL VL]
mova z5.s,p0/m,za2h.s[w12,0]
ld1w {z7.s}, p0/z, [x16]
mova z16.s,p0/m,za3h.s[w12,0]
ld1w {z17.s}, p0/z, [x16, #1, MUL VL]
mova z18.s,p0/m,za0h.s[w12,1]
ld1w {z19.s}, p0/z, [x17]
mova z20.s,p0/m,za1h.s[w12,1]
ld1w {z21.s}, p0/z, [x17, #1, MUL VL]
mova z22.s,p0/m,za2h.s[w12,1]
ld1w {z23.s}, p0/z, [x2]
mova z24.s,p0/m,za3h.s[w12,1]
ld1w {z25.s}, p0/z, [x2, #1, MUL VL]
mova z26.s,p0/m,za0h.s[w12,2]
ld1w {z27.s}, p0/z, [x19]
mova z28.s,p0/m,za1h.s[w12,2]
ld1w {z29.s}, p0/z, [x19, #1, MUL VL]
mova z30.s,p0/m,za2h.s[w12,2]
ld1w {z31.s}, p0/z, [x9]
mova z8.s,p0/m,za3h.s[w12,2]
ld1w {z9.s}, p0/z, [x9, #1, MUL VL]
mova z10.s,p0/m,za0h.s[w12,3]
ld1w {z11.s}, p0/z, [x10]
mova z12.s,p0/m,za1h.s[w12,3]
ld1w {z13.s}, p0/z, [x10, #1, MUL VL]
mova z14.s,p0/m,za2h.s[w12,3]
mova z3.s,p0/m,za3h.s[w12,3]
fmla z7.s,p0/m,z5.s,z2.s
ld1w {z4.s}, p0/z, [x1]
ld1w {z6.s}, p0/z, [x1, #1, MUL VL]
fmla z17.s,p0/m,z16.s,z2.s
fmla z19.s,p0/m,z18.s,z2.s
fmla z21.s,p0/m,z20.s,z2.s
fmla z23.s,p0/m,z22.s,z2.s
fmla z25.s,p0/m,z24.s,z2.s
fmla z27.s,p0/m,z26.s,z2.s
fmla z29.s,p0/m,z28.s,z2.s
fmla z31.s,p0/m,z30.s,z2.s
fmla z9.s,p0/m,z8.s,z2.s
fmla z11.s,p0/m,z10.s,z2.s
fmla z13.s,p0/m,z12.s,z2.s
fmla z4.s,p0/m,z14.s,z2.s
fmla z6.s,p0/m,z3.s,z2.s
st1w {z7.s}, p0, [x24]
st1w {z17.s}, p0, [x24, #1, MUL VL]
st1w {z19.s}, p0, [x25]
st1w {z21.s}, p0, [x25, #1, MUL VL]
st1w {z23.s}, p0, [x21]
st1w {z25.s}, p0, [x21, #1, MUL VL]
st1w {z27.s}, p0, [x26]
st1w {z29.s}, p0, [x26, #1, MUL VL]
st1w {z31.s}, p0, [x22]
st1w {z9.s}, p0, [x22, #1, MUL VL]
st1w {z11.s}, p0, [x23]
st1w {z13.s}, p0, [x23, #1, MUL VL]
st1w {z4.s}, p0, [x20]
st1w {z6.s}, p0, [x20, #1, MUL VL]
add x0,x0,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x19,x19,x6, LSL #2
add x9,x9,x6, LSL #2
add x10,x10,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x24,x24,x6, LSL #2
add x25,x25,x6, LSL #2
add x21,x21,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x23,x23,x6, LSL #2
add x20,x20,x6, LSL #2
add x12,x12,#4
add x11,x11,#-4
cbnz x11,.ukr4_slices
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
add x1,x0,x8
add x2,x0,x8
add x9,x0,x8
add x10,x0,x6
mov x11,x7
mov x12,#0
add x16,x0,x8
add x17,x0,x6
add x2,x2,x6
add x19,x0,x6, LSL #1
add x9,x9,x6, LSL #1
add x10,x10,x6, LSL #1
ld1rw {z2.s}, p0/z, [x5]
add x20,x3,x8
add x1,x1,x6
add x21,x3,x8
add x22,x3,x8
add x23,x3,x6
add x20,x20,x6
add x1,x1,x6, LSL #1
add x24,x3,x8
add x25,x3,x6
add x21,x21,x6
add x26,x3,x6, LSL #1
add x22,x22,x6, LSL #1
add x23,x23,x6, LSL #1
add x20,x20,x6, LSL #1
.ukr5_slices:
mova z3.s,p0/m,za0h.s[w12,0]
ld1w {z4.s}, p0/z, [x0]
mova z5.s,p0/m,za1h.s[w12,0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
mova z7.s,p0/m,za2h.s[w12,0]
ld1w {z16.s}, p0/z, [x16]
mova z17.s,p0/m,za3h.s[w12,0]
ld1w {z18.s}, p0/z, [x16, #1, MUL VL]
fmla z3.s,p0/m,z4.s,z2.s
fmla z5.s,p0/m,z6.s,z2.s
fmla z7.s,p0/m,z16.s,z2.s
fmla z17.s,p0/m,z18.s,z2.s
mova za0h.s[w12,0],p0/m,z3.s
mova za1h.s[w12,0],p0/m,z5.s
mova za2h.s[w12,0],p0/m,z7.s
mova za3h.s[w12,0],p0/m,z17.s
mova z16.s,p0/m,za0h.s[w12,1]
ld1w {z18.s}, p0/z, [x17]
mova z19.s,p0/m,za1h.s[w12,1]
ld1w {z20.s}, p0/z, [x17, #1, MUL VL]
mova z21.s,p0/m,za2h.s[w12,1]
ld1w {z22.s}, p0/z, [x2]
mova z23.s,p0/m,za3h.s[w12,1]
ld1w {z24.s}, p0/z, [x2, #1, MUL VL]
fmla z16.s,p0/m,z18.s,z2.s
fmla z19.s,p0/m,z20.s,z2.s
fmla z21.s,p0/m,z22.s,z2.s
fmla z23.s,p0/m,z24.s,z2.s
mova za0h.s[w12,1],p0/m,z16.s
mova za1h.s[w12,1],p0/m,z19.s
mova za2h.s[w12,1],p0/m,z21.s
mova za3h.s[w12,1],p0/m,z23.s
mova z18.s,p0/m,za0h.s[w12,2]
ld1w {z20.s}, p0/z, [x19]
mova z22.s,p0/m,za1h.s[w12,2]
ld1w {z24.s}, p0/z, [x19, #1, MUL VL]
mova z25.s,p0/m,za2h.s[w12,2]
ld1w {z26.s}, p0/z, [x9]
mova z27.s,p0/m,za3h.s[w12,2]
ld1w {z28.s}, p0/z, [x9, #1, MUL VL]
fmla z18.s,p0/m,z20.s,z2.s
fmla z22.s,p0/m,z24.s,z2.s
fmla z25.s,p0/m,z26.s,z2.s
fmla z27.s,p0/m,z28.s,z2.s
st1w {z3.s}, p0, [x3]
mova za0h.s[w12,2],p0/m,z18.s
mova za1h.s[w12,2],p0/m,z22.s
mova za2h.s[w12,2],p0/m,z25.s
mova za3h.s[w12,2],p0/m,z27.s
mova z20.s,p0/m,za0h.s[w12,3]
ld1w {z24.s}, p0/z, [x10]
mova z26.s,p0/m,za1h.s[w12,3]
ld1w {z28.s}, p0/z, [x10, #1, MUL VL]
mova z29.s,p0/m,za2h.s[w12,3]
ld1w {z4.s}, p0/z, [x1]
mova z3.s,p0/m,za3h.s[w12,3]
ld1w {z6.s}, p0/z, [x1, #1, MUL VL]
fmla z20.s,p0/m,z24.s,z2.s
fmla z26.s,p0/m,z28.s,z2.s
fmla z29.s,p0/m,z4.s,z2.s
fmla z3.s,p0/m,z6.s,z2.s
st1w {z5.s}, p0, [x3, #1, MUL VL]
st1w {z7.s}, p0, [x24]
st1w {z17.s}, p0, [x24, #1, MUL VL]
st1w {z16.s}, p0, [x25]
st1w {z19.s}, p0, [x25, #1, MUL VL]
st1w {z21.s}, p0, [x21]
st1w {z23.s}, p0, [x21, #1, MUL VL]
st1w {z18.s}, p0, [x26]
st1w {z22.s}, p0, [x26, #1, MUL VL]
st1w {z25.s}, p0, [x22]
st1w {z27.s}, p0, [x22, #1, MUL VL]
st1w {z20.s}, p0, [x23]
st1w {z26.s}, p0, [x23, #1, MUL VL]
st1w {z29.s}, p0, [x20]
st1w {z3.s}, p0, [x20, #1, MUL VL]
mova za0h.s[w12,3],p0/m,z20.s
mova za1h.s[w12,3],p0/m,z26.s
mova za2h.s[w12,3],p0/m,z29.s
mova za3h.s[w12,3],p0/m,z3.s
add x0,x0,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x19,x19,x6, LSL #2
add x9,x9,x6, LSL #2
add x10,x10,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x24,x24,x6, LSL #2
add x25,x25,x6, LSL #2
add x21,x21,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x23,x23,x6, LSL #2
add x20,x20,x6, LSL #2
add x12,x12,#4
add x11,x11,#-4
cbnz x11,.ukr5_slices
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
add x1,x0,x8
add x2,x0,x8
add x9,x0,x6
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x9,x9,x6, LSL #1
ld1rw {z2.s}, p0/z, [x5]
add x19,x0,x8
ld1rw {z3.s}, p0/z, [x4]
add x20,x3,x8
add x19,x19,x6
add x21,x3,x8
add x22,x3,x8
add x23,x3,x6
add x20,x20,x6
add x19,x19,x6, LSL #1
add x24,x3,x8
add x25,x3,x6
add x21,x21,x6
add x26,x3,x6, LSL #1
add x22,x22,x6, LSL #1
add x23,x23,x6, LSL #1
add x20,x20,x6, LSL #1
.ukr6_slices:
ld1w {z4.s}, p0/z, [x0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
fmul z4.s,z4.s,z2.s
mova z6.s,p0/m,za0h.s[w12,0]
fmul z5.s,z5.s,z2.s
mova z7.s,p0/m,za1h.s[w12,0]
fmla z4.s,p0/m,z6.s,z3.s
fmla z5.s,p0/m,z7.s,z3.s
st1w {z4.s}, p0, [x3]
st1w {z5.s}, p0, [x3, #1, MUL VL]
ld1w {z16.s}, p0/z, [x11]
ld1w {z17.s}, p0/z, [x11, #1, MUL VL]
ld1w {z18.s}, p0/z, [x16]
ld1w {z19.s}, p0/z, [x16, #1, MUL VL]
ld1w {z20.s}, p0/z, [x1]
ld1w {z21.s}, p0/z, [x1, #1, MUL VL]
ld1w {z22.s}, p0/z, [x17]
ld1w {z23.s}, p0/z, [x17, #1, MUL VL]
ld1w {z24.s}, p0/z, [x2]
ld1w {z25.s}, p0/z, [x2, #1, MUL VL]
ld1w {z26.s}, p0/z, [x9]
ld1w {z27.s}, p0/z, [x9, #1, MUL VL]
ld1w {z4.s}, p0/z, [x19]
ld1w {z5.s}, p0/z, [x19, #1, MUL VL]
fmul z16.s,z16.s,z2.s
mova z28.s,p0/m,za2h.s[w12,0]
fmul z17.s,z17.s,z2.s
mova z29.s,p0/m,za3h.s[w12,0]
fmul z18.s,z18.s,z2.s
mova z30.s,p0/m,za0h.s[w12,1]
fmul z19.s,z19.s,z2.s
mova z31.s,p0/m,za1h.s[w12,1]
fmul z20.s,z20.s,z2.s
mova z8.s,p0/m,za2h.s[w12,1]
fmul z21.s,z21.s,z2.s
mova z9.s,p0/m,za3h.s[w12,1]
fmul z22.s,z22.s,z2.s
mova z10.s,p0/m,za0h.s[w12,2]
fmul z23.s,z23.s,z2.s
mova z11.s,p0/m,za1h.s[w12,2]
fmul z24.s,z24.s,z2.s
mova z12.s,p0/m,za2h.s[w12,2]
fmul z25.s,z25.s,z2.s
mova z13.s,p0/m,za3h.s[w12,2]
fmul z26.s,z26.s,z2.s
mova z14.s,p0/m,za0h.s[w12,3]
mova z6.s,p0/m,za2h.s[w12,3]
mova z7.s,p0/m,za3h.s[w12,3]
fmla z16.s,p0/m,z28.s,z3.s
fmul z27.s,z27.s,z2.s
mova z28.s,p0/m,za1h.s[w12,3]
fmla z17.s,p0/m,z29.s,z3.s
fmul z4.s,z4.s,z2.s
fmul z5.s,z5.s,z2.s
fmla z18.s,p0/m,z30.s,z3.s
fmla z19.s,p0/m,z31.s,z3.s
fmla z20.s,p0/m,z8.s,z3.s
fmla z21.s,p0/m,z9.s,z3.s
fmla z22.s,p0/m,z10.s,z3.s
fmla z23.s,p0/m,z11.s,z3.s
fmla z24.s,p0/m,z12.s,z3.s
fmla z25.s,p0/m,z13.s,z3.s
fmla z26.s,p0/m,z14.s,z3.s
fmla z27.s,p0/m,z28.s,z3.s
fmla z4.s,p0/m,z6.s,z3.s
fmla z5.s,p0/m,z7.s,z3.s
st1w {z16.s}, p0, [x24]
st1w {z17.s}, p0, [x24, #1, MUL VL]
st1w {z18.s}, p0, [x25]
st1w {z19.s}, p0, [x25, #1, MUL VL]
st1w {z20.s}, p0, [x21]
st1w {z21.s}, p0, [x21, #1, MUL VL]
st1w {z22.s}, p0, [x26]
st1w {z23.s}, p0, [x26, #1, MUL VL]
st1w {z24.s}, p0, [x22]
st1w {z25.s}, p0, [x22, #1, MUL VL]
st1w {z26.s}, p0, [x23]
st1w {z27.s}, p0, [x23, #1, MUL VL]
st1w {z4.s}, p0, [x20]
st1w {z5.s}, p0, [x20, #1, MUL VL]
add x0,x0,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
add x1,x1,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x9,x9,x6, LSL #2
add x19,x19,x6, LSL #2
add x3,x3,x6, LSL #2
add x24,x24,x6, LSL #2
add x25,x25,x6, LSL #2
add x21,x21,x6, LSL #2
add x26,x26,x6, LSL #2
add x22,x22,x6, LSL #2
add x23,x23,x6, LSL #2
add x20,x20,x6, LSL #2
add x12,x12,#4
add x10,x10,#-4
cbnz x10,.ukr6_slices
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
ldr x19, [sp]
.cfi_restore x19
ldr x20, [sp, #8]
.cfi_restore x20
ldr x21, [sp, #16]
.cfi_restore x21
ldr x22, [sp, #24]
.cfi_restore x22
ldr x23, [sp, #32]
.cfi_restore x23
ldr x24, [sp, #40]
.cfi_restore x24
ldr x25, [sp, #48]
.cfi_restore x25
ldr x26, [sp, #56]
.cfi_restore x26
ldr x27, [sp, #64]
.cfi_restore x27
ldr d8, [sp, #72]
.cfi_restore d8
ldr d9, [sp, #80]
.cfi_restore d9
ldr d10, [sp, #88]
.cfi_restore d10
ldr d11, [sp, #96]
.cfi_restore d11
ldr d12, [sp, #104]
.cfi_restore d12
ldr d13, [sp, #112]
.cfi_restore d13
ldr d14, [sp, #120]
.cfi_restore d14
ldr d15, [sp, #128]
.cfi_restore d15
add sp,sp,#144
.cfi_adjust_cfa_offset -144
ret
.cfi_endproc
.size bli_sgemm_ukrgen_sme_sf_2vx2v_1x2v_asm, .-bli_sgemm_ukrgen_sme_sf_2vx2v_1x2v_asm
.section .note.GNU-stack,"",%progbits
