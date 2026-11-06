### bli_dgemm_ukrgen_sme_sf_1vx2v_1x2v
.text
.global bli_dgemm_ukrgen_sme_sf_1vx2v_1x2v_asm
.type bli_dgemm_ukrgen_sme_sf_1vx2v_1x2v_asm, %function
bli_dgemm_ukrgen_sme_sf_1vx2v_1x2v_asm:
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
ptrue p0.d
cntd x7
mul x8,x7,x6
and x9,x0,#3
lsr x0,x0,#2
zero {za0.d}
zero {za1.d}
dup z0.d,#0
dup z1.d,#0
cbz x0,.ukr7_done
add x10,x1,#8
ld1d {z2.d}, p0/z, [x2]
ld1d {z3.d}, p0/z, [x2, #1, MUL VL]
ld1d {z4.d}, p0/z, [x1]
ld1d {z5.d}, p0/z, [x10, #1, MUL VL]
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x10,x1,#16
ld1d {z6.d}, p0/z, [x10, #2, MUL VL]
add x10,x10,#8
ld1d {z7.d}, p0/z, [x10, #3, MUL VL]
add x10,x10,#-24
incb x10, ALL, MUL #1
ld1rd {z16.d}, p0/z, [x10]
add x10,x10,#8
incb x10, ALL, MUL #1
ld1rd {z17.d}, p0/z, [x10]
add x10,x10,#8
incb x10, ALL, MUL #1
ld1rd {z18.d}, p0/z, [x10]
add x10,x10,#8
incb x10, ALL, MUL #1
ld1rd {z19.d}, p0/z, [x10]
add x10,x10,#8
fmopa za0.d,p0/m,p0/m,z4.d,z2.d
fmopa za1.d,p0/m,p0/m,z4.d,z3.d
ld1d {z20.d}, p0/z, [x2]
ld1d {z21.d}, p0/z, [x2, #1, MUL VL]
fmla z0.d,p0/m,z2.d,z16.d
fmla z1.d,p0/m,z3.d,z16.d
decb x10, ALL, MUL #4
fmopa za0.d,p0/m,p0/m,z5.d,z20.d
fmopa za1.d,p0/m,p0/m,z5.d,z21.d
ld1d {z22.d}, p0/z, [x2, #2, MUL VL]
ld1d {z23.d}, p0/z, [x2, #3, MUL VL]
fmla z0.d,p0/m,z20.d,z17.d
fmla z1.d,p0/m,z21.d,z17.d
ld1d {z4.d}, p0/z, [x10, #4, MUL VL]
fmopa za0.d,p0/m,p0/m,z6.d,z22.d
fmopa za1.d,p0/m,p0/m,z6.d,z23.d
ld1d {z24.d}, p0/z, [x2, #4, MUL VL]
ld1d {z25.d}, p0/z, [x2, #5, MUL VL]
fmla z0.d,p0/m,z22.d,z18.d
fmla z1.d,p0/m,z23.d,z18.d
add x10,x10,#8
ld1d {z2.d}, p0/z, [x2, #6, MUL VL]
ld1d {z3.d}, p0/z, [x2, #7, MUL VL]
add x1,x1,#32
fmopa za0.d,p0/m,p0/m,z7.d,z24.d
fmopa za1.d,p0/m,p0/m,z7.d,z25.d
fmla z0.d,p0/m,z24.d,z19.d
fmla z1.d,p0/m,z25.d,z19.d
ld1d {z5.d}, p0/z, [x10, #5, MUL VL]
incb x1, ALL, MUL #4
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x10,x1,#16
ld1d {z6.d}, p0/z, [x10, #2, MUL VL]
add x10,x10,#8
ld1d {z7.d}, p0/z, [x10, #3, MUL VL]
add x10,x10,#-24
incb x10, ALL, MUL #1
ld1rd {z16.d}, p0/z, [x10]
add x10,x10,#8
incb x10, ALL, MUL #1
ld1rd {z17.d}, p0/z, [x10]
add x10,x10,#8
incb x10, ALL, MUL #1
ld1rd {z18.d}, p0/z, [x10]
fmopa za0.d,p0/m,p0/m,z4.d,z2.d
fmopa za1.d,p0/m,p0/m,z4.d,z3.d
ld1d {z20.d}, p0/z, [x2]
ld1d {z21.d}, p0/z, [x2, #1, MUL VL]
fmla z0.d,p0/m,z2.d,z16.d
fmla z1.d,p0/m,z3.d,z16.d
add x10,x10,#8
fmopa za0.d,p0/m,p0/m,z5.d,z20.d
fmopa za1.d,p0/m,p0/m,z5.d,z21.d
ld1d {z22.d}, p0/z, [x2, #2, MUL VL]
ld1d {z23.d}, p0/z, [x2, #3, MUL VL]
fmla z0.d,p0/m,z20.d,z17.d
fmla z1.d,p0/m,z21.d,z17.d
incb x10, ALL, MUL #1
fmopa za0.d,p0/m,p0/m,z6.d,z22.d
fmopa za1.d,p0/m,p0/m,z6.d,z23.d
ld1d {z24.d}, p0/z, [x2, #4, MUL VL]
ld1d {z25.d}, p0/z, [x2, #5, MUL VL]
fmla z0.d,p0/m,z22.d,z18.d
fmla z1.d,p0/m,z23.d,z18.d
ld1rd {z19.d}, p0/z, [x10]
add x1,x1,#32
fmopa za0.d,p0/m,p0/m,z7.d,z24.d
fmopa za1.d,p0/m,p0/m,z7.d,z25.d
fmla z0.d,p0/m,z24.d,z19.d
fmla z1.d,p0/m,z25.d,z19.d
incb x1, ALL, MUL #4
incb x2, ALL, MUL #6
.ukr7_done:
cbz x9,.ukr7_taildone
.ukr7_tail:
add x9,x9,#-1
mov x10,x1
incb x10, ALL, MUL #1
ld1d {z4.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x2]
ld1d {z3.d}, p0/z, [x2, #1, MUL VL]
ld1rd {z16.d}, p0/z, [x10]
fmopa za0.d,p0/m,p0/m,z4.d,z2.d
fmopa za1.d,p0/m,p0/m,z4.d,z3.d
fmla z0.d,p0/m,z2.d,z16.d
fmla z1.d,p0/m,z3.d,z16.d
add x1,x1,#8
incb x1, ALL, MUL #1
incb x2, ALL, MUL #2
cbnz x9,.ukr7_tail
.ukr7_taildone:
ldr d2, [x5]
fmov d3,xzr
fcmp d2,d3
b.ne .ukr0_try0
ldr d2, [x4]
mov x0,#4607182418800017408
fmov d3,x0
fcmp d2,d3
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr d2, [x5]
mov x0,#4607182418800017408
fmov d3,x0
fcmp d2,d3
b.ne .ukr0_try2
ldr d2, [x4]
mov x0,#4607182418800017408
fmov d3,x0
fcmp d2,d3
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr d2, [x4]
mov x0,#4607182418800017408
fmov d3,x0
fcmp d2,d3
b.ne .ukr0_try4
b .ukr0_case4
.ukr0_try4:
b .ukr0_case5
b .ukr0_cases_end
.ukr0_case0:
mov x0,x3
mov x1,x0
mov x2,x0
incb x1, ALL, MUL #1
mov x9,x7
mov x12,#0
incb x2, ALL, MUL #1
add x10,x0,x6
add x1,x1,x6
.ukr1_slices:
add x9,x9,#-2
st1d {za0h.d[w12, 0]}, p0, [x0]
st1d {za1h.d[w12, 0]}, p0, [x2]
st1d {za0h.d[w12, 1]}, p0, [x10]
st1d {za1h.d[w12, 1]}, p0, [x1]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x10,x10,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x9,.ukr1_slices
st1d {z0.d}, p0, [x0]
st1d {z1.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
ld1rd {z2.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
.ukr2_slices:
add x1,x1,#-2
mova z3.d,p0/m,za0h.d[w12,0]
mova z4.d,p0/m,za1h.d[w12,0]
mova z5.d,p0/m,za0h.d[w12,1]
mova z6.d,p0/m,za1h.d[w12,1]
fmul z7.d,z3.d,z2.d
fmul z16.d,z4.d,z2.d
fmul z17.d,z5.d,z2.d
fmul z18.d,z6.d,z2.d
st1d {z7.d}, p0, [x0]
st1d {z16.d}, p0, [x0, #1, MUL VL]
st1d {z17.d}, p0, [x2]
st1d {z18.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr2_slices
sub x0,x0,x8
fmul z3.d,z0.d,z2.d
add x0,x0,x8
fmul z0.d,z1.d,z2.d
st1d {z3.d}, p0, [x0]
st1d {z0.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
add x2,x0,x6
add x9,x3,x6
.ukr3_slices:
add x1,x1,#-2
mova z2.d,p0/m,za0h.d[w12,0]
ld1d {z3.d}, p0/z, [x0]
mova z4.d,p0/m,za1h.d[w12,0]
ld1d {z5.d}, p0/z, [x0, #1, MUL VL]
mova z6.d,p0/m,za0h.d[w12,1]
ld1d {z7.d}, p0/z, [x2]
mova z16.d,p0/m,za1h.d[w12,1]
ld1d {z17.d}, p0/z, [x2, #1, MUL VL]
fadd z3.d,z2.d,z3.d
fadd z5.d,z4.d,z5.d
fadd z7.d,z6.d,z7.d
fadd z17.d,z16.d,z17.d
st1d {z3.d}, p0, [x3]
st1d {z5.d}, p0, [x3, #1, MUL VL]
st1d {z7.d}, p0, [x9]
st1d {z17.d}, p0, [x9, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x9,x9,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr3_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1d {z2.d}, p0/z, [x0]
ld1d {z3.d}, p0/z, [x0, #1, MUL VL]
fadd z2.d,z0.d,z2.d
add x3,x3,x8
fadd z3.d,z1.d,z3.d
st1d {z2.d}, p0, [x3]
st1d {z3.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
ld1rd {z2.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x9,x3,x6
.ukr4_slices:
add x1,x1,#-2
mova z3.d,p0/m,za0h.d[w12,0]
ld1d {z4.d}, p0/z, [x0]
mova z5.d,p0/m,za1h.d[w12,0]
ld1d {z6.d}, p0/z, [x0, #1, MUL VL]
mova z7.d,p0/m,za0h.d[w12,1]
ld1d {z16.d}, p0/z, [x2]
mova z17.d,p0/m,za1h.d[w12,1]
ld1d {z18.d}, p0/z, [x2, #1, MUL VL]
fmla z4.d,p0/m,z3.d,z2.d
fmla z6.d,p0/m,z5.d,z2.d
fmla z16.d,p0/m,z7.d,z2.d
fmla z18.d,p0/m,z17.d,z2.d
st1d {z4.d}, p0, [x3]
st1d {z6.d}, p0, [x3, #1, MUL VL]
st1d {z16.d}, p0, [x9]
st1d {z18.d}, p0, [x9, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x9,x9,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr4_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1d {z3.d}, p0/z, [x0]
ld1d {z4.d}, p0/z, [x0, #1, MUL VL]
fmla z3.d,p0/m,z0.d,z2.d
add x3,x3,x8
fmla z4.d,p0/m,z1.d,z2.d
st1d {z3.d}, p0, [x3]
st1d {z4.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
ld1rd {z2.d}, p0/z, [x5]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x9,x3,x6
.ukr5_slices:
add x1,x1,#-2
mova z3.d,p0/m,za0h.d[w12,0]
ld1d {z4.d}, p0/z, [x0]
mova z5.d,p0/m,za1h.d[w12,0]
ld1d {z6.d}, p0/z, [x0, #1, MUL VL]
fmla z3.d,p0/m,z4.d,z2.d
fmla z5.d,p0/m,z6.d,z2.d
mova za0h.d[w12,0],p0/m,z3.d
mova za1h.d[w12,0],p0/m,z5.d
mova z7.d,p0/m,za0h.d[w12,1]
ld1d {z16.d}, p0/z, [x2]
mova z17.d,p0/m,za1h.d[w12,1]
ld1d {z18.d}, p0/z, [x2, #1, MUL VL]
fmla z7.d,p0/m,z16.d,z2.d
fmla z17.d,p0/m,z18.d,z2.d
st1d {z3.d}, p0, [x3]
st1d {z5.d}, p0, [x3, #1, MUL VL]
st1d {z7.d}, p0, [x9]
st1d {z17.d}, p0, [x9, #1, MUL VL]
mova za0h.d[w12,1],p0/m,z7.d
mova za1h.d[w12,1],p0/m,z17.d
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x9,x9,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr5_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1d {z3.d}, p0/z, [x0]
ld1d {z4.d}, p0/z, [x0, #1, MUL VL]
fmla z0.d,p0/m,z3.d,z2.d
add x3,x3,x8
fmla z1.d,p0/m,z4.d,z2.d
st1d {z0.d}, p0, [x3]
st1d {z1.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
ld1rd {z2.d}, p0/z, [x5]
ld1rd {z3.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x9,x3,x6
.ukr6_slices:
add x1,x1,#-2
ld1d {z4.d}, p0/z, [x0]
ld1d {z5.d}, p0/z, [x0, #1, MUL VL]
ld1d {z6.d}, p0/z, [x2]
ld1d {z7.d}, p0/z, [x2, #1, MUL VL]
fmul z4.d,z4.d,z2.d
mova z16.d,p0/m,za0h.d[w12,0]
fmul z5.d,z5.d,z2.d
mova z17.d,p0/m,za1h.d[w12,0]
fmul z6.d,z6.d,z2.d
mova z18.d,p0/m,za0h.d[w12,1]
fmul z7.d,z7.d,z2.d
mova z19.d,p0/m,za1h.d[w12,1]
fmla z4.d,p0/m,z16.d,z3.d
fmla z5.d,p0/m,z17.d,z3.d
fmla z6.d,p0/m,z18.d,z3.d
fmla z7.d,p0/m,z19.d,z3.d
st1d {z4.d}, p0, [x3]
st1d {z5.d}, p0, [x3, #1, MUL VL]
st1d {z6.d}, p0, [x9]
st1d {z7.d}, p0, [x9, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x9,x9,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr6_slices
sub x0,x0,x8
add x0,x0,x8
ld1d {z4.d}, p0/z, [x0]
ld1d {z5.d}, p0/z, [x0, #1, MUL VL]
sub x3,x3,x8
fmul z4.d,z4.d,z2.d
fmul z5.d,z5.d,z2.d
fmla z4.d,p0/m,z0.d,z3.d
add x3,x3,x8
fmla z5.d,p0/m,z1.d,z3.d
st1d {z4.d}, p0, [x3]
st1d {z5.d}, p0, [x3, #1, MUL VL]
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
.size bli_dgemm_ukrgen_sme_sf_1vx2v_1x2v_asm, .-bli_dgemm_ukrgen_sme_sf_1vx2v_1x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_dgemm_ukrgen_sme_sf_1vx2v_2x2v
.text
.global bli_dgemm_ukrgen_sme_sf_1vx2v_2x2v_asm
.type bli_dgemm_ukrgen_sme_sf_1vx2v_2x2v_asm, %function
bli_dgemm_ukrgen_sme_sf_1vx2v_2x2v_asm:
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
ptrue p0.d
cntd x7
mul x8,x7,x6
lsr x9,x6,#3
and x10,x0,#3
lsr x0,x0,#2
zero {za0.d}
zero {za1.d}
dup z0.d,#0
dup z1.d,#0
dup z2.d,#0
dup z3.d,#0
cbz x0,.ukr7_done
add x11,x1,#16
ld1d {z4.d}, p0/z, [x11, #1, MUL VL]
add x11,x11,#16
ld1d {z5.d}, p0/z, [x2]
ld1d {z6.d}, p0/z, [x2, #1, MUL VL]
ld1d {z7.d}, p0/z, [x1]
ld1d {z16.d}, p0/z, [x11, #2, MUL VL]
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x11,x1,#48
ld1d {z17.d}, p0/z, [x11, #3, MUL VL]
add x11,x11,#-48
incb x11, ALL, MUL #1
ld1rd {z18.d}, p0/z, [x11]
ld1rd {z19.d}, p0/z, [x11, #8]
add x11,x11,#16
incb x11, ALL, MUL #1
ld1rd {z20.d}, p0/z, [x11]
ld1rd {z21.d}, p0/z, [x11, #8]
add x11,x11,#16
incb x11, ALL, MUL #1
ld1rd {z22.d}, p0/z, [x11]
ld1rd {z23.d}, p0/z, [x11, #8]
add x11,x11,#16
incb x11, ALL, MUL #1
ld1rd {z24.d}, p0/z, [x11]
ld1rd {z25.d}, p0/z, [x11, #8]
add x11,x11,#16
fmopa za0.d,p0/m,p0/m,z7.d,z5.d
fmopa za1.d,p0/m,p0/m,z7.d,z6.d
decb x11, ALL, MUL #4
ld1d {z26.d}, p0/z, [x2]
ld1d {z27.d}, p0/z, [x2, #1, MUL VL]
ld1d {z7.d}, p0/z, [x11, #4, MUL VL]
fmopa za0.d,p0/m,p0/m,z4.d,z26.d
fmopa za1.d,p0/m,p0/m,z4.d,z27.d
fmla z0.d,p0/m,z5.d,z18.d
fmla z1.d,p0/m,z6.d,z18.d
fmla z2.d,p0/m,z5.d,z19.d
fmla z3.d,p0/m,z6.d,z19.d
add x11,x11,#16
ld1d {z28.d}, p0/z, [x2, #2, MUL VL]
ld1d {z29.d}, p0/z, [x2, #3, MUL VL]
fmla z0.d,p0/m,z26.d,z20.d
fmla z1.d,p0/m,z27.d,z20.d
fmla z2.d,p0/m,z26.d,z21.d
fmla z3.d,p0/m,z27.d,z21.d
ld1d {z4.d}, p0/z, [x11, #5, MUL VL]
fmopa za0.d,p0/m,p0/m,z16.d,z28.d
fmopa za1.d,p0/m,p0/m,z16.d,z29.d
ld1d {z30.d}, p0/z, [x2, #4, MUL VL]
ld1d {z31.d}, p0/z, [x2, #5, MUL VL]
fmla z0.d,p0/m,z28.d,z22.d
fmla z1.d,p0/m,z29.d,z22.d
fmla z2.d,p0/m,z28.d,z23.d
fmla z3.d,p0/m,z29.d,z23.d
add x11,x11,#16
ld1d {z5.d}, p0/z, [x2, #6, MUL VL]
ld1d {z6.d}, p0/z, [x2, #7, MUL VL]
add x1,x1,#64
fmopa za0.d,p0/m,p0/m,z17.d,z30.d
fmopa za1.d,p0/m,p0/m,z17.d,z31.d
fmla z0.d,p0/m,z30.d,z24.d
fmla z1.d,p0/m,z31.d,z24.d
fmla z2.d,p0/m,z30.d,z25.d
fmla z3.d,p0/m,z31.d,z25.d
ld1d {z16.d}, p0/z, [x11, #6, MUL VL]
incb x1, ALL, MUL #4
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x11,x1,#48
ld1d {z17.d}, p0/z, [x11, #3, MUL VL]
add x11,x11,#-48
incb x11, ALL, MUL #1
ld1rd {z18.d}, p0/z, [x11]
ld1rd {z19.d}, p0/z, [x11, #8]
add x11,x11,#16
incb x11, ALL, MUL #1
ld1rd {z20.d}, p0/z, [x11]
ld1rd {z21.d}, p0/z, [x11, #8]
add x11,x11,#16
incb x11, ALL, MUL #1
ld1rd {z22.d}, p0/z, [x11]
ld1rd {z23.d}, p0/z, [x11, #8]
fmopa za0.d,p0/m,p0/m,z7.d,z5.d
fmopa za1.d,p0/m,p0/m,z7.d,z6.d
ld1d {z26.d}, p0/z, [x2]
ld1d {z27.d}, p0/z, [x2, #1, MUL VL]
fmla z0.d,p0/m,z5.d,z18.d
fmla z1.d,p0/m,z6.d,z18.d
fmla z2.d,p0/m,z5.d,z19.d
fmla z3.d,p0/m,z6.d,z19.d
add x11,x11,#16
fmopa za0.d,p0/m,p0/m,z4.d,z26.d
fmopa za1.d,p0/m,p0/m,z4.d,z27.d
ld1d {z28.d}, p0/z, [x2, #2, MUL VL]
ld1d {z29.d}, p0/z, [x2, #3, MUL VL]
fmla z0.d,p0/m,z26.d,z20.d
fmla z1.d,p0/m,z27.d,z20.d
fmla z2.d,p0/m,z26.d,z21.d
fmla z3.d,p0/m,z27.d,z21.d
incb x11, ALL, MUL #1
fmopa za0.d,p0/m,p0/m,z16.d,z28.d
fmopa za1.d,p0/m,p0/m,z16.d,z29.d
ld1d {z30.d}, p0/z, [x2, #4, MUL VL]
ld1d {z31.d}, p0/z, [x2, #5, MUL VL]
fmla z0.d,p0/m,z28.d,z22.d
fmla z1.d,p0/m,z29.d,z22.d
fmla z2.d,p0/m,z28.d,z23.d
fmla z3.d,p0/m,z29.d,z23.d
ld1rd {z24.d}, p0/z, [x11]
ld1rd {z25.d}, p0/z, [x11, #8]
add x1,x1,#64
fmopa za0.d,p0/m,p0/m,z17.d,z30.d
fmopa za1.d,p0/m,p0/m,z17.d,z31.d
fmla z0.d,p0/m,z30.d,z24.d
fmla z1.d,p0/m,z31.d,z24.d
fmla z2.d,p0/m,z30.d,z25.d
fmla z3.d,p0/m,z31.d,z25.d
incb x1, ALL, MUL #4
incb x2, ALL, MUL #6
.ukr7_done:
cbz x10,.ukr7_taildone
.ukr7_tail:
add x10,x10,#-1
mov x11,x1
incb x11, ALL, MUL #1
ld1d {z7.d}, p0/z, [x1]
ld1d {z5.d}, p0/z, [x2]
ld1d {z6.d}, p0/z, [x2, #1, MUL VL]
ld1rd {z18.d}, p0/z, [x11]
ld1rd {z19.d}, p0/z, [x11, #8]
fmopa za0.d,p0/m,p0/m,z7.d,z5.d
fmopa za1.d,p0/m,p0/m,z7.d,z6.d
fmla z0.d,p0/m,z5.d,z18.d
fmla z1.d,p0/m,z6.d,z18.d
fmla z2.d,p0/m,z5.d,z19.d
fmla z3.d,p0/m,z6.d,z19.d
add x1,x1,#16
incb x1, ALL, MUL #1
incb x2, ALL, MUL #2
cbnz x10,.ukr7_tail
.ukr7_taildone:
ldr d4, [x5]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try0
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr d4, [x5]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try2
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try4
b .ukr0_case4
.ukr0_try4:
b .ukr0_case5
b .ukr0_cases_end
.ukr0_case0:
mov x0,x3
mov x1,x0
mov x2,x0
incb x1, ALL, MUL #1
mov x10,x7
mov x12,#0
incb x2, ALL, MUL #1
add x11,x0,x6
add x1,x1,x6
.ukr1_slices:
add x10,x10,#-2
st1d {za0h.d[w12, 0]}, p0, [x0]
st1d {za1h.d[w12, 0]}, p0, [x2]
st1d {za0h.d[w12, 1]}, p0, [x11]
st1d {za1h.d[w12, 1]}, p0, [x1]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr1_slices
st1d {z0.d}, p0, [x0]
st1d {z1.d}, p0, [x0, #1, MUL VL]
st1d {z2.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z3.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
ld1rd {z4.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
.ukr2_slices:
add x1,x1,#-2
mova z5.d,p0/m,za0h.d[w12,0]
mova z6.d,p0/m,za1h.d[w12,0]
mova z7.d,p0/m,za0h.d[w12,1]
mova z16.d,p0/m,za1h.d[w12,1]
fmul z17.d,z5.d,z4.d
fmul z18.d,z6.d,z4.d
fmul z19.d,z7.d,z4.d
fmul z20.d,z16.d,z4.d
st1d {z17.d}, p0, [x0]
st1d {z18.d}, p0, [x0, #1, MUL VL]
st1d {z19.d}, p0, [x2]
st1d {z20.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr2_slices
sub x0,x0,x8
fmul z5.d,z0.d,z4.d
add x0,x0,x8
fmul z0.d,z1.d,z4.d
fmul z1.d,z2.d,z4.d
st1d {z5.d}, p0, [x0]
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z3.d,z4.d
add x0,x0,x6
st1d {z0.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
add x2,x0,x6
add x10,x3,x6
.ukr3_slices:
add x1,x1,#-2
mova z4.d,p0/m,za0h.d[w12,0]
ld1d {z5.d}, p0/z, [x0]
mova z6.d,p0/m,za1h.d[w12,0]
ld1d {z7.d}, p0/z, [x0, #1, MUL VL]
mova z16.d,p0/m,za0h.d[w12,1]
ld1d {z17.d}, p0/z, [x2]
mova z18.d,p0/m,za1h.d[w12,1]
ld1d {z19.d}, p0/z, [x2, #1, MUL VL]
fadd z5.d,z4.d,z5.d
fadd z7.d,z6.d,z7.d
fadd z17.d,z16.d,z17.d
fadd z19.d,z18.d,z19.d
st1d {z5.d}, p0, [x3]
st1d {z7.d}, p0, [x3, #1, MUL VL]
st1d {z17.d}, p0, [x10]
st1d {z19.d}, p0, [x10, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x10,x10,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr3_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1d {z4.d}, p0/z, [x0]
ld1d {z5.d}, p0/z, [x0, #1, MUL VL]
ld1d {z6.d}, p0/z, [x0, x9, lsl #3]
fadd z4.d,z0.d,z4.d
add x3,x3,x8
fadd z5.d,z1.d,z5.d
fadd z6.d,z2.d,z6.d
add x0,x0,x6
st1d {z4.d}, p0, [x3]
st1d {z5.d}, p0, [x3, #1, MUL VL]
st1d {z6.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fadd z0.d,z3.d,z0.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
ld1rd {z4.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x10,x3,x6
.ukr4_slices:
add x1,x1,#-2
mova z5.d,p0/m,za0h.d[w12,0]
ld1d {z6.d}, p0/z, [x0]
mova z7.d,p0/m,za1h.d[w12,0]
ld1d {z16.d}, p0/z, [x0, #1, MUL VL]
mova z17.d,p0/m,za0h.d[w12,1]
ld1d {z18.d}, p0/z, [x2]
mova z19.d,p0/m,za1h.d[w12,1]
ld1d {z20.d}, p0/z, [x2, #1, MUL VL]
fmla z6.d,p0/m,z5.d,z4.d
fmla z16.d,p0/m,z7.d,z4.d
fmla z18.d,p0/m,z17.d,z4.d
fmla z20.d,p0/m,z19.d,z4.d
st1d {z6.d}, p0, [x3]
st1d {z16.d}, p0, [x3, #1, MUL VL]
st1d {z18.d}, p0, [x10]
st1d {z20.d}, p0, [x10, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x10,x10,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr4_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1d {z5.d}, p0/z, [x0]
ld1d {z6.d}, p0/z, [x0, #1, MUL VL]
ld1d {z7.d}, p0/z, [x0, x9, lsl #3]
fmla z5.d,p0/m,z0.d,z4.d
add x3,x3,x8
fmla z6.d,p0/m,z1.d,z4.d
fmla z7.d,p0/m,z2.d,z4.d
add x0,x0,x6
st1d {z5.d}, p0, [x3]
st1d {z6.d}, p0, [x3, #1, MUL VL]
st1d {z7.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fmla z0.d,p0/m,z3.d,z4.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
ld1rd {z4.d}, p0/z, [x5]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x10,x3,x6
.ukr5_slices:
add x1,x1,#-2
mova z5.d,p0/m,za0h.d[w12,0]
ld1d {z6.d}, p0/z, [x0]
mova z7.d,p0/m,za1h.d[w12,0]
ld1d {z16.d}, p0/z, [x0, #1, MUL VL]
fmla z5.d,p0/m,z6.d,z4.d
fmla z7.d,p0/m,z16.d,z4.d
mova za0h.d[w12,0],p0/m,z5.d
mova za1h.d[w12,0],p0/m,z7.d
mova z17.d,p0/m,za0h.d[w12,1]
ld1d {z18.d}, p0/z, [x2]
mova z19.d,p0/m,za1h.d[w12,1]
ld1d {z20.d}, p0/z, [x2, #1, MUL VL]
fmla z17.d,p0/m,z18.d,z4.d
fmla z19.d,p0/m,z20.d,z4.d
st1d {z5.d}, p0, [x3]
st1d {z7.d}, p0, [x3, #1, MUL VL]
st1d {z17.d}, p0, [x10]
st1d {z19.d}, p0, [x10, #1, MUL VL]
mova za0h.d[w12,1],p0/m,z17.d
mova za1h.d[w12,1],p0/m,z19.d
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x10,x10,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr5_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1d {z5.d}, p0/z, [x0]
ld1d {z6.d}, p0/z, [x0, #1, MUL VL]
ld1d {z7.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z5.d,z4.d
add x3,x3,x8
fmla z1.d,p0/m,z6.d,z4.d
fmla z2.d,p0/m,z7.d,z4.d
add x0,x0,x6
st1d {z0.d}, p0, [x3]
st1d {z1.d}, p0, [x3, #1, MUL VL]
st1d {z2.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fmla z3.d,p0/m,z0.d,z4.d
add x3,x3,x6
st1d {z3.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
ld1rd {z4.d}, p0/z, [x5]
ld1rd {z5.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x10,x3,x6
.ukr6_slices:
add x1,x1,#-2
ld1d {z6.d}, p0/z, [x0]
ld1d {z7.d}, p0/z, [x0, #1, MUL VL]
ld1d {z16.d}, p0/z, [x2]
ld1d {z17.d}, p0/z, [x2, #1, MUL VL]
fmul z6.d,z6.d,z4.d
mova z18.d,p0/m,za0h.d[w12,0]
fmul z7.d,z7.d,z4.d
mova z19.d,p0/m,za1h.d[w12,0]
fmul z16.d,z16.d,z4.d
mova z20.d,p0/m,za0h.d[w12,1]
fmul z17.d,z17.d,z4.d
mova z21.d,p0/m,za1h.d[w12,1]
fmla z6.d,p0/m,z18.d,z5.d
fmla z7.d,p0/m,z19.d,z5.d
fmla z16.d,p0/m,z20.d,z5.d
fmla z17.d,p0/m,z21.d,z5.d
st1d {z6.d}, p0, [x3]
st1d {z7.d}, p0, [x3, #1, MUL VL]
st1d {z16.d}, p0, [x10]
st1d {z17.d}, p0, [x10, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x10,x10,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr6_slices
sub x0,x0,x8
add x0,x0,x8
ld1d {z6.d}, p0/z, [x0]
ld1d {z7.d}, p0/z, [x0, #1, MUL VL]
ld1d {z16.d}, p0/z, [x0, x9, lsl #3]
sub x3,x3,x8
fmul z6.d,z6.d,z4.d
fmul z7.d,z7.d,z4.d
fmul z16.d,z16.d,z4.d
add x0,x0,x6
fmla z6.d,p0/m,z0.d,z5.d
add x3,x3,x8
fmla z7.d,p0/m,z1.d,z5.d
fmla z16.d,p0/m,z2.d,z5.d
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
st1d {z6.d}, p0, [x3]
st1d {z7.d}, p0, [x3, #1, MUL VL]
st1d {z16.d}, p0, [x3, x9, lsl #3]
fmul z0.d,z0.d,z4.d
fmla z0.d,p0/m,z3.d,z5.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
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
.size bli_dgemm_ukrgen_sme_sf_1vx2v_2x2v_asm, .-bli_dgemm_ukrgen_sme_sf_1vx2v_2x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_dgemm_ukrgen_sme_sf_1vx2v_3x2v
.text
.global bli_dgemm_ukrgen_sme_sf_1vx2v_3x2v_asm
.type bli_dgemm_ukrgen_sme_sf_1vx2v_3x2v_asm, %function
bli_dgemm_ukrgen_sme_sf_1vx2v_3x2v_asm:
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
ptrue p0.d
cntd x7
mul x8,x7,x6
lsr x9,x6,#3
and x10,x0,#3
lsr x0,x0,#2
zero {za0.d}
zero {za1.d}
dup z0.d,#0
dup z1.d,#0
dup z2.d,#0
dup z3.d,#0
dup z4.d,#0
dup z5.d,#0
cbz x0,.ukr7_done
add x11,x1,#24
ld1d {z6.d}, p0/z, [x11, #1, MUL VL]
add x11,x11,#24
ld1d {z7.d}, p0/z, [x11, #2, MUL VL]
ld1d {z16.d}, p0/z, [x1]
add x11,x11,#24
ld1d {z17.d}, p0/z, [x2]
ld1d {z18.d}, p0/z, [x2, #1, MUL VL]
ld1d {z19.d}, p0/z, [x11, #3, MUL VL]
incb x2, ALL, MUL #2
incb x1, ALL, MUL #1
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x11,x1,#24
incb x11, ALL, MUL #1
ld1rd {z20.d}, p0/z, [x11]
ld1rd {z21.d}, p0/z, [x11, #8]
ld1rd {z22.d}, p0/z, [x11, #16]
add x11,x11,#24
incb x11, ALL, MUL #1
ld1rd {z23.d}, p0/z, [x11]
ld1rd {z24.d}, p0/z, [x11, #8]
ld1rd {z25.d}, p0/z, [x11, #16]
add x11,x11,#24
incb x11, ALL, MUL #1
ld1rd {z26.d}, p0/z, [x11]
ld1rd {z27.d}, p0/z, [x11, #8]
ld1rd {z28.d}, p0/z, [x11, #16]
add x11,x11,#24
fmopa za0.d,p0/m,p0/m,z16.d,z17.d
fmopa za1.d,p0/m,p0/m,z16.d,z18.d
decb x11, ALL, MUL #3
ld1d {z29.d}, p0/z, [x2]
ld1d {z30.d}, p0/z, [x2, #1, MUL VL]
ld1d {z16.d}, p0/z, [x11, #3, MUL VL]
fmopa za0.d,p0/m,p0/m,z6.d,z29.d
fmopa za1.d,p0/m,p0/m,z6.d,z30.d
add x11,x11,#24
ld1d {z31.d}, p0/z, [x2, #2, MUL VL]
ld1d {z8.d}, p0/z, [x2, #3, MUL VL]
ld1rd {z9.d}, p0/z, [x1]
ld1rd {z10.d}, p0/z, [x1, #8]
ld1rd {z11.d}, p0/z, [x1, #16]
ld1d {z6.d}, p0/z, [x11, #4, MUL VL]
fmopa za0.d,p0/m,p0/m,z7.d,z31.d
fmopa za1.d,p0/m,p0/m,z7.d,z8.d
fmla z0.d,p0/m,z17.d,z9.d
fmla z1.d,p0/m,z18.d,z9.d
fmla z2.d,p0/m,z17.d,z10.d
fmla z3.d,p0/m,z18.d,z10.d
fmla z4.d,p0/m,z17.d,z11.d
fmla z5.d,p0/m,z18.d,z11.d
add x11,x11,#24
ld1d {z12.d}, p0/z, [x2, #4, MUL VL]
ld1d {z13.d}, p0/z, [x2, #5, MUL VL]
fmla z0.d,p0/m,z29.d,z20.d
fmla z1.d,p0/m,z30.d,z20.d
fmla z2.d,p0/m,z29.d,z21.d
fmla z3.d,p0/m,z30.d,z21.d
fmla z4.d,p0/m,z29.d,z22.d
fmla z5.d,p0/m,z30.d,z22.d
ld1d {z7.d}, p0/z, [x11, #5, MUL VL]
fmopa za0.d,p0/m,p0/m,z19.d,z12.d
fmopa za1.d,p0/m,p0/m,z19.d,z13.d
fmla z0.d,p0/m,z31.d,z23.d
fmla z1.d,p0/m,z8.d,z23.d
fmla z2.d,p0/m,z31.d,z24.d
fmla z3.d,p0/m,z8.d,z24.d
fmla z4.d,p0/m,z31.d,z25.d
fmla z5.d,p0/m,z8.d,z25.d
add x11,x11,#24
ld1d {z17.d}, p0/z, [x2, #6, MUL VL]
ld1d {z18.d}, p0/z, [x2, #7, MUL VL]
add x1,x1,#96
fmla z0.d,p0/m,z12.d,z26.d
fmla z1.d,p0/m,z13.d,z26.d
fmla z2.d,p0/m,z12.d,z27.d
fmla z3.d,p0/m,z13.d,z27.d
fmla z4.d,p0/m,z12.d,z28.d
fmla z5.d,p0/m,z13.d,z28.d
ld1d {z19.d}, p0/z, [x11, #6, MUL VL]
incb x1, ALL, MUL #4
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x11,x1,#24
incb x11, ALL, MUL #1
ld1rd {z20.d}, p0/z, [x11]
ld1rd {z21.d}, p0/z, [x11, #8]
ld1rd {z22.d}, p0/z, [x11, #16]
add x11,x11,#24
incb x11, ALL, MUL #1
ld1rd {z9.d}, p0/z, [x1]
ld1rd {z10.d}, p0/z, [x1, #8]
ld1rd {z11.d}, p0/z, [x1, #16]
ld1rd {z23.d}, p0/z, [x11]
ld1rd {z24.d}, p0/z, [x11, #8]
ld1rd {z25.d}, p0/z, [x11, #16]
fmopa za0.d,p0/m,p0/m,z16.d,z17.d
fmopa za1.d,p0/m,p0/m,z16.d,z18.d
ld1d {z29.d}, p0/z, [x2]
ld1d {z30.d}, p0/z, [x2, #1, MUL VL]
fmla z0.d,p0/m,z17.d,z9.d
fmla z1.d,p0/m,z18.d,z9.d
fmla z2.d,p0/m,z17.d,z10.d
fmla z3.d,p0/m,z18.d,z10.d
fmla z4.d,p0/m,z17.d,z11.d
fmla z5.d,p0/m,z18.d,z11.d
add x11,x11,#24
fmopa za0.d,p0/m,p0/m,z6.d,z29.d
fmopa za1.d,p0/m,p0/m,z6.d,z30.d
ld1d {z31.d}, p0/z, [x2, #2, MUL VL]
ld1d {z8.d}, p0/z, [x2, #3, MUL VL]
fmla z0.d,p0/m,z29.d,z20.d
fmla z1.d,p0/m,z30.d,z20.d
fmla z2.d,p0/m,z29.d,z21.d
fmla z3.d,p0/m,z30.d,z21.d
fmla z4.d,p0/m,z29.d,z22.d
fmla z5.d,p0/m,z30.d,z22.d
incb x11, ALL, MUL #1
add x1,x1,#96
fmopa za0.d,p0/m,p0/m,z7.d,z31.d
fmopa za1.d,p0/m,p0/m,z7.d,z8.d
ld1d {z12.d}, p0/z, [x2, #4, MUL VL]
ld1d {z13.d}, p0/z, [x2, #5, MUL VL]
fmla z0.d,p0/m,z31.d,z23.d
fmla z1.d,p0/m,z8.d,z23.d
fmla z2.d,p0/m,z31.d,z24.d
fmla z3.d,p0/m,z8.d,z24.d
fmla z4.d,p0/m,z31.d,z25.d
fmla z5.d,p0/m,z8.d,z25.d
ld1rd {z26.d}, p0/z, [x11]
ld1rd {z27.d}, p0/z, [x11, #8]
ld1rd {z28.d}, p0/z, [x11, #16]
incb x1, ALL, MUL #4
fmopa za0.d,p0/m,p0/m,z19.d,z12.d
fmopa za1.d,p0/m,p0/m,z19.d,z13.d
fmla z0.d,p0/m,z12.d,z26.d
fmla z1.d,p0/m,z13.d,z26.d
fmla z2.d,p0/m,z12.d,z27.d
fmla z3.d,p0/m,z13.d,z27.d
fmla z4.d,p0/m,z12.d,z28.d
fmla z5.d,p0/m,z13.d,z28.d
incb x2, ALL, MUL #6
decb x1, ALL, MUL #1
.ukr7_done:
cbz x10,.ukr7_taildone
.ukr7_tail:
add x10,x10,#-1
mov x11,x1
incb x11, ALL, MUL #1
ld1d {z16.d}, p0/z, [x1]
ld1d {z17.d}, p0/z, [x2]
ld1d {z18.d}, p0/z, [x2, #1, MUL VL]
ld1rd {z9.d}, p0/z, [x11]
ld1rd {z10.d}, p0/z, [x11, #8]
ld1rd {z11.d}, p0/z, [x11, #16]
fmopa za0.d,p0/m,p0/m,z16.d,z17.d
fmopa za1.d,p0/m,p0/m,z16.d,z18.d
fmla z0.d,p0/m,z17.d,z9.d
fmla z1.d,p0/m,z18.d,z9.d
fmla z2.d,p0/m,z17.d,z10.d
fmla z3.d,p0/m,z18.d,z10.d
fmla z4.d,p0/m,z17.d,z11.d
fmla z5.d,p0/m,z18.d,z11.d
add x1,x1,#24
incb x1, ALL, MUL #1
incb x2, ALL, MUL #2
cbnz x10,.ukr7_tail
.ukr7_taildone:
ldr d6, [x5]
fmov d7,xzr
fcmp d6,d7
b.ne .ukr0_try0
ldr d6, [x4]
mov x0,#4607182418800017408
fmov d7,x0
fcmp d6,d7
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr d6, [x5]
mov x0,#4607182418800017408
fmov d7,x0
fcmp d6,d7
b.ne .ukr0_try2
ldr d6, [x4]
mov x0,#4607182418800017408
fmov d7,x0
fcmp d6,d7
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr d6, [x4]
mov x0,#4607182418800017408
fmov d7,x0
fcmp d6,d7
b.ne .ukr0_try4
b .ukr0_case4
.ukr0_try4:
b .ukr0_case5
b .ukr0_cases_end
.ukr0_case0:
mov x0,x3
mov x1,x0
mov x2,x0
incb x1, ALL, MUL #1
mov x10,x7
mov x12,#0
incb x2, ALL, MUL #1
add x11,x0,x6
add x1,x1,x6
.ukr1_slices:
add x10,x10,#-2
st1d {za0h.d[w12, 0]}, p0, [x0]
st1d {za1h.d[w12, 0]}, p0, [x2]
st1d {za0h.d[w12, 1]}, p0, [x11]
st1d {za1h.d[w12, 1]}, p0, [x1]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr1_slices
st1d {z0.d}, p0, [x0]
st1d {z1.d}, p0, [x0, #1, MUL VL]
st1d {z2.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z3.d}, p0, [x0, #1, MUL VL]
st1d {z4.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z5.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
ld1rd {z6.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
.ukr2_slices:
add x1,x1,#-2
mova z7.d,p0/m,za0h.d[w12,0]
mova z16.d,p0/m,za1h.d[w12,0]
mova z17.d,p0/m,za0h.d[w12,1]
mova z18.d,p0/m,za1h.d[w12,1]
fmul z19.d,z7.d,z6.d
fmul z20.d,z16.d,z6.d
fmul z21.d,z17.d,z6.d
fmul z22.d,z18.d,z6.d
st1d {z19.d}, p0, [x0]
st1d {z20.d}, p0, [x0, #1, MUL VL]
st1d {z21.d}, p0, [x2]
st1d {z22.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr2_slices
sub x0,x0,x8
fmul z7.d,z0.d,z6.d
add x0,x0,x8
fmul z0.d,z1.d,z6.d
fmul z1.d,z2.d,z6.d
st1d {z7.d}, p0, [x0]
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z3.d,z6.d
add x0,x0,x6
fmul z1.d,z4.d,z6.d
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z5.d,z6.d
add x0,x0,x6
st1d {z0.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x7
mov x12,#0
add x2,x0,x6
add x10,x3,x6
.ukr3_slices:
add x1,x1,#-2
mova z6.d,p0/m,za0h.d[w12,0]
ld1d {z7.d}, p0/z, [x0]
mova z16.d,p0/m,za1h.d[w12,0]
ld1d {z17.d}, p0/z, [x0, #1, MUL VL]
mova z18.d,p0/m,za0h.d[w12,1]
ld1d {z19.d}, p0/z, [x2]
mova z20.d,p0/m,za1h.d[w12,1]
ld1d {z21.d}, p0/z, [x2, #1, MUL VL]
fadd z7.d,z6.d,z7.d
fadd z17.d,z16.d,z17.d
fadd z19.d,z18.d,z19.d
fadd z21.d,z20.d,z21.d
st1d {z7.d}, p0, [x3]
st1d {z17.d}, p0, [x3, #1, MUL VL]
st1d {z19.d}, p0, [x10]
st1d {z21.d}, p0, [x10, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x10,x10,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr3_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1d {z6.d}, p0/z, [x0]
ld1d {z7.d}, p0/z, [x0, #1, MUL VL]
ld1d {z16.d}, p0/z, [x0, x9, lsl #3]
fadd z6.d,z0.d,z6.d
add x3,x3,x8
fadd z7.d,z1.d,z7.d
fadd z16.d,z2.d,z16.d
add x0,x0,x6
st1d {z6.d}, p0, [x3]
st1d {z7.d}, p0, [x3, #1, MUL VL]
st1d {z16.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fadd z0.d,z3.d,z0.d
add x3,x3,x6
fadd z1.d,z4.d,z1.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fadd z0.d,z5.d,z0.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
ld1rd {z6.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x10,x3,x6
.ukr4_slices:
add x1,x1,#-2
mova z7.d,p0/m,za0h.d[w12,0]
ld1d {z16.d}, p0/z, [x0]
mova z17.d,p0/m,za1h.d[w12,0]
ld1d {z18.d}, p0/z, [x0, #1, MUL VL]
mova z19.d,p0/m,za0h.d[w12,1]
ld1d {z20.d}, p0/z, [x2]
mova z21.d,p0/m,za1h.d[w12,1]
ld1d {z22.d}, p0/z, [x2, #1, MUL VL]
fmla z16.d,p0/m,z7.d,z6.d
fmla z18.d,p0/m,z17.d,z6.d
fmla z20.d,p0/m,z19.d,z6.d
fmla z22.d,p0/m,z21.d,z6.d
st1d {z16.d}, p0, [x3]
st1d {z18.d}, p0, [x3, #1, MUL VL]
st1d {z20.d}, p0, [x10]
st1d {z22.d}, p0, [x10, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x10,x10,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr4_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1d {z7.d}, p0/z, [x0]
ld1d {z16.d}, p0/z, [x0, #1, MUL VL]
ld1d {z17.d}, p0/z, [x0, x9, lsl #3]
fmla z7.d,p0/m,z0.d,z6.d
add x3,x3,x8
fmla z16.d,p0/m,z1.d,z6.d
fmla z17.d,p0/m,z2.d,z6.d
add x0,x0,x6
st1d {z7.d}, p0, [x3]
st1d {z16.d}, p0, [x3, #1, MUL VL]
st1d {z17.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z3.d,z6.d
add x3,x3,x6
fmla z1.d,p0/m,z4.d,z6.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fmla z0.d,p0/m,z5.d,z6.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
ld1rd {z6.d}, p0/z, [x5]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x10,x3,x6
.ukr5_slices:
add x1,x1,#-2
mova z7.d,p0/m,za0h.d[w12,0]
ld1d {z16.d}, p0/z, [x0]
mova z17.d,p0/m,za1h.d[w12,0]
ld1d {z18.d}, p0/z, [x0, #1, MUL VL]
fmla z7.d,p0/m,z16.d,z6.d
fmla z17.d,p0/m,z18.d,z6.d
mova za0h.d[w12,0],p0/m,z7.d
mova za1h.d[w12,0],p0/m,z17.d
mova z19.d,p0/m,za0h.d[w12,1]
ld1d {z20.d}, p0/z, [x2]
mova z21.d,p0/m,za1h.d[w12,1]
ld1d {z22.d}, p0/z, [x2, #1, MUL VL]
fmla z19.d,p0/m,z20.d,z6.d
fmla z21.d,p0/m,z22.d,z6.d
st1d {z7.d}, p0, [x3]
st1d {z17.d}, p0, [x3, #1, MUL VL]
st1d {z19.d}, p0, [x10]
st1d {z21.d}, p0, [x10, #1, MUL VL]
mova za0h.d[w12,1],p0/m,z19.d
mova za1h.d[w12,1],p0/m,z21.d
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x10,x10,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr5_slices
sub x0,x0,x8
add x0,x0,x8
sub x3,x3,x8
ld1d {z7.d}, p0/z, [x0]
ld1d {z16.d}, p0/z, [x0, #1, MUL VL]
ld1d {z17.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z7.d,z6.d
add x3,x3,x8
fmla z1.d,p0/m,z16.d,z6.d
fmla z2.d,p0/m,z17.d,z6.d
add x0,x0,x6
st1d {z0.d}, p0, [x3]
st1d {z1.d}, p0, [x3, #1, MUL VL]
st1d {z2.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z3.d,p0/m,z0.d,z6.d
add x3,x3,x6
fmla z4.d,p0/m,z1.d,z6.d
add x0,x0,x6
st1d {z3.d}, p0, [x3, #1, MUL VL]
st1d {z4.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fmla z5.d,p0/m,z0.d,z6.d
add x3,x3,x6
st1d {z5.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
ld1rd {z6.d}, p0/z, [x5]
ld1rd {z7.d}, p0/z, [x4]
mov x1,x7
mov x12,#0
add x2,x0,x6
add x10,x3,x6
.ukr6_slices:
add x1,x1,#-2
ld1d {z16.d}, p0/z, [x0]
ld1d {z17.d}, p0/z, [x0, #1, MUL VL]
ld1d {z18.d}, p0/z, [x2]
ld1d {z19.d}, p0/z, [x2, #1, MUL VL]
fmul z16.d,z16.d,z6.d
mova z20.d,p0/m,za0h.d[w12,0]
fmul z17.d,z17.d,z6.d
mova z21.d,p0/m,za1h.d[w12,0]
fmul z18.d,z18.d,z6.d
mova z22.d,p0/m,za0h.d[w12,1]
fmul z19.d,z19.d,z6.d
mova z23.d,p0/m,za1h.d[w12,1]
fmla z16.d,p0/m,z20.d,z7.d
fmla z17.d,p0/m,z21.d,z7.d
fmla z18.d,p0/m,z22.d,z7.d
fmla z19.d,p0/m,z23.d,z7.d
st1d {z16.d}, p0, [x3]
st1d {z17.d}, p0, [x3, #1, MUL VL]
st1d {z18.d}, p0, [x10]
st1d {z19.d}, p0, [x10, #1, MUL VL]
add x0,x0,x6, LSL #1
add x2,x2,x6, LSL #1
add x3,x3,x6, LSL #1
add x10,x10,x6, LSL #1
add x12,x12,#2
cbnz x1,.ukr6_slices
sub x0,x0,x8
add x0,x0,x8
ld1d {z16.d}, p0/z, [x0]
ld1d {z17.d}, p0/z, [x0, #1, MUL VL]
ld1d {z18.d}, p0/z, [x0, x9, lsl #3]
sub x3,x3,x8
fmul z16.d,z16.d,z6.d
fmul z17.d,z17.d,z6.d
fmul z18.d,z18.d,z6.d
add x0,x0,x6
fmla z16.d,p0/m,z0.d,z7.d
add x3,x3,x8
fmla z17.d,p0/m,z1.d,z7.d
fmla z18.d,p0/m,z2.d,z7.d
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
st1d {z16.d}, p0, [x3]
st1d {z17.d}, p0, [x3, #1, MUL VL]
st1d {z18.d}, p0, [x3, x9, lsl #3]
fmul z0.d,z0.d,z6.d
fmul z1.d,z1.d,z6.d
add x0,x0,x6
fmla z0.d,p0/m,z3.d,z7.d
add x3,x3,x6
fmla z1.d,p0/m,z4.d,z7.d
ld1d {z2.d}, p0/z, [x0, #1, MUL VL]
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
fmul z2.d,z2.d,z6.d
fmla z2.d,p0/m,z5.d,z7.d
add x3,x3,x6
st1d {z2.d}, p0, [x3, #1, MUL VL]
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
.size bli_dgemm_ukrgen_sme_sf_1vx2v_3x2v_asm, .-bli_dgemm_ukrgen_sme_sf_1vx2v_3x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_dgemm_ukrgen_sme_sf_2vx2v_2x2v
.text
.global bli_dgemm_ukrgen_sme_sf_2vx2v_2x2v_asm
.type bli_dgemm_ukrgen_sme_sf_2vx2v_2x2v_asm, %function
bli_dgemm_ukrgen_sme_sf_2vx2v_2x2v_asm:
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
ptrue p0.d
cntd x7
mul x8,x7,x6
lsr x9,x6,#3
and x10,x0,#3
lsr x0,x0,#2
zero {za0.d}
zero {za1.d}
zero {za2.d}
zero {za3.d}
dup z0.d,#0
dup z1.d,#0
dup z2.d,#0
dup z3.d,#0
cbz x0,.ukr7_done
add x11,x1,#16
ld1d {z4.d}, p0/z, [x2]
ld1d {z5.d}, p0/z, [x2, #1, MUL VL]
ld1d {z6.d}, p0/z, [x1]
ld1d {z7.d}, p0/z, [x1, #1, MUL VL]
ld1d {z16.d}, p0/z, [x11, #2, MUL VL]
ld1d {z17.d}, p0/z, [x11, #3, MUL VL]
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x11,x1,#32
ld1d {z18.d}, p0/z, [x11, #4, MUL VL]
ld1d {z19.d}, p0/z, [x11, #5, MUL VL]
add x11,x11,#16
ld1d {z20.d}, p0/z, [x11, #6, MUL VL]
ld1d {z21.d}, p0/z, [x11, #7, MUL VL]
add x11,x11,#-48
incb x11, ALL, MUL #2
ld1rd {z22.d}, p0/z, [x11]
ld1rd {z23.d}, p0/z, [x11, #8]
add x11,x11,#16
incb x11, ALL, MUL #2
ld1rd {z24.d}, p0/z, [x11]
ld1rd {z25.d}, p0/z, [x11, #8]
add x11,x11,#16
incb x11, ALL, MUL #2
ld1rd {z26.d}, p0/z, [x11]
ld1rd {z27.d}, p0/z, [x11, #8]
add x11,x11,#16
incb x11, ALL, MUL #2
ld1rd {z28.d}, p0/z, [x11]
ld1rd {z29.d}, p0/z, [x11, #8]
fmopa za0.d,p0/m,p0/m,z6.d,z4.d
fmopa za1.d,p0/m,p0/m,z6.d,z5.d
fmopa za2.d,p0/m,p0/m,z7.d,z4.d
fmopa za3.d,p0/m,p0/m,z7.d,z5.d
add x11,x11,#16
ld1d {z30.d}, p0/z, [x2]
ld1d {z31.d}, p0/z, [x2, #1, MUL VL]
fmla z0.d,p0/m,z4.d,z22.d
fmla z1.d,p0/m,z5.d,z22.d
fmla z2.d,p0/m,z4.d,z23.d
fmla z3.d,p0/m,z5.d,z23.d
ld1d {z6.d}, p0/z, [x11]
ld1d {z7.d}, p0/z, [x11, #1, MUL VL]
fmopa za0.d,p0/m,p0/m,z16.d,z30.d
fmopa za1.d,p0/m,p0/m,z16.d,z31.d
fmopa za2.d,p0/m,p0/m,z17.d,z30.d
fmopa za3.d,p0/m,p0/m,z17.d,z31.d
ld1d {z8.d}, p0/z, [x2, #2, MUL VL]
ld1d {z9.d}, p0/z, [x2, #3, MUL VL]
fmla z0.d,p0/m,z30.d,z24.d
fmla z1.d,p0/m,z31.d,z24.d
fmla z2.d,p0/m,z30.d,z25.d
fmla z3.d,p0/m,z31.d,z25.d
add x11,x11,#16
fmopa za0.d,p0/m,p0/m,z18.d,z8.d
fmopa za1.d,p0/m,p0/m,z18.d,z9.d
fmopa za2.d,p0/m,p0/m,z19.d,z8.d
fmopa za3.d,p0/m,p0/m,z19.d,z9.d
ld1d {z10.d}, p0/z, [x2, #4, MUL VL]
ld1d {z11.d}, p0/z, [x2, #5, MUL VL]
fmla z0.d,p0/m,z8.d,z26.d
fmla z1.d,p0/m,z9.d,z26.d
fmla z2.d,p0/m,z8.d,z27.d
fmla z3.d,p0/m,z9.d,z27.d
incb x11, ALL, MUL #2
ld1d {z4.d}, p0/z, [x2, #6, MUL VL]
ld1d {z5.d}, p0/z, [x2, #7, MUL VL]
add x1,x1,#64
fmopa za0.d,p0/m,p0/m,z20.d,z10.d
fmopa za1.d,p0/m,p0/m,z20.d,z11.d
fmopa za2.d,p0/m,p0/m,z21.d,z10.d
fmopa za3.d,p0/m,p0/m,z21.d,z11.d
fmla z0.d,p0/m,z10.d,z28.d
fmla z1.d,p0/m,z11.d,z28.d
fmla z2.d,p0/m,z10.d,z29.d
fmla z3.d,p0/m,z11.d,z29.d
ld1d {z16.d}, p0/z, [x11]
ld1d {z17.d}, p0/z, [x11, #1, MUL VL]
incb x1, ALL, MUL #8
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x11,x1,#32
ld1d {z18.d}, p0/z, [x11, #4, MUL VL]
ld1d {z19.d}, p0/z, [x11, #5, MUL VL]
add x11,x11,#16
ld1d {z20.d}, p0/z, [x11, #6, MUL VL]
ld1d {z21.d}, p0/z, [x11, #7, MUL VL]
add x11,x11,#-48
incb x11, ALL, MUL #2
ld1rd {z22.d}, p0/z, [x11]
ld1rd {z23.d}, p0/z, [x11, #8]
add x11,x11,#16
incb x11, ALL, MUL #2
ld1rd {z24.d}, p0/z, [x11]
ld1rd {z25.d}, p0/z, [x11, #8]
add x11,x11,#16
incb x11, ALL, MUL #2
ld1rd {z26.d}, p0/z, [x11]
ld1rd {z27.d}, p0/z, [x11, #8]
fmopa za0.d,p0/m,p0/m,z6.d,z4.d
fmopa za1.d,p0/m,p0/m,z6.d,z5.d
fmopa za2.d,p0/m,p0/m,z7.d,z4.d
fmopa za3.d,p0/m,p0/m,z7.d,z5.d
ld1d {z30.d}, p0/z, [x2]
ld1d {z31.d}, p0/z, [x2, #1, MUL VL]
fmla z0.d,p0/m,z4.d,z22.d
fmla z1.d,p0/m,z5.d,z22.d
fmla z2.d,p0/m,z4.d,z23.d
fmla z3.d,p0/m,z5.d,z23.d
add x11,x11,#16
fmopa za0.d,p0/m,p0/m,z16.d,z30.d
fmopa za1.d,p0/m,p0/m,z16.d,z31.d
fmopa za2.d,p0/m,p0/m,z17.d,z30.d
fmopa za3.d,p0/m,p0/m,z17.d,z31.d
ld1d {z8.d}, p0/z, [x2, #2, MUL VL]
ld1d {z9.d}, p0/z, [x2, #3, MUL VL]
fmla z0.d,p0/m,z30.d,z24.d
fmla z1.d,p0/m,z31.d,z24.d
fmla z2.d,p0/m,z30.d,z25.d
fmla z3.d,p0/m,z31.d,z25.d
incb x11, ALL, MUL #2
fmopa za0.d,p0/m,p0/m,z18.d,z8.d
fmopa za1.d,p0/m,p0/m,z18.d,z9.d
fmopa za2.d,p0/m,p0/m,z19.d,z8.d
fmopa za3.d,p0/m,p0/m,z19.d,z9.d
ld1d {z10.d}, p0/z, [x2, #4, MUL VL]
ld1d {z11.d}, p0/z, [x2, #5, MUL VL]
fmla z0.d,p0/m,z8.d,z26.d
fmla z1.d,p0/m,z9.d,z26.d
fmla z2.d,p0/m,z8.d,z27.d
fmla z3.d,p0/m,z9.d,z27.d
ld1rd {z28.d}, p0/z, [x11]
ld1rd {z29.d}, p0/z, [x11, #8]
add x1,x1,#64
fmopa za0.d,p0/m,p0/m,z20.d,z10.d
fmopa za1.d,p0/m,p0/m,z20.d,z11.d
fmopa za2.d,p0/m,p0/m,z21.d,z10.d
fmopa za3.d,p0/m,p0/m,z21.d,z11.d
fmla z0.d,p0/m,z10.d,z28.d
fmla z1.d,p0/m,z11.d,z28.d
fmla z2.d,p0/m,z10.d,z29.d
fmla z3.d,p0/m,z11.d,z29.d
incb x1, ALL, MUL #8
incb x2, ALL, MUL #6
.ukr7_done:
cbz x10,.ukr7_taildone
.ukr7_tail:
add x10,x10,#-1
mov x11,x1
incb x11, ALL, MUL #2
ld1d {z6.d}, p0/z, [x1]
ld1d {z4.d}, p0/z, [x2]
ld1d {z5.d}, p0/z, [x2, #1, MUL VL]
ld1d {z7.d}, p0/z, [x1, #1, MUL VL]
ld1rd {z22.d}, p0/z, [x11]
ld1rd {z23.d}, p0/z, [x11, #8]
fmopa za0.d,p0/m,p0/m,z6.d,z4.d
fmopa za1.d,p0/m,p0/m,z6.d,z5.d
fmopa za2.d,p0/m,p0/m,z7.d,z4.d
fmopa za3.d,p0/m,p0/m,z7.d,z5.d
fmla z0.d,p0/m,z4.d,z22.d
fmla z1.d,p0/m,z5.d,z22.d
fmla z2.d,p0/m,z4.d,z23.d
fmla z3.d,p0/m,z5.d,z23.d
add x1,x1,#16
incb x1, ALL, MUL #2
incb x2, ALL, MUL #2
cbnz x10,.ukr7_tail
.ukr7_taildone:
ldr d4, [x5]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try0
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr d4, [x5]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try2
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
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
add x16,x0,x8
add x1,x1,x8
mov x17,x7
mov x12,#0
incb x11, ALL, MUL #1
add x19,x0,x8
add x2,x2,x8
add x20,x0,x6
add x10,x10,x6
add x16,x16,x6
add x1,x1,x6
.ukr1_slices:
add x17,x17,#-2
st1d {za0h.d[w12, 0]}, p0, [x0]
st1d {za1h.d[w12, 0]}, p0, [x11]
st1d {za2h.d[w12, 0]}, p0, [x19]
st1d {za3h.d[w12, 0]}, p0, [x2]
st1d {za0h.d[w12, 1]}, p0, [x20]
st1d {za1h.d[w12, 1]}, p0, [x10]
st1d {za2h.d[w12, 1]}, p0, [x16]
st1d {za3h.d[w12, 1]}, p0, [x1]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x20,x20,x6, LSL #1
add x10,x10,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x17,.ukr1_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1d {z0.d}, p0, [x0]
st1d {z1.d}, p0, [x0, #1, MUL VL]
st1d {z2.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z3.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
add x1,x0,x8
ld1rd {z4.d}, p0/z, [x4]
mov x2,x7
mov x12,#0
add x10,x0,x8
add x11,x0,x6
add x1,x1,x6
.ukr2_slices:
add x2,x2,#-2
mova z5.d,p0/m,za0h.d[w12,0]
mova z6.d,p0/m,za1h.d[w12,0]
mova z7.d,p0/m,za2h.d[w12,0]
mova z16.d,p0/m,za3h.d[w12,0]
mova z17.d,p0/m,za0h.d[w12,1]
mova z18.d,p0/m,za1h.d[w12,1]
mova z19.d,p0/m,za2h.d[w12,1]
mova z20.d,p0/m,za3h.d[w12,1]
fmul z21.d,z5.d,z4.d
fmul z22.d,z6.d,z4.d
fmul z23.d,z7.d,z4.d
fmul z24.d,z16.d,z4.d
fmul z25.d,z17.d,z4.d
fmul z26.d,z18.d,z4.d
fmul z27.d,z19.d,z4.d
fmul z28.d,z20.d,z4.d
st1d {z21.d}, p0, [x0]
st1d {z22.d}, p0, [x0, #1, MUL VL]
st1d {z23.d}, p0, [x10]
st1d {z24.d}, p0, [x10, #1, MUL VL]
st1d {z25.d}, p0, [x11]
st1d {z26.d}, p0, [x11, #1, MUL VL]
st1d {z27.d}, p0, [x1]
st1d {z28.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x2,.ukr2_slices
sub x0,x0,x8
fmul z5.d,z0.d,z4.d
add x0,x0,x8, LSL #1
fmul z0.d,z1.d,z4.d
fmul z1.d,z2.d,z4.d
st1d {z5.d}, p0, [x0]
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z3.d,z4.d
add x0,x0,x6
st1d {z0.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr3_slices:
add x10,x10,#-2
mova z4.d,p0/m,za0h.d[w12,0]
ld1d {z5.d}, p0/z, [x0]
mova z6.d,p0/m,za1h.d[w12,0]
ld1d {z7.d}, p0/z, [x0, #1, MUL VL]
mova z16.d,p0/m,za2h.d[w12,0]
ld1d {z17.d}, p0/z, [x11]
mova z18.d,p0/m,za3h.d[w12,0]
ld1d {z19.d}, p0/z, [x11, #1, MUL VL]
mova z20.d,p0/m,za0h.d[w12,1]
ld1d {z21.d}, p0/z, [x16]
mova z22.d,p0/m,za1h.d[w12,1]
ld1d {z23.d}, p0/z, [x16, #1, MUL VL]
mova z24.d,p0/m,za2h.d[w12,1]
ld1d {z25.d}, p0/z, [x1]
mova z26.d,p0/m,za3h.d[w12,1]
ld1d {z27.d}, p0/z, [x1, #1, MUL VL]
fadd z5.d,z4.d,z5.d
fadd z7.d,z6.d,z7.d
fadd z17.d,z16.d,z17.d
fadd z19.d,z18.d,z19.d
fadd z21.d,z20.d,z21.d
fadd z23.d,z22.d,z23.d
fadd z25.d,z24.d,z25.d
fadd z27.d,z26.d,z27.d
st1d {z5.d}, p0, [x3]
st1d {z7.d}, p0, [x3, #1, MUL VL]
st1d {z17.d}, p0, [x17]
st1d {z19.d}, p0, [x17, #1, MUL VL]
st1d {z21.d}, p0, [x19]
st1d {z23.d}, p0, [x19, #1, MUL VL]
st1d {z25.d}, p0, [x2]
st1d {z27.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr3_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z4.d}, p0/z, [x0]
mov x3,x0
ld1d {z5.d}, p0/z, [x0, #1, MUL VL]
ld1d {z6.d}, p0/z, [x0, x9, lsl #3]
fadd z4.d,z0.d,z4.d
fadd z5.d,z1.d,z5.d
fadd z6.d,z2.d,z6.d
add x0,x0,x6
st1d {z4.d}, p0, [x3]
st1d {z5.d}, p0, [x3, #1, MUL VL]
st1d {z6.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fadd z0.d,z3.d,z0.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z4.d}, p0/z, [x4]
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr4_slices:
add x10,x10,#-2
mova z5.d,p0/m,za0h.d[w12,0]
ld1d {z6.d}, p0/z, [x0]
mova z7.d,p0/m,za1h.d[w12,0]
ld1d {z16.d}, p0/z, [x0, #1, MUL VL]
mova z17.d,p0/m,za2h.d[w12,0]
ld1d {z18.d}, p0/z, [x11]
mova z19.d,p0/m,za3h.d[w12,0]
ld1d {z20.d}, p0/z, [x11, #1, MUL VL]
mova z21.d,p0/m,za0h.d[w12,1]
ld1d {z22.d}, p0/z, [x16]
mova z23.d,p0/m,za1h.d[w12,1]
ld1d {z24.d}, p0/z, [x16, #1, MUL VL]
mova z25.d,p0/m,za2h.d[w12,1]
ld1d {z26.d}, p0/z, [x1]
mova z27.d,p0/m,za3h.d[w12,1]
ld1d {z28.d}, p0/z, [x1, #1, MUL VL]
fmla z6.d,p0/m,z5.d,z4.d
fmla z16.d,p0/m,z7.d,z4.d
fmla z18.d,p0/m,z17.d,z4.d
fmla z20.d,p0/m,z19.d,z4.d
fmla z22.d,p0/m,z21.d,z4.d
fmla z24.d,p0/m,z23.d,z4.d
fmla z26.d,p0/m,z25.d,z4.d
fmla z28.d,p0/m,z27.d,z4.d
st1d {z6.d}, p0, [x3]
st1d {z16.d}, p0, [x3, #1, MUL VL]
st1d {z18.d}, p0, [x17]
st1d {z20.d}, p0, [x17, #1, MUL VL]
st1d {z22.d}, p0, [x19]
st1d {z24.d}, p0, [x19, #1, MUL VL]
st1d {z26.d}, p0, [x2]
st1d {z28.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr4_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z5.d}, p0/z, [x0]
mov x3,x0
ld1d {z6.d}, p0/z, [x0, #1, MUL VL]
ld1d {z7.d}, p0/z, [x0, x9, lsl #3]
fmla z5.d,p0/m,z0.d,z4.d
fmla z6.d,p0/m,z1.d,z4.d
fmla z7.d,p0/m,z2.d,z4.d
add x0,x0,x6
st1d {z5.d}, p0, [x3]
st1d {z6.d}, p0, [x3, #1, MUL VL]
st1d {z7.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fmla z0.d,p0/m,z3.d,z4.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z4.d}, p0/z, [x5]
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr5_slices:
add x10,x10,#-2
mova z5.d,p0/m,za0h.d[w12,0]
ld1d {z6.d}, p0/z, [x0]
mova z7.d,p0/m,za1h.d[w12,0]
ld1d {z16.d}, p0/z, [x0, #1, MUL VL]
mova z17.d,p0/m,za2h.d[w12,0]
ld1d {z18.d}, p0/z, [x11]
mova z19.d,p0/m,za3h.d[w12,0]
ld1d {z20.d}, p0/z, [x11, #1, MUL VL]
fmla z5.d,p0/m,z6.d,z4.d
fmla z7.d,p0/m,z16.d,z4.d
fmla z17.d,p0/m,z18.d,z4.d
fmla z19.d,p0/m,z20.d,z4.d
mova za0h.d[w12,0],p0/m,z5.d
mova za1h.d[w12,0],p0/m,z7.d
mova za2h.d[w12,0],p0/m,z17.d
mova za3h.d[w12,0],p0/m,z19.d
mova z21.d,p0/m,za0h.d[w12,1]
ld1d {z22.d}, p0/z, [x16]
mova z23.d,p0/m,za1h.d[w12,1]
ld1d {z24.d}, p0/z, [x16, #1, MUL VL]
mova z25.d,p0/m,za2h.d[w12,1]
ld1d {z26.d}, p0/z, [x1]
mova z27.d,p0/m,za3h.d[w12,1]
ld1d {z28.d}, p0/z, [x1, #1, MUL VL]
fmla z21.d,p0/m,z22.d,z4.d
fmla z23.d,p0/m,z24.d,z4.d
fmla z25.d,p0/m,z26.d,z4.d
fmla z27.d,p0/m,z28.d,z4.d
st1d {z5.d}, p0, [x3]
st1d {z7.d}, p0, [x3, #1, MUL VL]
st1d {z17.d}, p0, [x17]
st1d {z19.d}, p0, [x17, #1, MUL VL]
st1d {z21.d}, p0, [x19]
st1d {z23.d}, p0, [x19, #1, MUL VL]
st1d {z25.d}, p0, [x2]
st1d {z27.d}, p0, [x2, #1, MUL VL]
mova za0h.d[w12,1],p0/m,z21.d
mova za1h.d[w12,1],p0/m,z23.d
mova za2h.d[w12,1],p0/m,z25.d
mova za3h.d[w12,1],p0/m,z27.d
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr5_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z5.d}, p0/z, [x0]
mov x3,x0
ld1d {z6.d}, p0/z, [x0, #1, MUL VL]
ld1d {z7.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z5.d,z4.d
fmla z1.d,p0/m,z6.d,z4.d
fmla z2.d,p0/m,z7.d,z4.d
add x0,x0,x6
st1d {z0.d}, p0, [x3]
st1d {z1.d}, p0, [x3, #1, MUL VL]
st1d {z2.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fmla z3.d,p0/m,z0.d,z4.d
add x3,x3,x6
st1d {z3.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z4.d}, p0/z, [x5]
ld1rd {z5.d}, p0/z, [x4]
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr6_slices:
add x10,x10,#-2
ld1d {z6.d}, p0/z, [x0]
ld1d {z7.d}, p0/z, [x0, #1, MUL VL]
ld1d {z16.d}, p0/z, [x11]
ld1d {z17.d}, p0/z, [x11, #1, MUL VL]
ld1d {z18.d}, p0/z, [x16]
ld1d {z19.d}, p0/z, [x16, #1, MUL VL]
ld1d {z20.d}, p0/z, [x1]
ld1d {z21.d}, p0/z, [x1, #1, MUL VL]
fmul z6.d,z6.d,z4.d
mova z22.d,p0/m,za0h.d[w12,0]
fmul z7.d,z7.d,z4.d
mova z23.d,p0/m,za1h.d[w12,0]
fmul z16.d,z16.d,z4.d
mova z24.d,p0/m,za2h.d[w12,0]
fmul z17.d,z17.d,z4.d
mova z25.d,p0/m,za3h.d[w12,0]
fmul z18.d,z18.d,z4.d
mova z26.d,p0/m,za0h.d[w12,1]
fmul z19.d,z19.d,z4.d
mova z27.d,p0/m,za1h.d[w12,1]
fmul z20.d,z20.d,z4.d
mova z28.d,p0/m,za2h.d[w12,1]
fmul z21.d,z21.d,z4.d
mova z29.d,p0/m,za3h.d[w12,1]
fmla z6.d,p0/m,z22.d,z5.d
fmla z7.d,p0/m,z23.d,z5.d
fmla z16.d,p0/m,z24.d,z5.d
fmla z17.d,p0/m,z25.d,z5.d
fmla z18.d,p0/m,z26.d,z5.d
fmla z19.d,p0/m,z27.d,z5.d
fmla z20.d,p0/m,z28.d,z5.d
fmla z21.d,p0/m,z29.d,z5.d
st1d {z6.d}, p0, [x3]
st1d {z7.d}, p0, [x3, #1, MUL VL]
st1d {z16.d}, p0, [x17]
st1d {z17.d}, p0, [x17, #1, MUL VL]
st1d {z18.d}, p0, [x19]
st1d {z19.d}, p0, [x19, #1, MUL VL]
st1d {z20.d}, p0, [x2]
st1d {z21.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr6_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z6.d}, p0/z, [x0]
mov x3,x0
ld1d {z7.d}, p0/z, [x0, #1, MUL VL]
ld1d {z16.d}, p0/z, [x0, x9, lsl #3]
fmul z6.d,z6.d,z4.d
fmul z7.d,z7.d,z4.d
fmul z16.d,z16.d,z4.d
add x0,x0,x6
fmla z6.d,p0/m,z0.d,z5.d
fmla z7.d,p0/m,z1.d,z5.d
fmla z16.d,p0/m,z2.d,z5.d
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
st1d {z6.d}, p0, [x3]
st1d {z7.d}, p0, [x3, #1, MUL VL]
st1d {z16.d}, p0, [x3, x9, lsl #3]
fmul z0.d,z0.d,z4.d
fmla z0.d,p0/m,z3.d,z5.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
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
.size bli_dgemm_ukrgen_sme_sf_2vx2v_2x2v_asm, .-bli_dgemm_ukrgen_sme_sf_2vx2v_2x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_dgemm_ukrgen_sme_sf_2vx2v_4x2v
.text
.global bli_dgemm_ukrgen_sme_sf_2vx2v_4x2v_asm
.type bli_dgemm_ukrgen_sme_sf_2vx2v_4x2v_asm, %function
bli_dgemm_ukrgen_sme_sf_2vx2v_4x2v_asm:
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
ptrue p0.d
cntd x7
mul x8,x7,x6
lsr x9,x6,#3
and x10,x0,#3
lsr x0,x0,#2
zero {za0.d}
zero {za1.d}
zero {za2.d}
zero {za3.d}
dup z0.d,#0
dup z1.d,#0
dup z2.d,#0
dup z3.d,#0
dup z4.d,#0
dup z5.d,#0
dup z6.d,#0
dup z7.d,#0
cbz x0,.ukr7_done
add x11,x1,#32
ld1d {z16.d}, p0/z, [x11, #2, MUL VL]
ld1d {z17.d}, p0/z, [x11, #3, MUL VL]
add x11,x11,#32
ld1d {z18.d}, p0/z, [x2]
ld1d {z19.d}, p0/z, [x2, #1, MUL VL]
ld1d {z20.d}, p0/z, [x1]
ld1d {z21.d}, p0/z, [x1, #1, MUL VL]
ld1d {z22.d}, p0/z, [x11, #4, MUL VL]
ld1d {z23.d}, p0/z, [x11, #5, MUL VL]
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x11,x1,#96
ld1d {z24.d}, p0/z, [x11, #6, MUL VL]
ld1d {z25.d}, p0/z, [x11, #7, MUL VL]
add x11,x11,#-96
incb x11, ALL, MUL #2
ld1rd {z26.d}, p0/z, [x11]
ld1rd {z27.d}, p0/z, [x11, #8]
ld1rd {z28.d}, p0/z, [x11, #16]
ld1rd {z29.d}, p0/z, [x11, #24]
fmopa za0.d,p0/m,p0/m,z20.d,z18.d
fmopa za1.d,p0/m,p0/m,z20.d,z19.d
fmopa za2.d,p0/m,p0/m,z21.d,z18.d
fmopa za3.d,p0/m,p0/m,z21.d,z19.d
ld1d {z30.d}, p0/z, [x2]
ld1d {z31.d}, p0/z, [x2, #1, MUL VL]
add x11,x11,#32
fmopa za0.d,p0/m,p0/m,z16.d,z30.d
fmopa za1.d,p0/m,p0/m,z16.d,z31.d
fmopa za2.d,p0/m,p0/m,z17.d,z30.d
fmopa za3.d,p0/m,p0/m,z17.d,z31.d
incb x11, ALL, MUL #2
ld1d {z8.d}, p0/z, [x2, #2, MUL VL]
ld1d {z9.d}, p0/z, [x2, #3, MUL VL]
ld1rd {z20.d}, p0/z, [x11]
ld1rd {z21.d}, p0/z, [x11, #8]
ld1rd {z16.d}, p0/z, [x11, #16]
ld1rd {z17.d}, p0/z, [x11, #24]
fmopa za0.d,p0/m,p0/m,z22.d,z8.d
fmopa za1.d,p0/m,p0/m,z22.d,z9.d
fmopa za2.d,p0/m,p0/m,z23.d,z8.d
fmopa za3.d,p0/m,p0/m,z23.d,z9.d
ld1d {z10.d}, p0/z, [x2, #4, MUL VL]
ld1d {z11.d}, p0/z, [x2, #5, MUL VL]
add x11,x11,#32
fmopa za0.d,p0/m,p0/m,z24.d,z10.d
fmopa za1.d,p0/m,p0/m,z24.d,z11.d
fmopa za2.d,p0/m,p0/m,z25.d,z10.d
fmopa za3.d,p0/m,p0/m,z25.d,z11.d
incb x11, ALL, MUL #2
ld1rd {z22.d}, p0/z, [x11]
ld1rd {z23.d}, p0/z, [x11, #8]
ld1rd {z24.d}, p0/z, [x11, #16]
ld1rd {z25.d}, p0/z, [x11, #24]
add x11,x11,#32
fmla z0.d,p0/m,z18.d,z26.d
fmla z1.d,p0/m,z19.d,z26.d
fmla z2.d,p0/m,z18.d,z27.d
fmla z3.d,p0/m,z19.d,z27.d
fmla z4.d,p0/m,z18.d,z28.d
fmla z5.d,p0/m,z19.d,z28.d
fmla z6.d,p0/m,z18.d,z29.d
fmla z7.d,p0/m,z19.d,z29.d
incb x11, ALL, MUL #2
ld1rd {z26.d}, p0/z, [x11]
ld1rd {z27.d}, p0/z, [x11, #8]
ld1rd {z28.d}, p0/z, [x11, #16]
ld1rd {z29.d}, p0/z, [x11, #24]
fmla z0.d,p0/m,z30.d,z20.d
fmla z1.d,p0/m,z31.d,z20.d
fmla z2.d,p0/m,z30.d,z21.d
fmla z3.d,p0/m,z31.d,z21.d
add x11,x11,#32
ld1d {z20.d}, p0/z, [x11]
ld1d {z21.d}, p0/z, [x11, #1, MUL VL]
add x11,x11,#32
fmla z4.d,p0/m,z30.d,z16.d
fmla z5.d,p0/m,z31.d,z16.d
fmla z6.d,p0/m,z30.d,z17.d
fmla z7.d,p0/m,z31.d,z17.d
incb x11, ALL, MUL #2
ld1d {z16.d}, p0/z, [x11]
ld1d {z17.d}, p0/z, [x11, #1, MUL VL]
add x11,x11,#32
fmla z0.d,p0/m,z8.d,z22.d
fmla z1.d,p0/m,z9.d,z22.d
fmla z2.d,p0/m,z8.d,z23.d
fmla z3.d,p0/m,z9.d,z23.d
fmla z4.d,p0/m,z8.d,z24.d
fmla z5.d,p0/m,z9.d,z24.d
fmla z6.d,p0/m,z8.d,z25.d
fmla z7.d,p0/m,z9.d,z25.d
incb x11, ALL, MUL #2
ld1d {z18.d}, p0/z, [x2, #6, MUL VL]
ld1d {z19.d}, p0/z, [x2, #7, MUL VL]
add x1,x1,#128
fmla z0.d,p0/m,z10.d,z26.d
fmla z1.d,p0/m,z11.d,z26.d
fmla z2.d,p0/m,z10.d,z27.d
fmla z3.d,p0/m,z11.d,z27.d
fmla z4.d,p0/m,z10.d,z28.d
fmla z5.d,p0/m,z11.d,z28.d
fmla z6.d,p0/m,z10.d,z29.d
fmla z7.d,p0/m,z11.d,z29.d
ld1d {z22.d}, p0/z, [x11]
ld1d {z23.d}, p0/z, [x11, #1, MUL VL]
incb x1, ALL, MUL #8
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x11,x1,#96
ld1d {z24.d}, p0/z, [x11, #6, MUL VL]
ld1d {z25.d}, p0/z, [x11, #7, MUL VL]
add x11,x11,#-96
incb x11, ALL, MUL #2
ld1rd {z26.d}, p0/z, [x11]
ld1rd {z27.d}, p0/z, [x11, #8]
ld1rd {z28.d}, p0/z, [x11, #16]
ld1rd {z29.d}, p0/z, [x11, #24]
fmopa za0.d,p0/m,p0/m,z20.d,z18.d
fmopa za1.d,p0/m,p0/m,z20.d,z19.d
fmopa za2.d,p0/m,p0/m,z21.d,z18.d
fmopa za3.d,p0/m,p0/m,z21.d,z19.d
ld1d {z30.d}, p0/z, [x2]
ld1d {z31.d}, p0/z, [x2, #1, MUL VL]
add x11,x11,#32
fmopa za0.d,p0/m,p0/m,z16.d,z30.d
fmopa za1.d,p0/m,p0/m,z16.d,z31.d
fmopa za2.d,p0/m,p0/m,z17.d,z30.d
fmopa za3.d,p0/m,p0/m,z17.d,z31.d
incb x11, ALL, MUL #2
ld1d {z8.d}, p0/z, [x2, #2, MUL VL]
ld1d {z9.d}, p0/z, [x2, #3, MUL VL]
ld1rd {z20.d}, p0/z, [x11]
ld1rd {z21.d}, p0/z, [x11, #8]
ld1rd {z16.d}, p0/z, [x11, #16]
ld1rd {z17.d}, p0/z, [x11, #24]
fmopa za0.d,p0/m,p0/m,z22.d,z8.d
fmopa za1.d,p0/m,p0/m,z22.d,z9.d
fmopa za2.d,p0/m,p0/m,z23.d,z8.d
fmopa za3.d,p0/m,p0/m,z23.d,z9.d
ld1d {z10.d}, p0/z, [x2, #4, MUL VL]
ld1d {z11.d}, p0/z, [x2, #5, MUL VL]
add x11,x11,#32
fmopa za0.d,p0/m,p0/m,z24.d,z10.d
fmopa za1.d,p0/m,p0/m,z24.d,z11.d
fmopa za2.d,p0/m,p0/m,z25.d,z10.d
fmopa za3.d,p0/m,p0/m,z25.d,z11.d
incb x11, ALL, MUL #2
ld1rd {z22.d}, p0/z, [x11]
ld1rd {z23.d}, p0/z, [x11, #8]
ld1rd {z24.d}, p0/z, [x11, #16]
ld1rd {z25.d}, p0/z, [x11, #24]
fmla z0.d,p0/m,z18.d,z26.d
fmla z1.d,p0/m,z19.d,z26.d
fmla z2.d,p0/m,z18.d,z27.d
fmla z3.d,p0/m,z19.d,z27.d
fmla z4.d,p0/m,z18.d,z28.d
fmla z5.d,p0/m,z19.d,z28.d
fmla z6.d,p0/m,z18.d,z29.d
fmla z7.d,p0/m,z19.d,z29.d
add x11,x11,#32
fmla z0.d,p0/m,z30.d,z20.d
fmla z1.d,p0/m,z31.d,z20.d
fmla z2.d,p0/m,z30.d,z21.d
fmla z3.d,p0/m,z31.d,z21.d
fmla z4.d,p0/m,z30.d,z16.d
fmla z5.d,p0/m,z31.d,z16.d
fmla z6.d,p0/m,z30.d,z17.d
fmla z7.d,p0/m,z31.d,z17.d
incb x11, ALL, MUL #2
fmla z0.d,p0/m,z8.d,z22.d
fmla z1.d,p0/m,z9.d,z22.d
fmla z2.d,p0/m,z8.d,z23.d
fmla z3.d,p0/m,z9.d,z23.d
fmla z4.d,p0/m,z8.d,z24.d
fmla z5.d,p0/m,z9.d,z24.d
fmla z6.d,p0/m,z8.d,z25.d
fmla z7.d,p0/m,z9.d,z25.d
ld1rd {z26.d}, p0/z, [x11]
ld1rd {z27.d}, p0/z, [x11, #8]
ld1rd {z28.d}, p0/z, [x11, #16]
ld1rd {z29.d}, p0/z, [x11, #24]
add x1,x1,#128
fmla z0.d,p0/m,z10.d,z26.d
fmla z1.d,p0/m,z11.d,z26.d
fmla z2.d,p0/m,z10.d,z27.d
fmla z3.d,p0/m,z11.d,z27.d
fmla z4.d,p0/m,z10.d,z28.d
fmla z5.d,p0/m,z11.d,z28.d
fmla z6.d,p0/m,z10.d,z29.d
fmla z7.d,p0/m,z11.d,z29.d
incb x1, ALL, MUL #8
incb x2, ALL, MUL #6
.ukr7_done:
cbz x10,.ukr7_taildone
.ukr7_tail:
add x10,x10,#-1
mov x11,x1
incb x11, ALL, MUL #2
ld1d {z20.d}, p0/z, [x1]
ld1d {z18.d}, p0/z, [x2]
ld1d {z19.d}, p0/z, [x2, #1, MUL VL]
ld1d {z21.d}, p0/z, [x1, #1, MUL VL]
ld1rd {z16.d}, p0/z, [x11]
ld1rd {z17.d}, p0/z, [x11, #8]
ld1rd {z22.d}, p0/z, [x11, #16]
ld1rd {z23.d}, p0/z, [x11, #24]
fmopa za0.d,p0/m,p0/m,z20.d,z18.d
fmopa za1.d,p0/m,p0/m,z20.d,z19.d
fmopa za2.d,p0/m,p0/m,z21.d,z18.d
fmopa za3.d,p0/m,p0/m,z21.d,z19.d
fmla z0.d,p0/m,z18.d,z16.d
fmla z1.d,p0/m,z19.d,z16.d
fmla z2.d,p0/m,z18.d,z17.d
fmla z3.d,p0/m,z19.d,z17.d
fmla z4.d,p0/m,z18.d,z22.d
fmla z5.d,p0/m,z19.d,z22.d
fmla z6.d,p0/m,z18.d,z23.d
fmla z7.d,p0/m,z19.d,z23.d
add x1,x1,#32
incb x1, ALL, MUL #2
incb x2, ALL, MUL #2
cbnz x10,.ukr7_tail
.ukr7_taildone:
ldr d16, [x5]
fmov d17,xzr
fcmp d16,d17
b.ne .ukr0_try0
ldr d16, [x4]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr d16, [x5]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try2
ldr d16, [x4]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr d16, [x4]
mov x0,#4607182418800017408
fmov d17,x0
fcmp d16,d17
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
add x16,x0,x8
add x1,x1,x8
mov x17,x7
mov x12,#0
incb x11, ALL, MUL #1
add x19,x0,x8
add x2,x2,x8
add x20,x0,x6
add x10,x10,x6
add x16,x16,x6
add x1,x1,x6
.ukr1_slices:
add x17,x17,#-2
st1d {za0h.d[w12, 0]}, p0, [x0]
st1d {za1h.d[w12, 0]}, p0, [x11]
st1d {za2h.d[w12, 0]}, p0, [x19]
st1d {za3h.d[w12, 0]}, p0, [x2]
st1d {za0h.d[w12, 1]}, p0, [x20]
st1d {za1h.d[w12, 1]}, p0, [x10]
st1d {za2h.d[w12, 1]}, p0, [x16]
st1d {za3h.d[w12, 1]}, p0, [x1]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x20,x20,x6, LSL #1
add x10,x10,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x17,.ukr1_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1d {z0.d}, p0, [x0]
st1d {z1.d}, p0, [x0, #1, MUL VL]
st1d {z2.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z3.d}, p0, [x0, #1, MUL VL]
st1d {z4.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z5.d}, p0, [x0, #1, MUL VL]
st1d {z6.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z7.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
add x1,x0,x8
ld1rd {z16.d}, p0/z, [x4]
mov x2,x7
mov x12,#0
add x10,x0,x8
add x11,x0,x6
add x1,x1,x6
.ukr2_slices:
add x2,x2,#-2
mova z17.d,p0/m,za0h.d[w12,0]
mova z18.d,p0/m,za1h.d[w12,0]
mova z19.d,p0/m,za2h.d[w12,0]
mova z20.d,p0/m,za3h.d[w12,0]
mova z21.d,p0/m,za0h.d[w12,1]
mova z22.d,p0/m,za1h.d[w12,1]
mova z23.d,p0/m,za2h.d[w12,1]
mova z24.d,p0/m,za3h.d[w12,1]
fmul z25.d,z17.d,z16.d
fmul z26.d,z18.d,z16.d
fmul z27.d,z19.d,z16.d
fmul z28.d,z20.d,z16.d
fmul z29.d,z21.d,z16.d
fmul z30.d,z22.d,z16.d
fmul z31.d,z23.d,z16.d
fmul z8.d,z24.d,z16.d
st1d {z25.d}, p0, [x0]
st1d {z26.d}, p0, [x0, #1, MUL VL]
st1d {z27.d}, p0, [x10]
st1d {z28.d}, p0, [x10, #1, MUL VL]
st1d {z29.d}, p0, [x11]
st1d {z30.d}, p0, [x11, #1, MUL VL]
st1d {z31.d}, p0, [x1]
st1d {z8.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x2,.ukr2_slices
sub x0,x0,x8
fmul z17.d,z0.d,z16.d
add x0,x0,x8, LSL #1
fmul z0.d,z1.d,z16.d
fmul z1.d,z2.d,z16.d
st1d {z17.d}, p0, [x0]
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z3.d,z16.d
add x0,x0,x6
fmul z1.d,z4.d,z16.d
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z5.d,z16.d
add x0,x0,x6
fmul z1.d,z6.d,z16.d
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z7.d,z16.d
add x0,x0,x6
st1d {z0.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr3_slices:
add x10,x10,#-2
mova z16.d,p0/m,za0h.d[w12,0]
ld1d {z17.d}, p0/z, [x0]
mova z18.d,p0/m,za1h.d[w12,0]
ld1d {z19.d}, p0/z, [x0, #1, MUL VL]
mova z20.d,p0/m,za2h.d[w12,0]
ld1d {z21.d}, p0/z, [x11]
mova z22.d,p0/m,za3h.d[w12,0]
ld1d {z23.d}, p0/z, [x11, #1, MUL VL]
mova z24.d,p0/m,za0h.d[w12,1]
ld1d {z25.d}, p0/z, [x16]
mova z26.d,p0/m,za1h.d[w12,1]
ld1d {z27.d}, p0/z, [x16, #1, MUL VL]
mova z28.d,p0/m,za2h.d[w12,1]
ld1d {z29.d}, p0/z, [x1]
mova z30.d,p0/m,za3h.d[w12,1]
ld1d {z31.d}, p0/z, [x1, #1, MUL VL]
fadd z17.d,z16.d,z17.d
fadd z19.d,z18.d,z19.d
fadd z21.d,z20.d,z21.d
fadd z23.d,z22.d,z23.d
fadd z25.d,z24.d,z25.d
fadd z27.d,z26.d,z27.d
fadd z29.d,z28.d,z29.d
fadd z31.d,z30.d,z31.d
st1d {z17.d}, p0, [x3]
st1d {z19.d}, p0, [x3, #1, MUL VL]
st1d {z21.d}, p0, [x17]
st1d {z23.d}, p0, [x17, #1, MUL VL]
st1d {z25.d}, p0, [x19]
st1d {z27.d}, p0, [x19, #1, MUL VL]
st1d {z29.d}, p0, [x2]
st1d {z31.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr3_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z16.d}, p0/z, [x0]
mov x3,x0
ld1d {z17.d}, p0/z, [x0, #1, MUL VL]
ld1d {z18.d}, p0/z, [x0, x9, lsl #3]
fadd z16.d,z0.d,z16.d
fadd z17.d,z1.d,z17.d
fadd z18.d,z2.d,z18.d
add x0,x0,x6
st1d {z16.d}, p0, [x3]
st1d {z17.d}, p0, [x3, #1, MUL VL]
st1d {z18.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fadd z0.d,z3.d,z0.d
add x3,x3,x6
fadd z1.d,z4.d,z1.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fadd z0.d,z5.d,z0.d
add x3,x3,x6
fadd z1.d,z6.d,z1.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fadd z0.d,z7.d,z0.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z16.d}, p0/z, [x4]
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr4_slices:
add x10,x10,#-2
mova z17.d,p0/m,za0h.d[w12,0]
ld1d {z18.d}, p0/z, [x0]
mova z19.d,p0/m,za1h.d[w12,0]
ld1d {z20.d}, p0/z, [x0, #1, MUL VL]
mova z21.d,p0/m,za2h.d[w12,0]
ld1d {z22.d}, p0/z, [x11]
mova z23.d,p0/m,za3h.d[w12,0]
ld1d {z24.d}, p0/z, [x11, #1, MUL VL]
mova z25.d,p0/m,za0h.d[w12,1]
ld1d {z26.d}, p0/z, [x16]
mova z27.d,p0/m,za1h.d[w12,1]
ld1d {z28.d}, p0/z, [x16, #1, MUL VL]
mova z29.d,p0/m,za2h.d[w12,1]
ld1d {z30.d}, p0/z, [x1]
mova z31.d,p0/m,za3h.d[w12,1]
ld1d {z8.d}, p0/z, [x1, #1, MUL VL]
fmla z18.d,p0/m,z17.d,z16.d
fmla z20.d,p0/m,z19.d,z16.d
fmla z22.d,p0/m,z21.d,z16.d
fmla z24.d,p0/m,z23.d,z16.d
fmla z26.d,p0/m,z25.d,z16.d
fmla z28.d,p0/m,z27.d,z16.d
fmla z30.d,p0/m,z29.d,z16.d
fmla z8.d,p0/m,z31.d,z16.d
st1d {z18.d}, p0, [x3]
st1d {z20.d}, p0, [x3, #1, MUL VL]
st1d {z22.d}, p0, [x17]
st1d {z24.d}, p0, [x17, #1, MUL VL]
st1d {z26.d}, p0, [x19]
st1d {z28.d}, p0, [x19, #1, MUL VL]
st1d {z30.d}, p0, [x2]
st1d {z8.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr4_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z17.d}, p0/z, [x0]
mov x3,x0
ld1d {z18.d}, p0/z, [x0, #1, MUL VL]
ld1d {z19.d}, p0/z, [x0, x9, lsl #3]
fmla z17.d,p0/m,z0.d,z16.d
fmla z18.d,p0/m,z1.d,z16.d
fmla z19.d,p0/m,z2.d,z16.d
add x0,x0,x6
st1d {z17.d}, p0, [x3]
st1d {z18.d}, p0, [x3, #1, MUL VL]
st1d {z19.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z3.d,z16.d
add x3,x3,x6
fmla z1.d,p0/m,z4.d,z16.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z5.d,z16.d
add x3,x3,x6
fmla z1.d,p0/m,z6.d,z16.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fmla z0.d,p0/m,z7.d,z16.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z16.d}, p0/z, [x5]
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr5_slices:
add x10,x10,#-2
mova z17.d,p0/m,za0h.d[w12,0]
ld1d {z18.d}, p0/z, [x0]
mova z19.d,p0/m,za1h.d[w12,0]
ld1d {z20.d}, p0/z, [x0, #1, MUL VL]
mova z21.d,p0/m,za2h.d[w12,0]
ld1d {z22.d}, p0/z, [x11]
mova z23.d,p0/m,za3h.d[w12,0]
ld1d {z24.d}, p0/z, [x11, #1, MUL VL]
fmla z17.d,p0/m,z18.d,z16.d
fmla z19.d,p0/m,z20.d,z16.d
fmla z21.d,p0/m,z22.d,z16.d
fmla z23.d,p0/m,z24.d,z16.d
mova za0h.d[w12,0],p0/m,z17.d
mova za1h.d[w12,0],p0/m,z19.d
mova za2h.d[w12,0],p0/m,z21.d
mova za3h.d[w12,0],p0/m,z23.d
mova z25.d,p0/m,za0h.d[w12,1]
ld1d {z26.d}, p0/z, [x16]
mova z27.d,p0/m,za1h.d[w12,1]
ld1d {z28.d}, p0/z, [x16, #1, MUL VL]
mova z29.d,p0/m,za2h.d[w12,1]
ld1d {z30.d}, p0/z, [x1]
mova z31.d,p0/m,za3h.d[w12,1]
ld1d {z8.d}, p0/z, [x1, #1, MUL VL]
fmla z25.d,p0/m,z26.d,z16.d
fmla z27.d,p0/m,z28.d,z16.d
fmla z29.d,p0/m,z30.d,z16.d
fmla z31.d,p0/m,z8.d,z16.d
st1d {z17.d}, p0, [x3]
st1d {z19.d}, p0, [x3, #1, MUL VL]
st1d {z21.d}, p0, [x17]
st1d {z23.d}, p0, [x17, #1, MUL VL]
st1d {z25.d}, p0, [x19]
st1d {z27.d}, p0, [x19, #1, MUL VL]
st1d {z29.d}, p0, [x2]
st1d {z31.d}, p0, [x2, #1, MUL VL]
mova za0h.d[w12,1],p0/m,z25.d
mova za1h.d[w12,1],p0/m,z27.d
mova za2h.d[w12,1],p0/m,z29.d
mova za3h.d[w12,1],p0/m,z31.d
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr5_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z17.d}, p0/z, [x0]
mov x3,x0
ld1d {z18.d}, p0/z, [x0, #1, MUL VL]
ld1d {z19.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z17.d,z16.d
fmla z1.d,p0/m,z18.d,z16.d
fmla z2.d,p0/m,z19.d,z16.d
add x0,x0,x6
st1d {z0.d}, p0, [x3]
st1d {z1.d}, p0, [x3, #1, MUL VL]
st1d {z2.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z3.d,p0/m,z0.d,z16.d
add x3,x3,x6
fmla z4.d,p0/m,z1.d,z16.d
add x0,x0,x6
st1d {z3.d}, p0, [x3, #1, MUL VL]
st1d {z4.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z5.d,p0/m,z0.d,z16.d
add x3,x3,x6
fmla z6.d,p0/m,z1.d,z16.d
add x0,x0,x6
st1d {z5.d}, p0, [x3, #1, MUL VL]
st1d {z6.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fmla z7.d,p0/m,z0.d,z16.d
add x3,x3,x6
st1d {z7.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z16.d}, p0/z, [x5]
ld1rd {z17.d}, p0/z, [x4]
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr6_slices:
add x10,x10,#-2
ld1d {z18.d}, p0/z, [x0]
ld1d {z19.d}, p0/z, [x0, #1, MUL VL]
ld1d {z20.d}, p0/z, [x11]
ld1d {z21.d}, p0/z, [x11, #1, MUL VL]
ld1d {z22.d}, p0/z, [x16]
ld1d {z23.d}, p0/z, [x16, #1, MUL VL]
ld1d {z24.d}, p0/z, [x1]
ld1d {z25.d}, p0/z, [x1, #1, MUL VL]
fmul z18.d,z18.d,z16.d
mova z26.d,p0/m,za0h.d[w12,0]
fmul z19.d,z19.d,z16.d
mova z27.d,p0/m,za1h.d[w12,0]
fmul z20.d,z20.d,z16.d
mova z28.d,p0/m,za2h.d[w12,0]
fmul z21.d,z21.d,z16.d
mova z29.d,p0/m,za3h.d[w12,0]
fmul z22.d,z22.d,z16.d
mova z30.d,p0/m,za0h.d[w12,1]
fmul z23.d,z23.d,z16.d
mova z31.d,p0/m,za1h.d[w12,1]
fmul z24.d,z24.d,z16.d
mova z8.d,p0/m,za2h.d[w12,1]
fmul z25.d,z25.d,z16.d
mova z9.d,p0/m,za3h.d[w12,1]
fmla z18.d,p0/m,z26.d,z17.d
fmla z19.d,p0/m,z27.d,z17.d
fmla z20.d,p0/m,z28.d,z17.d
fmla z21.d,p0/m,z29.d,z17.d
fmla z22.d,p0/m,z30.d,z17.d
fmla z23.d,p0/m,z31.d,z17.d
fmla z24.d,p0/m,z8.d,z17.d
fmla z25.d,p0/m,z9.d,z17.d
st1d {z18.d}, p0, [x3]
st1d {z19.d}, p0, [x3, #1, MUL VL]
st1d {z20.d}, p0, [x17]
st1d {z21.d}, p0, [x17, #1, MUL VL]
st1d {z22.d}, p0, [x19]
st1d {z23.d}, p0, [x19, #1, MUL VL]
st1d {z24.d}, p0, [x2]
st1d {z25.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr6_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z18.d}, p0/z, [x0]
mov x3,x0
ld1d {z19.d}, p0/z, [x0, #1, MUL VL]
ld1d {z20.d}, p0/z, [x0, x9, lsl #3]
fmul z18.d,z18.d,z16.d
fmul z19.d,z19.d,z16.d
fmul z20.d,z20.d,z16.d
add x0,x0,x6
fmla z18.d,p0/m,z0.d,z17.d
fmla z19.d,p0/m,z1.d,z17.d
fmla z20.d,p0/m,z2.d,z17.d
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
st1d {z18.d}, p0, [x3]
st1d {z19.d}, p0, [x3, #1, MUL VL]
st1d {z20.d}, p0, [x3, x9, lsl #3]
fmul z0.d,z0.d,z16.d
fmul z1.d,z1.d,z16.d
add x0,x0,x6
fmla z0.d,p0/m,z3.d,z17.d
add x3,x3,x6
fmla z1.d,p0/m,z4.d,z17.d
ld1d {z2.d}, p0/z, [x0, #1, MUL VL]
ld1d {z3.d}, p0/z, [x0, x9, lsl #3]
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
fmul z2.d,z2.d,z16.d
fmul z3.d,z3.d,z16.d
add x0,x0,x6
fmla z2.d,p0/m,z5.d,z17.d
add x3,x3,x6
fmla z3.d,p0/m,z6.d,z17.d
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
st1d {z2.d}, p0, [x3, #1, MUL VL]
st1d {z3.d}, p0, [x3, x9, lsl #3]
fmul z0.d,z0.d,z16.d
fmla z0.d,p0/m,z7.d,z17.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
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
.size bli_dgemm_ukrgen_sme_sf_2vx2v_4x2v_asm, .-bli_dgemm_ukrgen_sme_sf_2vx2v_4x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_dgemm_ukrgen_sme_sf_2vx2v_6x2v
.text
.global bli_dgemm_ukrgen_sme_sf_2vx2v_6x2v_asm
.type bli_dgemm_ukrgen_sme_sf_2vx2v_6x2v_asm, %function
bli_dgemm_ukrgen_sme_sf_2vx2v_6x2v_asm:
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
ptrue p0.d
cntd x7
mul x8,x7,x6
lsr x9,x6,#3
and x10,x0,#3
lsr x0,x0,#2
zero {za0.d}
zero {za1.d}
zero {za2.d}
zero {za3.d}
dup z0.d,#0
dup z1.d,#0
dup z2.d,#0
dup z3.d,#0
dup z4.d,#0
dup z5.d,#0
dup z6.d,#0
dup z7.d,#0
dup z16.d,#0
dup z17.d,#0
dup z18.d,#0
dup z19.d,#0
cbz x0,.ukr7_done
add x11,x1,#48
ld1d {z20.d}, p0/z, [x11, #2, MUL VL]
ld1d {z21.d}, p0/z, [x11, #3, MUL VL]
add x11,x11,#48
ld1d {z22.d}, p0/z, [x11, #4, MUL VL]
ld1d {z23.d}, p0/z, [x11, #5, MUL VL]
ld1d {z24.d}, p0/z, [x1]
ld1d {z25.d}, p0/z, [x1, #1, MUL VL]
add x11,x11,#48
ld1d {z26.d}, p0/z, [x2]
ld1d {z27.d}, p0/z, [x2, #1, MUL VL]
ld1d {z28.d}, p0/z, [x11, #6, MUL VL]
ld1d {z29.d}, p0/z, [x11, #7, MUL VL]
incb x2, ALL, MUL #2
incb x1, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
fmopa za0.d,p0/m,p0/m,z24.d,z26.d
fmopa za1.d,p0/m,p0/m,z24.d,z27.d
fmopa za2.d,p0/m,p0/m,z25.d,z26.d
fmopa za3.d,p0/m,p0/m,z25.d,z27.d
ld1d {z30.d}, p0/z, [x2]
ld1d {z31.d}, p0/z, [x2, #1, MUL VL]
fmopa za0.d,p0/m,p0/m,z20.d,z30.d
fmopa za1.d,p0/m,p0/m,z20.d,z31.d
fmopa za2.d,p0/m,p0/m,z21.d,z30.d
fmopa za3.d,p0/m,p0/m,z21.d,z31.d
ld1d {z8.d}, p0/z, [x2, #2, MUL VL]
ld1d {z9.d}, p0/z, [x2, #3, MUL VL]
fmopa za0.d,p0/m,p0/m,z22.d,z8.d
fmopa za1.d,p0/m,p0/m,z22.d,z9.d
fmopa za2.d,p0/m,p0/m,z23.d,z8.d
fmopa za3.d,p0/m,p0/m,z23.d,z9.d
ld1d {z10.d}, p0/z, [x2, #4, MUL VL]
ld1d {z11.d}, p0/z, [x2, #5, MUL VL]
ld1rd {z24.d}, p0/z, [x1]
ld1rd {z25.d}, p0/z, [x1, #8]
ld1rd {z20.d}, p0/z, [x1, #16]
ld1rd {z21.d}, p0/z, [x1, #24]
add x11,x1,#48
fmopa za0.d,p0/m,p0/m,z28.d,z10.d
fmopa za1.d,p0/m,p0/m,z28.d,z11.d
fmopa za2.d,p0/m,p0/m,z29.d,z10.d
fmopa za3.d,p0/m,p0/m,z29.d,z11.d
fmla z0.d,p0/m,z26.d,z24.d
fmla z1.d,p0/m,z27.d,z24.d
fmla z2.d,p0/m,z26.d,z25.d
fmla z3.d,p0/m,z27.d,z25.d
fmla z4.d,p0/m,z26.d,z20.d
fmla z5.d,p0/m,z27.d,z20.d
fmla z6.d,p0/m,z26.d,z21.d
fmla z7.d,p0/m,z27.d,z21.d
incb x11, ALL, MUL #2
ld1rd {z28.d}, p0/z, [x11]
ld1rd {z29.d}, p0/z, [x11, #8]
ld1rd {z24.d}, p0/z, [x11, #16]
ld1rd {z25.d}, p0/z, [x11, #24]
ld1rd {z20.d}, p0/z, [x11, #32]
ld1rd {z21.d}, p0/z, [x11, #40]
ld1rd {z22.d}, p0/z, [x1, #32]
ld1rd {z23.d}, p0/z, [x1, #40]
add x11,x11,#48
fmla z16.d,p0/m,z26.d,z22.d
fmla z17.d,p0/m,z27.d,z22.d
fmla z18.d,p0/m,z26.d,z23.d
fmla z19.d,p0/m,z27.d,z23.d
fmla z0.d,p0/m,z30.d,z28.d
fmla z1.d,p0/m,z31.d,z28.d
fmla z2.d,p0/m,z30.d,z29.d
fmla z3.d,p0/m,z31.d,z29.d
fmla z4.d,p0/m,z30.d,z24.d
fmla z5.d,p0/m,z31.d,z24.d
fmla z6.d,p0/m,z30.d,z25.d
fmla z7.d,p0/m,z31.d,z25.d
incb x11, ALL, MUL #2
ld1rd {z22.d}, p0/z, [x11]
ld1rd {z23.d}, p0/z, [x11, #8]
ld1rd {z28.d}, p0/z, [x11, #16]
ld1rd {z29.d}, p0/z, [x11, #24]
ld1rd {z24.d}, p0/z, [x11, #32]
ld1rd {z25.d}, p0/z, [x11, #40]
add x11,x11,#48
fmla z16.d,p0/m,z30.d,z20.d
fmla z17.d,p0/m,z31.d,z20.d
fmla z18.d,p0/m,z30.d,z21.d
fmla z19.d,p0/m,z31.d,z21.d
fmla z0.d,p0/m,z8.d,z22.d
fmla z1.d,p0/m,z9.d,z22.d
fmla z2.d,p0/m,z8.d,z23.d
fmla z3.d,p0/m,z9.d,z23.d
fmla z4.d,p0/m,z8.d,z28.d
fmla z5.d,p0/m,z9.d,z28.d
fmla z6.d,p0/m,z8.d,z29.d
fmla z7.d,p0/m,z9.d,z29.d
incb x11, ALL, MUL #2
ld1rd {z20.d}, p0/z, [x11]
ld1rd {z21.d}, p0/z, [x11, #8]
ld1rd {z22.d}, p0/z, [x11, #16]
ld1rd {z23.d}, p0/z, [x11, #24]
ld1rd {z28.d}, p0/z, [x11, #32]
ld1rd {z29.d}, p0/z, [x11, #40]
add x11,x11,#48
fmla z16.d,p0/m,z8.d,z24.d
fmla z17.d,p0/m,z9.d,z24.d
fmla z18.d,p0/m,z8.d,z25.d
fmla z19.d,p0/m,z9.d,z25.d
decb x11, ALL, MUL #6
ld1d {z24.d}, p0/z, [x11, #6, MUL VL]
ld1d {z25.d}, p0/z, [x11, #7, MUL VL]
add x11,x11,#48
fmla z0.d,p0/m,z10.d,z20.d
fmla z1.d,p0/m,z11.d,z20.d
fmla z2.d,p0/m,z10.d,z21.d
fmla z3.d,p0/m,z11.d,z21.d
incb x11, ALL, MUL #8
ld1d {z20.d}, p0/z, [x11]
ld1d {z21.d}, p0/z, [x11, #1, MUL VL]
add x11,x11,#48
fmla z4.d,p0/m,z10.d,z22.d
fmla z5.d,p0/m,z11.d,z22.d
fmla z6.d,p0/m,z10.d,z23.d
fmla z7.d,p0/m,z11.d,z23.d
incb x11, ALL, MUL #2
ld1d {z22.d}, p0/z, [x11]
ld1d {z23.d}, p0/z, [x11, #1, MUL VL]
add x11,x11,#48
fmla z16.d,p0/m,z10.d,z28.d
fmla z17.d,p0/m,z11.d,z28.d
fmla z18.d,p0/m,z10.d,z29.d
fmla z19.d,p0/m,z11.d,z29.d
incb x11, ALL, MUL #2
ld1d {z26.d}, p0/z, [x2, #6, MUL VL]
ld1d {z27.d}, p0/z, [x2, #7, MUL VL]
add x1,x1,#192
ld1d {z28.d}, p0/z, [x11]
ld1d {z29.d}, p0/z, [x11, #1, MUL VL]
incb x1, ALL, MUL #8
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
fmopa za0.d,p0/m,p0/m,z24.d,z26.d
fmopa za1.d,p0/m,p0/m,z24.d,z27.d
fmopa za2.d,p0/m,p0/m,z25.d,z26.d
fmopa za3.d,p0/m,p0/m,z25.d,z27.d
ld1d {z30.d}, p0/z, [x2]
ld1d {z31.d}, p0/z, [x2, #1, MUL VL]
fmopa za0.d,p0/m,p0/m,z20.d,z30.d
fmopa za1.d,p0/m,p0/m,z20.d,z31.d
fmopa za2.d,p0/m,p0/m,z21.d,z30.d
fmopa za3.d,p0/m,p0/m,z21.d,z31.d
ld1d {z8.d}, p0/z, [x2, #2, MUL VL]
ld1d {z9.d}, p0/z, [x2, #3, MUL VL]
fmopa za0.d,p0/m,p0/m,z22.d,z8.d
fmopa za1.d,p0/m,p0/m,z22.d,z9.d
fmopa za2.d,p0/m,p0/m,z23.d,z8.d
fmopa za3.d,p0/m,p0/m,z23.d,z9.d
ld1d {z10.d}, p0/z, [x2, #4, MUL VL]
ld1d {z11.d}, p0/z, [x2, #5, MUL VL]
ld1rd {z24.d}, p0/z, [x1]
ld1rd {z25.d}, p0/z, [x1, #8]
ld1rd {z20.d}, p0/z, [x1, #16]
ld1rd {z21.d}, p0/z, [x1, #24]
add x11,x1,#48
fmopa za0.d,p0/m,p0/m,z28.d,z10.d
fmopa za1.d,p0/m,p0/m,z28.d,z11.d
fmopa za2.d,p0/m,p0/m,z29.d,z10.d
fmopa za3.d,p0/m,p0/m,z29.d,z11.d
fmla z0.d,p0/m,z26.d,z24.d
fmla z1.d,p0/m,z27.d,z24.d
fmla z2.d,p0/m,z26.d,z25.d
fmla z3.d,p0/m,z27.d,z25.d
fmla z4.d,p0/m,z26.d,z20.d
fmla z5.d,p0/m,z27.d,z20.d
fmla z6.d,p0/m,z26.d,z21.d
fmla z7.d,p0/m,z27.d,z21.d
incb x11, ALL, MUL #2
ld1rd {z28.d}, p0/z, [x11]
ld1rd {z29.d}, p0/z, [x11, #8]
ld1rd {z24.d}, p0/z, [x11, #16]
ld1rd {z25.d}, p0/z, [x11, #24]
ld1rd {z20.d}, p0/z, [x11, #32]
ld1rd {z21.d}, p0/z, [x11, #40]
ld1rd {z22.d}, p0/z, [x1, #32]
ld1rd {z23.d}, p0/z, [x1, #40]
add x11,x11,#48
fmla z16.d,p0/m,z26.d,z22.d
fmla z17.d,p0/m,z27.d,z22.d
fmla z18.d,p0/m,z26.d,z23.d
fmla z19.d,p0/m,z27.d,z23.d
fmla z0.d,p0/m,z30.d,z28.d
fmla z1.d,p0/m,z31.d,z28.d
fmla z2.d,p0/m,z30.d,z29.d
fmla z3.d,p0/m,z31.d,z29.d
fmla z4.d,p0/m,z30.d,z24.d
fmla z5.d,p0/m,z31.d,z24.d
fmla z6.d,p0/m,z30.d,z25.d
fmla z7.d,p0/m,z31.d,z25.d
incb x11, ALL, MUL #2
ld1rd {z22.d}, p0/z, [x11]
ld1rd {z23.d}, p0/z, [x11, #8]
ld1rd {z28.d}, p0/z, [x11, #16]
ld1rd {z29.d}, p0/z, [x11, #24]
ld1rd {z24.d}, p0/z, [x11, #32]
ld1rd {z25.d}, p0/z, [x11, #40]
add x11,x11,#48
fmla z16.d,p0/m,z30.d,z20.d
fmla z17.d,p0/m,z31.d,z20.d
fmla z18.d,p0/m,z30.d,z21.d
fmla z19.d,p0/m,z31.d,z21.d
fmla z0.d,p0/m,z8.d,z22.d
fmla z1.d,p0/m,z9.d,z22.d
fmla z2.d,p0/m,z8.d,z23.d
fmla z3.d,p0/m,z9.d,z23.d
fmla z4.d,p0/m,z8.d,z28.d
fmla z5.d,p0/m,z9.d,z28.d
fmla z6.d,p0/m,z8.d,z29.d
fmla z7.d,p0/m,z9.d,z29.d
incb x11, ALL, MUL #2
add x1,x1,#192
fmla z16.d,p0/m,z8.d,z24.d
fmla z17.d,p0/m,z9.d,z24.d
fmla z18.d,p0/m,z8.d,z25.d
fmla z19.d,p0/m,z9.d,z25.d
ld1rd {z20.d}, p0/z, [x11]
ld1rd {z21.d}, p0/z, [x11, #8]
ld1rd {z22.d}, p0/z, [x11, #16]
ld1rd {z23.d}, p0/z, [x11, #24]
ld1rd {z28.d}, p0/z, [x11, #32]
ld1rd {z29.d}, p0/z, [x11, #40]
incb x1, ALL, MUL #8
fmla z0.d,p0/m,z10.d,z20.d
fmla z1.d,p0/m,z11.d,z20.d
fmla z2.d,p0/m,z10.d,z21.d
fmla z3.d,p0/m,z11.d,z21.d
fmla z4.d,p0/m,z10.d,z22.d
fmla z5.d,p0/m,z11.d,z22.d
fmla z6.d,p0/m,z10.d,z23.d
fmla z7.d,p0/m,z11.d,z23.d
fmla z16.d,p0/m,z10.d,z28.d
fmla z17.d,p0/m,z11.d,z28.d
fmla z18.d,p0/m,z10.d,z29.d
fmla z19.d,p0/m,z11.d,z29.d
incb x2, ALL, MUL #6
decb x1, ALL, MUL #2
.ukr7_done:
cbz x10,.ukr7_taildone
.ukr7_tail:
add x10,x10,#-1
mov x11,x1
incb x11, ALL, MUL #2
ld1d {z24.d}, p0/z, [x1]
ld1d {z26.d}, p0/z, [x2]
ld1d {z27.d}, p0/z, [x2, #1, MUL VL]
ld1d {z25.d}, p0/z, [x1, #1, MUL VL]
ld1rd {z20.d}, p0/z, [x11]
ld1rd {z21.d}, p0/z, [x11, #8]
ld1rd {z22.d}, p0/z, [x11, #16]
ld1rd {z23.d}, p0/z, [x11, #24]
ld1rd {z28.d}, p0/z, [x11, #32]
ld1rd {z29.d}, p0/z, [x11, #40]
fmopa za0.d,p0/m,p0/m,z24.d,z26.d
fmopa za1.d,p0/m,p0/m,z24.d,z27.d
fmopa za2.d,p0/m,p0/m,z25.d,z26.d
fmopa za3.d,p0/m,p0/m,z25.d,z27.d
fmla z0.d,p0/m,z26.d,z20.d
fmla z1.d,p0/m,z27.d,z20.d
fmla z2.d,p0/m,z26.d,z21.d
fmla z3.d,p0/m,z27.d,z21.d
fmla z4.d,p0/m,z26.d,z22.d
fmla z5.d,p0/m,z27.d,z22.d
fmla z6.d,p0/m,z26.d,z23.d
fmla z7.d,p0/m,z27.d,z23.d
fmla z16.d,p0/m,z26.d,z28.d
fmla z17.d,p0/m,z27.d,z28.d
fmla z18.d,p0/m,z26.d,z29.d
fmla z19.d,p0/m,z27.d,z29.d
add x1,x1,#48
incb x1, ALL, MUL #2
incb x2, ALL, MUL #2
cbnz x10,.ukr7_tail
.ukr7_taildone:
ldr d20, [x5]
fmov d21,xzr
fcmp d20,d21
b.ne .ukr0_try0
ldr d20, [x4]
mov x0,#4607182418800017408
fmov d21,x0
fcmp d20,d21
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr d20, [x5]
mov x0,#4607182418800017408
fmov d21,x0
fcmp d20,d21
b.ne .ukr0_try2
ldr d20, [x4]
mov x0,#4607182418800017408
fmov d21,x0
fcmp d20,d21
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr d20, [x4]
mov x0,#4607182418800017408
fmov d21,x0
fcmp d20,d21
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
add x16,x0,x8
add x1,x1,x8
mov x17,x7
mov x12,#0
incb x11, ALL, MUL #1
add x19,x0,x8
add x2,x2,x8
add x20,x0,x6
add x10,x10,x6
add x16,x16,x6
add x1,x1,x6
.ukr1_slices:
add x17,x17,#-2
st1d {za0h.d[w12, 0]}, p0, [x0]
st1d {za1h.d[w12, 0]}, p0, [x11]
st1d {za2h.d[w12, 0]}, p0, [x19]
st1d {za3h.d[w12, 0]}, p0, [x2]
st1d {za0h.d[w12, 1]}, p0, [x20]
st1d {za1h.d[w12, 1]}, p0, [x10]
st1d {za2h.d[w12, 1]}, p0, [x16]
st1d {za3h.d[w12, 1]}, p0, [x1]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x20,x20,x6, LSL #1
add x10,x10,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x17,.ukr1_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1d {z0.d}, p0, [x0]
st1d {z1.d}, p0, [x0, #1, MUL VL]
st1d {z2.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z3.d}, p0, [x0, #1, MUL VL]
st1d {z4.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z5.d}, p0, [x0, #1, MUL VL]
st1d {z6.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z7.d}, p0, [x0, #1, MUL VL]
st1d {z16.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z17.d}, p0, [x0, #1, MUL VL]
st1d {z18.d}, p0, [x0, x9, lsl #3]
add x0,x0,x6
st1d {z19.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
add x1,x0,x8
ld1rd {z20.d}, p0/z, [x4]
mov x2,x7
mov x12,#0
add x10,x0,x8
add x11,x0,x6
add x1,x1,x6
.ukr2_slices:
add x2,x2,#-2
mova z21.d,p0/m,za0h.d[w12,0]
mova z22.d,p0/m,za1h.d[w12,0]
mova z23.d,p0/m,za2h.d[w12,0]
mova z24.d,p0/m,za3h.d[w12,0]
mova z25.d,p0/m,za0h.d[w12,1]
mova z26.d,p0/m,za1h.d[w12,1]
mova z27.d,p0/m,za2h.d[w12,1]
mova z28.d,p0/m,za3h.d[w12,1]
fmul z29.d,z21.d,z20.d
fmul z30.d,z22.d,z20.d
fmul z31.d,z23.d,z20.d
fmul z8.d,z24.d,z20.d
fmul z9.d,z25.d,z20.d
fmul z10.d,z26.d,z20.d
fmul z11.d,z27.d,z20.d
fmul z12.d,z28.d,z20.d
st1d {z29.d}, p0, [x0]
st1d {z30.d}, p0, [x0, #1, MUL VL]
st1d {z31.d}, p0, [x10]
st1d {z8.d}, p0, [x10, #1, MUL VL]
st1d {z9.d}, p0, [x11]
st1d {z10.d}, p0, [x11, #1, MUL VL]
st1d {z11.d}, p0, [x1]
st1d {z12.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x2,.ukr2_slices
sub x0,x0,x8
fmul z21.d,z0.d,z20.d
add x0,x0,x8, LSL #1
fmul z0.d,z1.d,z20.d
fmul z1.d,z2.d,z20.d
st1d {z21.d}, p0, [x0]
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z3.d,z20.d
add x0,x0,x6
fmul z1.d,z4.d,z20.d
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z5.d,z20.d
add x0,x0,x6
fmul z1.d,z6.d,z20.d
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z7.d,z20.d
add x0,x0,x6
fmul z1.d,z16.d,z20.d
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z17.d,z20.d
add x0,x0,x6
fmul z1.d,z18.d,z20.d
st1d {z0.d}, p0, [x0, #1, MUL VL]
st1d {z1.d}, p0, [x0, x9, lsl #3]
fmul z0.d,z19.d,z20.d
add x0,x0,x6
st1d {z0.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr3_slices:
add x10,x10,#-2
mova z20.d,p0/m,za0h.d[w12,0]
ld1d {z21.d}, p0/z, [x0]
mova z22.d,p0/m,za1h.d[w12,0]
ld1d {z23.d}, p0/z, [x0, #1, MUL VL]
mova z24.d,p0/m,za2h.d[w12,0]
ld1d {z25.d}, p0/z, [x11]
mova z26.d,p0/m,za3h.d[w12,0]
ld1d {z27.d}, p0/z, [x11, #1, MUL VL]
mova z28.d,p0/m,za0h.d[w12,1]
ld1d {z29.d}, p0/z, [x16]
mova z30.d,p0/m,za1h.d[w12,1]
ld1d {z31.d}, p0/z, [x16, #1, MUL VL]
mova z8.d,p0/m,za2h.d[w12,1]
ld1d {z9.d}, p0/z, [x1]
mova z10.d,p0/m,za3h.d[w12,1]
ld1d {z11.d}, p0/z, [x1, #1, MUL VL]
fadd z21.d,z20.d,z21.d
fadd z23.d,z22.d,z23.d
fadd z25.d,z24.d,z25.d
fadd z27.d,z26.d,z27.d
fadd z29.d,z28.d,z29.d
fadd z31.d,z30.d,z31.d
fadd z9.d,z8.d,z9.d
fadd z11.d,z10.d,z11.d
st1d {z21.d}, p0, [x3]
st1d {z23.d}, p0, [x3, #1, MUL VL]
st1d {z25.d}, p0, [x17]
st1d {z27.d}, p0, [x17, #1, MUL VL]
st1d {z29.d}, p0, [x19]
st1d {z31.d}, p0, [x19, #1, MUL VL]
st1d {z9.d}, p0, [x2]
st1d {z11.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr3_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z20.d}, p0/z, [x0]
mov x3,x0
ld1d {z21.d}, p0/z, [x0, #1, MUL VL]
ld1d {z22.d}, p0/z, [x0, x9, lsl #3]
fadd z20.d,z0.d,z20.d
fadd z21.d,z1.d,z21.d
fadd z22.d,z2.d,z22.d
add x0,x0,x6
st1d {z20.d}, p0, [x3]
st1d {z21.d}, p0, [x3, #1, MUL VL]
st1d {z22.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fadd z0.d,z3.d,z0.d
add x3,x3,x6
fadd z1.d,z4.d,z1.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fadd z0.d,z5.d,z0.d
add x3,x3,x6
fadd z1.d,z6.d,z1.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fadd z0.d,z7.d,z0.d
add x3,x3,x6
fadd z1.d,z16.d,z1.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fadd z0.d,z17.d,z0.d
add x3,x3,x6
fadd z1.d,z18.d,z1.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fadd z0.d,z19.d,z0.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z20.d}, p0/z, [x4]
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr4_slices:
add x10,x10,#-2
mova z21.d,p0/m,za0h.d[w12,0]
ld1d {z22.d}, p0/z, [x0]
mova z23.d,p0/m,za1h.d[w12,0]
ld1d {z24.d}, p0/z, [x0, #1, MUL VL]
mova z25.d,p0/m,za2h.d[w12,0]
ld1d {z26.d}, p0/z, [x11]
mova z27.d,p0/m,za3h.d[w12,0]
ld1d {z28.d}, p0/z, [x11, #1, MUL VL]
mova z29.d,p0/m,za0h.d[w12,1]
ld1d {z30.d}, p0/z, [x16]
mova z31.d,p0/m,za1h.d[w12,1]
ld1d {z8.d}, p0/z, [x16, #1, MUL VL]
mova z9.d,p0/m,za2h.d[w12,1]
ld1d {z10.d}, p0/z, [x1]
mova z11.d,p0/m,za3h.d[w12,1]
ld1d {z12.d}, p0/z, [x1, #1, MUL VL]
fmla z22.d,p0/m,z21.d,z20.d
fmla z24.d,p0/m,z23.d,z20.d
fmla z26.d,p0/m,z25.d,z20.d
fmla z28.d,p0/m,z27.d,z20.d
fmla z30.d,p0/m,z29.d,z20.d
fmla z8.d,p0/m,z31.d,z20.d
fmla z10.d,p0/m,z9.d,z20.d
fmla z12.d,p0/m,z11.d,z20.d
st1d {z22.d}, p0, [x3]
st1d {z24.d}, p0, [x3, #1, MUL VL]
st1d {z26.d}, p0, [x17]
st1d {z28.d}, p0, [x17, #1, MUL VL]
st1d {z30.d}, p0, [x19]
st1d {z8.d}, p0, [x19, #1, MUL VL]
st1d {z10.d}, p0, [x2]
st1d {z12.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr4_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z21.d}, p0/z, [x0]
mov x3,x0
ld1d {z22.d}, p0/z, [x0, #1, MUL VL]
ld1d {z23.d}, p0/z, [x0, x9, lsl #3]
fmla z21.d,p0/m,z0.d,z20.d
fmla z22.d,p0/m,z1.d,z20.d
fmla z23.d,p0/m,z2.d,z20.d
add x0,x0,x6
st1d {z21.d}, p0, [x3]
st1d {z22.d}, p0, [x3, #1, MUL VL]
st1d {z23.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z3.d,z20.d
add x3,x3,x6
fmla z1.d,p0/m,z4.d,z20.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z5.d,z20.d
add x3,x3,x6
fmla z1.d,p0/m,z6.d,z20.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z7.d,z20.d
add x3,x3,x6
fmla z1.d,p0/m,z16.d,z20.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z17.d,z20.d
add x3,x3,x6
fmla z1.d,p0/m,z18.d,z20.d
add x0,x0,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fmla z0.d,p0/m,z19.d,z20.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z20.d}, p0/z, [x5]
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr5_slices:
add x10,x10,#-2
mova z21.d,p0/m,za0h.d[w12,0]
ld1d {z22.d}, p0/z, [x0]
mova z23.d,p0/m,za1h.d[w12,0]
ld1d {z24.d}, p0/z, [x0, #1, MUL VL]
mova z25.d,p0/m,za2h.d[w12,0]
ld1d {z26.d}, p0/z, [x11]
mova z27.d,p0/m,za3h.d[w12,0]
ld1d {z28.d}, p0/z, [x11, #1, MUL VL]
fmla z21.d,p0/m,z22.d,z20.d
fmla z23.d,p0/m,z24.d,z20.d
fmla z25.d,p0/m,z26.d,z20.d
fmla z27.d,p0/m,z28.d,z20.d
mova za0h.d[w12,0],p0/m,z21.d
mova za1h.d[w12,0],p0/m,z23.d
mova za2h.d[w12,0],p0/m,z25.d
mova za3h.d[w12,0],p0/m,z27.d
mova z29.d,p0/m,za0h.d[w12,1]
ld1d {z30.d}, p0/z, [x16]
mova z31.d,p0/m,za1h.d[w12,1]
ld1d {z8.d}, p0/z, [x16, #1, MUL VL]
mova z9.d,p0/m,za2h.d[w12,1]
ld1d {z10.d}, p0/z, [x1]
mova z11.d,p0/m,za3h.d[w12,1]
ld1d {z12.d}, p0/z, [x1, #1, MUL VL]
fmla z29.d,p0/m,z30.d,z20.d
fmla z31.d,p0/m,z8.d,z20.d
fmla z9.d,p0/m,z10.d,z20.d
fmla z11.d,p0/m,z12.d,z20.d
st1d {z21.d}, p0, [x3]
st1d {z23.d}, p0, [x3, #1, MUL VL]
st1d {z25.d}, p0, [x17]
st1d {z27.d}, p0, [x17, #1, MUL VL]
st1d {z29.d}, p0, [x19]
st1d {z31.d}, p0, [x19, #1, MUL VL]
st1d {z9.d}, p0, [x2]
st1d {z11.d}, p0, [x2, #1, MUL VL]
mova za0h.d[w12,1],p0/m,z29.d
mova za1h.d[w12,1],p0/m,z31.d
mova za2h.d[w12,1],p0/m,z9.d
mova za3h.d[w12,1],p0/m,z11.d
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr5_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z21.d}, p0/z, [x0]
mov x3,x0
ld1d {z22.d}, p0/z, [x0, #1, MUL VL]
ld1d {z23.d}, p0/z, [x0, x9, lsl #3]
fmla z0.d,p0/m,z21.d,z20.d
fmla z1.d,p0/m,z22.d,z20.d
fmla z2.d,p0/m,z23.d,z20.d
add x0,x0,x6
st1d {z0.d}, p0, [x3]
st1d {z1.d}, p0, [x3, #1, MUL VL]
st1d {z2.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z3.d,p0/m,z0.d,z20.d
add x3,x3,x6
fmla z4.d,p0/m,z1.d,z20.d
add x0,x0,x6
st1d {z3.d}, p0, [x3, #1, MUL VL]
st1d {z4.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z5.d,p0/m,z0.d,z20.d
add x3,x3,x6
fmla z6.d,p0/m,z1.d,z20.d
add x0,x0,x6
st1d {z5.d}, p0, [x3, #1, MUL VL]
st1d {z6.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z7.d,p0/m,z0.d,z20.d
add x3,x3,x6
fmla z16.d,p0/m,z1.d,z20.d
add x0,x0,x6
st1d {z7.d}, p0, [x3, #1, MUL VL]
st1d {z16.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
fmla z17.d,p0/m,z0.d,z20.d
add x3,x3,x6
fmla z18.d,p0/m,z1.d,z20.d
add x0,x0,x6
st1d {z17.d}, p0, [x3, #1, MUL VL]
st1d {z18.d}, p0, [x3, x9, lsl #3]
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
fmla z19.d,p0/m,z0.d,z20.d
add x3,x3,x6
st1d {z19.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z20.d}, p0/z, [x5]
ld1rd {z21.d}, p0/z, [x4]
mov x10,x7
mov x12,#0
add x11,x0,x8
add x16,x0,x6
add x1,x1,x6
add x17,x3,x8
add x19,x3,x6
add x2,x2,x6
.ukr6_slices:
add x10,x10,#-2
ld1d {z22.d}, p0/z, [x0]
ld1d {z23.d}, p0/z, [x0, #1, MUL VL]
ld1d {z24.d}, p0/z, [x11]
ld1d {z25.d}, p0/z, [x11, #1, MUL VL]
ld1d {z26.d}, p0/z, [x16]
ld1d {z27.d}, p0/z, [x16, #1, MUL VL]
ld1d {z28.d}, p0/z, [x1]
ld1d {z29.d}, p0/z, [x1, #1, MUL VL]
fmul z22.d,z22.d,z20.d
mova z30.d,p0/m,za0h.d[w12,0]
fmul z23.d,z23.d,z20.d
mova z31.d,p0/m,za1h.d[w12,0]
fmul z24.d,z24.d,z20.d
mova z8.d,p0/m,za2h.d[w12,0]
fmul z25.d,z25.d,z20.d
mova z9.d,p0/m,za3h.d[w12,0]
fmul z26.d,z26.d,z20.d
mova z10.d,p0/m,za0h.d[w12,1]
fmul z27.d,z27.d,z20.d
mova z11.d,p0/m,za1h.d[w12,1]
fmul z28.d,z28.d,z20.d
mova z12.d,p0/m,za2h.d[w12,1]
fmul z29.d,z29.d,z20.d
mova z13.d,p0/m,za3h.d[w12,1]
fmla z22.d,p0/m,z30.d,z21.d
fmla z23.d,p0/m,z31.d,z21.d
fmla z24.d,p0/m,z8.d,z21.d
fmla z25.d,p0/m,z9.d,z21.d
fmla z26.d,p0/m,z10.d,z21.d
fmla z27.d,p0/m,z11.d,z21.d
fmla z28.d,p0/m,z12.d,z21.d
fmla z29.d,p0/m,z13.d,z21.d
st1d {z22.d}, p0, [x3]
st1d {z23.d}, p0, [x3, #1, MUL VL]
st1d {z24.d}, p0, [x17]
st1d {z25.d}, p0, [x17, #1, MUL VL]
st1d {z26.d}, p0, [x19]
st1d {z27.d}, p0, [x19, #1, MUL VL]
st1d {z28.d}, p0, [x2]
st1d {z29.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x11,x11,x6, LSL #1
add x16,x16,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x17,x17,x6, LSL #1
add x19,x19,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x10,.ukr6_slices
sub x0,x0,x8
sub x3,x3,x8
add x0,x0,x8, LSL #1
ld1d {z22.d}, p0/z, [x0]
mov x3,x0
ld1d {z23.d}, p0/z, [x0, #1, MUL VL]
ld1d {z24.d}, p0/z, [x0, x9, lsl #3]
fmul z22.d,z22.d,z20.d
fmul z23.d,z23.d,z20.d
fmul z24.d,z24.d,z20.d
add x0,x0,x6
fmla z22.d,p0/m,z0.d,z21.d
fmla z23.d,p0/m,z1.d,z21.d
fmla z24.d,p0/m,z2.d,z21.d
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
st1d {z22.d}, p0, [x3]
st1d {z23.d}, p0, [x3, #1, MUL VL]
st1d {z24.d}, p0, [x3, x9, lsl #3]
fmul z0.d,z0.d,z20.d
fmul z1.d,z1.d,z20.d
add x0,x0,x6
fmla z0.d,p0/m,z3.d,z21.d
add x3,x3,x6
fmla z1.d,p0/m,z4.d,z21.d
ld1d {z2.d}, p0/z, [x0, #1, MUL VL]
ld1d {z3.d}, p0/z, [x0, x9, lsl #3]
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
fmul z2.d,z2.d,z20.d
fmul z3.d,z3.d,z20.d
add x0,x0,x6
fmla z2.d,p0/m,z5.d,z21.d
add x3,x3,x6
fmla z3.d,p0/m,z6.d,z21.d
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
ld1d {z1.d}, p0/z, [x0, x9, lsl #3]
st1d {z2.d}, p0, [x3, #1, MUL VL]
st1d {z3.d}, p0, [x3, x9, lsl #3]
fmul z0.d,z0.d,z20.d
fmul z1.d,z1.d,z20.d
add x0,x0,x6
fmla z0.d,p0/m,z7.d,z21.d
add x3,x3,x6
fmla z1.d,p0/m,z16.d,z21.d
ld1d {z2.d}, p0/z, [x0, #1, MUL VL]
ld1d {z3.d}, p0/z, [x0, x9, lsl #3]
st1d {z0.d}, p0, [x3, #1, MUL VL]
st1d {z1.d}, p0, [x3, x9, lsl #3]
fmul z2.d,z2.d,z20.d
fmul z3.d,z3.d,z20.d
add x0,x0,x6
fmla z2.d,p0/m,z17.d,z21.d
add x3,x3,x6
fmla z3.d,p0/m,z18.d,z21.d
ld1d {z0.d}, p0/z, [x0, #1, MUL VL]
st1d {z2.d}, p0, [x3, #1, MUL VL]
st1d {z3.d}, p0, [x3, x9, lsl #3]
fmul z0.d,z0.d,z20.d
fmla z0.d,p0/m,z19.d,z21.d
add x3,x3,x6
st1d {z0.d}, p0, [x3, #1, MUL VL]
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
.size bli_dgemm_ukrgen_sme_sf_2vx2v_6x2v_asm, .-bli_dgemm_ukrgen_sme_sf_2vx2v_6x2v_asm
.section .note.GNU-stack,"",%progbits


### bli_dgemm_ukrgen_sme_sf_2vx2v_1x2v
.text
.global bli_dgemm_ukrgen_sme_sf_2vx2v_1x2v_asm
.type bli_dgemm_ukrgen_sme_sf_2vx2v_1x2v_asm, %function
bli_dgemm_ukrgen_sme_sf_2vx2v_1x2v_asm:
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
ptrue p0.d
cntd x7
mul x8,x7,x6
and x9,x0,#3
lsr x0,x0,#2
zero {za0.d}
zero {za1.d}
zero {za2.d}
zero {za3.d}
dup z0.d,#0
dup z1.d,#0
cbz x0,.ukr7_done
add x10,x1,#8
ld1d {z2.d}, p0/z, [x2]
ld1d {z3.d}, p0/z, [x2, #1, MUL VL]
ld1d {z4.d}, p0/z, [x1]
ld1d {z5.d}, p0/z, [x1, #1, MUL VL]
ld1d {z6.d}, p0/z, [x10, #2, MUL VL]
incb x2, ALL, MUL #2
add x0,x0,#-1
cbz x0,.ukr7_last
.ukr7_loop:
add x0,x0,#-1
add x10,x1,#8
ld1d {z7.d}, p0/z, [x10, #3, MUL VL]
add x10,x10,#8
ld1d {z16.d}, p0/z, [x10, #4, MUL VL]
ld1d {z17.d}, p0/z, [x10, #5, MUL VL]
add x10,x10,#8
ld1d {z18.d}, p0/z, [x10, #6, MUL VL]
ld1d {z19.d}, p0/z, [x10, #7, MUL VL]
add x10,x10,#-24
incb x10, ALL, MUL #2
ld1rd {z20.d}, p0/z, [x10]
add x10,x10,#8
incb x10, ALL, MUL #2
ld1rd {z21.d}, p0/z, [x10]
add x10,x10,#8
incb x10, ALL, MUL #2
ld1rd {z22.d}, p0/z, [x10]
add x10,x10,#8
incb x10, ALL, MUL #2
ld1rd {z23.d}, p0/z, [x10]
fmopa za0.d,p0/m,p0/m,z4.d,z2.d
fmopa za1.d,p0/m,p0/m,z4.d,z3.d
fmopa za2.d,p0/m,p0/m,z5.d,z2.d
fmopa za3.d,p0/m,p0/m,z5.d,z3.d
add x10,x10,#8
ld1d {z24.d}, p0/z, [x2]
ld1d {z25.d}, p0/z, [x2, #1, MUL VL]
fmla z0.d,p0/m,z2.d,z20.d
fmla z1.d,p0/m,z3.d,z20.d
ld1d {z4.d}, p0/z, [x10]
ld1d {z5.d}, p0/z, [x10, #1, MUL VL]
fmopa za0.d,p0/m,p0/m,z6.d,z24.d
fmopa za1.d,p0/m,p0/m,z6.d,z25.d
fmopa za2.d,p0/m,p0/m,z7.d,z24.d
fmopa za3.d,p0/m,p0/m,z7.d,z25.d
ld1d {z26.d}, p0/z, [x2, #2, MUL VL]
ld1d {z27.d}, p0/z, [x2, #3, MUL VL]
fmla z0.d,p0/m,z24.d,z21.d
fmla z1.d,p0/m,z25.d,z21.d
add x10,x10,#8
fmopa za0.d,p0/m,p0/m,z16.d,z26.d
fmopa za1.d,p0/m,p0/m,z16.d,z27.d
fmopa za2.d,p0/m,p0/m,z17.d,z26.d
fmopa za3.d,p0/m,p0/m,z17.d,z27.d
ld1d {z28.d}, p0/z, [x2, #4, MUL VL]
ld1d {z29.d}, p0/z, [x2, #5, MUL VL]
fmla z0.d,p0/m,z26.d,z22.d
fmla z1.d,p0/m,z27.d,z22.d
incb x10, ALL, MUL #2
ld1d {z2.d}, p0/z, [x2, #6, MUL VL]
ld1d {z3.d}, p0/z, [x2, #7, MUL VL]
add x1,x1,#32
fmopa za0.d,p0/m,p0/m,z18.d,z28.d
fmopa za1.d,p0/m,p0/m,z18.d,z29.d
fmopa za2.d,p0/m,p0/m,z19.d,z28.d
fmopa za3.d,p0/m,p0/m,z19.d,z29.d
fmla z0.d,p0/m,z28.d,z23.d
fmla z1.d,p0/m,z29.d,z23.d
ld1d {z6.d}, p0/z, [x10]
incb x1, ALL, MUL #8
incb x2, ALL, MUL #8
cbnz x0,.ukr7_loop
.ukr7_last:
add x10,x1,#8
ld1d {z7.d}, p0/z, [x10, #3, MUL VL]
add x10,x10,#8
ld1d {z16.d}, p0/z, [x10, #4, MUL VL]
ld1d {z17.d}, p0/z, [x10, #5, MUL VL]
add x10,x10,#8
ld1d {z18.d}, p0/z, [x10, #6, MUL VL]
ld1d {z19.d}, p0/z, [x10, #7, MUL VL]
add x10,x10,#-24
incb x10, ALL, MUL #2
ld1rd {z20.d}, p0/z, [x10]
add x10,x10,#8
incb x10, ALL, MUL #2
ld1rd {z21.d}, p0/z, [x10]
add x10,x10,#8
incb x10, ALL, MUL #2
ld1rd {z22.d}, p0/z, [x10]
fmopa za0.d,p0/m,p0/m,z4.d,z2.d
fmopa za1.d,p0/m,p0/m,z4.d,z3.d
fmopa za2.d,p0/m,p0/m,z5.d,z2.d
fmopa za3.d,p0/m,p0/m,z5.d,z3.d
ld1d {z24.d}, p0/z, [x2]
ld1d {z25.d}, p0/z, [x2, #1, MUL VL]
fmla z0.d,p0/m,z2.d,z20.d
fmla z1.d,p0/m,z3.d,z20.d
add x10,x10,#8
fmopa za0.d,p0/m,p0/m,z6.d,z24.d
fmopa za1.d,p0/m,p0/m,z6.d,z25.d
fmopa za2.d,p0/m,p0/m,z7.d,z24.d
fmopa za3.d,p0/m,p0/m,z7.d,z25.d
ld1d {z26.d}, p0/z, [x2, #2, MUL VL]
ld1d {z27.d}, p0/z, [x2, #3, MUL VL]
fmla z0.d,p0/m,z24.d,z21.d
fmla z1.d,p0/m,z25.d,z21.d
incb x10, ALL, MUL #2
fmopa za0.d,p0/m,p0/m,z16.d,z26.d
fmopa za1.d,p0/m,p0/m,z16.d,z27.d
fmopa za2.d,p0/m,p0/m,z17.d,z26.d
fmopa za3.d,p0/m,p0/m,z17.d,z27.d
ld1d {z28.d}, p0/z, [x2, #4, MUL VL]
ld1d {z29.d}, p0/z, [x2, #5, MUL VL]
fmla z0.d,p0/m,z26.d,z22.d
fmla z1.d,p0/m,z27.d,z22.d
ld1rd {z23.d}, p0/z, [x10]
add x1,x1,#32
fmopa za0.d,p0/m,p0/m,z18.d,z28.d
fmopa za1.d,p0/m,p0/m,z18.d,z29.d
fmopa za2.d,p0/m,p0/m,z19.d,z28.d
fmopa za3.d,p0/m,p0/m,z19.d,z29.d
fmla z0.d,p0/m,z28.d,z23.d
fmla z1.d,p0/m,z29.d,z23.d
incb x1, ALL, MUL #8
incb x2, ALL, MUL #6
.ukr7_done:
cbz x9,.ukr7_taildone
.ukr7_tail:
add x9,x9,#-1
mov x10,x1
incb x10, ALL, MUL #2
ld1d {z4.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x2]
ld1d {z3.d}, p0/z, [x2, #1, MUL VL]
ld1d {z5.d}, p0/z, [x1, #1, MUL VL]
ld1rd {z20.d}, p0/z, [x10]
fmopa za0.d,p0/m,p0/m,z4.d,z2.d
fmopa za1.d,p0/m,p0/m,z4.d,z3.d
fmopa za2.d,p0/m,p0/m,z5.d,z2.d
fmopa za3.d,p0/m,p0/m,z5.d,z3.d
fmla z0.d,p0/m,z2.d,z20.d
fmla z1.d,p0/m,z3.d,z20.d
add x1,x1,#8
incb x1, ALL, MUL #2
incb x2, ALL, MUL #2
cbnz x9,.ukr7_tail
.ukr7_taildone:
ldr d2, [x5]
fmov d3,xzr
fcmp d2,d3
b.ne .ukr0_try0
ldr d2, [x4]
mov x0,#4607182418800017408
fmov d3,x0
fcmp d2,d3
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
b .ukr0_case1
.ukr0_try0:
ldr d2, [x5]
mov x0,#4607182418800017408
fmov d3,x0
fcmp d2,d3
b.ne .ukr0_try2
ldr d2, [x4]
mov x0,#4607182418800017408
fmov d3,x0
fcmp d2,d3
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
b .ukr0_case3
.ukr0_try2:
ldr d2, [x4]
mov x0,#4607182418800017408
fmov d3,x0
fcmp d2,d3
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
add x11,x0,x8
add x1,x1,x8
mov x16,x7
mov x12,#0
incb x10, ALL, MUL #1
add x17,x0,x8
add x2,x2,x8
add x19,x0,x6
add x9,x9,x6
add x11,x11,x6
add x1,x1,x6
.ukr1_slices:
add x16,x16,#-2
st1d {za0h.d[w12, 0]}, p0, [x0]
st1d {za1h.d[w12, 0]}, p0, [x10]
st1d {za2h.d[w12, 0]}, p0, [x17]
st1d {za3h.d[w12, 0]}, p0, [x2]
st1d {za0h.d[w12, 1]}, p0, [x19]
st1d {za1h.d[w12, 1]}, p0, [x9]
st1d {za2h.d[w12, 1]}, p0, [x11]
st1d {za3h.d[w12, 1]}, p0, [x1]
add x0,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x17,x17,x6, LSL #1
add x2,x2,x6, LSL #1
add x19,x19,x6, LSL #1
add x9,x9,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x16,.ukr1_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
st1d {z0.d}, p0, [x0]
st1d {z1.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
add x1,x0,x8
ld1rd {z2.d}, p0/z, [x4]
mov x2,x7
mov x12,#0
add x9,x0,x8
add x10,x0,x6
add x1,x1,x6
.ukr2_slices:
add x2,x2,#-2
mova z3.d,p0/m,za0h.d[w12,0]
mova z4.d,p0/m,za1h.d[w12,0]
mova z5.d,p0/m,za2h.d[w12,0]
mova z6.d,p0/m,za3h.d[w12,0]
mova z7.d,p0/m,za0h.d[w12,1]
mova z16.d,p0/m,za1h.d[w12,1]
mova z17.d,p0/m,za2h.d[w12,1]
mova z18.d,p0/m,za3h.d[w12,1]
fmul z19.d,z3.d,z2.d
fmul z20.d,z4.d,z2.d
fmul z21.d,z5.d,z2.d
fmul z22.d,z6.d,z2.d
fmul z23.d,z7.d,z2.d
fmul z24.d,z16.d,z2.d
fmul z25.d,z17.d,z2.d
fmul z26.d,z18.d,z2.d
st1d {z19.d}, p0, [x0]
st1d {z20.d}, p0, [x0, #1, MUL VL]
st1d {z21.d}, p0, [x9]
st1d {z22.d}, p0, [x9, #1, MUL VL]
st1d {z23.d}, p0, [x10]
st1d {z24.d}, p0, [x10, #1, MUL VL]
st1d {z25.d}, p0, [x1]
st1d {z26.d}, p0, [x1, #1, MUL VL]
add x0,x0,x6, LSL #1
add x9,x9,x6, LSL #1
add x10,x10,x6, LSL #1
add x1,x1,x6, LSL #1
add x12,x12,#2
cbnz x2,.ukr2_slices
sub x0,x0,x8
fmul z3.d,z0.d,z2.d
add x0,x0,x8, LSL #1
fmul z0.d,z1.d,z2.d
st1d {z3.d}, p0, [x0]
st1d {z0.d}, p0, [x0, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
mov x9,x7
mov x12,#0
add x10,x0,x8
add x11,x0,x6
add x1,x1,x6
add x16,x3,x8
add x17,x3,x6
add x2,x2,x6
.ukr3_slices:
add x9,x9,#-2
mova z2.d,p0/m,za0h.d[w12,0]
ld1d {z3.d}, p0/z, [x0]
mova z4.d,p0/m,za1h.d[w12,0]
ld1d {z5.d}, p0/z, [x0, #1, MUL VL]
mova z6.d,p0/m,za2h.d[w12,0]
ld1d {z7.d}, p0/z, [x10]
mova z16.d,p0/m,za3h.d[w12,0]
ld1d {z17.d}, p0/z, [x10, #1, MUL VL]
mova z18.d,p0/m,za0h.d[w12,1]
ld1d {z19.d}, p0/z, [x11]
mova z20.d,p0/m,za1h.d[w12,1]
ld1d {z21.d}, p0/z, [x11, #1, MUL VL]
mova z22.d,p0/m,za2h.d[w12,1]
ld1d {z23.d}, p0/z, [x1]
mova z24.d,p0/m,za3h.d[w12,1]
ld1d {z25.d}, p0/z, [x1, #1, MUL VL]
fadd z3.d,z2.d,z3.d
fadd z5.d,z4.d,z5.d
fadd z7.d,z6.d,z7.d
fadd z17.d,z16.d,z17.d
fadd z19.d,z18.d,z19.d
fadd z21.d,z20.d,z21.d
fadd z23.d,z22.d,z23.d
fadd z25.d,z24.d,z25.d
st1d {z3.d}, p0, [x3]
st1d {z5.d}, p0, [x3, #1, MUL VL]
st1d {z7.d}, p0, [x16]
st1d {z17.d}, p0, [x16, #1, MUL VL]
st1d {z19.d}, p0, [x17]
st1d {z21.d}, p0, [x17, #1, MUL VL]
st1d {z23.d}, p0, [x2]
st1d {z25.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x16,x16,x6, LSL #1
add x17,x17,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x9,.ukr3_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
sub x3,x3,x8
ld1d {z2.d}, p0/z, [x0]
ld1d {z3.d}, p0/z, [x0, #1, MUL VL]
fadd z2.d,z0.d,z2.d
mov x3,x0
fadd z3.d,z1.d,z3.d
st1d {z2.d}, p0, [x3]
st1d {z3.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z2.d}, p0/z, [x4]
mov x9,x7
mov x12,#0
add x10,x0,x8
add x11,x0,x6
add x1,x1,x6
add x16,x3,x8
add x17,x3,x6
add x2,x2,x6
.ukr4_slices:
add x9,x9,#-2
mova z3.d,p0/m,za0h.d[w12,0]
ld1d {z4.d}, p0/z, [x0]
mova z5.d,p0/m,za1h.d[w12,0]
ld1d {z6.d}, p0/z, [x0, #1, MUL VL]
mova z7.d,p0/m,za2h.d[w12,0]
ld1d {z16.d}, p0/z, [x10]
mova z17.d,p0/m,za3h.d[w12,0]
ld1d {z18.d}, p0/z, [x10, #1, MUL VL]
mova z19.d,p0/m,za0h.d[w12,1]
ld1d {z20.d}, p0/z, [x11]
mova z21.d,p0/m,za1h.d[w12,1]
ld1d {z22.d}, p0/z, [x11, #1, MUL VL]
mova z23.d,p0/m,za2h.d[w12,1]
ld1d {z24.d}, p0/z, [x1]
mova z25.d,p0/m,za3h.d[w12,1]
ld1d {z26.d}, p0/z, [x1, #1, MUL VL]
fmla z4.d,p0/m,z3.d,z2.d
fmla z6.d,p0/m,z5.d,z2.d
fmla z16.d,p0/m,z7.d,z2.d
fmla z18.d,p0/m,z17.d,z2.d
fmla z20.d,p0/m,z19.d,z2.d
fmla z22.d,p0/m,z21.d,z2.d
fmla z24.d,p0/m,z23.d,z2.d
fmla z26.d,p0/m,z25.d,z2.d
st1d {z4.d}, p0, [x3]
st1d {z6.d}, p0, [x3, #1, MUL VL]
st1d {z16.d}, p0, [x16]
st1d {z18.d}, p0, [x16, #1, MUL VL]
st1d {z20.d}, p0, [x17]
st1d {z22.d}, p0, [x17, #1, MUL VL]
st1d {z24.d}, p0, [x2]
st1d {z26.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x16,x16,x6, LSL #1
add x17,x17,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x9,.ukr4_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
sub x3,x3,x8
ld1d {z3.d}, p0/z, [x0]
ld1d {z4.d}, p0/z, [x0, #1, MUL VL]
fmla z3.d,p0/m,z0.d,z2.d
mov x3,x0
fmla z4.d,p0/m,z1.d,z2.d
st1d {z3.d}, p0, [x3]
st1d {z4.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z2.d}, p0/z, [x5]
mov x9,x7
mov x12,#0
add x10,x0,x8
add x11,x0,x6
add x1,x1,x6
add x16,x3,x8
add x17,x3,x6
add x2,x2,x6
.ukr5_slices:
add x9,x9,#-2
mova z3.d,p0/m,za0h.d[w12,0]
ld1d {z4.d}, p0/z, [x0]
mova z5.d,p0/m,za1h.d[w12,0]
ld1d {z6.d}, p0/z, [x0, #1, MUL VL]
mova z7.d,p0/m,za2h.d[w12,0]
ld1d {z16.d}, p0/z, [x10]
mova z17.d,p0/m,za3h.d[w12,0]
ld1d {z18.d}, p0/z, [x10, #1, MUL VL]
fmla z3.d,p0/m,z4.d,z2.d
fmla z5.d,p0/m,z6.d,z2.d
fmla z7.d,p0/m,z16.d,z2.d
fmla z17.d,p0/m,z18.d,z2.d
mova za0h.d[w12,0],p0/m,z3.d
mova za1h.d[w12,0],p0/m,z5.d
mova za2h.d[w12,0],p0/m,z7.d
mova za3h.d[w12,0],p0/m,z17.d
mova z19.d,p0/m,za0h.d[w12,1]
ld1d {z20.d}, p0/z, [x11]
mova z21.d,p0/m,za1h.d[w12,1]
ld1d {z22.d}, p0/z, [x11, #1, MUL VL]
mova z23.d,p0/m,za2h.d[w12,1]
ld1d {z24.d}, p0/z, [x1]
mova z25.d,p0/m,za3h.d[w12,1]
ld1d {z26.d}, p0/z, [x1, #1, MUL VL]
fmla z19.d,p0/m,z20.d,z2.d
fmla z21.d,p0/m,z22.d,z2.d
fmla z23.d,p0/m,z24.d,z2.d
fmla z25.d,p0/m,z26.d,z2.d
st1d {z3.d}, p0, [x3]
st1d {z5.d}, p0, [x3, #1, MUL VL]
st1d {z7.d}, p0, [x16]
st1d {z17.d}, p0, [x16, #1, MUL VL]
st1d {z19.d}, p0, [x17]
st1d {z21.d}, p0, [x17, #1, MUL VL]
st1d {z23.d}, p0, [x2]
st1d {z25.d}, p0, [x2, #1, MUL VL]
mova za0h.d[w12,1],p0/m,z19.d
mova za1h.d[w12,1],p0/m,z21.d
mova za2h.d[w12,1],p0/m,z23.d
mova za3h.d[w12,1],p0/m,z25.d
add x0,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x16,x16,x6, LSL #1
add x17,x17,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x9,.ukr5_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
sub x3,x3,x8
ld1d {z3.d}, p0/z, [x0]
ld1d {z4.d}, p0/z, [x0, #1, MUL VL]
fmla z0.d,p0/m,z3.d,z2.d
mov x3,x0
fmla z1.d,p0/m,z4.d,z2.d
st1d {z0.d}, p0, [x3]
st1d {z1.d}, p0, [x3, #1, MUL VL]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
add x1,x0,x8
add x2,x3,x8
ld1rd {z2.d}, p0/z, [x5]
ld1rd {z3.d}, p0/z, [x4]
mov x9,x7
mov x12,#0
add x10,x0,x8
add x11,x0,x6
add x1,x1,x6
add x16,x3,x8
add x17,x3,x6
add x2,x2,x6
.ukr6_slices:
add x9,x9,#-2
ld1d {z4.d}, p0/z, [x0]
ld1d {z5.d}, p0/z, [x0, #1, MUL VL]
ld1d {z6.d}, p0/z, [x10]
ld1d {z7.d}, p0/z, [x10, #1, MUL VL]
ld1d {z16.d}, p0/z, [x11]
ld1d {z17.d}, p0/z, [x11, #1, MUL VL]
ld1d {z18.d}, p0/z, [x1]
ld1d {z19.d}, p0/z, [x1, #1, MUL VL]
fmul z4.d,z4.d,z2.d
mova z20.d,p0/m,za0h.d[w12,0]
fmul z5.d,z5.d,z2.d
mova z21.d,p0/m,za1h.d[w12,0]
fmul z6.d,z6.d,z2.d
mova z22.d,p0/m,za2h.d[w12,0]
fmul z7.d,z7.d,z2.d
mova z23.d,p0/m,za3h.d[w12,0]
fmul z16.d,z16.d,z2.d
mova z24.d,p0/m,za0h.d[w12,1]
fmul z17.d,z17.d,z2.d
mova z25.d,p0/m,za1h.d[w12,1]
fmul z18.d,z18.d,z2.d
mova z26.d,p0/m,za2h.d[w12,1]
fmul z19.d,z19.d,z2.d
mova z27.d,p0/m,za3h.d[w12,1]
fmla z4.d,p0/m,z20.d,z3.d
fmla z5.d,p0/m,z21.d,z3.d
fmla z6.d,p0/m,z22.d,z3.d
fmla z7.d,p0/m,z23.d,z3.d
fmla z16.d,p0/m,z24.d,z3.d
fmla z17.d,p0/m,z25.d,z3.d
fmla z18.d,p0/m,z26.d,z3.d
fmla z19.d,p0/m,z27.d,z3.d
st1d {z4.d}, p0, [x3]
st1d {z5.d}, p0, [x3, #1, MUL VL]
st1d {z6.d}, p0, [x16]
st1d {z7.d}, p0, [x16, #1, MUL VL]
st1d {z16.d}, p0, [x17]
st1d {z17.d}, p0, [x17, #1, MUL VL]
st1d {z18.d}, p0, [x2]
st1d {z19.d}, p0, [x2, #1, MUL VL]
add x0,x0,x6, LSL #1
add x10,x10,x6, LSL #1
add x11,x11,x6, LSL #1
add x1,x1,x6, LSL #1
add x3,x3,x6, LSL #1
add x16,x16,x6, LSL #1
add x17,x17,x6, LSL #1
add x2,x2,x6, LSL #1
add x12,x12,#2
cbnz x9,.ukr6_slices
sub x0,x0,x8
add x0,x0,x8, LSL #1
ld1d {z4.d}, p0/z, [x0]
ld1d {z5.d}, p0/z, [x0, #1, MUL VL]
sub x3,x3,x8
fmul z4.d,z4.d,z2.d
fmul z5.d,z5.d,z2.d
fmla z4.d,p0/m,z0.d,z3.d
mov x3,x0
fmla z5.d,p0/m,z1.d,z3.d
st1d {z4.d}, p0, [x3]
st1d {z5.d}, p0, [x3, #1, MUL VL]
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
.size bli_dgemm_ukrgen_sme_sf_2vx2v_1x2v_asm, .-bli_dgemm_ukrgen_sme_sf_2vx2v_1x2v_asm
.section .note.GNU-stack,"",%progbits
