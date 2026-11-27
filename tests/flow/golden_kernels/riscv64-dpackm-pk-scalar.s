### bli_dpackm_ukrgen_riscv64_pk_scalar1
.text
.global bli_dpackm_ukrgen_riscv64_pk_scalar1_asm
.type bli_dpackm_ukrgen_riscv64_pk_scalar1_asm, %function
bli_dpackm_ukrgen_riscv64_pk_scalar1_asm:
.cfi_startproc
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
fld f0, 0(a3)
li t0,4607182418800017408
fmv.d.x f1,t0
feq.d t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,7
srli a0,a0,3
beq a0,zero,.ukr1_done
fld f0, 0(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsd f0, 0(a2)
add a2,a2,a5
fld f1, 0(a1)
add a1,a1,a4
fld f2, 0(a1)
fsd f1, 0(a2)
add a1,a1,a4
add a2,a2,a5
fld f3, 0(a1)
fsd f2, 0(a2)
add a1,a1,a4
add a2,a2,a5
fld f4, 0(a1)
fsd f3, 0(a2)
add a1,a1,a4
add a2,a2,a5
fld f5, 0(a1)
fsd f4, 0(a2)
add a1,a1,a4
add a2,a2,a5
fld f6, 0(a1)
fsd f5, 0(a2)
add a1,a1,a4
add a2,a2,a5
fld f7, 0(a1)
fsd f6, 0(a2)
add a1,a1,a4
add a2,a2,a5
fld f0, 0(a1)
fsd f7, 0(a2)
add a2,a2,a5
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsd f0, 0(a2)
add a2,a2,a5
fld f1, 0(a1)
add a1,a1,a4
fld f2, 0(a1)
fsd f1, 0(a2)
add a1,a1,a4
add a2,a2,a5
fld f3, 0(a1)
fsd f2, 0(a2)
add a1,a1,a4
add a2,a2,a5
fld f4, 0(a1)
fsd f3, 0(a2)
add a1,a1,a4
add a2,a2,a5
fld f5, 0(a1)
fsd f4, 0(a2)
add a1,a1,a4
add a2,a2,a5
fld f6, 0(a1)
fsd f5, 0(a2)
add a1,a1,a4
add a2,a2,a5
fld f7, 0(a1)
fsd f6, 0(a2)
add a1,a1,a4
add a2,a2,a5
fsd f7, 0(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
fld f0, 0(a1)
fsd f0, 0(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,7
srli a0,a0,3
fld f0, 0(a3)
beq a0,zero,.ukr2_done
fld f1, 0(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
add a1,a1,a4
fmul.d f2,f1,f0
fld f3, 0(a1)
add a1,a1,a4
fsd f2, 0(a2)
fmul.d f4,f3,f0
fld f5, 0(a1)
add a1,a1,a4
add a2,a2,a5
fmul.d f6,f5,f0
fld f7, 0(a1)
fsd f4, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f10,f7,f0
fld f11, 0(a1)
fsd f6, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f12,f11,f0
fld f13, 0(a1)
fsd f10, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f14,f13,f0
fld f15, 0(a1)
fsd f12, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f16,f15,f0
fld f17, 0(a1)
fsd f14, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f28,f17,f0
fld f1, 0(a1)
fsd f16, 0(a2)
add a2,a2,a5
fsd f28, 0(a2)
add a2,a2,a5
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.d f2,f1,f0
fld f3, 0(a1)
add a1,a1,a4
fsd f2, 0(a2)
fmul.d f4,f3,f0
fld f5, 0(a1)
add a1,a1,a4
add a2,a2,a5
fmul.d f6,f5,f0
fld f7, 0(a1)
fsd f4, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f10,f7,f0
fld f11, 0(a1)
fsd f6, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f12,f11,f0
fld f13, 0(a1)
fsd f10, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f14,f13,f0
fld f15, 0(a1)
fsd f12, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f16,f15,f0
fld f17, 0(a1)
fsd f14, 0(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f28,f17,f0
fsd f16, 0(a2)
add a2,a2,a5
fsd f28, 0(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
fld f1, 0(a1)
fmul.d f2,f1,f0
fsd f2, 0(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr2_tail
.ukr2_taildone:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dpackm_ukrgen_riscv64_pk_scalar1_asm, .-bli_dpackm_ukrgen_riscv64_pk_scalar1_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_riscv64_pk_scalar2
.text
.global bli_dpackm_ukrgen_riscv64_pk_scalar2_asm
.type bli_dpackm_ukrgen_riscv64_pk_scalar2_asm, %function
bli_dpackm_ukrgen_riscv64_pk_scalar2_asm:
.cfi_startproc
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
fld f0, 0(a3)
li t0,4607182418800017408
fmv.d.x f1,t0
feq.d t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,3
srli a0,a0,2
beq a0,zero,.ukr1_done
fld f0, 0(a1)
fld f1, 8(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f2, 0(a1)
add a2,a2,a5
fld f3, 8(a1)
add a1,a1,a4
fsd f2, 0(a2)
fld f4, 0(a1)
fld f5, 8(a1)
fsd f3, 8(a2)
add a1,a1,a4
add a2,a2,a5
fld f6, 0(a1)
fld f7, 8(a1)
fsd f4, 0(a2)
add a1,a1,a4
fsd f5, 8(a2)
add a2,a2,a5
fld f0, 0(a1)
fld f1, 8(a1)
fsd f6, 0(a2)
fsd f7, 8(a2)
add a2,a2,a5
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f2, 0(a1)
add a2,a2,a5
fld f3, 8(a1)
add a1,a1,a4
fsd f2, 0(a2)
fld f4, 0(a1)
fld f5, 8(a1)
fsd f3, 8(a2)
add a1,a1,a4
add a2,a2,a5
fld f6, 0(a1)
fld f7, 8(a1)
fsd f4, 0(a2)
add a1,a1,a4
fsd f5, 8(a2)
add a2,a2,a5
fsd f6, 0(a2)
fsd f7, 8(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
fld f0, 0(a1)
fld f1, 8(a1)
fsd f0, 0(a2)
fsd f1, 8(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,3
srli a0,a0,2
fld f0, 0(a3)
beq a0,zero,.ukr2_done
fld f1, 0(a1)
fld f2, 8(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
add a1,a1,a4
fmul.d f3,f1,f0
fmul.d f4,f2,f0
fld f5, 0(a1)
fld f6, 8(a1)
add a1,a1,a4
fsd f3, 0(a2)
fmul.d f7,f5,f0
fsd f4, 8(a2)
fmul.d f10,f6,f0
fld f11, 0(a1)
fld f12, 8(a1)
add a2,a2,a5
add a1,a1,a4
fmul.d f13,f11,f0
fsd f7, 0(a2)
fmul.d f14,f12,f0
fld f15, 0(a1)
fld f16, 8(a1)
fsd f10, 8(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f17,f15,f0
fld f1, 0(a1)
fmul.d f28,f16,f0
fsd f13, 0(a2)
fsd f14, 8(a2)
add a2,a2,a5
fld f2, 8(a1)
fsd f17, 0(a2)
fsd f28, 8(a2)
add a2,a2,a5
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.d f3,f1,f0
fmul.d f4,f2,f0
fld f5, 0(a1)
fld f6, 8(a1)
add a1,a1,a4
fsd f3, 0(a2)
fmul.d f7,f5,f0
fsd f4, 8(a2)
fmul.d f10,f6,f0
fld f11, 0(a1)
fld f12, 8(a1)
add a2,a2,a5
add a1,a1,a4
fmul.d f13,f11,f0
fsd f7, 0(a2)
fmul.d f14,f12,f0
fld f15, 0(a1)
fld f16, 8(a1)
fsd f10, 8(a2)
add a1,a1,a4
add a2,a2,a5
fmul.d f17,f15,f0
fmul.d f28,f16,f0
fsd f13, 0(a2)
fsd f14, 8(a2)
add a2,a2,a5
fsd f17, 0(a2)
fsd f28, 8(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
fld f1, 0(a1)
fld f2, 8(a1)
fmul.d f3,f1,f0
fmul.d f4,f2,f0
fsd f3, 0(a2)
fsd f4, 8(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr2_tail
.ukr2_taildone:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dpackm_ukrgen_riscv64_pk_scalar2_asm, .-bli_dpackm_ukrgen_riscv64_pk_scalar2_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_riscv64_pk_scalar3
.text
.global bli_dpackm_ukrgen_riscv64_pk_scalar3_asm
.type bli_dpackm_ukrgen_riscv64_pk_scalar3_asm, %function
bli_dpackm_ukrgen_riscv64_pk_scalar3_asm:
.cfi_startproc
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
fld f0, 0(a3)
li t0,4607182418800017408
fmv.d.x f1,t0
feq.d t0,f0,f1
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
fld f0, 0(a1)
fld f1, 8(a1)
fld f2, 16(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f3, 0(a1)
fld f4, 8(a1)
fld f5, 16(a1)
fsd f2, 16(a2)
add a1,a1,a4
add a2,a2,a5
fld f6, 0(a1)
fld f7, 8(a1)
fld f10, 16(a1)
fsd f3, 0(a2)
add a1,a1,a4
fsd f4, 8(a2)
fsd f5, 16(a2)
add a2,a2,a5
fld f0, 0(a1)
fld f1, 8(a1)
fsd f6, 0(a2)
fsd f7, 8(a2)
fsd f10, 16(a2)
fld f2, 16(a1)
add a2,a2,a5
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f3, 0(a1)
fld f4, 8(a1)
fld f5, 16(a1)
fsd f2, 16(a2)
add a1,a1,a4
add a2,a2,a5
fld f6, 0(a1)
fld f7, 8(a1)
fld f10, 16(a1)
fsd f3, 0(a2)
add a1,a1,a4
fsd f4, 8(a2)
fsd f5, 16(a2)
add a2,a2,a5
fsd f6, 0(a2)
fsd f7, 8(a2)
fsd f10, 16(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
fld f0, 0(a1)
fld f1, 8(a1)
fld f2, 16(a1)
fsd f0, 0(a2)
fsd f1, 8(a2)
fsd f2, 16(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
li t1,3
remu t0,a0,t1
divu a0,a0,t1
fld f0, 0(a3)
beq a0,zero,.ukr2_done
fld f1, 0(a1)
fld f2, 8(a1)
fld f3, 16(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.d f4,f1,f0
fmul.d f5,f2,f0
fmul.d f6,f3,f0
add a1,a1,a4
fsd f4, 0(a2)
fsd f5, 8(a2)
fld f7, 0(a1)
fld f10, 8(a1)
fld f11, 16(a1)
add a1,a1,a4
fsd f6, 16(a2)
fmul.d f12,f7,f0
fmul.d f13,f10,f0
fld f14, 0(a1)
fmul.d f15,f11,f0
fld f16, 8(a1)
fld f17, 16(a1)
add a2,a2,a5
fmul.d f28,f14,f0
fmul.d f29,f16,f0
fsd f12, 0(a2)
fmul.d f30,f17,f0
fsd f13, 8(a2)
fsd f15, 16(a2)
add a1,a1,a4
add a2,a2,a5
fld f1, 0(a1)
fsd f28, 0(a2)
fsd f29, 8(a2)
fsd f30, 16(a2)
fld f2, 8(a1)
add a2,a2,a5
fld f3, 16(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.d f4,f1,f0
fmul.d f5,f2,f0
fld f7, 0(a1)
fmul.d f6,f3,f0
fld f10, 8(a1)
fld f11, 16(a1)
add a1,a1,a4
fsd f4, 0(a2)
fmul.d f12,f7,f0
fsd f5, 8(a2)
fmul.d f13,f10,f0
fld f14, 0(a1)
fmul.d f15,f11,f0
fld f16, 8(a1)
fld f17, 16(a1)
fsd f6, 16(a2)
fmul.d f28,f14,f0
add a2,a2,a5
fmul.d f29,f16,f0
fmul.d f30,f17,f0
fsd f12, 0(a2)
fsd f13, 8(a2)
add a1,a1,a4
fsd f15, 16(a2)
add a2,a2,a5
fsd f28, 0(a2)
fsd f29, 8(a2)
fsd f30, 16(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
fld f1, 0(a1)
fld f2, 8(a1)
fld f3, 16(a1)
fmul.d f4,f1,f0
fmul.d f5,f2,f0
fmul.d f6,f3,f0
fsd f4, 0(a2)
fsd f5, 8(a2)
fsd f6, 16(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr2_tail
.ukr2_taildone:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dpackm_ukrgen_riscv64_pk_scalar3_asm, .-bli_dpackm_ukrgen_riscv64_pk_scalar3_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_riscv64_pk_scalar4
.text
.global bli_dpackm_ukrgen_riscv64_pk_scalar4_asm
.type bli_dpackm_ukrgen_riscv64_pk_scalar4_asm, %function
bli_dpackm_ukrgen_riscv64_pk_scalar4_asm:
.cfi_startproc
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
fld f0, 0(a3)
li t0,4607182418800017408
fmv.d.x f1,t0
feq.d t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,1
srli a0,a0,1
beq a0,zero,.ukr1_done
fld f0, 0(a1)
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f4, 0(a1)
fld f5, 8(a1)
fld f6, 16(a1)
fld f7, 24(a1)
fsd f2, 16(a2)
add a1,a1,a4
fsd f3, 24(a2)
add a2,a2,a5
fld f0, 0(a1)
fld f1, 8(a1)
fsd f4, 0(a2)
fsd f5, 8(a2)
fsd f6, 16(a2)
fsd f7, 24(a2)
fld f2, 16(a1)
add a2,a2,a5
fld f3, 24(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f4, 0(a1)
fld f5, 8(a1)
fld f6, 16(a1)
fld f7, 24(a1)
fsd f2, 16(a2)
add a1,a1,a4
fsd f3, 24(a2)
add a2,a2,a5
fsd f4, 0(a2)
fsd f5, 8(a2)
fsd f6, 16(a2)
fsd f7, 24(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
fld f0, 0(a1)
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
fsd f0, 0(a2)
fsd f1, 8(a2)
fsd f2, 16(a2)
fsd f3, 24(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,1
srli a0,a0,1
fld f0, 0(a3)
beq a0,zero,.ukr2_done
fld f1, 0(a1)
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.d f5,f1,f0
fmul.d f6,f2,f0
fmul.d f7,f3,f0
fmul.d f10,f4,f0
fsd f5, 0(a2)
add a1,a1,a4
fsd f6, 8(a2)
fsd f7, 16(a2)
fld f11, 0(a1)
fld f12, 8(a1)
fld f13, 16(a1)
fld f14, 24(a1)
fmul.d f15,f11,f0
fmul.d f16,f12,f0
fsd f10, 24(a2)
fmul.d f17,f13,f0
fmul.d f28,f14,f0
add a2,a2,a5
add a1,a1,a4
fsd f15, 0(a2)
fsd f16, 8(a2)
fsd f17, 16(a2)
fsd f28, 24(a2)
fld f1, 0(a1)
add a2,a2,a5
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.d f5,f1,f0
fmul.d f6,f2,f0
fld f11, 0(a1)
fmul.d f7,f3,f0
fld f12, 8(a1)
fmul.d f10,f4,f0
fld f13, 16(a1)
fld f14, 24(a1)
fmul.d f15,f11,f0
fmul.d f16,f12,f0
fsd f5, 0(a2)
fmul.d f17,f13,f0
fsd f6, 8(a2)
fmul.d f28,f14,f0
fsd f7, 16(a2)
fsd f10, 24(a2)
add a1,a1,a4
add a2,a2,a5
fsd f15, 0(a2)
fsd f16, 8(a2)
fsd f17, 16(a2)
fsd f28, 24(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
fld f1, 0(a1)
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fmul.d f5,f1,f0
fmul.d f6,f2,f0
fmul.d f7,f3,f0
fmul.d f10,f4,f0
fsd f5, 0(a2)
fsd f6, 8(a2)
fsd f7, 16(a2)
fsd f10, 24(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr2_tail
.ukr2_taildone:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dpackm_ukrgen_riscv64_pk_scalar4_asm, .-bli_dpackm_ukrgen_riscv64_pk_scalar4_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_riscv64_pk_scalar5
.text
.global bli_dpackm_ukrgen_riscv64_pk_scalar5_asm
.type bli_dpackm_ukrgen_riscv64_pk_scalar5_asm, %function
bli_dpackm_ukrgen_riscv64_pk_scalar5_asm:
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
fld f0, 0(a3)
li t0,4607182418800017408
fmv.d.x f1,t0
feq.d t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,1
srli a0,a0,1
beq a0,zero,.ukr1_done
fld f0, 0(a1)
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
fld f4, 32(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f5, 0(a1)
fld f6, 8(a1)
fld f7, 16(a1)
fld f10, 24(a1)
fld f11, 32(a1)
fsd f2, 16(a2)
add a1,a1,a4
fsd f3, 24(a2)
fsd f4, 32(a2)
add a2,a2,a5
fld f0, 0(a1)
fld f1, 8(a1)
fsd f5, 0(a2)
fsd f6, 8(a2)
fsd f7, 16(a2)
fsd f10, 24(a2)
fsd f11, 32(a2)
fld f2, 16(a1)
add a2,a2,a5
fld f3, 24(a1)
fld f4, 32(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f5, 0(a1)
fld f6, 8(a1)
fld f7, 16(a1)
fld f10, 24(a1)
fld f11, 32(a1)
fsd f2, 16(a2)
add a1,a1,a4
fsd f3, 24(a2)
fsd f4, 32(a2)
add a2,a2,a5
fsd f5, 0(a2)
fsd f6, 8(a2)
fsd f7, 16(a2)
fsd f10, 24(a2)
fsd f11, 32(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
fld f0, 0(a1)
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
fld f4, 32(a1)
fsd f0, 0(a2)
fsd f1, 8(a2)
fsd f2, 16(a2)
fsd f3, 24(a2)
fsd f4, 32(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,1
srli a0,a0,1
fld f0, 0(a3)
beq a0,zero,.ukr2_done
fld f1, 0(a1)
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fld f5, 32(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.d f6,f1,f0
fmul.d f7,f2,f0
fmul.d f10,f3,f0
fmul.d f11,f4,f0
fsd f6, 0(a2)
fmul.d f12,f5,f0
fsd f7, 8(a2)
add a1,a1,a4
fsd f10, 16(a2)
fsd f11, 24(a2)
fld f13, 0(a1)
fld f14, 8(a1)
fld f15, 16(a1)
fld f16, 24(a1)
fmul.d f17,f13,f0
fld f28, 32(a1)
fmul.d f29,f14,f0
fmul.d f30,f15,f0
fsd f12, 32(a2)
fmul.d f31,f16,f0
fmul.d f8,f28,f0
add a2,a2,a5
add a1,a1,a4
fsd f17, 0(a2)
fsd f29, 8(a2)
fsd f30, 16(a2)
fsd f31, 24(a2)
fsd f8, 32(a2)
fld f1, 0(a1)
add a2,a2,a5
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fld f5, 32(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.d f6,f1,f0
fmul.d f7,f2,f0
fld f13, 0(a1)
fmul.d f10,f3,f0
fld f14, 8(a1)
fmul.d f11,f4,f0
fld f15, 16(a1)
fmul.d f12,f5,f0
fld f16, 24(a1)
fld f28, 32(a1)
fmul.d f17,f13,f0
fmul.d f29,f14,f0
fsd f6, 0(a2)
fmul.d f30,f15,f0
fsd f7, 8(a2)
fmul.d f31,f16,f0
fsd f10, 16(a2)
fmul.d f8,f28,f0
fsd f11, 24(a2)
fsd f12, 32(a2)
add a1,a1,a4
add a2,a2,a5
fsd f17, 0(a2)
fsd f29, 8(a2)
fsd f30, 16(a2)
fsd f31, 24(a2)
fsd f8, 32(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
fld f1, 0(a1)
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fmul.d f6,f1,f0
fld f5, 32(a1)
fmul.d f7,f2,f0
fmul.d f10,f3,f0
fmul.d f11,f4,f0
fsd f6, 0(a2)
fmul.d f12,f5,f0
fsd f7, 8(a2)
fsd f10, 16(a2)
fsd f11, 24(a2)
fsd f12, 32(a2)
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
.size bli_dpackm_ukrgen_riscv64_pk_scalar5_asm, .-bli_dpackm_ukrgen_riscv64_pk_scalar5_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_riscv64_pk_scalar6
.text
.global bli_dpackm_ukrgen_riscv64_pk_scalar6_asm
.type bli_dpackm_ukrgen_riscv64_pk_scalar6_asm, %function
bli_dpackm_ukrgen_riscv64_pk_scalar6_asm:
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
fld f0, 0(a3)
li t0,4607182418800017408
fmv.d.x f1,t0
feq.d t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,1
srli a0,a0,1
beq a0,zero,.ukr1_done
fld f0, 0(a1)
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
fld f4, 32(a1)
fld f5, 40(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f6, 0(a1)
fld f7, 8(a1)
fld f10, 16(a1)
fld f11, 24(a1)
fld f12, 32(a1)
fld f13, 40(a1)
fsd f2, 16(a2)
add a1,a1,a4
fsd f3, 24(a2)
fsd f4, 32(a2)
fsd f5, 40(a2)
add a2,a2,a5
fld f0, 0(a1)
fld f1, 8(a1)
fsd f6, 0(a2)
fsd f7, 8(a2)
fsd f10, 16(a2)
fsd f11, 24(a2)
fsd f12, 32(a2)
fsd f13, 40(a2)
fld f2, 16(a1)
add a2,a2,a5
fld f3, 24(a1)
fld f4, 32(a1)
fld f5, 40(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f6, 0(a1)
fld f7, 8(a1)
fld f10, 16(a1)
fld f11, 24(a1)
fld f12, 32(a1)
fld f13, 40(a1)
fsd f2, 16(a2)
add a1,a1,a4
fsd f3, 24(a2)
fsd f4, 32(a2)
fsd f5, 40(a2)
add a2,a2,a5
fsd f6, 0(a2)
fsd f7, 8(a2)
fsd f10, 16(a2)
fsd f11, 24(a2)
fsd f12, 32(a2)
fsd f13, 40(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
fld f0, 0(a1)
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
fld f4, 32(a1)
fld f5, 40(a1)
fsd f0, 0(a2)
fsd f1, 8(a2)
fsd f2, 16(a2)
fsd f3, 24(a2)
fsd f4, 32(a2)
fsd f5, 40(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,1
srli a0,a0,1
fld f0, 0(a3)
beq a0,zero,.ukr2_done
fld f1, 0(a1)
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fld f5, 32(a1)
fld f6, 40(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.d f7,f1,f0
fmul.d f10,f2,f0
fmul.d f11,f3,f0
fmul.d f12,f4,f0
fsd f7, 0(a2)
fmul.d f13,f5,f0
fsd f10, 8(a2)
fmul.d f14,f6,f0
fsd f11, 16(a2)
add a1,a1,a4
fsd f12, 24(a2)
fsd f13, 32(a2)
fld f15, 0(a1)
fld f16, 8(a1)
fld f17, 16(a1)
fld f28, 24(a1)
fmul.d f29,f15,f0
fld f30, 32(a1)
fmul.d f31,f16,f0
fld f8, 40(a1)
fmul.d f9,f17,f0
fmul.d f18,f28,f0
fsd f14, 40(a2)
fmul.d f19,f30,f0
fmul.d f20,f8,f0
add a2,a2,a5
add a1,a1,a4
fsd f29, 0(a2)
fsd f31, 8(a2)
fsd f9, 16(a2)
fsd f18, 24(a2)
fsd f19, 32(a2)
fsd f20, 40(a2)
fld f1, 0(a1)
add a2,a2,a5
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fld f5, 32(a1)
fld f6, 40(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.d f7,f1,f0
fmul.d f10,f2,f0
fld f15, 0(a1)
fmul.d f11,f3,f0
fld f16, 8(a1)
fmul.d f12,f4,f0
fld f17, 16(a1)
fmul.d f13,f5,f0
fld f28, 24(a1)
fmul.d f14,f6,f0
fld f30, 32(a1)
fld f8, 40(a1)
fmul.d f29,f15,f0
fmul.d f31,f16,f0
fsd f7, 0(a2)
fmul.d f9,f17,f0
fsd f10, 8(a2)
fmul.d f18,f28,f0
fsd f11, 16(a2)
fmul.d f19,f30,f0
fsd f12, 24(a2)
fmul.d f20,f8,f0
fsd f13, 32(a2)
fsd f14, 40(a2)
add a1,a1,a4
add a2,a2,a5
fsd f29, 0(a2)
fsd f31, 8(a2)
fsd f9, 16(a2)
fsd f18, 24(a2)
fsd f19, 32(a2)
fsd f20, 40(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
fld f1, 0(a1)
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fmul.d f7,f1,f0
fld f5, 32(a1)
fmul.d f10,f2,f0
fld f6, 40(a1)
fmul.d f11,f3,f0
fmul.d f12,f4,f0
fsd f7, 0(a2)
fmul.d f13,f5,f0
fsd f10, 8(a2)
fmul.d f14,f6,f0
fsd f11, 16(a2)
fsd f12, 24(a2)
fsd f13, 32(a2)
fsd f14, 40(a2)
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
.size bli_dpackm_ukrgen_riscv64_pk_scalar6_asm, .-bli_dpackm_ukrgen_riscv64_pk_scalar6_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_riscv64_pk_scalar7
.text
.global bli_dpackm_ukrgen_riscv64_pk_scalar7_asm
.type bli_dpackm_ukrgen_riscv64_pk_scalar7_asm, %function
bli_dpackm_ukrgen_riscv64_pk_scalar7_asm:
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
fld f0, 0(a3)
li t0,4607182418800017408
fmv.d.x f1,t0
feq.d t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
andi t0,a0,1
srli a0,a0,1
beq a0,zero,.ukr1_done
fld f0, 0(a1)
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
fld f4, 32(a1)
fld f5, 40(a1)
fld f6, 48(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f7, 0(a1)
fld f10, 8(a1)
fld f11, 16(a1)
fld f12, 24(a1)
fld f13, 32(a1)
fld f14, 40(a1)
fld f15, 48(a1)
fsd f2, 16(a2)
add a1,a1,a4
fsd f3, 24(a2)
fsd f4, 32(a2)
fsd f5, 40(a2)
fsd f6, 48(a2)
add a2,a2,a5
fld f0, 0(a1)
fld f1, 8(a1)
fsd f7, 0(a2)
fsd f10, 8(a2)
fsd f11, 16(a2)
fsd f12, 24(a2)
fsd f13, 32(a2)
fsd f14, 40(a2)
fsd f15, 48(a2)
fld f2, 16(a1)
add a2,a2,a5
fld f3, 24(a1)
fld f4, 32(a1)
fld f5, 40(a1)
fld f6, 48(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fld f7, 0(a1)
fld f10, 8(a1)
fld f11, 16(a1)
fld f12, 24(a1)
fld f13, 32(a1)
fld f14, 40(a1)
fld f15, 48(a1)
fsd f2, 16(a2)
add a1,a1,a4
fsd f3, 24(a2)
fsd f4, 32(a2)
fsd f5, 40(a2)
fsd f6, 48(a2)
add a2,a2,a5
fsd f7, 0(a2)
fsd f10, 8(a2)
fsd f11, 16(a2)
fsd f12, 24(a2)
fsd f13, 32(a2)
fsd f14, 40(a2)
fsd f15, 48(a2)
add a2,a2,a5
.ukr1_done:
beq t0,zero,.ukr1_taildone
.ukr1_tail:
add t0,t0,-1
fld f0, 0(a1)
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
fld f4, 32(a1)
fld f5, 40(a1)
fld f6, 48(a1)
fsd f0, 0(a2)
fsd f1, 8(a2)
fsd f2, 16(a2)
fsd f3, 24(a2)
fsd f4, 32(a2)
fsd f5, 40(a2)
fsd f6, 48(a2)
add a1,a1,a4
add a2,a2,a5
bne t0,zero,.ukr1_tail
.ukr1_taildone:
j .ukr0_cases_end
.ukr0_case1:
andi t0,a0,1
srli a0,a0,1
fld f0, 0(a3)
beq a0,zero,.ukr2_done
fld f1, 0(a1)
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fld f5, 32(a1)
fld f6, 40(a1)
fld f7, 48(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.d f10,f1,f0
fmul.d f11,f2,f0
fmul.d f12,f3,f0
fmul.d f13,f4,f0
fsd f10, 0(a2)
fmul.d f14,f5,f0
fsd f11, 8(a2)
fmul.d f15,f6,f0
fsd f12, 16(a2)
fmul.d f16,f7,f0
fsd f13, 24(a2)
add a1,a1,a4
fsd f14, 32(a2)
fsd f15, 40(a2)
fld f17, 0(a1)
fld f28, 8(a1)
fld f29, 16(a1)
fld f30, 24(a1)
fmul.d f31,f17,f0
fld f8, 32(a1)
fmul.d f9,f28,f0
fld f18, 40(a1)
fmul.d f19,f29,f0
fld f20, 48(a1)
fmul.d f21,f30,f0
fmul.d f22,f8,f0
fsd f16, 48(a2)
fmul.d f23,f18,f0
fmul.d f24,f20,f0
add a2,a2,a5
add a1,a1,a4
fsd f31, 0(a2)
fsd f9, 8(a2)
fsd f19, 16(a2)
fsd f21, 24(a2)
fsd f22, 32(a2)
fsd f23, 40(a2)
fsd f24, 48(a2)
fld f1, 0(a1)
add a2,a2,a5
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fld f5, 32(a1)
fld f6, 40(a1)
fld f7, 48(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
add a1,a1,a4
fmul.d f10,f1,f0
fmul.d f11,f2,f0
fld f17, 0(a1)
fmul.d f12,f3,f0
fld f28, 8(a1)
fmul.d f13,f4,f0
fld f29, 16(a1)
fmul.d f14,f5,f0
fld f30, 24(a1)
fmul.d f15,f6,f0
fld f8, 32(a1)
fmul.d f16,f7,f0
fld f18, 40(a1)
fld f20, 48(a1)
fmul.d f31,f17,f0
fmul.d f9,f28,f0
fsd f10, 0(a2)
fmul.d f19,f29,f0
fsd f11, 8(a2)
fmul.d f21,f30,f0
fsd f12, 16(a2)
fmul.d f22,f8,f0
fsd f13, 24(a2)
fmul.d f23,f18,f0
fsd f14, 32(a2)
fmul.d f24,f20,f0
fsd f15, 40(a2)
fsd f16, 48(a2)
add a1,a1,a4
add a2,a2,a5
fsd f31, 0(a2)
fsd f9, 8(a2)
fsd f19, 16(a2)
fsd f21, 24(a2)
fsd f22, 32(a2)
fsd f23, 40(a2)
fsd f24, 48(a2)
add a2,a2,a5
.ukr2_done:
beq t0,zero,.ukr2_taildone
.ukr2_tail:
add t0,t0,-1
fld f1, 0(a1)
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fmul.d f10,f1,f0
fld f5, 32(a1)
fmul.d f11,f2,f0
fld f6, 40(a1)
fmul.d f12,f3,f0
fld f7, 48(a1)
fmul.d f13,f4,f0
fmul.d f14,f5,f0
fsd f10, 0(a2)
fmul.d f15,f6,f0
fsd f11, 8(a2)
fmul.d f16,f7,f0
fsd f12, 16(a2)
fsd f13, 24(a2)
fsd f14, 32(a2)
fsd f15, 40(a2)
fsd f16, 48(a2)
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
.size bli_dpackm_ukrgen_riscv64_pk_scalar7_asm, .-bli_dpackm_ukrgen_riscv64_pk_scalar7_asm
.section .note.GNU-stack,"",%progbits


### bli_dpackm_ukrgen_riscv64_pk_scalar8
.text
.global bli_dpackm_ukrgen_riscv64_pk_scalar8_asm
.type bli_dpackm_ukrgen_riscv64_pk_scalar8_asm, %function
bli_dpackm_ukrgen_riscv64_pk_scalar8_asm:
.cfi_startproc
# a0 = n
# a1 = base(X)
# a2 = base(Y)
# a3 = base(kappa)
# a4 = stride(X,n)
# a5 = stride(Y,n)
fld f0, 0(a3)
li t0,4607182418800017408
fmv.d.x f1,t0
feq.d t0,f0,f1
beqz t0,.ukr0_try0
j .ukr0_case0
.ukr0_try0:
j .ukr0_case1
j .ukr0_cases_end
.ukr0_case0:
beq a0,zero,.ukr1_done
fld f0, 0(a1)
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
fld f4, 32(a1)
fld f5, 40(a1)
fld f6, 48(a1)
fld f7, 56(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsd f0, 0(a2)
fsd f1, 8(a2)
fsd f2, 16(a2)
fsd f3, 24(a2)
fsd f4, 32(a2)
fsd f5, 40(a2)
fsd f6, 48(a2)
fsd f7, 56(a2)
fld f0, 0(a1)
add a2,a2,a5
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
fld f4, 32(a1)
fld f5, 40(a1)
fld f6, 48(a1)
fld f7, 56(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
fsd f0, 0(a2)
fsd f1, 8(a2)
fsd f2, 16(a2)
fsd f3, 24(a2)
fsd f4, 32(a2)
fsd f5, 40(a2)
fsd f6, 48(a2)
fsd f7, 56(a2)
.ukr1_done:
j .ukr0_cases_end
.ukr0_case1:
fld f0, 0(a3)
beq a0,zero,.ukr2_done
fld f1, 0(a1)
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fld f5, 32(a1)
fld f6, 40(a1)
fld f7, 48(a1)
fld f10, 56(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.d f11,f1,f0
fmul.d f12,f2,f0
fmul.d f13,f3,f0
fmul.d f14,f4,f0
fsd f11, 0(a2)
fmul.d f15,f5,f0
fsd f12, 8(a2)
fmul.d f16,f6,f0
fsd f13, 16(a2)
fmul.d f17,f7,f0
fsd f14, 24(a2)
fmul.d f28,f10,f0
fsd f15, 32(a2)
add a1,a1,a4
fsd f16, 40(a2)
fsd f17, 48(a2)
fsd f28, 56(a2)
fld f1, 0(a1)
add a2,a2,a5
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fld f5, 32(a1)
fld f6, 40(a1)
fld f7, 48(a1)
fld f10, 56(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
fmul.d f11,f1,f0
fmul.d f12,f2,f0
fmul.d f13,f3,f0
fmul.d f14,f4,f0
fsd f11, 0(a2)
fmul.d f15,f5,f0
fsd f12, 8(a2)
fmul.d f16,f6,f0
fsd f13, 16(a2)
fmul.d f17,f7,f0
fsd f14, 24(a2)
fmul.d f28,f10,f0
fsd f15, 32(a2)
fsd f16, 40(a2)
fsd f17, 48(a2)
fsd f28, 56(a2)
.ukr2_done:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dpackm_ukrgen_riscv64_pk_scalar8_asm, .-bli_dpackm_ukrgen_riscv64_pk_scalar8_asm
.section .note.GNU-stack,"",%progbits
