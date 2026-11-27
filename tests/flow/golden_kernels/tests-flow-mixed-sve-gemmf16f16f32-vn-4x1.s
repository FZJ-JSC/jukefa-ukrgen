.text
.global gemmf16f16f32_sve_vn_4x1v
.type gemmf16f16f32_sve_vn_4x1v, %function
gemmf16f16f32_sve_vn_4x1v:
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
ptrue p0.h
and x7,x0,#3
lsr x0,x0,#2
dup z0.s,#0
dup z2.s,#0
dup z4.s,#0
dup z6.s,#0
dup z1.s,#0
dup z3.s,#0
dup z5.s,#0
dup z7.s,#0
cbz x0,.ukr1_done
ld1rh {z16.h}, p0/z, [x1]
ld1rh {z17.h}, p0/z, [x1, #2]
ld1rh {z18.h}, p0/z, [x1, #4]
ld1rh {z19.h}, p0/z, [x1, #6]
ld1h {z20.h}, p0/z, [x2]
add x1,x1,#8
incb x2, ALL, MUL #1
add x0,x0,#-1
cbz x0,.ukr1_last
.ukr1_loop:
add x0,x0,#-1
fmlalb z0.s,z20.h,z16.h
fmlalb z2.s,z20.h,z17.h
fmlalb z4.s,z20.h,z18.h
fmlalb z6.s,z20.h,z19.h
fmlalt z1.s,z20.h,z16.h
fmlalt z3.s,z20.h,z17.h
fmlalt z5.s,z20.h,z18.h
fmlalt z7.s,z20.h,z19.h
ld1rh {z21.h}, p0/z, [x1]
ld1h {z22.h}, p0/z, [x2]
ld1rh {z23.h}, p0/z, [x1, #2]
ld1rh {z24.h}, p0/z, [x1, #4]
ld1rh {z25.h}, p0/z, [x1, #6]
fmlalb z0.s,z22.h,z21.h
fmlalb z2.s,z22.h,z23.h
fmlalb z4.s,z22.h,z24.h
fmlalb z6.s,z22.h,z25.h
fmlalt z1.s,z22.h,z21.h
fmlalt z3.s,z22.h,z23.h
fmlalt z5.s,z22.h,z24.h
fmlalt z7.s,z22.h,z25.h
ld1rh {z26.h}, p0/z, [x1, #8]
ld1h {z27.h}, p0/z, [x2, #1, MUL VL]
ld1rh {z28.h}, p0/z, [x1, #10]
ld1rh {z29.h}, p0/z, [x1, #12]
ld1rh {z30.h}, p0/z, [x1, #14]
fmlalb z0.s,z27.h,z26.h
fmlalb z2.s,z27.h,z28.h
fmlalb z4.s,z27.h,z29.h
fmlalb z6.s,z27.h,z30.h
fmlalt z1.s,z27.h,z26.h
fmlalt z3.s,z27.h,z28.h
fmlalt z5.s,z27.h,z29.h
fmlalt z7.s,z27.h,z30.h
ld1rh {z31.h}, p0/z, [x1, #16]
ld1h {z8.h}, p0/z, [x2, #2, MUL VL]
ld1rh {z9.h}, p0/z, [x1, #18]
ld1rh {z10.h}, p0/z, [x1, #20]
ld1rh {z11.h}, p0/z, [x1, #22]
fmlalb z0.s,z8.h,z31.h
fmlalb z2.s,z8.h,z9.h
fmlalb z4.s,z8.h,z10.h
fmlalb z6.s,z8.h,z11.h
ld1rh {z16.h}, p0/z, [x1, #24]
ld1rh {z17.h}, p0/z, [x1, #26]
ld1rh {z18.h}, p0/z, [x1, #28]
ld1rh {z19.h}, p0/z, [x1, #30]
ld1h {z20.h}, p0/z, [x2, #3, MUL VL]
fmlalt z1.s,z8.h,z31.h
fmlalt z3.s,z8.h,z9.h
fmlalt z5.s,z8.h,z10.h
fmlalt z7.s,z8.h,z11.h
add x1,x1,#32
incb x2, ALL, MUL #4
cbnz x0,.ukr1_loop
.ukr1_last:
fmlalb z0.s,z20.h,z16.h
fmlalb z2.s,z20.h,z17.h
fmlalb z4.s,z20.h,z18.h
fmlalb z6.s,z20.h,z19.h
fmlalt z1.s,z20.h,z16.h
fmlalt z3.s,z20.h,z17.h
fmlalt z5.s,z20.h,z18.h
fmlalt z7.s,z20.h,z19.h
ld1rh {z21.h}, p0/z, [x1]
ld1h {z22.h}, p0/z, [x2]
ld1rh {z23.h}, p0/z, [x1, #2]
ld1rh {z24.h}, p0/z, [x1, #4]
ld1rh {z25.h}, p0/z, [x1, #6]
fmlalb z0.s,z22.h,z21.h
fmlalb z2.s,z22.h,z23.h
fmlalb z4.s,z22.h,z24.h
fmlalb z6.s,z22.h,z25.h
fmlalt z1.s,z22.h,z21.h
fmlalt z3.s,z22.h,z23.h
fmlalt z5.s,z22.h,z24.h
fmlalt z7.s,z22.h,z25.h
ld1rh {z26.h}, p0/z, [x1, #8]
ld1h {z27.h}, p0/z, [x2, #1, MUL VL]
ld1rh {z28.h}, p0/z, [x1, #10]
ld1rh {z29.h}, p0/z, [x1, #12]
ld1rh {z30.h}, p0/z, [x1, #14]
fmlalb z0.s,z27.h,z26.h
fmlalb z2.s,z27.h,z28.h
fmlalb z4.s,z27.h,z29.h
fmlalb z6.s,z27.h,z30.h
fmlalt z1.s,z27.h,z26.h
fmlalt z3.s,z27.h,z28.h
fmlalt z5.s,z27.h,z29.h
fmlalt z7.s,z27.h,z30.h
ld1rh {z31.h}, p0/z, [x1, #16]
ld1h {z8.h}, p0/z, [x2, #2, MUL VL]
ld1rh {z9.h}, p0/z, [x1, #18]
ld1rh {z10.h}, p0/z, [x1, #20]
ld1rh {z11.h}, p0/z, [x1, #22]
fmlalb z0.s,z8.h,z31.h
fmlalb z2.s,z8.h,z9.h
fmlalb z4.s,z8.h,z10.h
fmlalb z6.s,z8.h,z11.h
fmlalt z1.s,z8.h,z31.h
fmlalt z3.s,z8.h,z9.h
fmlalt z5.s,z8.h,z10.h
fmlalt z7.s,z8.h,z11.h
add x1,x1,#24
incb x2, ALL, MUL #3
.ukr1_done:
cbz x7,.ukr1_taildone
.ukr1_tail:
add x7,x7,#-1
ld1rh {z16.h}, p0/z, [x1]
ld1h {z20.h}, p0/z, [x2]
ld1rh {z17.h}, p0/z, [x1, #2]
ld1rh {z18.h}, p0/z, [x1, #4]
ld1rh {z19.h}, p0/z, [x1, #6]
fmlalb z0.s,z20.h,z16.h
fmlalb z2.s,z20.h,z17.h
fmlalb z4.s,z20.h,z18.h
fmlalb z6.s,z20.h,z19.h
fmlalt z1.s,z20.h,z16.h
fmlalt z3.s,z20.h,z17.h
fmlalt z5.s,z20.h,z18.h
fmlalt z7.s,z20.h,z19.h
add x1,x1,#8
incb x2, ALL, MUL #1
cbnz x7,.ukr1_tail
.ukr1_taildone:
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
st2w {z0.s, z1.s}, p0, [x0]
add x0,x0,x6
st2w {z2.s, z3.s}, p0, [x0]
add x0,x0,x6
st2w {z4.s, z5.s}, p0, [x0]
add x0,x0,x6
st2w {z6.s, z7.s}, p0, [x0]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
ld1rw {z8.s}, p0/z, [x4]
ld1rw {z9.s}, p0/z, [x4]
fmul z10.s,z0.s,z8.s
fmul z11.s,z1.s,z9.s
fmul z12.s,z2.s,z8.s
fmul z13.s,z3.s,z9.s
fmul z14.s,z4.s,z8.s
st2w {z10.s, z11.s}, p0, [x0]
fmul z15.s,z5.s,z9.s
add x0,x0,x6
fmul z16.s,z6.s,z8.s
st2w {z12.s, z13.s}, p0, [x0]
fmul z17.s,z7.s,z9.s
add x0,x0,x6
st2w {z14.s, z15.s}, p0, [x0]
add x0,x0,x6
st2w {z16.s, z17.s}, p0, [x0]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
ld2w {z8.s, z9.s}, p0/z, [x0]
fadd z8.s,z0.s,z8.s
fadd z9.s,z1.s,z9.s
st2w {z8.s, z9.s}, p0, [x3]
add x0,x0,x6
ld2w {z10.s, z11.s}, p0/z, [x0]
add x3,x3,x6
fadd z10.s,z2.s,z10.s
fadd z11.s,z3.s,z11.s
st2w {z10.s, z11.s}, p0, [x3]
add x0,x0,x6
ld2w {z12.s, z13.s}, p0/z, [x0]
add x3,x3,x6
fadd z12.s,z4.s,z12.s
fadd z13.s,z5.s,z13.s
st2w {z12.s, z13.s}, p0, [x3]
add x0,x0,x6
ld2w {z14.s, z15.s}, p0/z, [x0]
add x3,x3,x6
fadd z14.s,z6.s,z14.s
fadd z15.s,z7.s,z15.s
st2w {z14.s, z15.s}, p0, [x3]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
ld1rw {z8.s}, p0/z, [x4]
ld1rw {z9.s}, p0/z, [x4]
ld2w {z10.s, z11.s}, p0/z, [x0]
fmla z10.s,p0/m,z0.s,z8.s
fmla z11.s,p0/m,z1.s,z9.s
st2w {z10.s, z11.s}, p0, [x3]
add x0,x0,x6
ld2w {z12.s, z13.s}, p0/z, [x0]
add x3,x3,x6
fmla z12.s,p0/m,z2.s,z8.s
fmla z13.s,p0/m,z3.s,z9.s
st2w {z12.s, z13.s}, p0, [x3]
add x0,x0,x6
ld2w {z14.s, z15.s}, p0/z, [x0]
add x3,x3,x6
fmla z14.s,p0/m,z4.s,z8.s
fmla z15.s,p0/m,z5.s,z9.s
st2w {z14.s, z15.s}, p0, [x3]
add x0,x0,x6
ld2w {z16.s, z17.s}, p0/z, [x0]
add x3,x3,x6
fmla z16.s,p0/m,z6.s,z8.s
fmla z17.s,p0/m,z7.s,z9.s
st2w {z16.s, z17.s}, p0, [x3]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
ld1rw {z8.s}, p0/z, [x5]
ld2w {z10.s, z11.s}, p0/z, [x0]
ld1rw {z9.s}, p0/z, [x5]
fmla z0.s,p0/m,z10.s,z8.s
fmla z1.s,p0/m,z11.s,z9.s
st2w {z0.s, z1.s}, p0, [x3]
add x0,x0,x6
ld2w {z12.s, z13.s}, p0/z, [x0]
add x3,x3,x6
fmla z2.s,p0/m,z12.s,z8.s
fmla z3.s,p0/m,z13.s,z9.s
st2w {z2.s, z3.s}, p0, [x3]
add x0,x0,x6
ld2w {z14.s, z15.s}, p0/z, [x0]
add x3,x3,x6
fmla z4.s,p0/m,z14.s,z8.s
fmla z5.s,p0/m,z15.s,z9.s
st2w {z4.s, z5.s}, p0, [x3]
add x0,x0,x6
ld2w {z16.s, z17.s}, p0/z, [x0]
add x3,x3,x6
fmla z6.s,p0/m,z16.s,z8.s
fmla z7.s,p0/m,z17.s,z9.s
st2w {z6.s, z7.s}, p0, [x3]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
ld1rw {z8.s}, p0/z, [x5]
ld1rw {z9.s}, p0/z, [x5]
ld2w {z10.s, z11.s}, p0/z, [x0]
ld1rw {z12.s}, p0/z, [x4]
ld1rw {z13.s}, p0/z, [x4]
fmul z10.s,z10.s,z8.s
fmul z11.s,z11.s,z9.s
fmla z10.s,p0/m,z0.s,z12.s
fmla z11.s,p0/m,z1.s,z13.s
st2w {z10.s, z11.s}, p0, [x3]
add x0,x0,x6
ld2w {z14.s, z15.s}, p0/z, [x0]
add x3,x3,x6
fmul z14.s,z14.s,z8.s
fmul z15.s,z15.s,z9.s
fmla z14.s,p0/m,z2.s,z12.s
fmla z15.s,p0/m,z3.s,z13.s
st2w {z14.s, z15.s}, p0, [x3]
add x0,x0,x6
ld2w {z16.s, z17.s}, p0/z, [x0]
add x3,x3,x6
fmul z16.s,z16.s,z8.s
fmul z17.s,z17.s,z9.s
fmla z16.s,p0/m,z4.s,z12.s
fmla z17.s,p0/m,z5.s,z13.s
st2w {z16.s, z17.s}, p0, [x3]
add x0,x0,x6
ld2w {z18.s, z19.s}, p0/z, [x0]
add x3,x3,x6
fmul z18.s,z18.s,z8.s
fmul z19.s,z19.s,z9.s
fmla z18.s,p0/m,z6.s,z12.s
fmla z19.s,p0/m,z7.s,z13.s
st2w {z18.s, z19.s}, p0, [x3]
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
.size gemmf16f16f32_sve_vn_4x1v, .-gemmf16f16f32_sve_vn_4x1v
.section .note.GNU-stack,"",%progbits
