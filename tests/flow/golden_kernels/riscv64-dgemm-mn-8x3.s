.text
.global bli_dgemm_ukrgen_riscv64_mn_8x3_asm
.type bli_dgemm_ukrgen_riscv64_mn_8x3_asm, %function
bli_dgemm_ukrgen_riscv64_mn_8x3_asm:
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
fcvt.d.w f0, zero
fcvt.d.w f1, zero
fcvt.d.w f2, zero
fcvt.d.w f3, zero
fcvt.d.w f4, zero
fcvt.d.w f5, zero
fcvt.d.w f6, zero
fcvt.d.w f7, zero
fcvt.d.w f10, zero
fcvt.d.w f11, zero
fcvt.d.w f12, zero
fcvt.d.w f13, zero
fcvt.d.w f14, zero
fcvt.d.w f15, zero
fcvt.d.w f16, zero
fcvt.d.w f17, zero
fcvt.d.w f28, zero
fcvt.d.w f29, zero
fcvt.d.w f30, zero
fcvt.d.w f31, zero
fcvt.d.w f8, zero
fcvt.d.w f9, zero
fcvt.d.w f18, zero
fcvt.d.w f19, zero
beq a0,zero,.ukr1_done
fld f20, 0(a1)
fld f21, 8(a1)
fld f22, 16(a1)
fld f23, 24(a1)
fld f24, 32(a1)
fld f25, 0(a2)
fld f26, 8(a2)
fld f27, 16(a2)
add a1,a1,40
add a2,a2,24
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
fmadd.d f0,f20,f25,f0
fmadd.d f1,f20,f26,f1
fmadd.d f2,f20,f27,f2
fmadd.d f3,f21,f25,f3
fmadd.d f4,f21,f26,f4
fmadd.d f5,f21,f27,f5
fmadd.d f6,f22,f25,f6
fmadd.d f7,f22,f26,f7
fmadd.d f10,f22,f27,f10
fld f20, 0(a1)
fld f21, 8(a1)
fld f22, 16(a1)
fmadd.d f11,f23,f25,f11
fmadd.d f12,f23,f26,f12
fmadd.d f13,f23,f27,f13
fmadd.d f14,f24,f25,f14
fmadd.d f15,f24,f26,f15
fmadd.d f16,f24,f27,f16
fmadd.d f17,f20,f25,f17
fmadd.d f28,f20,f26,f28
fmadd.d f29,f20,f27,f29
fmadd.d f30,f21,f25,f30
fmadd.d f31,f21,f26,f31
fmadd.d f8,f21,f27,f8
fmadd.d f9,f22,f25,f9
fmadd.d f18,f22,f26,f18
fmadd.d f19,f22,f27,f19
fld f20, 24(a1)
fld f21, 32(a1)
fld f22, 40(a1)
fld f23, 48(a1)
fld f24, 56(a1)
fld f25, 0(a2)
fld f26, 8(a2)
fld f27, 16(a2)
add a1,a1,64
add a2,a2,24
bne a0,zero,.ukr1_loop
.ukr1_last:
fmadd.d f0,f20,f25,f0
fmadd.d f1,f20,f26,f1
fmadd.d f2,f20,f27,f2
fmadd.d f3,f21,f25,f3
fmadd.d f4,f21,f26,f4
fmadd.d f5,f21,f27,f5
fmadd.d f6,f22,f25,f6
fmadd.d f7,f22,f26,f7
fmadd.d f10,f22,f27,f10
fld f20, 0(a1)
fld f21, 8(a1)
fld f22, 16(a1)
fmadd.d f11,f23,f25,f11
fmadd.d f12,f23,f26,f12
fmadd.d f13,f23,f27,f13
fmadd.d f14,f24,f25,f14
fmadd.d f15,f24,f26,f15
fmadd.d f16,f24,f27,f16
fmadd.d f17,f20,f25,f17
fmadd.d f28,f20,f26,f28
fmadd.d f29,f20,f27,f29
fmadd.d f30,f21,f25,f30
fmadd.d f31,f21,f26,f31
fmadd.d f8,f21,f27,f8
fmadd.d f9,f22,f25,f9
fmadd.d f18,f22,f26,f18
fmadd.d f19,f22,f27,f19
.ukr1_done:
fld f20, 0(a5)
fcvt.d.w f21, zero
feq.d t0,f20,f21
beqz t0,.ukr0_try0
fld f20, 0(a4)
li t0,4607182418800017408
fmv.d.x f21,t0
feq.d t0,f20,f21
beqz t0,.ukr0_try1
j .ukr0_case0
.ukr0_try1:
j .ukr0_case1
.ukr0_try0:
fld f20, 0(a5)
li t0,4607182418800017408
fmv.d.x f21,t0
feq.d t0,f20,f21
beqz t0,.ukr0_try2
fld f20, 0(a4)
li t0,4607182418800017408
fmv.d.x f21,t0
feq.d t0,f20,f21
beqz t0,.ukr0_try3
j .ukr0_case2
.ukr0_try3:
j .ukr0_case3
.ukr0_try2:
fld f20, 0(a4)
li t0,4607182418800017408
fmv.d.x f21,t0
feq.d t0,f20,f21
beqz t0,.ukr0_try4
j .ukr0_case4
.ukr0_try4:
j .ukr0_case5
j .ukr0_cases_end
.ukr0_case0:
add t0,a3,0
fsd f0, 0(t0)
add t0,t0,a6
fsd f1, 0(t0)
add t0,t0,a6
fsd f2, 0(t0)
add t0,a3,0
fsd f3, 8(t0)
add t0,t0,a6
fsd f4, 8(t0)
add t0,t0,a6
fsd f5, 8(t0)
add t0,a3,0
fsd f6, 16(t0)
add t0,t0,a6
fsd f7, 16(t0)
add t0,t0,a6
fsd f10, 16(t0)
add t0,a3,0
fsd f11, 24(t0)
add t0,t0,a6
fsd f12, 24(t0)
add t0,t0,a6
fsd f13, 24(t0)
add t0,a3,0
fsd f14, 32(t0)
add t0,t0,a6
fsd f15, 32(t0)
add t0,t0,a6
fsd f16, 32(t0)
add t0,a3,0
fsd f17, 40(t0)
add t0,t0,a6
fsd f28, 40(t0)
add t0,t0,a6
fsd f29, 40(t0)
add t0,a3,0
fsd f30, 48(t0)
add t0,t0,a6
fsd f31, 48(t0)
add t0,t0,a6
fsd f8, 48(t0)
add t0,a3,0
fsd f9, 56(t0)
add t0,t0,a6
fsd f18, 56(t0)
add t0,t0,a6
fsd f19, 56(t0)
j .ukr0_cases_end
.ukr0_case1:
add t0,a3,0
fld f20, 0(a4)
fmul.d f21,f0,f20
fsd f21, 0(t0)
fmul.d f0,f1,f20
add t0,t0,a6
fsd f0, 0(t0)
fmul.d f0,f2,f20
add t0,t0,a6
fsd f0, 0(t0)
fmul.d f0,f3,f20
add t0,a3,0
fsd f0, 8(t0)
fmul.d f0,f4,f20
add t0,t0,a6
fsd f0, 8(t0)
fmul.d f0,f5,f20
add t0,t0,a6
fsd f0, 8(t0)
fmul.d f0,f6,f20
add t0,a3,0
fsd f0, 16(t0)
fmul.d f0,f7,f20
add t0,t0,a6
fsd f0, 16(t0)
fmul.d f0,f10,f20
add t0,t0,a6
fsd f0, 16(t0)
fmul.d f0,f11,f20
add t0,a3,0
fsd f0, 24(t0)
fmul.d f0,f12,f20
add t0,t0,a6
fsd f0, 24(t0)
fmul.d f0,f13,f20
add t0,t0,a6
fsd f0, 24(t0)
fmul.d f0,f14,f20
add t0,a3,0
fsd f0, 32(t0)
fmul.d f0,f15,f20
add t0,t0,a6
fsd f0, 32(t0)
fmul.d f0,f16,f20
add t0,t0,a6
fsd f0, 32(t0)
fmul.d f0,f17,f20
add t0,a3,0
fsd f0, 40(t0)
fmul.d f0,f28,f20
add t0,t0,a6
fsd f0, 40(t0)
fmul.d f0,f29,f20
add t0,t0,a6
fsd f0, 40(t0)
fmul.d f0,f30,f20
add t0,a3,0
fsd f0, 48(t0)
fmul.d f0,f31,f20
add t0,t0,a6
fsd f0, 48(t0)
fmul.d f0,f8,f20
add t0,t0,a6
fsd f0, 48(t0)
fmul.d f0,f9,f20
add t0,a3,0
fsd f0, 56(t0)
fmul.d f0,f18,f20
add t0,t0,a6
fsd f0, 56(t0)
fmul.d f0,f19,f20
add t0,t0,a6
fsd f0, 56(t0)
j .ukr0_cases_end
.ukr0_case2:
add t0,a3,0
fld f20, 0(t0)
fadd.d f20,f0,f20
add t0,t0,a6
fsd f20, 0(a3)
fld f0, 0(t0)
fadd.d f0,f1,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 0(a3)
fld f0, 0(t0)
fadd.d f0,f2,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 0(a3)
sub t0,t0,a6
fld f0, 8(t0)
add a3,t0,0
fadd.d f0,f3,f0
add t0,t0,a6
fsd f0, 8(a3)
fld f0, 8(t0)
fadd.d f0,f4,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 8(a3)
fld f0, 8(t0)
fadd.d f0,f5,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 8(a3)
sub t0,t0,a6
fld f0, 16(t0)
add a3,t0,0
fadd.d f0,f6,f0
add t0,t0,a6
fsd f0, 16(a3)
fld f0, 16(t0)
fadd.d f0,f7,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 16(a3)
fld f0, 16(t0)
fadd.d f0,f10,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 16(a3)
sub t0,t0,a6
fld f0, 24(t0)
add a3,t0,0
fadd.d f0,f11,f0
add t0,t0,a6
fsd f0, 24(a3)
fld f0, 24(t0)
fadd.d f0,f12,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 24(a3)
fld f0, 24(t0)
fadd.d f0,f13,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 24(a3)
sub t0,t0,a6
fld f0, 32(t0)
add a3,t0,0
fadd.d f0,f14,f0
add t0,t0,a6
fsd f0, 32(a3)
fld f0, 32(t0)
fadd.d f0,f15,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 32(a3)
fld f0, 32(t0)
fadd.d f0,f16,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 32(a3)
sub t0,t0,a6
fld f0, 40(t0)
add a3,t0,0
fadd.d f0,f17,f0
add t0,t0,a6
fsd f0, 40(a3)
fld f0, 40(t0)
fadd.d f0,f28,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 40(a3)
fld f0, 40(t0)
fadd.d f0,f29,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 40(a3)
sub t0,t0,a6
fld f0, 48(t0)
add a3,t0,0
fadd.d f0,f30,f0
add t0,t0,a6
fsd f0, 48(a3)
fld f0, 48(t0)
fadd.d f0,f31,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 48(a3)
fld f0, 48(t0)
fadd.d f0,f8,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 48(a3)
sub t0,t0,a6
fld f0, 56(t0)
add a3,t0,0
fadd.d f0,f9,f0
add t0,t0,a6
fsd f0, 56(a3)
fld f0, 56(t0)
fadd.d f0,f18,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 56(a3)
fld f0, 56(t0)
fadd.d f0,f19,f0
add a3,a3,a6
fsd f0, 56(a3)
j .ukr0_cases_end
.ukr0_case3:
add t0,a3,0
fld f20, 0(t0)
fld f21, 0(a4)
fmadd.d f20,f0,f21,f20
add t0,t0,a6
fsd f20, 0(a3)
fld f0, 0(t0)
fmadd.d f0,f1,f21,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 0(a3)
fld f0, 0(t0)
fmadd.d f0,f2,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 0(a3)
sub t0,t0,a6
fld f0, 8(t0)
add a3,t0,0
fmadd.d f0,f3,f21,f0
add t0,t0,a6
fsd f0, 8(a3)
fld f0, 8(t0)
fmadd.d f0,f4,f21,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 8(a3)
fld f0, 8(t0)
fmadd.d f0,f5,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 8(a3)
sub t0,t0,a6
fld f0, 16(t0)
add a3,t0,0
fmadd.d f0,f6,f21,f0
add t0,t0,a6
fsd f0, 16(a3)
fld f0, 16(t0)
fmadd.d f0,f7,f21,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 16(a3)
fld f0, 16(t0)
fmadd.d f0,f10,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 16(a3)
sub t0,t0,a6
fld f0, 24(t0)
add a3,t0,0
fmadd.d f0,f11,f21,f0
add t0,t0,a6
fsd f0, 24(a3)
fld f0, 24(t0)
fmadd.d f0,f12,f21,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 24(a3)
fld f0, 24(t0)
fmadd.d f0,f13,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 24(a3)
sub t0,t0,a6
fld f0, 32(t0)
add a3,t0,0
fmadd.d f0,f14,f21,f0
add t0,t0,a6
fsd f0, 32(a3)
fld f0, 32(t0)
fmadd.d f0,f15,f21,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 32(a3)
fld f0, 32(t0)
fmadd.d f0,f16,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 32(a3)
sub t0,t0,a6
fld f0, 40(t0)
add a3,t0,0
fmadd.d f0,f17,f21,f0
add t0,t0,a6
fsd f0, 40(a3)
fld f0, 40(t0)
fmadd.d f0,f28,f21,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 40(a3)
fld f0, 40(t0)
fmadd.d f0,f29,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 40(a3)
sub t0,t0,a6
fld f0, 48(t0)
add a3,t0,0
fmadd.d f0,f30,f21,f0
add t0,t0,a6
fsd f0, 48(a3)
fld f0, 48(t0)
fmadd.d f0,f31,f21,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 48(a3)
fld f0, 48(t0)
fmadd.d f0,f8,f21,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 48(a3)
sub t0,t0,a6
fld f0, 56(t0)
add a3,t0,0
fmadd.d f0,f9,f21,f0
add t0,t0,a6
fsd f0, 56(a3)
fld f0, 56(t0)
fmadd.d f0,f18,f21,f0
add a3,a3,a6
add t0,t0,a6
fsd f0, 56(a3)
fld f0, 56(t0)
fmadd.d f0,f19,f21,f0
add a3,a3,a6
fsd f0, 56(a3)
j .ukr0_cases_end
.ukr0_case4:
add t0,a3,0
fld f20, 0(t0)
fld f21, 0(a5)
fmadd.d f0,f20,f21,f0
add t0,t0,a6
fsd f0, 0(a3)
fld f0, 0(t0)
fmadd.d f1,f0,f21,f1
add a3,a3,a6
add t0,t0,a6
fsd f1, 0(a3)
fld f0, 0(t0)
fmadd.d f2,f0,f21,f2
add a3,a3,a6
sub t0,t0,a6
fsd f2, 0(a3)
sub t0,t0,a6
fld f0, 8(t0)
add a3,t0,0
fmadd.d f3,f0,f21,f3
add t0,t0,a6
fsd f3, 8(a3)
fld f0, 8(t0)
fmadd.d f4,f0,f21,f4
add a3,a3,a6
add t0,t0,a6
fsd f4, 8(a3)
fld f0, 8(t0)
fmadd.d f5,f0,f21,f5
add a3,a3,a6
sub t0,t0,a6
fsd f5, 8(a3)
sub t0,t0,a6
fld f0, 16(t0)
add a3,t0,0
fmadd.d f6,f0,f21,f6
add t0,t0,a6
fsd f6, 16(a3)
fld f0, 16(t0)
fmadd.d f7,f0,f21,f7
add a3,a3,a6
add t0,t0,a6
fsd f7, 16(a3)
fld f0, 16(t0)
fmadd.d f10,f0,f21,f10
add a3,a3,a6
sub t0,t0,a6
fsd f10, 16(a3)
sub t0,t0,a6
fld f0, 24(t0)
add a3,t0,0
fmadd.d f11,f0,f21,f11
add t0,t0,a6
fsd f11, 24(a3)
fld f0, 24(t0)
fmadd.d f12,f0,f21,f12
add a3,a3,a6
add t0,t0,a6
fsd f12, 24(a3)
fld f0, 24(t0)
fmadd.d f13,f0,f21,f13
add a3,a3,a6
sub t0,t0,a6
fsd f13, 24(a3)
sub t0,t0,a6
fld f0, 32(t0)
add a3,t0,0
fmadd.d f14,f0,f21,f14
add t0,t0,a6
fsd f14, 32(a3)
fld f0, 32(t0)
fmadd.d f15,f0,f21,f15
add a3,a3,a6
add t0,t0,a6
fsd f15, 32(a3)
fld f0, 32(t0)
fmadd.d f16,f0,f21,f16
add a3,a3,a6
sub t0,t0,a6
fsd f16, 32(a3)
sub t0,t0,a6
fld f0, 40(t0)
add a3,t0,0
fmadd.d f17,f0,f21,f17
add t0,t0,a6
fsd f17, 40(a3)
fld f0, 40(t0)
fmadd.d f28,f0,f21,f28
add a3,a3,a6
add t0,t0,a6
fsd f28, 40(a3)
fld f0, 40(t0)
fmadd.d f29,f0,f21,f29
add a3,a3,a6
sub t0,t0,a6
fsd f29, 40(a3)
sub t0,t0,a6
fld f0, 48(t0)
add a3,t0,0
fmadd.d f30,f0,f21,f30
add t0,t0,a6
fsd f30, 48(a3)
fld f0, 48(t0)
fmadd.d f31,f0,f21,f31
add a3,a3,a6
add t0,t0,a6
fsd f31, 48(a3)
fld f0, 48(t0)
fmadd.d f8,f0,f21,f8
add a3,a3,a6
sub t0,t0,a6
fsd f8, 48(a3)
sub t0,t0,a6
fld f0, 56(t0)
add a3,t0,0
fmadd.d f9,f0,f21,f9
add t0,t0,a6
fsd f9, 56(a3)
fld f0, 56(t0)
fmadd.d f18,f0,f21,f18
add a3,a3,a6
add t0,t0,a6
fsd f18, 56(a3)
fld f0, 56(t0)
fmadd.d f19,f0,f21,f19
add a3,a3,a6
fsd f19, 56(a3)
j .ukr0_cases_end
.ukr0_case5:
add t0,a3,0
fld f20, 0(t0)
fld f21, 0(a5)
fmul.d f20,f20,f21
fld f22, 0(a4)
add t0,t0,a6
fmadd.d f20,f0,f22,f20
fld f0, 0(t0)
fsd f20, 0(a3)
fmul.d f0,f0,f21
add t0,t0,a6
fmadd.d f0,f1,f22,f0
add a3,a3,a6
fld f1, 0(t0)
fsd f0, 0(a3)
fmul.d f1,f1,f21
fmadd.d f1,f2,f22,f1
add a3,a3,a6
sub t0,t0,a6
fsd f1, 0(a3)
sub t0,t0,a6
fld f0, 8(t0)
add a3,t0,0
fmul.d f0,f0,f21
add t0,t0,a6
fmadd.d f0,f3,f22,f0
fld f1, 8(t0)
fsd f0, 8(a3)
fmul.d f1,f1,f21
add t0,t0,a6
fmadd.d f1,f4,f22,f1
add a3,a3,a6
fld f0, 8(t0)
fsd f1, 8(a3)
fmul.d f0,f0,f21
fmadd.d f0,f5,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 8(a3)
sub t0,t0,a6
fld f0, 16(t0)
add a3,t0,0
fmul.d f0,f0,f21
add t0,t0,a6
fmadd.d f0,f6,f22,f0
fld f1, 16(t0)
fsd f0, 16(a3)
fmul.d f1,f1,f21
add t0,t0,a6
fmadd.d f1,f7,f22,f1
add a3,a3,a6
fld f0, 16(t0)
fsd f1, 16(a3)
fmul.d f0,f0,f21
fmadd.d f0,f10,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 16(a3)
sub t0,t0,a6
fld f0, 24(t0)
add a3,t0,0
fmul.d f0,f0,f21
add t0,t0,a6
fmadd.d f0,f11,f22,f0
fld f1, 24(t0)
fsd f0, 24(a3)
fmul.d f1,f1,f21
add t0,t0,a6
fmadd.d f1,f12,f22,f1
add a3,a3,a6
fld f0, 24(t0)
fsd f1, 24(a3)
fmul.d f0,f0,f21
fmadd.d f0,f13,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 24(a3)
sub t0,t0,a6
fld f0, 32(t0)
add a3,t0,0
fmul.d f0,f0,f21
add t0,t0,a6
fmadd.d f0,f14,f22,f0
fld f1, 32(t0)
fsd f0, 32(a3)
fmul.d f1,f1,f21
add t0,t0,a6
fmadd.d f1,f15,f22,f1
add a3,a3,a6
fld f0, 32(t0)
fsd f1, 32(a3)
fmul.d f0,f0,f21
fmadd.d f0,f16,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 32(a3)
sub t0,t0,a6
fld f0, 40(t0)
add a3,t0,0
fmul.d f0,f0,f21
add t0,t0,a6
fmadd.d f0,f17,f22,f0
fld f1, 40(t0)
fsd f0, 40(a3)
fmul.d f1,f1,f21
add t0,t0,a6
fmadd.d f1,f28,f22,f1
add a3,a3,a6
fld f0, 40(t0)
fsd f1, 40(a3)
fmul.d f0,f0,f21
fmadd.d f0,f29,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 40(a3)
sub t0,t0,a6
fld f0, 48(t0)
add a3,t0,0
fmul.d f0,f0,f21
add t0,t0,a6
fmadd.d f0,f30,f22,f0
fld f1, 48(t0)
fsd f0, 48(a3)
fmul.d f1,f1,f21
add t0,t0,a6
fmadd.d f1,f31,f22,f1
add a3,a3,a6
fld f0, 48(t0)
fsd f1, 48(a3)
fmul.d f0,f0,f21
fmadd.d f0,f8,f22,f0
add a3,a3,a6
sub t0,t0,a6
fsd f0, 48(a3)
sub t0,t0,a6
fld f0, 56(t0)
add a3,t0,0
fmul.d f0,f0,f21
add t0,t0,a6
fmadd.d f0,f9,f22,f0
fld f1, 56(t0)
fsd f0, 56(a3)
fmul.d f1,f1,f21
add t0,t0,a6
fmadd.d f1,f18,f22,f1
add a3,a3,a6
fld f0, 56(t0)
fsd f1, 56(a3)
fmul.d f0,f0,f21
fmadd.d f0,f19,f22,f0
add a3,a3,a6
fsd f0, 56(a3)
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
.size bli_dgemm_ukrgen_riscv64_mn_8x3_asm, .-bli_dgemm_ukrgen_riscv64_mn_8x3_asm
.section .note.GNU-stack,"",%progbits
