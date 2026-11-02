.text
.global bli_dgemm_ukrgen_rvv_vm_2vx14_asm
.type bli_dgemm_ukrgen_rvv_vm_2vx14_asm, %function
bli_dgemm_ukrgen_rvv_vm_2vx14_asm:
.cfi_startproc
add sp,sp,-144
.cfi_adjust_cfa_offset 144
sd s1, 0(sp)
.cfi_rel_offset s1, 0
sd s2, 8(sp)
.cfi_rel_offset s2, 8
sd s3, 16(sp)
.cfi_rel_offset s3, 16
sd s4, 24(sp)
.cfi_rel_offset s4, 24
sd s5, 32(sp)
.cfi_rel_offset s5, 32
sd s6, 40(sp)
.cfi_rel_offset s6, 40
sd s7, 48(sp)
.cfi_rel_offset s7, 48
sd s8, 56(sp)
.cfi_rel_offset s8, 56
sd s9, 64(sp)
.cfi_rel_offset s9, 64
fsd f8, 72(sp)
.cfi_rel_offset f8, 72
fsd f9, 80(sp)
.cfi_rel_offset f9, 80
fsd f18, 88(sp)
.cfi_rel_offset f18, 88
fsd f19, 96(sp)
.cfi_rel_offset f19, 96
fsd f20, 104(sp)
.cfi_rel_offset f20, 104
fsd f21, 112(sp)
.cfi_rel_offset f21, 112
fsd f22, 120(sp)
.cfi_rel_offset f22, 120
fsd f23, 128(sp)
.cfi_rel_offset f23, 128
# a0 = k
# a1 = base(A)
# a2 = base(B)
# a3 = base(C)
# a4 = base(alpha)
# a5 = base(beta)
# a6 = stride(C,m)
# a7 = stride(C,n)
vsetvli t0, zero, e64, m1, ta, ma
slli t1,t0,3
slli t2,t1,1
slli t3,t1,3
mul t4,t0,a6
add t5,a1,0
add a1,a1,t1
add t6,a2,0
add a2,a2,8
andi s1,a0,3
srli a0,a0,2
vmv.v.i v1,0
vmv.v.i v2,0
vmv.v.i v3,0
vmv.v.i v4,0
vmv.v.i v5,0
vmv.v.i v6,0
vmv.v.i v7,0
vmv.v.i v8,0
vmv.v.i v9,0
vmv.v.i v10,0
vmv.v.i v11,0
vmv.v.i v12,0
vmv.v.i v13,0
vmv.v.i v14,0
vmv.v.i v15,0
vmv.v.i v16,0
vmv.v.i v17,0
vmv.v.i v18,0
vmv.v.i v19,0
vmv.v.i v20,0
vmv.v.i v21,0
vmv.v.i v22,0
vmv.v.i v23,0
vmv.v.i v24,0
vmv.v.i v25,0
vmv.v.i v26,0
vmv.v.i v27,0
vmv.v.i v28,0
beq a0,zero,.ukr1_done
vle64.v v29, (t5)
fld f0, 0(t6)
vle64.v v30, (a1)
fld f1, 0(a2)
fld f2, 16(t6)
fld f3, 16(a2)
fld f4, 32(t6)
fld f5, 32(a2)
fld f6, 48(t6)
fld f7, 48(a2)
fld f10, 64(t6)
fld f11, 64(a2)
fld f12, 80(t6)
fld f13, 80(a2)
fld f14, 96(t6)
fld f15, 96(a2)
add t5,t5,t2
add t6,t6,112
add a2,a2,112
add a1,a1,t2
add a0,a0,-1
beq a0,zero,.ukr1_last
.ukr1_loop:
add a0,a0,-1
vfmacc.vf v1,f0,v29
add s2,t5,t2
vfmacc.vf v2,f1,v29
vfmacc.vf v3,f2,v29
vfmacc.vf v4,f3,v29
vfmacc.vf v5,f4,v29
vle64.v v31, (t5)
fld f16, 0(t6)
vfmacc.vf v6,f5,v29
add t5,t5,t3
fld f17, 0(a2)
vle64.v v0, (a1)
vfmacc.vf v7,f6,v29
add a1,a1,t3
fld f28, 16(t6)
vfmacc.vf v8,f7,v29
fld f29, 16(a2)
vfmacc.vf v9,f10,v29
fld f30, 32(t6)
vfmacc.vf v10,f11,v29
fld f31, 32(a2)
vfmacc.vf v11,f12,v29
fld f8, 48(t6)
vfmacc.vf v12,f13,v29
fld f9, 48(a2)
vfmacc.vf v13,f14,v29
fld f18, 64(t6)
vfmacc.vf v14,f15,v29
fld f19, 64(a2)
vfmacc.vf v15,f0,v30
fld f20, 80(t6)
vfmacc.vf v16,f1,v30
fld f21, 80(a2)
vfmacc.vf v17,f2,v30
fld f22, 96(t6)
vfmacc.vf v18,f3,v30
fld f23, 96(a2)
vfmacc.vf v19,f4,v30
vfmacc.vf v20,f5,v30
vfmacc.vf v21,f6,v30
vle64.v v29, (s2)
vfmacc.vf v22,f7,v30
add s2,s2,t1
fld f0, 112(t6)
vfmacc.vf v23,f10,v30
fld f1, 112(a2)
vfmacc.vf v24,f11,v30
fld f2, 128(t6)
vfmacc.vf v25,f12,v30
fld f3, 128(a2)
vfmacc.vf v26,f13,v30
fld f4, 144(t6)
vfmacc.vf v27,f14,v30
fld f5, 144(a2)
vfmacc.vf v28,f15,v30
fld f6, 160(t6)
vfmacc.vf v1,f16,v31
fld f7, 160(a2)
vfmacc.vf v2,f17,v31
fld f10, 176(t6)
vfmacc.vf v3,f28,v31
fld f11, 176(a2)
vfmacc.vf v4,f29,v31
fld f12, 192(t6)
vfmacc.vf v5,f30,v31
fld f13, 192(a2)
vfmacc.vf v6,f31,v31
fld f14, 208(t6)
vle64.v v30, (s2)
vfmacc.vf v7,f8,v31
add s2,s2,t1
fld f15, 208(a2)
vfmacc.vf v8,f9,v31
vfmacc.vf v9,f18,v31
vfmacc.vf v10,f19,v31
vfmacc.vf v11,f20,v31
vfmacc.vf v12,f21,v31
vfmacc.vf v13,f22,v31
vfmacc.vf v14,f23,v31
vfmacc.vf v15,f16,v0
vfmacc.vf v16,f17,v0
vfmacc.vf v17,f28,v0
vfmacc.vf v18,f29,v0
vfmacc.vf v19,f30,v0
vfmacc.vf v20,f31,v0
vfmacc.vf v21,f8,v0
vfmacc.vf v22,f9,v0
vfmacc.vf v23,f18,v0
vfmacc.vf v24,f19,v0
vfmacc.vf v25,f20,v0
vfmacc.vf v26,f21,v0
vle64.v v31, (s2)
vfmacc.vf v27,f22,v0
add s2,s2,t1
fld f16, 224(t6)
vfmacc.vf v28,f23,v0
fld f17, 224(a2)
vfmacc.vf v1,f0,v29
fld f28, 240(t6)
vfmacc.vf v2,f1,v29
fld f29, 240(a2)
vfmacc.vf v3,f2,v29
fld f30, 256(t6)
vfmacc.vf v4,f3,v29
fld f31, 256(a2)
vfmacc.vf v5,f4,v29
fld f8, 272(t6)
vfmacc.vf v6,f5,v29
fld f9, 272(a2)
vle64.v v0, (s2)
vfmacc.vf v7,f6,v29
add s2,s2,t1
fld f18, 288(t6)
vfmacc.vf v8,f7,v29
fld f19, 288(a2)
vfmacc.vf v9,f10,v29
fld f20, 304(t6)
vfmacc.vf v10,f11,v29
fld f21, 304(a2)
vfmacc.vf v11,f12,v29
fld f22, 320(t6)
vfmacc.vf v12,f13,v29
fld f23, 320(a2)
vfmacc.vf v13,f14,v29
vfmacc.vf v14,f15,v29
vfmacc.vf v15,f0,v30
vfmacc.vf v16,f1,v30
vfmacc.vf v17,f2,v30
vfmacc.vf v18,f3,v30
vfmacc.vf v19,f4,v30
vfmacc.vf v20,f5,v30
vfmacc.vf v21,f6,v30
vfmacc.vf v22,f7,v30
vfmacc.vf v23,f10,v30
vfmacc.vf v24,f11,v30
vfmacc.vf v25,f12,v30
vfmacc.vf v26,f13,v30
vle64.v v29, (s2)
vfmacc.vf v27,f14,v30
add s2,s2,t1
fld f0, 336(t6)
vfmacc.vf v28,f15,v30
fld f1, 336(a2)
vfmacc.vf v1,f16,v31
fld f2, 352(t6)
vfmacc.vf v2,f17,v31
fld f3, 352(a2)
vfmacc.vf v3,f28,v31
fld f4, 368(t6)
vfmacc.vf v4,f29,v31
fld f5, 368(a2)
vfmacc.vf v5,f30,v31
fld f6, 384(t6)
vfmacc.vf v6,f31,v31
fld f7, 384(a2)
vle64.v v30, (s2)
vfmacc.vf v7,f8,v31
fld f10, 400(t6)
vfmacc.vf v8,f9,v31
fld f11, 400(a2)
vfmacc.vf v9,f18,v31
fld f12, 416(t6)
vfmacc.vf v10,f19,v31
fld f13, 416(a2)
vfmacc.vf v11,f20,v31
fld f14, 432(t6)
vfmacc.vf v12,f21,v31
add t6,t6,448
fld f15, 432(a2)
vfmacc.vf v13,f22,v31
add a2,a2,448
vfmacc.vf v14,f23,v31
vfmacc.vf v15,f16,v0
vfmacc.vf v16,f17,v0
vfmacc.vf v17,f28,v0
vfmacc.vf v18,f29,v0
vfmacc.vf v19,f30,v0
vfmacc.vf v20,f31,v0
vfmacc.vf v21,f8,v0
vfmacc.vf v22,f9,v0
vfmacc.vf v23,f18,v0
vfmacc.vf v24,f19,v0
vfmacc.vf v25,f20,v0
vfmacc.vf v26,f21,v0
vfmacc.vf v27,f22,v0
vfmacc.vf v28,f23,v0
bne a0,zero,.ukr1_loop
.ukr1_last:
vfmacc.vf v1,f0,v29
add s2,t5,t2
vfmacc.vf v2,f1,v29
vfmacc.vf v3,f2,v29
vfmacc.vf v4,f3,v29
vfmacc.vf v5,f4,v29
vle64.v v31, (t5)
fld f16, 0(t6)
vfmacc.vf v6,f5,v29
add t5,t5,t3
fld f17, 0(a2)
vle64.v v0, (a1)
vfmacc.vf v7,f6,v29
add a1,a1,t3
fld f28, 16(t6)
sub t5,t5,t1
vfmacc.vf v8,f7,v29
fld f29, 16(a2)
sub a1,a1,t1
vfmacc.vf v9,f10,v29
sub t5,t5,t1
fld f30, 32(t6)
vfmacc.vf v10,f11,v29
sub a1,a1,t1
fld f31, 32(a2)
vfmacc.vf v11,f12,v29
fld f8, 48(t6)
vfmacc.vf v12,f13,v29
fld f9, 48(a2)
vfmacc.vf v13,f14,v29
fld f18, 64(t6)
vfmacc.vf v14,f15,v29
fld f19, 64(a2)
vfmacc.vf v15,f0,v30
fld f20, 80(t6)
vfmacc.vf v16,f1,v30
fld f21, 80(a2)
vfmacc.vf v17,f2,v30
fld f22, 96(t6)
vfmacc.vf v18,f3,v30
fld f23, 96(a2)
vfmacc.vf v19,f4,v30
vfmacc.vf v20,f5,v30
vfmacc.vf v21,f6,v30
vle64.v v29, (s2)
vfmacc.vf v22,f7,v30
add s2,s2,t1
fld f0, 112(t6)
vfmacc.vf v23,f10,v30
fld f1, 112(a2)
vfmacc.vf v24,f11,v30
fld f2, 128(t6)
vfmacc.vf v25,f12,v30
fld f3, 128(a2)
vfmacc.vf v26,f13,v30
fld f4, 144(t6)
vfmacc.vf v27,f14,v30
fld f5, 144(a2)
vfmacc.vf v28,f15,v30
fld f6, 160(t6)
vfmacc.vf v1,f16,v31
fld f7, 160(a2)
vfmacc.vf v2,f17,v31
fld f10, 176(t6)
vfmacc.vf v3,f28,v31
fld f11, 176(a2)
vfmacc.vf v4,f29,v31
fld f12, 192(t6)
vfmacc.vf v5,f30,v31
fld f13, 192(a2)
vfmacc.vf v6,f31,v31
fld f14, 208(t6)
vle64.v v30, (s2)
vfmacc.vf v7,f8,v31
add s2,s2,t1
fld f15, 208(a2)
vfmacc.vf v8,f9,v31
vfmacc.vf v9,f18,v31
vfmacc.vf v10,f19,v31
vfmacc.vf v11,f20,v31
vfmacc.vf v12,f21,v31
vfmacc.vf v13,f22,v31
vfmacc.vf v14,f23,v31
vfmacc.vf v15,f16,v0
vfmacc.vf v16,f17,v0
vfmacc.vf v17,f28,v0
vfmacc.vf v18,f29,v0
vfmacc.vf v19,f30,v0
vfmacc.vf v20,f31,v0
vfmacc.vf v21,f8,v0
vfmacc.vf v22,f9,v0
vfmacc.vf v23,f18,v0
vfmacc.vf v24,f19,v0
vfmacc.vf v25,f20,v0
vfmacc.vf v26,f21,v0
vle64.v v31, (s2)
vfmacc.vf v27,f22,v0
add s2,s2,t1
fld f16, 224(t6)
vfmacc.vf v28,f23,v0
fld f17, 224(a2)
vfmacc.vf v1,f0,v29
fld f28, 240(t6)
vfmacc.vf v2,f1,v29
fld f29, 240(a2)
vfmacc.vf v3,f2,v29
fld f30, 256(t6)
vfmacc.vf v4,f3,v29
fld f31, 256(a2)
vfmacc.vf v5,f4,v29
fld f8, 272(t6)
vfmacc.vf v6,f5,v29
fld f9, 272(a2)
vle64.v v0, (s2)
vfmacc.vf v7,f6,v29
fld f18, 288(t6)
vfmacc.vf v8,f7,v29
fld f19, 288(a2)
vfmacc.vf v9,f10,v29
fld f20, 304(t6)
vfmacc.vf v10,f11,v29
fld f21, 304(a2)
vfmacc.vf v11,f12,v29
fld f22, 320(t6)
vfmacc.vf v12,f13,v29
add t6,t6,336
fld f23, 320(a2)
vfmacc.vf v13,f14,v29
add a2,a2,336
vfmacc.vf v14,f15,v29
vfmacc.vf v15,f0,v30
vfmacc.vf v16,f1,v30
vfmacc.vf v17,f2,v30
vfmacc.vf v18,f3,v30
vfmacc.vf v19,f4,v30
vfmacc.vf v20,f5,v30
vfmacc.vf v21,f6,v30
vfmacc.vf v22,f7,v30
vfmacc.vf v23,f10,v30
vfmacc.vf v24,f11,v30
vfmacc.vf v25,f12,v30
vfmacc.vf v26,f13,v30
vfmacc.vf v27,f14,v30
vfmacc.vf v28,f15,v30
vfmacc.vf v1,f16,v31
vfmacc.vf v2,f17,v31
vfmacc.vf v3,f28,v31
vfmacc.vf v4,f29,v31
vfmacc.vf v5,f30,v31
vfmacc.vf v6,f31,v31
vfmacc.vf v7,f8,v31
vfmacc.vf v8,f9,v31
vfmacc.vf v9,f18,v31
vfmacc.vf v10,f19,v31
vfmacc.vf v11,f20,v31
vfmacc.vf v12,f21,v31
vfmacc.vf v13,f22,v31
vfmacc.vf v14,f23,v31
vfmacc.vf v15,f16,v0
vfmacc.vf v16,f17,v0
vfmacc.vf v17,f28,v0
vfmacc.vf v18,f29,v0
vfmacc.vf v19,f30,v0
vfmacc.vf v20,f31,v0
vfmacc.vf v21,f8,v0
vfmacc.vf v22,f9,v0
vfmacc.vf v23,f18,v0
vfmacc.vf v24,f19,v0
vfmacc.vf v25,f20,v0
vfmacc.vf v26,f21,v0
vfmacc.vf v27,f22,v0
vfmacc.vf v28,f23,v0
.ukr1_done:
beq s1,zero,.ukr1_taildone
.ukr1_tail:
add s1,s1,-1
vle64.v v29, (t5)
fld f0, 0(t6)
fld f1, 0(a2)
vle64.v v30, (a1)
fld f2, 16(t6)
fld f3, 16(a2)
fld f4, 32(t6)
fld f5, 32(a2)
fld f6, 48(t6)
fld f7, 48(a2)
fld f10, 64(t6)
fld f11, 64(a2)
fld f12, 80(t6)
fld f13, 80(a2)
fld f14, 96(t6)
vfmacc.vf v1,f0,v29
vfmacc.vf v2,f1,v29
vfmacc.vf v3,f2,v29
vfmacc.vf v4,f3,v29
vfmacc.vf v5,f4,v29
fld f15, 96(a2)
vfmacc.vf v6,f5,v29
vfmacc.vf v7,f6,v29
vfmacc.vf v8,f7,v29
vfmacc.vf v9,f10,v29
vfmacc.vf v10,f11,v29
vfmacc.vf v11,f12,v29
vfmacc.vf v12,f13,v29
vfmacc.vf v13,f14,v29
vfmacc.vf v15,f0,v30
vfmacc.vf v16,f1,v30
vfmacc.vf v17,f2,v30
vfmacc.vf v18,f3,v30
vfmacc.vf v14,f15,v29
vfmacc.vf v19,f4,v30
vfmacc.vf v20,f5,v30
vfmacc.vf v21,f6,v30
vfmacc.vf v22,f7,v30
vfmacc.vf v23,f10,v30
vfmacc.vf v24,f11,v30
vfmacc.vf v25,f12,v30
vfmacc.vf v26,f13,v30
vfmacc.vf v27,f14,v30
vfmacc.vf v28,f15,v30
add t5,t5,t2
add a1,a1,t2
add t6,t6,112
add a2,a2,112
bne s1,zero,.ukr1_tail
.ukr1_taildone:
add t5,a6,0
add t5,t5,-8
beq t5,zero,.ukr0_ok0_0
j .ukr0_try1
.ukr0_ok0_0:
fld f0, 0(a5)
fcvt.d.w f1, zero
feq.d t5,f0,f1
beqz t5,.ukr0_try1
fld f0, 0(a4)
li t5,4607182418800017408
fmv.d.x f1,t5
feq.d t5,f0,f1
beqz t5,.ukr0_try1
j .ukr0_case0
.ukr0_try1:
add t5,a6,0
add t5,t5,-8
beq t5,zero,.ukr0_ok1_0
j .ukr0_try2
.ukr0_ok1_0:
fld f0, 0(a5)
fcvt.d.w f1, zero
feq.d t5,f0,f1
beqz t5,.ukr0_try2
j .ukr0_case1
.ukr0_try2:
add t5,a6,0
add t5,t5,-8
beq t5,zero,.ukr0_ok2_0
j .ukr0_try3
.ukr0_ok2_0:
fld f0, 0(a5)
li t5,4607182418800017408
fmv.d.x f1,t5
feq.d t5,f0,f1
beqz t5,.ukr0_try3
fld f0, 0(a4)
li t5,4607182418800017408
fmv.d.x f1,t5
feq.d t5,f0,f1
beqz t5,.ukr0_try3
j .ukr0_case2
.ukr0_try3:
add t5,a6,0
add t5,t5,-8
beq t5,zero,.ukr0_ok3_0
j .ukr0_try4
.ukr0_ok3_0:
fld f0, 0(a5)
li t5,4607182418800017408
fmv.d.x f1,t5
feq.d t5,f0,f1
beqz t5,.ukr0_try4
j .ukr0_case3
.ukr0_try4:
add t5,a6,0
add t5,t5,-8
beq t5,zero,.ukr0_ok4_0
j .ukr0_try5
.ukr0_ok4_0:
fld f0, 0(a4)
li t5,4607182418800017408
fmv.d.x f1,t5
feq.d t5,f0,f1
beqz t5,.ukr0_try5
j .ukr0_case4
.ukr0_try5:
add t5,a6,0
add t5,t5,-8
beq t5,zero,.ukr0_ok5_0
j .ukr0_try6
.ukr0_ok5_0:
j .ukr0_case5
.ukr0_try6:
fld f0, 0(a5)
fcvt.d.w f1, zero
feq.d t5,f0,f1
beqz t5,.ukr0_try7
fld f0, 0(a4)
li t5,4607182418800017408
fmv.d.x f1,t5
feq.d t5,f0,f1
beqz t5,.ukr0_try7
j .ukr0_case6
.ukr0_try7:
fld f0, 0(a5)
fcvt.d.w f1, zero
feq.d t5,f0,f1
beqz t5,.ukr0_try8
j .ukr0_case7
.ukr0_try8:
fld f0, 0(a5)
li t5,4607182418800017408
fmv.d.x f1,t5
feq.d t5,f0,f1
beqz t5,.ukr0_try9
fld f0, 0(a4)
li t5,4607182418800017408
fmv.d.x f1,t5
feq.d t5,f0,f1
beqz t5,.ukr0_try9
j .ukr0_case8
.ukr0_try9:
fld f0, 0(a5)
li t5,4607182418800017408
fmv.d.x f1,t5
feq.d t5,f0,f1
beqz t5,.ukr0_try10
j .ukr0_case9
.ukr0_try10:
fld f0, 0(a4)
li t5,4607182418800017408
fmv.d.x f1,t5
feq.d t5,f0,f1
beqz t5,.ukr0_try11
j .ukr0_case10
.ukr0_try11:
j .ukr0_case11
.ukr0_try12:
j .ukr0_cases_end
.ukr0_case0:
add t5,a3,0
add t6,a3,0
add a0,t5,a7
vse64.v v1, (t5)
add a1,t5,a7
add a2,t5,a7
add s1,t5,0
vse64.v v2, (a0)
add s2,t5,0
add a1,a1,a7
add a2,a2,a7
li s3,5
li s4,4
vse64.v v3, (a1)
add a2,a2,a7
mul s3,a7,s3
mul s4,a7,s4
vse64.v v4, (a2)
add s2,s2,s3
add s1,s1,s4
vse64.v v6, (s2)
add s2,s2,a7
vse64.v v5, (s1)
vse64.v v7, (s2)
add s2,s2,a7
vse64.v v8, (s2)
add s2,s2,a7
add s3,t5,t1
vse64.v v9, (s2)
add s2,s2,a7
vse64.v v15, (s3)
add s3,a0,t1
vse64.v v10, (s2)
add s2,s2,a7
vse64.v v16, (s3)
add s3,a1,t1
vse64.v v11, (s2)
add s2,s2,a7
vse64.v v17, (s3)
add s3,a2,t1
vse64.v v12, (s2)
add s2,s2,a7
vse64.v v18, (s3)
add s3,s1,t1
vse64.v v13, (s2)
add s2,s2,a7
vse64.v v19, (s3)
vse64.v v14, (s2)
li s4,8
mul s4,a7,s4
sub s2,s2,s4
add s3,s2,t1
add s2,s2,a7
vse64.v v20, (s3)
add s3,s2,t1
add s2,s2,a7
vse64.v v21, (s3)
add s3,s2,t1
add s2,s2,a7
vse64.v v22, (s3)
add s3,s2,t1
add s2,s2,a7
vse64.v v23, (s3)
add s3,s2,t1
add s2,s2,a7
vse64.v v24, (s3)
add s3,s2,t1
add s2,s2,a7
vse64.v v25, (s3)
add s3,s2,t1
add s2,s2,a7
vse64.v v26, (s3)
add s3,s2,t1
add s2,s2,a7
vse64.v v27, (s3)
add s3,s2,t1
vse64.v v28, (s3)
j .ukr0_cases_end
.ukr0_case1:
add t5,a3,0
add t6,a3,0
fld f0, 0(a4)
add a0,t5,a7
add a1,t5,a7
add a2,t5,a7
add a1,a1,a7
add a2,a2,a7
vfmul.vf v29,v1,f0
add a2,a2,a7
vfmul.vf v1,v2,f0
vfmul.vf v2,v3,f0
vfmul.vf v3,v4,f0
vse64.v v29, (t5)
add s1,t5,0
vfmul.vf v4,v5,f0
vse64.v v1, (a0)
li s2,4
vse64.v v2, (a1)
vfmul.vf v1,v6,f0
add s3,t5,0
vse64.v v3, (a2)
vfmul.vf v2,v7,f0
mul s2,a7,s2
vfmul.vf v3,v8,f0
li s4,5
add s1,s1,s2
mul s4,a7,s4
add s3,s3,s4
vse64.v v4, (s1)
vfmul.vf v4,v9,f0
vfmul.vf v5,v10,f0
vse64.v v1, (s3)
vfmul.vf v1,v11,f0
add s3,s3,a7
vse64.v v2, (s3)
vfmul.vf v2,v12,f0
add s3,s3,a7
vse64.v v3, (s3)
vfmul.vf v3,v13,f0
add s3,s3,a7
vse64.v v4, (s3)
vfmul.vf v4,v14,f0
add s3,s3,a7
vse64.v v5, (s3)
vfmul.vf v5,v15,f0
add s3,s3,a7
add s2,t5,t1
vse64.v v1, (s3)
vfmul.vf v1,v16,f0
add s3,s3,a7
vse64.v v2, (s3)
vfmul.vf v2,v17,f0
add s3,s3,a7
vse64.v v3, (s3)
vfmul.vf v3,v18,f0
add s3,s3,a7
vse64.v v5, (s2)
add s2,a0,t1
vse64.v v4, (s3)
vfmul.vf v4,v19,f0
li s4,8
vfmul.vf v5,v20,f0
vse64.v v1, (s2)
add s2,a1,t1
mul s4,a7,s4
vse64.v v2, (s2)
vfmul.vf v1,v21,f0
add s2,a2,t1
sub s3,s3,s4
vse64.v v3, (s2)
add s2,s1,t1
vfmul.vf v2,v22,f0
vse64.v v4, (s2)
vfmul.vf v3,v23,f0
add s2,s3,t1
add s3,s3,a7
vse64.v v5, (s2)
vfmul.vf v4,v24,f0
add s2,s3,t1
add s3,s3,a7
vse64.v v1, (s2)
vfmul.vf v1,v25,f0
add s2,s3,t1
add s3,s3,a7
vse64.v v2, (s2)
vfmul.vf v2,v26,f0
add s2,s3,t1
add s3,s3,a7
vse64.v v3, (s2)
vfmul.vf v3,v27,f0
add s2,s3,t1
add s3,s3,a7
vse64.v v4, (s2)
vfmul.vf v4,v28,f0
add s2,s3,t1
add s3,s3,a7
vse64.v v1, (s2)
add s2,s3,t1
add s3,s3,a7
vse64.v v2, (s2)
add s2,s3,t1
add s3,s3,a7
vse64.v v3, (s2)
add s2,s3,t1
vse64.v v4, (s2)
j .ukr0_cases_end
.ukr0_case2:
add t5,a3,0
add t6,a3,0
add a0,t5,a7
vle64.v v29, (t5)
add a1,t5,a7
add a2,t6,a7
vle64.v v30, (a0)
add s1,t6,a7
add a1,a1,a7
vle64.v v31, (a1)
vfadd.vv v29,v1,v29
add a2,a2,a7
vfadd.vv v30,v2,v30
vfadd.vv v31,v3,v31
vse64.v v29, (t6)
add s2,t5,a7
add s2,s2,a7
vse64.v v30, (s1)
add s3,t5,0
add s4,t6,a7
add s2,s2,a7
li s5,4
vse64.v v31, (a2)
add s4,s4,a7
vle64.v v1, (s2)
add s6,t6,0
mul s5,a7,s5
add s4,s4,a7
add s3,s3,s5
vle64.v v2, (s3)
vfadd.vv v1,v4,v1
li s5,4
mul s5,a7,s5
add s6,s6,s5
vfadd.vv v2,v5,v2
vse64.v v1, (s4)
add s5,t5,0
add s7,t6,0
li s8,5
li s9,5
mul s8,a7,s8
mul s9,a7,s9
vse64.v v2, (s6)
add s5,s5,s8
add s7,s7,s9
vle64.v v1, (s5)
add s5,s5,a7
vle64.v v2, (s5)
add s5,s5,a7
vfadd.vv v1,v6,v1
vle64.v v3, (s5)
add s5,s5,a7
vfadd.vv v2,v7,v2
vse64.v v1, (s7)
vfadd.vv v3,v8,v3
add s7,s7,a7
vle64.v v1, (s5)
add s5,s5,a7
vse64.v v2, (s7)
add s7,s7,a7
vle64.v v2, (s5)
add s5,s5,a7
vse64.v v3, (s7)
vfadd.vv v1,v9,v1
add s7,s7,a7
vle64.v v3, (s5)
add s5,s5,a7
vfadd.vv v2,v10,v2
vse64.v v1, (s7)
vfadd.vv v3,v11,v3
add s7,s7,a7
vle64.v v1, (s5)
add s5,s5,a7
vse64.v v2, (s7)
add s7,s7,a7
vle64.v v2, (s5)
add s5,s5,a7
vse64.v v3, (s7)
vfadd.vv v1,v12,v1
add s7,s7,a7
add s8,t5,t1
vle64.v v3, (s5)
vfadd.vv v2,v13,v2
vse64.v v1, (s7)
vfadd.vv v3,v14,v3
add s7,s7,a7
vle64.v v1, (s8)
vse64.v v2, (s7)
add s7,s7,a7
vse64.v v3, (s7)
vfadd.vv v1,v15,v1
vse64.v v1, (s8)
add s8,a0,t1
vle64.v v1, (s8)
vfadd.vv v1,v16,v1
vse64.v v1, (s8)
add s8,a1,t1
li s9,8
vle64.v v1, (s8)
mul s9,a7,s9
vfadd.vv v1,v17,v1
sub s5,s5,s9
vse64.v v1, (s8)
add s8,s2,t1
vle64.v v1, (s8)
vfadd.vv v1,v18,v1
li s9,8
vse64.v v1, (s8)
mul s9,a7,s9
add s8,s3,t1
sub s7,s7,s9
vle64.v v1, (s8)
vfadd.vv v1,v19,v1
vse64.v v1, (s8)
add s7,s7,a7
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfadd.vv v1,v20,v1
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfadd.vv v1,v21,v1
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfadd.vv v1,v22,v1
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfadd.vv v1,v23,v1
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfadd.vv v1,v24,v1
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfadd.vv v1,v25,v1
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfadd.vv v1,v26,v1
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfadd.vv v1,v27,v1
vse64.v v1, (s8)
add s8,s5,t1
vle64.v v1, (s8)
vfadd.vv v1,v28,v1
vse64.v v1, (s8)
j .ukr0_cases_end
.ukr0_case3:
add t5,a3,0
add t6,a3,0
fld f0, 0(a4)
add a0,t5,a7
add a1,t5,a7
vle64.v v29, (t5)
add a2,t6,a7
vle64.v v30, (a0)
add s1,t6,a7
add a1,a1,a7
vle64.v v31, (a1)
vfmacc.vf v29,f0,v1
add a2,a2,a7
vfmacc.vf v30,f0,v2
vfmacc.vf v31,f0,v3
vse64.v v29, (t6)
add s2,t5,a7
vse64.v v30, (s1)
add s3,t5,0
add s2,s2,a7
add s4,t6,a7
li s5,4
add s2,s2,a7
vse64.v v31, (a2)
add s4,s4,a7
mul s5,a7,s5
vle64.v v1, (s2)
add s6,t6,0
add s4,s4,a7
add s3,s3,s5
vle64.v v2, (s3)
vfmacc.vf v1,f0,v4
li s5,4
mul s5,a7,s5
vfmacc.vf v2,f0,v5
add s6,s6,s5
vse64.v v1, (s4)
add s5,t5,0
add s7,t6,0
li s8,5
li s9,5
vse64.v v2, (s6)
mul s8,a7,s8
mul s9,a7,s9
add s5,s5,s8
add s7,s7,s9
vle64.v v1, (s5)
add s5,s5,a7
vle64.v v2, (s5)
add s5,s5,a7
vfmacc.vf v1,f0,v6
vle64.v v3, (s5)
add s5,s5,a7
vfmacc.vf v2,f0,v7
vse64.v v1, (s7)
vfmacc.vf v3,f0,v8
add s7,s7,a7
vle64.v v1, (s5)
add s5,s5,a7
vse64.v v2, (s7)
add s7,s7,a7
vle64.v v2, (s5)
add s5,s5,a7
vse64.v v3, (s7)
vfmacc.vf v1,f0,v9
add s7,s7,a7
vle64.v v3, (s5)
add s5,s5,a7
vfmacc.vf v2,f0,v10
vse64.v v1, (s7)
vfmacc.vf v3,f0,v11
add s7,s7,a7
vle64.v v1, (s5)
add s5,s5,a7
vse64.v v2, (s7)
add s7,s7,a7
vle64.v v2, (s5)
add s5,s5,a7
vse64.v v3, (s7)
vfmacc.vf v1,f0,v12
add s7,s7,a7
add s8,t5,t1
vle64.v v3, (s5)
vfmacc.vf v2,f0,v13
vse64.v v1, (s7)
vfmacc.vf v3,f0,v14
add s7,s7,a7
vle64.v v1, (s8)
vse64.v v2, (s7)
add s7,s7,a7
vse64.v v3, (s7)
vfmacc.vf v1,f0,v15
vse64.v v1, (s8)
add s8,a0,t1
vle64.v v1, (s8)
vfmacc.vf v1,f0,v16
vse64.v v1, (s8)
add s8,a1,t1
li s9,8
vle64.v v1, (s8)
mul s9,a7,s9
vfmacc.vf v1,f0,v17
sub s5,s5,s9
vse64.v v1, (s8)
add s8,s2,t1
vle64.v v1, (s8)
vfmacc.vf v1,f0,v18
li s9,8
vse64.v v1, (s8)
mul s9,a7,s9
add s8,s3,t1
sub s7,s7,s9
vle64.v v1, (s8)
vfmacc.vf v1,f0,v19
vse64.v v1, (s8)
add s7,s7,a7
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v1,f0,v20
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v1,f0,v21
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v1,f0,v22
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v1,f0,v23
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v1,f0,v24
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v1,f0,v25
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v1,f0,v26
add s7,s7,a7
vse64.v v1, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v1,f0,v27
vse64.v v1, (s8)
add s8,s5,t1
vle64.v v1, (s8)
vfmacc.vf v1,f0,v28
vse64.v v1, (s8)
j .ukr0_cases_end
.ukr0_case4:
add t5,a3,0
add t6,a3,0
fld f0, 0(a5)
add a0,t5,a7
add a1,t5,a7
vle64.v v29, (t5)
add a2,t6,a7
vle64.v v30, (a0)
add s1,t6,a7
add a1,a1,a7
vle64.v v31, (a1)
vfmacc.vf v1,f0,v29
add a2,a2,a7
vfmacc.vf v2,f0,v30
vfmacc.vf v3,f0,v31
vse64.v v1, (t6)
add s2,t5,a7
vse64.v v2, (s1)
add s3,t5,0
add s2,s2,a7
add s4,t6,a7
li s5,4
add s2,s2,a7
vse64.v v3, (a2)
add s4,s4,a7
mul s5,a7,s5
vle64.v v1, (s2)
add s6,t6,0
add s4,s4,a7
add s3,s3,s5
vle64.v v2, (s3)
vfmacc.vf v4,f0,v1
li s5,4
mul s5,a7,s5
vfmacc.vf v5,f0,v2
add s6,s6,s5
vse64.v v4, (s4)
add s5,t5,0
add s7,t6,0
li s8,5
li s9,5
vse64.v v5, (s6)
mul s8,a7,s8
mul s9,a7,s9
add s5,s5,s8
add s7,s7,s9
vle64.v v1, (s5)
add s5,s5,a7
vle64.v v2, (s5)
add s5,s5,a7
vfmacc.vf v6,f0,v1
vle64.v v1, (s5)
add s5,s5,a7
vfmacc.vf v7,f0,v2
vse64.v v6, (s7)
vfmacc.vf v8,f0,v1
add s7,s7,a7
vle64.v v1, (s5)
add s5,s5,a7
vse64.v v7, (s7)
add s7,s7,a7
vle64.v v2, (s5)
add s5,s5,a7
vse64.v v8, (s7)
vfmacc.vf v9,f0,v1
add s7,s7,a7
vle64.v v1, (s5)
add s5,s5,a7
vfmacc.vf v10,f0,v2
vse64.v v9, (s7)
vfmacc.vf v11,f0,v1
add s7,s7,a7
vle64.v v1, (s5)
add s5,s5,a7
vse64.v v10, (s7)
add s7,s7,a7
vle64.v v2, (s5)
add s5,s5,a7
vse64.v v11, (s7)
vfmacc.vf v12,f0,v1
add s7,s7,a7
add s8,t5,t1
vle64.v v1, (s5)
vfmacc.vf v13,f0,v2
vse64.v v12, (s7)
vfmacc.vf v14,f0,v1
add s7,s7,a7
vle64.v v1, (s8)
vse64.v v13, (s7)
add s7,s7,a7
vse64.v v14, (s7)
vfmacc.vf v15,f0,v1
vse64.v v15, (s8)
add s8,a0,t1
vle64.v v1, (s8)
vfmacc.vf v16,f0,v1
vse64.v v16, (s8)
add s8,a1,t1
li s9,8
vle64.v v1, (s8)
mul s9,a7,s9
vfmacc.vf v17,f0,v1
sub s5,s5,s9
vse64.v v17, (s8)
add s8,s2,t1
vle64.v v1, (s8)
vfmacc.vf v18,f0,v1
li s9,8
vse64.v v18, (s8)
mul s9,a7,s9
add s8,s3,t1
sub s7,s7,s9
vle64.v v1, (s8)
vfmacc.vf v19,f0,v1
vse64.v v19, (s8)
add s7,s7,a7
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v20,f0,v1
add s7,s7,a7
vse64.v v20, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v21,f0,v1
add s7,s7,a7
vse64.v v21, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v22,f0,v1
add s7,s7,a7
vse64.v v22, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v23,f0,v1
add s7,s7,a7
vse64.v v23, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v24,f0,v1
add s7,s7,a7
vse64.v v24, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v25,f0,v1
add s7,s7,a7
vse64.v v25, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v26,f0,v1
add s7,s7,a7
vse64.v v26, (s8)
add s8,s5,t1
add s5,s5,a7
vle64.v v1, (s8)
vfmacc.vf v27,f0,v1
vse64.v v27, (s8)
add s8,s5,t1
vle64.v v1, (s8)
vfmacc.vf v28,f0,v1
vse64.v v28, (s8)
j .ukr0_cases_end
.ukr0_case5:
add t5,a3,0
add t6,a3,0
fld f0, 0(a5)
add a0,t5,a7
fld f1, 0(a4)
add a1,t5,a7
vle64.v v29, (t5)
add a2,t6,a7
vle64.v v30, (a0)
add a1,a1,a7
vfmul.vf v29,v29,f0
vfmul.vf v30,v30,f0
vle64.v v31, (a1)
vfmacc.vf v29,f1,v1
vfmacc.vf v30,f1,v2
vfmul.vf v31,v31,f0
vse64.v v29, (t6)
add s1,t5,a7
add s2,t6,a7
vse64.v v30, (a2)
vfmacc.vf v31,f1,v3
add s3,t6,a7
add s1,s1,a7
add s2,s2,a7
add s4,t5,0
add s1,s1,a7
add s3,s3,a7
vle64.v v1, (s1)
add s3,s3,a7
vse64.v v31, (s2)
li s5,4
mul s5,a7,s5
add s4,s4,s5
vfmul.vf v1,v1,f0
vle64.v v2, (s4)
vfmacc.vf v1,f1,v4
add s5,t6,0
vfmul.vf v2,v2,f0
li s6,4
mul s6,a7,s6
add s5,s5,s6
vse64.v v1, (s3)
add s6,t5,0
vfmacc.vf v2,f1,v5
add s7,t6,0
li s8,5
li s9,5
mul s8,a7,s8
mul s9,a7,s9
add s6,s6,s8
add s7,s7,s9
vle64.v v1, (s6)
vse64.v v2, (s5)
add s6,s6,a7
vle64.v v2, (s6)
vfmul.vf v1,v1,f0
vfmul.vf v2,v2,f0
vfmacc.vf v1,f1,v6
add s6,s6,a7
vle64.v v3, (s6)
vfmacc.vf v2,f1,v7
vse64.v v1, (s7)
add s6,s6,a7
add s7,s7,a7
vfmul.vf v3,v3,f0
vle64.v v1, (s6)
vse64.v v2, (s7)
add s6,s6,a7
add s7,s7,a7
vle64.v v2, (s6)
vfmacc.vf v3,f1,v8
vfmul.vf v1,v1,f0
vfmul.vf v2,v2,f0
vse64.v v3, (s7)
add s6,s6,a7
vfmacc.vf v1,f1,v9
add s7,s7,a7
vle64.v v3, (s6)
vfmacc.vf v2,f1,v10
vse64.v v1, (s7)
add s6,s6,a7
add s7,s7,a7
vfmul.vf v3,v3,f0
vle64.v v1, (s6)
vse64.v v2, (s7)
add s6,s6,a7
add s7,s7,a7
vle64.v v2, (s6)
vfmacc.vf v3,f1,v11
vfmul.vf v1,v1,f0
vfmul.vf v2,v2,f0
vse64.v v3, (s7)
add s6,s6,a7
vfmacc.vf v1,f1,v12
add s7,s7,a7
vle64.v v3, (s6)
vfmacc.vf v2,f1,v13
vse64.v v1, (s7)
add s8,t5,t1
add s7,s7,a7
vfmul.vf v3,v3,f0
vle64.v v1, (s8)
vse64.v v2, (s7)
add s7,s7,a7
vfmacc.vf v3,f1,v14
vfmul.vf v1,v1,f0
vse64.v v3, (s7)
vfmacc.vf v1,f1,v15
vse64.v v1, (s8)
add s8,a0,t1
vle64.v v1, (s8)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v16
vse64.v v1, (s8)
add s8,a1,t1
vle64.v v1, (s8)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v17
li s9,8
vse64.v v1, (s8)
mul s9,a7,s9
add s8,s1,t1
sub s6,s6,s9
vle64.v v1, (s8)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v18
vse64.v v1, (s8)
add s8,s4,t1
li s9,8
vle64.v v1, (s8)
mul s9,a7,s9
vfmul.vf v1,v1,f0
sub s7,s7,s9
vfmacc.vf v1,f1,v19
vse64.v v1, (s8)
add s8,s6,t1
add s6,s6,a7
vle64.v v1, (s8)
add s7,s7,a7
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v20
vse64.v v1, (s8)
add s7,s7,a7
add s8,s6,t1
add s6,s6,a7
vle64.v v1, (s8)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v21
vse64.v v1, (s8)
add s7,s7,a7
add s8,s6,t1
add s6,s6,a7
vle64.v v1, (s8)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v22
vse64.v v1, (s8)
add s7,s7,a7
add s8,s6,t1
add s6,s6,a7
vle64.v v1, (s8)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v23
vse64.v v1, (s8)
add s7,s7,a7
add s8,s6,t1
add s6,s6,a7
vle64.v v1, (s8)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v24
vse64.v v1, (s8)
add s7,s7,a7
add s8,s6,t1
add s6,s6,a7
vle64.v v1, (s8)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v25
vse64.v v1, (s8)
add s7,s7,a7
add s8,s6,t1
add s6,s6,a7
vle64.v v1, (s8)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v26
vse64.v v1, (s8)
add s7,s7,a7
add s8,s6,t1
add s6,s6,a7
vle64.v v1, (s8)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v27
vse64.v v1, (s8)
add s8,s6,t1
vle64.v v1, (s8)
vfmul.vf v1,v1,f0
vfmacc.vf v1,f1,v28
vse64.v v1, (s8)
j .ukr0_cases_end
.ukr0_case6:
add t5,a3,0
add t6,t5,0
vsse64.v v1, (t5), a6
add a0,t5,a7
add a1,t5,a7
li a2,4
add a0,a0,a7
add s1,t5,a7
mul a2,a7,a2
add a1,a1,a7
add a0,a0,a7
vsse64.v v2, (s1), a6
add s2,t5,0
add t6,t6,a2
vsse64.v v3, (a1), a6
vsse64.v v4, (a0), a6
li a2,5
vsse64.v v5, (t6), a6
mul a2,a7,a2
add s2,s2,a2
vsse64.v v6, (s2), a6
add s2,s2,a7
vsse64.v v7, (s2), a6
add s2,s2,a7
vsse64.v v8, (s2), a6
add s2,s2,a7
vsse64.v v9, (s2), a6
add s2,s2,a7
vsse64.v v10, (s2), a6
add s2,s2,a7
vsse64.v v11, (s2), a6
add s2,s2,a7
vsse64.v v12, (s2), a6
add s2,s2,a7
vsse64.v v13, (s2), a6
add s2,s2,a7
vsse64.v v14, (s2), a6
add s2,s2,t4
li a2,13
mul a2,a7,a2
sub s2,s2,a2
vsse64.v v15, (s2), a6
add s2,s2,a7
vsse64.v v16, (s2), a6
add s2,s2,a7
vsse64.v v17, (s2), a6
add s2,s2,a7
vsse64.v v18, (s2), a6
add s2,s2,a7
vsse64.v v19, (s2), a6
add s2,s2,a7
vsse64.v v20, (s2), a6
add s2,s2,a7
vsse64.v v21, (s2), a6
add s2,s2,a7
vsse64.v v22, (s2), a6
add s2,s2,a7
vsse64.v v23, (s2), a6
add s2,s2,a7
vsse64.v v24, (s2), a6
add s2,s2,a7
vsse64.v v25, (s2), a6
add s2,s2,a7
vsse64.v v26, (s2), a6
add s2,s2,a7
vsse64.v v27, (s2), a6
add s2,s2,a7
vsse64.v v28, (s2), a6
j .ukr0_cases_end
.ukr0_case7:
add t5,a3,0
fld f0, 0(a4)
add t6,t5,a7
add a0,t5,a7
add a1,t5,a7
add t6,t6,a7
add a0,a0,a7
vfmul.vf v29,v1,f0
add t6,t6,a7
vfmul.vf v1,v2,f0
vfmul.vf v2,v3,f0
vfmul.vf v3,v4,f0
vsse64.v v29, (t5), a6
add a2,t5,0
vfmul.vf v4,v5,f0
vsse64.v v1, (a1), a6
li s1,4
vsse64.v v2, (a0), a6
vfmul.vf v1,v6,f0
add s2,t5,0
vsse64.v v3, (t6), a6
vfmul.vf v2,v7,f0
mul s1,a7,s1
vfmul.vf v3,v8,f0
li s3,5
add a2,a2,s1
mul s3,a7,s3
add s2,s2,s3
vsse64.v v4, (a2), a6
vfmul.vf v4,v9,f0
vfmul.vf v5,v10,f0
vsse64.v v1, (s2), a6
vfmul.vf v1,v11,f0
add s2,s2,a7
vsse64.v v2, (s2), a6
vfmul.vf v2,v12,f0
add s2,s2,a7
vsse64.v v3, (s2), a6
vfmul.vf v3,v13,f0
add s2,s2,a7
vsse64.v v4, (s2), a6
vfmul.vf v4,v14,f0
add s2,s2,a7
vsse64.v v5, (s2), a6
vfmul.vf v5,v15,f0
add s2,s2,a7
vsse64.v v1, (s2), a6
add s2,s2,a7
vsse64.v v2, (s2), a6
vfmul.vf v1,v16,f0
add s2,s2,a7
vsse64.v v3, (s2), a6
vfmul.vf v2,v17,f0
add s2,s2,a7
vsse64.v v4, (s2), a6
vfmul.vf v3,v18,f0
add s2,s2,t4
li s1,13
mul s1,a7,s1
vfmul.vf v4,v19,f0
sub s2,s2,s1
vsse64.v v5, (s2), a6
vfmul.vf v5,v20,f0
add s2,s2,a7
vsse64.v v1, (s2), a6
vfmul.vf v1,v21,f0
add s2,s2,a7
vsse64.v v2, (s2), a6
vfmul.vf v2,v22,f0
add s2,s2,a7
vsse64.v v3, (s2), a6
vfmul.vf v3,v23,f0
add s2,s2,a7
vsse64.v v4, (s2), a6
vfmul.vf v4,v24,f0
add s2,s2,a7
vsse64.v v5, (s2), a6
vfmul.vf v5,v25,f0
add s2,s2,a7
vsse64.v v1, (s2), a6
vfmul.vf v1,v26,f0
add s2,s2,a7
vsse64.v v2, (s2), a6
vfmul.vf v2,v27,f0
add s2,s2,a7
vsse64.v v3, (s2), a6
vfmul.vf v3,v28,f0
add s2,s2,a7
vsse64.v v4, (s2), a6
add s2,s2,a7
vsse64.v v5, (s2), a6
add s2,s2,a7
vsse64.v v1, (s2), a6
add s2,s2,a7
vsse64.v v2, (s2), a6
add s2,s2,a7
vsse64.v v3, (s2), a6
j .ukr0_cases_end
.ukr0_case8:
add t5,a3,0
add t6,t5,a7
vlse64.v v29, (t5), a6
add a0,t5,a7
add a1,a3,a7
add t6,t6,a7
vlse64.v v30, (a0), a6
add a2,a3,a7
vlse64.v v31, (t6), a6
vfadd.vv v29,v1,v29
add a1,a1,a7
vfadd.vv v30,v2,v30
vfadd.vv v31,v3,v31
vsse64.v v29, (a3), a6
add s1,t5,a7
add s1,s1,a7
vsse64.v v30, (a2), a6
add s2,t5,0
add s3,a3,a7
add s1,s1,a7
vsse64.v v31, (a1), a6
li s4,4
add s3,s3,a7
vlse64.v v1, (s1), a6
add s5,a3,0
mul s4,a7,s4
add s3,s3,a7
add s2,s2,s4
vlse64.v v2, (s2), a6
vfadd.vv v1,v4,v1
li s4,4
mul s4,a7,s4
add s5,s5,s4
vfadd.vv v2,v5,v2
vsse64.v v1, (s3), a6
add s4,t5,0
add s6,a3,0
li s7,5
li s8,5
mul s7,a7,s7
mul s8,a7,s8
vsse64.v v2, (s5), a6
add s4,s4,s7
add s6,s6,s8
vlse64.v v1, (s4), a6
add s4,s4,a7
vlse64.v v2, (s4), a6
add s4,s4,a7
vfadd.vv v1,v6,v1
vlse64.v v3, (s4), a6
add s4,s4,a7
vfadd.vv v2,v7,v2
vsse64.v v1, (s6), a6
vfadd.vv v3,v8,v3
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
add s6,s6,a7
vlse64.v v2, (s4), a6
add s4,s4,a7
vsse64.v v3, (s6), a6
vfadd.vv v1,v9,v1
add s6,s6,a7
vlse64.v v3, (s4), a6
add s4,s4,a7
vfadd.vv v2,v10,v2
vsse64.v v1, (s6), a6
vfadd.vv v3,v11,v3
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
add s6,s6,a7
vlse64.v v2, (s4), a6
add s4,s4,a7
vsse64.v v3, (s6), a6
vfadd.vv v1,v12,v1
add s6,s6,a7
vlse64.v v3, (s4), a6
add s4,s4,t4
vfadd.vv v2,v13,v2
vsse64.v v1, (s6), a6
li s7,13
vfadd.vv v3,v14,v3
add s6,s6,a7
mul s7,a7,s7
vsse64.v v2, (s6), a6
add s6,s6,a7
sub s4,s4,s7
vlse64.v v1, (s4), a6
vsse64.v v3, (s6), a6
add s4,s4,a7
add s6,s6,t4
vlse64.v v2, (s4), a6
add s4,s4,a7
li s7,13
vfadd.vv v1,v15,v1
mul s7,a7,s7
vlse64.v v3, (s4), a6
sub s6,s6,s7
add s4,s4,a7
vfadd.vv v2,v16,v2
vsse64.v v1, (s6), a6
vfadd.vv v3,v17,v3
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
add s4,s4,a7
vsse64.v v3, (s6), a6
vfadd.vv v1,v18,v1
add s6,s6,a7
vlse64.v v3, (s4), a6
add s4,s4,a7
vfadd.vv v2,v19,v2
vsse64.v v1, (s6), a6
vfadd.vv v3,v20,v3
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
add s4,s4,a7
vsse64.v v3, (s6), a6
vfadd.vv v1,v21,v1
add s6,s6,a7
vlse64.v v3, (s4), a6
add s4,s4,a7
vfadd.vv v2,v22,v2
vsse64.v v1, (s6), a6
vfadd.vv v3,v23,v3
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
add s4,s4,a7
vsse64.v v3, (s6), a6
vfadd.vv v1,v24,v1
add s6,s6,a7
vlse64.v v3, (s4), a6
add s4,s4,a7
vfadd.vv v2,v25,v2
vsse64.v v1, (s6), a6
vfadd.vv v3,v26,v3
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
vsse64.v v3, (s6), a6
vfadd.vv v1,v27,v1
add s6,s6,a7
vfadd.vv v2,v28,v2
vsse64.v v1, (s6), a6
add s6,s6,a7
vsse64.v v2, (s6), a6
j .ukr0_cases_end
.ukr0_case9:
add t5,a3,0
fld f0, 0(a4)
add t6,t5,a7
add a0,t5,a7
vlse64.v v29, (t5), a6
add a1,a3,a7
add t6,t6,a7
vlse64.v v30, (a0), a6
add a2,a3,a7
vlse64.v v31, (t6), a6
vfmacc.vf v29,f0,v1
add a1,a1,a7
vfmacc.vf v30,f0,v2
vfmacc.vf v31,f0,v3
vsse64.v v29, (a3), a6
add s1,t5,a7
add s1,s1,a7
vsse64.v v30, (a2), a6
add s2,t5,0
add s3,a3,a7
vsse64.v v31, (a1), a6
add s1,s1,a7
li s4,4
add s3,s3,a7
vlse64.v v1, (s1), a6
add s5,a3,0
mul s4,a7,s4
add s3,s3,a7
add s2,s2,s4
vlse64.v v2, (s2), a6
vfmacc.vf v1,f0,v4
li s4,4
mul s4,a7,s4
add s5,s5,s4
vfmacc.vf v2,f0,v5
vsse64.v v1, (s3), a6
add s4,t5,0
add s6,a3,0
li s7,5
li s8,5
mul s7,a7,s7
mul s8,a7,s8
vsse64.v v2, (s5), a6
add s4,s4,s7
add s6,s6,s8
vlse64.v v1, (s4), a6
add s4,s4,a7
vlse64.v v2, (s4), a6
add s4,s4,a7
vfmacc.vf v1,f0,v6
vlse64.v v3, (s4), a6
add s4,s4,a7
vfmacc.vf v2,f0,v7
vsse64.v v1, (s6), a6
vfmacc.vf v3,f0,v8
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
add s6,s6,a7
vlse64.v v2, (s4), a6
add s4,s4,a7
vsse64.v v3, (s6), a6
vfmacc.vf v1,f0,v9
add s6,s6,a7
vlse64.v v3, (s4), a6
add s4,s4,a7
vfmacc.vf v2,f0,v10
vsse64.v v1, (s6), a6
vfmacc.vf v3,f0,v11
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
add s6,s6,a7
vlse64.v v2, (s4), a6
add s4,s4,a7
vsse64.v v3, (s6), a6
vfmacc.vf v1,f0,v12
add s6,s6,a7
vlse64.v v3, (s4), a6
add s4,s4,t4
vfmacc.vf v2,f0,v13
vsse64.v v1, (s6), a6
li s7,13
vfmacc.vf v3,f0,v14
add s6,s6,a7
mul s7,a7,s7
vsse64.v v2, (s6), a6
add s6,s6,a7
sub s4,s4,s7
vlse64.v v1, (s4), a6
vsse64.v v3, (s6), a6
add s4,s4,a7
add s6,s6,t4
vlse64.v v2, (s4), a6
add s4,s4,a7
li s7,13
vfmacc.vf v1,f0,v15
mul s7,a7,s7
vlse64.v v3, (s4), a6
sub s6,s6,s7
add s4,s4,a7
vfmacc.vf v2,f0,v16
vsse64.v v1, (s6), a6
vfmacc.vf v3,f0,v17
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
add s4,s4,a7
vsse64.v v3, (s6), a6
vfmacc.vf v1,f0,v18
add s6,s6,a7
vlse64.v v3, (s4), a6
add s4,s4,a7
vfmacc.vf v2,f0,v19
vsse64.v v1, (s6), a6
vfmacc.vf v3,f0,v20
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
add s4,s4,a7
vsse64.v v3, (s6), a6
vfmacc.vf v1,f0,v21
add s6,s6,a7
vlse64.v v3, (s4), a6
add s4,s4,a7
vfmacc.vf v2,f0,v22
vsse64.v v1, (s6), a6
vfmacc.vf v3,f0,v23
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
add s4,s4,a7
vsse64.v v3, (s6), a6
vfmacc.vf v1,f0,v24
add s6,s6,a7
vlse64.v v3, (s4), a6
add s4,s4,a7
vfmacc.vf v2,f0,v25
vsse64.v v1, (s6), a6
vfmacc.vf v3,f0,v26
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v2, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
vsse64.v v3, (s6), a6
vfmacc.vf v1,f0,v27
add s6,s6,a7
vfmacc.vf v2,f0,v28
vsse64.v v1, (s6), a6
add s6,s6,a7
vsse64.v v2, (s6), a6
j .ukr0_cases_end
.ukr0_case10:
add t5,a3,0
fld f0, 0(a5)
add t6,t5,a7
add a0,t5,a7
vlse64.v v29, (t5), a6
add a1,a3,a7
add t6,t6,a7
vlse64.v v30, (a0), a6
add a2,a3,a7
vlse64.v v31, (t6), a6
vfmacc.vf v1,f0,v29
add a1,a1,a7
vfmacc.vf v2,f0,v30
vfmacc.vf v3,f0,v31
vsse64.v v1, (a3), a6
add s1,t5,a7
add s1,s1,a7
vsse64.v v2, (a2), a6
add s2,t5,0
add s3,a3,a7
vsse64.v v3, (a1), a6
add s1,s1,a7
li s4,4
add s3,s3,a7
vlse64.v v1, (s1), a6
add s5,a3,0
mul s4,a7,s4
add s3,s3,a7
add s2,s2,s4
vlse64.v v2, (s2), a6
vfmacc.vf v4,f0,v1
li s4,4
mul s4,a7,s4
add s5,s5,s4
vfmacc.vf v5,f0,v2
vsse64.v v4, (s3), a6
add s4,t5,0
add s6,a3,0
li s7,5
li s8,5
mul s7,a7,s7
mul s8,a7,s8
vsse64.v v5, (s5), a6
add s4,s4,s7
add s6,s6,s8
vlse64.v v1, (s4), a6
add s4,s4,a7
vlse64.v v2, (s4), a6
add s4,s4,a7
vfmacc.vf v6,f0,v1
vlse64.v v1, (s4), a6
add s4,s4,a7
vfmacc.vf v7,f0,v2
vsse64.v v6, (s6), a6
vfmacc.vf v8,f0,v1
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v7, (s6), a6
add s6,s6,a7
vlse64.v v2, (s4), a6
add s4,s4,a7
vsse64.v v8, (s6), a6
vfmacc.vf v9,f0,v1
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vfmacc.vf v10,f0,v2
vsse64.v v9, (s6), a6
vfmacc.vf v11,f0,v1
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v10, (s6), a6
add s6,s6,a7
vlse64.v v2, (s4), a6
add s4,s4,a7
vsse64.v v11, (s6), a6
vfmacc.vf v12,f0,v1
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,t4
vfmacc.vf v13,f0,v2
vsse64.v v12, (s6), a6
li s7,13
vfmacc.vf v14,f0,v1
add s6,s6,a7
mul s7,a7,s7
vsse64.v v13, (s6), a6
add s6,s6,a7
sub s4,s4,s7
vlse64.v v1, (s4), a6
vsse64.v v14, (s6), a6
add s4,s4,a7
add s6,s6,t4
vlse64.v v2, (s4), a6
add s4,s4,a7
li s7,13
vfmacc.vf v15,f0,v1
mul s7,a7,s7
vlse64.v v1, (s4), a6
sub s6,s6,s7
add s4,s4,a7
vfmacc.vf v16,f0,v2
vsse64.v v15, (s6), a6
vfmacc.vf v17,f0,v1
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v16, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
add s4,s4,a7
vsse64.v v17, (s6), a6
vfmacc.vf v18,f0,v1
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vfmacc.vf v19,f0,v2
vsse64.v v18, (s6), a6
vfmacc.vf v20,f0,v1
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v19, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
add s4,s4,a7
vsse64.v v20, (s6), a6
vfmacc.vf v21,f0,v1
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vfmacc.vf v22,f0,v2
vsse64.v v21, (s6), a6
vfmacc.vf v23,f0,v1
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v22, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
add s4,s4,a7
vsse64.v v23, (s6), a6
vfmacc.vf v24,f0,v1
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vfmacc.vf v25,f0,v2
vsse64.v v24, (s6), a6
vfmacc.vf v26,f0,v1
add s6,s6,a7
vlse64.v v1, (s4), a6
add s4,s4,a7
vsse64.v v25, (s6), a6
vlse64.v v2, (s4), a6
add s6,s6,a7
vsse64.v v26, (s6), a6
vfmacc.vf v27,f0,v1
add s6,s6,a7
vfmacc.vf v28,f0,v2
vsse64.v v27, (s6), a6
add s6,s6,a7
vsse64.v v28, (s6), a6
j .ukr0_cases_end
.ukr0_case11:
add t5,a3,0
fld f0, 0(a5)
add t6,t5,a7
fld f1, 0(a4)
vlse64.v v29, (t5), a6
add a0,t5,a7
vlse64.v v30, (t6), a6
add a1,a3,a7
add a0,a0,a7
vfmul.vf v29,v29,f0
vlse64.v v31, (a0), a6
vfmul.vf v30,v30,f0
vfmacc.vf v29,f1,v1
vfmul.vf v31,v31,f0
vfmacc.vf v30,f1,v2
vsse64.v v29, (a3), a6
add a2,t5,a7
vfmacc.vf v31,f1,v3
add s1,a3,a7
vsse64.v v30, (a1), a6
add s2,a3,a7
add a2,a2,a7
add s1,s1,a7
add s3,t5,0
add a2,a2,a7
add s2,s2,a7
vlse64.v v1, (a2), a6
add s2,s2,a7
vsse64.v v31, (s1), a6
li s4,4
mul s4,a7,s4
add s3,s3,s4
vfmul.vf v1,v1,f0
vlse64.v v2, (s3), a6
vfmacc.vf v1,f1,v4
add s4,a3,0
vfmul.vf v2,v2,f0
li s5,4
mul s5,a7,s5
add s4,s4,s5
vsse64.v v1, (s2), a6
add s5,t5,0
vfmacc.vf v2,f1,v5
add s6,a3,0
li s7,5
li s8,5
mul s7,a7,s7
mul s8,a7,s8
add s5,s5,s7
add s6,s6,s8
vlse64.v v1, (s5), a6
vsse64.v v2, (s4), a6
add s5,s5,a7
vlse64.v v2, (s5), a6
vfmul.vf v1,v1,f0
vfmul.vf v2,v2,f0
vfmacc.vf v1,f1,v6
add s5,s5,a7
vlse64.v v3, (s5), a6
vfmacc.vf v2,f1,v7
vsse64.v v1, (s6), a6
add s5,s5,a7
add s6,s6,a7
vfmul.vf v3,v3,f0
vlse64.v v1, (s5), a6
vsse64.v v2, (s6), a6
add s5,s5,a7
add s6,s6,a7
vlse64.v v2, (s5), a6
vfmacc.vf v3,f1,v8
vfmul.vf v1,v1,f0
vfmul.vf v2,v2,f0
vsse64.v v3, (s6), a6
add s5,s5,a7
vfmacc.vf v1,f1,v9
add s6,s6,a7
vlse64.v v3, (s5), a6
vfmacc.vf v2,f1,v10
vsse64.v v1, (s6), a6
add s5,s5,a7
add s6,s6,a7
vfmul.vf v3,v3,f0
vlse64.v v1, (s5), a6
vsse64.v v2, (s6), a6
add s5,s5,a7
add s6,s6,a7
vlse64.v v2, (s5), a6
vfmacc.vf v3,f1,v11
vfmul.vf v1,v1,f0
vfmul.vf v2,v2,f0
vsse64.v v3, (s6), a6
add s5,s5,a7
vfmacc.vf v1,f1,v12
add s6,s6,a7
vlse64.v v3, (s5), a6
vfmacc.vf v2,f1,v13
vsse64.v v1, (s6), a6
add s5,s5,t4
add s6,s6,a7
vfmul.vf v3,v3,f0
li s7,13
vsse64.v v2, (s6), a6
add s6,s6,a7
mul s7,a7,s7
sub s5,s5,s7
vlse64.v v1, (s5), a6
vfmacc.vf v3,f1,v14
vfmul.vf v1,v1,f0
vsse64.v v3, (s6), a6
add s5,s5,a7
add s6,s6,t4
vlse64.v v2, (s5), a6
li s7,13
mul s7,a7,s7
vfmacc.vf v1,f1,v15
add s5,s5,a7
sub s6,s6,s7
vlse64.v v3, (s5), a6
vfmul.vf v2,v2,f0
vsse64.v v1, (s6), a6
add s5,s5,a7
add s6,s6,a7
vfmul.vf v3,v3,f0
vlse64.v v1, (s5), a6
vfmacc.vf v2,f1,v16
vfmacc.vf v3,f1,v17
vfmul.vf v1,v1,f0
vsse64.v v2, (s6), a6
add s5,s5,a7
add s6,s6,a7
vlse64.v v2, (s5), a6
vsse64.v v3, (s6), a6
add s5,s5,a7
vfmacc.vf v1,f1,v18
add s6,s6,a7
vlse64.v v3, (s5), a6
vfmul.vf v2,v2,f0
vsse64.v v1, (s6), a6
add s5,s5,a7
add s6,s6,a7
vfmul.vf v3,v3,f0
vlse64.v v1, (s5), a6
vfmacc.vf v2,f1,v19
vfmacc.vf v3,f1,v20
vfmul.vf v1,v1,f0
vsse64.v v2, (s6), a6
add s5,s5,a7
add s6,s6,a7
vlse64.v v2, (s5), a6
vsse64.v v3, (s6), a6
add s5,s5,a7
vfmacc.vf v1,f1,v21
add s6,s6,a7
vlse64.v v3, (s5), a6
vfmul.vf v2,v2,f0
vsse64.v v1, (s6), a6
add s5,s5,a7
add s6,s6,a7
vfmul.vf v3,v3,f0
vlse64.v v1, (s5), a6
vfmacc.vf v2,f1,v22
vfmacc.vf v3,f1,v23
vfmul.vf v1,v1,f0
vsse64.v v2, (s6), a6
add s5,s5,a7
add s6,s6,a7
vlse64.v v2, (s5), a6
vsse64.v v3, (s6), a6
add s5,s5,a7
vfmacc.vf v1,f1,v24
add s6,s6,a7
vlse64.v v3, (s5), a6
vfmul.vf v2,v2,f0
vsse64.v v1, (s6), a6
add s5,s5,a7
add s6,s6,a7
vfmul.vf v3,v3,f0
vlse64.v v1, (s5), a6
vfmacc.vf v2,f1,v25
vfmacc.vf v3,f1,v26
vfmul.vf v1,v1,f0
vsse64.v v2, (s6), a6
add s5,s5,a7
add s6,s6,a7
vlse64.v v2, (s5), a6
vsse64.v v3, (s6), a6
vfmacc.vf v1,f1,v27
add s6,s6,a7
vfmul.vf v2,v2,f0
vsse64.v v1, (s6), a6
add s6,s6,a7
vfmacc.vf v2,f1,v28
vsse64.v v2, (s6), a6
.ukr0_cases_end:
ld s1, 0(sp)
.cfi_restore s1
ld s2, 8(sp)
.cfi_restore s2
ld s3, 16(sp)
.cfi_restore s3
ld s4, 24(sp)
.cfi_restore s4
ld s5, 32(sp)
.cfi_restore s5
ld s6, 40(sp)
.cfi_restore s6
ld s7, 48(sp)
.cfi_restore s7
ld s8, 56(sp)
.cfi_restore s8
ld s9, 64(sp)
.cfi_restore s9
fld f8, 72(sp)
.cfi_restore f8
fld f9, 80(sp)
.cfi_restore f9
fld f18, 88(sp)
.cfi_restore f18
fld f19, 96(sp)
.cfi_restore f19
fld f20, 104(sp)
.cfi_restore f20
fld f21, 112(sp)
.cfi_restore f21
fld f22, 120(sp)
.cfi_restore f22
fld f23, 128(sp)
.cfi_restore f23
add sp,sp,144
.cfi_adjust_cfa_offset -144
ret
.cfi_endproc
.size bli_dgemm_ukrgen_rvv_vm_2vx14_asm, .-bli_dgemm_ukrgen_rvv_vm_2vx14_asm
.section .note.GNU-stack,"",%progbits
