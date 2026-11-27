### bli_dpackm_ukrgen_sme_pk_ztrans1v
.text
.global bli_dpackm_ukrgen_sme_pk_ztrans1v_asm
.type bli_dpackm_ukrgen_sme_pk_ztrans1v_asm, %function
bli_dpackm_ukrgen_sme_pk_ztrans1v_asm:
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
# x0 = n
# x1 = base(X)
# x2 = base(Y)
# x3 = base(kappa)
# x4 = stride(X,m)
smstart
ptrue p0.d
cntd x5
mul x6,x5,x5
lsl x6,x6,#3
mul x7,x5,x4
ldr d0, [x3]
mov x8,#4607182418800017408
fmov d1,x8
fcmp d0,d1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
and x8,x0,#7
lsr x0,x0,#3
cbz x0,.ukr15_done
mov x9,x5
mov x12,#0
.ukr1_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr15_last
.ukr15_loop:
add x0,x0,#-1
incb x1, ALL, MUL #1
mov x9,x5
mov x12,#0
.ukr2_slices:
add x9,x9,#-1
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za6h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za7h.d[w12, 0]}, p0/z, [x1]
decb x1, ALL, MUL #6
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr2_slices
sub x1,x1,x7
mov x9,x5
mov x12,#0
.ukr3_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za1v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za2v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za3v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za4v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za5v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za6v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr3_slices
incb x1, ALL, MUL #7
mov x9,x5
mov x12,#0
.ukr4_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr4_slices
sub x2,x2,x6
sub x1,x1,x7
add x2,x2,x6, LSL #3
cbnz x0,.ukr15_loop
.ukr15_last:
incb x1, ALL, MUL #1
mov x9,x5
mov x12,#0
.ukr5_slices:
add x9,x9,#-1
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za6h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
ld1d {za7h.d[w12, 0]}, p0/z, [x1]
decb x1, ALL, MUL #6
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr5_slices
mov x9,x5
mov x12,#0
.ukr6_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za1v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za2v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za3v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za4v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za5v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za6v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr6_slices
sub x1,x1,x7
sub x2,x2,x6
incb x1, ALL, MUL #7
add x2,x2,x6, LSL #3
.ukr15_done:
cbz x8,.ukr15_taildone
.ukr15_tail:
add x8,x8,#-1
mov x9,x5
mov x12,#0
.ukr7_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr7_slices
mov x9,x5
mov x12,#0
.ukr8_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x9,.ukr8_slices
sub x1,x1,x7
sub x2,x2,x6
incb x1, ALL, MUL #1
add x2,x2,x6
cbnz x8,.ukr15_tail
.ukr15_taildone:
b .ukr0_cases_end
.ukr0_case1:
and x8,x0,#7
lsr x0,x0,#3
ld1rd {z0.d}, p0/z, [x3]
cbz x0,.ukr16_done
add x0,x0,#-1
cbz x0,.ukr16_last
.ukr16_loop:
add x0,x0,#-1
mov x9,x5
mov x12,#0
.ukr9_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x1, #1, MUL VL]
ld1d {z3.d}, p0/z, [x1, #2, MUL VL]
ld1d {z4.d}, p0/z, [x1, #3, MUL VL]
ld1d {z5.d}, p0/z, [x1, #4, MUL VL]
ld1d {z6.d}, p0/z, [x1, #5, MUL VL]
ld1d {z7.d}, p0/z, [x1, #6, MUL VL]
ld1d {z16.d}, p0/z, [x1, #7, MUL VL]
fmul z17.d,z1.d,z0.d
fmul z18.d,z2.d,z0.d
fmul z19.d,z3.d,z0.d
fmul z20.d,z4.d,z0.d
fmul z21.d,z5.d,z0.d
fmul z22.d,z6.d,z0.d
fmul z23.d,z7.d,z0.d
fmul z24.d,z16.d,z0.d
mova za0h.d[w12,0],p0/m,z17.d
mova za1h.d[w12,0],p0/m,z18.d
mova za2h.d[w12,0],p0/m,z19.d
mova za3h.d[w12,0],p0/m,z20.d
mova za4h.d[w12,0],p0/m,z21.d
mova za5h.d[w12,0],p0/m,z22.d
mova za6h.d[w12,0],p0/m,z23.d
mova za7h.d[w12,0],p0/m,z24.d
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr9_slices
mov x9,x5
mov x12,#0
.ukr10_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za1v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za2v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za3v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za4v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za5v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za6v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr10_slices
sub x1,x1,x7
sub x2,x2,x6
incb x1, ALL, MUL #8
add x2,x2,x6, LSL #3
cbnz x0,.ukr16_loop
.ukr16_last:
mov x9,x5
mov x12,#0
.ukr11_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x1, #1, MUL VL]
ld1d {z3.d}, p0/z, [x1, #2, MUL VL]
ld1d {z4.d}, p0/z, [x1, #3, MUL VL]
ld1d {z5.d}, p0/z, [x1, #4, MUL VL]
ld1d {z6.d}, p0/z, [x1, #5, MUL VL]
ld1d {z7.d}, p0/z, [x1, #6, MUL VL]
ld1d {z16.d}, p0/z, [x1, #7, MUL VL]
fmul z17.d,z1.d,z0.d
fmul z18.d,z2.d,z0.d
fmul z19.d,z3.d,z0.d
fmul z20.d,z4.d,z0.d
fmul z21.d,z5.d,z0.d
fmul z22.d,z6.d,z0.d
fmul z23.d,z7.d,z0.d
fmul z24.d,z16.d,z0.d
mova za0h.d[w12,0],p0/m,z17.d
mova za1h.d[w12,0],p0/m,z18.d
mova za2h.d[w12,0],p0/m,z19.d
mova za3h.d[w12,0],p0/m,z20.d
mova za4h.d[w12,0],p0/m,z21.d
mova za5h.d[w12,0],p0/m,z22.d
mova za6h.d[w12,0],p0/m,z23.d
mova za7h.d[w12,0],p0/m,z24.d
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr11_slices
mov x9,x5
mov x12,#0
.ukr12_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za1v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za2v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za3v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za4v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za5v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za6v.d[w12, 0]}, p0, [x2]
add x2,x2,x6
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr12_slices
sub x1,x1,x7
sub x2,x2,x6
incb x1, ALL, MUL #8
add x2,x2,x6, LSL #3
.ukr16_done:
cbz x8,.ukr16_taildone
.ukr16_tail:
add x8,x8,#-1
mov x9,x5
mov x12,#0
.ukr13_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
fmul z2.d,z1.d,z0.d
mova za0h.d[w12,0],p0/m,z2.d
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr13_slices
mov x9,x5
mov x12,#0
.ukr14_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x9,.ukr14_slices
sub x1,x1,x7
sub x2,x2,x6
incb x1, ALL, MUL #1
add x2,x2,x6
cbnz x8,.ukr16_tail
.ukr16_taildone:
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
.size bli_dpackm_ukrgen_sme_pk_ztrans1v_asm, .-bli_dpackm_ukrgen_sme_pk_ztrans1v_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_sme_pk_ztrans2v
.text
.global bli_dpackm_ukrgen_sme_pk_ztrans2v_asm
.type bli_dpackm_ukrgen_sme_pk_ztrans2v_asm, %function
bli_dpackm_ukrgen_sme_pk_ztrans2v_asm:
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
# x0 = n
# x1 = base(X)
# x2 = base(Y)
# x3 = base(kappa)
# x4 = stride(X,m)
smstart
ptrue p0.d
cntd x5
mul x6,x5,x5
lsl x6,x6,#3
mul x7,x5,x4
ldr d0, [x3]
mov x8,#4607182418800017408
fmov d1,x8
fcmp d0,d1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
and x8,x0,#3
lsr x0,x0,#2
cbz x0,.ukr15_done
mov x9,x5
mov x12,#0
.ukr1_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr15_last
.ukr15_loop:
add x0,x0,#-1
incb x1, ALL, MUL #1
mov x9,x5
mov x12,#0
.ukr2_slices:
add x9,x9,#-1
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
sub x1,x1,x7
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
sub x1,x1,x7
ld1d {za6h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za7h.d[w12, 0]}, p0/z, [x1]
decb x1, ALL, MUL #2
sub x1,x1,x7
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr2_slices
sub x1,x1,x7
mov x9,x5
mov x12,#0
.ukr3_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr3_slices
incb x1, ALL, MUL #3
mov x9,x5
mov x12,#0
.ukr4_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr4_slices
sub x2,x2,x6, LSL #1
sub x1,x1,x7
add x2,x2,x6, LSL #3
cbnz x0,.ukr15_loop
.ukr15_last:
incb x1, ALL, MUL #1
mov x9,x5
mov x12,#0
.ukr5_slices:
add x9,x9,#-1
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
sub x1,x1,x7
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
incb x1, ALL, MUL #1
sub x1,x1,x7
ld1d {za6h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za7h.d[w12, 0]}, p0/z, [x1]
decb x1, ALL, MUL #2
sub x1,x1,x7
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr5_slices
mov x9,x5
mov x12,#0
.ukr6_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr6_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #1
incb x1, ALL, MUL #3
add x2,x2,x6, LSL #3
.ukr15_done:
cbz x8,.ukr15_taildone
.ukr15_tail:
add x8,x8,#-1
mov x9,x5
mov x12,#0
.ukr7_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr7_slices
mov x9,x5
mov x12,#0
.ukr8_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x9,.ukr8_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #1
incb x1, ALL, MUL #1
add x2,x2,x6, LSL #1
cbnz x8,.ukr15_tail
.ukr15_taildone:
b .ukr0_cases_end
.ukr0_case1:
and x8,x0,#3
lsr x0,x0,#2
ld1rd {z0.d}, p0/z, [x3]
cbz x0,.ukr16_done
add x0,x0,#-1
cbz x0,.ukr16_last
.ukr16_loop:
add x0,x0,#-1
mov x9,x5
mov x12,#0
.ukr9_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
sub x1,x1,x7
ld1d {z3.d}, p0/z, [x1, #1, MUL VL]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1, #1, MUL VL]
sub x1,x1,x7
ld1d {z5.d}, p0/z, [x1, #2, MUL VL]
add x1,x1,x7
ld1d {z6.d}, p0/z, [x1, #2, MUL VL]
sub x1,x1,x7
ld1d {z7.d}, p0/z, [x1, #3, MUL VL]
add x1,x1,x7
ld1d {z16.d}, p0/z, [x1, #3, MUL VL]
fmul z17.d,z1.d,z0.d
fmul z18.d,z2.d,z0.d
fmul z19.d,z3.d,z0.d
fmul z20.d,z4.d,z0.d
fmul z21.d,z5.d,z0.d
fmul z22.d,z6.d,z0.d
fmul z23.d,z7.d,z0.d
fmul z24.d,z16.d,z0.d
sub x1,x1,x7
mova za0h.d[w12,0],p0/m,z17.d
mova za1h.d[w12,0],p0/m,z18.d
mova za2h.d[w12,0],p0/m,z19.d
mova za3h.d[w12,0],p0/m,z20.d
mova za4h.d[w12,0],p0/m,z21.d
mova za5h.d[w12,0],p0/m,z22.d
mova za6h.d[w12,0],p0/m,z23.d
mova za7h.d[w12,0],p0/m,z24.d
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr9_slices
mov x9,x5
mov x12,#0
.ukr10_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr10_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #1
incb x1, ALL, MUL #4
add x2,x2,x6, LSL #3
cbnz x0,.ukr16_loop
.ukr16_last:
mov x9,x5
mov x12,#0
.ukr11_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
sub x1,x1,x7
ld1d {z3.d}, p0/z, [x1, #1, MUL VL]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1, #1, MUL VL]
sub x1,x1,x7
ld1d {z5.d}, p0/z, [x1, #2, MUL VL]
add x1,x1,x7
ld1d {z6.d}, p0/z, [x1, #2, MUL VL]
sub x1,x1,x7
ld1d {z7.d}, p0/z, [x1, #3, MUL VL]
add x1,x1,x7
ld1d {z16.d}, p0/z, [x1, #3, MUL VL]
fmul z17.d,z1.d,z0.d
fmul z18.d,z2.d,z0.d
fmul z19.d,z3.d,z0.d
fmul z20.d,z4.d,z0.d
fmul z21.d,z5.d,z0.d
fmul z22.d,z6.d,z0.d
fmul z23.d,z7.d,z0.d
fmul z24.d,z16.d,z0.d
sub x1,x1,x7
mova za0h.d[w12,0],p0/m,z17.d
mova za1h.d[w12,0],p0/m,z18.d
mova za2h.d[w12,0],p0/m,z19.d
mova za3h.d[w12,0],p0/m,z20.d
mova za4h.d[w12,0],p0/m,z21.d
mova za5h.d[w12,0],p0/m,z22.d
mova za6h.d[w12,0],p0/m,z23.d
mova za7h.d[w12,0],p0/m,z24.d
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr11_slices
mov x9,x5
mov x12,#0
.ukr12_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #1
add x2,x2,x6, LSL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr12_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #1
incb x1, ALL, MUL #4
add x2,x2,x6, LSL #3
.ukr16_done:
cbz x8,.ukr16_taildone
.ukr16_tail:
add x8,x8,#-1
mov x9,x5
mov x12,#0
.ukr13_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
fmul z3.d,z1.d,z0.d
fmul z4.d,z2.d,z0.d
sub x1,x1,x7
mova za0h.d[w12,0],p0/m,z3.d
mova za1h.d[w12,0],p0/m,z4.d
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr13_slices
mov x9,x5
mov x12,#0
.ukr14_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x9,.ukr14_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #1
incb x1, ALL, MUL #1
add x2,x2,x6, LSL #1
cbnz x8,.ukr16_tail
.ukr16_taildone:
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
.size bli_dpackm_ukrgen_sme_pk_ztrans2v_asm, .-bli_dpackm_ukrgen_sme_pk_ztrans2v_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_sme_pk_ztrans3v
.text
.global bli_dpackm_ukrgen_sme_pk_ztrans3v_asm
.type bli_dpackm_ukrgen_sme_pk_ztrans3v_asm, %function
bli_dpackm_ukrgen_sme_pk_ztrans3v_asm:
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
# x0 = n
# x1 = base(X)
# x2 = base(Y)
# x3 = base(kappa)
# x4 = stride(X,m)
smstart
ptrue p0.d
cntd x5
mul x6,x5,x5
lsl x6,x6,#3
mul x7,x5,x4
ldr d0, [x3]
mov x8,#4607182418800017408
fmov d1,x8
fcmp d0,d1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
cbz x0,.ukr9_done
mov x8,x5
mov x12,#0
.ukr1_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7, LSL #1
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr9_last
.ukr9_loop:
add x0,x0,#-1
mov x8,x5
mov x12,#0
.ukr2_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr2_slices
sub x2,x2,x6
incb x1, ALL, MUL #1
mov x8,x5
mov x12,#0
sub x2,x2,x6, LSL #1
.ukr3_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7, LSL #1
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr3_slices
sub x1,x1,x7
add x2,x2,x6
add x2,x2,x6, LSL #1
cbnz x0,.ukr9_loop
.ukr9_last:
mov x8,x5
mov x12,#0
.ukr4_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr4_slices
sub x2,x2,x6
sub x2,x2,x6, LSL #1
.ukr9_done:
b .ukr0_cases_end
.ukr0_case1:
ld1rd {z0.d}, p0/z, [x3]
cbz x0,.ukr10_done
add x0,x0,#-1
cbz x0,.ukr10_last
.ukr10_loop:
add x0,x0,#-1
mov x8,x5
mov x12,#0
.ukr5_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
fmul z4.d,z1.d,z0.d
fmul z5.d,z2.d,z0.d
fmul z6.d,z3.d,z0.d
sub x1,x1,x7, LSL #1
mova za0h.d[w12,0],p0/m,z4.d
mova za1h.d[w12,0],p0/m,z5.d
mova za2h.d[w12,0],p0/m,z6.d
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr5_slices
mov x8,x5
mov x12,#0
.ukr6_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr6_slices
sub x2,x2,x6
sub x2,x2,x6, LSL #1
sub x1,x1,x7
add x2,x2,x6
incb x1, ALL, MUL #1
add x2,x2,x6, LSL #1
cbnz x0,.ukr10_loop
.ukr10_last:
mov x8,x5
mov x12,#0
.ukr7_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
fmul z4.d,z1.d,z0.d
fmul z5.d,z2.d,z0.d
fmul z6.d,z3.d,z0.d
sub x1,x1,x7, LSL #1
mova za0h.d[w12,0],p0/m,z4.d
mova za1h.d[w12,0],p0/m,z5.d
mova za2h.d[w12,0],p0/m,z6.d
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr7_slices
mov x8,x5
mov x12,#0
.ukr8_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr8_slices
sub x2,x2,x6
sub x1,x1,x7
sub x2,x2,x6, LSL #1
.ukr10_done:
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
.size bli_dpackm_ukrgen_sme_pk_ztrans3v_asm, .-bli_dpackm_ukrgen_sme_pk_ztrans3v_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_sme_pk_ztrans4v
.text
.global bli_dpackm_ukrgen_sme_pk_ztrans4v_asm
.type bli_dpackm_ukrgen_sme_pk_ztrans4v_asm, %function
bli_dpackm_ukrgen_sme_pk_ztrans4v_asm:
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
# x0 = n
# x1 = base(X)
# x2 = base(Y)
# x3 = base(kappa)
# x4 = stride(X,m)
smstart
ptrue p0.d
cntd x5
mul x6,x5,x5
lsl x6,x6,#3
mul x7,x5,x4
ldr d0, [x3]
mov x8,#4607182418800017408
fmov d1,x8
fcmp d0,d1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
and x8,x0,#1
lsr x0,x0,#1
cbz x0,.ukr15_done
mov x9,x5
mov x12,#0
.ukr1_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #1
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr15_last
.ukr15_loop:
add x0,x0,#-1
incb x1, ALL, MUL #1
mov x9,x5
mov x12,#0
.ukr2_slices:
add x9,x9,#-1
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za6h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za7h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #1
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr2_slices
sub x1,x1,x7
mov x9,x5
mov x12,#0
.ukr3_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #3
add x2,x2,x6, LSL #2
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr3_slices
incb x1, ALL, MUL #1
mov x9,x5
mov x12,#0
.ukr4_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #1
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr4_slices
sub x2,x2,x6, LSL #2
sub x1,x1,x7
add x2,x2,x6, LSL #3
cbnz x0,.ukr15_loop
.ukr15_last:
incb x1, ALL, MUL #1
mov x9,x5
mov x12,#0
.ukr5_slices:
add x9,x9,#-1
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za6h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za7h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #1
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr5_slices
mov x9,x5
mov x12,#0
.ukr6_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #3
add x2,x2,x6, LSL #2
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr6_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #2
incb x1, ALL, MUL #1
add x2,x2,x6, LSL #3
.ukr15_done:
cbz x8,.ukr15_taildone
.ukr15_tail:
add x8,x8,#-1
mov x9,x5
mov x12,#0
.ukr7_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #1
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr7_slices
mov x9,x5
mov x12,#0
.ukr8_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x9,.ukr8_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #2
incb x1, ALL, MUL #1
add x2,x2,x6, LSL #2
cbnz x8,.ukr15_tail
.ukr15_taildone:
b .ukr0_cases_end
.ukr0_case1:
and x8,x0,#1
lsr x0,x0,#1
ld1rd {z0.d}, p0/z, [x3]
cbz x0,.ukr16_done
add x0,x0,#-1
cbz x0,.ukr16_last
.ukr16_loop:
add x0,x0,#-1
mov x9,x5
mov x12,#0
.ukr9_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #1
ld1d {z5.d}, p0/z, [x1, #1, MUL VL]
add x1,x1,x7
ld1d {z6.d}, p0/z, [x1, #1, MUL VL]
add x1,x1,x7
ld1d {z7.d}, p0/z, [x1, #1, MUL VL]
add x1,x1,x7
ld1d {z16.d}, p0/z, [x1, #1, MUL VL]
sub x1,x1,x7
fmul z17.d,z1.d,z0.d
fmul z18.d,z2.d,z0.d
fmul z19.d,z3.d,z0.d
fmul z20.d,z4.d,z0.d
fmul z21.d,z5.d,z0.d
fmul z22.d,z6.d,z0.d
fmul z23.d,z7.d,z0.d
fmul z24.d,z16.d,z0.d
sub x1,x1,x7, LSL #1
mova za0h.d[w12,0],p0/m,z17.d
mova za1h.d[w12,0],p0/m,z18.d
mova za2h.d[w12,0],p0/m,z19.d
mova za3h.d[w12,0],p0/m,z20.d
mova za4h.d[w12,0],p0/m,z21.d
mova za5h.d[w12,0],p0/m,z22.d
mova za6h.d[w12,0],p0/m,z23.d
mova za7h.d[w12,0],p0/m,z24.d
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr9_slices
mov x9,x5
mov x12,#0
.ukr10_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #3
add x2,x2,x6, LSL #2
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr10_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #2
incb x1, ALL, MUL #2
add x2,x2,x6, LSL #3
cbnz x0,.ukr16_loop
.ukr16_last:
mov x9,x5
mov x12,#0
.ukr11_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #1
ld1d {z5.d}, p0/z, [x1, #1, MUL VL]
add x1,x1,x7
ld1d {z6.d}, p0/z, [x1, #1, MUL VL]
add x1,x1,x7
ld1d {z7.d}, p0/z, [x1, #1, MUL VL]
add x1,x1,x7
ld1d {z16.d}, p0/z, [x1, #1, MUL VL]
sub x1,x1,x7
fmul z17.d,z1.d,z0.d
fmul z18.d,z2.d,z0.d
fmul z19.d,z3.d,z0.d
fmul z20.d,z4.d,z0.d
fmul z21.d,z5.d,z0.d
fmul z22.d,z6.d,z0.d
fmul z23.d,z7.d,z0.d
fmul z24.d,z16.d,z0.d
sub x1,x1,x7, LSL #1
mova za0h.d[w12,0],p0/m,z17.d
mova za1h.d[w12,0],p0/m,z18.d
mova za2h.d[w12,0],p0/m,z19.d
mova za3h.d[w12,0],p0/m,z20.d
mova za4h.d[w12,0],p0/m,z21.d
mova za5h.d[w12,0],p0/m,z22.d
mova za6h.d[w12,0],p0/m,z23.d
mova za7h.d[w12,0],p0/m,z24.d
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr11_slices
mov x9,x5
mov x12,#0
.ukr12_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
decb x2, ALL, MUL #3
add x2,x2,x6, LSL #2
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
sub x2,x2,x6, LSL #2
add x12,x12,#1
cbnz x9,.ukr12_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #2
incb x1, ALL, MUL #2
add x2,x2,x6, LSL #3
.ukr16_done:
cbz x8,.ukr16_taildone
.ukr16_tail:
add x8,x8,#-1
mov x9,x5
mov x12,#0
.ukr13_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1]
sub x1,x1,x7
fmul z5.d,z1.d,z0.d
fmul z6.d,z2.d,z0.d
fmul z7.d,z3.d,z0.d
fmul z16.d,z4.d,z0.d
sub x1,x1,x7, LSL #1
mova za0h.d[w12,0],p0/m,z5.d
mova za1h.d[w12,0],p0/m,z6.d
mova za2h.d[w12,0],p0/m,z7.d
mova za3h.d[w12,0],p0/m,z16.d
add x1,x1,x4
add x12,x12,#1
cbnz x9,.ukr13_slices
mov x9,x5
mov x12,#0
.ukr14_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x9,.ukr14_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #2
incb x1, ALL, MUL #1
add x2,x2,x6, LSL #2
cbnz x8,.ukr16_tail
.ukr16_taildone:
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
.size bli_dpackm_ukrgen_sme_pk_ztrans4v_asm, .-bli_dpackm_ukrgen_sme_pk_ztrans4v_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_sme_pk_ztrans5v
.text
.global bli_dpackm_ukrgen_sme_pk_ztrans5v_asm
.type bli_dpackm_ukrgen_sme_pk_ztrans5v_asm, %function
bli_dpackm_ukrgen_sme_pk_ztrans5v_asm:
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
# x0 = n
# x1 = base(X)
# x2 = base(Y)
# x3 = base(kappa)
# x4 = stride(X,m)
smstart
ptrue p0.d
cntd x5
mul x6,x5,x5
lsl x6,x6,#3
mul x7,x5,x4
ldr d0, [x3]
mov x8,#4607182418800017408
fmov d1,x8
fcmp d0,d1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
cbz x0,.ukr9_done
mov x8,x5
mov x12,#0
.ukr1_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7, LSL #2
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr9_last
.ukr9_loop:
add x0,x0,#-1
mov x8,x5
mov x12,#0
.ukr2_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr2_slices
sub x2,x2,x6
incb x1, ALL, MUL #1
mov x8,x5
mov x12,#0
sub x2,x2,x6, LSL #2
.ukr3_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7, LSL #2
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr3_slices
sub x1,x1,x7
add x2,x2,x6
add x2,x2,x6, LSL #2
cbnz x0,.ukr9_loop
.ukr9_last:
mov x8,x5
mov x12,#0
.ukr4_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr4_slices
sub x2,x2,x6
sub x2,x2,x6, LSL #2
.ukr9_done:
b .ukr0_cases_end
.ukr0_case1:
ld1rd {z0.d}, p0/z, [x3]
cbz x0,.ukr10_done
add x0,x0,#-1
cbz x0,.ukr10_last
.ukr10_loop:
add x0,x0,#-1
mov x8,x5
mov x12,#0
.ukr5_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z5.d}, p0/z, [x1]
fmul z6.d,z1.d,z0.d
fmul z7.d,z2.d,z0.d
fmul z16.d,z3.d,z0.d
fmul z17.d,z4.d,z0.d
fmul z18.d,z5.d,z0.d
sub x1,x1,x7, LSL #2
mova za0h.d[w12,0],p0/m,z6.d
mova za1h.d[w12,0],p0/m,z7.d
mova za2h.d[w12,0],p0/m,z16.d
mova za3h.d[w12,0],p0/m,z17.d
mova za4h.d[w12,0],p0/m,z18.d
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr5_slices
mov x8,x5
mov x12,#0
.ukr6_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr6_slices
sub x2,x2,x6
sub x2,x2,x6, LSL #2
sub x1,x1,x7
add x2,x2,x6
incb x1, ALL, MUL #1
add x2,x2,x6, LSL #2
cbnz x0,.ukr10_loop
.ukr10_last:
mov x8,x5
mov x12,#0
.ukr7_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z5.d}, p0/z, [x1]
fmul z6.d,z1.d,z0.d
fmul z7.d,z2.d,z0.d
fmul z16.d,z3.d,z0.d
fmul z17.d,z4.d,z0.d
fmul z18.d,z5.d,z0.d
sub x1,x1,x7, LSL #2
mova za0h.d[w12,0],p0/m,z6.d
mova za1h.d[w12,0],p0/m,z7.d
mova za2h.d[w12,0],p0/m,z16.d
mova za3h.d[w12,0],p0/m,z17.d
mova za4h.d[w12,0],p0/m,z18.d
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr7_slices
mov x8,x5
mov x12,#0
.ukr8_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr8_slices
sub x2,x2,x6
sub x1,x1,x7
sub x2,x2,x6, LSL #2
.ukr10_done:
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
.size bli_dpackm_ukrgen_sme_pk_ztrans5v_asm, .-bli_dpackm_ukrgen_sme_pk_ztrans5v_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_sme_pk_ztrans6v
.text
.global bli_dpackm_ukrgen_sme_pk_ztrans6v_asm
.type bli_dpackm_ukrgen_sme_pk_ztrans6v_asm, %function
bli_dpackm_ukrgen_sme_pk_ztrans6v_asm:
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
# x0 = n
# x1 = base(X)
# x2 = base(Y)
# x3 = base(kappa)
# x4 = stride(X,m)
smstart
ptrue p0.d
cntd x5
mul x6,x5,x5
lsl x6,x6,#3
mul x7,x5,x4
ldr d0, [x3]
mov x8,#4607182418800017408
fmov d1,x8
fcmp d0,d1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
cbz x0,.ukr9_done
mov x8,x5
mov x12,#0
.ukr1_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #2
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr9_last
.ukr9_loop:
add x0,x0,#-1
mov x8,x5
mov x12,#0
.ukr2_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr2_slices
sub x2,x2,x6, LSL #1
incb x1, ALL, MUL #1
mov x8,x5
mov x12,#0
sub x2,x2,x6, LSL #2
.ukr3_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #2
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr3_slices
sub x1,x1,x7
add x2,x2,x6, LSL #1
add x2,x2,x6, LSL #2
cbnz x0,.ukr9_loop
.ukr9_last:
mov x8,x5
mov x12,#0
.ukr4_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr4_slices
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
.ukr9_done:
b .ukr0_cases_end
.ukr0_case1:
ld1rd {z0.d}, p0/z, [x3]
cbz x0,.ukr10_done
add x0,x0,#-1
cbz x0,.ukr10_last
.ukr10_loop:
add x0,x0,#-1
mov x8,x5
mov x12,#0
.ukr5_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z5.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z6.d}, p0/z, [x1]
sub x1,x1,x7
fmul z7.d,z1.d,z0.d
fmul z16.d,z2.d,z0.d
fmul z17.d,z3.d,z0.d
fmul z18.d,z4.d,z0.d
fmul z19.d,z5.d,z0.d
fmul z20.d,z6.d,z0.d
sub x1,x1,x7, LSL #2
mova za0h.d[w12,0],p0/m,z7.d
mova za1h.d[w12,0],p0/m,z16.d
mova za2h.d[w12,0],p0/m,z17.d
mova za3h.d[w12,0],p0/m,z18.d
mova za4h.d[w12,0],p0/m,z19.d
mova za5h.d[w12,0],p0/m,z20.d
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr5_slices
mov x8,x5
mov x12,#0
.ukr6_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr6_slices
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
sub x1,x1,x7
add x2,x2,x6, LSL #1
incb x1, ALL, MUL #1
add x2,x2,x6, LSL #2
cbnz x0,.ukr10_loop
.ukr10_last:
mov x8,x5
mov x12,#0
.ukr7_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z5.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z6.d}, p0/z, [x1]
sub x1,x1,x7
fmul z7.d,z1.d,z0.d
fmul z16.d,z2.d,z0.d
fmul z17.d,z3.d,z0.d
fmul z18.d,z4.d,z0.d
fmul z19.d,z5.d,z0.d
fmul z20.d,z6.d,z0.d
sub x1,x1,x7, LSL #2
mova za0h.d[w12,0],p0/m,z7.d
mova za1h.d[w12,0],p0/m,z16.d
mova za2h.d[w12,0],p0/m,z17.d
mova za3h.d[w12,0],p0/m,z18.d
mova za4h.d[w12,0],p0/m,z19.d
mova za5h.d[w12,0],p0/m,z20.d
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr7_slices
mov x8,x5
mov x12,#0
.ukr8_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr8_slices
sub x2,x2,x6, LSL #1
sub x1,x1,x7
sub x2,x2,x6, LSL #2
.ukr10_done:
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
.size bli_dpackm_ukrgen_sme_pk_ztrans6v_asm, .-bli_dpackm_ukrgen_sme_pk_ztrans6v_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_sme_pk_ztrans7v
.text
.global bli_dpackm_ukrgen_sme_pk_ztrans7v_asm
.type bli_dpackm_ukrgen_sme_pk_ztrans7v_asm, %function
bli_dpackm_ukrgen_sme_pk_ztrans7v_asm:
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
# x0 = n
# x1 = base(X)
# x2 = base(Y)
# x3 = base(kappa)
# x4 = stride(X,m)
smstart
ptrue p0.d
cntd x5
mul x6,x5,x5
lsl x6,x6,#3
mul x7,x5,x4
ldr d0, [x3]
mov x8,#4607182418800017408
fmov d1,x8
fcmp d0,d1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
cbz x0,.ukr9_done
mov x8,x5
mov x12,#0
.ukr1_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za6h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7, LSL #1
sub x1,x1,x7, LSL #2
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr9_last
.ukr9_loop:
add x0,x0,#-1
mov x8,x5
mov x12,#0
.ukr2_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr2_slices
sub x2,x2,x6
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
incb x1, ALL, MUL #1
mov x8,x5
mov x12,#0
.ukr3_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za6h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7, LSL #1
sub x1,x1,x7, LSL #2
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr3_slices
add x2,x2,x6
sub x1,x1,x7
add x2,x2,x6, LSL #1
add x2,x2,x6, LSL #2
cbnz x0,.ukr9_loop
.ukr9_last:
mov x8,x5
mov x12,#0
.ukr4_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr4_slices
sub x2,x2,x6
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
.ukr9_done:
b .ukr0_cases_end
.ukr0_case1:
ld1rd {z0.d}, p0/z, [x3]
cbz x0,.ukr10_done
add x0,x0,#-1
cbz x0,.ukr10_last
.ukr10_loop:
add x0,x0,#-1
mov x8,x5
mov x12,#0
.ukr5_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z5.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z6.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z7.d}, p0/z, [x1]
sub x1,x1,x7, LSL #1
fmul z16.d,z1.d,z0.d
fmul z17.d,z2.d,z0.d
fmul z18.d,z3.d,z0.d
fmul z19.d,z4.d,z0.d
fmul z20.d,z5.d,z0.d
fmul z21.d,z6.d,z0.d
fmul z22.d,z7.d,z0.d
sub x1,x1,x7, LSL #2
mova za0h.d[w12,0],p0/m,z16.d
mova za1h.d[w12,0],p0/m,z17.d
mova za2h.d[w12,0],p0/m,z18.d
mova za3h.d[w12,0],p0/m,z19.d
mova za4h.d[w12,0],p0/m,z20.d
mova za5h.d[w12,0],p0/m,z21.d
mova za6h.d[w12,0],p0/m,z22.d
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr5_slices
mov x8,x5
mov x12,#0
.ukr6_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr6_slices
sub x2,x2,x6
sub x2,x2,x6, LSL #1
sub x2,x2,x6, LSL #2
add x2,x2,x6
sub x1,x1,x7
add x2,x2,x6, LSL #1
incb x1, ALL, MUL #1
add x2,x2,x6, LSL #2
cbnz x0,.ukr10_loop
.ukr10_last:
mov x8,x5
mov x12,#0
.ukr7_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z5.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z6.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z7.d}, p0/z, [x1]
sub x1,x1,x7, LSL #1
fmul z16.d,z1.d,z0.d
fmul z17.d,z2.d,z0.d
fmul z18.d,z3.d,z0.d
fmul z19.d,z4.d,z0.d
fmul z20.d,z5.d,z0.d
fmul z21.d,z6.d,z0.d
fmul z22.d,z7.d,z0.d
sub x1,x1,x7, LSL #2
mova za0h.d[w12,0],p0/m,z16.d
mova za1h.d[w12,0],p0/m,z17.d
mova za2h.d[w12,0],p0/m,z18.d
mova za3h.d[w12,0],p0/m,z19.d
mova za4h.d[w12,0],p0/m,z20.d
mova za5h.d[w12,0],p0/m,z21.d
mova za6h.d[w12,0],p0/m,z22.d
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr7_slices
mov x8,x5
mov x12,#0
.ukr8_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr8_slices
sub x2,x2,x6
sub x2,x2,x6, LSL #1
sub x1,x1,x7
sub x2,x2,x6, LSL #2
.ukr10_done:
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
.size bli_dpackm_ukrgen_sme_pk_ztrans7v_asm, .-bli_dpackm_ukrgen_sme_pk_ztrans7v_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_sme_pk_ztrans8v
.text
.global bli_dpackm_ukrgen_sme_pk_ztrans8v_asm
.type bli_dpackm_ukrgen_sme_pk_ztrans8v_asm, %function
bli_dpackm_ukrgen_sme_pk_ztrans8v_asm:
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
# x0 = n
# x1 = base(X)
# x2 = base(Y)
# x3 = base(kappa)
# x4 = stride(X,m)
smstart
ptrue p0.d
cntd x5
mul x6,x5,x5
lsl x6,x6,#3
mul x7,x5,x4
ldr d0, [x3]
mov x8,#4607182418800017408
fmov d1,x8
fcmp d0,d1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
cbz x0,.ukr9_done
mov x8,x5
mov x12,#0
.ukr1_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za6h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za7h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #1
sub x1,x1,x7, LSL #2
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr9_last
.ukr9_loop:
add x0,x0,#-1
mov x8,x5
mov x12,#0
.ukr2_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr2_slices
incb x1, ALL, MUL #1
mov x8,x5
mov x12,#0
.ukr3_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za3h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za5h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za6h.d[w12, 0]}, p0/z, [x1]
add x1,x1,x7
ld1d {za7h.d[w12, 0]}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #1
sub x1,x1,x7, LSL #2
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr3_slices
sub x2,x2,x6, LSL #3
sub x1,x1,x7
add x2,x2,x6, LSL #3
cbnz x0,.ukr9_loop
.ukr9_last:
mov x8,x5
mov x12,#0
.ukr4_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr4_slices
sub x2,x2,x6, LSL #3
.ukr9_done:
b .ukr0_cases_end
.ukr0_case1:
ld1rd {z0.d}, p0/z, [x3]
cbz x0,.ukr10_done
add x0,x0,#-1
cbz x0,.ukr10_last
.ukr10_loop:
add x0,x0,#-1
mov x8,x5
mov x12,#0
.ukr5_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z5.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z6.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z7.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z16.d}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #1
fmul z17.d,z1.d,z0.d
fmul z18.d,z2.d,z0.d
fmul z19.d,z3.d,z0.d
fmul z20.d,z4.d,z0.d
fmul z21.d,z5.d,z0.d
fmul z22.d,z6.d,z0.d
fmul z23.d,z7.d,z0.d
fmul z24.d,z16.d,z0.d
sub x1,x1,x7, LSL #2
mova za0h.d[w12,0],p0/m,z17.d
mova za1h.d[w12,0],p0/m,z18.d
mova za2h.d[w12,0],p0/m,z19.d
mova za3h.d[w12,0],p0/m,z20.d
mova za4h.d[w12,0],p0/m,z21.d
mova za5h.d[w12,0],p0/m,z22.d
mova za6h.d[w12,0],p0/m,z23.d
mova za7h.d[w12,0],p0/m,z24.d
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr5_slices
mov x8,x5
mov x12,#0
.ukr6_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr6_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #3
incb x1, ALL, MUL #1
add x2,x2,x6, LSL #3
cbnz x0,.ukr10_loop
.ukr10_last:
mov x8,x5
mov x12,#0
.ukr7_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z2.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z3.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z4.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z5.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z6.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z7.d}, p0/z, [x1]
add x1,x1,x7
ld1d {z16.d}, p0/z, [x1]
sub x1,x1,x7
sub x1,x1,x7, LSL #1
fmul z17.d,z1.d,z0.d
fmul z18.d,z2.d,z0.d
fmul z19.d,z3.d,z0.d
fmul z20.d,z4.d,z0.d
fmul z21.d,z5.d,z0.d
fmul z22.d,z6.d,z0.d
fmul z23.d,z7.d,z0.d
fmul z24.d,z16.d,z0.d
sub x1,x1,x7, LSL #2
mova za0h.d[w12,0],p0/m,z17.d
mova za1h.d[w12,0],p0/m,z18.d
mova za2h.d[w12,0],p0/m,z19.d
mova za3h.d[w12,0],p0/m,z20.d
mova za4h.d[w12,0],p0/m,z21.d
mova za5h.d[w12,0],p0/m,z22.d
mova za6h.d[w12,0],p0/m,z23.d
mova za7h.d[w12,0],p0/m,z24.d
add x1,x1,x4
add x12,x12,#1
cbnz x8,.ukr7_slices
mov x8,x5
mov x12,#0
.ukr8_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za1v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za2v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za3v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za4v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za5v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za6v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
st1d {za7v.d[w12, 0]}, p0, [x2]
incb x2, ALL, MUL #1
add x12,x12,#1
cbnz x8,.ukr8_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #3
.ukr10_done:
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
.size bli_dpackm_ukrgen_sme_pk_ztrans8v_asm, .-bli_dpackm_ukrgen_sme_pk_ztrans8v_asm
.section .note.GNU-stack,"",%progbits
