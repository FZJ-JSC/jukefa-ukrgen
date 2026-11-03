.text
.global bli_dgemm_ukrgen_neon_vm_2x4_asm
.type bli_dgemm_ukrgen_neon_vm_2x4_asm, %function
bli_dgemm_ukrgen_neon_vm_2x4_asm:
.cfi_startproc
# x0 = k
# x1 = base(A)
# x2 = base(B)
# x3 = base(C)
# x4 = base(alpha)
# x5 = base(beta)
# x6 = stride(C,m)
# x7 = stride(C,n)
mov x8,x7
sub x8,x8,x6
and x9,x0,#3
lsr x0,x0,#2
dup v0.2d,xzr
dup v1.2d,xzr
dup v2.2d,xzr
dup v3.2d,xzr
cbz x0,.ukr1_done
ld1 {v4.2d}, [x1]
ld1 {v5.2d}, [x2]
ldr q6, [x2, #16]
add x1,x1,#16
add x2,x2,#32
add x0,x0,#-1
cbz x0,.ukr1_last
.ukr1_loop:
add x0,x0,#-1
fmla v0.2d,v4.2d,v5.d[0]
fmla v1.2d,v4.2d,v5.d[1]
fmla v2.2d,v4.2d,v6.d[0]
fmla v3.2d,v4.2d,v6.d[1]
ld1 {v7.2d}, [x1]
ld1 {v16.2d}, [x2]
ldr q17, [x2, #16]
ldr q18, [x1, #16]
ldr q19, [x2, #32]
fmla v0.2d,v7.2d,v16.d[0]
fmla v1.2d,v7.2d,v16.d[1]
fmla v2.2d,v7.2d,v17.d[0]
fmla v3.2d,v7.2d,v17.d[1]
ldr q20, [x2, #48]
fmla v0.2d,v18.2d,v19.d[0]
fmla v1.2d,v18.2d,v19.d[1]
ldr q21, [x1, #32]
fmla v2.2d,v18.2d,v20.d[0]
fmla v3.2d,v18.2d,v20.d[1]
ldr q22, [x2, #64]
ldr q23, [x2, #80]
ldr q4, [x1, #48]
ldr q5, [x2, #96]
ldr q6, [x2, #112]
fmla v0.2d,v21.2d,v22.d[0]
fmla v1.2d,v21.2d,v22.d[1]
fmla v2.2d,v21.2d,v23.d[0]
fmla v3.2d,v21.2d,v23.d[1]
add x1,x1,#64
add x2,x2,#128
cbnz x0,.ukr1_loop
.ukr1_last:
fmla v0.2d,v4.2d,v5.d[0]
fmla v1.2d,v4.2d,v5.d[1]
fmla v2.2d,v4.2d,v6.d[0]
fmla v3.2d,v4.2d,v6.d[1]
ld1 {v7.2d}, [x1]
ld1 {v16.2d}, [x2]
ldr q17, [x2, #16]
ldr q18, [x1, #16]
ldr q19, [x2, #32]
fmla v0.2d,v7.2d,v16.d[0]
fmla v1.2d,v7.2d,v16.d[1]
fmla v2.2d,v7.2d,v17.d[0]
fmla v3.2d,v7.2d,v17.d[1]
ldr q20, [x2, #48]
fmla v0.2d,v18.2d,v19.d[0]
fmla v1.2d,v18.2d,v19.d[1]
ldr q21, [x1, #32]
fmla v2.2d,v18.2d,v20.d[0]
fmla v3.2d,v18.2d,v20.d[1]
ldr q22, [x2, #64]
ldr q23, [x2, #80]
add x1,x1,#48
add x2,x2,#96
fmla v0.2d,v21.2d,v22.d[0]
fmla v1.2d,v21.2d,v22.d[1]
fmla v2.2d,v21.2d,v23.d[0]
fmla v3.2d,v21.2d,v23.d[1]
.ukr1_done:
cbz x9,.ukr1_taildone
.ukr1_tail:
add x9,x9,#-1
ld1 {v4.2d}, [x1]
ld1 {v5.2d}, [x2]
ldr q6, [x2, #16]
fmla v0.2d,v4.2d,v5.d[0]
fmla v1.2d,v4.2d,v5.d[1]
fmla v2.2d,v4.2d,v6.d[0]
fmla v3.2d,v4.2d,v6.d[1]
add x1,x1,#16
add x2,x2,#32
cbnz x9,.ukr1_tail
.ukr1_taildone:
mov x0,x6
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok0_0
b .ukr0_try1
.ukr0_ok0_0:
ldr d4, [x5]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try1
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try1
b .ukr0_case0
.ukr0_try1:
mov x0,x6
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok1_0
b .ukr0_try2
.ukr0_ok1_0:
ldr d4, [x5]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try2
b .ukr0_case1
.ukr0_try2:
mov x0,x6
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok2_0
b .ukr0_try3
.ukr0_ok2_0:
ldr d4, [x5]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try3
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try3
b .ukr0_case2
.ukr0_try3:
mov x0,x6
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok3_0
b .ukr0_try4
.ukr0_ok3_0:
ldr d4, [x5]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try4
b .ukr0_case3
.ukr0_try4:
mov x0,x6
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok4_0
b .ukr0_try5
.ukr0_ok4_0:
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try5
b .ukr0_case4
.ukr0_try5:
mov x0,x6
add x0,x0,#-8
cmp x0,0
b.eq .ukr0_ok5_0
b .ukr0_try6
.ukr0_ok5_0:
b .ukr0_case5
.ukr0_try6:
ldr d4, [x5]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try7
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try7
b .ukr0_case6
.ukr0_try7:
ldr d4, [x5]
fmov d5,xzr
fcmp d4,d5
b.ne .ukr0_try8
b .ukr0_case7
.ukr0_try8:
ldr d4, [x5]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try9
ldr d4, [x4]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try9
b .ukr0_case8
.ukr0_try9:
ldr d4, [x5]
mov x0,#4607182418800017408
fmov d5,x0
fcmp d4,d5
b.ne .ukr0_try10
b .ukr0_case9
.ukr0_try10:
ldr d4, [x4]
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
st1 {v0.2d}, [x0]
add x0,x0,x7
st1 {v1.2d}, [x0], x7
st1 {v2.2d}, [x0], x7
st1 {v3.2d}, [x0]
b .ukr0_cases_end
.ukr0_case1:
mov x0,x3
mov x1,x3
ld1r {v4.2d}, [x4]
fmul v5.2d,v0.2d,v4.2d
fmul v0.2d,v1.2d,v4.2d
fmul v1.2d,v2.2d,v4.2d
fmul v2.2d,v3.2d,v4.2d
st1 {v5.2d}, [x0]
add x0,x0,x7
st1 {v0.2d}, [x0], x7
st1 {v1.2d}, [x0], x7
st1 {v2.2d}, [x0]
b .ukr0_cases_end
.ukr0_case2:
mov x0,x3
mov x1,x3
ld1 {v4.2d}, [x0]
add x0,x0,x7
ld1 {v5.2d}, [x0], x7
ld1 {v6.2d}, [x0], x7
fadd v4.2d,v0.2d,v4.2d
ld1 {v0.2d}, [x0]
fadd v5.2d,v1.2d,v5.2d
fadd v6.2d,v2.2d,v6.2d
st1 {v4.2d}, [x1]
fadd v0.2d,v3.2d,v0.2d
add x1,x1,x7
st1 {v5.2d}, [x1], x7
st1 {v6.2d}, [x1], x7
st1 {v0.2d}, [x1]
b .ukr0_cases_end
.ukr0_case3:
mov x0,x3
mov x1,x3
ld1r {v4.2d}, [x4]
ld1 {v5.2d}, [x0]
add x0,x0,x7
ld1 {v6.2d}, [x0], x7
ld1 {v7.2d}, [x0], x7
fmla v5.2d,v0.2d,v4.2d
ld1 {v0.2d}, [x0]
fmla v6.2d,v1.2d,v4.2d
fmla v7.2d,v2.2d,v4.2d
st1 {v5.2d}, [x1]
fmla v0.2d,v3.2d,v4.2d
add x1,x1,x7
st1 {v6.2d}, [x1], x7
st1 {v7.2d}, [x1], x7
st1 {v0.2d}, [x1]
b .ukr0_cases_end
.ukr0_case4:
mov x0,x3
mov x1,x3
ld1r {v4.2d}, [x5]
ld1 {v5.2d}, [x0]
add x0,x0,x7
ld1 {v6.2d}, [x0], x7
ld1 {v7.2d}, [x0], x7
fmla v0.2d,v5.2d,v4.2d
ld1 {v5.2d}, [x0]
fmla v1.2d,v6.2d,v4.2d
fmla v2.2d,v7.2d,v4.2d
st1 {v0.2d}, [x1]
fmla v3.2d,v5.2d,v4.2d
add x1,x1,x7
st1 {v1.2d}, [x1], x7
st1 {v2.2d}, [x1], x7
st1 {v3.2d}, [x1]
b .ukr0_cases_end
.ukr0_case5:
mov x0,x3
mov x1,x3
ld1r {v4.2d}, [x5]
ld1 {v5.2d}, [x0]
add x0,x0,x7
ld1 {v6.2d}, [x0], x7
ld1 {v7.2d}, [x0], x7
fmul v5.2d,v5.2d,v4.2d
ld1r {v16.2d}, [x4]
fmul v6.2d,v6.2d,v4.2d
fmul v7.2d,v7.2d,v4.2d
fmla v5.2d,v0.2d,v16.2d
ld1 {v0.2d}, [x0]
fmla v6.2d,v1.2d,v16.2d
fmla v7.2d,v2.2d,v16.2d
st1 {v5.2d}, [x1]
fmul v0.2d,v0.2d,v4.2d
add x1,x1,x7
st1 {v6.2d}, [x1], x7
st1 {v7.2d}, [x1], x7
fmla v0.2d,v3.2d,v16.2d
st1 {v0.2d}, [x1]
b .ukr0_cases_end
.ukr0_case6:
mov x0,x3
st1 {v0.d}[0], [x0]
add x0,x0,x6
st1 {v0.d}[1], [x0], x8
st1 {v1.d}[0], [x0], x6
st1 {v1.d}[1], [x0], x8
st1 {v2.d}[0], [x0], x6
st1 {v2.d}[1], [x0], x8
st1 {v3.d}[0], [x0], x6
st1 {v3.d}[1], [x0]
b .ukr0_cases_end
.ukr0_case7:
mov x0,x3
ld1r {v4.2d}, [x4]
fmul v5.2d,v0.2d,v4.2d
fmul v0.2d,v1.2d,v4.2d
fmul v1.2d,v2.2d,v4.2d
fmul v2.2d,v3.2d,v4.2d
st1 {v5.d}[0], [x0]
add x0,x0,x6
st1 {v5.d}[1], [x0], x8
st1 {v0.d}[0], [x0], x6
st1 {v0.d}[1], [x0], x8
st1 {v1.d}[0], [x0], x6
st1 {v1.d}[1], [x0], x8
st1 {v2.d}[0], [x0], x6
st1 {v2.d}[1], [x0]
b .ukr0_cases_end
.ukr0_case8:
mov x0,x3
ld1 {v4.d}[0], [x0]
add x0,x0,x6
ld1 {v4.d}[1], [x0], x8
ld1 {v5.d}[0], [x0], x6
ld1 {v5.d}[1], [x0], x8
ld1 {v6.d}[0], [x0], x6
fadd v4.2d,v0.2d,v4.2d
ld1 {v6.d}[1], [x0], x8
fadd v5.2d,v1.2d,v5.2d
st1 {v4.d}[0], [x3]
add x3,x3,x6
ld1 {v0.d}[0], [x0], x6
fadd v6.2d,v2.2d,v6.2d
st1 {v4.d}[1], [x3], x8
ld1 {v0.d}[1], [x0]
st1 {v5.d}[0], [x3], x6
st1 {v5.d}[1], [x3], x8
st1 {v6.d}[0], [x3], x6
fadd v0.2d,v3.2d,v0.2d
st1 {v6.d}[1], [x3], x8
st1 {v0.d}[0], [x3], x6
st1 {v0.d}[1], [x3]
b .ukr0_cases_end
.ukr0_case9:
mov x0,x3
ld1 {v4.d}[0], [x0]
add x0,x0,x6
ld1 {v4.d}[1], [x0], x8
ld1r {v5.2d}, [x4]
ld1 {v6.d}[0], [x0], x6
ld1 {v6.d}[1], [x0], x8
ld1 {v7.d}[0], [x0], x6
fmla v4.2d,v0.2d,v5.2d
ld1 {v7.d}[1], [x0], x8
fmla v6.2d,v1.2d,v5.2d
st1 {v4.d}[0], [x3]
add x3,x3,x6
ld1 {v0.d}[0], [x0], x6
fmla v7.2d,v2.2d,v5.2d
st1 {v4.d}[1], [x3], x8
ld1 {v0.d}[1], [x0]
st1 {v6.d}[0], [x3], x6
st1 {v6.d}[1], [x3], x8
st1 {v7.d}[0], [x3], x6
fmla v0.2d,v3.2d,v5.2d
st1 {v7.d}[1], [x3], x8
st1 {v0.d}[0], [x3], x6
st1 {v0.d}[1], [x3]
b .ukr0_cases_end
.ukr0_case10:
mov x0,x3
ld1 {v4.d}[0], [x0]
add x0,x0,x6
ld1 {v4.d}[1], [x0], x8
ld1r {v5.2d}, [x5]
ld1 {v6.d}[0], [x0], x6
ld1 {v6.d}[1], [x0], x8
ld1 {v7.d}[0], [x0], x6
fmla v0.2d,v4.2d,v5.2d
ld1 {v7.d}[1], [x0], x8
fmla v1.2d,v6.2d,v5.2d
st1 {v0.d}[0], [x3]
add x3,x3,x6
ld1 {v4.d}[0], [x0], x6
fmla v2.2d,v7.2d,v5.2d
st1 {v0.d}[1], [x3], x8
ld1 {v4.d}[1], [x0]
st1 {v1.d}[0], [x3], x6
st1 {v1.d}[1], [x3], x8
st1 {v2.d}[0], [x3], x6
fmla v3.2d,v4.2d,v5.2d
st1 {v2.d}[1], [x3], x8
st1 {v3.d}[0], [x3], x6
st1 {v3.d}[1], [x3]
b .ukr0_cases_end
.ukr0_case11:
mov x0,x3
ld1 {v4.d}[0], [x0]
add x0,x0,x6
ld1 {v4.d}[1], [x0], x8
ld1r {v5.2d}, [x5]
ld1 {v6.d}[0], [x0], x6
ld1 {v6.d}[1], [x0], x8
ld1r {v7.2d}, [x4]
fmul v4.2d,v4.2d,v5.2d
ld1 {v16.d}[0], [x0], x6
ld1 {v16.d}[1], [x0], x8
fmul v6.2d,v6.2d,v5.2d
fmla v4.2d,v0.2d,v7.2d
fmul v16.2d,v16.2d,v5.2d
fmla v6.2d,v1.2d,v7.2d
st1 {v4.d}[0], [x3]
add x3,x3,x6
fmla v16.2d,v2.2d,v7.2d
st1 {v4.d}[1], [x3], x8
ld1 {v0.d}[0], [x0], x6
ld1 {v0.d}[1], [x0]
st1 {v6.d}[0], [x3], x6
st1 {v6.d}[1], [x3], x8
st1 {v16.d}[0], [x3], x6
fmul v0.2d,v0.2d,v5.2d
st1 {v16.d}[1], [x3], x8
fmla v0.2d,v3.2d,v7.2d
st1 {v0.d}[0], [x3], x6
st1 {v0.d}[1], [x3]
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dgemm_ukrgen_neon_vm_2x4_asm, .-bli_dgemm_ukrgen_neon_vm_2x4_asm
.section .note.GNU-stack,"",%progbits
