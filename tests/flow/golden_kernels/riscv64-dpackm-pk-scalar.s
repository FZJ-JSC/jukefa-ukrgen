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
beq a0,zero,.ukr1_done
fld f0, 0(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsd f0, 0(a2)
add a2,a2,a5
fld f0, 0(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
fsd f0, 0(a2)
.ukr1_done:
j .ukr0_cases_end
.ukr0_case1:
fld f0, 0(a3)
beq a0,zero,.ukr2_done
fld f1, 0(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.d f2,f1,f0
add a1,a1,a4
fld f1, 0(a1)
fsd f2, 0(a2)
add a2,a2,a5
bne a0,zero,.ukr2_loop
.ukr2_last:
fmul.d f2,f1,f0
fsd f2, 0(a2)
.ukr2_done:
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
fld f0, 0(a1)
add a2,a2,a5
fld f1, 8(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
fsd f0, 0(a2)
fsd f1, 8(a2)
.ukr1_done:
j .ukr0_cases_end
.ukr0_case1:
fld f0, 0(a3)
beq a0,zero,.ukr2_done
fld f1, 0(a1)
fld f2, 8(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.d f3,f1,f0
fmul.d f4,f2,f0
add a1,a1,a4
fsd f3, 0(a2)
fsd f4, 8(a2)
fld f1, 0(a1)
add a2,a2,a5
fld f2, 8(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
fmul.d f3,f1,f0
fmul.d f4,f2,f0
fsd f3, 0(a2)
fsd f4, 8(a2)
.ukr2_done:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dpackm_ukrgen_riscv64_pk_scalar2_asm, .-bli_dpackm_ukrgen_riscv64_pk_scalar2_asm
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
fsd f2, 16(a2)
fsd f3, 24(a2)
fld f0, 0(a1)
add a2,a2,a5
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
fsd f0, 0(a2)
fsd f1, 8(a2)
fsd f2, 16(a2)
fsd f3, 24(a2)
.ukr1_done:
j .ukr0_cases_end
.ukr0_case1:
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
fsd f10, 24(a2)
fld f1, 0(a1)
add a2,a2,a5
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
fmul.d f5,f1,f0
fmul.d f6,f2,f0
fmul.d f7,f3,f0
fmul.d f10,f4,f0
fsd f5, 0(a2)
fsd f6, 8(a2)
fsd f7, 16(a2)
fsd f10, 24(a2)
.ukr2_done:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dpackm_ukrgen_riscv64_pk_scalar4_asm, .-bli_dpackm_ukrgen_riscv64_pk_scalar4_asm
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


### bli_dpackm_ukrgen_riscv64_pk_scalar16
.text
.global bli_dpackm_ukrgen_riscv64_pk_scalar16_asm
.type bli_dpackm_ukrgen_riscv64_pk_scalar16_asm, %function
bli_dpackm_ukrgen_riscv64_pk_scalar16_asm:
.cfi_startproc
add sp,sp,-96
.cfi_adjust_cfa_offset 96
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
fsd f25, 72(sp)
.cfi_rel_offset f25, 72
fsd f26, 80(sp)
.cfi_rel_offset f26, 80
fsd f27, 88(sp)
.cfi_rel_offset f27, 88
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
fld f10, 64(a1)
fld f11, 72(a1)
fld f12, 80(a1)
fld f13, 88(a1)
fld f14, 96(a1)
fld f15, 104(a1)
fld f16, 112(a1)
fld f17, 120(a1)
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
fsd f10, 64(a2)
fsd f11, 72(a2)
fsd f12, 80(a2)
fsd f13, 88(a2)
fsd f14, 96(a2)
fsd f15, 104(a2)
fsd f16, 112(a2)
fsd f17, 120(a2)
fld f0, 0(a1)
add a2,a2,a5
fld f1, 8(a1)
fld f2, 16(a1)
fld f3, 24(a1)
fld f4, 32(a1)
fld f5, 40(a1)
fld f6, 48(a1)
fld f7, 56(a1)
fld f10, 64(a1)
fld f11, 72(a1)
fld f12, 80(a1)
fld f13, 88(a1)
fld f14, 96(a1)
fld f15, 104(a1)
fld f16, 112(a1)
fld f17, 120(a1)
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
fsd f10, 64(a2)
fsd f11, 72(a2)
fsd f12, 80(a2)
fsd f13, 88(a2)
fsd f14, 96(a2)
fsd f15, 104(a2)
fsd f16, 112(a2)
fsd f17, 120(a2)
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
fld f11, 64(a1)
fld f12, 72(a1)
fld f13, 80(a1)
fld f14, 88(a1)
fld f15, 96(a1)
fld f16, 104(a1)
fld f17, 112(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.d f28,f1,f0
fld f1, 120(a1)
fmul.d f29,f2,f0
fmul.d f30,f3,f0
fmul.d f31,f4,f0
fsd f28, 0(a2)
fmul.d f8,f5,f0
fsd f29, 8(a2)
fmul.d f9,f6,f0
fsd f30, 16(a2)
fmul.d f18,f7,f0
fsd f31, 24(a2)
fmul.d f19,f10,f0
fsd f8, 32(a2)
fmul.d f20,f11,f0
fsd f9, 40(a2)
fmul.d f21,f12,f0
fsd f18, 48(a2)
fmul.d f22,f13,f0
fsd f19, 56(a2)
fmul.d f23,f14,f0
fsd f20, 64(a2)
fmul.d f24,f15,f0
fsd f21, 72(a2)
fmul.d f25,f16,f0
fsd f22, 80(a2)
fmul.d f26,f17,f0
fsd f23, 88(a2)
fmul.d f27,f1,f0
fsd f24, 96(a2)
add a1,a1,a4
fsd f25, 104(a2)
fsd f26, 112(a2)
fsd f27, 120(a2)
fld f1, 0(a1)
add a2,a2,a5
fld f2, 8(a1)
fld f3, 16(a1)
fld f4, 24(a1)
fld f5, 32(a1)
fld f6, 40(a1)
fld f7, 48(a1)
fld f10, 56(a1)
fld f11, 64(a1)
fld f12, 72(a1)
fld f13, 80(a1)
fld f14, 88(a1)
fld f15, 96(a1)
fld f16, 104(a1)
fld f17, 112(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
fmul.d f28,f1,f0
fld f1, 120(a1)
fmul.d f29,f2,f0
fmul.d f30,f3,f0
fmul.d f31,f4,f0
fsd f28, 0(a2)
fmul.d f8,f5,f0
fsd f29, 8(a2)
fmul.d f9,f6,f0
fsd f30, 16(a2)
fmul.d f18,f7,f0
fsd f31, 24(a2)
fmul.d f19,f10,f0
fsd f8, 32(a2)
fmul.d f20,f11,f0
fsd f9, 40(a2)
fmul.d f21,f12,f0
fsd f18, 48(a2)
fmul.d f22,f13,f0
fsd f19, 56(a2)
fmul.d f23,f14,f0
fsd f20, 64(a2)
fmul.d f24,f15,f0
fsd f21, 72(a2)
fmul.d f25,f16,f0
fsd f22, 80(a2)
fmul.d f26,f17,f0
fsd f23, 88(a2)
fmul.d f27,f1,f0
fsd f24, 96(a2)
fsd f25, 104(a2)
fsd f26, 112(a2)
fsd f27, 120(a2)
.ukr2_done:
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
fld f25, 72(sp)
.cfi_restore f25
fld f26, 80(sp)
.cfi_restore f26
fld f27, 88(sp)
.cfi_restore f27
add sp,sp,96
.cfi_adjust_cfa_offset -96
ret
.cfi_endproc
.size bli_dpackm_ukrgen_riscv64_pk_scalar16_asm, .-bli_dpackm_ukrgen_riscv64_pk_scalar16_asm
.section .note.GNU-stack,"",%progbits
