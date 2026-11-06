.text
.global bli_sgemm_ukrgen_sme_opa_2vx2v_asm
.type bli_sgemm_ukrgen_sme_opa_2vx2v_asm, %function
bli_sgemm_ukrgen_sme_opa_2vx2v_asm:
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
add x19,x0,x8
incb x10, ALL, MUL #1
add x1,x1,x8
mov x20,x0
incb x11, ALL, MUL #1
add x21,x0,x8
incb x16, ALL, MUL #1
add x2,x2,x8
add x22,x0,x8
incb x17, ALL, MUL #1
add x9,x9,x8
add x23,x0,x6
add x19,x19,x6
add x10,x10,x6
add x1,x1,x6
mov x24,x7
mov x12,#0
add x25,x0,x8
incb x20, ALL, MUL #1
add x11,x11,x8
add x26,x0,x6
add x21,x21,x6
add x16,x16,x6
add x2,x2,x6
add x27,x0,x6, LSL #1
add x22,x22,x6, LSL #1
add x17,x17,x6, LSL #1
add x9,x9,x6, LSL #1
add x23,x23,x6, LSL #1
add x19,x19,x6, LSL #1
add x10,x10,x6, LSL #1
add x1,x1,x6, LSL #1
.ukr1_slices:
add x24,x24,#-4
st1w {za0v.s[w12, 0]}, p0, [x0]
st1w {za1v.s[w12, 0]}, p0, [x25]
st1w {za2v.s[w12, 0]}, p0, [x20]
st1w {za3v.s[w12, 0]}, p0, [x11]
st1w {za0v.s[w12, 1]}, p0, [x26]
st1w {za1v.s[w12, 1]}, p0, [x21]
st1w {za2v.s[w12, 1]}, p0, [x16]
st1w {za3v.s[w12, 1]}, p0, [x2]
st1w {za0v.s[w12, 2]}, p0, [x27]
st1w {za1v.s[w12, 2]}, p0, [x22]
st1w {za2v.s[w12, 2]}, p0, [x17]
st1w {za3v.s[w12, 2]}, p0, [x9]
st1w {za0v.s[w12, 3]}, p0, [x23]
st1w {za1v.s[w12, 3]}, p0, [x19]
st1w {za2v.s[w12, 3]}, p0, [x10]
st1w {za3v.s[w12, 3]}, p0, [x1]
add x0,x0,x6, LSL #2
add x25,x25,x6, LSL #2
add x20,x20,x6, LSL #2
add x11,x11,x6, LSL #2
add x26,x26,x6, LSL #2
add x21,x21,x6, LSL #2
add x16,x16,x6, LSL #2
add x2,x2,x6, LSL #2
add x27,x27,x6, LSL #2
add x22,x22,x6, LSL #2
add x17,x17,x6, LSL #2
add x9,x9,x6, LSL #2
add x23,x23,x6, LSL #2
add x19,x19,x6, LSL #2
add x10,x10,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
cbnz x24,.ukr1_slices
sub x0,x0,x8
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
ld1rw {z0.s}, p0/z, [x4]
add x1,x1,x6
add x1,x1,x6, LSL #1
.ukr2_slices:
add x11,x11,#-4
mova z1.s,p0/m,za0v.s[w12,0]
fmul z2.s,z1.s,z0.s
st1w {z2.s}, p0, [x0]
mova z1.s,p0/m,za1v.s[w12,0]
mova z3.s,p0/m,za2v.s[w12,0]
mova z4.s,p0/m,za3v.s[w12,0]
mova z5.s,p0/m,za0v.s[w12,1]
mova z6.s,p0/m,za1v.s[w12,1]
mova z7.s,p0/m,za2v.s[w12,1]
mova z16.s,p0/m,za3v.s[w12,1]
mova z17.s,p0/m,za0v.s[w12,2]
mova z18.s,p0/m,za1v.s[w12,2]
mova z19.s,p0/m,za2v.s[w12,2]
mova z20.s,p0/m,za3v.s[w12,2]
mova z21.s,p0/m,za0v.s[w12,3]
mova z22.s,p0/m,za1v.s[w12,3]
mova z23.s,p0/m,za2v.s[w12,3]
mova z24.s,p0/m,za3v.s[w12,3]
fmul z25.s,z1.s,z0.s
fmul z1.s,z3.s,z0.s
fmul z3.s,z4.s,z0.s
fmul z4.s,z5.s,z0.s
fmul z5.s,z6.s,z0.s
fmul z6.s,z7.s,z0.s
fmul z7.s,z16.s,z0.s
fmul z16.s,z17.s,z0.s
fmul z17.s,z18.s,z0.s
fmul z18.s,z19.s,z0.s
fmul z19.s,z20.s,z0.s
fmul z20.s,z21.s,z0.s
fmul z21.s,z22.s,z0.s
fmul z22.s,z23.s,z0.s
fmul z2.s,z24.s,z0.s
st1w {z25.s}, p0, [x16]
st1w {z1.s}, p0, [x0, #1, MUL VL]
st1w {z3.s}, p0, [x16, #1, MUL VL]
st1w {z4.s}, p0, [x17]
st1w {z5.s}, p0, [x2]
st1w {z6.s}, p0, [x17, #1, MUL VL]
st1w {z7.s}, p0, [x2, #1, MUL VL]
st1w {z16.s}, p0, [x19]
st1w {z17.s}, p0, [x9]
st1w {z18.s}, p0, [x19, #1, MUL VL]
st1w {z19.s}, p0, [x9, #1, MUL VL]
st1w {z20.s}, p0, [x10]
st1w {z21.s}, p0, [x1]
st1w {z22.s}, p0, [x10, #1, MUL VL]
st1w {z2.s}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x2,x2,x6, LSL #2
add x19,x19,x6, LSL #2
add x9,x9,x6, LSL #2
add x10,x10,x6, LSL #2
add x1,x1,x6, LSL #2
add x12,x12,#4
cbnz x11,.ukr2_slices
sub x0,x0,x8
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
add x9,x0,x8
add x10,x0,x8
add x11,x0,x6
add x1,x1,x6
add x16,x3,x8
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
mov x20,x7
mov x12,#0
add x21,x0,x8
add x22,x0,x6
add x9,x9,x6
add x23,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x24,x3,x8
add x25,x3,x6
add x16,x16,x6
add x26,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
.ukr3_slices:
add x20,x20,#-4
mova z0.s,p0/m,za0v.s[w12,0]
ld1w {z1.s}, p0/z, [x0]
mova z2.s,p0/m,za1v.s[w12,0]
ld1w {z3.s}, p0/z, [x21]
mova z4.s,p0/m,za2v.s[w12,0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
mova z6.s,p0/m,za3v.s[w12,0]
ld1w {z7.s}, p0/z, [x21, #1, MUL VL]
mova z16.s,p0/m,za0v.s[w12,1]
ld1w {z17.s}, p0/z, [x22]
mova z18.s,p0/m,za1v.s[w12,1]
ld1w {z19.s}, p0/z, [x9]
mova z20.s,p0/m,za2v.s[w12,1]
ld1w {z21.s}, p0/z, [x22, #1, MUL VL]
mova z22.s,p0/m,za3v.s[w12,1]
ld1w {z23.s}, p0/z, [x9, #1, MUL VL]
mova z24.s,p0/m,za0v.s[w12,2]
ld1w {z25.s}, p0/z, [x23]
mova z26.s,p0/m,za1v.s[w12,2]
ld1w {z27.s}, p0/z, [x10]
mova z28.s,p0/m,za2v.s[w12,2]
ld1w {z29.s}, p0/z, [x23, #1, MUL VL]
mova z30.s,p0/m,za3v.s[w12,2]
ld1w {z31.s}, p0/z, [x10, #1, MUL VL]
mova z8.s,p0/m,za0v.s[w12,3]
ld1w {z9.s}, p0/z, [x11]
mova z10.s,p0/m,za1v.s[w12,3]
ld1w {z11.s}, p0/z, [x1]
mova z12.s,p0/m,za2v.s[w12,3]
ld1w {z13.s}, p0/z, [x11, #1, MUL VL]
mova z14.s,p0/m,za3v.s[w12,3]
fadd z1.s,z0.s,z1.s
ld1w {z0.s}, p0/z, [x1, #1, MUL VL]
fadd z3.s,z2.s,z3.s
fadd z5.s,z4.s,z5.s
fadd z7.s,z6.s,z7.s
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
fadd z0.s,z14.s,z0.s
st1w {z1.s}, p0, [x3]
st1w {z3.s}, p0, [x24]
st1w {z5.s}, p0, [x3, #1, MUL VL]
st1w {z7.s}, p0, [x24, #1, MUL VL]
st1w {z17.s}, p0, [x25]
st1w {z19.s}, p0, [x16]
st1w {z21.s}, p0, [x25, #1, MUL VL]
st1w {z23.s}, p0, [x16, #1, MUL VL]
st1w {z25.s}, p0, [x26]
st1w {z27.s}, p0, [x17]
st1w {z29.s}, p0, [x26, #1, MUL VL]
st1w {z31.s}, p0, [x17, #1, MUL VL]
st1w {z9.s}, p0, [x19]
st1w {z11.s}, p0, [x2]
st1w {z13.s}, p0, [x19, #1, MUL VL]
st1w {z0.s}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #2
add x21,x21,x6, LSL #2
add x22,x22,x6, LSL #2
add x9,x9,x6, LSL #2
add x23,x23,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x1,x1,x6, LSL #2
add x3,x3,x6, LSL #2
add x24,x24,x6, LSL #2
add x25,x25,x6, LSL #2
add x16,x16,x6, LSL #2
add x26,x26,x6, LSL #2
add x17,x17,x6, LSL #2
add x19,x19,x6, LSL #2
add x2,x2,x6, LSL #2
add x12,x12,#4
cbnz x20,.ukr3_slices
sub x0,x0,x8
sub x3,x3,x8
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
ld1rw {z0.s}, p0/z, [x4]
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
add x11,x11,#-4
mova z1.s,p0/m,za0v.s[w12,0]
ld1w {z2.s}, p0/z, [x0]
fmla z2.s,p0/m,z1.s,z0.s
st1w {z2.s}, p0, [x3]
mova z1.s,p0/m,za1v.s[w12,0]
ld1w {z3.s}, p0/z, [x16]
mova z4.s,p0/m,za2v.s[w12,0]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
mova z6.s,p0/m,za3v.s[w12,0]
ld1w {z7.s}, p0/z, [x16, #1, MUL VL]
mova z16.s,p0/m,za0v.s[w12,1]
ld1w {z17.s}, p0/z, [x17]
mova z18.s,p0/m,za1v.s[w12,1]
ld1w {z19.s}, p0/z, [x2]
mova z20.s,p0/m,za2v.s[w12,1]
ld1w {z21.s}, p0/z, [x17, #1, MUL VL]
mova z22.s,p0/m,za3v.s[w12,1]
ld1w {z23.s}, p0/z, [x2, #1, MUL VL]
mova z24.s,p0/m,za0v.s[w12,2]
ld1w {z25.s}, p0/z, [x19]
mova z26.s,p0/m,za1v.s[w12,2]
ld1w {z27.s}, p0/z, [x9]
mova z28.s,p0/m,za2v.s[w12,2]
ld1w {z29.s}, p0/z, [x19, #1, MUL VL]
mova z30.s,p0/m,za3v.s[w12,2]
ld1w {z31.s}, p0/z, [x9, #1, MUL VL]
mova z8.s,p0/m,za0v.s[w12,3]
ld1w {z9.s}, p0/z, [x10]
mova z10.s,p0/m,za1v.s[w12,3]
ld1w {z11.s}, p0/z, [x1]
mova z12.s,p0/m,za2v.s[w12,3]
ld1w {z13.s}, p0/z, [x10, #1, MUL VL]
mova z14.s,p0/m,za3v.s[w12,3]
fmla z3.s,p0/m,z1.s,z0.s
ld1w {z2.s}, p0/z, [x1, #1, MUL VL]
fmla z5.s,p0/m,z4.s,z0.s
fmla z7.s,p0/m,z6.s,z0.s
fmla z17.s,p0/m,z16.s,z0.s
fmla z19.s,p0/m,z18.s,z0.s
fmla z21.s,p0/m,z20.s,z0.s
fmla z23.s,p0/m,z22.s,z0.s
fmla z25.s,p0/m,z24.s,z0.s
fmla z27.s,p0/m,z26.s,z0.s
fmla z29.s,p0/m,z28.s,z0.s
fmla z31.s,p0/m,z30.s,z0.s
fmla z9.s,p0/m,z8.s,z0.s
fmla z11.s,p0/m,z10.s,z0.s
fmla z13.s,p0/m,z12.s,z0.s
fmla z2.s,p0/m,z14.s,z0.s
st1w {z3.s}, p0, [x24]
st1w {z5.s}, p0, [x3, #1, MUL VL]
st1w {z7.s}, p0, [x24, #1, MUL VL]
st1w {z17.s}, p0, [x25]
st1w {z19.s}, p0, [x21]
st1w {z21.s}, p0, [x25, #1, MUL VL]
st1w {z23.s}, p0, [x21, #1, MUL VL]
st1w {z25.s}, p0, [x26]
st1w {z27.s}, p0, [x22]
st1w {z29.s}, p0, [x26, #1, MUL VL]
st1w {z31.s}, p0, [x22, #1, MUL VL]
st1w {z9.s}, p0, [x23]
st1w {z11.s}, p0, [x20]
st1w {z13.s}, p0, [x23, #1, MUL VL]
st1w {z2.s}, p0, [x20, #1, MUL VL]
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
cbnz x11,.ukr4_slices
sub x0,x0,x8
sub x3,x3,x8
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
ld1rw {z0.s}, p0/z, [x5]
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
add x11,x11,#-4
mova z1.s,p0/m,za0v.s[w12,0]
ld1w {z2.s}, p0/z, [x0]
mova z3.s,p0/m,za1v.s[w12,0]
ld1w {z4.s}, p0/z, [x16]
mova z5.s,p0/m,za2v.s[w12,0]
ld1w {z6.s}, p0/z, [x0, #1, MUL VL]
mova z7.s,p0/m,za3v.s[w12,0]
ld1w {z16.s}, p0/z, [x16, #1, MUL VL]
fmla z1.s,p0/m,z2.s,z0.s
fmla z3.s,p0/m,z4.s,z0.s
fmla z5.s,p0/m,z6.s,z0.s
fmla z7.s,p0/m,z16.s,z0.s
mova za0v.s[w12,0],p0/m,z1.s
mova za1v.s[w12,0],p0/m,z3.s
mova za2v.s[w12,0],p0/m,z5.s
mova za3v.s[w12,0],p0/m,z7.s
mova z4.s,p0/m,za0v.s[w12,1]
ld1w {z6.s}, p0/z, [x17]
mova z16.s,p0/m,za1v.s[w12,1]
ld1w {z17.s}, p0/z, [x2]
mova z18.s,p0/m,za2v.s[w12,1]
ld1w {z19.s}, p0/z, [x17, #1, MUL VL]
mova z20.s,p0/m,za3v.s[w12,1]
ld1w {z21.s}, p0/z, [x2, #1, MUL VL]
fmla z4.s,p0/m,z6.s,z0.s
fmla z16.s,p0/m,z17.s,z0.s
fmla z18.s,p0/m,z19.s,z0.s
fmla z20.s,p0/m,z21.s,z0.s
mova za0v.s[w12,1],p0/m,z4.s
mova za1v.s[w12,1],p0/m,z16.s
mova za2v.s[w12,1],p0/m,z18.s
mova za3v.s[w12,1],p0/m,z20.s
mova z6.s,p0/m,za0v.s[w12,2]
ld1w {z17.s}, p0/z, [x19]
mova z19.s,p0/m,za1v.s[w12,2]
ld1w {z21.s}, p0/z, [x9]
mova z22.s,p0/m,za2v.s[w12,2]
ld1w {z23.s}, p0/z, [x19, #1, MUL VL]
mova z24.s,p0/m,za3v.s[w12,2]
ld1w {z25.s}, p0/z, [x9, #1, MUL VL]
fmla z6.s,p0/m,z17.s,z0.s
fmla z19.s,p0/m,z21.s,z0.s
fmla z22.s,p0/m,z23.s,z0.s
fmla z24.s,p0/m,z25.s,z0.s
mova za0v.s[w12,2],p0/m,z6.s
mova za1v.s[w12,2],p0/m,z19.s
mova za2v.s[w12,2],p0/m,z22.s
mova za3v.s[w12,2],p0/m,z24.s
mova z17.s,p0/m,za0v.s[w12,3]
ld1w {z21.s}, p0/z, [x10]
mova z23.s,p0/m,za1v.s[w12,3]
ld1w {z25.s}, p0/z, [x1]
mova z26.s,p0/m,za2v.s[w12,3]
ld1w {z27.s}, p0/z, [x10, #1, MUL VL]
mova z28.s,p0/m,za3v.s[w12,3]
ld1w {z2.s}, p0/z, [x1, #1, MUL VL]
fmla z17.s,p0/m,z21.s,z0.s
fmla z23.s,p0/m,z25.s,z0.s
fmla z26.s,p0/m,z27.s,z0.s
fmla z28.s,p0/m,z2.s,z0.s
st1w {z1.s}, p0, [x3]
st1w {z3.s}, p0, [x24]
st1w {z5.s}, p0, [x3, #1, MUL VL]
st1w {z7.s}, p0, [x24, #1, MUL VL]
st1w {z4.s}, p0, [x25]
st1w {z16.s}, p0, [x21]
st1w {z18.s}, p0, [x25, #1, MUL VL]
st1w {z20.s}, p0, [x21, #1, MUL VL]
st1w {z6.s}, p0, [x26]
st1w {z19.s}, p0, [x22]
st1w {z22.s}, p0, [x26, #1, MUL VL]
st1w {z24.s}, p0, [x22, #1, MUL VL]
st1w {z17.s}, p0, [x23]
st1w {z23.s}, p0, [x20]
st1w {z26.s}, p0, [x23, #1, MUL VL]
st1w {z28.s}, p0, [x20, #1, MUL VL]
mova za0v.s[w12,3],p0/m,z17.s
mova za1v.s[w12,3],p0/m,z23.s
mova za2v.s[w12,3],p0/m,z26.s
mova za3v.s[w12,3],p0/m,z28.s
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
cbnz x11,.ukr5_slices
sub x0,x0,x8
sub x3,x3,x8
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
ld1rw {z0.s}, p0/z, [x5]
add x19,x0,x8
ld1rw {z1.s}, p0/z, [x4]
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
add x10,x10,#-4
ld1w {z2.s}, p0/z, [x0]
fmul z2.s,z2.s,z0.s
mova z3.s,p0/m,za0v.s[w12,0]
fmla z2.s,p0/m,z3.s,z1.s
st1w {z2.s}, p0, [x3]
ld1w {z4.s}, p0/z, [x11]
ld1w {z5.s}, p0/z, [x0, #1, MUL VL]
ld1w {z6.s}, p0/z, [x11, #1, MUL VL]
ld1w {z7.s}, p0/z, [x16]
ld1w {z16.s}, p0/z, [x1]
ld1w {z17.s}, p0/z, [x16, #1, MUL VL]
ld1w {z18.s}, p0/z, [x1, #1, MUL VL]
ld1w {z19.s}, p0/z, [x17]
ld1w {z20.s}, p0/z, [x2]
ld1w {z21.s}, p0/z, [x17, #1, MUL VL]
ld1w {z22.s}, p0/z, [x2, #1, MUL VL]
ld1w {z23.s}, p0/z, [x9]
ld1w {z24.s}, p0/z, [x19]
ld1w {z25.s}, p0/z, [x9, #1, MUL VL]
ld1w {z2.s}, p0/z, [x19, #1, MUL VL]
fmul z4.s,z4.s,z0.s
mova z26.s,p0/m,za1v.s[w12,0]
fmul z5.s,z5.s,z0.s
mova z27.s,p0/m,za2v.s[w12,0]
fmul z6.s,z6.s,z0.s
mova z28.s,p0/m,za3v.s[w12,0]
fmul z7.s,z7.s,z0.s
mova z29.s,p0/m,za0v.s[w12,1]
fmul z16.s,z16.s,z0.s
mova z30.s,p0/m,za1v.s[w12,1]
fmul z17.s,z17.s,z0.s
mova z31.s,p0/m,za2v.s[w12,1]
fmul z18.s,z18.s,z0.s
mova z8.s,p0/m,za3v.s[w12,1]
fmul z19.s,z19.s,z0.s
mova z9.s,p0/m,za0v.s[w12,2]
fmul z20.s,z20.s,z0.s
mova z10.s,p0/m,za1v.s[w12,2]
fmul z21.s,z21.s,z0.s
mova z11.s,p0/m,za2v.s[w12,2]
fmul z22.s,z22.s,z0.s
mova z12.s,p0/m,za3v.s[w12,2]
fmul z23.s,z23.s,z0.s
mova z13.s,p0/m,za0v.s[w12,3]
fmul z24.s,z24.s,z0.s
mova z14.s,p0/m,za1v.s[w12,3]
mova z3.s,p0/m,za3v.s[w12,3]
fmla z4.s,p0/m,z26.s,z1.s
fmul z25.s,z25.s,z0.s
mova z26.s,p0/m,za2v.s[w12,3]
fmul z2.s,z2.s,z0.s
fmla z5.s,p0/m,z27.s,z1.s
fmla z6.s,p0/m,z28.s,z1.s
fmla z7.s,p0/m,z29.s,z1.s
fmla z16.s,p0/m,z30.s,z1.s
fmla z17.s,p0/m,z31.s,z1.s
fmla z18.s,p0/m,z8.s,z1.s
fmla z19.s,p0/m,z9.s,z1.s
fmla z20.s,p0/m,z10.s,z1.s
fmla z21.s,p0/m,z11.s,z1.s
fmla z22.s,p0/m,z12.s,z1.s
fmla z23.s,p0/m,z13.s,z1.s
fmla z24.s,p0/m,z14.s,z1.s
fmla z25.s,p0/m,z26.s,z1.s
fmla z2.s,p0/m,z3.s,z1.s
st1w {z4.s}, p0, [x24]
st1w {z5.s}, p0, [x3, #1, MUL VL]
st1w {z6.s}, p0, [x24, #1, MUL VL]
st1w {z7.s}, p0, [x25]
st1w {z16.s}, p0, [x21]
st1w {z17.s}, p0, [x25, #1, MUL VL]
st1w {z18.s}, p0, [x21, #1, MUL VL]
st1w {z19.s}, p0, [x26]
st1w {z20.s}, p0, [x22]
st1w {z21.s}, p0, [x26, #1, MUL VL]
st1w {z22.s}, p0, [x22, #1, MUL VL]
st1w {z23.s}, p0, [x23]
st1w {z24.s}, p0, [x20]
st1w {z25.s}, p0, [x23, #1, MUL VL]
st1w {z2.s}, p0, [x20, #1, MUL VL]
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
cbnz x10,.ukr6_slices
sub x0,x0,x8
sub x3,x3,x8
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
.size bli_sgemm_ukrgen_sme_opa_2vx2v_asm, .-bli_sgemm_ukrgen_sme_opa_2vx2v_asm
.section .note.GNU-stack,"",%progbits
