.text
.global bli_sgemm_ukrgen_riscv64_mn_8x3_asm
.type bli_sgemm_ukrgen_riscv64_mn_8x3_asm, %function
bli_sgemm_ukrgen_riscv64_mn_8x3_asm:
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
# a0 = k
# a1 = base(A)
# a2 = base(B)
# a3 = base(C)
# a4 = base(alpha)
# a5 = base(beta)
# a6 = stride(C,n)
fcvt.s.w f0, zero
fcvt.s.w f1, zero
fcvt.s.w f2, zero
fcvt.s.w f3, zero
fcvt.s.w f4, zero
fcvt.s.w f5, zero
fcvt.s.w f6, zero
fcvt.s.w f7, zero
fcvt.s.w f10, zero
fcvt.s.w f11, zero
fcvt.s.w f12, zero
fcvt.s.w f13, zero
fcvt.s.w f14, zero
fcvt.s.w f15, zero
fcvt.s.w f16, zero
fcvt.s.w f17, zero
fcvt.s.w f28, zero
fcvt.s.w f29, zero
fcvt.s.w f30, zero
fcvt.s.w f31, zero
fcvt.s.w f8, zero
fcvt.s.w f9, zero
fcvt.s.w f18, zero
fcvt.s.w f19, zero
beq a0,zero,.ukr1_done
flw f20, 0(a1)
flw f21, 4(a1)
flw f22, 8(a1)
flw f23, 12(a1)
flw f24, 16(a1)
flw f25, 0(a2)
flw f26, 4(a2)
flw f27, 8(a2)
add a1,a1,20
add a2,a2,12
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
fmadd.s f0,f20,f25,f0
fmadd.s f1,f20,f26,f1
fmadd.s f2,f20,f27,f2
fmadd.s f3,f21,f25,f3
fmadd.s f4,f21,f26,f4
fmadd.s f5,f21,f27,f5
fmadd.s f6,f22,f25,f6
fmadd.s f7,f22,f26,f7
fmadd.s f10,f22,f27,f10
flw f20, 0(a1)
flw f21, 4(a1)
flw f22, 8(a1)
fmadd.s f11,f23,f25,f11
fmadd.s f12,f23,f26,f12
fmadd.s f13,f23,f27,f13
fmadd.s f14,f24,f25,f14
fmadd.s f15,f24,f26,f15
fmadd.s f16,f24,f27,f16
fmadd.s f17,f20,f25,f17
fmadd.s f28,f20,f26,f28
fmadd.s f29,f20,f27,f29
fmadd.s f30,f21,f25,f30
fmadd.s f31,f21,f26,f31
fmadd.s f8,f21,f27,f8
fmadd.s f9,f22,f25,f9
fmadd.s f18,f22,f26,f18
fmadd.s f19,f22,f27,f19
flw f20, 12(a1)
flw f21, 16(a1)
flw f22, 20(a1)
flw f23, 24(a1)
flw f24, 28(a1)
flw f25, 0(a2)
flw f26, 4(a2)
flw f27, 8(a2)
add a1,a1,32
add a2,a2,12
bne a0,zero,.ukr1_loop
.ukr1_last:
fmadd.s f0,f20,f25,f0
fmadd.s f1,f20,f26,f1
fmadd.s f2,f20,f27,f2
fmadd.s f3,f21,f25,f3
fmadd.s f4,f21,f26,f4
fmadd.s f5,f21,f27,f5
fmadd.s f6,f22,f25,f6
fmadd.s f7,f22,f26,f7
fmadd.s f10,f22,f27,f10
flw f20, 0(a1)
flw f21, 4(a1)
flw f22, 8(a1)
fmadd.s f11,f23,f25,f11
fmadd.s f12,f23,f26,f12
fmadd.s f13,f23,f27,f13
fmadd.s f14,f24,f25,f14
fmadd.s f15,f24,f26,f15
fmadd.s f16,f24,f27,f16
fmadd.s f17,f20,f25,f17
fmadd.s f28,f20,f26,f28
fmadd.s f29,f20,f27,f29
fmadd.s f30,f21,f25,f30
fmadd.s f31,f21,f26,f31
fmadd.s f8,f21,f27,f8
fmadd.s f9,f22,f25,f9
fmadd.s f18,f22,f26,f18
fmadd.s f19,f22,f27,f19
.ukr1_done:
flw f20, 0(a5)
fcvt.s.w f21, zero
feq.s t0,f20,f21
beqz t0,.ukr0_try0
flw f20, 0(a4)
li t0,1065353216
fmv.w.x f21,t0
feq.s t0,f20,f21
beqz t0,.ukr0_try1
j .ukr0_case0
.ukr0_try1:
j .ukr0_case1
.ukr0_try0:
flw f20, 0(a5)
li t0,1065353216
fmv.w.x f21,t0
feq.s t0,f20,f21
beqz t0,.ukr0_try2
flw f20, 0(a4)
li t0,1065353216
fmv.w.x f21,t0
feq.s t0,f20,f21
beqz t0,.ukr0_try3
j .ukr0_case2
.ukr0_try3:
j .ukr0_case3
.ukr0_try2:
flw f20, 0(a4)
li t0,1065353216
fmv.w.x f21,t0
feq.s t0,f20,f21
beqz t0,.ukr0_try4
j .ukr0_case4
.ukr0_try4:
j .ukr0_case5
j .ukr0_cases_end
.ukr0_case0:
add t0,a3,0
fsw f0, 0(t0)
add t0,t0,a6
fsw f1, 0(t0)
add t0,t0,a6
fsw f2, 0(t0)
add t0,a3,0
fsw f3, 4(t0)
add t0,t0,a6
fsw f4, 4(t0)
add t0,t0,a6
fsw f5, 4(t0)
add t0,a3,0
fsw f6, 8(t0)
add t0,t0,a6
fsw f7, 8(t0)
add t0,t0,a6
fsw f10, 8(t0)
add t0,a3,0
fsw f11, 12(t0)
add t0,t0,a6
fsw f12, 12(t0)
add t0,t0,a6
fsw f13, 12(t0)
add t0,a3,0
fsw f14, 16(t0)
add t0,t0,a6
fsw f15, 16(t0)
add t0,t0,a6
fsw f16, 16(t0)
add t0,a3,0
fsw f17, 20(t0)
add t0,t0,a6
fsw f28, 20(t0)
add t0,t0,a6
fsw f29, 20(t0)
add t0,a3,0
fsw f30, 24(t0)
add t0,t0,a6
fsw f31, 24(t0)
add t0,t0,a6
fsw f8, 24(t0)
add t0,a3,0
fsw f9, 28(t0)
add t0,t0,a6
fsw f18, 28(t0)
add t0,t0,a6
fsw f19, 28(t0)
j .ukr0_cases_end
.ukr0_case1:
add t0,a3,0
flw f20, 0(a4)
fmul.s f21,f0,f20
fsw f21, 0(t0)
fmul.s f0,f1,f20
add t0,t0,a6
fsw f0, 0(t0)
fmul.s f0,f2,f20
add t0,t0,a6
fsw f0, 0(t0)
fmul.s f0,f3,f20
add t0,a3,0
fsw f0, 4(t0)
fmul.s f0,f4,f20
add t0,t0,a6
fsw f0, 4(t0)
fmul.s f0,f5,f20
add t0,t0,a6
fsw f0, 4(t0)
fmul.s f0,f6,f20
add t0,a3,0
fsw f0, 8(t0)
fmul.s f0,f7,f20
add t0,t0,a6
fsw f0, 8(t0)
fmul.s f0,f10,f20
add t0,t0,a6
fsw f0, 8(t0)
fmul.s f0,f11,f20
add t0,a3,0
fsw f0, 12(t0)
fmul.s f0,f12,f20
add t0,t0,a6
fsw f0, 12(t0)
fmul.s f0,f13,f20
add t0,t0,a6
fsw f0, 12(t0)
fmul.s f0,f14,f20
add t0,a3,0
fsw f0, 16(t0)
fmul.s f0,f15,f20
add t0,t0,a6
fsw f0, 16(t0)
fmul.s f0,f16,f20
add t0,t0,a6
fsw f0, 16(t0)
fmul.s f0,f17,f20
add t0,a3,0
fsw f0, 20(t0)
fmul.s f0,f28,f20
add t0,t0,a6
fsw f0, 20(t0)
fmul.s f0,f29,f20
add t0,t0,a6
fsw f0, 20(t0)
fmul.s f0,f30,f20
add t0,a3,0
fsw f0, 24(t0)
fmul.s f0,f31,f20
add t0,t0,a6
fsw f0, 24(t0)
fmul.s f0,f8,f20
add t0,t0,a6
fsw f0, 24(t0)
fmul.s f0,f9,f20
add t0,a3,0
fsw f0, 28(t0)
fmul.s f0,f18,f20
add t0,t0,a6
fsw f0, 28(t0)
fmul.s f0,f19,f20
add t0,t0,a6
fsw f0, 28(t0)
j .ukr0_cases_end
.ukr0_case2:
add t0,a3,0
flw f20, 0(t0)
fadd.s f20,f0,f20
add t0,t0,a6
fsw f20, 0(a3)
flw f0, 0(t0)
fadd.s f0,f1,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 0(a3)
flw f0, 0(t0)
fadd.s f0,f2,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 0(a3)
sub t0,t0,a6
flw f0, 4(t0)
add a3,t0,0
fadd.s f0,f3,f0
add t0,t0,a6
fsw f0, 4(a3)
flw f0, 4(t0)
fadd.s f0,f4,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 4(a3)
flw f0, 4(t0)
fadd.s f0,f5,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 4(a3)
sub t0,t0,a6
flw f0, 8(t0)
add a3,t0,0
fadd.s f0,f6,f0
add t0,t0,a6
fsw f0, 8(a3)
flw f0, 8(t0)
fadd.s f0,f7,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 8(a3)
flw f0, 8(t0)
fadd.s f0,f10,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 8(a3)
sub t0,t0,a6
flw f0, 12(t0)
add a3,t0,0
fadd.s f0,f11,f0
add t0,t0,a6
fsw f0, 12(a3)
flw f0, 12(t0)
fadd.s f0,f12,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 12(a3)
flw f0, 12(t0)
fadd.s f0,f13,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 12(a3)
sub t0,t0,a6
flw f0, 16(t0)
add a3,t0,0
fadd.s f0,f14,f0
add t0,t0,a6
fsw f0, 16(a3)
flw f0, 16(t0)
fadd.s f0,f15,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 16(a3)
flw f0, 16(t0)
fadd.s f0,f16,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 16(a3)
sub t0,t0,a6
flw f0, 20(t0)
add a3,t0,0
fadd.s f0,f17,f0
add t0,t0,a6
fsw f0, 20(a3)
flw f0, 20(t0)
fadd.s f0,f28,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 20(a3)
flw f0, 20(t0)
fadd.s f0,f29,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 20(a3)
sub t0,t0,a6
flw f0, 24(t0)
add a3,t0,0
fadd.s f0,f30,f0
add t0,t0,a6
fsw f0, 24(a3)
flw f0, 24(t0)
fadd.s f0,f31,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 24(a3)
flw f0, 24(t0)
fadd.s f0,f8,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 24(a3)
sub t0,t0,a6
flw f0, 28(t0)
add a3,t0,0
fadd.s f0,f9,f0
add t0,t0,a6
fsw f0, 28(a3)
flw f0, 28(t0)
fadd.s f0,f18,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 28(a3)
flw f0, 28(t0)
fadd.s f0,f19,f0
add a3,a3,a6
fsw f0, 28(a3)
j .ukr0_cases_end
.ukr0_case3:
add t0,a3,0
flw f20, 0(t0)
flw f21, 0(a4)
fmadd.s f20,f0,f21,f20
add t0,t0,a6
fsw f20, 0(a3)
flw f0, 0(t0)
fmadd.s f0,f1,f21,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 0(a3)
flw f0, 0(t0)
fmadd.s f0,f2,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 0(a3)
sub t0,t0,a6
flw f0, 4(t0)
add a3,t0,0
fmadd.s f0,f3,f21,f0
add t0,t0,a6
fsw f0, 4(a3)
flw f0, 4(t0)
fmadd.s f0,f4,f21,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 4(a3)
flw f0, 4(t0)
fmadd.s f0,f5,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 4(a3)
sub t0,t0,a6
flw f0, 8(t0)
add a3,t0,0
fmadd.s f0,f6,f21,f0
add t0,t0,a6
fsw f0, 8(a3)
flw f0, 8(t0)
fmadd.s f0,f7,f21,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 8(a3)
flw f0, 8(t0)
fmadd.s f0,f10,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 8(a3)
sub t0,t0,a6
flw f0, 12(t0)
add a3,t0,0
fmadd.s f0,f11,f21,f0
add t0,t0,a6
fsw f0, 12(a3)
flw f0, 12(t0)
fmadd.s f0,f12,f21,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 12(a3)
flw f0, 12(t0)
fmadd.s f0,f13,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 12(a3)
sub t0,t0,a6
flw f0, 16(t0)
add a3,t0,0
fmadd.s f0,f14,f21,f0
add t0,t0,a6
fsw f0, 16(a3)
flw f0, 16(t0)
fmadd.s f0,f15,f21,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 16(a3)
flw f0, 16(t0)
fmadd.s f0,f16,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 16(a3)
sub t0,t0,a6
flw f0, 20(t0)
add a3,t0,0
fmadd.s f0,f17,f21,f0
add t0,t0,a6
fsw f0, 20(a3)
flw f0, 20(t0)
fmadd.s f0,f28,f21,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 20(a3)
flw f0, 20(t0)
fmadd.s f0,f29,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 20(a3)
sub t0,t0,a6
flw f0, 24(t0)
add a3,t0,0
fmadd.s f0,f30,f21,f0
add t0,t0,a6
fsw f0, 24(a3)
flw f0, 24(t0)
fmadd.s f0,f31,f21,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 24(a3)
flw f0, 24(t0)
fmadd.s f0,f8,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 24(a3)
sub t0,t0,a6
flw f0, 28(t0)
add a3,t0,0
fmadd.s f0,f9,f21,f0
add t0,t0,a6
fsw f0, 28(a3)
flw f0, 28(t0)
fmadd.s f0,f18,f21,f0
add a3,a3,a6
add t0,t0,a6
fsw f0, 28(a3)
flw f0, 28(t0)
fmadd.s f0,f19,f21,f0
add a3,a3,a6
fsw f0, 28(a3)
j .ukr0_cases_end
.ukr0_case4:
add t0,a3,0
flw f20, 0(t0)
flw f21, 0(a5)
fmadd.s f0,f20,f21,f0
add t0,t0,a6
fsw f0, 0(a3)
flw f0, 0(t0)
fmadd.s f1,f0,f21,f1
add a3,a3,a6
add t0,t0,a6
fsw f1, 0(a3)
flw f0, 0(t0)
fmadd.s f2,f0,f21,f2
add a3,a3,a6
sub t0,t0,a6
fsw f2, 0(a3)
sub t0,t0,a6
flw f0, 4(t0)
add a3,t0,0
fmadd.s f3,f0,f21,f3
add t0,t0,a6
fsw f3, 4(a3)
flw f0, 4(t0)
fmadd.s f4,f0,f21,f4
add a3,a3,a6
add t0,t0,a6
fsw f4, 4(a3)
flw f0, 4(t0)
fmadd.s f5,f0,f21,f5
add a3,a3,a6
sub t0,t0,a6
fsw f5, 4(a3)
sub t0,t0,a6
flw f0, 8(t0)
add a3,t0,0
fmadd.s f6,f0,f21,f6
add t0,t0,a6
fsw f6, 8(a3)
flw f0, 8(t0)
fmadd.s f7,f0,f21,f7
add a3,a3,a6
add t0,t0,a6
fsw f7, 8(a3)
flw f0, 8(t0)
fmadd.s f10,f0,f21,f10
add a3,a3,a6
sub t0,t0,a6
fsw f10, 8(a3)
sub t0,t0,a6
flw f0, 12(t0)
add a3,t0,0
fmadd.s f11,f0,f21,f11
add t0,t0,a6
fsw f11, 12(a3)
flw f0, 12(t0)
fmadd.s f12,f0,f21,f12
add a3,a3,a6
add t0,t0,a6
fsw f12, 12(a3)
flw f0, 12(t0)
fmadd.s f13,f0,f21,f13
add a3,a3,a6
sub t0,t0,a6
fsw f13, 12(a3)
sub t0,t0,a6
flw f0, 16(t0)
add a3,t0,0
fmadd.s f14,f0,f21,f14
add t0,t0,a6
fsw f14, 16(a3)
flw f0, 16(t0)
fmadd.s f15,f0,f21,f15
add a3,a3,a6
add t0,t0,a6
fsw f15, 16(a3)
flw f0, 16(t0)
fmadd.s f16,f0,f21,f16
add a3,a3,a6
sub t0,t0,a6
fsw f16, 16(a3)
sub t0,t0,a6
flw f0, 20(t0)
add a3,t0,0
fmadd.s f17,f0,f21,f17
add t0,t0,a6
fsw f17, 20(a3)
flw f0, 20(t0)
fmadd.s f28,f0,f21,f28
add a3,a3,a6
add t0,t0,a6
fsw f28, 20(a3)
flw f0, 20(t0)
fmadd.s f29,f0,f21,f29
add a3,a3,a6
sub t0,t0,a6
fsw f29, 20(a3)
sub t0,t0,a6
flw f0, 24(t0)
add a3,t0,0
fmadd.s f30,f0,f21,f30
add t0,t0,a6
fsw f30, 24(a3)
flw f0, 24(t0)
fmadd.s f31,f0,f21,f31
add a3,a3,a6
add t0,t0,a6
fsw f31, 24(a3)
flw f0, 24(t0)
fmadd.s f8,f0,f21,f8
add a3,a3,a6
sub t0,t0,a6
fsw f8, 24(a3)
sub t0,t0,a6
flw f0, 28(t0)
add a3,t0,0
fmadd.s f9,f0,f21,f9
add t0,t0,a6
fsw f9, 28(a3)
flw f0, 28(t0)
fmadd.s f18,f0,f21,f18
add a3,a3,a6
add t0,t0,a6
fsw f18, 28(a3)
flw f0, 28(t0)
fmadd.s f19,f0,f21,f19
add a3,a3,a6
fsw f19, 28(a3)
j .ukr0_cases_end
.ukr0_case5:
add t0,a3,0
flw f20, 0(t0)
flw f21, 0(a5)
fmul.s f20,f20,f21
flw f22, 0(a4)
add t0,t0,a6
fmadd.s f20,f0,f22,f20
flw f0, 0(t0)
fsw f20, 0(a3)
fmul.s f0,f0,f21
add t0,t0,a6
fmadd.s f0,f1,f22,f0
add a3,a3,a6
flw f1, 0(t0)
fsw f0, 0(a3)
fmul.s f1,f1,f21
fmadd.s f1,f2,f22,f1
add a3,a3,a6
sub t0,t0,a6
fsw f1, 0(a3)
sub t0,t0,a6
flw f0, 4(t0)
add a3,t0,0
fmul.s f0,f0,f21
add t0,t0,a6
fmadd.s f0,f3,f22,f0
flw f1, 4(t0)
fsw f0, 4(a3)
fmul.s f1,f1,f21
add t0,t0,a6
fmadd.s f1,f4,f22,f1
add a3,a3,a6
flw f0, 4(t0)
fsw f1, 4(a3)
fmul.s f0,f0,f21
fmadd.s f0,f5,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 4(a3)
sub t0,t0,a6
flw f0, 8(t0)
add a3,t0,0
fmul.s f0,f0,f21
add t0,t0,a6
fmadd.s f0,f6,f22,f0
flw f1, 8(t0)
fsw f0, 8(a3)
fmul.s f1,f1,f21
add t0,t0,a6
fmadd.s f1,f7,f22,f1
add a3,a3,a6
flw f0, 8(t0)
fsw f1, 8(a3)
fmul.s f0,f0,f21
fmadd.s f0,f10,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 8(a3)
sub t0,t0,a6
flw f0, 12(t0)
add a3,t0,0
fmul.s f0,f0,f21
add t0,t0,a6
fmadd.s f0,f11,f22,f0
flw f1, 12(t0)
fsw f0, 12(a3)
fmul.s f1,f1,f21
add t0,t0,a6
fmadd.s f1,f12,f22,f1
add a3,a3,a6
flw f0, 12(t0)
fsw f1, 12(a3)
fmul.s f0,f0,f21
fmadd.s f0,f13,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 12(a3)
sub t0,t0,a6
flw f0, 16(t0)
add a3,t0,0
fmul.s f0,f0,f21
add t0,t0,a6
fmadd.s f0,f14,f22,f0
flw f1, 16(t0)
fsw f0, 16(a3)
fmul.s f1,f1,f21
add t0,t0,a6
fmadd.s f1,f15,f22,f1
add a3,a3,a6
flw f0, 16(t0)
fsw f1, 16(a3)
fmul.s f0,f0,f21
fmadd.s f0,f16,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 16(a3)
sub t0,t0,a6
flw f0, 20(t0)
add a3,t0,0
fmul.s f0,f0,f21
add t0,t0,a6
fmadd.s f0,f17,f22,f0
flw f1, 20(t0)
fsw f0, 20(a3)
fmul.s f1,f1,f21
add t0,t0,a6
fmadd.s f1,f28,f22,f1
add a3,a3,a6
flw f0, 20(t0)
fsw f1, 20(a3)
fmul.s f0,f0,f21
fmadd.s f0,f29,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 20(a3)
sub t0,t0,a6
flw f0, 24(t0)
add a3,t0,0
fmul.s f0,f0,f21
add t0,t0,a6
fmadd.s f0,f30,f22,f0
flw f1, 24(t0)
fsw f0, 24(a3)
fmul.s f1,f1,f21
add t0,t0,a6
fmadd.s f1,f31,f22,f1
add a3,a3,a6
flw f0, 24(t0)
fsw f1, 24(a3)
fmul.s f0,f0,f21
fmadd.s f0,f8,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsw f0, 24(a3)
sub t0,t0,a6
flw f0, 28(t0)
add a3,t0,0
fmul.s f0,f0,f21
add t0,t0,a6
fmadd.s f0,f9,f22,f0
flw f1, 28(t0)
fsw f0, 28(a3)
fmul.s f1,f1,f21
add t0,t0,a6
fmadd.s f1,f18,f22,f1
add a3,a3,a6
flw f0, 28(t0)
fsw f1, 28(a3)
fmul.s f0,f0,f21
fmadd.s f0,f19,f22,f0
add a3,a3,a6
fsw f0, 28(a3)
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
.size bli_sgemm_ukrgen_riscv64_mn_8x3_asm, .-bli_sgemm_ukrgen_riscv64_mn_8x3_asm
.section .note.GNU-stack,"",%progbits
