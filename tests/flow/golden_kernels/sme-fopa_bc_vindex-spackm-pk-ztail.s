### bli_spackm_ukrgen_sme_pk_ztail0vt
.text
.global bli_spackm_ukrgen_sme_pk_ztail0vt_asm
.type bli_spackm_ukrgen_sme_pk_ztail0vt_asm, %function
bli_spackm_ukrgen_sme_pk_ztail0vt_asm:
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
# x0 = n
# x1 = base(X)
# x2 = base(Y)
# x3 = base(kappa)
# x4 = stride(X,m)
# x5 = stride(Y,n)
# x6 = tail(m)
smstart
ptrue p0.s
whilelo p1.s, xzr, x6
cntw x7
mul x8,x7,x5
ldr s0, [x3]
mov x9,#1065353216
fmov s1,w9
fcmp s0,s1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
and x9,x0,#3
lsr x0,x0,#2
cbz x0,.ukr15_done
mov x10,x6
mov x12,#0
mov x11,x1
.ukr1_slices:
add x10,x10,#-1
ld1w {za0h.s[w12, 0]}, p0/z, [x11]
add x11,x11,x4
add x12,x12,#1
cbnz x10,.ukr1_slices
add x0,x0,#-1
cbz x0,.ukr15_last
.ukr15_loop:
add x0,x0,#-1
mov x10,x1
mov x11,x1
mov x16,x1
mov x17,x6
mov x12,#0
incb x10, ALL, MUL #1
incb x11, ALL, MUL #2
incb x16, ALL, MUL #3
add x19,x2,x8
.ukr2_slices:
add x17,x17,#-1
ld1w {za1h.s[w12, 0]}, p0/z, [x10]
ld1w {za2h.s[w12, 0]}, p0/z, [x11]
ld1w {za3h.s[w12, 0]}, p0/z, [x16]
add x10,x10,x4
add x11,x11,x4
add x16,x16,x4
add x12,x12,#1
cbnz x17,.ukr2_slices
mov x10,x7
mov x12,#0
add x11,x2,x8
add x16,x2,x8, LSL #1
add x19,x19,x8, LSL #1
mov x17,x1
.ukr3_slices:
add x10,x10,#-1
st1w {za0v.s[w12, 0]}, p1, [x2]
st1w {za1v.s[w12, 0]}, p1, [x11]
st1w {za2v.s[w12, 0]}, p1, [x16]
st1w {za3v.s[w12, 0]}, p1, [x19]
add x2,x2,x5
add x11,x11,x5
add x16,x16,x5
add x19,x19,x5
add x12,x12,#1
cbnz x10,.ukr3_slices
mov x10,x6
mov x12,#0
incb x17, ALL, MUL #4
sub x2,x2,x8
.ukr4_slices:
add x10,x10,#-1
ld1w {za0h.s[w12, 0]}, p0/z, [x17]
add x17,x17,x4
add x12,x12,#1
cbnz x10,.ukr4_slices
incb x1, ALL, MUL #4
add x2,x2,x8, LSL #2
cbnz x0,.ukr15_loop
.ukr15_last:
mov x10,x1
mov x11,x1
mov x16,x1
mov x17,x6
mov x12,#0
incb x10, ALL, MUL #1
incb x11, ALL, MUL #2
incb x16, ALL, MUL #3
add x19,x2,x8
.ukr5_slices:
add x17,x17,#-1
ld1w {za1h.s[w12, 0]}, p0/z, [x10]
ld1w {za2h.s[w12, 0]}, p0/z, [x11]
ld1w {za3h.s[w12, 0]}, p0/z, [x16]
add x10,x10,x4
add x11,x11,x4
add x16,x16,x4
add x12,x12,#1
cbnz x17,.ukr5_slices
mov x10,x7
mov x12,#0
add x11,x2,x8
add x16,x2,x8, LSL #1
add x19,x19,x8, LSL #1
.ukr6_slices:
add x10,x10,#-1
st1w {za0v.s[w12, 0]}, p1, [x2]
st1w {za1v.s[w12, 0]}, p1, [x11]
st1w {za2v.s[w12, 0]}, p1, [x16]
st1w {za3v.s[w12, 0]}, p1, [x19]
add x2,x2,x5
add x11,x11,x5
add x16,x16,x5
add x19,x19,x5
add x12,x12,#1
cbnz x10,.ukr6_slices
sub x2,x2,x8
incb x1, ALL, MUL #4
add x2,x2,x8, LSL #2
.ukr15_done:
cbz x9,.ukr15_taildone
.ukr15_tail:
add x9,x9,#-1
mov x10,x6
mov x12,#0
mov x11,x1
.ukr7_slices:
add x10,x10,#-1
ld1w {za0h.s[w12, 0]}, p0/z, [x11]
add x11,x11,x4
add x12,x12,#1
cbnz x10,.ukr7_slices
mov x10,x7
mov x12,#0
.ukr8_slices:
add x10,x10,#-1
st1w {za0v.s[w12, 0]}, p1, [x2]
add x2,x2,x5
add x12,x12,#1
cbnz x10,.ukr8_slices
sub x2,x2,x8
incb x1, ALL, MUL #1
add x2,x2,x8
cbnz x9,.ukr15_tail
.ukr15_taildone:
b .ukr0_cases_end
.ukr0_case1:
and x9,x0,#3
lsr x0,x0,#2
ld1rw {z0.s}, p0/z, [x3]
cbz x0,.ukr16_done
add x0,x0,#-1
cbz x0,.ukr16_last
.ukr16_loop:
add x0,x0,#-1
mov x10,x1
mov x11,x1
mov x16,x1
mov x17,x6
mov x12,#0
mov x19,x1
incb x10, ALL, MUL #1
incb x11, ALL, MUL #2
incb x16, ALL, MUL #3
add x20,x2,x8
.ukr9_slices:
add x17,x17,#-1
ld1w {z1.s}, p0/z, [x19]
ld1w {z2.s}, p0/z, [x10]
ld1w {z3.s}, p0/z, [x11]
ld1w {z4.s}, p0/z, [x16]
fmul z5.s,z1.s,z0.s
fmul z1.s,z2.s,z0.s
fmul z2.s,z3.s,z0.s
fmul z3.s,z4.s,z0.s
mova za0h.s[w12,0],p0/m,z5.s
mova za1h.s[w12,0],p0/m,z1.s
mova za2h.s[w12,0],p0/m,z2.s
mova za3h.s[w12,0],p0/m,z3.s
add x19,x19,x4
add x10,x10,x4
add x11,x11,x4
add x16,x16,x4
add x12,x12,#1
cbnz x17,.ukr9_slices
mov x10,x7
mov x12,#0
add x11,x2,x8
add x16,x2,x8, LSL #1
add x20,x20,x8, LSL #1
.ukr10_slices:
add x10,x10,#-1
st1w {za0v.s[w12, 0]}, p1, [x2]
st1w {za1v.s[w12, 0]}, p1, [x11]
st1w {za2v.s[w12, 0]}, p1, [x16]
st1w {za3v.s[w12, 0]}, p1, [x20]
add x2,x2,x5
add x11,x11,x5
add x16,x16,x5
add x20,x20,x5
add x12,x12,#1
cbnz x10,.ukr10_slices
sub x2,x2,x8
incb x1, ALL, MUL #4
add x2,x2,x8, LSL #2
cbnz x0,.ukr16_loop
.ukr16_last:
mov x10,x1
mov x11,x1
mov x16,x1
mov x17,x6
mov x12,#0
mov x19,x1
incb x10, ALL, MUL #1
incb x11, ALL, MUL #2
incb x16, ALL, MUL #3
add x20,x2,x8
.ukr11_slices:
add x17,x17,#-1
ld1w {z1.s}, p0/z, [x19]
ld1w {z2.s}, p0/z, [x10]
ld1w {z3.s}, p0/z, [x11]
ld1w {z4.s}, p0/z, [x16]
fmul z5.s,z1.s,z0.s
fmul z1.s,z2.s,z0.s
fmul z2.s,z3.s,z0.s
fmul z3.s,z4.s,z0.s
mova za0h.s[w12,0],p0/m,z5.s
mova za1h.s[w12,0],p0/m,z1.s
mova za2h.s[w12,0],p0/m,z2.s
mova za3h.s[w12,0],p0/m,z3.s
add x19,x19,x4
add x10,x10,x4
add x11,x11,x4
add x16,x16,x4
add x12,x12,#1
cbnz x17,.ukr11_slices
mov x10,x7
mov x12,#0
add x11,x2,x8
add x16,x2,x8, LSL #1
add x20,x20,x8, LSL #1
.ukr12_slices:
add x10,x10,#-1
st1w {za0v.s[w12, 0]}, p1, [x2]
st1w {za1v.s[w12, 0]}, p1, [x11]
st1w {za2v.s[w12, 0]}, p1, [x16]
st1w {za3v.s[w12, 0]}, p1, [x20]
add x2,x2,x5
add x11,x11,x5
add x16,x16,x5
add x20,x20,x5
add x12,x12,#1
cbnz x10,.ukr12_slices
sub x2,x2,x8
incb x1, ALL, MUL #4
add x2,x2,x8, LSL #2
.ukr16_done:
cbz x9,.ukr16_taildone
.ukr16_tail:
add x9,x9,#-1
mov x10,x6
mov x12,#0
mov x11,x1
.ukr13_slices:
add x10,x10,#-1
ld1w {z1.s}, p0/z, [x11]
fmul z2.s,z1.s,z0.s
mova za0h.s[w12,0],p0/m,z2.s
add x11,x11,x4
add x12,x12,#1
cbnz x10,.ukr13_slices
mov x10,x7
mov x12,#0
.ukr14_slices:
add x10,x10,#-1
st1w {za0v.s[w12, 0]}, p1, [x2]
add x2,x2,x5
add x12,x12,#1
cbnz x10,.ukr14_slices
sub x2,x2,x8
incb x1, ALL, MUL #1
add x2,x2,x8
cbnz x9,.ukr16_tail
.ukr16_taildone:
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
.size bli_spackm_ukrgen_sme_pk_ztail0vt_asm, .-bli_spackm_ukrgen_sme_pk_ztail0vt_asm
.section .note.GNU-stack,"",%progbits


### bli_spackm_ukrgen_sme_pk_ztail1vt
.text
.global bli_spackm_ukrgen_sme_pk_ztail1vt_asm
.type bli_spackm_ukrgen_sme_pk_ztail1vt_asm, %function
bli_spackm_ukrgen_sme_pk_ztail1vt_asm:
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
# x0 = n
# x1 = base(X)
# x2 = base(Y)
# x3 = base(kappa)
# x4 = stride(X,m)
# x5 = stride(Y,n)
# x6 = tail(m)
smstart
ptrue p0.s
whilelo p1.s, xzr, x6
cntw x7
mul x8,x7,x4
mul x9,x7,x5
ldr s0, [x3]
mov x10,#1065353216
fmov s1,w10
fcmp s0,s1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
and x10,x0,#1
lsr x0,x0,#1
cbz x0,.ukr23_done
mov x11,x7
mov x12,#0
.ukr1_slices:
add x11,x11,#-1
ld1w {za0h.s[w12, 0]}, p0/z, [x1]
add x1,x1,x4
add x12,x12,#1
cbnz x11,.ukr1_slices
sub x1,x1,x8
mov x11,x6
mov x12,#0
add x16,x1,x8
.ukr2_slices:
add x11,x11,#-1
ld1w {za1h.s[w12, 0]}, p0/z, [x16]
add x16,x16,x4
add x12,x12,#1
cbnz x11,.ukr2_slices
add x0,x0,#-1
cbz x0,.ukr23_last
.ukr23_loop:
add x0,x0,#-1
incb x1, ALL, MUL #1
mov x11,x7
mov x12,#0
.ukr3_slices:
add x11,x11,#-1
ld1w {za2h.s[w12, 0]}, p0/z, [x1]
add x1,x1,x4
add x12,x12,#1
cbnz x11,.ukr3_slices
sub x1,x1,x8
mov x11,x2
mov x16,x6
mov x12,#0
add x17,x1,x8
mov x19,x2
incb x11, ALL, MUL #1
.ukr4_slices:
add x16,x16,#-1
ld1w {za3h.s[w12, 0]}, p0/z, [x17]
add x17,x17,x4
add x12,x12,#1
cbnz x16,.ukr4_slices
mov x16,x7
mov x12,#0
incb x19, ALL, MUL #1
add x17,x2,x9
add x11,x11,x9
.ukr5_slices:
add x16,x16,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za1v.s[w12, 0]}, p1, [x19]
st1w {za2v.s[w12, 0]}, p0, [x17]
st1w {za3v.s[w12, 0]}, p1, [x11]
add x2,x2,x5
add x19,x19,x5
add x17,x17,x5
add x11,x11,x5
add x12,x12,#1
cbnz x16,.ukr5_slices
incb x1, ALL, MUL #1
mov x11,x7
mov x12,#0
.ukr6_slices:
add x11,x11,#-1
ld1w {za0h.s[w12, 0]}, p0/z, [x1]
add x1,x1,x4
add x12,x12,#1
cbnz x11,.ukr6_slices
sub x1,x1,x8
mov x11,x6
mov x12,#0
add x16,x1,x8
sub x2,x2,x9
.ukr7_slices:
add x11,x11,#-1
ld1w {za1h.s[w12, 0]}, p0/z, [x16]
add x16,x16,x4
add x12,x12,#1
cbnz x11,.ukr7_slices
add x2,x2,x9, LSL #1
cbnz x0,.ukr23_loop
.ukr23_last:
incb x1, ALL, MUL #1
mov x11,x7
mov x12,#0
.ukr8_slices:
add x11,x11,#-1
ld1w {za2h.s[w12, 0]}, p0/z, [x1]
add x1,x1,x4
add x12,x12,#1
cbnz x11,.ukr8_slices
sub x1,x1,x8
mov x11,x2
mov x16,x6
mov x12,#0
add x17,x1,x8
mov x19,x2
incb x11, ALL, MUL #1
.ukr9_slices:
add x16,x16,#-1
ld1w {za3h.s[w12, 0]}, p0/z, [x17]
add x17,x17,x4
add x12,x12,#1
cbnz x16,.ukr9_slices
mov x16,x7
mov x12,#0
incb x19, ALL, MUL #1
add x17,x2,x9
add x11,x11,x9
.ukr10_slices:
add x16,x16,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za1v.s[w12, 0]}, p1, [x19]
st1w {za2v.s[w12, 0]}, p0, [x17]
st1w {za3v.s[w12, 0]}, p1, [x11]
add x2,x2,x5
add x19,x19,x5
add x17,x17,x5
add x11,x11,x5
add x12,x12,#1
cbnz x16,.ukr10_slices
sub x2,x2,x9
incb x1, ALL, MUL #1
add x2,x2,x9, LSL #1
.ukr23_done:
cbz x10,.ukr23_taildone
.ukr23_tail:
add x10,x10,#-1
mov x11,x7
mov x12,#0
.ukr11_slices:
add x11,x11,#-1
ld1w {za0h.s[w12, 0]}, p0/z, [x1]
add x1,x1,x4
add x12,x12,#1
cbnz x11,.ukr11_slices
sub x1,x1,x8
mov x11,x6
mov x12,#0
add x16,x1,x8
mov x17,x2
.ukr12_slices:
add x11,x11,#-1
ld1w {za1h.s[w12, 0]}, p0/z, [x16]
add x16,x16,x4
add x12,x12,#1
cbnz x11,.ukr12_slices
mov x11,x7
mov x12,#0
incb x17, ALL, MUL #1
.ukr13_slices:
add x11,x11,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za1v.s[w12, 0]}, p1, [x17]
add x2,x2,x5
add x17,x17,x5
add x12,x12,#1
cbnz x11,.ukr13_slices
sub x2,x2,x9
incb x1, ALL, MUL #1
add x2,x2,x9
cbnz x10,.ukr23_tail
.ukr23_taildone:
b .ukr0_cases_end
.ukr0_case1:
and x10,x0,#1
lsr x0,x0,#1
ld1rw {z0.s}, p0/z, [x3]
cbz x0,.ukr24_done
add x0,x0,#-1
cbz x0,.ukr24_last
.ukr24_loop:
add x0,x0,#-1
mov x11,x7
mov x12,#0
.ukr14_slices:
add x11,x11,#-1
ld1w {z1.s}, p0/z, [x1]
ld1w {z2.s}, p0/z, [x1, #1, MUL VL]
fmul z3.s,z1.s,z0.s
fmul z1.s,z2.s,z0.s
mova za0h.s[w12,0],p0/m,z3.s
mova za1h.s[w12,0],p0/m,z1.s
add x1,x1,x4
add x12,x12,#1
cbnz x11,.ukr14_slices
sub x1,x1,x8
mov x11,x1
incb x11, ALL, MUL #1
mov x16,x2
mov x17,x6
mov x12,#0
add x19,x1,x8
add x11,x11,x8
mov x20,x2
incb x16, ALL, MUL #1
.ukr15_slices:
add x17,x17,#-1
ld1w {z1.s}, p0/z, [x19]
ld1w {z2.s}, p0/z, [x11]
fmul z3.s,z1.s,z0.s
fmul z1.s,z2.s,z0.s
mova za2h.s[w12,0],p0/m,z3.s
mova za3h.s[w12,0],p0/m,z1.s
add x19,x19,x4
add x11,x11,x4
add x12,x12,#1
cbnz x17,.ukr15_slices
mov x11,x7
mov x12,#0
incb x20, ALL, MUL #1
add x17,x2,x9
add x16,x16,x9
.ukr16_slices:
add x11,x11,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za2v.s[w12, 0]}, p1, [x20]
st1w {za1v.s[w12, 0]}, p0, [x17]
st1w {za3v.s[w12, 0]}, p1, [x16]
add x2,x2,x5
add x20,x20,x5
add x17,x17,x5
add x16,x16,x5
add x12,x12,#1
cbnz x11,.ukr16_slices
sub x2,x2,x9
incb x1, ALL, MUL #2
add x2,x2,x9, LSL #1
cbnz x0,.ukr24_loop
.ukr24_last:
mov x11,x7
mov x12,#0
.ukr17_slices:
add x11,x11,#-1
ld1w {z1.s}, p0/z, [x1]
ld1w {z2.s}, p0/z, [x1, #1, MUL VL]
fmul z3.s,z1.s,z0.s
fmul z1.s,z2.s,z0.s
mova za0h.s[w12,0],p0/m,z3.s
mova za1h.s[w12,0],p0/m,z1.s
add x1,x1,x4
add x12,x12,#1
cbnz x11,.ukr17_slices
sub x1,x1,x8
mov x11,x1
incb x11, ALL, MUL #1
mov x16,x2
mov x17,x6
mov x12,#0
add x19,x1,x8
add x11,x11,x8
mov x20,x2
incb x16, ALL, MUL #1
.ukr18_slices:
add x17,x17,#-1
ld1w {z1.s}, p0/z, [x19]
ld1w {z2.s}, p0/z, [x11]
fmul z3.s,z1.s,z0.s
fmul z1.s,z2.s,z0.s
mova za2h.s[w12,0],p0/m,z3.s
mova za3h.s[w12,0],p0/m,z1.s
add x19,x19,x4
add x11,x11,x4
add x12,x12,#1
cbnz x17,.ukr18_slices
mov x11,x7
mov x12,#0
incb x20, ALL, MUL #1
add x17,x2,x9
add x16,x16,x9
.ukr19_slices:
add x11,x11,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za2v.s[w12, 0]}, p1, [x20]
st1w {za1v.s[w12, 0]}, p0, [x17]
st1w {za3v.s[w12, 0]}, p1, [x16]
add x2,x2,x5
add x20,x20,x5
add x17,x17,x5
add x16,x16,x5
add x12,x12,#1
cbnz x11,.ukr19_slices
sub x2,x2,x9
incb x1, ALL, MUL #2
add x2,x2,x9, LSL #1
.ukr24_done:
cbz x10,.ukr24_taildone
.ukr24_tail:
add x10,x10,#-1
mov x11,x7
mov x12,#0
.ukr20_slices:
add x11,x11,#-1
ld1w {z1.s}, p0/z, [x1]
fmul z2.s,z1.s,z0.s
mova za0h.s[w12,0],p0/m,z2.s
add x1,x1,x4
add x12,x12,#1
cbnz x11,.ukr20_slices
sub x1,x1,x8
mov x11,x6
mov x12,#0
add x16,x1,x8
mov x17,x2
.ukr21_slices:
add x11,x11,#-1
ld1w {z1.s}, p0/z, [x16]
fmul z2.s,z1.s,z0.s
mova za2h.s[w12,0],p0/m,z2.s
add x16,x16,x4
add x12,x12,#1
cbnz x11,.ukr21_slices
mov x11,x7
mov x12,#0
incb x17, ALL, MUL #1
.ukr22_slices:
add x11,x11,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za2v.s[w12, 0]}, p1, [x17]
add x2,x2,x5
add x17,x17,x5
add x12,x12,#1
cbnz x11,.ukr22_slices
sub x2,x2,x9
incb x1, ALL, MUL #1
add x2,x2,x9
cbnz x10,.ukr24_tail
.ukr24_taildone:
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
.size bli_spackm_ukrgen_sme_pk_ztail1vt_asm, .-bli_spackm_ukrgen_sme_pk_ztail1vt_asm
.section .note.GNU-stack,"",%progbits


### bli_spackm_ukrgen_sme_pk_ztail2vt
.text
.global bli_spackm_ukrgen_sme_pk_ztail2vt_asm
.type bli_spackm_ukrgen_sme_pk_ztail2vt_asm, %function
bli_spackm_ukrgen_sme_pk_ztail2vt_asm:
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
# x5 = stride(Y,n)
# x6 = tail(m)
smstart
ptrue p0.s
whilelo p1.s, xzr, x6
cntw x7
mul x8,x7,x4
mul x9,x7,x5
ldr s0, [x3]
mov x10,#1065353216
fmov s1,w10
fcmp s0,s1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
cbz x0,.ukr13_done
mov x10,x7
mov x12,#0
add x11,x1,x8
.ukr1_slices:
add x10,x10,#-1
ld1w {za0h.s[w12, 0]}, p0/z, [x1]
ld1w {za1h.s[w12, 0]}, p0/z, [x11]
add x1,x1,x4
add x11,x11,x4
add x12,x12,#1
cbnz x10,.ukr1_slices
sub x1,x1,x8
mov x10,x6
mov x12,#0
add x11,x1,x8, LSL #1
.ukr2_slices:
add x10,x10,#-1
ld1w {za2h.s[w12, 0]}, p0/z, [x11]
add x11,x11,x4
add x12,x12,#1
cbnz x10,.ukr2_slices
add x0,x0,#-1
cbz x0,.ukr13_last
.ukr13_loop:
add x0,x0,#-1
mov x10,x2
mov x11,x2
mov x16,x7
mov x12,#0
incb x10, ALL, MUL #1
incb x11, ALL, MUL #2
incb x1, ALL, MUL #1
.ukr3_slices:
add x16,x16,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za1v.s[w12, 0]}, p0, [x10]
st1w {za2v.s[w12, 0]}, p1, [x11]
add x2,x2,x5
add x10,x10,x5
add x11,x11,x5
add x12,x12,#1
cbnz x16,.ukr3_slices
mov x10,x7
mov x12,#0
add x11,x1,x8
.ukr4_slices:
add x10,x10,#-1
ld1w {za0h.s[w12, 0]}, p0/z, [x1]
ld1w {za1h.s[w12, 0]}, p0/z, [x11]
add x1,x1,x4
add x11,x11,x4
add x12,x12,#1
cbnz x10,.ukr4_slices
sub x1,x1,x8
mov x10,x6
mov x12,#0
add x11,x1,x8, LSL #1
sub x2,x2,x9
.ukr5_slices:
add x10,x10,#-1
ld1w {za2h.s[w12, 0]}, p0/z, [x11]
add x11,x11,x4
add x12,x12,#1
cbnz x10,.ukr5_slices
add x2,x2,x9
cbnz x0,.ukr13_loop
.ukr13_last:
mov x10,x2
mov x11,x2
mov x16,x7
mov x12,#0
incb x10, ALL, MUL #1
incb x11, ALL, MUL #2
.ukr6_slices:
add x16,x16,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za1v.s[w12, 0]}, p0, [x10]
st1w {za2v.s[w12, 0]}, p1, [x11]
add x2,x2,x5
add x10,x10,x5
add x11,x11,x5
add x12,x12,#1
cbnz x16,.ukr6_slices
sub x2,x2,x9
.ukr13_done:
b .ukr0_cases_end
.ukr0_case1:
ld1rw {z0.s}, p0/z, [x3]
cbz x0,.ukr14_done
add x0,x0,#-1
cbz x0,.ukr14_last
.ukr14_loop:
add x0,x0,#-1
mov x10,x7
mov x12,#0
add x11,x1,x8
.ukr7_slices:
add x10,x10,#-1
ld1w {z1.s}, p0/z, [x1]
ld1w {z2.s}, p0/z, [x11]
fmul z3.s,z1.s,z0.s
fmul z1.s,z2.s,z0.s
mova za0h.s[w12,0],p0/m,z3.s
mova za1h.s[w12,0],p0/m,z1.s
add x1,x1,x4
add x11,x11,x4
add x12,x12,#1
cbnz x10,.ukr7_slices
sub x1,x1,x8
mov x10,x6
mov x12,#0
add x11,x1,x8, LSL #1
mov x16,x2
mov x17,x2
.ukr8_slices:
add x10,x10,#-1
ld1w {z1.s}, p0/z, [x11]
fmul z2.s,z1.s,z0.s
mova za2h.s[w12,0],p0/m,z2.s
add x11,x11,x4
add x12,x12,#1
cbnz x10,.ukr8_slices
mov x10,x7
mov x12,#0
incb x16, ALL, MUL #1
incb x17, ALL, MUL #2
.ukr9_slices:
add x10,x10,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za1v.s[w12, 0]}, p0, [x16]
st1w {za2v.s[w12, 0]}, p1, [x17]
add x2,x2,x5
add x16,x16,x5
add x17,x17,x5
add x12,x12,#1
cbnz x10,.ukr9_slices
sub x2,x2,x9
incb x1, ALL, MUL #1
add x2,x2,x9
cbnz x0,.ukr14_loop
.ukr14_last:
mov x10,x7
mov x12,#0
add x11,x1,x8
.ukr10_slices:
add x10,x10,#-1
ld1w {z1.s}, p0/z, [x1]
ld1w {z2.s}, p0/z, [x11]
fmul z3.s,z1.s,z0.s
fmul z1.s,z2.s,z0.s
mova za0h.s[w12,0],p0/m,z3.s
mova za1h.s[w12,0],p0/m,z1.s
add x1,x1,x4
add x11,x11,x4
add x12,x12,#1
cbnz x10,.ukr10_slices
sub x1,x1,x8
mov x10,x6
mov x12,#0
add x11,x1,x8, LSL #1
mov x16,x2
mov x17,x2
.ukr11_slices:
add x10,x10,#-1
ld1w {z1.s}, p0/z, [x11]
fmul z2.s,z1.s,z0.s
mova za2h.s[w12,0],p0/m,z2.s
add x11,x11,x4
add x12,x12,#1
cbnz x10,.ukr11_slices
mov x10,x7
mov x12,#0
incb x16, ALL, MUL #1
incb x17, ALL, MUL #2
.ukr12_slices:
add x10,x10,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za1v.s[w12, 0]}, p0, [x16]
st1w {za2v.s[w12, 0]}, p1, [x17]
add x2,x2,x5
add x16,x16,x5
add x17,x17,x5
add x12,x12,#1
cbnz x10,.ukr12_slices
sub x2,x2,x9
.ukr14_done:
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
.size bli_spackm_ukrgen_sme_pk_ztail2vt_asm, .-bli_spackm_ukrgen_sme_pk_ztail2vt_asm
.section .note.GNU-stack,"",%progbits


### bli_spackm_ukrgen_sme_pk_ztail3vt
.text
.global bli_spackm_ukrgen_sme_pk_ztail3vt_asm
.type bli_spackm_ukrgen_sme_pk_ztail3vt_asm, %function
bli_spackm_ukrgen_sme_pk_ztail3vt_asm:
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
# x0 = n
# x1 = base(X)
# x2 = base(Y)
# x3 = base(kappa)
# x4 = stride(X,m)
# x5 = stride(Y,n)
# x6 = tail(m)
smstart
ptrue p0.s
whilelo p1.s, xzr, x6
cntw x7
mul x8,x7,x4
mul x9,x7,x5
ldr s0, [x3]
mov x10,#1065353216
fmov s1,w10
fcmp s0,s1
b.ne .ukr0_try0
b .ukr0_case0
.ukr0_try0:
b .ukr0_case1
b .ukr0_cases_end
.ukr0_case0:
cbz x0,.ukr13_done
mov x10,x7
mov x12,#0
add x11,x1,x8
add x16,x1,x8, LSL #1
.ukr1_slices:
add x10,x10,#-1
ld1w {za0h.s[w12, 0]}, p0/z, [x1]
ld1w {za1h.s[w12, 0]}, p0/z, [x11]
ld1w {za2h.s[w12, 0]}, p0/z, [x16]
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x12,x12,#1
cbnz x10,.ukr1_slices
sub x1,x1,x8
add x10,x1,x8
mov x11,x6
mov x12,#0
add x10,x10,x8, LSL #1
.ukr2_slices:
add x11,x11,#-1
ld1w {za3h.s[w12, 0]}, p0/z, [x10]
add x10,x10,x4
add x12,x12,#1
cbnz x11,.ukr2_slices
add x0,x0,#-1
cbz x0,.ukr13_last
.ukr13_loop:
add x0,x0,#-1
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x7
mov x12,#0
incb x10, ALL, MUL #1
incb x11, ALL, MUL #2
incb x16, ALL, MUL #3
incb x1, ALL, MUL #1
.ukr3_slices:
add x17,x17,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za1v.s[w12, 0]}, p0, [x10]
st1w {za2v.s[w12, 0]}, p0, [x11]
st1w {za3v.s[w12, 0]}, p1, [x16]
add x2,x2,x5
add x10,x10,x5
add x11,x11,x5
add x16,x16,x5
add x12,x12,#1
cbnz x17,.ukr3_slices
mov x10,x7
mov x12,#0
add x11,x1,x8
add x16,x1,x8, LSL #1
.ukr4_slices:
add x10,x10,#-1
ld1w {za0h.s[w12, 0]}, p0/z, [x1]
ld1w {za1h.s[w12, 0]}, p0/z, [x11]
ld1w {za2h.s[w12, 0]}, p0/z, [x16]
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x12,x12,#1
cbnz x10,.ukr4_slices
sub x1,x1,x8
add x10,x1,x8
mov x11,x6
mov x12,#0
add x10,x10,x8, LSL #1
sub x2,x2,x9
.ukr5_slices:
add x11,x11,#-1
ld1w {za3h.s[w12, 0]}, p0/z, [x10]
add x10,x10,x4
add x12,x12,#1
cbnz x11,.ukr5_slices
add x2,x2,x9
cbnz x0,.ukr13_loop
.ukr13_last:
mov x10,x2
mov x11,x2
mov x16,x2
mov x17,x7
mov x12,#0
incb x10, ALL, MUL #1
incb x11, ALL, MUL #2
incb x16, ALL, MUL #3
.ukr6_slices:
add x17,x17,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za1v.s[w12, 0]}, p0, [x10]
st1w {za2v.s[w12, 0]}, p0, [x11]
st1w {za3v.s[w12, 0]}, p1, [x16]
add x2,x2,x5
add x10,x10,x5
add x11,x11,x5
add x16,x16,x5
add x12,x12,#1
cbnz x17,.ukr6_slices
sub x2,x2,x9
.ukr13_done:
b .ukr0_cases_end
.ukr0_case1:
ld1rw {z0.s}, p0/z, [x3]
cbz x0,.ukr14_done
add x0,x0,#-1
cbz x0,.ukr14_last
.ukr14_loop:
add x0,x0,#-1
mov x10,x7
mov x12,#0
add x11,x1,x8
add x16,x1,x8, LSL #1
.ukr7_slices:
add x10,x10,#-1
ld1w {z1.s}, p0/z, [x1]
ld1w {z2.s}, p0/z, [x11]
ld1w {z3.s}, p0/z, [x16]
fmul z4.s,z1.s,z0.s
fmul z1.s,z2.s,z0.s
fmul z2.s,z3.s,z0.s
mova za0h.s[w12,0],p0/m,z4.s
mova za1h.s[w12,0],p0/m,z1.s
mova za2h.s[w12,0],p0/m,z2.s
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x12,x12,#1
cbnz x10,.ukr7_slices
sub x1,x1,x8
add x10,x1,x8
mov x11,x6
mov x12,#0
add x10,x10,x8, LSL #1
mov x16,x2
mov x17,x2
mov x19,x2
.ukr8_slices:
add x11,x11,#-1
ld1w {z1.s}, p0/z, [x10]
fmul z2.s,z1.s,z0.s
mova za3h.s[w12,0],p0/m,z2.s
add x10,x10,x4
add x12,x12,#1
cbnz x11,.ukr8_slices
mov x10,x7
mov x12,#0
incb x16, ALL, MUL #1
incb x17, ALL, MUL #2
incb x19, ALL, MUL #3
.ukr9_slices:
add x10,x10,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za1v.s[w12, 0]}, p0, [x16]
st1w {za2v.s[w12, 0]}, p0, [x17]
st1w {za3v.s[w12, 0]}, p1, [x19]
add x2,x2,x5
add x16,x16,x5
add x17,x17,x5
add x19,x19,x5
add x12,x12,#1
cbnz x10,.ukr9_slices
sub x2,x2,x9
incb x1, ALL, MUL #1
add x2,x2,x9
cbnz x0,.ukr14_loop
.ukr14_last:
mov x10,x7
mov x12,#0
add x11,x1,x8
add x16,x1,x8, LSL #1
.ukr10_slices:
add x10,x10,#-1
ld1w {z1.s}, p0/z, [x1]
ld1w {z2.s}, p0/z, [x11]
ld1w {z3.s}, p0/z, [x16]
fmul z4.s,z1.s,z0.s
fmul z1.s,z2.s,z0.s
fmul z2.s,z3.s,z0.s
mova za0h.s[w12,0],p0/m,z4.s
mova za1h.s[w12,0],p0/m,z1.s
mova za2h.s[w12,0],p0/m,z2.s
add x1,x1,x4
add x11,x11,x4
add x16,x16,x4
add x12,x12,#1
cbnz x10,.ukr10_slices
sub x1,x1,x8
add x10,x1,x8
mov x11,x6
mov x12,#0
add x10,x10,x8, LSL #1
mov x16,x2
mov x17,x2
mov x19,x2
.ukr11_slices:
add x11,x11,#-1
ld1w {z1.s}, p0/z, [x10]
fmul z2.s,z1.s,z0.s
mova za3h.s[w12,0],p0/m,z2.s
add x10,x10,x4
add x12,x12,#1
cbnz x11,.ukr11_slices
mov x10,x7
mov x12,#0
incb x16, ALL, MUL #1
incb x17, ALL, MUL #2
incb x19, ALL, MUL #3
.ukr12_slices:
add x10,x10,#-1
st1w {za0v.s[w12, 0]}, p0, [x2]
st1w {za1v.s[w12, 0]}, p0, [x16]
st1w {za2v.s[w12, 0]}, p0, [x17]
st1w {za3v.s[w12, 0]}, p1, [x19]
add x2,x2,x5
add x16,x16,x5
add x17,x17,x5
add x19,x19,x5
add x12,x12,#1
cbnz x10,.ukr12_slices
sub x2,x2,x9
.ukr14_done:
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
.size bli_spackm_ukrgen_sme_pk_ztail3vt_asm, .-bli_spackm_ukrgen_sme_pk_ztail3vt_asm
.section .note.GNU-stack,"",%progbits
