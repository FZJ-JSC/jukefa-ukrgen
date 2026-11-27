.text
.global gemmf16f16f32_rvv_vn_4x1v
.type gemmf16f16f32_rvv_vn_4x1v, %function
gemmf16f16f32_rvv_vn_4x1v:
.cfi_startproc
add sp,sp,-16
.cfi_adjust_cfa_offset 16
sd s1, 0(sp)
.cfi_rel_offset s1, 0
# a0 = k
# a1 = base(A)
# a2 = base(B)
# a3 = base(C)
# a4 = base(alpha)
# a5 = base(beta)
# a6 = stride(C,m)
# a7 = stride(C,n)
vsetvli t0, zero, e16, m1, ta, ma
slli t1,t0,1
slli t2,t1,1
slli t3,t1,2
add t4,a1,0
add a1,a1,2
add t5,a2,0
add a2,a2,t1
andi t6,a0,3
srli a0,a0,2
vmv.v.i v0,0
vmv.v.i v2,0
vmv.v.i v4,0
vmv.v.i v6,0
vmv.v.i v1,0
vmv.v.i v3,0
vmv.v.i v5,0
vmv.v.i v7,0
beq a0,zero,.ukr1_done
flh f0, 0(t4)
flh f1, 0(a1)
flh f2, 4(t4)
flh f3, 4(a1)
vle16.v v9, (t5)
add t4,t4,8
add a1,a1,8
add t5,t5,t2
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
vfwmacc.vf v0,f0,v9
add s1,a2,t2
vfwmacc.vf v2,f1,v9
vfwmacc.vf v4,f2,v9
vfwmacc.vf v6,f3,v9
flh f4, 0(t4)
vle16.v v11, (a2)
flh f5, 0(a1)
vle16.v v13, (t5)
flh f6, 4(t4)
add t5,t5,t3
flh f7, 4(a1)
add a2,a2,t3
flh f10, 8(t4)
vle16.v v15, (s1)
flh f11, 8(a1)
add s1,s1,t1
flh f12, 12(t4)
flh f13, 12(a1)
flh f14, 16(t4)
flh f15, 16(a1)
flh f16, 20(t4)
flh f17, 20(a1)
flh f0, 24(t4)
vle16.v v9, (s1)
vfwmacc.vf v0,f4,v11
vfwmacc.vf v2,f5,v11
vfwmacc.vf v4,f6,v11
vfwmacc.vf v6,f7,v11
flh f1, 24(a1)
flh f2, 28(t4)
flh f3, 28(a1)
add t4,t4,32
add a1,a1,32
vfwmacc.vf v0,f10,v13
vfwmacc.vf v2,f11,v13
vfwmacc.vf v4,f12,v13
vfwmacc.vf v6,f13,v13
vfwmacc.vf v0,f14,v15
vfwmacc.vf v2,f15,v15
vfwmacc.vf v4,f16,v15
vfwmacc.vf v6,f17,v15
bne a0,zero,.ukr1_loop
.ukr1_last:
vfwmacc.vf v0,f0,v9
add s1,a2,t2
vfwmacc.vf v2,f1,v9
vfwmacc.vf v4,f2,v9
vfwmacc.vf v6,f3,v9
flh f4, 0(t4)
vle16.v v11, (a2)
flh f5, 0(a1)
vle16.v v13, (t5)
flh f6, 4(t4)
vle16.v v15, (s1)
flh f7, 4(a1)
add t5,t5,t3
flh f10, 8(t4)
add a2,a2,t3
flh f11, 8(a1)
flh f12, 12(t4)
sub t5,t5,t1
flh f13, 12(a1)
flh f14, 16(t4)
flh f15, 16(a1)
sub t5,t5,t1
flh f16, 20(t4)
flh f17, 20(a1)
add t4,t4,24
add a1,a1,24
vfwmacc.vf v0,f4,v11
vfwmacc.vf v2,f5,v11
vfwmacc.vf v4,f6,v11
vfwmacc.vf v6,f7,v11
vfwmacc.vf v0,f10,v13
vfwmacc.vf v2,f11,v13
vfwmacc.vf v4,f12,v13
vfwmacc.vf v6,f13,v13
vfwmacc.vf v0,f14,v15
vfwmacc.vf v2,f15,v15
vfwmacc.vf v4,f16,v15
vfwmacc.vf v6,f17,v15
.ukr1_done:
beq t6,zero,.ukr1_taildone
.ukr1_tail:
add t6,t6,-1
flh f0, 0(t4)
vle16.v v9, (t5)
flh f1, 0(a1)
flh f2, 4(t4)
flh f3, 4(a1)
vfwmacc.vf v0,f0,v9
vfwmacc.vf v2,f1,v9
vfwmacc.vf v4,f2,v9
vfwmacc.vf v6,f3,v9
add t4,t4,8
add a1,a1,8
add t5,t5,t1
add a2,a2,t1
bne t6,zero,.ukr1_tail
.ukr1_taildone:
add t4,a7,0
add t4,t4,-4
beq t4,zero,.ukr0_ok1
j .ukr0_try0
.ukr0_ok1:
flw f0, 0(a5)
fcvt.s.w f1, zero
feq.s t4,f0,f1
beqz t4,.ukr0_try2
flw f0, 0(a4)
li t4,1065353216
fmv.w.x f1,t4
feq.s t4,f0,f1
beqz t4,.ukr0_try3
j .ukr0_case0
.ukr0_try3:
j .ukr0_case1
.ukr0_try2:
flw f0, 0(a5)
li t4,1065353216
fmv.w.x f1,t4
feq.s t4,f0,f1
beqz t4,.ukr0_try4
flw f0, 0(a4)
li t4,1065353216
fmv.w.x f1,t4
feq.s t4,f0,f1
beqz t4,.ukr0_try5
j .ukr0_case2
.ukr0_try5:
j .ukr0_case3
.ukr0_try4:
flw f0, 0(a4)
li t4,1065353216
fmv.w.x f1,t4
feq.s t4,f0,f1
beqz t4,.ukr0_try6
j .ukr0_case4
.ukr0_try6:
j .ukr0_case5
.ukr0_try0:
flw f0, 0(a5)
fcvt.s.w f1, zero
feq.s t4,f0,f1
beqz t4,.ukr0_try7
flw f0, 0(a4)
li t4,1065353216
fmv.w.x f1,t4
feq.s t4,f0,f1
beqz t4,.ukr0_try8
j .ukr0_case6
.ukr0_try8:
j .ukr0_case7
.ukr0_try7:
flw f0, 0(a5)
li t4,1065353216
fmv.w.x f1,t4
feq.s t4,f0,f1
beqz t4,.ukr0_try9
flw f0, 0(a4)
li t4,1065353216
fmv.w.x f1,t4
feq.s t4,f0,f1
beqz t4,.ukr0_try10
j .ukr0_case8
.ukr0_try10:
j .ukr0_case9
.ukr0_try9:
flw f0, 0(a4)
li t4,1065353216
fmv.w.x f1,t4
feq.s t4,f0,f1
beqz t4,.ukr0_try11
j .ukr0_case10
.ukr0_try11:
j .ukr0_case11
j .ukr0_cases_end
.ukr0_case0:
add t4,a3,0
add t5,a3,0
vse32.v v0, (t4)
add t4,t4,a6
vse32.v v2, (t4)
add t4,t4,a6
vse32.v v4, (t4)
add t4,t4,a6
vse32.v v6, (t4)
j .ukr0_cases_end
.ukr0_case1:
add t4,a3,0
add t5,a3,0
flw f0, 0(a4)
vsetvli zero, zero, e32, m2, ta, ma
vfmul.vf v8,v0,f0
vfmul.vf v10,v2,f0
vfmul.vf v12,v4,f0
vfmul.vf v14,v6,f0
vse32.v v8, (t4)
add t4,t4,a6
vse32.v v10, (t4)
add t4,t4,a6
vse32.v v12, (t4)
add t4,t4,a6
vse32.v v14, (t4)
vsetvli zero, zero, e16, m1, ta, ma
j .ukr0_cases_end
.ukr0_case2:
add t4,a3,0
add t5,a3,0
vle32.v v8, (t4)
vsetvli zero, zero, e32, m2, ta, ma
vfadd.vv v8,v0,v8
vse32.v v8, (t5)
add t4,t4,a6
vle32.v v10, (t4)
add t5,t5,a6
vfadd.vv v10,v2,v10
vse32.v v10, (t5)
add t4,t4,a6
vle32.v v12, (t4)
add t5,t5,a6
vfadd.vv v12,v4,v12
vse32.v v12, (t5)
add t4,t4,a6
vle32.v v14, (t4)
add t5,t5,a6
vfadd.vv v14,v6,v14
vse32.v v14, (t5)
vsetvli zero, zero, e16, m1, ta, ma
j .ukr0_cases_end
.ukr0_case3:
add t4,a3,0
add t5,a3,0
flw f0, 0(a4)
vle32.v v8, (t4)
vsetvli zero, zero, e32, m2, ta, ma
vfmacc.vf v8,f0,v0
vse32.v v8, (t5)
add t4,t4,a6
vle32.v v10, (t4)
add t5,t5,a6
vfmacc.vf v10,f0,v2
vse32.v v10, (t5)
add t4,t4,a6
vle32.v v12, (t4)
add t5,t5,a6
vfmacc.vf v12,f0,v4
vse32.v v12, (t5)
add t4,t4,a6
vle32.v v14, (t4)
add t5,t5,a6
vfmacc.vf v14,f0,v6
vse32.v v14, (t5)
vsetvli zero, zero, e16, m1, ta, ma
j .ukr0_cases_end
.ukr0_case4:
add t4,a3,0
add t5,a3,0
flw f0, 0(a5)
vle32.v v8, (t4)
vsetvli zero, zero, e32, m2, ta, ma
vfmacc.vf v0,f0,v8
vse32.v v0, (t5)
add t4,t4,a6
vle32.v v10, (t4)
add t5,t5,a6
vfmacc.vf v2,f0,v10
vse32.v v2, (t5)
add t4,t4,a6
vle32.v v12, (t4)
add t5,t5,a6
vfmacc.vf v4,f0,v12
vse32.v v4, (t5)
add t4,t4,a6
vle32.v v14, (t4)
add t5,t5,a6
vfmacc.vf v6,f0,v14
vse32.v v6, (t5)
vsetvli zero, zero, e16, m1, ta, ma
j .ukr0_cases_end
.ukr0_case5:
add t4,a3,0
add t5,a3,0
flw f0, 0(a5)
vle32.v v8, (t4)
vsetvli zero, zero, e32, m2, ta, ma
flw f1, 0(a4)
vfmul.vf v8,v8,f0
vfmacc.vf v8,f1,v0
vse32.v v8, (t5)
add t4,t4,a6
vle32.v v10, (t4)
add t5,t5,a6
vfmul.vf v10,v10,f0
vfmacc.vf v10,f1,v2
vse32.v v10, (t5)
add t4,t4,a6
vle32.v v12, (t4)
add t5,t5,a6
vfmul.vf v12,v12,f0
vfmacc.vf v12,f1,v4
vse32.v v12, (t5)
add t4,t4,a6
vle32.v v14, (t4)
add t5,t5,a6
vfmul.vf v14,v14,f0
vfmacc.vf v14,f1,v6
vse32.v v14, (t5)
vsetvli zero, zero, e16, m1, ta, ma
j .ukr0_cases_end
.ukr0_case6:
add t4,a3,0
vsse32.v v0, (t4), a7
add t4,t4,a6
vsse32.v v2, (t4), a7
add t4,t4,a6
vsse32.v v4, (t4), a7
add t4,t4,a6
vsse32.v v6, (t4), a7
j .ukr0_cases_end
.ukr0_case7:
add t4,a3,0
flw f0, 0(a4)
vsetvli zero, zero, e32, m2, ta, ma
vfmul.vf v8,v0,f0
vfmul.vf v10,v2,f0
vfmul.vf v12,v4,f0
vfmul.vf v14,v6,f0
vsse32.v v8, (t4), a7
add t4,t4,a6
vsse32.v v10, (t4), a7
add t4,t4,a6
vsse32.v v12, (t4), a7
add t4,t4,a6
vsse32.v v14, (t4), a7
vsetvli zero, zero, e16, m1, ta, ma
j .ukr0_cases_end
.ukr0_case8:
add t4,a3,0
vlse32.v v8, (t4), a7
vsetvli zero, zero, e32, m2, ta, ma
vfadd.vv v8,v0,v8
vsse32.v v8, (a3), a7
add t4,t4,a6
vlse32.v v10, (t4), a7
add a3,a3,a6
vfadd.vv v10,v2,v10
vsse32.v v10, (a3), a7
add t4,t4,a6
vlse32.v v12, (t4), a7
add a3,a3,a6
vfadd.vv v12,v4,v12
vsse32.v v12, (a3), a7
add t4,t4,a6
vlse32.v v14, (t4), a7
add a3,a3,a6
vfadd.vv v14,v6,v14
vsse32.v v14, (a3), a7
vsetvli zero, zero, e16, m1, ta, ma
j .ukr0_cases_end
.ukr0_case9:
add t4,a3,0
vlse32.v v8, (t4), a7
flw f0, 0(a4)
vsetvli zero, zero, e32, m2, ta, ma
vfmacc.vf v8,f0,v0
vsse32.v v8, (a3), a7
add t4,t4,a6
vlse32.v v10, (t4), a7
add a3,a3,a6
vfmacc.vf v10,f0,v2
vsse32.v v10, (a3), a7
add t4,t4,a6
vlse32.v v12, (t4), a7
add a3,a3,a6
vfmacc.vf v12,f0,v4
vsse32.v v12, (a3), a7
add t4,t4,a6
vlse32.v v14, (t4), a7
add a3,a3,a6
vfmacc.vf v14,f0,v6
vsse32.v v14, (a3), a7
vsetvli zero, zero, e16, m1, ta, ma
j .ukr0_cases_end
.ukr0_case10:
add t4,a3,0
vlse32.v v8, (t4), a7
flw f0, 0(a5)
vsetvli zero, zero, e32, m2, ta, ma
vfmacc.vf v0,f0,v8
vsse32.v v0, (a3), a7
add t4,t4,a6
vlse32.v v10, (t4), a7
add a3,a3,a6
vfmacc.vf v2,f0,v10
vsse32.v v2, (a3), a7
add t4,t4,a6
vlse32.v v12, (t4), a7
add a3,a3,a6
vfmacc.vf v4,f0,v12
vsse32.v v4, (a3), a7
add t4,t4,a6
vlse32.v v14, (t4), a7
add a3,a3,a6
vfmacc.vf v6,f0,v14
vsse32.v v6, (a3), a7
vsetvli zero, zero, e16, m1, ta, ma
j .ukr0_cases_end
.ukr0_case11:
add t4,a3,0
vlse32.v v8, (t4), a7
flw f0, 0(a5)
vsetvli zero, zero, e32, m2, ta, ma
flw f1, 0(a4)
vfmul.vf v8,v8,f0
vfmacc.vf v8,f1,v0
vsse32.v v8, (a3), a7
add t4,t4,a6
vlse32.v v10, (t4), a7
add a3,a3,a6
vfmul.vf v10,v10,f0
vfmacc.vf v10,f1,v2
vsse32.v v10, (a3), a7
add t4,t4,a6
vlse32.v v12, (t4), a7
add a3,a3,a6
vfmul.vf v12,v12,f0
vfmacc.vf v12,f1,v4
vsse32.v v12, (a3), a7
add t4,t4,a6
vlse32.v v14, (t4), a7
add a3,a3,a6
vfmul.vf v14,v14,f0
vfmacc.vf v14,f1,v6
vsse32.v v14, (a3), a7
vsetvli zero, zero, e16, m1, ta, ma
.ukr0_cases_end:
ld s1, 0(sp)
.cfi_restore s1
add sp,sp,16
.cfi_adjust_cfa_offset -16
ret
.cfi_endproc
.size gemmf16f16f32_rvv_vn_4x1v, .-gemmf16f16f32_rvv_vn_4x1v
.section .note.GNU-stack,"",%progbits
