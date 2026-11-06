.text
.global bli_dgemm_ukrgen_sme_opa_2vx4v_asm
.type bli_dgemm_ukrgen_sme_opa_2vx4v_asm, %function
bli_dgemm_ukrgen_sme_opa_2vx4v_asm:
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
ptrue p0.d
cntd x7
mul x8,x7,x6
and x9,x0,#3
lsr x0,x0,#2
zero {za0.d}
zero {za1.d}
zero {za2.d}
zero {za3.d}
zero {za4.d}
zero {za5.d}
zero {za6.d}
zero {za7.d}
cbz x0,.ukr7_done
ld1d {z0.d}, p0/z, [x1]
ld1d {z1.d}, p0/z, [x1, #1, MUL VL]
ld1d {z2.d}, p0/z, [x2]
ld1d {z3.d}, p0/z, [x2, #1, MUL VL]
ld1d {z4.d}, p0/z, [x2, #2, MUL VL]
ld1d {z5.d}, p0/z, [x2, #3, MUL VL]
incb x1, ALL, MUL #2
incb x2, ALL, MUL #4
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
fmopa za0.d,p0/m,p0/m,z0.d,z2.d
fmopa za1.d,p0/m,p0/m,z0.d,z3.d
fmopa za2.d,p0/m,p0/m,z0.d,z4.d
fmopa za3.d,p0/m,p0/m,z0.d,z5.d
fmopa za4.d,p0/m,p0/m,z1.d,z2.d
fmopa za5.d,p0/m,p0/m,z1.d,z3.d
fmopa za6.d,p0/m,p0/m,z1.d,z4.d
fmopa za7.d,p0/m,p0/m,z1.d,z5.d
ld1d {z6.d}, p0/z, [x1]
ld1d {z7.d}, p0/z, [x2]
ld1d {z16.d}, p0/z, [x2, #1, MUL VL]
ld1d {z17.d}, p0/z, [x2, #2, MUL VL]
ld1d {z18.d}, p0/z, [x2, #3, MUL VL]
ld1d {z19.d}, p0/z, [x1, #1, MUL VL]
mov x10,x2
fmopa za0.d,p0/m,p0/m,z6.d,z7.d
fmopa za1.d,p0/m,p0/m,z6.d,z16.d
fmopa za2.d,p0/m,p0/m,z6.d,z17.d
fmopa za3.d,p0/m,p0/m,z6.d,z18.d
fmopa za4.d,p0/m,p0/m,z19.d,z7.d
fmopa za5.d,p0/m,p0/m,z19.d,z16.d
fmopa za6.d,p0/m,p0/m,z19.d,z17.d
fmopa za7.d,p0/m,p0/m,z19.d,z18.d
ld1d {z20.d}, p0/z, [x1, #2, MUL VL]
ld1d {z21.d}, p0/z, [x2, #4, MUL VL]
ld1d {z22.d}, p0/z, [x2, #5, MUL VL]
ld1d {z23.d}, p0/z, [x2, #6, MUL VL]
ld1d {z24.d}, p0/z, [x2, #7, MUL VL]
ld1d {z25.d}, p0/z, [x1, #3, MUL VL]
incb x10, ALL, MUL #8
fmopa za0.d,p0/m,p0/m,z20.d,z21.d
fmopa za1.d,p0/m,p0/m,z20.d,z22.d
fmopa za2.d,p0/m,p0/m,z20.d,z23.d
fmopa za3.d,p0/m,p0/m,z20.d,z24.d
fmopa za4.d,p0/m,p0/m,z25.d,z21.d
fmopa za5.d,p0/m,p0/m,z25.d,z22.d
fmopa za6.d,p0/m,p0/m,z25.d,z23.d
fmopa za7.d,p0/m,p0/m,z25.d,z24.d
ld1d {z26.d}, p0/z, [x1, #4, MUL VL]
ld1d {z27.d}, p0/z, [x10]
ld1d {z28.d}, p0/z, [x10, #1, MUL VL]
ld1d {z29.d}, p0/z, [x10, #2, MUL VL]
ld1d {z30.d}, p0/z, [x10, #3, MUL VL]
ld1d {z31.d}, p0/z, [x1, #5, MUL VL]
ld1d {z0.d}, p0/z, [x1, #6, MUL VL]
ld1d {z1.d}, p0/z, [x1, #7, MUL VL]
fmopa za0.d,p0/m,p0/m,z26.d,z27.d
fmopa za1.d,p0/m,p0/m,z26.d,z28.d
fmopa za2.d,p0/m,p0/m,z26.d,z29.d
fmopa za3.d,p0/m,p0/m,z26.d,z30.d
fmopa za4.d,p0/m,p0/m,z31.d,z27.d
fmopa za5.d,p0/m,p0/m,z31.d,z28.d
fmopa za6.d,p0/m,p0/m,z31.d,z29.d
fmopa za7.d,p0/m,p0/m,z31.d,z30.d
ld1d {z2.d}, p0/z, [x10, #4, MUL VL]
ld1d {z3.d}, p0/z, [x10, #5, MUL VL]
ld1d {z4.d}, p0/z, [x10, #6, MUL VL]
ld1d {z5.d}, p0/z, [x10, #7, MUL VL]
incb x1, ALL, MUL #8
incb x2, ALL, MUL #16
cbnz x0,.ukr7_loop
.ukr7_last:
fmopa za0.d,p0/m,p0/m,z0.d,z2.d
fmopa za1.d,p0/m,p0/m,z0.d,z3.d
fmopa za2.d,p0/m,p0/m,z0.d,z4.d
fmopa za3.d,p0/m,p0/m,z0.d,z5.d
fmopa za4.d,p0/m,p0/m,z1.d,z2.d
fmopa za5.d,p0/m,p0/m,z1.d,z3.d
fmopa za6.d,p0/m,p0/m,z1.d,z4.d
fmopa za7.d,p0/m,p0/m,z1.d,z5.d
ld1d {z6.d}, p0/z, [x1]
ld1d {z7.d}, p0/z, [x2]
ld1d {z16.d}, p0/z, [x2, #1, MUL VL]
ld1d {z17.d}, p0/z, [x2, #2, MUL VL]
ld1d {z18.d}, p0/z, [x2, #3, MUL VL]
ld1d {z19.d}, p0/z, [x1, #1, MUL VL]
mov x10,x2
fmopa za0.d,p0/m,p0/m,z6.d,z7.d
fmopa za1.d,p0/m,p0/m,z6.d,z16.d
fmopa za2.d,p0/m,p0/m,z6.d,z17.d
fmopa za3.d,p0/m,p0/m,z6.d,z18.d
fmopa za4.d,p0/m,p0/m,z19.d,z7.d
fmopa za5.d,p0/m,p0/m,z19.d,z16.d
fmopa za6.d,p0/m,p0/m,z19.d,z17.d
fmopa za7.d,p0/m,p0/m,z19.d,z18.d
ld1d {z20.d}, p0/z, [x1, #2, MUL VL]
ld1d {z21.d}, p0/z, [x2, #4, MUL VL]
ld1d {z22.d}, p0/z, [x2, #5, MUL VL]
ld1d {z23.d}, p0/z, [x2, #6, MUL VL]
ld1d {z24.d}, p0/z, [x2, #7, MUL VL]
ld1d {z25.d}, p0/z, [x1, #3, MUL VL]
incb x10, ALL, MUL #8
fmopa za0.d,p0/m,p0/m,z20.d,z21.d
fmopa za1.d,p0/m,p0/m,z20.d,z22.d
fmopa za2.d,p0/m,p0/m,z20.d,z23.d
fmopa za3.d,p0/m,p0/m,z20.d,z24.d
fmopa za4.d,p0/m,p0/m,z25.d,z21.d
fmopa za5.d,p0/m,p0/m,z25.d,z22.d
fmopa za6.d,p0/m,p0/m,z25.d,z23.d
fmopa za7.d,p0/m,p0/m,z25.d,z24.d
ld1d {z26.d}, p0/z, [x1, #4, MUL VL]
ld1d {z27.d}, p0/z, [x10]
ld1d {z28.d}, p0/z, [x10, #1, MUL VL]
ld1d {z29.d}, p0/z, [x10, #2, MUL VL]
ld1d {z30.d}, p0/z, [x10, #3, MUL VL]
ld1d {z31.d}, p0/z, [x1, #5, MUL VL]
fmopa za0.d,p0/m,p0/m,z26.d,z27.d
fmopa za1.d,p0/m,p0/m,z26.d,z28.d
fmopa za2.d,p0/m,p0/m,z26.d,z29.d
fmopa za3.d,p0/m,p0/m,z26.d,z30.d
fmopa za4.d,p0/m,p0/m,z31.d,z27.d
fmopa za5.d,p0/m,p0/m,z31.d,z28.d
fmopa za6.d,p0/m,p0/m,z31.d,z29.d
fmopa za7.d,p0/m,p0/m,z31.d,z30.d
incb x1, ALL, MUL #6
incb x2, ALL, MUL #12
.ukr7_done:
cbz x9,.ukr7_taildone
.ukr7_tail:
add x9,x9,#-1
ld1d {z0.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x2]
ld1d {z3.d}, p0/z, [x2, #1, MUL VL]
ld1d {z4.d}, p0/z, [x2, #2, MUL VL]
ld1d {z5.d}, p0/z, [x2, #3, MUL VL]
ld1d {z1.d}, p0/z, [x1, #1, MUL VL]
fmopa za0.d,p0/m,p0/m,z0.d,z2.d
fmopa za1.d,p0/m,p0/m,z0.d,z3.d
fmopa za2.d,p0/m,p0/m,z0.d,z4.d
fmopa za3.d,p0/m,p0/m,z0.d,z5.d
fmopa za4.d,p0/m,p0/m,z1.d,z2.d
fmopa za5.d,p0/m,p0/m,z1.d,z3.d
fmopa za6.d,p0/m,p0/m,z1.d,z4.d
fmopa za7.d,p0/m,p0/m,z1.d,z5.d
incb x1, ALL, MUL #2
incb x2, ALL, MUL #4
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
mov x1,x0
mov x2,x0
mov x9,x0
mov x10,x0
incb x1, ALL, MUL #1
mov x11,x0
mov x16,x0
incb x2, ALL, MUL #1
add x17,x0,x8
mov x19,x0
incb x9, ALL, MUL #1
incb x10, ALL, MUL #1
add x1,x1,x8
add x20,x0,x8
mov x21,x0
incb x11, ALL, MUL #1
incb x16, ALL, MUL #1
add x2,x2,x8
add x22,x0,x8
add x23,x0,x8, LSL #1
add x17,x17,x8, LSL #1
incb x19, ALL, MUL #1
add x9,x9,x8
add x10,x10,x8, LSL #1
add x1,x1,x8, LSL #1
mov x24,x7
mov x12,#0
add x25,x0,x8
add x26,x0,x8, LSL #1
add x20,x20,x8, LSL #1
incb x21, ALL, MUL #1
add x11,x11,x8
add x16,x16,x8, LSL #1
add x2,x2,x8, LSL #1
add x27,x0,x6
add x22,x22,x6
add x23,x23,x6
add x17,x17,x6
add x19,x19,x6
add x9,x9,x6
add x10,x10,x6
add x1,x1,x6
.ukr1_slices:
add x24,x24,#-2
st1d {za0v.d[w12, 0]}, p0, [x0]
st1d {za1v.d[w12, 0]}, p0, [x25]
st1d {za2v.d[w12, 0]}, p0, [x26]
st1d {za3v.d[w12, 0]}, p0, [x20]
st1d {za4v.d[w12, 0]}, p0, [x21]
st1d {za5v.d[w12, 0]}, p0, [x11]
st1d {za6v.d[w12, 0]}, p0, [x16]
st1d {za7v.d[w12, 0]}, p0, [x2]
st1d {za0v.d[w12, 1]}, p0, [x27]
st1d {za1v.d[w12, 1]}, p0, [x22]
st1d {za2v.d[w12, 1]}, p0, [x23]
st1d {za3v.d[w12, 1]}, p0, [x17]
st1d {za4v.d[w12, 1]}, p0, [x19]
st1d {za5v.d[w12, 1]}, p0, [x9]
st1d {za6v.d[w12, 1]}, p0, [x10]
st1d {za7v.d[w12, 1]}, p0, [x1]
add x0,x0,x6, LSL #1
add x25,x25,x6, LSL #1
add x26,x26,x6, LSL #1
add x20,x20,x6, LSL #1
add x21,x21,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x2,x2,x6, LSL #1
add x27,x27,x6, LSL #1
add x22,x22,x6, LSL #1
add x23,x23,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x9,x9,x6, LSL #1
add x10,x10,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x24,.ukr1_slices
sub x0,x0,x8
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
add x1,x0,x8
add x2,x0,x8
add x9,x0,x8
add x10,x0,x8, LSL #1
mov x11,x7
mov x12,#0
add x16,x0,x8
add x17,x0,x8, LSL #1
add x2,x2,x8, LSL #1
add x19,x0,x6
add x9,x9,x6
add x10,x10,x6
ld1rd {z0.d}, p0/z, [x4]
add x1,x1,x8, LSL #1
add x1,x1,x6
.ukr2_slices:
add x11,x11,#-2
mova z1.d,p0/m,za0v.d[w12,0]
fmul z2.d,z1.d,z0.d
st1d {z2.d}, p0, [x0]
mova z3.d,p0/m,za1v.d[w12,0]
mova z4.d,p0/m,za2v.d[w12,0]
mova z5.d,p0/m,za3v.d[w12,0]
mova z6.d,p0/m,za4v.d[w12,0]
mova z7.d,p0/m,za5v.d[w12,0]
mova z16.d,p0/m,za6v.d[w12,0]
mova z17.d,p0/m,za7v.d[w12,0]
mova z18.d,p0/m,za0v.d[w12,1]
mova z19.d,p0/m,za1v.d[w12,1]
mova z20.d,p0/m,za2v.d[w12,1]
mova z21.d,p0/m,za3v.d[w12,1]
mova z22.d,p0/m,za4v.d[w12,1]
mova z23.d,p0/m,za5v.d[w12,1]
mova z24.d,p0/m,za6v.d[w12,1]
mova z25.d,p0/m,za7v.d[w12,1]
fmul z26.d,z3.d,z0.d
fmul z27.d,z4.d,z0.d
fmul z28.d,z5.d,z0.d
fmul z29.d,z6.d,z0.d
fmul z30.d,z7.d,z0.d
fmul z31.d,z16.d,z0.d
fmul z8.d,z17.d,z0.d
fmul z9.d,z18.d,z0.d
fmul z10.d,z19.d,z0.d
fmul z11.d,z20.d,z0.d
fmul z12.d,z21.d,z0.d
fmul z13.d,z22.d,z0.d
fmul z14.d,z23.d,z0.d
fmul z15.d,z24.d,z0.d
fmul z2.d,z25.d,z0.d
st1d {z26.d}, p0, [x16]
st1d {z27.d}, p0, [x17]
st1d {z28.d}, p0, [x2]
st1d {z29.d}, p0, [x0, #1, MUL VL]
st1d {z30.d}, p0, [x16, #1, MUL VL]
st1d {z31.d}, p0, [x17, #1, MUL VL]
st1d {z8.d}, p0, [x2, #1, MUL VL]
st1d {z9.d}, p0, [x19]
st1d {z10.d}, p0, [x9]
st1d {z11.d}, p0, [x10]
st1d {z12.d}, p0, [x1]
st1d {z13.d}, p0, [x19, #1, MUL VL]
st1d {z14.d}, p0, [x9, #1, MUL VL]
st1d {z15.d}, p0, [x10, #1, MUL VL]
st1d {z2.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #1
add x16,x16,x6, LSL #1
add x17,x17,x6, LSL #1
add x2,x2,x6, LSL #1
add x19,x19,x6, LSL #1
add x9,x9,x6, LSL #1
add x10,x10,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x11,.ukr2_slices
sub x0,x0,x8
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
add x9,x0,x8
add x10,x0,x8
add x11,x0,x8, LSL #1
add x1,x1,x8, LSL #1
add x16,x3,x8
add x17,x3,x8
add x19,x3,x8, LSL #1
add x2,x2,x8, LSL #1
mov x20,x7
mov x12,#0
add x21,x0,x8
add x22,x0,x8, LSL #1
add x9,x9,x8, LSL #1
add x23,x0,x6
add x10,x10,x6
add x11,x11,x6
add x1,x1,x6
add x24,x3,x8
add x25,x3,x8, LSL #1
add x16,x16,x8, LSL #1
add x26,x3,x6
add x17,x17,x6
add x19,x19,x6
add x2,x2,x6
.ukr3_slices:
add x20,x20,#-2
mova z0.d,p0/m,za0v.d[w12,0]
ld1d {z1.d}, p0/z, [x0]
mova z2.d,p0/m,za1v.d[w12,0]
ld1d {z3.d}, p0/z, [x21]
mova z4.d,p0/m,za2v.d[w12,0]
ld1d {z5.d}, p0/z, [x22]
mova z6.d,p0/m,za3v.d[w12,0]
ld1d {z7.d}, p0/z, [x9]
mova z16.d,p0/m,za4v.d[w12,0]
ld1d {z17.d}, p0/z, [x0, #1, MUL VL]
mova z18.d,p0/m,za5v.d[w12,0]
ld1d {z19.d}, p0/z, [x21, #1, MUL VL]
mova z20.d,p0/m,za6v.d[w12,0]
ld1d {z21.d}, p0/z, [x22, #1, MUL VL]
mova z22.d,p0/m,za7v.d[w12,0]
ld1d {z23.d}, p0/z, [x9, #1, MUL VL]
mova z24.d,p0/m,za0v.d[w12,1]
ld1d {z25.d}, p0/z, [x23]
mova z26.d,p0/m,za1v.d[w12,1]
ld1d {z27.d}, p0/z, [x10]
mova z28.d,p0/m,za2v.d[w12,1]
ld1d {z29.d}, p0/z, [x11]
mova z30.d,p0/m,za3v.d[w12,1]
ld1d {z31.d}, p0/z, [x1]
mova z8.d,p0/m,za4v.d[w12,1]
ld1d {z9.d}, p0/z, [x23, #1, MUL VL]
mova z10.d,p0/m,za5v.d[w12,1]
ld1d {z11.d}, p0/z, [x10, #1, MUL VL]
mova z12.d,p0/m,za6v.d[w12,1]
ld1d {z13.d}, p0/z, [x11, #1, MUL VL]
mova z14.d,p0/m,za7v.d[w12,1]
fadd z1.d,z0.d,z1.d
ld1d {z15.d}, p0/z, [x1, #1, MUL VL]
fadd z3.d,z2.d,z3.d
fadd z5.d,z4.d,z5.d
fadd z7.d,z6.d,z7.d
fadd z17.d,z16.d,z17.d
fadd z19.d,z18.d,z19.d
fadd z21.d,z20.d,z21.d
fadd z23.d,z22.d,z23.d
fadd z25.d,z24.d,z25.d
fadd z27.d,z26.d,z27.d
fadd z29.d,z28.d,z29.d
fadd z31.d,z30.d,z31.d
fadd z9.d,z8.d,z9.d
fadd z11.d,z10.d,z11.d
fadd z13.d,z12.d,z13.d
fadd z15.d,z14.d,z15.d
st1d {z1.d}, p0, [x3]
st1d {z3.d}, p0, [x24]
st1d {z5.d}, p0, [x25]
st1d {z7.d}, p0, [x16]
st1d {z17.d}, p0, [x3, #1, MUL VL]
st1d {z19.d}, p0, [x24, #1, MUL VL]
st1d {z21.d}, p0, [x25, #1, MUL VL]
st1d {z23.d}, p0, [x16, #1, MUL VL]
st1d {z25.d}, p0, [x26]
st1d {z27.d}, p0, [x17]
st1d {z29.d}, p0, [x19]
st1d {z31.d}, p0, [x2]
st1d {z9.d}, p0, [x26, #1, MUL VL]
st1d {z11.d}, p0, [x17, #1, MUL VL]
st1d {z13.d}, p0, [x19, #1, MUL VL]
st1d {z15.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x21,x21,x6, LSL #1
add x22,x22,x6, LSL #1
add x9,x9,x6, LSL #1
add x23,x23,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x24,x24,x6, LSL #1
add x25,x25,x6, LSL #1
add x16,x16,x6, LSL #1
add x26,x26,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x20,.ukr3_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
add x1,x0,x8
add x2,x0,x8
add x9,x0,x8
add x10,x0,x8, LSL #1
mov x11,x7
mov x12,#0
add x16,x0,x8
add x17,x0,x8, LSL #1
add x2,x2,x8, LSL #1
add x19,x0,x6
add x9,x9,x6
add x10,x10,x6
ld1rd {z0.d}, p0/z, [x4]
add x20,x3,x8
add x1,x1,x8, LSL #1
add x21,x3,x8
add x22,x3,x8
add x23,x3,x8, LSL #1
add x20,x20,x8, LSL #1
add x1,x1,x6
add x24,x3,x8
add x25,x3,x8, LSL #1
add x21,x21,x8, LSL #1
add x26,x3,x6
add x22,x22,x6
add x23,x23,x6
add x20,x20,x6
.ukr4_slices:
add x11,x11,#-2
mova z1.d,p0/m,za0v.d[w12,0]
ld1d {z2.d}, p0/z, [x0]
fmla z2.d,p0/m,z1.d,z0.d
st1d {z2.d}, p0, [x3]
mova z3.d,p0/m,za1v.d[w12,0]
ld1d {z4.d}, p0/z, [x16]
mova z5.d,p0/m,za2v.d[w12,0]
ld1d {z6.d}, p0/z, [x17]
mova z7.d,p0/m,za3v.d[w12,0]
ld1d {z16.d}, p0/z, [x2]
mova z17.d,p0/m,za4v.d[w12,0]
ld1d {z18.d}, p0/z, [x0, #1, MUL VL]
mova z19.d,p0/m,za5v.d[w12,0]
ld1d {z20.d}, p0/z, [x16, #1, MUL VL]
mova z21.d,p0/m,za6v.d[w12,0]
ld1d {z22.d}, p0/z, [x17, #1, MUL VL]
mova z23.d,p0/m,za7v.d[w12,0]
ld1d {z24.d}, p0/z, [x2, #1, MUL VL]
mova z25.d,p0/m,za0v.d[w12,1]
ld1d {z26.d}, p0/z, [x19]
mova z27.d,p0/m,za1v.d[w12,1]
ld1d {z28.d}, p0/z, [x9]
mova z29.d,p0/m,za2v.d[w12,1]
ld1d {z30.d}, p0/z, [x10]
mova z31.d,p0/m,za3v.d[w12,1]
ld1d {z8.d}, p0/z, [x1]
mova z9.d,p0/m,za4v.d[w12,1]
ld1d {z10.d}, p0/z, [x19, #1, MUL VL]
mova z11.d,p0/m,za5v.d[w12,1]
ld1d {z12.d}, p0/z, [x9, #1, MUL VL]
mova z13.d,p0/m,za6v.d[w12,1]
ld1d {z14.d}, p0/z, [x10, #1, MUL VL]
mova z15.d,p0/m,za7v.d[w12,1]
fmla z4.d,p0/m,z3.d,z0.d
ld1d {z2.d}, p0/z, [x1, #1, MUL VL]
fmla z6.d,p0/m,z5.d,z0.d
fmla z16.d,p0/m,z7.d,z0.d
fmla z18.d,p0/m,z17.d,z0.d
fmla z20.d,p0/m,z19.d,z0.d
fmla z22.d,p0/m,z21.d,z0.d
fmla z24.d,p0/m,z23.d,z0.d
fmla z26.d,p0/m,z25.d,z0.d
fmla z28.d,p0/m,z27.d,z0.d
fmla z30.d,p0/m,z29.d,z0.d
fmla z8.d,p0/m,z31.d,z0.d
fmla z10.d,p0/m,z9.d,z0.d
fmla z12.d,p0/m,z11.d,z0.d
fmla z14.d,p0/m,z13.d,z0.d
fmla z2.d,p0/m,z15.d,z0.d
st1d {z4.d}, p0, [x24]
st1d {z6.d}, p0, [x25]
st1d {z16.d}, p0, [x21]
st1d {z18.d}, p0, [x3, #1, MUL VL]
st1d {z20.d}, p0, [x24, #1, MUL VL]
st1d {z22.d}, p0, [x25, #1, MUL VL]
st1d {z24.d}, p0, [x21, #1, MUL VL]
st1d {z26.d}, p0, [x26]
st1d {z28.d}, p0, [x22]
st1d {z30.d}, p0, [x23]
st1d {z8.d}, p0, [x20]
st1d {z10.d}, p0, [x26, #1, MUL VL]
st1d {z12.d}, p0, [x22, #1, MUL VL]
st1d {z14.d}, p0, [x23, #1, MUL VL]
st1d {z2.d}, p0, [x20, #1, MUL VL]
add x0,x0,x6, LSL #1
add x16,x16,x6, LSL #1
add x17,x17,x6, LSL #1
add x2,x2,x6, LSL #1
add x19,x19,x6, LSL #1
add x9,x9,x6, LSL #1
add x10,x10,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x24,x24,x6, LSL #1
add x25,x25,x6, LSL #1
add x21,x21,x6, LSL #1
add x26,x26,x6, LSL #1
add x22,x22,x6, LSL #1
add x23,x23,x6, LSL #1
add x20,x20,x6, LSL #1
add x12,x12,#2
cbnz x11,.ukr4_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
add x1,x0,x8
add x2,x0,x8
add x9,x0,x8
add x10,x0,x8, LSL #1
mov x11,x7
mov x12,#0
add x16,x0,x8
add x17,x0,x8, LSL #1
add x2,x2,x8, LSL #1
add x19,x0,x6
add x9,x9,x6
add x10,x10,x6
ld1rd {z0.d}, p0/z, [x5]
add x20,x3,x8
add x1,x1,x8, LSL #1
add x21,x3,x8
add x22,x3,x8
add x23,x3,x8, LSL #1
add x20,x20,x8, LSL #1
add x1,x1,x6
add x24,x3,x8
add x25,x3,x8, LSL #1
add x21,x21,x8, LSL #1
add x26,x3,x6
add x22,x22,x6
add x23,x23,x6
add x20,x20,x6
.ukr5_slices:
add x11,x11,#-2
mova z1.d,p0/m,za0v.d[w12,0]
ld1d {z2.d}, p0/z, [x0]
mova z3.d,p0/m,za1v.d[w12,0]
ld1d {z4.d}, p0/z, [x16]
mova z5.d,p0/m,za2v.d[w12,0]
ld1d {z6.d}, p0/z, [x17]
mova z7.d,p0/m,za3v.d[w12,0]
ld1d {z16.d}, p0/z, [x2]
mova z17.d,p0/m,za4v.d[w12,0]
ld1d {z18.d}, p0/z, [x0, #1, MUL VL]
mova z19.d,p0/m,za5v.d[w12,0]
ld1d {z20.d}, p0/z, [x16, #1, MUL VL]
mova z21.d,p0/m,za6v.d[w12,0]
ld1d {z22.d}, p0/z, [x17, #1, MUL VL]
mova z23.d,p0/m,za7v.d[w12,0]
ld1d {z24.d}, p0/z, [x2, #1, MUL VL]
fmla z1.d,p0/m,z2.d,z0.d
fmla z3.d,p0/m,z4.d,z0.d
fmla z5.d,p0/m,z6.d,z0.d
fmla z7.d,p0/m,z16.d,z0.d
fmla z17.d,p0/m,z18.d,z0.d
fmla z19.d,p0/m,z20.d,z0.d
fmla z21.d,p0/m,z22.d,z0.d
fmla z23.d,p0/m,z24.d,z0.d
mova za0v.d[w12,0],p0/m,z1.d
mova za1v.d[w12,0],p0/m,z3.d
mova za2v.d[w12,0],p0/m,z5.d
mova za3v.d[w12,0],p0/m,z7.d
mova za4v.d[w12,0],p0/m,z17.d
mova za5v.d[w12,0],p0/m,z19.d
mova za6v.d[w12,0],p0/m,z21.d
mova za7v.d[w12,0],p0/m,z23.d
mova z25.d,p0/m,za0v.d[w12,1]
ld1d {z26.d}, p0/z, [x19]
mova z27.d,p0/m,za1v.d[w12,1]
ld1d {z28.d}, p0/z, [x9]
mova z29.d,p0/m,za2v.d[w12,1]
ld1d {z30.d}, p0/z, [x10]
mova z31.d,p0/m,za3v.d[w12,1]
ld1d {z8.d}, p0/z, [x1]
mova z9.d,p0/m,za4v.d[w12,1]
ld1d {z10.d}, p0/z, [x19, #1, MUL VL]
mova z11.d,p0/m,za5v.d[w12,1]
ld1d {z12.d}, p0/z, [x9, #1, MUL VL]
mova z13.d,p0/m,za6v.d[w12,1]
ld1d {z14.d}, p0/z, [x10, #1, MUL VL]
mova z15.d,p0/m,za7v.d[w12,1]
ld1d {z2.d}, p0/z, [x1, #1, MUL VL]
fmla z25.d,p0/m,z26.d,z0.d
fmla z27.d,p0/m,z28.d,z0.d
fmla z29.d,p0/m,z30.d,z0.d
fmla z31.d,p0/m,z8.d,z0.d
fmla z9.d,p0/m,z10.d,z0.d
fmla z11.d,p0/m,z12.d,z0.d
fmla z13.d,p0/m,z14.d,z0.d
fmla z15.d,p0/m,z2.d,z0.d
st1d {z1.d}, p0, [x3]
st1d {z3.d}, p0, [x24]
st1d {z5.d}, p0, [x25]
st1d {z7.d}, p0, [x21]
st1d {z17.d}, p0, [x3, #1, MUL VL]
st1d {z19.d}, p0, [x24, #1, MUL VL]
st1d {z21.d}, p0, [x25, #1, MUL VL]
st1d {z23.d}, p0, [x21, #1, MUL VL]
st1d {z25.d}, p0, [x26]
st1d {z27.d}, p0, [x22]
st1d {z29.d}, p0, [x23]
st1d {z31.d}, p0, [x20]
st1d {z9.d}, p0, [x26, #1, MUL VL]
st1d {z11.d}, p0, [x22, #1, MUL VL]
st1d {z13.d}, p0, [x23, #1, MUL VL]
st1d {z15.d}, p0, [x20, #1, MUL VL]
mova za0v.d[w12,1],p0/m,z25.d
mova za1v.d[w12,1],p0/m,z27.d
mova za2v.d[w12,1],p0/m,z29.d
mova za3v.d[w12,1],p0/m,z31.d
mova za4v.d[w12,1],p0/m,z9.d
mova za5v.d[w12,1],p0/m,z11.d
mova za6v.d[w12,1],p0/m,z13.d
mova za7v.d[w12,1],p0/m,z15.d
add x0,x0,x6, LSL #1
add x16,x16,x6, LSL #1
add x17,x17,x6, LSL #1
add x2,x2,x6, LSL #1
add x19,x19,x6, LSL #1
add x9,x9,x6, LSL #1
add x10,x10,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x24,x24,x6, LSL #1
add x25,x25,x6, LSL #1
add x21,x21,x6, LSL #1
add x26,x26,x6, LSL #1
add x22,x22,x6, LSL #1
add x23,x23,x6, LSL #1
add x20,x20,x6, LSL #1
add x12,x12,#2
cbnz x11,.ukr5_slices
sub x0,x0,x8
sub x3,x3,x8
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
add x1,x0,x8
add x2,x0,x8
add x9,x0,x8, LSL #1
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x8, LSL #1
add x1,x1,x8, LSL #1
add x17,x0,x6
add x2,x2,x6
add x9,x9,x6
ld1rd {z0.d}, p0/z, [x5]
add x19,x0,x8
ld1rd {z1.d}, p0/z, [x4]
add x20,x3,x8
add x19,x19,x8, LSL #1
add x21,x3,x8
add x22,x3,x8
add x23,x3,x8, LSL #1
add x20,x20,x8, LSL #1
add x19,x19,x6
add x24,x3,x8
add x25,x3,x8, LSL #1
add x21,x21,x8, LSL #1
add x26,x3,x6
add x22,x22,x6
add x23,x23,x6
add x20,x20,x6
.ukr6_slices:
add x10,x10,#-2
ld1d {z2.d}, p0/z, [x0]
fmul z2.d,z2.d,z0.d
mova z3.d,p0/m,za0v.d[w12,0]
fmla z2.d,p0/m,z3.d,z1.d
st1d {z2.d}, p0, [x3]
ld1d {z4.d}, p0/z, [x11]
ld1d {z5.d}, p0/z, [x16]
ld1d {z6.d}, p0/z, [x1]
ld1d {z7.d}, p0/z, [x0, #1, MUL VL]
ld1d {z16.d}, p0/z, [x11, #1, MUL VL]
ld1d {z17.d}, p0/z, [x16, #1, MUL VL]
ld1d {z18.d}, p0/z, [x1, #1, MUL VL]
ld1d {z19.d}, p0/z, [x17]
ld1d {z20.d}, p0/z, [x2]
ld1d {z21.d}, p0/z, [x9]
ld1d {z22.d}, p0/z, [x19]
ld1d {z23.d}, p0/z, [x17, #1, MUL VL]
ld1d {z24.d}, p0/z, [x2, #1, MUL VL]
ld1d {z25.d}, p0/z, [x9, #1, MUL VL]
ld1d {z2.d}, p0/z, [x19, #1, MUL VL]
fmul z4.d,z4.d,z0.d
mova z26.d,p0/m,za1v.d[w12,0]
fmul z5.d,z5.d,z0.d
mova z27.d,p0/m,za2v.d[w12,0]
fmul z6.d,z6.d,z0.d
mova z28.d,p0/m,za3v.d[w12,0]
fmul z7.d,z7.d,z0.d
mova z29.d,p0/m,za4v.d[w12,0]
fmul z16.d,z16.d,z0.d
mova z30.d,p0/m,za5v.d[w12,0]
fmul z17.d,z17.d,z0.d
mova z31.d,p0/m,za6v.d[w12,0]
fmul z18.d,z18.d,z0.d
mova z8.d,p0/m,za7v.d[w12,0]
fmul z19.d,z19.d,z0.d
mova z9.d,p0/m,za0v.d[w12,1]
fmul z20.d,z20.d,z0.d
mova z10.d,p0/m,za1v.d[w12,1]
fmul z21.d,z21.d,z0.d
mova z11.d,p0/m,za2v.d[w12,1]
fmul z22.d,z22.d,z0.d
mova z12.d,p0/m,za3v.d[w12,1]
fmul z23.d,z23.d,z0.d
mova z13.d,p0/m,za4v.d[w12,1]
fmul z24.d,z24.d,z0.d
mova z14.d,p0/m,za5v.d[w12,1]
mova z3.d,p0/m,za7v.d[w12,1]
fmla z4.d,p0/m,z26.d,z1.d
fmul z25.d,z25.d,z0.d
mova z15.d,p0/m,za6v.d[w12,1]
fmul z2.d,z2.d,z0.d
fmla z5.d,p0/m,z27.d,z1.d
fmla z6.d,p0/m,z28.d,z1.d
fmla z7.d,p0/m,z29.d,z1.d
fmla z16.d,p0/m,z30.d,z1.d
fmla z17.d,p0/m,z31.d,z1.d
fmla z18.d,p0/m,z8.d,z1.d
fmla z19.d,p0/m,z9.d,z1.d
fmla z20.d,p0/m,z10.d,z1.d
fmla z21.d,p0/m,z11.d,z1.d
fmla z22.d,p0/m,z12.d,z1.d
fmla z23.d,p0/m,z13.d,z1.d
fmla z24.d,p0/m,z14.d,z1.d
fmla z25.d,p0/m,z15.d,z1.d
fmla z2.d,p0/m,z3.d,z1.d
st1d {z4.d}, p0, [x24]
st1d {z5.d}, p0, [x25]
st1d {z6.d}, p0, [x21]
st1d {z7.d}, p0, [x3, #1, MUL VL]
st1d {z16.d}, p0, [x24, #1, MUL VL]
st1d {z17.d}, p0, [x25, #1, MUL VL]
st1d {z18.d}, p0, [x21, #1, MUL VL]
st1d {z19.d}, p0, [x26]
st1d {z20.d}, p0, [x22]
st1d {z21.d}, p0, [x23]
st1d {z22.d}, p0, [x20]
st1d {z23.d}, p0, [x26, #1, MUL VL]
st1d {z24.d}, p0, [x22, #1, MUL VL]
st1d {z25.d}, p0, [x23, #1, MUL VL]
st1d {z2.d}, p0, [x20, #1, MUL VL]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x17,x17,x6, LSL #1
add x2,x2,x6, LSL #1
add x9,x9,x6, LSL #1
add x19,x19,x6, LSL #1
add x3,x3,x6, LSL #1
add x24,x24,x6, LSL #1
add x25,x25,x6, LSL #1
add x21,x21,x6, LSL #1
add x26,x26,x6, LSL #1
add x22,x22,x6, LSL #1
add x23,x23,x6, LSL #1
add x20,x20,x6, LSL #1
add x12,x12,#2
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
.size bli_dgemm_ukrgen_sme_opa_2vx4v_asm, .-bli_dgemm_ukrgen_sme_opa_2vx4v_asm
.section .note.GNU-stack,"",%progbits
