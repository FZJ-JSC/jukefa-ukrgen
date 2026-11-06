### bli_dpackm_ukrgen_sme_pk_ztrans1v
.text
.global bli_dpackm_ukrgen_sme_pk_ztrans1v_asm
.type bli_dpackm_ukrgen_sme_pk_ztrans1v_asm, %function
bli_dpackm_ukrgen_sme_pk_ztrans1v_asm:
.cfi_startproc
add sp,sp,#-112
.cfi_adjust_cfa_offset 112
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
str d8, [sp, #48]
.cfi_rel_offset d8, 48
str d9, [sp, #56]
.cfi_rel_offset d9, 56
str d10, [sp, #64]
.cfi_rel_offset d10, 64
str d11, [sp, #72]
.cfi_rel_offset d11, 72
str d12, [sp, #80]
.cfi_rel_offset d12, 80
str d13, [sp, #88]
.cfi_rel_offset d13, 88
str d14, [sp, #96]
.cfi_rel_offset d14, 96
str d15, [sp, #104]
.cfi_rel_offset d15, 104
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
mov x9,x1
mov x10,x1
mov x11,x1
mov x16,x1
mov x17,x1
mov x19,x1
mov x20,x5
mov x12,#0
incb x9, ALL, MUL #1
incb x10, ALL, MUL #2
incb x11, ALL, MUL #3
incb x16, ALL, MUL #4
incb x17, ALL, MUL #5
incb x19, ALL, MUL #6
add x21,x2,x6
.ukr2_slices:
add x20,x20,#-1
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
ld1d {za2h.d[w12, 0]}, p0/z, [x9]
ld1d {za3h.d[w12, 0]}, p0/z, [x10]
ld1d {za4h.d[w12, 0]}, p0/z, [x11]
ld1d {za5h.d[w12, 0]}, p0/z, [x16]
ld1d {za6h.d[w12, 0]}, p0/z, [x17]
ld1d {za7h.d[w12, 0]}, p0/z, [x19]
add x1,x1,x4
add x9,x9,x4
add x10,x10,x4
add x11,x11,x4
add x16,x16,x4
add x17,x17,x4
add x19,x19,x4
add x12,x12,#1
cbnz x20,.ukr2_slices
add x9,x2,x6
add x10,x2,x6
add x11,x2,x6, LSL #1
add x21,x21,x6, LSL #1
sub x1,x1,x7
mov x16,x5
mov x12,#0
add x17,x2,x6
add x19,x2,x6, LSL #1
add x9,x9,x6, LSL #1
add x20,x2,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x21,x21,x6, LSL #2
.ukr3_slices:
add x16,x16,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x17]
st1d {za2v.d[w12, 0]}, p0, [x19]
st1d {za3v.d[w12, 0]}, p0, [x9]
st1d {za4v.d[w12, 0]}, p0, [x20]
st1d {za5v.d[w12, 0]}, p0, [x10]
st1d {za6v.d[w12, 0]}, p0, [x11]
st1d {za7v.d[w12, 0]}, p0, [x21]
incb x2, ALL, MUL #1
incb x17, ALL, MUL #1
incb x19, ALL, MUL #1
incb x9, ALL, MUL #1
incb x20, ALL, MUL #1
incb x10, ALL, MUL #1
incb x11, ALL, MUL #1
incb x21, ALL, MUL #1
add x12,x12,#1
cbnz x16,.ukr3_slices
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
mov x9,x1
mov x10,x1
mov x11,x1
mov x16,x1
mov x17,x1
mov x19,x1
add x20,x2,x6
mov x21,x5
mov x12,#0
incb x9, ALL, MUL #1
incb x10, ALL, MUL #2
incb x11, ALL, MUL #3
incb x16, ALL, MUL #4
incb x17, ALL, MUL #5
incb x19, ALL, MUL #6
add x22,x2,x6
add x23,x2,x6
add x24,x2,x6, LSL #1
add x20,x20,x6, LSL #1
.ukr5_slices:
add x21,x21,#-1
ld1d {za1h.d[w12, 0]}, p0/z, [x1]
ld1d {za2h.d[w12, 0]}, p0/z, [x9]
ld1d {za3h.d[w12, 0]}, p0/z, [x10]
ld1d {za4h.d[w12, 0]}, p0/z, [x11]
ld1d {za5h.d[w12, 0]}, p0/z, [x16]
ld1d {za6h.d[w12, 0]}, p0/z, [x17]
ld1d {za7h.d[w12, 0]}, p0/z, [x19]
add x1,x1,x4
add x9,x9,x4
add x10,x10,x4
add x11,x11,x4
add x16,x16,x4
add x17,x17,x4
add x19,x19,x4
add x12,x12,#1
cbnz x21,.ukr5_slices
mov x9,x5
mov x12,#0
add x10,x2,x6
add x11,x2,x6, LSL #1
add x22,x22,x6, LSL #1
add x16,x2,x6, LSL #2
add x23,x23,x6, LSL #2
add x24,x24,x6, LSL #2
add x20,x20,x6, LSL #2
.ukr6_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x10]
st1d {za2v.d[w12, 0]}, p0, [x11]
st1d {za3v.d[w12, 0]}, p0, [x22]
st1d {za4v.d[w12, 0]}, p0, [x16]
st1d {za5v.d[w12, 0]}, p0, [x23]
st1d {za6v.d[w12, 0]}, p0, [x24]
st1d {za7v.d[w12, 0]}, p0, [x20]
incb x2, ALL, MUL #1
incb x10, ALL, MUL #1
incb x11, ALL, MUL #1
incb x22, ALL, MUL #1
incb x16, ALL, MUL #1
incb x23, ALL, MUL #1
incb x24, ALL, MUL #1
incb x20, ALL, MUL #1
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
add x9,x2,x6
mov x10,x5
mov x12,#0
add x11,x2,x6
add x16,x2,x6
add x17,x2,x6, LSL #1
add x9,x9,x6, LSL #1
.ukr9_slices:
add x10,x10,#-1
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
cbnz x10,.ukr9_slices
mov x10,x5
mov x12,#0
add x19,x2,x6
add x20,x2,x6, LSL #1
add x11,x11,x6, LSL #1
add x21,x2,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x9,x9,x6, LSL #2
.ukr10_slices:
add x10,x10,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x19]
st1d {za2v.d[w12, 0]}, p0, [x20]
st1d {za3v.d[w12, 0]}, p0, [x11]
st1d {za4v.d[w12, 0]}, p0, [x21]
st1d {za5v.d[w12, 0]}, p0, [x16]
st1d {za6v.d[w12, 0]}, p0, [x17]
st1d {za7v.d[w12, 0]}, p0, [x9]
incb x2, ALL, MUL #1
incb x19, ALL, MUL #1
incb x20, ALL, MUL #1
incb x11, ALL, MUL #1
incb x21, ALL, MUL #1
incb x16, ALL, MUL #1
incb x17, ALL, MUL #1
incb x9, ALL, MUL #1
add x12,x12,#1
cbnz x10,.ukr10_slices
sub x1,x1,x7
sub x2,x2,x6
incb x1, ALL, MUL #8
add x2,x2,x6, LSL #3
cbnz x0,.ukr16_loop
.ukr16_last:
add x9,x2,x6
mov x10,x5
mov x12,#0
add x11,x2,x6
add x16,x2,x6
add x17,x2,x6, LSL #1
add x9,x9,x6, LSL #1
.ukr11_slices:
add x10,x10,#-1
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
cbnz x10,.ukr11_slices
mov x10,x5
mov x12,#0
add x19,x2,x6
add x20,x2,x6, LSL #1
add x11,x11,x6, LSL #1
add x21,x2,x6, LSL #2
add x16,x16,x6, LSL #2
add x17,x17,x6, LSL #2
add x9,x9,x6, LSL #2
.ukr12_slices:
add x10,x10,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x19]
st1d {za2v.d[w12, 0]}, p0, [x20]
st1d {za3v.d[w12, 0]}, p0, [x11]
st1d {za4v.d[w12, 0]}, p0, [x21]
st1d {za5v.d[w12, 0]}, p0, [x16]
st1d {za6v.d[w12, 0]}, p0, [x17]
st1d {za7v.d[w12, 0]}, p0, [x9]
incb x2, ALL, MUL #1
incb x19, ALL, MUL #1
incb x20, ALL, MUL #1
incb x11, ALL, MUL #1
incb x21, ALL, MUL #1
incb x16, ALL, MUL #1
incb x17, ALL, MUL #1
incb x9, ALL, MUL #1
add x12,x12,#1
cbnz x10,.ukr12_slices
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
ldr d8, [sp, #48]
.cfi_restore d8
ldr d9, [sp, #56]
.cfi_restore d9
ldr d10, [sp, #64]
.cfi_restore d10
ldr d11, [sp, #72]
.cfi_restore d11
ldr d12, [sp, #80]
.cfi_restore d12
ldr d13, [sp, #88]
.cfi_restore d13
ldr d14, [sp, #96]
.cfi_restore d14
ldr d15, [sp, #104]
.cfi_restore d15
add sp,sp,#112
.cfi_adjust_cfa_offset -112
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
add sp,sp,#-112
.cfi_adjust_cfa_offset 112
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
str d8, [sp, #48]
.cfi_rel_offset d8, 48
str d9, [sp, #56]
.cfi_rel_offset d9, 56
str d10, [sp, #64]
.cfi_rel_offset d10, 64
str d11, [sp, #72]
.cfi_rel_offset d11, 72
str d12, [sp, #80]
.cfi_rel_offset d12, 80
str d13, [sp, #88]
.cfi_rel_offset d13, 88
str d14, [sp, #96]
.cfi_rel_offset d14, 96
str d15, [sp, #104]
.cfi_rel_offset d15, 104
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
add x10,x1,x7
.ukr1_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x10]
add x1,x1,x4
add x10,x10,x4
add x12,x12,#1
cbnz x9,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr15_last
.ukr15_loop:
add x0,x0,#-1
incb x1, ALL, MUL #1
mov x9,x1
mov x10,x1
mov x11,x1
incb x9, ALL, MUL #1
mov x16,x1
incb x10, ALL, MUL #2
mov x17,x5
mov x12,#0
add x19,x1,x7
incb x11, ALL, MUL #1
add x9,x9,x7
incb x16, ALL, MUL #2
add x10,x10,x7
mov x20,x2
.ukr2_slices:
add x17,x17,#-1
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
ld1d {za3h.d[w12, 0]}, p0/z, [x19]
ld1d {za4h.d[w12, 0]}, p0/z, [x11]
ld1d {za5h.d[w12, 0]}, p0/z, [x9]
ld1d {za6h.d[w12, 0]}, p0/z, [x16]
ld1d {za7h.d[w12, 0]}, p0/z, [x10]
add x1,x1,x4
add x19,x19,x4
add x11,x11,x4
add x9,x9,x4
add x16,x16,x4
add x10,x10,x4
add x12,x12,#1
cbnz x17,.ukr2_slices
mov x9,x2
mov x10,x2
incb x20, ALL, MUL #1
sub x1,x1,x7
mov x11,x2
incb x9, ALL, MUL #1
incb x10, ALL, MUL #1
add x16,x2,x6, LSL #1
add x20,x20,x6, LSL #1
mov x17,x5
mov x12,#0
incb x11, ALL, MUL #1
add x19,x2,x6, LSL #1
add x9,x9,x6, LSL #1
add x21,x2,x6, LSL #2
add x10,x10,x6, LSL #2
add x16,x16,x6, LSL #2
add x20,x20,x6, LSL #2
incb x1, ALL, MUL #3
.ukr3_slices:
add x17,x17,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x11]
st1d {za2v.d[w12, 0]}, p0, [x19]
st1d {za3v.d[w12, 0]}, p0, [x9]
st1d {za4v.d[w12, 0]}, p0, [x21]
st1d {za5v.d[w12, 0]}, p0, [x10]
st1d {za6v.d[w12, 0]}, p0, [x16]
st1d {za7v.d[w12, 0]}, p0, [x20]
incb x2, ALL, MUL #2
incb x11, ALL, MUL #2
incb x19, ALL, MUL #2
incb x9, ALL, MUL #2
incb x21, ALL, MUL #2
incb x10, ALL, MUL #2
incb x16, ALL, MUL #2
incb x20, ALL, MUL #2
add x12,x12,#1
cbnz x17,.ukr3_slices
mov x9,x5
mov x12,#0
add x10,x1,x7
.ukr4_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x10]
add x1,x1,x4
add x10,x10,x4
add x12,x12,#1
cbnz x9,.ukr4_slices
sub x2,x2,x6, LSL #1
sub x1,x1,x7
add x2,x2,x6, LSL #3
cbnz x0,.ukr15_loop
.ukr15_last:
incb x1, ALL, MUL #1
mov x9,x1
mov x10,x1
mov x11,x2
mov x16,x1
incb x9, ALL, MUL #1
mov x17,x1
incb x10, ALL, MUL #2
mov x19,x2
mov x20,x2
incb x11, ALL, MUL #1
mov x21,x5
mov x12,#0
add x22,x1,x7
incb x16, ALL, MUL #1
add x9,x9,x7
incb x17, ALL, MUL #2
add x10,x10,x7
mov x23,x2
incb x19, ALL, MUL #1
incb x20, ALL, MUL #1
add x24,x2,x6, LSL #1
add x11,x11,x6, LSL #1
.ukr5_slices:
add x21,x21,#-1
ld1d {za2h.d[w12, 0]}, p0/z, [x1]
ld1d {za3h.d[w12, 0]}, p0/z, [x22]
ld1d {za4h.d[w12, 0]}, p0/z, [x16]
ld1d {za5h.d[w12, 0]}, p0/z, [x9]
ld1d {za6h.d[w12, 0]}, p0/z, [x17]
ld1d {za7h.d[w12, 0]}, p0/z, [x10]
add x1,x1,x4
add x22,x22,x4
add x16,x16,x4
add x9,x9,x4
add x17,x17,x4
add x10,x10,x4
add x12,x12,#1
cbnz x21,.ukr5_slices
mov x9,x5
mov x12,#0
incb x23, ALL, MUL #1
add x10,x2,x6, LSL #1
add x19,x19,x6, LSL #1
add x16,x2,x6, LSL #2
add x20,x20,x6, LSL #2
add x24,x24,x6, LSL #2
add x11,x11,x6, LSL #2
.ukr6_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x23]
st1d {za2v.d[w12, 0]}, p0, [x10]
st1d {za3v.d[w12, 0]}, p0, [x19]
st1d {za4v.d[w12, 0]}, p0, [x16]
st1d {za5v.d[w12, 0]}, p0, [x20]
st1d {za6v.d[w12, 0]}, p0, [x24]
st1d {za7v.d[w12, 0]}, p0, [x11]
incb x2, ALL, MUL #2
incb x23, ALL, MUL #2
incb x10, ALL, MUL #2
incb x19, ALL, MUL #2
incb x16, ALL, MUL #2
incb x20, ALL, MUL #2
incb x24, ALL, MUL #2
incb x11, ALL, MUL #2
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
add x10,x1,x7
mov x11,x2
.ukr7_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x10]
add x1,x1,x4
add x10,x10,x4
add x12,x12,#1
cbnz x9,.ukr7_slices
mov x9,x5
mov x12,#0
incb x11, ALL, MUL #1
.ukr8_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x11]
incb x2, ALL, MUL #2
incb x11, ALL, MUL #2
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
mov x9,x2
mov x10,x2
mov x11,x2
incb x9, ALL, MUL #1
mov x16,x5
mov x12,#0
add x17,x1,x7
mov x19,x2
incb x10, ALL, MUL #1
incb x11, ALL, MUL #1
add x20,x2,x6, LSL #1
add x9,x9,x6, LSL #1
.ukr9_slices:
add x16,x16,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x17]
ld1d {z3.d}, p0/z, [x1, #1, MUL VL]
ld1d {z4.d}, p0/z, [x17, #1, MUL VL]
ld1d {z5.d}, p0/z, [x1, #2, MUL VL]
ld1d {z6.d}, p0/z, [x17, #2, MUL VL]
ld1d {z7.d}, p0/z, [x1, #3, MUL VL]
ld1d {z16.d}, p0/z, [x17, #3, MUL VL]
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
add x17,x17,x4
add x12,x12,#1
cbnz x16,.ukr9_slices
mov x16,x5
mov x12,#0
incb x19, ALL, MUL #1
add x17,x2,x6, LSL #1
add x10,x10,x6, LSL #1
add x21,x2,x6, LSL #2
add x11,x11,x6, LSL #2
add x20,x20,x6, LSL #2
add x9,x9,x6, LSL #2
.ukr10_slices:
add x16,x16,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x19]
st1d {za2v.d[w12, 0]}, p0, [x17]
st1d {za3v.d[w12, 0]}, p0, [x10]
st1d {za4v.d[w12, 0]}, p0, [x21]
st1d {za5v.d[w12, 0]}, p0, [x11]
st1d {za6v.d[w12, 0]}, p0, [x20]
st1d {za7v.d[w12, 0]}, p0, [x9]
incb x2, ALL, MUL #2
incb x19, ALL, MUL #2
incb x17, ALL, MUL #2
incb x10, ALL, MUL #2
incb x21, ALL, MUL #2
incb x11, ALL, MUL #2
incb x20, ALL, MUL #2
incb x9, ALL, MUL #2
add x12,x12,#1
cbnz x16,.ukr10_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #1
incb x1, ALL, MUL #4
add x2,x2,x6, LSL #3
cbnz x0,.ukr16_loop
.ukr16_last:
mov x9,x2
mov x10,x2
mov x11,x2
incb x9, ALL, MUL #1
mov x16,x5
mov x12,#0
add x17,x1,x7
mov x19,x2
incb x10, ALL, MUL #1
incb x11, ALL, MUL #1
add x20,x2,x6, LSL #1
add x9,x9,x6, LSL #1
.ukr11_slices:
add x16,x16,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x17]
ld1d {z3.d}, p0/z, [x1, #1, MUL VL]
ld1d {z4.d}, p0/z, [x17, #1, MUL VL]
ld1d {z5.d}, p0/z, [x1, #2, MUL VL]
ld1d {z6.d}, p0/z, [x17, #2, MUL VL]
ld1d {z7.d}, p0/z, [x1, #3, MUL VL]
ld1d {z16.d}, p0/z, [x17, #3, MUL VL]
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
add x17,x17,x4
add x12,x12,#1
cbnz x16,.ukr11_slices
mov x16,x5
mov x12,#0
incb x19, ALL, MUL #1
add x17,x2,x6, LSL #1
add x10,x10,x6, LSL #1
add x21,x2,x6, LSL #2
add x11,x11,x6, LSL #2
add x20,x20,x6, LSL #2
add x9,x9,x6, LSL #2
.ukr12_slices:
add x16,x16,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x19]
st1d {za2v.d[w12, 0]}, p0, [x17]
st1d {za3v.d[w12, 0]}, p0, [x10]
st1d {za4v.d[w12, 0]}, p0, [x21]
st1d {za5v.d[w12, 0]}, p0, [x11]
st1d {za6v.d[w12, 0]}, p0, [x20]
st1d {za7v.d[w12, 0]}, p0, [x9]
incb x2, ALL, MUL #2
incb x19, ALL, MUL #2
incb x17, ALL, MUL #2
incb x10, ALL, MUL #2
incb x21, ALL, MUL #2
incb x11, ALL, MUL #2
incb x20, ALL, MUL #2
incb x9, ALL, MUL #2
add x12,x12,#1
cbnz x16,.ukr12_slices
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
add x10,x1,x7
mov x11,x2
.ukr13_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x10]
fmul z3.d,z1.d,z0.d
fmul z4.d,z2.d,z0.d
mova za0h.d[w12,0],p0/m,z3.d
mova za1h.d[w12,0],p0/m,z4.d
add x1,x1,x4
add x10,x10,x4
add x12,x12,#1
cbnz x9,.ukr13_slices
mov x9,x5
mov x12,#0
incb x11, ALL, MUL #1
.ukr14_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x11]
incb x2, ALL, MUL #2
incb x11, ALL, MUL #2
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
ldr d8, [sp, #48]
.cfi_restore d8
ldr d9, [sp, #56]
.cfi_restore d9
ldr d10, [sp, #64]
.cfi_restore d10
ldr d11, [sp, #72]
.cfi_restore d11
ldr d12, [sp, #80]
.cfi_restore d12
ldr d13, [sp, #88]
.cfi_restore d13
ldr d14, [sp, #96]
.cfi_restore d14
ldr d15, [sp, #104]
.cfi_restore d15
add sp,sp,#112
.cfi_adjust_cfa_offset -112
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
add x9,x1,x7
add x10,x1,x7, LSL #1
.ukr1_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x9]
ld1d {za2h.d[w12, 0]}, p0/z, [x10]
add x1,x1,x4
add x9,x9,x4
add x10,x10,x4
add x12,x12,#1
cbnz x8,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr9_last
.ukr9_loop:
add x0,x0,#-1
mov x8,x2
mov x9,x2
mov x10,x5
mov x12,#0
incb x8, ALL, MUL #1
incb x9, ALL, MUL #2
.ukr2_slices:
add x10,x10,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x8]
st1d {za2v.d[w12, 0]}, p0, [x9]
incb x2, ALL, MUL #3
incb x8, ALL, MUL #3
incb x9, ALL, MUL #3
add x12,x12,#1
cbnz x10,.ukr2_slices
incb x1, ALL, MUL #1
sub x2,x2,x6
mov x8,x5
mov x12,#0
add x9,x1,x7
add x10,x1,x7, LSL #1
sub x2,x2,x6, LSL #1
.ukr3_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x9]
ld1d {za2h.d[w12, 0]}, p0/z, [x10]
add x1,x1,x4
add x9,x9,x4
add x10,x10,x4
add x12,x12,#1
cbnz x8,.ukr3_slices
sub x1,x1,x7
add x2,x2,x6
add x2,x2,x6, LSL #1
cbnz x0,.ukr9_loop
.ukr9_last:
mov x8,x2
mov x9,x2
mov x10,x5
mov x12,#0
incb x8, ALL, MUL #1
incb x9, ALL, MUL #2
.ukr4_slices:
add x10,x10,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x8]
st1d {za2v.d[w12, 0]}, p0, [x9]
incb x2, ALL, MUL #3
incb x8, ALL, MUL #3
incb x9, ALL, MUL #3
add x12,x12,#1
cbnz x10,.ukr4_slices
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
add x9,x1,x7
add x10,x1,x7, LSL #1
mov x11,x2
mov x16,x2
.ukr5_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x9]
ld1d {z3.d}, p0/z, [x10]
fmul z4.d,z1.d,z0.d
fmul z5.d,z2.d,z0.d
fmul z6.d,z3.d,z0.d
mova za0h.d[w12,0],p0/m,z4.d
mova za1h.d[w12,0],p0/m,z5.d
mova za2h.d[w12,0],p0/m,z6.d
add x1,x1,x4
add x9,x9,x4
add x10,x10,x4
add x12,x12,#1
cbnz x8,.ukr5_slices
mov x8,x5
mov x12,#0
incb x11, ALL, MUL #1
incb x16, ALL, MUL #2
.ukr6_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x11]
st1d {za2v.d[w12, 0]}, p0, [x16]
incb x2, ALL, MUL #3
incb x11, ALL, MUL #3
incb x16, ALL, MUL #3
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
add x9,x1,x7
add x10,x1,x7, LSL #1
mov x11,x2
mov x16,x2
.ukr7_slices:
add x8,x8,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x9]
ld1d {z3.d}, p0/z, [x10]
fmul z4.d,z1.d,z0.d
fmul z5.d,z2.d,z0.d
fmul z6.d,z3.d,z0.d
mova za0h.d[w12,0],p0/m,z4.d
mova za1h.d[w12,0],p0/m,z5.d
mova za2h.d[w12,0],p0/m,z6.d
add x1,x1,x4
add x9,x9,x4
add x10,x10,x4
add x12,x12,#1
cbnz x8,.ukr7_slices
mov x8,x5
mov x12,#0
incb x11, ALL, MUL #1
incb x16, ALL, MUL #2
.ukr8_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x11]
st1d {za2v.d[w12, 0]}, p0, [x16]
incb x2, ALL, MUL #3
incb x11, ALL, MUL #3
incb x16, ALL, MUL #3
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
add sp,sp,#-112
.cfi_adjust_cfa_offset 112
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
str d8, [sp, #40]
.cfi_rel_offset d8, 40
str d9, [sp, #48]
.cfi_rel_offset d9, 48
str d10, [sp, #56]
.cfi_rel_offset d10, 56
str d11, [sp, #64]
.cfi_rel_offset d11, 64
str d12, [sp, #72]
.cfi_rel_offset d12, 72
str d13, [sp, #80]
.cfi_rel_offset d13, 80
str d14, [sp, #88]
.cfi_rel_offset d14, 88
str d15, [sp, #96]
.cfi_rel_offset d15, 96
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
add x9,x1,x7
mov x10,x5
mov x12,#0
add x11,x1,x7
add x16,x1,x7, LSL #1
add x9,x9,x7, LSL #1
.ukr1_slices:
add x10,x10,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x11]
ld1d {za2h.d[w12, 0]}, p0/z, [x16]
ld1d {za3h.d[w12, 0]}, p0/z, [x9]
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x9,x9,x4
add x12,x12,#1
cbnz x10,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr15_last
.ukr15_loop:
add x0,x0,#-1
incb x1, ALL, MUL #1
add x9,x1,x7
mov x10,x5
mov x12,#0
add x11,x1,x7
add x16,x1,x7, LSL #1
add x9,x9,x7, LSL #1
.ukr2_slices:
add x10,x10,#-1
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
ld1d {za5h.d[w12, 0]}, p0/z, [x11]
ld1d {za6h.d[w12, 0]}, p0/z, [x16]
ld1d {za7h.d[w12, 0]}, p0/z, [x9]
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x9,x9,x4
add x12,x12,#1
cbnz x10,.ukr2_slices
sub x1,x1,x7
mov x9,x2
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x2
mov x19,x2
incb x9, ALL, MUL #1
incb x10, ALL, MUL #2
incb x11, ALL, MUL #3
incb x1, ALL, MUL #1
mov x20,x5
mov x12,#0
incb x16, ALL, MUL #1
incb x17, ALL, MUL #2
incb x19, ALL, MUL #3
add x21,x2,x6, LSL #2
add x9,x9,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x22,x1,x7
.ukr3_slices:
add x20,x20,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x16]
st1d {za2v.d[w12, 0]}, p0, [x17]
st1d {za3v.d[w12, 0]}, p0, [x19]
st1d {za4v.d[w12, 0]}, p0, [x21]
st1d {za5v.d[w12, 0]}, p0, [x9]
st1d {za6v.d[w12, 0]}, p0, [x10]
st1d {za7v.d[w12, 0]}, p0, [x11]
incb x2, ALL, MUL #4
incb x16, ALL, MUL #4
incb x17, ALL, MUL #4
incb x19, ALL, MUL #4
incb x21, ALL, MUL #4
incb x9, ALL, MUL #4
incb x10, ALL, MUL #4
incb x11, ALL, MUL #4
add x12,x12,#1
cbnz x20,.ukr3_slices
mov x9,x5
mov x12,#0
add x10,x1,x7
add x11,x1,x7, LSL #1
add x22,x22,x7, LSL #1
.ukr4_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x10]
ld1d {za2h.d[w12, 0]}, p0/z, [x11]
ld1d {za3h.d[w12, 0]}, p0/z, [x22]
add x1,x1,x4
add x10,x10,x4
add x11,x11,x4
add x22,x22,x4
add x12,x12,#1
cbnz x9,.ukr4_slices
sub x2,x2,x6, LSL #2
sub x1,x1,x7
add x2,x2,x6, LSL #3
cbnz x0,.ukr15_loop
.ukr15_last:
incb x1, ALL, MUL #1
add x9,x1,x7
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x5
mov x12,#0
add x19,x1,x7
add x20,x1,x7, LSL #1
add x9,x9,x7, LSL #1
mov x21,x2
mov x22,x2
mov x23,x2
incb x10, ALL, MUL #1
incb x11, ALL, MUL #2
incb x16, ALL, MUL #3
.ukr5_slices:
add x17,x17,#-1
ld1d {za4h.d[w12, 0]}, p0/z, [x1]
ld1d {za5h.d[w12, 0]}, p0/z, [x19]
ld1d {za6h.d[w12, 0]}, p0/z, [x20]
ld1d {za7h.d[w12, 0]}, p0/z, [x9]
add x1,x1,x4
add x19,x19,x4
add x20,x20,x4
add x9,x9,x4
add x12,x12,#1
cbnz x17,.ukr5_slices
mov x9,x5
mov x12,#0
incb x21, ALL, MUL #1
incb x22, ALL, MUL #2
incb x23, ALL, MUL #3
add x17,x2,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
.ukr6_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x21]
st1d {za2v.d[w12, 0]}, p0, [x22]
st1d {za3v.d[w12, 0]}, p0, [x23]
st1d {za4v.d[w12, 0]}, p0, [x17]
st1d {za5v.d[w12, 0]}, p0, [x10]
st1d {za6v.d[w12, 0]}, p0, [x11]
st1d {za7v.d[w12, 0]}, p0, [x16]
incb x2, ALL, MUL #4
incb x21, ALL, MUL #4
incb x22, ALL, MUL #4
incb x23, ALL, MUL #4
incb x17, ALL, MUL #4
incb x10, ALL, MUL #4
incb x11, ALL, MUL #4
incb x16, ALL, MUL #4
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
add x9,x1,x7
mov x10,x5
mov x12,#0
add x11,x1,x7
add x16,x1,x7, LSL #1
add x9,x9,x7, LSL #1
mov x17,x2
mov x19,x2
mov x20,x2
.ukr7_slices:
add x10,x10,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x11]
ld1d {za2h.d[w12, 0]}, p0/z, [x16]
ld1d {za3h.d[w12, 0]}, p0/z, [x9]
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x9,x9,x4
add x12,x12,#1
cbnz x10,.ukr7_slices
mov x9,x5
mov x12,#0
incb x17, ALL, MUL #1
incb x19, ALL, MUL #2
incb x20, ALL, MUL #3
.ukr8_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x17]
st1d {za2v.d[w12, 0]}, p0, [x19]
st1d {za3v.d[w12, 0]}, p0, [x20]
incb x2, ALL, MUL #4
incb x17, ALL, MUL #4
incb x19, ALL, MUL #4
incb x20, ALL, MUL #4
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
add x9,x1,x7
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x5
mov x12,#0
add x19,x1,x7
add x20,x1,x7, LSL #1
add x9,x9,x7, LSL #1
mov x21,x2
mov x22,x2
mov x23,x2
incb x10, ALL, MUL #1
incb x11, ALL, MUL #2
incb x16, ALL, MUL #3
.ukr9_slices:
add x17,x17,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x19]
ld1d {z3.d}, p0/z, [x20]
ld1d {z4.d}, p0/z, [x9]
ld1d {z5.d}, p0/z, [x1, #1, MUL VL]
ld1d {z6.d}, p0/z, [x19, #1, MUL VL]
ld1d {z7.d}, p0/z, [x20, #1, MUL VL]
ld1d {z16.d}, p0/z, [x9, #1, MUL VL]
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
add x19,x19,x4
add x20,x20,x4
add x9,x9,x4
add x12,x12,#1
cbnz x17,.ukr9_slices
mov x9,x5
mov x12,#0
incb x21, ALL, MUL #1
incb x22, ALL, MUL #2
incb x23, ALL, MUL #3
add x17,x2,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
.ukr10_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x21]
st1d {za2v.d[w12, 0]}, p0, [x22]
st1d {za3v.d[w12, 0]}, p0, [x23]
st1d {za4v.d[w12, 0]}, p0, [x17]
st1d {za5v.d[w12, 0]}, p0, [x10]
st1d {za6v.d[w12, 0]}, p0, [x11]
st1d {za7v.d[w12, 0]}, p0, [x16]
incb x2, ALL, MUL #4
incb x21, ALL, MUL #4
incb x22, ALL, MUL #4
incb x23, ALL, MUL #4
incb x17, ALL, MUL #4
incb x10, ALL, MUL #4
incb x11, ALL, MUL #4
incb x16, ALL, MUL #4
add x12,x12,#1
cbnz x9,.ukr10_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #2
incb x1, ALL, MUL #2
add x2,x2,x6, LSL #3
cbnz x0,.ukr16_loop
.ukr16_last:
add x9,x1,x7
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x5
mov x12,#0
add x19,x1,x7
add x20,x1,x7, LSL #1
add x9,x9,x7, LSL #1
mov x21,x2
mov x22,x2
mov x23,x2
incb x10, ALL, MUL #1
incb x11, ALL, MUL #2
incb x16, ALL, MUL #3
.ukr11_slices:
add x17,x17,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x19]
ld1d {z3.d}, p0/z, [x20]
ld1d {z4.d}, p0/z, [x9]
ld1d {z5.d}, p0/z, [x1, #1, MUL VL]
ld1d {z6.d}, p0/z, [x19, #1, MUL VL]
ld1d {z7.d}, p0/z, [x20, #1, MUL VL]
ld1d {z16.d}, p0/z, [x9, #1, MUL VL]
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
add x19,x19,x4
add x20,x20,x4
add x9,x9,x4
add x12,x12,#1
cbnz x17,.ukr11_slices
mov x9,x5
mov x12,#0
incb x21, ALL, MUL #1
incb x22, ALL, MUL #2
incb x23, ALL, MUL #3
add x17,x2,x6, LSL #2
add x10,x10,x6, LSL #2
add x11,x11,x6, LSL #2
add x16,x16,x6, LSL #2
.ukr12_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x21]
st1d {za2v.d[w12, 0]}, p0, [x22]
st1d {za3v.d[w12, 0]}, p0, [x23]
st1d {za4v.d[w12, 0]}, p0, [x17]
st1d {za5v.d[w12, 0]}, p0, [x10]
st1d {za6v.d[w12, 0]}, p0, [x11]
st1d {za7v.d[w12, 0]}, p0, [x16]
incb x2, ALL, MUL #4
incb x21, ALL, MUL #4
incb x22, ALL, MUL #4
incb x23, ALL, MUL #4
incb x17, ALL, MUL #4
incb x10, ALL, MUL #4
incb x11, ALL, MUL #4
incb x16, ALL, MUL #4
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
add x9,x1,x7
mov x10,x5
mov x12,#0
add x11,x1,x7
add x16,x1,x7, LSL #1
add x9,x9,x7, LSL #1
mov x17,x2
mov x19,x2
mov x20,x2
.ukr13_slices:
add x10,x10,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x11]
ld1d {z3.d}, p0/z, [x16]
ld1d {z4.d}, p0/z, [x9]
fmul z5.d,z1.d,z0.d
fmul z6.d,z2.d,z0.d
fmul z7.d,z3.d,z0.d
fmul z16.d,z4.d,z0.d
mova za0h.d[w12,0],p0/m,z5.d
mova za1h.d[w12,0],p0/m,z6.d
mova za2h.d[w12,0],p0/m,z7.d
mova za3h.d[w12,0],p0/m,z16.d
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x9,x9,x4
add x12,x12,#1
cbnz x10,.ukr13_slices
mov x9,x5
mov x12,#0
incb x17, ALL, MUL #1
incb x19, ALL, MUL #2
incb x20, ALL, MUL #3
.ukr14_slices:
add x9,x9,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x17]
st1d {za2v.d[w12, 0]}, p0, [x19]
st1d {za3v.d[w12, 0]}, p0, [x20]
incb x2, ALL, MUL #4
incb x17, ALL, MUL #4
incb x19, ALL, MUL #4
incb x20, ALL, MUL #4
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
ldr d8, [sp, #40]
.cfi_restore d8
ldr d9, [sp, #48]
.cfi_restore d9
ldr d10, [sp, #56]
.cfi_restore d10
ldr d11, [sp, #64]
.cfi_restore d11
ldr d12, [sp, #72]
.cfi_restore d12
ldr d13, [sp, #80]
.cfi_restore d13
ldr d14, [sp, #88]
.cfi_restore d14
ldr d15, [sp, #96]
.cfi_restore d15
add sp,sp,#112
.cfi_adjust_cfa_offset -112
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
add sp,sp,#-96
.cfi_adjust_cfa_offset 96
str x19, [sp]
.cfi_rel_offset x19, 0
str x20, [sp, #8]
.cfi_rel_offset x20, 8
str x21, [sp, #16]
.cfi_rel_offset x21, 16
str d8, [sp, #24]
.cfi_rel_offset d8, 24
str d9, [sp, #32]
.cfi_rel_offset d9, 32
str d10, [sp, #40]
.cfi_rel_offset d10, 40
str d11, [sp, #48]
.cfi_rel_offset d11, 48
str d12, [sp, #56]
.cfi_rel_offset d12, 56
str d13, [sp, #64]
.cfi_rel_offset d13, 64
str d14, [sp, #72]
.cfi_rel_offset d14, 72
str d15, [sp, #80]
.cfi_rel_offset d15, 80
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
add x8,x1,x7
mov x9,x5
mov x12,#0
add x10,x1,x7
add x11,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x16,x1,x7, LSL #2
.ukr1_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x10]
ld1d {za2h.d[w12, 0]}, p0/z, [x11]
ld1d {za3h.d[w12, 0]}, p0/z, [x8]
ld1d {za4h.d[w12, 0]}, p0/z, [x16]
add x1,x1,x4
add x10,x10,x4
add x11,x11,x4
add x8,x8,x4
add x16,x16,x4
add x12,x12,#1
cbnz x9,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr9_last
.ukr9_loop:
add x0,x0,#-1
mov x8,x2
mov x9,x2
mov x10,x2
mov x11,x2
mov x16,x5
mov x12,#0
incb x8, ALL, MUL #1
incb x9, ALL, MUL #2
incb x10, ALL, MUL #3
incb x11, ALL, MUL #4
incb x1, ALL, MUL #1
.ukr2_slices:
add x16,x16,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x8]
st1d {za2v.d[w12, 0]}, p0, [x9]
st1d {za3v.d[w12, 0]}, p0, [x10]
st1d {za4v.d[w12, 0]}, p0, [x11]
incb x2, ALL, MUL #5
incb x8, ALL, MUL #5
incb x9, ALL, MUL #5
incb x10, ALL, MUL #5
incb x11, ALL, MUL #5
add x12,x12,#1
cbnz x16,.ukr2_slices
add x8,x1,x7
sub x2,x2,x6
mov x9,x5
mov x12,#0
add x10,x1,x7
add x11,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x16,x1,x7, LSL #2
sub x2,x2,x6, LSL #2
.ukr3_slices:
add x9,x9,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x10]
ld1d {za2h.d[w12, 0]}, p0/z, [x11]
ld1d {za3h.d[w12, 0]}, p0/z, [x8]
ld1d {za4h.d[w12, 0]}, p0/z, [x16]
add x1,x1,x4
add x10,x10,x4
add x11,x11,x4
add x8,x8,x4
add x16,x16,x4
add x12,x12,#1
cbnz x9,.ukr3_slices
sub x1,x1,x7
add x2,x2,x6
add x2,x2,x6, LSL #2
cbnz x0,.ukr9_loop
.ukr9_last:
mov x8,x2
mov x9,x2
mov x10,x2
mov x11,x2
mov x16,x5
mov x12,#0
incb x8, ALL, MUL #1
incb x9, ALL, MUL #2
incb x10, ALL, MUL #3
incb x11, ALL, MUL #4
.ukr4_slices:
add x16,x16,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x8]
st1d {za2v.d[w12, 0]}, p0, [x9]
st1d {za3v.d[w12, 0]}, p0, [x10]
st1d {za4v.d[w12, 0]}, p0, [x11]
incb x2, ALL, MUL #5
incb x8, ALL, MUL #5
incb x9, ALL, MUL #5
incb x10, ALL, MUL #5
incb x11, ALL, MUL #5
add x12,x12,#1
cbnz x16,.ukr4_slices
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
add x8,x1,x7
mov x9,x5
mov x12,#0
add x10,x1,x7
add x11,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x16,x1,x7, LSL #2
mov x17,x2
mov x19,x2
mov x20,x2
mov x21,x2
.ukr5_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x10]
ld1d {z3.d}, p0/z, [x11]
ld1d {z4.d}, p0/z, [x8]
ld1d {z5.d}, p0/z, [x16]
fmul z6.d,z1.d,z0.d
fmul z7.d,z2.d,z0.d
fmul z16.d,z3.d,z0.d
fmul z17.d,z4.d,z0.d
fmul z18.d,z5.d,z0.d
mova za0h.d[w12,0],p0/m,z6.d
mova za1h.d[w12,0],p0/m,z7.d
mova za2h.d[w12,0],p0/m,z16.d
mova za3h.d[w12,0],p0/m,z17.d
mova za4h.d[w12,0],p0/m,z18.d
add x1,x1,x4
add x10,x10,x4
add x11,x11,x4
add x8,x8,x4
add x16,x16,x4
add x12,x12,#1
cbnz x9,.ukr5_slices
mov x8,x5
mov x12,#0
incb x17, ALL, MUL #1
incb x19, ALL, MUL #2
incb x20, ALL, MUL #3
incb x21, ALL, MUL #4
.ukr6_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x17]
st1d {za2v.d[w12, 0]}, p0, [x19]
st1d {za3v.d[w12, 0]}, p0, [x20]
st1d {za4v.d[w12, 0]}, p0, [x21]
incb x2, ALL, MUL #5
incb x17, ALL, MUL #5
incb x19, ALL, MUL #5
incb x20, ALL, MUL #5
incb x21, ALL, MUL #5
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
add x8,x1,x7
mov x9,x5
mov x12,#0
add x10,x1,x7
add x11,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x16,x1,x7, LSL #2
mov x17,x2
mov x19,x2
mov x20,x2
mov x21,x2
.ukr7_slices:
add x9,x9,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x10]
ld1d {z3.d}, p0/z, [x11]
ld1d {z4.d}, p0/z, [x8]
ld1d {z5.d}, p0/z, [x16]
fmul z6.d,z1.d,z0.d
fmul z7.d,z2.d,z0.d
fmul z16.d,z3.d,z0.d
fmul z17.d,z4.d,z0.d
fmul z18.d,z5.d,z0.d
mova za0h.d[w12,0],p0/m,z6.d
mova za1h.d[w12,0],p0/m,z7.d
mova za2h.d[w12,0],p0/m,z16.d
mova za3h.d[w12,0],p0/m,z17.d
mova za4h.d[w12,0],p0/m,z18.d
add x1,x1,x4
add x10,x10,x4
add x11,x11,x4
add x8,x8,x4
add x16,x16,x4
add x12,x12,#1
cbnz x9,.ukr7_slices
mov x8,x5
mov x12,#0
incb x17, ALL, MUL #1
incb x19, ALL, MUL #2
incb x20, ALL, MUL #3
incb x21, ALL, MUL #4
.ukr8_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x17]
st1d {za2v.d[w12, 0]}, p0, [x19]
st1d {za3v.d[w12, 0]}, p0, [x20]
st1d {za4v.d[w12, 0]}, p0, [x21]
incb x2, ALL, MUL #5
incb x17, ALL, MUL #5
incb x19, ALL, MUL #5
incb x20, ALL, MUL #5
incb x21, ALL, MUL #5
add x12,x12,#1
cbnz x8,.ukr8_slices
sub x2,x2,x6
sub x1,x1,x7
sub x2,x2,x6, LSL #2
.ukr10_done:
.ukr0_cases_end:
smstop
ldr x19, [sp]
.cfi_restore x19
ldr x20, [sp, #8]
.cfi_restore x20
ldr x21, [sp, #16]
.cfi_restore x21
ldr d8, [sp, #24]
.cfi_restore d8
ldr d9, [sp, #32]
.cfi_restore d9
ldr d10, [sp, #40]
.cfi_restore d10
ldr d11, [sp, #48]
.cfi_restore d11
ldr d12, [sp, #56]
.cfi_restore d12
ldr d13, [sp, #64]
.cfi_restore d13
ldr d14, [sp, #72]
.cfi_restore d14
ldr d15, [sp, #80]
.cfi_restore d15
add sp,sp,#96
.cfi_adjust_cfa_offset -96
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
add sp,sp,#-112
.cfi_adjust_cfa_offset 112
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
str d8, [sp, #40]
.cfi_rel_offset d8, 40
str d9, [sp, #48]
.cfi_rel_offset d9, 48
str d10, [sp, #56]
.cfi_rel_offset d10, 56
str d11, [sp, #64]
.cfi_rel_offset d11, 64
str d12, [sp, #72]
.cfi_rel_offset d12, 72
str d13, [sp, #80]
.cfi_rel_offset d13, 80
str d14, [sp, #88]
.cfi_rel_offset d14, 88
str d15, [sp, #96]
.cfi_rel_offset d15, 96
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
add x8,x1,x7
add x9,x1,x7
mov x10,x5
mov x12,#0
add x11,x1,x7
add x16,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x17,x1,x7, LSL #2
add x9,x9,x7, LSL #2
.ukr1_slices:
add x10,x10,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x11]
ld1d {za2h.d[w12, 0]}, p0/z, [x16]
ld1d {za3h.d[w12, 0]}, p0/z, [x8]
ld1d {za4h.d[w12, 0]}, p0/z, [x17]
ld1d {za5h.d[w12, 0]}, p0/z, [x9]
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x8,x8,x4
add x17,x17,x4
add x9,x9,x4
add x12,x12,#1
cbnz x10,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr9_last
.ukr9_loop:
add x0,x0,#-1
mov x8,x2
mov x9,x2
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x5
mov x12,#0
incb x8, ALL, MUL #1
incb x9, ALL, MUL #2
incb x10, ALL, MUL #3
incb x11, ALL, MUL #4
incb x16, ALL, MUL #5
incb x1, ALL, MUL #1
.ukr2_slices:
add x17,x17,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x8]
st1d {za2v.d[w12, 0]}, p0, [x9]
st1d {za3v.d[w12, 0]}, p0, [x10]
st1d {za4v.d[w12, 0]}, p0, [x11]
st1d {za5v.d[w12, 0]}, p0, [x16]
incb x2, ALL, MUL #6
incb x8, ALL, MUL #6
incb x9, ALL, MUL #6
incb x10, ALL, MUL #6
incb x11, ALL, MUL #6
incb x16, ALL, MUL #6
add x12,x12,#1
cbnz x17,.ukr2_slices
add x8,x1,x7
add x9,x1,x7
sub x2,x2,x6, LSL #1
mov x10,x5
mov x12,#0
add x11,x1,x7
add x16,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x17,x1,x7, LSL #2
add x9,x9,x7, LSL #2
sub x2,x2,x6, LSL #2
.ukr3_slices:
add x10,x10,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x11]
ld1d {za2h.d[w12, 0]}, p0/z, [x16]
ld1d {za3h.d[w12, 0]}, p0/z, [x8]
ld1d {za4h.d[w12, 0]}, p0/z, [x17]
ld1d {za5h.d[w12, 0]}, p0/z, [x9]
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x8,x8,x4
add x17,x17,x4
add x9,x9,x4
add x12,x12,#1
cbnz x10,.ukr3_slices
sub x1,x1,x7
add x2,x2,x6, LSL #1
add x2,x2,x6, LSL #2
cbnz x0,.ukr9_loop
.ukr9_last:
mov x8,x2
mov x9,x2
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x5
mov x12,#0
incb x8, ALL, MUL #1
incb x9, ALL, MUL #2
incb x10, ALL, MUL #3
incb x11, ALL, MUL #4
incb x16, ALL, MUL #5
.ukr4_slices:
add x17,x17,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x8]
st1d {za2v.d[w12, 0]}, p0, [x9]
st1d {za3v.d[w12, 0]}, p0, [x10]
st1d {za4v.d[w12, 0]}, p0, [x11]
st1d {za5v.d[w12, 0]}, p0, [x16]
incb x2, ALL, MUL #6
incb x8, ALL, MUL #6
incb x9, ALL, MUL #6
incb x10, ALL, MUL #6
incb x11, ALL, MUL #6
incb x16, ALL, MUL #6
add x12,x12,#1
cbnz x17,.ukr4_slices
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
add x8,x1,x7
add x9,x1,x7
mov x10,x5
mov x12,#0
add x11,x1,x7
add x16,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x17,x1,x7, LSL #2
add x9,x9,x7, LSL #2
mov x19,x2
mov x20,x2
mov x21,x2
mov x22,x2
mov x23,x2
.ukr5_slices:
add x10,x10,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x11]
ld1d {z3.d}, p0/z, [x16]
ld1d {z4.d}, p0/z, [x8]
ld1d {z5.d}, p0/z, [x17]
ld1d {z6.d}, p0/z, [x9]
fmul z7.d,z1.d,z0.d
fmul z16.d,z2.d,z0.d
fmul z17.d,z3.d,z0.d
fmul z18.d,z4.d,z0.d
fmul z19.d,z5.d,z0.d
fmul z20.d,z6.d,z0.d
mova za0h.d[w12,0],p0/m,z7.d
mova za1h.d[w12,0],p0/m,z16.d
mova za2h.d[w12,0],p0/m,z17.d
mova za3h.d[w12,0],p0/m,z18.d
mova za4h.d[w12,0],p0/m,z19.d
mova za5h.d[w12,0],p0/m,z20.d
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x8,x8,x4
add x17,x17,x4
add x9,x9,x4
add x12,x12,#1
cbnz x10,.ukr5_slices
mov x8,x5
mov x12,#0
incb x19, ALL, MUL #1
incb x20, ALL, MUL #2
incb x21, ALL, MUL #3
incb x22, ALL, MUL #4
incb x23, ALL, MUL #5
.ukr6_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x19]
st1d {za2v.d[w12, 0]}, p0, [x20]
st1d {za3v.d[w12, 0]}, p0, [x21]
st1d {za4v.d[w12, 0]}, p0, [x22]
st1d {za5v.d[w12, 0]}, p0, [x23]
incb x2, ALL, MUL #6
incb x19, ALL, MUL #6
incb x20, ALL, MUL #6
incb x21, ALL, MUL #6
incb x22, ALL, MUL #6
incb x23, ALL, MUL #6
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
add x8,x1,x7
add x9,x1,x7
mov x10,x5
mov x12,#0
add x11,x1,x7
add x16,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x17,x1,x7, LSL #2
add x9,x9,x7, LSL #2
mov x19,x2
mov x20,x2
mov x21,x2
mov x22,x2
mov x23,x2
.ukr7_slices:
add x10,x10,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x11]
ld1d {z3.d}, p0/z, [x16]
ld1d {z4.d}, p0/z, [x8]
ld1d {z5.d}, p0/z, [x17]
ld1d {z6.d}, p0/z, [x9]
fmul z7.d,z1.d,z0.d
fmul z16.d,z2.d,z0.d
fmul z17.d,z3.d,z0.d
fmul z18.d,z4.d,z0.d
fmul z19.d,z5.d,z0.d
fmul z20.d,z6.d,z0.d
mova za0h.d[w12,0],p0/m,z7.d
mova za1h.d[w12,0],p0/m,z16.d
mova za2h.d[w12,0],p0/m,z17.d
mova za3h.d[w12,0],p0/m,z18.d
mova za4h.d[w12,0],p0/m,z19.d
mova za5h.d[w12,0],p0/m,z20.d
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x8,x8,x4
add x17,x17,x4
add x9,x9,x4
add x12,x12,#1
cbnz x10,.ukr7_slices
mov x8,x5
mov x12,#0
incb x19, ALL, MUL #1
incb x20, ALL, MUL #2
incb x21, ALL, MUL #3
incb x22, ALL, MUL #4
incb x23, ALL, MUL #5
.ukr8_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x19]
st1d {za2v.d[w12, 0]}, p0, [x20]
st1d {za3v.d[w12, 0]}, p0, [x21]
st1d {za4v.d[w12, 0]}, p0, [x22]
st1d {za5v.d[w12, 0]}, p0, [x23]
incb x2, ALL, MUL #6
incb x19, ALL, MUL #6
incb x20, ALL, MUL #6
incb x21, ALL, MUL #6
incb x22, ALL, MUL #6
incb x23, ALL, MUL #6
add x12,x12,#1
cbnz x8,.ukr8_slices
sub x2,x2,x6, LSL #1
sub x1,x1,x7
sub x2,x2,x6, LSL #2
.ukr10_done:
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
ldr d8, [sp, #40]
.cfi_restore d8
ldr d9, [sp, #48]
.cfi_restore d9
ldr d10, [sp, #56]
.cfi_restore d10
ldr d11, [sp, #64]
.cfi_restore d11
ldr d12, [sp, #72]
.cfi_restore d12
ldr d13, [sp, #80]
.cfi_restore d13
ldr d14, [sp, #88]
.cfi_restore d14
ldr d15, [sp, #96]
.cfi_restore d15
add sp,sp,#112
.cfi_adjust_cfa_offset -112
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
add sp,sp,#-128
.cfi_adjust_cfa_offset 128
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
str d8, [sp, #56]
.cfi_rel_offset d8, 56
str d9, [sp, #64]
.cfi_rel_offset d9, 64
str d10, [sp, #72]
.cfi_rel_offset d10, 72
str d11, [sp, #80]
.cfi_rel_offset d11, 80
str d12, [sp, #88]
.cfi_rel_offset d12, 88
str d13, [sp, #96]
.cfi_rel_offset d13, 96
str d14, [sp, #104]
.cfi_rel_offset d14, 104
str d15, [sp, #112]
.cfi_rel_offset d15, 112
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
add x8,x1,x7
add x9,x1,x7
add x10,x1,x7, LSL #1
mov x11,x5
mov x12,#0
add x16,x1,x7
add x17,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x19,x1,x7, LSL #2
add x9,x9,x7, LSL #2
add x10,x10,x7, LSL #2
.ukr1_slices:
add x11,x11,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x16]
ld1d {za2h.d[w12, 0]}, p0/z, [x17]
ld1d {za3h.d[w12, 0]}, p0/z, [x8]
ld1d {za4h.d[w12, 0]}, p0/z, [x19]
ld1d {za5h.d[w12, 0]}, p0/z, [x9]
ld1d {za6h.d[w12, 0]}, p0/z, [x10]
add x1,x1,x4
add x16,x16,x4
add x17,x17,x4
add x8,x8,x4
add x19,x19,x4
add x9,x9,x4
add x10,x10,x4
add x12,x12,#1
cbnz x11,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr9_last
.ukr9_loop:
add x0,x0,#-1
mov x8,x2
mov x9,x2
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x2
mov x19,x5
mov x12,#0
incb x8, ALL, MUL #1
incb x9, ALL, MUL #2
incb x10, ALL, MUL #3
incb x11, ALL, MUL #4
incb x16, ALL, MUL #5
incb x17, ALL, MUL #6
.ukr2_slices:
add x19,x19,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x8]
st1d {za2v.d[w12, 0]}, p0, [x9]
st1d {za3v.d[w12, 0]}, p0, [x10]
st1d {za4v.d[w12, 0]}, p0, [x11]
st1d {za5v.d[w12, 0]}, p0, [x16]
st1d {za6v.d[w12, 0]}, p0, [x17]
incb x2, ALL, MUL #7
incb x8, ALL, MUL #7
incb x9, ALL, MUL #7
incb x10, ALL, MUL #7
incb x11, ALL, MUL #7
incb x16, ALL, MUL #7
incb x17, ALL, MUL #7
add x12,x12,#1
cbnz x19,.ukr2_slices
sub x2,x2,x6
incb x1, ALL, MUL #1
sub x2,x2,x6, LSL #1
add x8,x1,x7
add x9,x1,x7
add x10,x1,x7, LSL #1
sub x2,x2,x6, LSL #2
mov x11,x5
mov x12,#0
add x16,x1,x7
add x17,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x19,x1,x7, LSL #2
add x9,x9,x7, LSL #2
add x10,x10,x7, LSL #2
.ukr3_slices:
add x11,x11,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x16]
ld1d {za2h.d[w12, 0]}, p0/z, [x17]
ld1d {za3h.d[w12, 0]}, p0/z, [x8]
ld1d {za4h.d[w12, 0]}, p0/z, [x19]
ld1d {za5h.d[w12, 0]}, p0/z, [x9]
ld1d {za6h.d[w12, 0]}, p0/z, [x10]
add x1,x1,x4
add x16,x16,x4
add x17,x17,x4
add x8,x8,x4
add x19,x19,x4
add x9,x9,x4
add x10,x10,x4
add x12,x12,#1
cbnz x11,.ukr3_slices
add x2,x2,x6
sub x1,x1,x7
add x2,x2,x6, LSL #1
add x2,x2,x6, LSL #2
cbnz x0,.ukr9_loop
.ukr9_last:
mov x8,x2
mov x9,x2
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x2
mov x19,x5
mov x12,#0
incb x8, ALL, MUL #1
incb x9, ALL, MUL #2
incb x10, ALL, MUL #3
incb x11, ALL, MUL #4
incb x16, ALL, MUL #5
incb x17, ALL, MUL #6
.ukr4_slices:
add x19,x19,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x8]
st1d {za2v.d[w12, 0]}, p0, [x9]
st1d {za3v.d[w12, 0]}, p0, [x10]
st1d {za4v.d[w12, 0]}, p0, [x11]
st1d {za5v.d[w12, 0]}, p0, [x16]
st1d {za6v.d[w12, 0]}, p0, [x17]
incb x2, ALL, MUL #7
incb x8, ALL, MUL #7
incb x9, ALL, MUL #7
incb x10, ALL, MUL #7
incb x11, ALL, MUL #7
incb x16, ALL, MUL #7
incb x17, ALL, MUL #7
add x12,x12,#1
cbnz x19,.ukr4_slices
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
add x8,x1,x7
add x9,x1,x7
add x10,x1,x7, LSL #1
mov x11,x5
mov x12,#0
add x16,x1,x7
add x17,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x19,x1,x7, LSL #2
add x9,x9,x7, LSL #2
add x10,x10,x7, LSL #2
mov x20,x2
mov x21,x2
mov x22,x2
mov x23,x2
mov x24,x2
mov x25,x2
.ukr5_slices:
add x11,x11,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x16]
ld1d {z3.d}, p0/z, [x17]
ld1d {z4.d}, p0/z, [x8]
ld1d {z5.d}, p0/z, [x19]
ld1d {z6.d}, p0/z, [x9]
ld1d {z7.d}, p0/z, [x10]
fmul z16.d,z1.d,z0.d
fmul z17.d,z2.d,z0.d
fmul z18.d,z3.d,z0.d
fmul z19.d,z4.d,z0.d
fmul z20.d,z5.d,z0.d
fmul z21.d,z6.d,z0.d
fmul z22.d,z7.d,z0.d
mova za0h.d[w12,0],p0/m,z16.d
mova za1h.d[w12,0],p0/m,z17.d
mova za2h.d[w12,0],p0/m,z18.d
mova za3h.d[w12,0],p0/m,z19.d
mova za4h.d[w12,0],p0/m,z20.d
mova za5h.d[w12,0],p0/m,z21.d
mova za6h.d[w12,0],p0/m,z22.d
add x1,x1,x4
add x16,x16,x4
add x17,x17,x4
add x8,x8,x4
add x19,x19,x4
add x9,x9,x4
add x10,x10,x4
add x12,x12,#1
cbnz x11,.ukr5_slices
mov x8,x5
mov x12,#0
incb x20, ALL, MUL #1
incb x21, ALL, MUL #2
incb x22, ALL, MUL #3
incb x23, ALL, MUL #4
incb x24, ALL, MUL #5
incb x25, ALL, MUL #6
.ukr6_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x20]
st1d {za2v.d[w12, 0]}, p0, [x21]
st1d {za3v.d[w12, 0]}, p0, [x22]
st1d {za4v.d[w12, 0]}, p0, [x23]
st1d {za5v.d[w12, 0]}, p0, [x24]
st1d {za6v.d[w12, 0]}, p0, [x25]
incb x2, ALL, MUL #7
incb x20, ALL, MUL #7
incb x21, ALL, MUL #7
incb x22, ALL, MUL #7
incb x23, ALL, MUL #7
incb x24, ALL, MUL #7
incb x25, ALL, MUL #7
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
add x8,x1,x7
add x9,x1,x7
add x10,x1,x7, LSL #1
mov x11,x5
mov x12,#0
add x16,x1,x7
add x17,x1,x7, LSL #1
add x8,x8,x7, LSL #1
add x19,x1,x7, LSL #2
add x9,x9,x7, LSL #2
add x10,x10,x7, LSL #2
mov x20,x2
mov x21,x2
mov x22,x2
mov x23,x2
mov x24,x2
mov x25,x2
.ukr7_slices:
add x11,x11,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x16]
ld1d {z3.d}, p0/z, [x17]
ld1d {z4.d}, p0/z, [x8]
ld1d {z5.d}, p0/z, [x19]
ld1d {z6.d}, p0/z, [x9]
ld1d {z7.d}, p0/z, [x10]
fmul z16.d,z1.d,z0.d
fmul z17.d,z2.d,z0.d
fmul z18.d,z3.d,z0.d
fmul z19.d,z4.d,z0.d
fmul z20.d,z5.d,z0.d
fmul z21.d,z6.d,z0.d
fmul z22.d,z7.d,z0.d
mova za0h.d[w12,0],p0/m,z16.d
mova za1h.d[w12,0],p0/m,z17.d
mova za2h.d[w12,0],p0/m,z18.d
mova za3h.d[w12,0],p0/m,z19.d
mova za4h.d[w12,0],p0/m,z20.d
mova za5h.d[w12,0],p0/m,z21.d
mova za6h.d[w12,0],p0/m,z22.d
add x1,x1,x4
add x16,x16,x4
add x17,x17,x4
add x8,x8,x4
add x19,x19,x4
add x9,x9,x4
add x10,x10,x4
add x12,x12,#1
cbnz x11,.ukr7_slices
mov x8,x5
mov x12,#0
incb x20, ALL, MUL #1
incb x21, ALL, MUL #2
incb x22, ALL, MUL #3
incb x23, ALL, MUL #4
incb x24, ALL, MUL #5
incb x25, ALL, MUL #6
.ukr8_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x20]
st1d {za2v.d[w12, 0]}, p0, [x21]
st1d {za3v.d[w12, 0]}, p0, [x22]
st1d {za4v.d[w12, 0]}, p0, [x23]
st1d {za5v.d[w12, 0]}, p0, [x24]
st1d {za6v.d[w12, 0]}, p0, [x25]
incb x2, ALL, MUL #7
incb x20, ALL, MUL #7
incb x21, ALL, MUL #7
incb x22, ALL, MUL #7
incb x23, ALL, MUL #7
incb x24, ALL, MUL #7
incb x25, ALL, MUL #7
add x12,x12,#1
cbnz x8,.ukr8_slices
sub x2,x2,x6
sub x2,x2,x6, LSL #1
sub x1,x1,x7
sub x2,x2,x6, LSL #2
.ukr10_done:
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
ldr d8, [sp, #56]
.cfi_restore d8
ldr d9, [sp, #64]
.cfi_restore d9
ldr d10, [sp, #72]
.cfi_restore d10
ldr d11, [sp, #80]
.cfi_restore d11
ldr d12, [sp, #88]
.cfi_restore d12
ldr d13, [sp, #96]
.cfi_restore d13
ldr d14, [sp, #104]
.cfi_restore d14
ldr d15, [sp, #112]
.cfi_restore d15
add sp,sp,#128
.cfi_adjust_cfa_offset -128
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
add x8,x1,x7
add x9,x1,x7
add x10,x1,x7
add x11,x1,x7, LSL #1
add x8,x8,x7, LSL #1
mov x16,x5
mov x12,#0
add x17,x1,x7
add x19,x1,x7, LSL #1
add x9,x9,x7, LSL #1
add x20,x1,x7, LSL #2
add x10,x10,x7, LSL #2
add x11,x11,x7, LSL #2
add x8,x8,x7, LSL #2
.ukr1_slices:
add x16,x16,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x17]
ld1d {za2h.d[w12, 0]}, p0/z, [x19]
ld1d {za3h.d[w12, 0]}, p0/z, [x9]
ld1d {za4h.d[w12, 0]}, p0/z, [x20]
ld1d {za5h.d[w12, 0]}, p0/z, [x10]
ld1d {za6h.d[w12, 0]}, p0/z, [x11]
ld1d {za7h.d[w12, 0]}, p0/z, [x8]
add x1,x1,x4
add x17,x17,x4
add x19,x19,x4
add x9,x9,x4
add x20,x20,x4
add x10,x10,x4
add x11,x11,x4
add x8,x8,x4
add x12,x12,#1
cbnz x16,.ukr1_slices
sub x1,x1,x7
add x0,x0,#-1
cbz x0,.ukr9_last
.ukr9_loop:
add x0,x0,#-1
incb x1, ALL, MUL #1
mov x8,x2
mov x9,x2
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x2
mov x19,x2
add x20,x1,x7
mov x21,x5
mov x12,#0
incb x8, ALL, MUL #1
incb x9, ALL, MUL #2
incb x10, ALL, MUL #3
incb x11, ALL, MUL #4
incb x16, ALL, MUL #5
incb x17, ALL, MUL #6
incb x19, ALL, MUL #7
add x22,x1,x7
add x23,x1,x7
add x24,x1,x7, LSL #1
add x20,x20,x7, LSL #1
.ukr2_slices:
add x21,x21,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x8]
st1d {za2v.d[w12, 0]}, p0, [x9]
st1d {za3v.d[w12, 0]}, p0, [x10]
st1d {za4v.d[w12, 0]}, p0, [x11]
st1d {za5v.d[w12, 0]}, p0, [x16]
st1d {za6v.d[w12, 0]}, p0, [x17]
st1d {za7v.d[w12, 0]}, p0, [x19]
incb x2, ALL, MUL #8
incb x8, ALL, MUL #8
incb x9, ALL, MUL #8
incb x10, ALL, MUL #8
incb x11, ALL, MUL #8
incb x16, ALL, MUL #8
incb x17, ALL, MUL #8
incb x19, ALL, MUL #8
add x12,x12,#1
cbnz x21,.ukr2_slices
mov x8,x5
mov x12,#0
add x9,x1,x7
add x10,x1,x7, LSL #1
add x22,x22,x7, LSL #1
add x11,x1,x7, LSL #2
add x23,x23,x7, LSL #2
add x24,x24,x7, LSL #2
add x20,x20,x7, LSL #2
.ukr3_slices:
add x8,x8,#-1
ld1d {za0h.d[w12, 0]}, p0/z, [x1]
ld1d {za1h.d[w12, 0]}, p0/z, [x9]
ld1d {za2h.d[w12, 0]}, p0/z, [x10]
ld1d {za3h.d[w12, 0]}, p0/z, [x22]
ld1d {za4h.d[w12, 0]}, p0/z, [x11]
ld1d {za5h.d[w12, 0]}, p0/z, [x23]
ld1d {za6h.d[w12, 0]}, p0/z, [x24]
ld1d {za7h.d[w12, 0]}, p0/z, [x20]
add x1,x1,x4
add x9,x9,x4
add x10,x10,x4
add x22,x22,x4
add x11,x11,x4
add x23,x23,x4
add x24,x24,x4
add x20,x20,x4
add x12,x12,#1
cbnz x8,.ukr3_slices
sub x2,x2,x6, LSL #3
sub x1,x1,x7
add x2,x2,x6, LSL #3
cbnz x0,.ukr9_loop
.ukr9_last:
mov x8,x2
mov x9,x2
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x2
mov x19,x2
mov x20,x5
mov x12,#0
incb x8, ALL, MUL #1
incb x9, ALL, MUL #2
incb x10, ALL, MUL #3
incb x11, ALL, MUL #4
incb x16, ALL, MUL #5
incb x17, ALL, MUL #6
incb x19, ALL, MUL #7
.ukr4_slices:
add x20,x20,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x8]
st1d {za2v.d[w12, 0]}, p0, [x9]
st1d {za3v.d[w12, 0]}, p0, [x10]
st1d {za4v.d[w12, 0]}, p0, [x11]
st1d {za5v.d[w12, 0]}, p0, [x16]
st1d {za6v.d[w12, 0]}, p0, [x17]
st1d {za7v.d[w12, 0]}, p0, [x19]
incb x2, ALL, MUL #8
incb x8, ALL, MUL #8
incb x9, ALL, MUL #8
incb x10, ALL, MUL #8
incb x11, ALL, MUL #8
incb x16, ALL, MUL #8
incb x17, ALL, MUL #8
incb x19, ALL, MUL #8
add x12,x12,#1
cbnz x20,.ukr4_slices
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
add x8,x1,x7
add x9,x1,x7
add x10,x1,x7
add x11,x1,x7, LSL #1
add x8,x8,x7, LSL #1
mov x16,x5
mov x12,#0
add x17,x1,x7
add x19,x1,x7, LSL #1
add x9,x9,x7, LSL #1
add x20,x1,x7, LSL #2
add x10,x10,x7, LSL #2
add x11,x11,x7, LSL #2
add x8,x8,x7, LSL #2
mov x21,x2
mov x22,x2
mov x23,x2
mov x24,x2
mov x25,x2
mov x26,x2
mov x27,x2
.ukr5_slices:
add x16,x16,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x17]
ld1d {z3.d}, p0/z, [x19]
ld1d {z4.d}, p0/z, [x9]
ld1d {z5.d}, p0/z, [x20]
ld1d {z6.d}, p0/z, [x10]
ld1d {z7.d}, p0/z, [x11]
ld1d {z16.d}, p0/z, [x8]
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
add x17,x17,x4
add x19,x19,x4
add x9,x9,x4
add x20,x20,x4
add x10,x10,x4
add x11,x11,x4
add x8,x8,x4
add x12,x12,#1
cbnz x16,.ukr5_slices
mov x8,x5
mov x12,#0
incb x21, ALL, MUL #1
incb x22, ALL, MUL #2
incb x23, ALL, MUL #3
incb x24, ALL, MUL #4
incb x25, ALL, MUL #5
incb x26, ALL, MUL #6
incb x27, ALL, MUL #7
.ukr6_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x21]
st1d {za2v.d[w12, 0]}, p0, [x22]
st1d {za3v.d[w12, 0]}, p0, [x23]
st1d {za4v.d[w12, 0]}, p0, [x24]
st1d {za5v.d[w12, 0]}, p0, [x25]
st1d {za6v.d[w12, 0]}, p0, [x26]
st1d {za7v.d[w12, 0]}, p0, [x27]
incb x2, ALL, MUL #8
incb x21, ALL, MUL #8
incb x22, ALL, MUL #8
incb x23, ALL, MUL #8
incb x24, ALL, MUL #8
incb x25, ALL, MUL #8
incb x26, ALL, MUL #8
incb x27, ALL, MUL #8
add x12,x12,#1
cbnz x8,.ukr6_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #3
incb x1, ALL, MUL #1
add x2,x2,x6, LSL #3
cbnz x0,.ukr10_loop
.ukr10_last:
add x8,x1,x7
add x9,x1,x7
add x10,x1,x7
add x11,x1,x7, LSL #1
add x8,x8,x7, LSL #1
mov x16,x5
mov x12,#0
add x17,x1,x7
add x19,x1,x7, LSL #1
add x9,x9,x7, LSL #1
add x20,x1,x7, LSL #2
add x10,x10,x7, LSL #2
add x11,x11,x7, LSL #2
add x8,x8,x7, LSL #2
mov x21,x2
mov x22,x2
mov x23,x2
mov x24,x2
mov x25,x2
mov x26,x2
mov x27,x2
.ukr7_slices:
add x16,x16,#-1
ld1d {z1.d}, p0/z, [x1]
ld1d {z2.d}, p0/z, [x17]
ld1d {z3.d}, p0/z, [x19]
ld1d {z4.d}, p0/z, [x9]
ld1d {z5.d}, p0/z, [x20]
ld1d {z6.d}, p0/z, [x10]
ld1d {z7.d}, p0/z, [x11]
ld1d {z16.d}, p0/z, [x8]
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
add x17,x17,x4
add x19,x19,x4
add x9,x9,x4
add x20,x20,x4
add x10,x10,x4
add x11,x11,x4
add x8,x8,x4
add x12,x12,#1
cbnz x16,.ukr7_slices
mov x8,x5
mov x12,#0
incb x21, ALL, MUL #1
incb x22, ALL, MUL #2
incb x23, ALL, MUL #3
incb x24, ALL, MUL #4
incb x25, ALL, MUL #5
incb x26, ALL, MUL #6
incb x27, ALL, MUL #7
.ukr8_slices:
add x8,x8,#-1
st1d {za0v.d[w12, 0]}, p0, [x2]
st1d {za1v.d[w12, 0]}, p0, [x21]
st1d {za2v.d[w12, 0]}, p0, [x22]
st1d {za3v.d[w12, 0]}, p0, [x23]
st1d {za4v.d[w12, 0]}, p0, [x24]
st1d {za5v.d[w12, 0]}, p0, [x25]
st1d {za6v.d[w12, 0]}, p0, [x26]
st1d {za7v.d[w12, 0]}, p0, [x27]
incb x2, ALL, MUL #8
incb x21, ALL, MUL #8
incb x22, ALL, MUL #8
incb x23, ALL, MUL #8
incb x24, ALL, MUL #8
incb x25, ALL, MUL #8
incb x26, ALL, MUL #8
incb x27, ALL, MUL #8
add x12,x12,#1
cbnz x8,.ukr8_slices
sub x1,x1,x7
sub x2,x2,x6, LSL #3
.ukr10_done:
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
.size bli_dpackm_ukrgen_sme_pk_ztrans8v_asm, .-bli_dpackm_ukrgen_sme_pk_ztrans8v_asm
.section .note.GNU-stack,"",%progbits
