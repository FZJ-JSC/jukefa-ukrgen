.text
.global bli_sgemm_ukrgen_riscv64_nm_3x8_asm
.type bli_sgemm_ukrgen_riscv64_nm_3x8_asm, %function
bli_sgemm_ukrgen_riscv64_nm_3x8_asm:
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
flw f23, 0(a2)
flw f24, 4(a2)
flw f25, 8(a2)
flw f26, 12(a2)
flw f27, 16(a2)
add a2,a2,20
add a1,a1,12
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
fmadd.s f0,f20,f23,f0
fmadd.s f1,f21,f23,f1
fmadd.s f2,f22,f23,f2
fmadd.s f3,f20,f24,f3
flw f23, 0(a2)
fmadd.s f4,f21,f24,f4
fmadd.s f5,f22,f24,f5
fmadd.s f6,f20,f25,f6
flw f24, 4(a2)
fmadd.s f7,f21,f25,f7
fmadd.s f10,f22,f25,f10
flw f25, 8(a2)
fmadd.s f11,f20,f26,f11
fmadd.s f12,f21,f26,f12
fmadd.s f13,f22,f26,f13
fmadd.s f14,f20,f27,f14
flw f26, 24(a2)
fmadd.s f15,f21,f27,f15
fmadd.s f16,f22,f27,f16
fmadd.s f17,f20,f23,f17
flw f27, 28(a2)
fmadd.s f28,f21,f23,f28
fmadd.s f29,f22,f23,f29
fmadd.s f30,f20,f24,f30
flw f23, 12(a2)
fmadd.s f31,f21,f24,f31
fmadd.s f8,f22,f24,f8
fmadd.s f9,f20,f25,f9
flw f24, 16(a2)
fmadd.s f18,f21,f25,f18
flw f20, 0(a1)
fmadd.s f19,f22,f25,f19
flw f21, 4(a1)
flw f22, 8(a1)
flw f25, 20(a2)
add a1,a1,12
add a2,a2,32
bne a0,zero,.ukr1_loop
.ukr1_last:
fmadd.s f0,f20,f23,f0
fmadd.s f1,f21,f23,f1
fmadd.s f2,f22,f23,f2
fmadd.s f3,f20,f24,f3
flw f23, 0(a2)
fmadd.s f4,f21,f24,f4
fmadd.s f5,f22,f24,f5
fmadd.s f6,f20,f25,f6
flw f24, 4(a2)
fmadd.s f7,f21,f25,f7
fmadd.s f10,f22,f25,f10
flw f25, 8(a2)
fmadd.s f11,f20,f26,f11
fmadd.s f12,f21,f26,f12
fmadd.s f13,f22,f26,f13
fmadd.s f14,f20,f27,f14
fmadd.s f15,f21,f27,f15
fmadd.s f16,f22,f27,f16
fmadd.s f17,f20,f23,f17
fmadd.s f28,f21,f23,f28
fmadd.s f29,f22,f23,f29
fmadd.s f30,f20,f24,f30
fmadd.s f31,f21,f24,f31
fmadd.s f8,f22,f24,f8
fmadd.s f9,f20,f25,f9
fmadd.s f18,f21,f25,f18
fmadd.s f19,f22,f25,f19
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
fsw f1, 4(t0)
fsw f2, 8(t0)
add t0,t0,a6
fsw f3, 0(t0)
fsw f4, 4(t0)
fsw f5, 8(t0)
add t0,t0,a6
fsw f6, 0(t0)
fsw f7, 4(t0)
fsw f10, 8(t0)
add t0,t0,a6
fsw f11, 0(t0)
fsw f12, 4(t0)
fsw f13, 8(t0)
add t0,t0,a6
fsw f14, 0(t0)
fsw f15, 4(t0)
fsw f16, 8(t0)
add t0,t0,a6
fsw f17, 0(t0)
fsw f28, 4(t0)
fsw f29, 8(t0)
add t0,t0,a6
fsw f30, 0(t0)
fsw f31, 4(t0)
fsw f8, 8(t0)
add t0,t0,a6
fsw f9, 0(t0)
fsw f18, 4(t0)
fsw f19, 8(t0)
j .ukr0_cases_end
.ukr0_case1:
add t0,a3,0
flw f20, 0(a4)
fmul.s f21,f0,f20
fmul.s f0,f1,f20
fsw f21, 0(t0)
fmul.s f1,f2,f20
fsw f0, 4(t0)
fsw f1, 8(t0)
fmul.s f0,f3,f20
add t0,t0,a6
fmul.s f1,f4,f20
fmul.s f2,f5,f20
fsw f0, 0(t0)
fsw f1, 4(t0)
fmul.s f0,f6,f20
fsw f2, 8(t0)
fmul.s f1,f7,f20
add t0,t0,a6
fmul.s f2,f10,f20
fsw f0, 0(t0)
fmul.s f0,f11,f20
fsw f1, 4(t0)
fmul.s f1,f12,f20
fsw f2, 8(t0)
fmul.s f2,f13,f20
add t0,t0,a6
fmul.s f3,f14,f20
fsw f0, 0(t0)
fmul.s f0,f15,f20
fsw f1, 4(t0)
fmul.s f1,f16,f20
fsw f2, 8(t0)
fmul.s f2,f17,f20
add t0,t0,a6
fmul.s f4,f28,f20
fsw f3, 0(t0)
fmul.s f3,f29,f20
fsw f0, 4(t0)
fmul.s f0,f30,f20
fsw f1, 8(t0)
fmul.s f1,f31,f20
add t0,t0,a6
fmul.s f5,f8,f20
fsw f2, 0(t0)
fmul.s f2,f9,f20
fsw f4, 4(t0)
fmul.s f4,f18,f20
fsw f3, 8(t0)
fmul.s f3,f19,f20
add t0,t0,a6
fsw f0, 0(t0)
fsw f1, 4(t0)
fsw f5, 8(t0)
add t0,t0,a6
fsw f2, 0(t0)
fsw f4, 4(t0)
fsw f3, 8(t0)
j .ukr0_cases_end
.ukr0_case2:
add t0,a3,0
flw f20, 0(t0)
flw f21, 4(t0)
fadd.s f20,f0,f20
flw f0, 8(t0)
fadd.s f21,f1,f21
fadd.s f0,f2,f0
fsw f20, 0(a3)
add t0,t0,a6
fsw f21, 4(a3)
fsw f0, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fadd.s f0,f3,f0
flw f2, 8(t0)
fadd.s f1,f4,f1
fadd.s f2,f5,f2
fsw f0, 0(a3)
add t0,t0,a6
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fadd.s f0,f6,f0
flw f2, 8(t0)
fadd.s f1,f7,f1
fadd.s f2,f10,f2
fsw f0, 0(a3)
add t0,t0,a6
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fadd.s f0,f11,f0
flw f2, 8(t0)
fadd.s f1,f12,f1
fadd.s f2,f13,f2
fsw f0, 0(a3)
add t0,t0,a6
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fadd.s f0,f14,f0
flw f2, 8(t0)
fadd.s f1,f15,f1
fadd.s f2,f16,f2
fsw f0, 0(a3)
add t0,t0,a6
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fadd.s f0,f17,f0
flw f2, 8(t0)
fadd.s f1,f28,f1
fadd.s f2,f29,f2
fsw f0, 0(a3)
add t0,t0,a6
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fadd.s f0,f30,f0
flw f2, 8(t0)
fadd.s f1,f31,f1
fadd.s f2,f8,f2
fsw f0, 0(a3)
add t0,t0,a6
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fadd.s f0,f9,f0
flw f2, 8(t0)
fadd.s f1,f18,f1
fadd.s f2,f19,f2
fsw f0, 0(a3)
fsw f1, 4(a3)
fsw f2, 8(a3)
j .ukr0_cases_end
.ukr0_case3:
add t0,a3,0
flw f20, 0(t0)
flw f21, 0(a4)
flw f22, 4(t0)
flw f23, 8(t0)
add t0,t0,a6
fmadd.s f20,f0,f21,f20
fmadd.s f22,f1,f21,f22
flw f0, 0(t0)
fmadd.s f23,f2,f21,f23
flw f1, 4(t0)
flw f2, 8(t0)
fsw f20, 0(a3)
add t0,t0,a6
fsw f22, 4(a3)
fmadd.s f0,f3,f21,f0
fsw f23, 8(a3)
fmadd.s f1,f4,f21,f1
add a3,a3,a6
flw f3, 0(t0)
fmadd.s f2,f5,f21,f2
flw f4, 4(t0)
flw f5, 8(t0)
fsw f0, 0(a3)
add t0,t0,a6
fsw f1, 4(a3)
fmadd.s f3,f6,f21,f3
fsw f2, 8(a3)
fmadd.s f4,f7,f21,f4
add a3,a3,a6
flw f0, 0(t0)
fmadd.s f5,f10,f21,f5
flw f1, 4(t0)
flw f2, 8(t0)
fsw f3, 0(a3)
add t0,t0,a6
fsw f4, 4(a3)
fmadd.s f0,f11,f21,f0
fsw f5, 8(a3)
fmadd.s f1,f12,f21,f1
add a3,a3,a6
flw f3, 0(t0)
fmadd.s f2,f13,f21,f2
flw f4, 4(t0)
flw f5, 8(t0)
fsw f0, 0(a3)
add t0,t0,a6
fsw f1, 4(a3)
fmadd.s f3,f14,f21,f3
fsw f2, 8(a3)
fmadd.s f4,f15,f21,f4
add a3,a3,a6
flw f0, 0(t0)
fmadd.s f5,f16,f21,f5
flw f1, 4(t0)
flw f2, 8(t0)
fsw f3, 0(a3)
add t0,t0,a6
fsw f4, 4(a3)
fmadd.s f0,f17,f21,f0
fsw f5, 8(a3)
fmadd.s f1,f28,f21,f1
add a3,a3,a6
flw f3, 0(t0)
fmadd.s f2,f29,f21,f2
flw f4, 4(t0)
flw f5, 8(t0)
fsw f0, 0(a3)
add t0,t0,a6
fsw f1, 4(a3)
fmadd.s f3,f30,f21,f3
fsw f2, 8(a3)
fmadd.s f4,f31,f21,f4
add a3,a3,a6
flw f0, 0(t0)
fmadd.s f5,f8,f21,f5
flw f1, 4(t0)
flw f2, 8(t0)
fsw f3, 0(a3)
fmadd.s f0,f9,f21,f0
fsw f4, 4(a3)
fmadd.s f1,f18,f21,f1
fsw f5, 8(a3)
fmadd.s f2,f19,f21,f2
add a3,a3,a6
fsw f0, 0(a3)
fsw f1, 4(a3)
fsw f2, 8(a3)
j .ukr0_cases_end
.ukr0_case4:
add t0,a3,0
flw f20, 0(t0)
flw f21, 0(a5)
flw f22, 4(t0)
flw f23, 8(t0)
add t0,t0,a6
fmadd.s f0,f20,f21,f0
fmadd.s f1,f22,f21,f1
flw f20, 0(t0)
fmadd.s f2,f23,f21,f2
flw f22, 4(t0)
flw f23, 8(t0)
fsw f0, 0(a3)
add t0,t0,a6
fsw f1, 4(a3)
fmadd.s f3,f20,f21,f3
fsw f2, 8(a3)
fmadd.s f4,f22,f21,f4
add a3,a3,a6
flw f0, 0(t0)
fmadd.s f5,f23,f21,f5
flw f1, 4(t0)
flw f2, 8(t0)
fsw f3, 0(a3)
add t0,t0,a6
fsw f4, 4(a3)
fmadd.s f6,f0,f21,f6
fsw f5, 8(a3)
fmadd.s f7,f1,f21,f7
add a3,a3,a6
flw f0, 0(t0)
fmadd.s f10,f2,f21,f10
flw f1, 4(t0)
flw f2, 8(t0)
fsw f6, 0(a3)
add t0,t0,a6
fsw f7, 4(a3)
fmadd.s f11,f0,f21,f11
fsw f10, 8(a3)
fmadd.s f12,f1,f21,f12
add a3,a3,a6
flw f0, 0(t0)
fmadd.s f13,f2,f21,f13
flw f1, 4(t0)
flw f2, 8(t0)
fsw f11, 0(a3)
add t0,t0,a6
fsw f12, 4(a3)
fmadd.s f14,f0,f21,f14
fsw f13, 8(a3)
fmadd.s f15,f1,f21,f15
add a3,a3,a6
flw f0, 0(t0)
fmadd.s f16,f2,f21,f16
flw f1, 4(t0)
flw f2, 8(t0)
fsw f14, 0(a3)
add t0,t0,a6
fsw f15, 4(a3)
fmadd.s f17,f0,f21,f17
fsw f16, 8(a3)
fmadd.s f28,f1,f21,f28
add a3,a3,a6
flw f0, 0(t0)
fmadd.s f29,f2,f21,f29
flw f1, 4(t0)
flw f2, 8(t0)
fsw f17, 0(a3)
add t0,t0,a6
fsw f28, 4(a3)
fmadd.s f30,f0,f21,f30
fsw f29, 8(a3)
fmadd.s f31,f1,f21,f31
add a3,a3,a6
flw f0, 0(t0)
fmadd.s f8,f2,f21,f8
flw f1, 4(t0)
flw f2, 8(t0)
fsw f30, 0(a3)
fmadd.s f9,f0,f21,f9
fsw f31, 4(a3)
fmadd.s f18,f1,f21,f18
fsw f8, 8(a3)
fmadd.s f19,f2,f21,f19
add a3,a3,a6
fsw f9, 0(a3)
fsw f18, 4(a3)
fsw f19, 8(a3)
j .ukr0_cases_end
.ukr0_case5:
add t0,a3,0
flw f20, 0(a4)
flw f21, 0(t0)
flw f22, 0(a5)
flw f23, 4(t0)
fmul.s f21,f21,f22
flw f24, 8(t0)
fmul.s f23,f23,f22
fmul.s f24,f24,f22
add t0,t0,a6
fmadd.s f21,f0,f20,f21
fmadd.s f23,f1,f20,f23
fsw f21, 0(a3)
fmadd.s f24,f2,f20,f24
fsw f23, 4(a3)
fsw f24, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fmul.s f0,f0,f22
flw f2, 8(t0)
fmul.s f1,f1,f22
fmul.s f2,f2,f22
add t0,t0,a6
fmadd.s f0,f3,f20,f0
fmadd.s f1,f4,f20,f1
fsw f0, 0(a3)
fmadd.s f2,f5,f20,f2
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fmul.s f0,f0,f22
flw f2, 8(t0)
fmul.s f1,f1,f22
fmul.s f2,f2,f22
add t0,t0,a6
fmadd.s f0,f6,f20,f0
fmadd.s f1,f7,f20,f1
fsw f0, 0(a3)
fmadd.s f2,f10,f20,f2
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fmul.s f0,f0,f22
flw f2, 8(t0)
fmul.s f1,f1,f22
fmul.s f2,f2,f22
add t0,t0,a6
fmadd.s f0,f11,f20,f0
fmadd.s f1,f12,f20,f1
fsw f0, 0(a3)
fmadd.s f2,f13,f20,f2
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fmul.s f0,f0,f22
flw f2, 8(t0)
fmul.s f1,f1,f22
fmul.s f2,f2,f22
add t0,t0,a6
fmadd.s f0,f14,f20,f0
fmadd.s f1,f15,f20,f1
fsw f0, 0(a3)
fmadd.s f2,f16,f20,f2
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fmul.s f0,f0,f22
flw f2, 8(t0)
fmul.s f1,f1,f22
fmul.s f2,f2,f22
add t0,t0,a6
fmadd.s f0,f17,f20,f0
fmadd.s f1,f28,f20,f1
fsw f0, 0(a3)
fmadd.s f2,f29,f20,f2
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fmul.s f0,f0,f22
flw f2, 8(t0)
fmul.s f1,f1,f22
fmul.s f2,f2,f22
add t0,t0,a6
fmadd.s f0,f30,f20,f0
fmadd.s f1,f31,f20,f1
fsw f0, 0(a3)
fmadd.s f2,f8,f20,f2
fsw f1, 4(a3)
fsw f2, 8(a3)
flw f0, 0(t0)
add a3,a3,a6
flw f1, 4(t0)
fmul.s f0,f0,f22
flw f2, 8(t0)
fmul.s f1,f1,f22
fmul.s f2,f2,f22
fmadd.s f0,f9,f20,f0
fmadd.s f1,f18,f20,f1
fsw f0, 0(a3)
fmadd.s f2,f19,f20,f2
fsw f1, 4(a3)
fsw f2, 8(a3)
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
.size bli_sgemm_ukrgen_riscv64_nm_3x8_asm, .-bli_sgemm_ukrgen_riscv64_nm_3x8_asm
.section .note.GNU-stack,"",%progbits
