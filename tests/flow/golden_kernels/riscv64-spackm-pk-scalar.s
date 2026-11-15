### bli_spackm_ukrgen_riscv64_pk_scalar1
.text
.global bli_spackm_ukrgen_riscv64_pk_scalar1_asm
.type bli_spackm_ukrgen_riscv64_pk_scalar1_asm, %function
bli_spackm_ukrgen_riscv64_pk_scalar1_asm:
.cfi_startproc
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
flw f0, 0(a3)
li t0,1065353216
fmv.w.x f1,t0
feq.s t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,7
srli a0,a0,3
beq a0,zero,.ukr1_done
flw f0, 0(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsw f0, 0(a2)
add a2,a2,a5
flw f1, 0(a1)
add a1,a1,a4
flw f2, 0(a1)
fsw f1, 0(a2)
add a1,a1,a4
add a2,a2,a5
flw f3, 0(a1)
fsw f2, 0(a2)
add a1,a1,a4
add a2,a2,a5
flw f4, 0(a1)
fsw f3, 0(a2)
add a1,a1,a4
add a2,a2,a5
flw f5, 0(a1)
fsw f4, 0(a2)
add a1,a1,a4
add a2,a2,a5
flw f6, 0(a1)
fsw f5, 0(a2)
add a1,a1,a4
add a2,a2,a5
flw f7, 0(a1)
fsw f6, 0(a2)
add a1,a1,a4
add a2,a2,a5
flw f0, 0(a1)
fsw f7, 0(a2)
add a2,a2,a5
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsw f0, 0(a2)
add a2,a2,a5
flw f1, 0(a1)
add a1,a1,a4
flw f2, 0(a1)
fsw f1, 0(a2)
add a1,a1,a4
add a2,a2,a5
flw f3, 0(a1)
fsw f2, 0(a2)
add a1,a1,a4
add a2,a2,a5
flw f4, 0(a1)
fsw f3, 0(a2)
add a1,a1,a4
add a2,a2,a5
flw f5, 0(a1)
fsw f4, 0(a2)
add a1,a1,a4
add a2,a2,a5
flw f6, 0(a1)
fsw f5, 0(a2)
add a1,a1,a4
add a2,a2,a5
flw f7, 0(a1)
fsw f6, 0(a2)
add a1,a1,a4
add a2,a2,a5
fsw f7, 0(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
flw f0, 0(a1)
fsw f0, 0(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,7
srli a0,a0,3
flw f0, 0(a3)
beq a0,zero,.ukr2_done
flw f1, 0(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
add a1,a1,a4
fmul.s f2,f1,f0
flw f3, 0(a1)
add a1,a1,a4
fsw f2, 0(a2)
fmul.s f4,f3,f0
flw f5, 0(a1)
add a1,a1,a4
add a2,a2,a5
fmul.s f6,f5,f0
flw f7, 0(a1)
fsw f4, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f10,f7,f0
flw f11, 0(a1)
fsw f6, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f12,f11,f0
flw f13, 0(a1)
fsw f10, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f14,f13,f0
flw f15, 0(a1)
fsw f12, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f16,f15,f0
flw f17, 0(a1)
fsw f14, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f28,f17,f0
flw f1, 0(a1)
fsw f16, 0(a2)
add a2,a2,a5
fsw f28, 0(a2)
add a2,a2,a5
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.s f2,f1,f0
flw f3, 0(a1)
add a1,a1,a4
fsw f2, 0(a2)
fmul.s f4,f3,f0
flw f5, 0(a1)
add a1,a1,a4
add a2,a2,a5
fmul.s f6,f5,f0
flw f7, 0(a1)
fsw f4, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f10,f7,f0
flw f11, 0(a1)
fsw f6, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f12,f11,f0
flw f13, 0(a1)
fsw f10, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f14,f13,f0
flw f15, 0(a1)
fsw f12, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f16,f15,f0
flw f17, 0(a1)
fsw f14, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f28,f17,f0
fsw f16, 0(a2)
add a2,a2,a5
fsw f28, 0(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
flw f1, 0(a1)
fmul.s f2,f1,f0
fsw f2, 0(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr2_tail
.ukr2_taildone:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_spackm_ukrgen_riscv64_pk_scalar1_asm, .-bli_spackm_ukrgen_riscv64_pk_scalar1_asm
.section .note.GNU-stack,"",%progbits


### bli_spackm_ukrgen_riscv64_pk_scalar2
.text
.global bli_spackm_ukrgen_riscv64_pk_scalar2_asm
.type bli_spackm_ukrgen_riscv64_pk_scalar2_asm, %function
bli_spackm_ukrgen_riscv64_pk_scalar2_asm:
.cfi_startproc
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
flw f0, 0(a3)
li t0,1065353216
fmv.w.x f1,t0
feq.s t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,3
srli a0,a0,2
beq a0,zero,.ukr1_done
flw f0, 0(a1)
flw f1, 4(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f2, 0(a1)
add a2,a2,a5
flw f3, 4(a1)
add a1,a1,a4
fsw f2, 0(a2)
flw f4, 0(a1)
flw f5, 4(a1)
fsw f3, 4(a2)
add a1,a1,a4
add a2,a2,a5
flw f6, 0(a1)
flw f7, 4(a1)
fsw f4, 0(a2)
add a1,a1,a4
fsw f5, 4(a2)
add a2,a2,a5
flw f0, 0(a1)
flw f1, 4(a1)
fsw f6, 0(a2)
fsw f7, 4(a2)
add a2,a2,a5
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f2, 0(a1)
add a2,a2,a5
flw f3, 4(a1)
add a1,a1,a4
fsw f2, 0(a2)
flw f4, 0(a1)
flw f5, 4(a1)
fsw f3, 4(a2)
add a1,a1,a4
add a2,a2,a5
flw f6, 0(a1)
flw f7, 4(a1)
fsw f4, 0(a2)
add a1,a1,a4
fsw f5, 4(a2)
add a2,a2,a5
fsw f6, 0(a2)
fsw f7, 4(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
flw f0, 0(a1)
flw f1, 4(a1)
fsw f0, 0(a2)
fsw f1, 4(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,3
srli a0,a0,2
flw f0, 0(a3)
beq a0,zero,.ukr2_done
flw f1, 0(a1)
flw f2, 4(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
add a1,a1,a4
fmul.s f3,f1,f0
fmul.s f4,f2,f0
flw f5, 0(a1)
flw f6, 4(a1)
add a1,a1,a4
fsw f3, 0(a2)
fmul.s f7,f5,f0
fsw f4, 4(a2)
fmul.s f10,f6,f0
flw f11, 0(a1)
flw f12, 4(a1)
add a2,a2,a5
add a1,a1,a4
fmul.s f13,f11,f0
fsw f7, 0(a2)
fmul.s f14,f12,f0
flw f15, 0(a1)
flw f16, 4(a1)
fsw f10, 4(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f17,f15,f0
flw f1, 0(a1)
fmul.s f28,f16,f0
fsw f13, 0(a2)
fsw f14, 4(a2)
add a2,a2,a5
flw f2, 4(a1)
fsw f17, 0(a2)
fsw f28, 4(a2)
add a2,a2,a5
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.s f3,f1,f0
fmul.s f4,f2,f0
flw f5, 0(a1)
flw f6, 4(a1)
add a1,a1,a4
fsw f3, 0(a2)
fmul.s f7,f5,f0
fsw f4, 4(a2)
fmul.s f10,f6,f0
flw f11, 0(a1)
flw f12, 4(a1)
add a2,a2,a5
add a1,a1,a4
fmul.s f13,f11,f0
fsw f7, 0(a2)
fmul.s f14,f12,f0
flw f15, 0(a1)
flw f16, 4(a1)
fsw f10, 4(a2)
add a1,a1,a4
add a2,a2,a5
fmul.s f17,f15,f0
fmul.s f28,f16,f0
fsw f13, 0(a2)
fsw f14, 4(a2)
add a2,a2,a5
fsw f17, 0(a2)
fsw f28, 4(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
flw f1, 0(a1)
flw f2, 4(a1)
fmul.s f3,f1,f0
fmul.s f4,f2,f0
fsw f3, 0(a2)
fsw f4, 4(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr2_tail
.ukr2_taildone:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_spackm_ukrgen_riscv64_pk_scalar2_asm, .-bli_spackm_ukrgen_riscv64_pk_scalar2_asm
.section .note.GNU-stack,"",%progbits


### bli_spackm_ukrgen_riscv64_pk_scalar3
.text
.global bli_spackm_ukrgen_riscv64_pk_scalar3_asm
.type bli_spackm_ukrgen_riscv64_pk_scalar3_asm, %function
bli_spackm_ukrgen_riscv64_pk_scalar3_asm:
.cfi_startproc
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
flw f0, 0(a3)
li t0,1065353216
fmv.w.x f1,t0
feq.s t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
li t1,3
remu t0,a0,t1
divu a0,a0,t1
beq a0,zero,.ukr1_done
flw f0, 0(a1)
flw f1, 4(a1)
flw f2, 8(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f3, 0(a1)
flw f4, 4(a1)
flw f5, 8(a1)
fsw f2, 8(a2)
add a1,a1,a4
add a2,a2,a5
flw f6, 0(a1)
flw f7, 4(a1)
flw f10, 8(a1)
fsw f3, 0(a2)
add a1,a1,a4
fsw f4, 4(a2)
fsw f5, 8(a2)
add a2,a2,a5
flw f0, 0(a1)
flw f1, 4(a1)
fsw f6, 0(a2)
fsw f7, 4(a2)
fsw f10, 8(a2)
flw f2, 8(a1)
add a2,a2,a5
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f3, 0(a1)
flw f4, 4(a1)
flw f5, 8(a1)
fsw f2, 8(a2)
add a1,a1,a4
add a2,a2,a5
flw f6, 0(a1)
flw f7, 4(a1)
flw f10, 8(a1)
fsw f3, 0(a2)
add a1,a1,a4
fsw f4, 4(a2)
fsw f5, 8(a2)
add a2,a2,a5
fsw f6, 0(a2)
fsw f7, 4(a2)
fsw f10, 8(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
flw f0, 0(a1)
flw f1, 4(a1)
flw f2, 8(a1)
fsw f0, 0(a2)
fsw f1, 4(a2)
fsw f2, 8(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
li t1,3
remu t0,a0,t1
divu a0,a0,t1
flw f0, 0(a3)
beq a0,zero,.ukr2_done
flw f1, 0(a1)
flw f2, 4(a1)
flw f3, 8(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.s f4,f1,f0
fmul.s f5,f2,f0
fmul.s f6,f3,f0
add a1,a1,a4
fsw f4, 0(a2)
fsw f5, 4(a2)
flw f7, 0(a1)
flw f10, 4(a1)
flw f11, 8(a1)
add a1,a1,a4
fsw f6, 8(a2)
fmul.s f12,f7,f0
fmul.s f13,f10,f0
flw f14, 0(a1)
fmul.s f15,f11,f0
flw f16, 4(a1)
flw f17, 8(a1)
add a2,a2,a5
fmul.s f28,f14,f0
fmul.s f29,f16,f0
fsw f12, 0(a2)
fmul.s f30,f17,f0
fsw f13, 4(a2)
fsw f15, 8(a2)
add a1,a1,a4
add a2,a2,a5
flw f1, 0(a1)
fsw f28, 0(a2)
fsw f29, 4(a2)
fsw f30, 8(a2)
flw f2, 4(a1)
add a2,a2,a5
flw f3, 8(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.s f4,f1,f0
fmul.s f5,f2,f0
flw f7, 0(a1)
fmul.s f6,f3,f0
flw f10, 4(a1)
flw f11, 8(a1)
add a1,a1,a4
fsw f4, 0(a2)
fmul.s f12,f7,f0
fsw f5, 4(a2)
fmul.s f13,f10,f0
flw f14, 0(a1)
fmul.s f15,f11,f0
flw f16, 4(a1)
flw f17, 8(a1)
fsw f6, 8(a2)
fmul.s f28,f14,f0
add a2,a2,a5
fmul.s f29,f16,f0
fmul.s f30,f17,f0
fsw f12, 0(a2)
fsw f13, 4(a2)
add a1,a1,a4
fsw f15, 8(a2)
add a2,a2,a5
fsw f28, 0(a2)
fsw f29, 4(a2)
fsw f30, 8(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
flw f1, 0(a1)
flw f2, 4(a1)
flw f3, 8(a1)
fmul.s f4,f1,f0
fmul.s f5,f2,f0
fmul.s f6,f3,f0
fsw f4, 0(a2)
fsw f5, 4(a2)
fsw f6, 8(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr2_tail
.ukr2_taildone:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_spackm_ukrgen_riscv64_pk_scalar3_asm, .-bli_spackm_ukrgen_riscv64_pk_scalar3_asm
.section .note.GNU-stack,"",%progbits


### bli_spackm_ukrgen_riscv64_pk_scalar4
.text
.global bli_spackm_ukrgen_riscv64_pk_scalar4_asm
.type bli_spackm_ukrgen_riscv64_pk_scalar4_asm, %function
bli_spackm_ukrgen_riscv64_pk_scalar4_asm:
.cfi_startproc
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
flw f0, 0(a3)
li t0,1065353216
fmv.w.x f1,t0
feq.s t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,1
srli a0,a0,1
beq a0,zero,.ukr1_done
flw f0, 0(a1)
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f4, 0(a1)
flw f5, 4(a1)
flw f6, 8(a1)
flw f7, 12(a1)
fsw f2, 8(a2)
add a1,a1,a4
fsw f3, 12(a2)
add a2,a2,a5
flw f0, 0(a1)
flw f1, 4(a1)
fsw f4, 0(a2)
fsw f5, 4(a2)
fsw f6, 8(a2)
fsw f7, 12(a2)
flw f2, 8(a1)
add a2,a2,a5
flw f3, 12(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f4, 0(a1)
flw f5, 4(a1)
flw f6, 8(a1)
flw f7, 12(a1)
fsw f2, 8(a2)
add a1,a1,a4
fsw f3, 12(a2)
add a2,a2,a5
fsw f4, 0(a2)
fsw f5, 4(a2)
fsw f6, 8(a2)
fsw f7, 12(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
flw f0, 0(a1)
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
fsw f0, 0(a2)
fsw f1, 4(a2)
fsw f2, 8(a2)
fsw f3, 12(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,1
srli a0,a0,1
flw f0, 0(a3)
beq a0,zero,.ukr2_done
flw f1, 0(a1)
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.s f5,f1,f0
fmul.s f6,f2,f0
fmul.s f7,f3,f0
fmul.s f10,f4,f0
fsw f5, 0(a2)
add a1,a1,a4
fsw f6, 4(a2)
fsw f7, 8(a2)
flw f11, 0(a1)
flw f12, 4(a1)
flw f13, 8(a1)
flw f14, 12(a1)
fmul.s f15,f11,f0
fmul.s f16,f12,f0
fsw f10, 12(a2)
fmul.s f17,f13,f0
fmul.s f28,f14,f0
add a2,a2,a5
add a1,a1,a4
fsw f15, 0(a2)
fsw f16, 4(a2)
fsw f17, 8(a2)
fsw f28, 12(a2)
flw f1, 0(a1)
add a2,a2,a5
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.s f5,f1,f0
fmul.s f6,f2,f0
flw f11, 0(a1)
fmul.s f7,f3,f0
flw f12, 4(a1)
fmul.s f10,f4,f0
flw f13, 8(a1)
flw f14, 12(a1)
fmul.s f15,f11,f0
fmul.s f16,f12,f0
fsw f5, 0(a2)
fmul.s f17,f13,f0
fsw f6, 4(a2)
fmul.s f28,f14,f0
fsw f7, 8(a2)
fsw f10, 12(a2)
add a1,a1,a4
add a2,a2,a5
fsw f15, 0(a2)
fsw f16, 4(a2)
fsw f17, 8(a2)
fsw f28, 12(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
flw f1, 0(a1)
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
fmul.s f5,f1,f0
fmul.s f6,f2,f0
fmul.s f7,f3,f0
fmul.s f10,f4,f0
fsw f5, 0(a2)
fsw f6, 4(a2)
fsw f7, 8(a2)
fsw f10, 12(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr2_tail
.ukr2_taildone:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_spackm_ukrgen_riscv64_pk_scalar4_asm, .-bli_spackm_ukrgen_riscv64_pk_scalar4_asm
.section .note.GNU-stack,"",%progbits


### bli_spackm_ukrgen_riscv64_pk_scalar5
.text
.global bli_spackm_ukrgen_riscv64_pk_scalar5_asm
.type bli_spackm_ukrgen_riscv64_pk_scalar5_asm, %function
bli_spackm_ukrgen_riscv64_pk_scalar5_asm:
.cfi_startproc
add sp,sp,-16
.cfi_adjust_cfa_offset 16
fsd f8, 0(sp)
.cfi_rel_offset f8, 0
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
flw f0, 0(a3)
li t0,1065353216
fmv.w.x f1,t0
feq.s t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,1
srli a0,a0,1
beq a0,zero,.ukr1_done
flw f0, 0(a1)
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
flw f4, 16(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f5, 0(a1)
flw f6, 4(a1)
flw f7, 8(a1)
flw f10, 12(a1)
flw f11, 16(a1)
fsw f2, 8(a2)
add a1,a1,a4
fsw f3, 12(a2)
fsw f4, 16(a2)
add a2,a2,a5
flw f0, 0(a1)
flw f1, 4(a1)
fsw f5, 0(a2)
fsw f6, 4(a2)
fsw f7, 8(a2)
fsw f10, 12(a2)
fsw f11, 16(a2)
flw f2, 8(a1)
add a2,a2,a5
flw f3, 12(a1)
flw f4, 16(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f5, 0(a1)
flw f6, 4(a1)
flw f7, 8(a1)
flw f10, 12(a1)
flw f11, 16(a1)
fsw f2, 8(a2)
add a1,a1,a4
fsw f3, 12(a2)
fsw f4, 16(a2)
add a2,a2,a5
fsw f5, 0(a2)
fsw f6, 4(a2)
fsw f7, 8(a2)
fsw f10, 12(a2)
fsw f11, 16(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
flw f0, 0(a1)
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
flw f4, 16(a1)
fsw f0, 0(a2)
fsw f1, 4(a2)
fsw f2, 8(a2)
fsw f3, 12(a2)
fsw f4, 16(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,1
srli a0,a0,1
flw f0, 0(a3)
beq a0,zero,.ukr2_done
flw f1, 0(a1)
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
flw f5, 16(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.s f6,f1,f0
fmul.s f7,f2,f0
fmul.s f10,f3,f0
fmul.s f11,f4,f0
fsw f6, 0(a2)
fmul.s f12,f5,f0
fsw f7, 4(a2)
add a1,a1,a4
fsw f10, 8(a2)
fsw f11, 12(a2)
flw f13, 0(a1)
flw f14, 4(a1)
flw f15, 8(a1)
flw f16, 12(a1)
fmul.s f17,f13,f0
flw f28, 16(a1)
fmul.s f29,f14,f0
fmul.s f30,f15,f0
fsw f12, 16(a2)
fmul.s f31,f16,f0
fmul.s f8,f28,f0
add a2,a2,a5
add a1,a1,a4
fsw f17, 0(a2)
fsw f29, 4(a2)
fsw f30, 8(a2)
fsw f31, 12(a2)
fsw f8, 16(a2)
flw f1, 0(a1)
add a2,a2,a5
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
flw f5, 16(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.s f6,f1,f0
fmul.s f7,f2,f0
flw f13, 0(a1)
fmul.s f10,f3,f0
flw f14, 4(a1)
fmul.s f11,f4,f0
flw f15, 8(a1)
fmul.s f12,f5,f0
flw f16, 12(a1)
flw f28, 16(a1)
fmul.s f17,f13,f0
fmul.s f29,f14,f0
fsw f6, 0(a2)
fmul.s f30,f15,f0
fsw f7, 4(a2)
fmul.s f31,f16,f0
fsw f10, 8(a2)
fmul.s f8,f28,f0
fsw f11, 12(a2)
fsw f12, 16(a2)
add a1,a1,a4
add a2,a2,a5
fsw f17, 0(a2)
fsw f29, 4(a2)
fsw f30, 8(a2)
fsw f31, 12(a2)
fsw f8, 16(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
flw f1, 0(a1)
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
fmul.s f6,f1,f0
flw f5, 16(a1)
fmul.s f7,f2,f0
fmul.s f10,f3,f0
fmul.s f11,f4,f0
fsw f6, 0(a2)
fmul.s f12,f5,f0
fsw f7, 4(a2)
fsw f10, 8(a2)
fsw f11, 12(a2)
fsw f12, 16(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr2_tail
.ukr2_taildone:
.ukr0_cases_end:
fld f8, 0(sp)
.cfi_restore f8
add sp,sp,16
.cfi_adjust_cfa_offset -16
ret
.cfi_endproc
.size bli_spackm_ukrgen_riscv64_pk_scalar5_asm, .-bli_spackm_ukrgen_riscv64_pk_scalar5_asm
.section .note.GNU-stack,"",%progbits


### bli_spackm_ukrgen_riscv64_pk_scalar6
.text
.global bli_spackm_ukrgen_riscv64_pk_scalar6_asm
.type bli_spackm_ukrgen_riscv64_pk_scalar6_asm, %function
bli_spackm_ukrgen_riscv64_pk_scalar6_asm:
.cfi_startproc
add sp,sp,-48
.cfi_adjust_cfa_offset 48
fsd f8, 0(sp)
.cfi_rel_offset f8, 0
fsd f9, 8(sp)
.cfi_rel_offset f9, 8
fsd f18, 16(sp)
.cfi_rel_offset f18, 16
fsd f19, 24(sp)
.cfi_rel_offset f19, 24
fsd f20, 32(sp)
.cfi_rel_offset f20, 32
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
flw f0, 0(a3)
li t0,1065353216
fmv.w.x f1,t0
feq.s t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,1
srli a0,a0,1
beq a0,zero,.ukr1_done
flw f0, 0(a1)
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
flw f4, 16(a1)
flw f5, 20(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f6, 0(a1)
flw f7, 4(a1)
flw f10, 8(a1)
flw f11, 12(a1)
flw f12, 16(a1)
flw f13, 20(a1)
fsw f2, 8(a2)
add a1,a1,a4
fsw f3, 12(a2)
fsw f4, 16(a2)
fsw f5, 20(a2)
add a2,a2,a5
flw f0, 0(a1)
flw f1, 4(a1)
fsw f6, 0(a2)
fsw f7, 4(a2)
fsw f10, 8(a2)
fsw f11, 12(a2)
fsw f12, 16(a2)
fsw f13, 20(a2)
flw f2, 8(a1)
add a2,a2,a5
flw f3, 12(a1)
flw f4, 16(a1)
flw f5, 20(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f6, 0(a1)
flw f7, 4(a1)
flw f10, 8(a1)
flw f11, 12(a1)
flw f12, 16(a1)
flw f13, 20(a1)
fsw f2, 8(a2)
add a1,a1,a4
fsw f3, 12(a2)
fsw f4, 16(a2)
fsw f5, 20(a2)
add a2,a2,a5
fsw f6, 0(a2)
fsw f7, 4(a2)
fsw f10, 8(a2)
fsw f11, 12(a2)
fsw f12, 16(a2)
fsw f13, 20(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
flw f0, 0(a1)
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
flw f4, 16(a1)
flw f5, 20(a1)
fsw f0, 0(a2)
fsw f1, 4(a2)
fsw f2, 8(a2)
fsw f3, 12(a2)
fsw f4, 16(a2)
fsw f5, 20(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,1
srli a0,a0,1
flw f0, 0(a3)
beq a0,zero,.ukr2_done
flw f1, 0(a1)
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
flw f5, 16(a1)
flw f6, 20(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.s f7,f1,f0
fmul.s f10,f2,f0
fmul.s f11,f3,f0
fmul.s f12,f4,f0
fsw f7, 0(a2)
fmul.s f13,f5,f0
fsw f10, 4(a2)
fmul.s f14,f6,f0
fsw f11, 8(a2)
add a1,a1,a4
fsw f12, 12(a2)
fsw f13, 16(a2)
flw f15, 0(a1)
flw f16, 4(a1)
flw f17, 8(a1)
flw f28, 12(a1)
fmul.s f29,f15,f0
flw f30, 16(a1)
fmul.s f31,f16,f0
flw f8, 20(a1)
fmul.s f9,f17,f0
fmul.s f18,f28,f0
fsw f14, 20(a2)
fmul.s f19,f30,f0
fmul.s f20,f8,f0
add a2,a2,a5
add a1,a1,a4
fsw f29, 0(a2)
fsw f31, 4(a2)
fsw f9, 8(a2)
fsw f18, 12(a2)
fsw f19, 16(a2)
fsw f20, 20(a2)
flw f1, 0(a1)
add a2,a2,a5
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
flw f5, 16(a1)
flw f6, 20(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.s f7,f1,f0
fmul.s f10,f2,f0
flw f15, 0(a1)
fmul.s f11,f3,f0
flw f16, 4(a1)
fmul.s f12,f4,f0
flw f17, 8(a1)
fmul.s f13,f5,f0
flw f28, 12(a1)
fmul.s f14,f6,f0
flw f30, 16(a1)
flw f8, 20(a1)
fmul.s f29,f15,f0
fmul.s f31,f16,f0
fsw f7, 0(a2)
fmul.s f9,f17,f0
fsw f10, 4(a2)
fmul.s f18,f28,f0
fsw f11, 8(a2)
fmul.s f19,f30,f0
fsw f12, 12(a2)
fmul.s f20,f8,f0
fsw f13, 16(a2)
fsw f14, 20(a2)
add a1,a1,a4
add a2,a2,a5
fsw f29, 0(a2)
fsw f31, 4(a2)
fsw f9, 8(a2)
fsw f18, 12(a2)
fsw f19, 16(a2)
fsw f20, 20(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
flw f1, 0(a1)
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
fmul.s f7,f1,f0
flw f5, 16(a1)
fmul.s f10,f2,f0
flw f6, 20(a1)
fmul.s f11,f3,f0
fmul.s f12,f4,f0
fsw f7, 0(a2)
fmul.s f13,f5,f0
fsw f10, 4(a2)
fmul.s f14,f6,f0
fsw f11, 8(a2)
fsw f12, 12(a2)
fsw f13, 16(a2)
fsw f14, 20(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr2_tail
.ukr2_taildone:
.ukr0_cases_end:
fld f8, 0(sp)
.cfi_restore f8
fld f9, 8(sp)
.cfi_restore f9
fld f18, 16(sp)
.cfi_restore f18
fld f19, 24(sp)
.cfi_restore f19
fld f20, 32(sp)
.cfi_restore f20
add sp,sp,48
.cfi_adjust_cfa_offset -48
ret
.cfi_endproc
.size bli_spackm_ukrgen_riscv64_pk_scalar6_asm, .-bli_spackm_ukrgen_riscv64_pk_scalar6_asm
.section .note.GNU-stack,"",%progbits


### bli_spackm_ukrgen_riscv64_pk_scalar7
.text
.global bli_spackm_ukrgen_riscv64_pk_scalar7_asm
.type bli_spackm_ukrgen_riscv64_pk_scalar7_asm, %function
bli_spackm_ukrgen_riscv64_pk_scalar7_asm:
.cfi_startproc
add sp,sp,-80
.cfi_adjust_cfa_offset 80
fsd f8, 0(sp)
.cfi_rel_offset f8, 0
fsd f9, 8(sp)
.cfi_rel_offset f9, 8
fsd f18, 16(sp)
.cfi_rel_offset f18, 16
fsd f19, 24(sp)
.cfi_rel_offset f19, 24
fsd f20, 32(sp)
.cfi_rel_offset f20, 32
fsd f21, 40(sp)
.cfi_rel_offset f21, 40
fsd f22, 48(sp)
.cfi_rel_offset f22, 48
fsd f23, 56(sp)
.cfi_rel_offset f23, 56
fsd f24, 64(sp)
.cfi_rel_offset f24, 64
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
flw f0, 0(a3)
li t0,1065353216
fmv.w.x f1,t0
feq.s t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,1
srli a0,a0,1
beq a0,zero,.ukr1_done
flw f0, 0(a1)
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
flw f4, 16(a1)
flw f5, 20(a1)
flw f6, 24(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f7, 0(a1)
flw f10, 4(a1)
flw f11, 8(a1)
flw f12, 12(a1)
flw f13, 16(a1)
flw f14, 20(a1)
flw f15, 24(a1)
fsw f2, 8(a2)
add a1,a1,a4
fsw f3, 12(a2)
fsw f4, 16(a2)
fsw f5, 20(a2)
fsw f6, 24(a2)
add a2,a2,a5
flw f0, 0(a1)
flw f1, 4(a1)
fsw f7, 0(a2)
fsw f10, 4(a2)
fsw f11, 8(a2)
fsw f12, 12(a2)
fsw f13, 16(a2)
fsw f14, 20(a2)
fsw f15, 24(a2)
flw f2, 8(a1)
add a2,a2,a5
flw f3, 12(a1)
flw f4, 16(a1)
flw f5, 20(a1)
flw f6, 24(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
flw f7, 0(a1)
flw f10, 4(a1)
flw f11, 8(a1)
flw f12, 12(a1)
flw f13, 16(a1)
flw f14, 20(a1)
flw f15, 24(a1)
fsw f2, 8(a2)
add a1,a1,a4
fsw f3, 12(a2)
fsw f4, 16(a2)
fsw f5, 20(a2)
fsw f6, 24(a2)
add a2,a2,a5
fsw f7, 0(a2)
fsw f10, 4(a2)
fsw f11, 8(a2)
fsw f12, 12(a2)
fsw f13, 16(a2)
fsw f14, 20(a2)
fsw f15, 24(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
flw f0, 0(a1)
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
flw f4, 16(a1)
flw f5, 20(a1)
flw f6, 24(a1)
fsw f0, 0(a2)
fsw f1, 4(a2)
fsw f2, 8(a2)
fsw f3, 12(a2)
fsw f4, 16(a2)
fsw f5, 20(a2)
fsw f6, 24(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,1
srli a0,a0,1
flw f0, 0(a3)
beq a0,zero,.ukr2_done
flw f1, 0(a1)
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
flw f5, 16(a1)
flw f6, 20(a1)
flw f7, 24(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.s f10,f1,f0
fmul.s f11,f2,f0
fmul.s f12,f3,f0
fmul.s f13,f4,f0
fsw f10, 0(a2)
fmul.s f14,f5,f0
fsw f11, 4(a2)
fmul.s f15,f6,f0
fsw f12, 8(a2)
fmul.s f16,f7,f0
fsw f13, 12(a2)
add a1,a1,a4
fsw f14, 16(a2)
fsw f15, 20(a2)
flw f17, 0(a1)
flw f28, 4(a1)
flw f29, 8(a1)
flw f30, 12(a1)
fmul.s f31,f17,f0
flw f8, 16(a1)
fmul.s f9,f28,f0
flw f18, 20(a1)
fmul.s f19,f29,f0
flw f20, 24(a1)
fmul.s f21,f30,f0
fmul.s f22,f8,f0
fsw f16, 24(a2)
fmul.s f23,f18,f0
fmul.s f24,f20,f0
add a2,a2,a5
add a1,a1,a4
fsw f31, 0(a2)
fsw f9, 4(a2)
fsw f19, 8(a2)
fsw f21, 12(a2)
fsw f22, 16(a2)
fsw f23, 20(a2)
fsw f24, 24(a2)
flw f1, 0(a1)
add a2,a2,a5
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
flw f5, 16(a1)
flw f6, 20(a1)
flw f7, 24(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.s f10,f1,f0
fmul.s f11,f2,f0
flw f17, 0(a1)
fmul.s f12,f3,f0
flw f28, 4(a1)
fmul.s f13,f4,f0
flw f29, 8(a1)
fmul.s f14,f5,f0
flw f30, 12(a1)
fmul.s f15,f6,f0
flw f8, 16(a1)
fmul.s f16,f7,f0
flw f18, 20(a1)
flw f20, 24(a1)
fmul.s f31,f17,f0
fmul.s f9,f28,f0
fsw f10, 0(a2)
fmul.s f19,f29,f0
fsw f11, 4(a2)
fmul.s f21,f30,f0
fsw f12, 8(a2)
fmul.s f22,f8,f0
fsw f13, 12(a2)
fmul.s f23,f18,f0
fsw f14, 16(a2)
fmul.s f24,f20,f0
fsw f15, 20(a2)
fsw f16, 24(a2)
add a1,a1,a4
add a2,a2,a5
fsw f31, 0(a2)
fsw f9, 4(a2)
fsw f19, 8(a2)
fsw f21, 12(a2)
fsw f22, 16(a2)
fsw f23, 20(a2)
fsw f24, 24(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
flw f1, 0(a1)
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
fmul.s f10,f1,f0
flw f5, 16(a1)
fmul.s f11,f2,f0
flw f6, 20(a1)
fmul.s f12,f3,f0
flw f7, 24(a1)
fmul.s f13,f4,f0
fmul.s f14,f5,f0
fsw f10, 0(a2)
fmul.s f15,f6,f0
fsw f11, 4(a2)
fmul.s f16,f7,f0
fsw f12, 8(a2)
fsw f13, 12(a2)
fsw f14, 16(a2)
fsw f15, 20(a2)
fsw f16, 24(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr2_tail
.ukr2_taildone:
.ukr0_cases_end:
fld f8, 0(sp)
.cfi_restore f8
fld f9, 8(sp)
.cfi_restore f9
fld f18, 16(sp)
.cfi_restore f18
fld f19, 24(sp)
.cfi_restore f19
fld f20, 32(sp)
.cfi_restore f20
fld f21, 40(sp)
.cfi_restore f21
fld f22, 48(sp)
.cfi_restore f22
fld f23, 56(sp)
.cfi_restore f23
fld f24, 64(sp)
.cfi_restore f24
add sp,sp,80
.cfi_adjust_cfa_offset -80
ret
.cfi_endproc
.size bli_spackm_ukrgen_riscv64_pk_scalar7_asm, .-bli_spackm_ukrgen_riscv64_pk_scalar7_asm
.section .note.GNU-stack,"",%progbits


### bli_spackm_ukrgen_riscv64_pk_scalar8
.text
.global bli_spackm_ukrgen_riscv64_pk_scalar8_asm
.type bli_spackm_ukrgen_riscv64_pk_scalar8_asm, %function
bli_spackm_ukrgen_riscv64_pk_scalar8_asm:
.cfi_startproc
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
flw f0, 0(a3)
li t0,1065353216
fmv.w.x f1,t0
feq.s t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
beq a0,zero,.ukr1_done
flw f0, 0(a1)
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
flw f4, 16(a1)
flw f5, 20(a1)
flw f6, 24(a1)
flw f7, 28(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsw f0, 0(a2)
fsw f1, 4(a2)
fsw f2, 8(a2)
fsw f3, 12(a2)
fsw f4, 16(a2)
fsw f5, 20(a2)
fsw f6, 24(a2)
fsw f7, 28(a2)
flw f0, 0(a1)
add a2,a2,a5
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
flw f4, 16(a1)
flw f5, 20(a1)
flw f6, 24(a1)
flw f7, 28(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
fsw f0, 0(a2)
fsw f1, 4(a2)
fsw f2, 8(a2)
fsw f3, 12(a2)
fsw f4, 16(a2)
fsw f5, 20(a2)
fsw f6, 24(a2)
fsw f7, 28(a2)
.ukr1_done:
j .ukr0_cases_end
.ukr0_case1:
flw f0, 0(a3)
beq a0,zero,.ukr2_done
flw f1, 0(a1)
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
flw f5, 16(a1)
flw f6, 20(a1)
flw f7, 24(a1)
flw f10, 28(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.s f11,f1,f0
fmul.s f12,f2,f0
fmul.s f13,f3,f0
fmul.s f14,f4,f0
fsw f11, 0(a2)
fmul.s f15,f5,f0
fsw f12, 4(a2)
fmul.s f16,f6,f0
fsw f13, 8(a2)
fmul.s f17,f7,f0
fsw f14, 12(a2)
fmul.s f28,f10,f0
fsw f15, 16(a2)
add a1,a1,a4
fsw f16, 20(a2)
fsw f17, 24(a2)
fsw f28, 28(a2)
flw f1, 0(a1)
add a2,a2,a5
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
flw f5, 16(a1)
flw f6, 20(a1)
flw f7, 24(a1)
flw f10, 28(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
fmul.s f11,f1,f0
fmul.s f12,f2,f0
fmul.s f13,f3,f0
fmul.s f14,f4,f0
fsw f11, 0(a2)
fmul.s f15,f5,f0
fsw f12, 4(a2)
fmul.s f16,f6,f0
fsw f13, 8(a2)
fmul.s f17,f7,f0
fsw f14, 12(a2)
fmul.s f28,f10,f0
fsw f15, 16(a2)
fsw f16, 20(a2)
fsw f17, 24(a2)
fsw f28, 28(a2)
.ukr2_done:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_spackm_ukrgen_riscv64_pk_scalar8_asm, .-bli_spackm_ukrgen_riscv64_pk_scalar8_asm
.section .note.GNU-stack,"",%progbits
