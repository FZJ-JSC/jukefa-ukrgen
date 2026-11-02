.text
.global bli_dgemm_ukrgen_neon_vm_2x4_asm
.type bli_dgemm_ukrgen_neon_vm_2x4_asm, %function
bli_dgemm_ukrgen_neon_vm_2x4_asm:
.cfi_startproc
add sp,sp,#-16
.cfi_adjust_cfa_offset 16
str d8, [sp]
.cfi_rel_offset d8, 0
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
ld1 {v4.2d}, [x2]
ld1 {v5.2d}, [x1]
dup v6.2d,v4.d[0]
dup v7.2d,v4.d[1]
ldr q4, [x2, #16]
add x1,x1,#16
dup v16.2d,v4.d[0]
dup v17.2d,v4.d[1]
add x2,x2,#32
add x0,x0,#-1
cbz x0,.ukr1_last
.ukr1_loop:
add x0,x0,#-1
ld1 {v4.2d}, [x2]
fmla v0.2d,v5.2d,v6.2d
fmla v1.2d,v5.2d,v7.2d
fmla v2.2d,v5.2d,v16.2d
dup v18.2d,v4.d[0]
dup v19.2d,v4.d[1]
ldr q4, [x2, #16]
fmla v3.2d,v5.2d,v17.2d
ld1 {v20.2d}, [x1]
ldr q21, [x1, #16]
dup v22.2d,v4.d[0]
dup v23.2d,v4.d[1]
ldr q4, [x2, #32]
fmla v0.2d,v20.2d,v18.2d
fmla v1.2d,v20.2d,v19.2d
fmla v2.2d,v20.2d,v22.2d
dup v24.2d,v4.d[0]
dup v25.2d,v4.d[1]
ldr q4, [x2, #48]
fmla v3.2d,v20.2d,v23.2d
fmla v0.2d,v21.2d,v24.2d
fmla v1.2d,v21.2d,v25.2d
dup v26.2d,v4.d[0]
dup v27.2d,v4.d[1]
ldr q4, [x2, #64]
ldr q28, [x1, #32]
fmla v2.2d,v21.2d,v26.2d
fmla v3.2d,v21.2d,v27.2d
dup v29.2d,v4.d[0]
dup v30.2d,v4.d[1]
ldr q4, [x2, #80]
ldr q5, [x1, #48]
fmla v0.2d,v28.2d,v29.2d
fmla v1.2d,v28.2d,v30.2d
dup v31.2d,v4.d[0]
dup v8.2d,v4.d[1]
ldr q4, [x2, #96]
add x1,x1,#64
fmla v2.2d,v28.2d,v31.2d
fmla v3.2d,v28.2d,v8.2d
dup v6.2d,v4.d[0]
dup v7.2d,v4.d[1]
ldr q4, [x2, #112]
add x2,x2,#128
dup v16.2d,v4.d[0]
dup v17.2d,v4.d[1]
cbnz x0,.ukr1_loop
.ukr1_last:
ld1 {v4.2d}, [x2]
fmla v0.2d,v5.2d,v6.2d
fmla v1.2d,v5.2d,v7.2d
fmla v2.2d,v5.2d,v16.2d
dup v18.2d,v4.d[0]
dup v19.2d,v4.d[1]
ldr q4, [x2, #16]
fmla v3.2d,v5.2d,v17.2d
ld1 {v20.2d}, [x1]
ldr q21, [x1, #16]
dup v22.2d,v4.d[0]
dup v23.2d,v4.d[1]
ldr q4, [x2, #32]
fmla v0.2d,v20.2d,v18.2d
fmla v1.2d,v20.2d,v19.2d
fmla v2.2d,v20.2d,v22.2d
dup v24.2d,v4.d[0]
dup v25.2d,v4.d[1]
ldr q4, [x2, #48]
fmla v3.2d,v20.2d,v23.2d
fmla v0.2d,v21.2d,v24.2d
fmla v1.2d,v21.2d,v25.2d
dup v26.2d,v4.d[0]
dup v27.2d,v4.d[1]
ldr q4, [x2, #64]
ldr q28, [x1, #32]
fmla v2.2d,v21.2d,v26.2d
fmla v3.2d,v21.2d,v27.2d
dup v29.2d,v4.d[0]
dup v30.2d,v4.d[1]
ldr q4, [x2, #80]
add x1,x1,#48
fmla v0.2d,v28.2d,v29.2d
fmla v1.2d,v28.2d,v30.2d
dup v31.2d,v4.d[0]
dup v8.2d,v4.d[1]
add x2,x2,#96
fmla v2.2d,v28.2d,v31.2d
fmla v3.2d,v28.2d,v8.2d
.ukr1_done:
cbz x8,.ukr1_taildone
.ukr1_tail:
add x8,x8,#-1
ld1 {v4.2d}, [x2]
ld1 {v5.2d}, [x1]
dup v6.2d,v4.d[0]
dup v7.2d,v4.d[1]
ldr q4, [x2, #16]
fmla v0.2d,v5.2d,v6.2d
fmla v1.2d,v5.2d,v7.2d
dup v16.2d,v4.d[0]
dup v17.2d,v4.d[1]
fmla v2.2d,v5.2d,v16.2d
fmla v3.2d,v5.2d,v17.2d
add x1,x1,#16
add x2,x2,#32
cbnz x8,.ukr1_tail
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
st1 {v0.d}[1], [x0]
sub x0,x0,x6
add x0,x0,x7
st1 {v1.d}[0], [x0], x6
st1 {v1.d}[1], [x0]
sub x0,x0,x6
add x0,x0,x7
st1 {v2.d}[0], [x0], x6
st1 {v2.d}[1], [x0]
sub x0,x0,x6
add x0,x0,x7
st1 {v3.d}[0], [x0], x6
st1 {v3.d}[1], [x0]
b .ukr0_cases_end
.ukr0_case7:
mov x0,x3
ld1r {v4.2d}, [x4]
fmul v5.2d,v0.2d,v4.2d
fmul v0.2d,v1.2d,v4.2d
fmul v1.2d,v2.2d,v4.2d
st1 {v5.d}[0], [x0]
add x0,x0,x6
st1 {v5.d}[1], [x0]
sub x0,x0,x6
add x0,x0,x7
st1 {v0.d}[0], [x0], x6
st1 {v0.d}[1], [x0]
sub x0,x0,x6
add x0,x0,x7
st1 {v1.d}[0], [x0], x6
fmul v0.2d,v3.2d,v4.2d
st1 {v1.d}[1], [x0]
sub x0,x0,x6
add x0,x0,x7
st1 {v0.d}[0], [x0], x6
st1 {v0.d}[1], [x0]
b .ukr0_cases_end
.ukr0_case8:
mov x0,x3
ld1 {v4.d}[0], [x0]
add x0,x0,x6
ld1 {v4.d}[1], [x0]
sub x0,x0,x6
add x0,x0,x7
ld1 {v5.d}[0], [x0], x6
fadd v4.2d,v0.2d,v4.2d
ld1 {v5.d}[1], [x0]
st1 {v4.d}[0], [x3]
sub x0,x0,x6
add x3,x3,x6
add x0,x0,x7
fadd v5.2d,v1.2d,v5.2d
st1 {v4.d}[1], [x3]
ld1 {v0.d}[0], [x0], x6
ld1 {v0.d}[1], [x0]
sub x3,x3,x6
add x3,x3,x7
sub x0,x0,x6
st1 {v5.d}[0], [x3], x6
add x0,x0,x7
fadd v0.2d,v2.2d,v0.2d
st1 {v5.d}[1], [x3]
ld1 {v1.d}[0], [x0], x6
ld1 {v1.d}[1], [x0]
sub x3,x3,x6
add x3,x3,x7
st1 {v0.d}[0], [x3], x6
fadd v1.2d,v3.2d,v1.2d
st1 {v0.d}[1], [x3]
sub x3,x3,x6
add x3,x3,x7
st1 {v1.d}[0], [x3], x6
st1 {v1.d}[1], [x3]
b .ukr0_cases_end
.ukr0_case9:
mov x0,x3
ld1 {v4.d}[0], [x0]
add x0,x0,x6
ld1 {v4.d}[1], [x0]
ld1r {v5.2d}, [x4]
sub x0,x0,x6
add x0,x0,x7
ld1 {v6.d}[0], [x0], x6
fmla v4.2d,v0.2d,v5.2d
ld1 {v6.d}[1], [x0]
st1 {v4.d}[0], [x3]
sub x0,x0,x6
add x3,x3,x6
add x0,x0,x7
fmla v6.2d,v1.2d,v5.2d
st1 {v4.d}[1], [x3]
ld1 {v0.d}[0], [x0], x6
ld1 {v0.d}[1], [x0]
sub x3,x3,x6
add x3,x3,x7
sub x0,x0,x6
st1 {v6.d}[0], [x3], x6
add x0,x0,x7
fmla v0.2d,v2.2d,v5.2d
st1 {v6.d}[1], [x3]
ld1 {v1.d}[0], [x0], x6
ld1 {v1.d}[1], [x0]
sub x3,x3,x6
add x3,x3,x7
st1 {v0.d}[0], [x3], x6
fmla v1.2d,v3.2d,v5.2d
st1 {v0.d}[1], [x3]
sub x3,x3,x6
add x3,x3,x7
st1 {v1.d}[0], [x3], x6
st1 {v1.d}[1], [x3]
b .ukr0_cases_end
.ukr0_case10:
mov x0,x3
ld1 {v4.d}[0], [x0]
add x0,x0,x6
ld1 {v4.d}[1], [x0]
ld1r {v5.2d}, [x5]
sub x0,x0,x6
add x0,x0,x7
ld1 {v6.d}[0], [x0], x6
fmla v0.2d,v4.2d,v5.2d
ld1 {v6.d}[1], [x0]
st1 {v0.d}[0], [x3]
sub x0,x0,x6
add x3,x3,x6
add x0,x0,x7
fmla v1.2d,v6.2d,v5.2d
st1 {v0.d}[1], [x3]
ld1 {v0.d}[0], [x0], x6
ld1 {v0.d}[1], [x0]
sub x3,x3,x6
add x3,x3,x7
sub x0,x0,x6
st1 {v1.d}[0], [x3], x6
add x0,x0,x7
fmla v2.2d,v0.2d,v5.2d
st1 {v1.d}[1], [x3]
ld1 {v0.d}[0], [x0], x6
ld1 {v0.d}[1], [x0]
sub x3,x3,x6
add x3,x3,x7
st1 {v2.d}[0], [x3], x6
fmla v3.2d,v0.2d,v5.2d
st1 {v2.d}[1], [x3]
sub x3,x3,x6
add x3,x3,x7
st1 {v3.d}[0], [x3], x6
st1 {v3.d}[1], [x3]
b .ukr0_cases_end
.ukr0_case11:
mov x0,x3
ld1 {v4.d}[0], [x0]
add x0,x0,x6
ld1 {v4.d}[1], [x0]
ld1r {v5.2d}, [x5]
sub x0,x0,x6
add x0,x0,x7
ld1r {v6.2d}, [x4]
fmul v4.2d,v4.2d,v5.2d
ld1 {v7.d}[0], [x0], x6
ld1 {v7.d}[1], [x0]
fmla v4.2d,v0.2d,v6.2d
fmul v7.2d,v7.2d,v5.2d
st1 {v4.d}[0], [x3]
add x3,x3,x6
sub x0,x0,x6
fmla v7.2d,v1.2d,v6.2d
st1 {v4.d}[1], [x3]
add x0,x0,x7
ld1 {v0.d}[0], [x0], x6
ld1 {v0.d}[1], [x0]
sub x3,x3,x6
add x3,x3,x7
st1 {v7.d}[0], [x3], x6
sub x0,x0,x6
fmul v0.2d,v0.2d,v5.2d
st1 {v7.d}[1], [x3]
add x0,x0,x7
ld1 {v1.d}[0], [x0], x6
ld1 {v1.d}[1], [x0]
fmla v0.2d,v2.2d,v6.2d
sub x3,x3,x6
add x3,x3,x7
fmul v1.2d,v1.2d,v5.2d
st1 {v0.d}[0], [x3], x6
st1 {v0.d}[1], [x3]
sub x3,x3,x6
fmla v1.2d,v3.2d,v6.2d
add x3,x3,x7
st1 {v1.d}[0], [x3], x6
st1 {v1.d}[1], [x3]
.ukr0_cases_end:
ldr d8, [sp]
.cfi_restore d8
add sp,sp,#16
.cfi_adjust_cfa_offset -16
ret
.cfi_endproc
.size bli_dgemm_ukrgen_neon_vm_2x4_asm, .-bli_dgemm_ukrgen_neon_vm_2x4_asm
.section .note.GNU-stack,"",%progbits
