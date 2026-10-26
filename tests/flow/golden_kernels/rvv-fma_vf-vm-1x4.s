.text
.global bli_dgemm_ukrgen_rvv_vm_1vx4_asm
.type bli_dgemm_ukrgen_rvv_vm_1vx4_asm, %function
bli_dgemm_ukrgen_rvv_vm_1vx4_asm:
.cfi_startproc
# a0 = k
# a1 = base(A)
# a2 = base(B)
# a3 = base(C)
# a4 = base(alpha)
# a5 = base(beta)
# a6 = stride(C,n)
vsetvli t0, zero, e64, m1, ta, ma
add t1,t0,0
slli t1,t1,3
add t2,t1,0
slli t2,t2,1
add t3,t1,0
slli t3,t3,2
add t4,a1,0
add a1,a1,t1
add t5,a2,0
add a2,a2,8
andi t6,a0,3
srli a0,a0,2
vmv.v.i v1,0
vmv.v.i v2,0
vmv.v.i v3,0
vmv.v.i v4,0
beq a0,zero,.ukr1_done
vle64.v v5, (t4)
fld f0, 0(t5)
fld f1, 0(a2)
fld f2, 16(t5)
fld f3, 16(a2)
add t5,t5,32
add a2,a2,32
add t4,t4,t2
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
vfmacc.vf v1,f0,v5
add a7,a1,t2
vfmacc.vf v2,f1,v5
vfmacc.vf v3,f2,v5
vfmacc.vf v4,f3,v5
vle64.v v6, (a1)
fld f4, 0(t5)
fld f5, 0(a2)
vle64.v v7, (t4)
fld f6, 16(t5)
add t4,t4,t3
fld f7, 16(a2)
add a1,a1,t3
fld f10, 32(t5)
vle64.v v8, (a7)
fld f11, 32(a2)
add a7,a7,t1
fld f12, 48(t5)
fld f13, 48(a2)
fld f14, 64(t5)
fld f15, 64(a2)
fld f16, 80(t5)
fld f17, 80(a2)
fld f0, 96(t5)
vle64.v v5, (a7)
vfmacc.vf v1,f4,v6
vfmacc.vf v2,f5,v6
vfmacc.vf v3,f6,v6
vfmacc.vf v4,f7,v6
fld f1, 96(a2)
fld f2, 112(t5)
fld f3, 112(a2)
add t5,t5,128
add a2,a2,128
vfmacc.vf v1,f10,v7
vfmacc.vf v2,f11,v7
vfmacc.vf v3,f12,v7
vfmacc.vf v4,f13,v7
vfmacc.vf v1,f14,v8
vfmacc.vf v2,f15,v8
vfmacc.vf v3,f16,v8
vfmacc.vf v4,f17,v8
bne a0,zero,.ukr1_loop
.ukr1_last:
vfmacc.vf v1,f0,v5
add a7,a1,t2
vfmacc.vf v2,f1,v5
vfmacc.vf v3,f2,v5
vfmacc.vf v4,f3,v5
vle64.v v6, (a1)
fld f4, 0(t5)
fld f5, 0(a2)
vle64.v v7, (t4)
fld f6, 16(t5)
vle64.v v8, (a7)
fld f7, 16(a2)
add t4,t4,t3
fld f10, 32(t5)
add a1,a1,t3
fld f11, 32(a2)
fld f12, 48(t5)
sub t4,t4,t1
sub t4,t4,t1
fld f13, 48(a2)
fld f14, 64(t5)
fld f15, 64(a2)
fld f16, 80(t5)
fld f17, 80(a2)
add t5,t5,96
add a2,a2,96
vfmacc.vf v1,f4,v6
vfmacc.vf v2,f5,v6
vfmacc.vf v3,f6,v6
vfmacc.vf v4,f7,v6
vfmacc.vf v1,f10,v7
vfmacc.vf v2,f11,v7
vfmacc.vf v3,f12,v7
vfmacc.vf v4,f13,v7
vfmacc.vf v1,f14,v8
vfmacc.vf v2,f15,v8
vfmacc.vf v3,f16,v8
vfmacc.vf v4,f17,v8
.ukr1_done:
beq t6,zero,.ukr1_taildone
.ukr1_tail:
add t6,t6,-1
vle64.v v5, (t4)
fld f0, 0(t5)
fld f1, 0(a2)
fld f2, 16(t5)
fld f3, 16(a2)
vfmacc.vf v1,f0,v5
vfmacc.vf v2,f1,v5
vfmacc.vf v3,f2,v5
vfmacc.vf v4,f3,v5
add t4,t4,t1
add a1,a1,t1
add t5,t5,32
add a2,a2,32
bne t6,zero,.ukr1_tail
.ukr1_taildone:
fld f0, 0(a5)
fcvt.d.w f1, zero
feq.d t4,f0,f1
beqz t4,.ukr0_try1
fld f0, 0(a4)
li t4,4607182418800017408
fmv.d.x f1,t4
feq.d t4,f0,f1
beqz t4,.ukr0_try1
j .ukr0_case0
.ukr0_try1:
fld f0, 0(a5)
fcvt.d.w f1, zero
feq.d t4,f0,f1
beqz t4,.ukr0_try2
j .ukr0_case1
.ukr0_try2:
fld f0, 0(a5)
li t4,4607182418800017408
fmv.d.x f1,t4
feq.d t4,f0,f1
beqz t4,.ukr0_try3
fld f0, 0(a4)
li t4,4607182418800017408
fmv.d.x f1,t4
feq.d t4,f0,f1
beqz t4,.ukr0_try3
j .ukr0_case2
.ukr0_try3:
fld f0, 0(a5)
li t4,4607182418800017408
fmv.d.x f1,t4
feq.d t4,f0,f1
beqz t4,.ukr0_try4
j .ukr0_case3
.ukr0_try4:
fld f0, 0(a4)
li t4,4607182418800017408
fmv.d.x f1,t4
feq.d t4,f0,f1
beqz t4,.ukr0_try5
j .ukr0_case4
.ukr0_try5:
j .ukr0_case5
.ukr0_try6:
j .ukr0_cases_end
.ukr0_case0:
add t4,a3,0
add t5,t4,0
add t5,t5,a6
vse64.v v1, (t4)
add t6,t4,0
add t6,t6,a6
add t6,t6,a6
add a0,t4,0
add a0,a0,a6
add a0,a0,a6
add a0,a0,a6
vse64.v v2, (t5)
vse64.v v3, (t6)
vse64.v v4, (a0)
j .ukr0_cases_end
.ukr0_case1:
add t4,a3,0
fld f0, 0(a4)
add t5,t4,0
add t5,t5,a6
add t6,t4,0
add t6,t6,a6
add t6,t6,a6
add a0,t4,0
add a0,a0,a6
add a0,a0,a6
add a0,a0,a6
vfmul.vf v5,v1,f0
vfmul.vf v1,v2,f0
vfmul.vf v2,v3,f0
vfmul.vf v3,v4,f0
vse64.v v5, (t4)
vse64.v v1, (t5)
vse64.v v2, (t6)
vse64.v v3, (a0)
j .ukr0_cases_end
.ukr0_case2:
add t4,a3,0
add t5,t4,0
add t5,t5,a6
vle64.v v5, (t4)
add t6,t4,0
add t6,t6,a6
add t6,t6,a6
add a0,a3,0
add a0,a0,a6
vle64.v v6, (t5)
add a1,a3,0
add a1,a1,a6
add a1,a1,a6
vle64.v v7, (t6)
vfadd.vv v5,v1,v5
add a2,t4,0
add a2,a2,a6
add a2,a2,a6
add a2,a2,a6
vfadd.vv v6,v2,v6
vfadd.vv v7,v3,v7
vse64.v v5, (a3)
add a7,a3,0
add a7,a7,a6
add a7,a7,a6
add a7,a7,a6
vle64.v v1, (a2)
vse64.v v6, (a0)
vse64.v v7, (a1)
vfadd.vv v1,v4,v1
vse64.v v1, (a7)
j .ukr0_cases_end
.ukr0_case3:
add t4,a3,0
add t5,t4,0
add t5,t5,a6
vle64.v v5, (t4)
add t6,t4,0
add t6,t6,a6
add t6,t6,a6
fld f0, 0(a4)
add a0,a3,0
add a0,a0,a6
vle64.v v6, (t5)
add a1,a3,0
add a1,a1,a6
add a1,a1,a6
vle64.v v7, (t6)
vfmacc.vf v5,f0,v1
add a2,t4,0
add a2,a2,a6
add a2,a2,a6
add a2,a2,a6
vfmacc.vf v6,f0,v2
vfmacc.vf v7,f0,v3
vse64.v v5, (a3)
add a7,a3,0
add a7,a7,a6
add a7,a7,a6
add a7,a7,a6
vle64.v v1, (a2)
vse64.v v6, (a0)
vse64.v v7, (a1)
vfmacc.vf v1,f0,v4
vse64.v v1, (a7)
j .ukr0_cases_end
.ukr0_case4:
add t4,a3,0
add t5,t4,0
add t5,t5,a6
vle64.v v5, (t4)
add t6,t4,0
add t6,t6,a6
add t6,t6,a6
fld f0, 0(a5)
add a0,a3,0
add a0,a0,a6
vle64.v v6, (t5)
add a1,a3,0
add a1,a1,a6
add a1,a1,a6
vle64.v v7, (t6)
vfmacc.vf v1,f0,v5
add a2,t4,0
add a2,a2,a6
add a2,a2,a6
add a2,a2,a6
vfmacc.vf v2,f0,v6
vfmacc.vf v3,f0,v7
vse64.v v1, (a3)
add a7,a3,0
add a7,a7,a6
add a7,a7,a6
add a7,a7,a6
vle64.v v1, (a2)
vse64.v v2, (a0)
vse64.v v3, (a1)
vfmacc.vf v4,f0,v1
vse64.v v4, (a7)
j .ukr0_cases_end
.ukr0_case5:
add t4,a3,0
add t5,t4,0
add t5,t5,a6
vle64.v v5, (t4)
add t6,t4,0
add t6,t6,a6
add t6,t6,a6
fld f0, 0(a5)
fld f1, 0(a4)
add a0,a3,0
add a0,a0,a6
vle64.v v6, (t5)
vle64.v v7, (t6)
vfmul.vf v5,v5,f0
vfmul.vf v6,v6,f0
vfmul.vf v7,v7,f0
vfmacc.vf v5,f1,v1
add a1,a3,0
add a1,a1,a6
add a1,a1,a6
vfmacc.vf v6,f1,v2
vfmacc.vf v7,f1,v3
vse64.v v5, (a3)
add a2,t4,0
add a2,a2,a6
add a2,a2,a6
add a2,a2,a6
add a7,a3,0
add a7,a7,a6
add a7,a7,a6
add a7,a7,a6
vse64.v v6, (a0)
vle64.v v1, (a2)
vse64.v v7, (a1)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v4
vse64.v v1, (a7)
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dgemm_ukrgen_rvv_vm_1vx4_asm, .-bli_dgemm_ukrgen_rvv_vm_1vx4_asm
.section .note.GNU-stack,"",%progbits
