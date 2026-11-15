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
beq a0,zero,.ukr1_done
flw f0, 0(a1)
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
add a1,a1,a4
fsw f0, 0(a2)
add a2,a2,a5
flw f0, 0(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
fsw f0, 0(a2)
.ukr1_done:
j .ukr0_cases_end
.ukr0_case1:
flw f0, 0(a3)
beq a0,zero,.ukr2_done
flw f1, 0(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.s f2,f1,f0
add a1,a1,a4
flw f1, 0(a1)
fsw f2, 0(a2)
add a2,a2,a5
bne a0,zero,.ukr2_loop
.ukr2_last:
fmul.s f2,f1,f0
fsw f2, 0(a2)
.ukr2_done:
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
flw f0, 0(a1)
add a2,a2,a5
flw f1, 4(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
fsw f0, 0(a2)
fsw f1, 4(a2)
.ukr1_done:
j .ukr0_cases_end
.ukr0_case1:
flw f0, 0(a3)
beq a0,zero,.ukr2_done
flw f1, 0(a1)
flw f2, 4(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.s f3,f1,f0
fmul.s f4,f2,f0
add a1,a1,a4
fsw f3, 0(a2)
fsw f4, 4(a2)
flw f1, 0(a1)
add a2,a2,a5
flw f2, 4(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
fmul.s f3,f1,f0
fmul.s f4,f2,f0
fsw f3, 0(a2)
fsw f4, 4(a2)
.ukr2_done:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_spackm_ukrgen_riscv64_pk_scalar2_asm, .-bli_spackm_ukrgen_riscv64_pk_scalar2_asm
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
fsw f2, 8(a2)
fsw f3, 12(a2)
flw f0, 0(a1)
add a2,a2,a5
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
bne a0,zero,.ukr1_loop
.ukr1_last:
fsw f0, 0(a2)
fsw f1, 4(a2)
fsw f2, 8(a2)
fsw f3, 12(a2)
.ukr1_done:
j .ukr0_cases_end
.ukr0_case1:
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
fsw f10, 12(a2)
flw f1, 0(a1)
add a2,a2,a5
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
fmul.s f5,f1,f0
fmul.s f6,f2,f0
fmul.s f7,f3,f0
fmul.s f10,f4,f0
fsw f5, 0(a2)
fsw f6, 4(a2)
fsw f7, 8(a2)
fsw f10, 12(a2)
.ukr2_done:
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_spackm_ukrgen_riscv64_pk_scalar4_asm, .-bli_spackm_ukrgen_riscv64_pk_scalar4_asm
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


### bli_spackm_ukrgen_riscv64_pk_scalar16
.text
.global bli_spackm_ukrgen_riscv64_pk_scalar16_asm
.type bli_spackm_ukrgen_riscv64_pk_scalar16_asm, %function
bli_spackm_ukrgen_riscv64_pk_scalar16_asm:
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
flw f10, 32(a1)
flw f11, 36(a1)
flw f12, 40(a1)
flw f13, 44(a1)
flw f14, 48(a1)
flw f15, 52(a1)
flw f16, 56(a1)
flw f17, 60(a1)
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
fsw f10, 32(a2)
fsw f11, 36(a2)
fsw f12, 40(a2)
fsw f13, 44(a2)
fsw f14, 48(a2)
fsw f15, 52(a2)
fsw f16, 56(a2)
fsw f17, 60(a2)
flw f0, 0(a1)
add a2,a2,a5
flw f1, 4(a1)
flw f2, 8(a1)
flw f3, 12(a1)
flw f4, 16(a1)
flw f5, 20(a1)
flw f6, 24(a1)
flw f7, 28(a1)
flw f10, 32(a1)
flw f11, 36(a1)
flw f12, 40(a1)
flw f13, 44(a1)
flw f14, 48(a1)
flw f15, 52(a1)
flw f16, 56(a1)
flw f17, 60(a1)
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
fsw f10, 32(a2)
fsw f11, 36(a2)
fsw f12, 40(a2)
fsw f13, 44(a2)
fsw f14, 48(a2)
fsw f15, 52(a2)
fsw f16, 56(a2)
fsw f17, 60(a2)
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
flw f11, 32(a1)
flw f12, 36(a1)
flw f13, 40(a1)
flw f14, 44(a1)
flw f15, 48(a1)
flw f16, 52(a1)
flw f17, 56(a1)
add a0,a0,-1
beq a0,zero,.ukr2_last
.ukr2_loop:
add a0,a0,-1
fmul.s f28,f1,f0
flw f1, 60(a1)
fmul.s f29,f2,f0
fmul.s f30,f3,f0
fmul.s f31,f4,f0
fsw f28, 0(a2)
fmul.s f8,f5,f0
fsw f29, 4(a2)
fmul.s f9,f6,f0
fsw f30, 8(a2)
fmul.s f18,f7,f0
fsw f31, 12(a2)
fmul.s f19,f10,f0
fsw f8, 16(a2)
fmul.s f20,f11,f0
fsw f9, 20(a2)
fmul.s f21,f12,f0
fsw f18, 24(a2)
fmul.s f22,f13,f0
fsw f19, 28(a2)
fmul.s f23,f14,f0
fsw f20, 32(a2)
fmul.s f24,f15,f0
fsw f21, 36(a2)
fmul.s f25,f16,f0
fsw f22, 40(a2)
fmul.s f26,f17,f0
fsw f23, 44(a2)
fmul.s f27,f1,f0
fsw f24, 48(a2)
add a1,a1,a4
fsw f25, 52(a2)
fsw f26, 56(a2)
fsw f27, 60(a2)
flw f1, 0(a1)
add a2,a2,a5
flw f2, 4(a1)
flw f3, 8(a1)
flw f4, 12(a1)
flw f5, 16(a1)
flw f6, 20(a1)
flw f7, 24(a1)
flw f10, 28(a1)
flw f11, 32(a1)
flw f12, 36(a1)
flw f13, 40(a1)
flw f14, 44(a1)
flw f15, 48(a1)
flw f16, 52(a1)
flw f17, 56(a1)
bne a0,zero,.ukr2_loop
.ukr2_last:
fmul.s f28,f1,f0
flw f1, 60(a1)
fmul.s f29,f2,f0
fmul.s f30,f3,f0
fmul.s f31,f4,f0
fsw f28, 0(a2)
fmul.s f8,f5,f0
fsw f29, 4(a2)
fmul.s f9,f6,f0
fsw f30, 8(a2)
fmul.s f18,f7,f0
fsw f31, 12(a2)
fmul.s f19,f10,f0
fsw f8, 16(a2)
fmul.s f20,f11,f0
fsw f9, 20(a2)
fmul.s f21,f12,f0
fsw f18, 24(a2)
fmul.s f22,f13,f0
fsw f19, 28(a2)
fmul.s f23,f14,f0
fsw f20, 32(a2)
fmul.s f24,f15,f0
fsw f21, 36(a2)
fmul.s f25,f16,f0
fsw f22, 40(a2)
fmul.s f26,f17,f0
fsw f23, 44(a2)
fmul.s f27,f1,f0
fsw f24, 48(a2)
fsw f25, 52(a2)
fsw f26, 56(a2)
fsw f27, 60(a2)
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
.size bli_spackm_ukrgen_riscv64_pk_scalar16_asm, .-bli_spackm_ukrgen_riscv64_pk_scalar16_asm
.section .note.GNU-stack,"",%progbits
