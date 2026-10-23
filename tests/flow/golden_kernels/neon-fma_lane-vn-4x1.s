.text
.global bli_dgemm_ukrgen_neon_vn_4x2_asm
bli_dgemm_ukrgen_neon_vn_4x2_asm:
add sp,sp,#-16
str d8,[sp,#0]
# x0 = k
# x1 = base(A)
# x2 = base(B)
# x3 = base(C)
# x4 = base(alpha)
# x5 = base(beta)
# x6 = stride(C,m)
# x7 = stride(C,n)
and x8,x0,#3
lsr x0,x0,#2
dup v0.2d,xzr
dup v1.2d,xzr
dup v2.2d,xzr
dup v3.2d,xzr
cbz x0,.ukr1_done
ld1 {v4.2d}, [x1]
ld1 {v5.2d}, [x2]
dup v6.2d,v4.d[0]
dup v7.2d,v4.d[1]
ldr q4, [x1, #16]
add x1,x1,#32
dup v16.2d,v4.d[0]
dup v17.2d,v4.d[1]
add x2,x2,#16
add x0,x0,#-1
cbz x0,.ukr1_last
.ukr1_loop:
add x0,x0,#-1
ld1 {v4.2d}, [x1]
fmla v0.2d,v5.2d,v6.2d
fmla v1.2d,v5.2d,v7.2d
fmla v2.2d,v5.2d,v16.2d
dup v18.2d,v4.d[0]
dup v19.2d,v4.d[1]
ldr q4, [x1, #16]
fmla v3.2d,v5.2d,v17.2d
ld1 {v20.2d}, [x2]
ldr q21, [x2, #16]
dup v22.2d,v4.d[0]
dup v23.2d,v4.d[1]
ldr q4, [x1, #32]
fmla v0.2d,v20.2d,v18.2d
fmla v1.2d,v20.2d,v19.2d
fmla v2.2d,v20.2d,v22.2d
dup v24.2d,v4.d[0]
dup v25.2d,v4.d[1]
ldr q4, [x1, #48]
fmla v3.2d,v20.2d,v23.2d
fmla v0.2d,v21.2d,v24.2d
fmla v1.2d,v21.2d,v25.2d
dup v26.2d,v4.d[0]
dup v27.2d,v4.d[1]
ldr q4, [x1, #64]
ldr q28, [x2, #32]
fmla v2.2d,v21.2d,v26.2d
fmla v3.2d,v21.2d,v27.2d
dup v29.2d,v4.d[0]
dup v30.2d,v4.d[1]
ldr q4, [x1, #80]
ldr q5, [x2, #48]
fmla v0.2d,v28.2d,v29.2d
fmla v1.2d,v28.2d,v30.2d
dup v31.2d,v4.d[0]
dup v8.2d,v4.d[1]
ldr q4, [x1, #96]
add x2,x2,#64
fmla v2.2d,v28.2d,v31.2d
fmla v3.2d,v28.2d,v8.2d
dup v6.2d,v4.d[0]
dup v7.2d,v4.d[1]
ldr q4, [x1, #112]
add x1,x1,#128
dup v16.2d,v4.d[0]
dup v17.2d,v4.d[1]
cbnz x0,.ukr1_loop
.ukr1_last:
ld1 {v4.2d}, [x1]
fmla v0.2d,v5.2d,v6.2d
fmla v1.2d,v5.2d,v7.2d
fmla v2.2d,v5.2d,v16.2d
dup v18.2d,v4.d[0]
dup v19.2d,v4.d[1]
ldr q4, [x1, #16]
fmla v3.2d,v5.2d,v17.2d
ld1 {v20.2d}, [x2]
ldr q21, [x2, #16]
dup v22.2d,v4.d[0]
dup v23.2d,v4.d[1]
ldr q4, [x1, #32]
fmla v0.2d,v20.2d,v18.2d
fmla v1.2d,v20.2d,v19.2d
fmla v2.2d,v20.2d,v22.2d
dup v24.2d,v4.d[0]
dup v25.2d,v4.d[1]
ldr q4, [x1, #48]
fmla v3.2d,v20.2d,v23.2d
fmla v0.2d,v21.2d,v24.2d
fmla v1.2d,v21.2d,v25.2d
dup v26.2d,v4.d[0]
dup v27.2d,v4.d[1]
ldr q4, [x1, #64]
ldr q28, [x2, #32]
fmla v2.2d,v21.2d,v26.2d
fmla v3.2d,v21.2d,v27.2d
dup v29.2d,v4.d[0]
dup v30.2d,v4.d[1]
ldr q4, [x1, #80]
add x1,x1,#128
add x2,x2,#64
fmla v0.2d,v28.2d,v29.2d
dup v31.2d,v4.d[0]
dup v8.2d,v4.d[1]
fmla v1.2d,v28.2d,v30.2d
add x1,x1,#-32
fmla v2.2d,v28.2d,v31.2d
fmla v3.2d,v28.2d,v8.2d
add x2,x2,#-16
.ukr1_done:
cbz x8,.ukr1_taildone
.ukr1_tail:
add x8,x8,#-1
ld1 {v4.2d}, [x1]
ld1 {v5.2d}, [x2]
dup v6.2d,v4.d[0]
dup v7.2d,v4.d[1]
ldr q4, [x1, #16]
fmla v0.2d,v5.2d,v6.2d
fmla v1.2d,v5.2d,v7.2d
dup v16.2d,v4.d[0]
dup v17.2d,v4.d[1]
fmla v2.2d,v5.2d,v16.2d
fmla v3.2d,v5.2d,v17.2d
add x1,x1,#32
add x2,x2,#16
cbnz x8,.ukr1_tail
.ukr1_taildone:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok0_0
b .ukr0_try1
.ukr0_ok0_0:
ldr d4,[x5,#0]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try1
ldr d4,[x4,#0]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok1_0
b .ukr0_try2
.ukr0_ok1_0:
ldr d4,[x5,#0]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try2
b .ukr0_case1
.ukr0_try2:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok2_0
b .ukr0_try3
.ukr0_ok2_0:
ldr d4,[x5,#0]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try3
ldr d4,[x4,#0]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok3_0
b .ukr0_try4
.ukr0_ok3_0:
ldr d4,[x5,#0]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try4
b .ukr0_case3
.ukr0_try4:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok4_0
b .ukr0_try5
.ukr0_ok4_0:
ldr d4,[x4,#0]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try5
b .ukr0_case4
.ukr0_try5:
mov x0,x7
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok5_0
b .ukr0_try6
.ukr0_ok5_0:
b .ukr0_case5
.ukr0_try6:
ldr d4,[x5,#0]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try7
ldr d4,[x4,#0]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try7
b .ukr0_case6
.ukr0_try7:
ldr d4,[x5,#0]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try8
b .ukr0_case7
.ukr0_try8:
ldr d4,[x5,#0]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try9
ldr d4,[x4,#0]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try9
b .ukr0_case8
.ukr0_try9:
ldr d4,[x5,#0]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try10
b .ukr0_case9
.ukr0_try10:
ldr d4,[x4,#0]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try11
b .ukr0_case10
.ukr0_try11:
b .ukr0_case11
.ukr0_try12:
b .ukr0_cases_end
.ukr0_case0:
mov x0,x3
mov x1,x3
mov x2,x0
add x2,x2,x6
mov x8,x0
add x8,x8,x6, LSL #1
mov x9,x0
add x9,x9,x6
add x9,x9,x6, LSL #1
st1 {v0.2d}, [x0]
st1 {v1.2d}, [x2]
st1 {v2.2d}, [x8]
st1 {v3.2d}, [x9]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
mov x1,x3
ld1r {v4.2d}, [x4]
mov x2,x0
add x2,x2,x6
mov x8,x0
add x8,x8,x6, LSL #1
mov x9,x0
add x9,x9,x6
add x9,x9,x6, LSL #1
fmul v5.2d,v0.2d,v4.2d
fmul v0.2d,v1.2d,v4.2d
fmul v1.2d,v2.2d,v4.2d
fmul v2.2d,v3.2d,v4.2d
st1 {v5.2d}, [x0]
st1 {v0.2d}, [x2]
st1 {v1.2d}, [x8]
st1 {v2.2d}, [x9]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x3
mov x2,x0
add x2,x2,x6
mov x8,x0
add x8,x8,x6, LSL #1
ld1 {v4.2d}, [x0]
ld1 {v5.2d}, [x2]
ld1 {v6.2d}, [x8]
mov x9,x1
add x9,x9,x6
fadd v4.2d,v0.2d,v4.2d
mov x10,x0
add x10,x10,x6
add x10,x10,x6, LSL #1
fadd v5.2d,v1.2d,v5.2d
fadd v6.2d,v2.2d,v6.2d
mov x11,x1
add x11,x11,x6, LSL #1
st1 {v4.2d}, [x1]
ld1 {v0.2d}, [x10]
mov x12,x1
add x12,x12,x6
add x12,x12,x6, LSL #1
st1 {v5.2d}, [x9]
st1 {v6.2d}, [x11]
fadd v0.2d,v3.2d,v0.2d
st1 {v0.2d}, [x12]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
mov x1,x3
mov x2,x0
add x2,x2,x6
mov x8,x0
add x8,x8,x6, LSL #1
ld1r {v4.2d}, [x4]
ld1 {v5.2d}, [x0]
ld1 {v6.2d}, [x2]
ld1 {v7.2d}, [x8]
mov x9,x1
add x9,x9,x6
fmla v5.2d,v0.2d,v4.2d
mov x10,x0
add x10,x10,x6
add x10,x10,x6, LSL #1
fmla v6.2d,v1.2d,v4.2d
fmla v7.2d,v2.2d,v4.2d
mov x11,x1
add x11,x11,x6, LSL #1
st1 {v5.2d}, [x1]
ld1 {v0.2d}, [x10]
mov x12,x1
add x12,x12,x6
add x12,x12,x6, LSL #1
st1 {v6.2d}, [x9]
st1 {v7.2d}, [x11]
fmla v0.2d,v3.2d,v4.2d
st1 {v0.2d}, [x12]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
mov x1,x3
mov x2,x0
add x2,x2,x6
mov x8,x0
add x8,x8,x6, LSL #1
ld1r {v4.2d}, [x5]
ld1 {v5.2d}, [x0]
ld1 {v6.2d}, [x2]
ld1 {v7.2d}, [x8]
mov x9,x1
add x9,x9,x6
fmla v0.2d,v5.2d,v4.2d
mov x10,x0
add x10,x10,x6
add x10,x10,x6, LSL #1
fmla v1.2d,v6.2d,v4.2d
fmla v2.2d,v7.2d,v4.2d
mov x11,x1
add x11,x11,x6, LSL #1
st1 {v0.2d}, [x1]
ld1 {v0.2d}, [x10]
mov x12,x1
add x12,x12,x6
add x12,x12,x6, LSL #1
st1 {v1.2d}, [x9]
st1 {v2.2d}, [x11]
fmla v3.2d,v0.2d,v4.2d
st1 {v3.2d}, [x12]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
mov x1,x3
mov x2,x0
add x2,x2,x6
ld1r {v4.2d}, [x5]
mov x8,x0
add x8,x8,x6, LSL #1
ld1 {v5.2d}, [x0]
ld1 {v6.2d}, [x2]
ld1 {v7.2d}, [x8]
ld1r {v16.2d}, [x4]
fmul v5.2d,v5.2d,v4.2d
fmul v6.2d,v6.2d,v4.2d
fmul v7.2d,v7.2d,v4.2d
mov x9,x1
add x9,x9,x6
fmla v5.2d,v0.2d,v16.2d
fmla v6.2d,v1.2d,v16.2d
fmla v7.2d,v2.2d,v16.2d
mov x10,x1
add x10,x10,x6, LSL #1
st1 {v5.2d}, [x1]
mov x11,x0
add x11,x11,x6
add x11,x11,x6, LSL #1
ld1 {v0.2d}, [x11]
mov x12,x1
add x12,x12,x6
add x12,x12,x6, LSL #1
st1 {v6.2d}, [x9]
st1 {v7.2d}, [x10]
fmul v0.2d,v0.2d,v4.2d
fmla v0.2d,v3.2d,v16.2d
st1 {v0.2d}, [x12]
b .ukr0_cases_end
.ukr0_case6:
mov x0,x3
mov x1,x0
add x1,x1,x7
st1 {v0.d}[1], [x1]
mov x2,x0
add x2,x2,x6
mov x8,x0
add x8,x8,x6
mov x1,x2
add x1,x1,x7
st1 {v1.d}[0], [x8]
st1 {v1.d}[1], [x1]
mov x9,x0
add x9,x9,x6, LSL #1
add x8,x8,x6
mov x1,x9
add x1,x1,x7
st1 {v2.d}[0], [x8]
st1 {v0.d}[0], [x0]
st1 {v2.d}[1], [x1]
mov x10,x0
add x10,x10,x6
add x10,x10,x6, LSL #1
add x8,x8,x6
mov x1,x10
add x1,x1,x7
st1 {v3.d}[0], [x8]
st1 {v3.d}[1], [x1]
b .ukr0_cases_end
.ukr0_case7:
mov x0,x3
ld1r {v4.2d}, [x4]
mov x1,x0
add x1,x1,x7
mov x2,x0
add x2,x2,x6
mov x8,x0
add x8,x8,x6
fmul v5.2d,v0.2d,v4.2d
fmul v0.2d,v1.2d,v4.2d
fmul v1.2d,v2.2d,v4.2d
st1 {v5.d}[1], [x1]
mov x1,x2
add x1,x1,x7
st1 {v0.d}[0], [x8]
st1 {v0.d}[1], [x1]
add x8,x8,x6
st1 {v1.d}[0], [x8]
st1 {v5.d}[0], [x0]
mov x9,x0
add x9,x9,x6, LSL #1
fmul v0.2d,v3.2d,v4.2d
mov x1,x9
add x1,x1,x7
st1 {v1.d}[1], [x1]
mov x10,x0
add x10,x10,x6
add x10,x10,x6, LSL #1
add x8,x8,x6
mov x1,x10
add x1,x1,x7
st1 {v0.d}[0], [x8]
st1 {v0.d}[1], [x1]
b .ukr0_cases_end
.ukr0_case8:
mov x0,x3
ld1 {v4.d}[0], [x0]
mov x1,x0
add x1,x1,x7
ld1 {v4.d}[1], [x1]
mov x2,x0
add x2,x2,x6
mov x8,x0
add x8,x8,x6
ld1 {v5.d}[0], [x2]
mov x1,x8
add x1,x1,x7
ld1 {v5.d}[1], [x1]
fadd v4.2d,v0.2d,v4.2d
mov x9,x3
add x9,x9,x7
mov x10,x3
add x10,x10,x6
fadd v5.2d,v1.2d,v5.2d
st1 {v4.d}[1], [x9]
mov x11,x3
add x11,x11,x6
st1 {v4.d}[0], [x3]
add x2,x2,x6
mov x12,x0
add x12,x12,x6, LSL #1
ld1 {v0.d}[0], [x2]
mov x1,x12
add x1,x1,x7
ld1 {v0.d}[1], [x1]
mov x9,x10
add x9,x9,x7
st1 {v5.d}[0], [x11]
st1 {v5.d}[1], [x9]
add x2,x2,x6
mov x13,x0
add x13,x13,x6
add x13,x13,x6, LSL #1
ld1 {v1.d}[0], [x2]
mov x1,x13
add x1,x1,x7
ld1 {v1.d}[1], [x1]
fadd v0.2d,v2.2d,v0.2d
mov x14,x3
add x14,x14,x6, LSL #1
add x11,x11,x6
fadd v1.2d,v3.2d,v1.2d
mov x9,x14
add x9,x9,x7
st1 {v0.d}[0], [x11]
st1 {v0.d}[1], [x9]
mov x15,x3
add x15,x15,x6
add x15,x15,x6, LSL #1
add x11,x11,x6
mov x9,x15
add x9,x9,x7
st1 {v1.d}[0], [x11]
st1 {v1.d}[1], [x9]
b .ukr0_cases_end
.ukr0_case9:
mov x0,x3
ld1 {v4.d}[0], [x0]
mov x1,x0
add x1,x1,x7
ld1 {v4.d}[1], [x1]
ld1r {v5.2d}, [x4]
mov x2,x0
add x2,x2,x6
mov x8,x0
add x8,x8,x6
ld1 {v6.d}[0], [x2]
mov x1,x8
add x1,x1,x7
ld1 {v6.d}[1], [x1]
fmla v4.2d,v0.2d,v5.2d
mov x9,x3
add x9,x9,x7
mov x10,x3
add x10,x10,x6
fmla v6.2d,v1.2d,v5.2d
st1 {v4.d}[1], [x9]
mov x11,x3
add x11,x11,x6
st1 {v4.d}[0], [x3]
add x2,x2,x6
mov x12,x0
add x12,x12,x6, LSL #1
ld1 {v0.d}[0], [x2]
mov x1,x12
add x1,x1,x7
ld1 {v0.d}[1], [x1]
mov x9,x10
add x9,x9,x7
st1 {v6.d}[0], [x11]
st1 {v6.d}[1], [x9]
add x2,x2,x6
mov x13,x0
add x13,x13,x6
add x13,x13,x6, LSL #1
ld1 {v1.d}[0], [x2]
mov x1,x13
add x1,x1,x7
ld1 {v1.d}[1], [x1]
fmla v0.2d,v2.2d,v5.2d
mov x14,x3
add x14,x14,x6, LSL #1
add x11,x11,x6
fmla v1.2d,v3.2d,v5.2d
mov x9,x14
add x9,x9,x7
st1 {v0.d}[0], [x11]
st1 {v0.d}[1], [x9]
mov x15,x3
add x15,x15,x6
add x15,x15,x6, LSL #1
add x11,x11,x6
mov x9,x15
add x9,x9,x7
st1 {v1.d}[0], [x11]
st1 {v1.d}[1], [x9]
b .ukr0_cases_end
.ukr0_case10:
mov x0,x3
ld1 {v4.d}[0], [x0]
mov x1,x0
add x1,x1,x7
ld1 {v4.d}[1], [x1]
ld1r {v5.2d}, [x5]
mov x2,x0
add x2,x2,x6
mov x8,x0
add x8,x8,x6
ld1 {v6.d}[0], [x2]
mov x1,x8
add x1,x1,x7
ld1 {v6.d}[1], [x1]
fmla v0.2d,v4.2d,v5.2d
mov x9,x3
add x9,x9,x7
mov x10,x3
add x10,x10,x6
fmla v1.2d,v6.2d,v5.2d
st1 {v0.d}[1], [x9]
mov x11,x3
add x11,x11,x6
st1 {v0.d}[0], [x3]
add x2,x2,x6
mov x12,x0
add x12,x12,x6, LSL #1
ld1 {v0.d}[0], [x2]
mov x1,x12
add x1,x1,x7
ld1 {v0.d}[1], [x1]
mov x9,x10
add x9,x9,x7
st1 {v1.d}[0], [x11]
st1 {v1.d}[1], [x9]
add x2,x2,x6
mov x13,x0
add x13,x13,x6
add x13,x13,x6, LSL #1
ld1 {v1.d}[0], [x2]
mov x1,x13
add x1,x1,x7
ld1 {v1.d}[1], [x1]
fmla v2.2d,v0.2d,v5.2d
mov x14,x3
add x14,x14,x6, LSL #1
add x11,x11,x6
fmla v3.2d,v1.2d,v5.2d
mov x9,x14
add x9,x9,x7
st1 {v2.d}[0], [x11]
st1 {v2.d}[1], [x9]
mov x15,x3
add x15,x15,x6
add x15,x15,x6, LSL #1
add x11,x11,x6
mov x9,x15
add x9,x9,x7
st1 {v3.d}[0], [x11]
st1 {v3.d}[1], [x9]
b .ukr0_cases_end
.ukr0_case11:
mov x0,x3
ld1 {v4.d}[0], [x0]
mov x1,x0
add x1,x1,x7
ld1 {v4.d}[1], [x1]
ld1r {v5.2d}, [x5]
mov x2,x0
add x2,x2,x6
mov x8,x0
add x8,x8,x6
ld1 {v6.d}[0], [x2]
mov x1,x8
add x1,x1,x7
ld1 {v6.d}[1], [x1]
fmul v4.2d,v4.2d,v5.2d
ld1r {v7.2d}, [x4]
mov x9,x3
add x9,x9,x7
fmul v6.2d,v6.2d,v5.2d
mov x10,x3
add x10,x10,x6
fmla v4.2d,v0.2d,v7.2d
fmla v6.2d,v1.2d,v7.2d
st1 {v4.d}[1], [x9]
st1 {v4.d}[0], [x3]
add x2,x2,x6
mov x11,x0
add x11,x11,x6, LSL #1
ld1 {v0.d}[0], [x2]
mov x1,x11
add x1,x1,x7
ld1 {v0.d}[1], [x1]
mov x12,x3
add x12,x12,x6
mov x9,x12
add x9,x9,x7
st1 {v6.d}[0], [x10]
fmul v0.2d,v0.2d,v5.2d
st1 {v6.d}[1], [x9]
add x2,x2,x6
mov x13,x0
add x13,x13,x6
add x13,x13,x6, LSL #1
ld1 {v1.d}[0], [x2]
mov x1,x13
add x1,x1,x7
ld1 {v1.d}[1], [x1]
fmla v0.2d,v2.2d,v7.2d
mov x14,x3
add x14,x14,x6, LSL #1
add x10,x10,x6
fmul v1.2d,v1.2d,v5.2d
mov x9,x14
add x9,x9,x7
st1 {v0.d}[0], [x10]
st1 {v0.d}[1], [x9]
fmla v1.2d,v3.2d,v7.2d
mov x15,x3
add x15,x15,x6
add x15,x15,x6, LSL #1
add x10,x10,x6
mov x9,x15
add x9,x9,x7
st1 {v1.d}[0], [x10]
st1 {v1.d}[1], [x9]
.ukr0_cases_end:
ldr d8,[sp,#0]
add sp,sp,#16
ret
.section .note.GNU-stack,"",%progbits
