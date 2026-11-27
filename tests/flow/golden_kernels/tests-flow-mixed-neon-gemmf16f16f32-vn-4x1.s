.text
.global gemmf16f16f32_neon_vn_4x8
.type gemmf16f16f32_neon_vn_4x8, %function
gemmf16f16f32_neon_vn_4x8:
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
# x7 = stride(C,n)
dup v0.4s,wzr
dup v2.4s,wzr
dup v4.4s,wzr
dup v6.4s,wzr
dup v1.4s,wzr
dup v3.4s,wzr
dup v5.4s,wzr
dup v7.4s,wzr
cbz x0,.ukr1_done
ld1r {v16.8h}, [x1]
add x1,x1,#2
ld1r {v17.8h}, [x1], #2
ld1r {v18.8h}, [x1], #2
ld1r {v19.8h}, [x1]
ld1 {v20.8h}, [x2]
add x1,x1,#2
add x2,x2,#16
add x0,x0,#-1
cbz x0,.ukr1_last
.ukr1_loop:
add x0,x0,#-1
fmlal v0.4s,v20.4h,v16.4h
fmlal v2.4s,v20.4h,v17.4h
fmlal v4.4s,v20.4h,v18.4h
fmlal v6.4s,v20.4h,v19.4h
fmlal2 v1.4s,v20.4h,v16.4h
ld1r {v16.8h}, [x1]
fmlal2 v3.4s,v20.4h,v17.4h
add x1,x1,#2
fmlal2 v5.4s,v20.4h,v18.4h
ld1r {v17.8h}, [x1], #2
fmlal2 v7.4s,v20.4h,v19.4h
ld1r {v18.8h}, [x1], #2
ld1r {v19.8h}, [x1]
ld1 {v20.8h}, [x2]
add x1,x1,#2
add x2,x2,#16
cbnz x0,.ukr1_loop
.ukr1_last:
fmlal v0.4s,v20.4h,v16.4h
fmlal v2.4s,v20.4h,v17.4h
fmlal v4.4s,v20.4h,v18.4h
fmlal v6.4s,v20.4h,v19.4h
fmlal2 v1.4s,v20.4h,v16.4h
fmlal2 v3.4s,v20.4h,v17.4h
fmlal2 v5.4s,v20.4h,v18.4h
fmlal2 v7.4s,v20.4h,v19.4h
.ukr1_done:
mov x0,x7
add x0,x0,#-4
cmp x0,0
b.eq .ukr0_ok1
b .ukr0_try0
.ukr0_ok1:
ldr s16, [x5]
fmov s17,wzr
fcmp s16,s17
b.ne .ukr0_try2
ldr s16, [x4]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
b.ne .ukr0_try3
b .ukr0_case0
.ukr0_try3:
b .ukr0_case1
.ukr0_try2:
ldr s16, [x5]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
b.ne .ukr0_try4
ldr s16, [x4]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
b.ne .ukr0_try5
b .ukr0_case2
.ukr0_try5:
b .ukr0_case3
.ukr0_try4:
ldr s16, [x4]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
b.ne .ukr0_try6
b .ukr0_case4
.ukr0_try6:
b .ukr0_case5
.ukr0_try0:
ldr s16, [x5]
fmov s17,wzr
fcmp s16,s17
b.ne .ukr0_try7
ldr s16, [x4]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
b.ne .ukr0_try8
b .ukr0_case6
.ukr0_try8:
b .ukr0_case7
.ukr0_try7:
ldr s16, [x5]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
b.ne .ukr0_try9
ldr s16, [x4]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
b.ne .ukr0_try10
b .ukr0_case8
.ukr0_try10:
b .ukr0_case9
.ukr0_try9:
ldr s16, [x4]
mov x0,#1065353216
fmov s17,w0
fcmp s16,s17
b.ne .ukr0_try11
b .ukr0_case10
.ukr0_try11:
b .ukr0_case11
b .ukr0_cases_end
.ukr0_case0:
mov x0,x3
mov x1,x3
st1 {v0.4s}, [x0]
str q1, [x0, #16]
add x0,x0,x6
st1 {v2.4s}, [x0]
str q3, [x0, #16]
add x0,x0,x6
st1 {v4.4s}, [x0]
str q5, [x0, #16]
add x0,x0,x6
st1 {v6.4s}, [x0]
str q7, [x0, #16]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
mov x1,x3
ld1r {v8.4s}, [x4]
ld1r {v9.4s}, [x4]
fmul v10.4s,v0.4s,v8.4s
fmul v11.4s,v1.4s,v9.4s
fmul v12.4s,v2.4s,v8.4s
fmul v13.4s,v3.4s,v9.4s
fmul v14.4s,v4.4s,v8.4s
st1 {v10.4s}, [x0]
str q11, [x0, #16]
fmul v15.4s,v5.4s,v9.4s
add x0,x0,x6
fmul v16.4s,v6.4s,v8.4s
st1 {v12.4s}, [x0]
str q13, [x0, #16]
fmul v17.4s,v7.4s,v9.4s
add x0,x0,x6
st1 {v14.4s}, [x0]
str q15, [x0, #16]
add x0,x0,x6
st1 {v16.4s}, [x0]
str q17, [x0, #16]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x3
ld1 {v8.4s}, [x0]
ldr q9, [x0, #16]
fadd v8.4s,v0.4s,v8.4s
fadd v9.4s,v1.4s,v9.4s
st1 {v8.4s}, [x1]
str q9, [x1, #16]
add x0,x0,x6
ld1 {v10.4s}, [x0]
ldr q11, [x0, #16]
add x1,x1,x6
fadd v10.4s,v2.4s,v10.4s
fadd v11.4s,v3.4s,v11.4s
st1 {v10.4s}, [x1]
str q11, [x1, #16]
add x0,x0,x6
ld1 {v12.4s}, [x0]
ldr q13, [x0, #16]
add x1,x1,x6
fadd v12.4s,v4.4s,v12.4s
fadd v13.4s,v5.4s,v13.4s
st1 {v12.4s}, [x1]
str q13, [x1, #16]
add x0,x0,x6
ld1 {v14.4s}, [x0]
ldr q15, [x0, #16]
add x1,x1,x6
fadd v14.4s,v6.4s,v14.4s
fadd v15.4s,v7.4s,v15.4s
st1 {v14.4s}, [x1]
str q15, [x1, #16]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
mov x1,x3
ld1r {v8.4s}, [x4]
ld1 {v10.4s}, [x0]
ld1r {v9.4s}, [x4]
ldr q11, [x0, #16]
fmla v10.4s,v0.4s,v8.4s
fmla v11.4s,v1.4s,v9.4s
st1 {v10.4s}, [x1]
str q11, [x1, #16]
add x0,x0,x6
ld1 {v12.4s}, [x0]
ldr q13, [x0, #16]
add x1,x1,x6
fmla v12.4s,v2.4s,v8.4s
fmla v13.4s,v3.4s,v9.4s
st1 {v12.4s}, [x1]
str q13, [x1, #16]
add x0,x0,x6
ld1 {v14.4s}, [x0]
ldr q15, [x0, #16]
add x1,x1,x6
fmla v14.4s,v4.4s,v8.4s
fmla v15.4s,v5.4s,v9.4s
st1 {v14.4s}, [x1]
str q15, [x1, #16]
add x0,x0,x6
ld1 {v16.4s}, [x0]
ldr q17, [x0, #16]
add x1,x1,x6
fmla v16.4s,v6.4s,v8.4s
fmla v17.4s,v7.4s,v9.4s
st1 {v16.4s}, [x1]
str q17, [x1, #16]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
mov x1,x3
ld1r {v8.4s}, [x5]
ld1 {v10.4s}, [x0]
ld1r {v9.4s}, [x5]
ldr q11, [x0, #16]
fmla v0.4s,v10.4s,v8.4s
fmla v1.4s,v11.4s,v9.4s
st1 {v0.4s}, [x1]
str q1, [x1, #16]
add x0,x0,x6
ld1 {v12.4s}, [x0]
ldr q13, [x0, #16]
add x1,x1,x6
fmla v2.4s,v12.4s,v8.4s
fmla v3.4s,v13.4s,v9.4s
st1 {v2.4s}, [x1]
str q3, [x1, #16]
add x0,x0,x6
ld1 {v14.4s}, [x0]
ldr q15, [x0, #16]
add x1,x1,x6
fmla v4.4s,v14.4s,v8.4s
fmla v5.4s,v15.4s,v9.4s
st1 {v4.4s}, [x1]
str q5, [x1, #16]
add x0,x0,x6
ld1 {v16.4s}, [x0]
ldr q17, [x0, #16]
add x1,x1,x6
fmla v6.4s,v16.4s,v8.4s
fmla v7.4s,v17.4s,v9.4s
st1 {v6.4s}, [x1]
str q7, [x1, #16]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
mov x1,x3
ld1r {v8.4s}, [x5]
ld1 {v10.4s}, [x0]
ld1r {v9.4s}, [x5]
ldr q11, [x0, #16]
ld1r {v12.4s}, [x4]
ld1r {v13.4s}, [x4]
fmul v10.4s,v10.4s,v8.4s
fmul v11.4s,v11.4s,v9.4s
fmla v10.4s,v0.4s,v12.4s
fmla v11.4s,v1.4s,v13.4s
st1 {v10.4s}, [x1]
str q11, [x1, #16]
add x0,x0,x6
ld1 {v14.4s}, [x0]
ldr q15, [x0, #16]
add x1,x1,x6
fmul v14.4s,v14.4s,v8.4s
fmul v15.4s,v15.4s,v9.4s
fmla v14.4s,v2.4s,v12.4s
fmla v15.4s,v3.4s,v13.4s
st1 {v14.4s}, [x1]
str q15, [x1, #16]
add x0,x0,x6
ld1 {v16.4s}, [x0]
ldr q17, [x0, #16]
add x1,x1,x6
fmul v16.4s,v16.4s,v8.4s
fmul v17.4s,v17.4s,v9.4s
fmla v16.4s,v4.4s,v12.4s
fmla v17.4s,v5.4s,v13.4s
st1 {v16.4s}, [x1]
str q17, [x1, #16]
add x0,x0,x6
ld1 {v18.4s}, [x0]
ldr q19, [x0, #16]
add x1,x1,x6
fmul v18.4s,v18.4s,v8.4s
fmul v19.4s,v19.4s,v9.4s
fmla v18.4s,v6.4s,v12.4s
fmla v19.4s,v7.4s,v13.4s
st1 {v18.4s}, [x1]
str q19, [x1, #16]
b .ukr0_cases_end
.ukr0_case6:
mov x0,x3
st1 {v0.s}[0], [x0]
add x0,x0,x7, LSL #2
st1 {v1.s}[0], [x0]
add x0,x3,x7
st1 {v0.s}[1], [x0]
add x0,x0,x7, LSL #2
st1 {v1.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v0.s}[2], [x0]
add x0,x0,x7, LSL #2
st1 {v1.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v0.s}[3], [x0]
add x0,x0,x7, LSL #2
st1 {v1.s}[3], [x0]
add x0,x3,x6
st1 {v2.s}[0], [x0]
add x0,x0,x7, LSL #2
st1 {v3.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v2.s}[1], [x0]
add x0,x0,x7, LSL #2
st1 {v3.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v2.s}[2], [x0]
add x0,x0,x7, LSL #2
st1 {v3.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v2.s}[3], [x0]
add x0,x0,x7, LSL #2
st1 {v3.s}[3], [x0]
add x0,x3,x6, LSL #1
st1 {v4.s}[0], [x0]
add x0,x0,x7, LSL #2
st1 {v5.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v4.s}[1], [x0]
add x0,x0,x7, LSL #2
st1 {v5.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v4.s}[2], [x0]
add x0,x0,x7, LSL #2
st1 {v5.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v4.s}[3], [x0]
add x0,x0,x7, LSL #2
st1 {v5.s}[3], [x0]
add x0,x3,x6
add x0,x0,x6, LSL #1
st1 {v6.s}[0], [x0]
add x0,x0,x7, LSL #2
st1 {v7.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v6.s}[1], [x0]
add x0,x0,x7, LSL #2
st1 {v7.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v6.s}[2], [x0]
add x0,x0,x7, LSL #2
st1 {v7.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v6.s}[3], [x0]
add x0,x0,x7, LSL #2
st1 {v7.s}[3], [x0]
b .ukr0_cases_end
.ukr0_case7:
mov x0,x3
ld1r {v8.4s}, [x4]
ld1r {v9.4s}, [x4]
fmul v10.4s,v0.4s,v8.4s
fmul v11.4s,v1.4s,v9.4s
fmul v12.4s,v2.4s,v8.4s
fmul v13.4s,v3.4s,v9.4s
fmul v14.4s,v4.4s,v8.4s
st1 {v10.s}[0], [x0]
add x0,x0,x7, LSL #2
st1 {v11.s}[0], [x0]
add x0,x3,x7
st1 {v10.s}[1], [x0]
add x0,x0,x7, LSL #2
st1 {v11.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v10.s}[2], [x0]
add x0,x0,x7, LSL #2
st1 {v11.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v10.s}[3], [x0]
add x0,x0,x7, LSL #2
st1 {v11.s}[3], [x0]
add x0,x3,x6
st1 {v12.s}[0], [x0]
add x0,x0,x7, LSL #2
st1 {v13.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v12.s}[1], [x0]
add x0,x0,x7, LSL #2
st1 {v13.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v12.s}[2], [x0]
add x0,x0,x7, LSL #2
st1 {v13.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v12.s}[3], [x0]
fmul v15.4s,v5.4s,v9.4s
add x0,x0,x7, LSL #2
st1 {v13.s}[3], [x0]
add x0,x3,x6, LSL #1
st1 {v14.s}[0], [x0]
add x0,x0,x7, LSL #2
st1 {v15.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v14.s}[1], [x0]
add x0,x0,x7, LSL #2
st1 {v15.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v14.s}[2], [x0]
add x0,x0,x7, LSL #2
st1 {v15.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v14.s}[3], [x0]
fmul v16.4s,v6.4s,v8.4s
add x0,x0,x7, LSL #2
fmul v17.4s,v7.4s,v9.4s
st1 {v15.s}[3], [x0]
add x0,x3,x6
add x0,x0,x6, LSL #1
st1 {v16.s}[0], [x0]
add x0,x0,x7, LSL #2
st1 {v17.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v16.s}[1], [x0]
add x0,x0,x7, LSL #2
st1 {v17.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v16.s}[2], [x0]
add x0,x0,x7, LSL #2
st1 {v17.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
st1 {v16.s}[3], [x0]
add x0,x0,x7, LSL #2
st1 {v17.s}[3], [x0]
b .ukr0_cases_end
.ukr0_case8:
mov x0,x3
ld1 {v8.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[0], [x0]
add x0,x3,x7
ld1 {v8.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v8.s}[2], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v8.s}[3], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[3], [x0]
fadd v8.4s,v0.4s,v8.4s
fadd v9.4s,v1.4s,v9.4s
st1 {v8.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v9.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v8.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v9.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v8.s}[2], [x3]
sub x3,x0,x7
st1 {v9.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v8.s}[3], [x3]
mov x3,x0
st1 {v9.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v10.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v11.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v10.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v11.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v10.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v11.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v10.s}[3], [x0]
add x0,x3,x6
ld1 {v11.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fadd v10.4s,v2.4s,v10.4s
sub x3,x3,x7, LSL #2
fadd v11.4s,v3.4s,v11.4s
st1 {v10.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v11.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v10.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v11.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v10.s}[2], [x3]
sub x3,x0,x7
st1 {v11.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v10.s}[3], [x3]
mov x3,x0
st1 {v11.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v12.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v13.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v12.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v13.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v12.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v13.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v12.s}[3], [x0]
add x0,x3,x6
ld1 {v13.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fadd v12.4s,v4.4s,v12.4s
sub x3,x3,x7, LSL #2
fadd v13.4s,v5.4s,v13.4s
st1 {v12.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v13.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v12.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v13.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v12.s}[2], [x3]
sub x3,x0,x7
st1 {v13.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v12.s}[3], [x3]
mov x3,x0
st1 {v13.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v14.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v15.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v15.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v15.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[3], [x0]
add x0,x3,x6
ld1 {v15.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fadd v14.4s,v6.4s,v14.4s
sub x3,x3,x7, LSL #2
fadd v15.4s,v7.4s,v15.4s
st1 {v14.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v15.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v14.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v15.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v14.s}[2], [x3]
sub x3,x0,x7
st1 {v15.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v14.s}[3], [x3]
mov x3,x0
st1 {v15.s}[3], [x3]
b .ukr0_cases_end
.ukr0_case9:
mov x0,x3
ld1 {v8.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1r {v10.4s}, [x4]
ld1r {v11.4s}, [x4]
ld1 {v9.s}[0], [x0]
add x0,x3,x7
ld1 {v8.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v8.s}[2], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v8.s}[3], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[3], [x0]
fmla v8.4s,v0.4s,v10.4s
fmla v9.4s,v1.4s,v11.4s
st1 {v8.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v9.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v8.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v9.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v8.s}[2], [x3]
sub x3,x0,x7
st1 {v9.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v8.s}[3], [x3]
mov x3,x0
st1 {v9.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v12.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v13.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v12.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v13.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v12.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v13.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v12.s}[3], [x0]
add x0,x3,x6
ld1 {v13.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fmla v12.4s,v2.4s,v10.4s
sub x3,x3,x7, LSL #2
fmla v13.4s,v3.4s,v11.4s
st1 {v12.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v13.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v12.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v13.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v12.s}[2], [x3]
sub x3,x0,x7
st1 {v13.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v12.s}[3], [x3]
mov x3,x0
st1 {v13.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v14.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v15.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v15.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v15.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[3], [x0]
add x0,x3,x6
ld1 {v15.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fmla v14.4s,v4.4s,v10.4s
sub x3,x3,x7, LSL #2
fmla v15.4s,v5.4s,v11.4s
st1 {v14.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v15.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v14.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v15.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v14.s}[2], [x3]
sub x3,x0,x7
st1 {v15.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v14.s}[3], [x3]
mov x3,x0
st1 {v15.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v16.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v17.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v16.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v17.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v16.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v17.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v16.s}[3], [x0]
add x0,x3,x6
ld1 {v17.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fmla v16.4s,v6.4s,v10.4s
sub x3,x3,x7, LSL #2
fmla v17.4s,v7.4s,v11.4s
st1 {v16.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v17.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v16.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v17.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v16.s}[2], [x3]
sub x3,x0,x7
st1 {v17.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v16.s}[3], [x3]
mov x3,x0
st1 {v17.s}[3], [x3]
b .ukr0_cases_end
.ukr0_case10:
mov x0,x3
ld1 {v8.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1r {v10.4s}, [x5]
ld1r {v11.4s}, [x5]
ld1 {v9.s}[0], [x0]
add x0,x3,x7
ld1 {v8.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v8.s}[2], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v8.s}[3], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[3], [x0]
fmla v0.4s,v8.4s,v10.4s
fmla v1.4s,v9.4s,v11.4s
st1 {v0.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v1.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v0.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v1.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v0.s}[2], [x3]
sub x3,x0,x7
st1 {v1.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v0.s}[3], [x3]
mov x3,x0
st1 {v1.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v12.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v13.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v12.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v13.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v12.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v13.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v12.s}[3], [x0]
add x0,x3,x6
ld1 {v13.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fmla v2.4s,v12.4s,v10.4s
sub x3,x3,x7, LSL #2
fmla v3.4s,v13.4s,v11.4s
st1 {v2.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v3.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v2.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v3.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v2.s}[2], [x3]
sub x3,x0,x7
st1 {v3.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v2.s}[3], [x3]
mov x3,x0
st1 {v3.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v14.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v15.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v15.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v15.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[3], [x0]
add x0,x3,x6
ld1 {v15.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fmla v4.4s,v14.4s,v10.4s
sub x3,x3,x7, LSL #2
fmla v5.4s,v15.4s,v11.4s
st1 {v4.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v5.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v4.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v5.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v4.s}[2], [x3]
sub x3,x0,x7
st1 {v5.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v4.s}[3], [x3]
mov x3,x0
st1 {v5.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v16.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v17.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v16.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v17.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v16.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v17.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v16.s}[3], [x0]
add x0,x3,x6
ld1 {v17.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fmla v6.4s,v16.4s,v10.4s
sub x3,x3,x7, LSL #2
fmla v7.4s,v17.4s,v11.4s
st1 {v6.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v7.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v6.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v7.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v6.s}[2], [x3]
sub x3,x0,x7
st1 {v7.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v6.s}[3], [x3]
mov x3,x0
st1 {v7.s}[3], [x3]
b .ukr0_cases_end
.ukr0_case11:
mov x0,x3
ld1 {v8.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1r {v10.4s}, [x5]
ld1r {v11.4s}, [x5]
ld1 {v9.s}[0], [x0]
add x0,x3,x7
ld1r {v12.4s}, [x4]
ld1r {v13.4s}, [x4]
ld1 {v8.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v8.s}[2], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v8.s}[3], [x0]
add x0,x0,x7, LSL #2
ld1 {v9.s}[3], [x0]
fmul v8.4s,v8.4s,v10.4s
fmul v9.4s,v9.4s,v11.4s
fmla v8.4s,v0.4s,v12.4s
fmla v9.4s,v1.4s,v13.4s
st1 {v8.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v9.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v8.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v9.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v8.s}[2], [x3]
sub x3,x0,x7
st1 {v9.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v8.s}[3], [x3]
mov x3,x0
st1 {v9.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v14.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v15.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v15.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v15.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v14.s}[3], [x0]
add x0,x3,x6
ld1 {v15.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fmul v14.4s,v14.4s,v10.4s
sub x3,x3,x7, LSL #2
fmul v15.4s,v15.4s,v11.4s
fmla v14.4s,v2.4s,v12.4s
fmla v15.4s,v3.4s,v13.4s
st1 {v14.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v15.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v14.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v15.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v14.s}[2], [x3]
sub x3,x0,x7
st1 {v15.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v14.s}[3], [x3]
mov x3,x0
st1 {v15.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v16.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v17.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v16.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v17.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v16.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v17.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v16.s}[3], [x0]
add x0,x3,x6
ld1 {v17.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fmul v16.4s,v16.4s,v10.4s
sub x3,x3,x7, LSL #2
fmul v17.4s,v17.4s,v11.4s
fmla v16.4s,v4.4s,v12.4s
fmla v17.4s,v5.4s,v13.4s
st1 {v16.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v17.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v16.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v17.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v16.s}[2], [x3]
sub x3,x0,x7
st1 {v17.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v16.s}[3], [x3]
mov x3,x0
st1 {v17.s}[3], [x3]
add x0,x0,x6
sub x0,x0,x7
sub x0,x0,x7, LSL #1
sub x0,x0,x7, LSL #2
ld1 {v18.s}[0], [x0]
add x0,x0,x7, LSL #2
ld1 {v19.s}[0], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v18.s}[1], [x0]
add x0,x0,x7, LSL #2
ld1 {v19.s}[1], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v18.s}[2], [x0]
add x0,x3,x6
sub x0,x0,x7
ld1 {v19.s}[2], [x0]
sub x0,x0,x7
sub x0,x0,x7, LSL #1
ld1 {v18.s}[3], [x0]
add x0,x3,x6
ld1 {v19.s}[3], [x0]
add x3,x3,x6
sub x3,x3,x7
sub x3,x3,x7, LSL #1
fmul v18.4s,v18.4s,v10.4s
sub x3,x3,x7, LSL #2
fmul v19.4s,v19.4s,v11.4s
fmla v18.4s,v6.4s,v12.4s
fmla v19.4s,v7.4s,v13.4s
st1 {v18.s}[0], [x3]
add x3,x3,x7, LSL #2
st1 {v19.s}[0], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v18.s}[1], [x3]
sub x3,x0,x7, LSL #1
st1 {v19.s}[1], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v18.s}[2], [x3]
sub x3,x0,x7
st1 {v19.s}[2], [x3]
sub x3,x3,x7
sub x3,x3,x7, LSL #1
st1 {v18.s}[3], [x3]
mov x3,x0
st1 {v19.s}[3], [x3]
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
.size gemmf16f16f32_neon_vn_4x8, .-gemmf16f16f32_neon_vn_4x8
.section .note.GNU-stack,"",%progbits
