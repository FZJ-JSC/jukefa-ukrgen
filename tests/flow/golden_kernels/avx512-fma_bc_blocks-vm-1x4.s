.text
.global bli_dgemm_ukrgen_avx512_vm_8x4_asm
.type bli_dgemm_ukrgen_avx512_vm_8x4_asm, %function
bli_dgemm_ukrgen_avx512_vm_8x4_asm:
.cfi_startproc
# rdi = k
# rsi = base(A)
# rdx = base(B)
# rcx = base(C)
# r8 = base(alpha)
# r9 = base(beta)
# r10 = stride(C,m)
# r11 = stride(C,n)
movq %rdi, %r10
andq $3, %r10
shrq $2, %rdi
vpxorq %zmm0,%zmm0,%zmm0
vpxorq %zmm1,%zmm1,%zmm1
vpxorq %zmm2,%zmm2,%zmm2
vpxorq %zmm3,%zmm3,%zmm3
test %rdi,%rdi
jz .ukr1_done
vmovupd (%rsi), %zmm4
vbroadcastsd (%rdx), %zmm5
vbroadcastsd 8(%rdx), %zmm6
vbroadcastsd 16(%rdx), %zmm7
vbroadcastsd 24(%rdx), %zmm8
addq $64,%rsi
addq $32,%rdx
addq $-1,%rdi
test %rdi,%rdi
jz .ukr1_last
.ukr1_loop:
addq $-1,%rdi
vfmadd231pd %zmm4,%zmm5,%zmm0
vfmadd231pd %zmm4,%zmm6,%zmm1
vfmadd231pd %zmm4,%zmm7,%zmm2
vfmadd231pd %zmm4,%zmm8,%zmm3
vmovupd (%rsi), %zmm9
vbroadcastsd (%rdx), %zmm10
vbroadcastsd 8(%rdx), %zmm11
vbroadcastsd 16(%rdx), %zmm12
vbroadcastsd 24(%rdx), %zmm13
vfmadd231pd %zmm9,%zmm10,%zmm0
vfmadd231pd %zmm9,%zmm11,%zmm1
vfmadd231pd %zmm9,%zmm12,%zmm2
vfmadd231pd %zmm9,%zmm13,%zmm3
vmovupd 64(%rsi), %zmm14
vbroadcastsd 32(%rdx), %zmm15
vbroadcastsd 40(%rdx), %zmm16
vbroadcastsd 48(%rdx), %zmm17
vbroadcastsd 56(%rdx), %zmm18
vfmadd231pd %zmm14,%zmm15,%zmm0
vfmadd231pd %zmm14,%zmm16,%zmm1
vfmadd231pd %zmm14,%zmm17,%zmm2
vfmadd231pd %zmm14,%zmm18,%zmm3
vmovupd 128(%rsi), %zmm19
vbroadcastsd 64(%rdx), %zmm20
vbroadcastsd 72(%rdx), %zmm21
vbroadcastsd 80(%rdx), %zmm22
vbroadcastsd 88(%rdx), %zmm23
vmovupd 192(%rsi), %zmm4
vbroadcastsd 96(%rdx), %zmm5
vbroadcastsd 104(%rdx), %zmm6
vbroadcastsd 112(%rdx), %zmm7
vbroadcastsd 120(%rdx), %zmm8
vfmadd231pd %zmm19,%zmm20,%zmm0
vfmadd231pd %zmm19,%zmm21,%zmm1
vfmadd231pd %zmm19,%zmm22,%zmm2
vfmadd231pd %zmm19,%zmm23,%zmm3
addq $256,%rsi
addq $128,%rdx
test %rdi,%rdi
jnz .ukr1_loop
.ukr1_last:
vfmadd231pd %zmm4,%zmm5,%zmm0
vfmadd231pd %zmm4,%zmm6,%zmm1
vfmadd231pd %zmm4,%zmm7,%zmm2
vfmadd231pd %zmm4,%zmm8,%zmm3
vmovupd (%rsi), %zmm9
vbroadcastsd (%rdx), %zmm10
vbroadcastsd 8(%rdx), %zmm11
vbroadcastsd 16(%rdx), %zmm12
vbroadcastsd 24(%rdx), %zmm13
vfmadd231pd %zmm9,%zmm10,%zmm0
vfmadd231pd %zmm9,%zmm11,%zmm1
vfmadd231pd %zmm9,%zmm12,%zmm2
vfmadd231pd %zmm9,%zmm13,%zmm3
vmovupd 64(%rsi), %zmm14
vbroadcastsd 32(%rdx), %zmm15
vbroadcastsd 40(%rdx), %zmm16
vbroadcastsd 48(%rdx), %zmm17
vbroadcastsd 56(%rdx), %zmm18
vfmadd231pd %zmm14,%zmm15,%zmm0
vfmadd231pd %zmm14,%zmm16,%zmm1
vfmadd231pd %zmm14,%zmm17,%zmm2
vfmadd231pd %zmm14,%zmm18,%zmm3
vmovupd 128(%rsi), %zmm19
vbroadcastsd 64(%rdx), %zmm20
vbroadcastsd 72(%rdx), %zmm21
vbroadcastsd 80(%rdx), %zmm22
vbroadcastsd 88(%rdx), %zmm23
vfmadd231pd %zmm19,%zmm20,%zmm0
vfmadd231pd %zmm19,%zmm21,%zmm1
vfmadd231pd %zmm19,%zmm22,%zmm2
vfmadd231pd %zmm19,%zmm23,%zmm3
addq $192,%rsi
addq $96,%rdx
.ukr1_done:
test %r10,%r10
jz .ukr1_taildone
.ukr1_tail:
addq $-1,%r10
vmovupd (%rsi), %zmm4
vbroadcastsd (%rdx), %zmm5
vbroadcastsd 8(%rdx), %zmm6
vbroadcastsd 16(%rdx), %zmm7
vbroadcastsd 24(%rdx), %zmm8
vfmadd231pd %zmm4,%zmm5,%zmm0
vfmadd231pd %zmm4,%zmm6,%zmm1
vfmadd231pd %zmm4,%zmm7,%zmm2
vfmadd231pd %zmm4,%zmm8,%zmm3
addq $64,%rsi
addq $32,%rdx
test %r10,%r10
jnz .ukr1_tail
.ukr1_taildone:
movq 8(%rsp), %r10
movq 16(%rsp), %r11
movq %r10, %rax
addq $-8,%rax
test %rax,%rax
jz .ukr0_ok0_0
jmp .ukr0_try1
.ukr0_ok0_0:
vmovsd (%r9), %xmm4
vpxord %xmm5,%xmm5,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try1
jp .ukr0_try1
vmovsd (%r8), %xmm4
movq $4607182418800017408,%rax
vmovq %rax,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try1
jp .ukr0_try1
jmp .ukr0_case0
.ukr0_try1:
movq %r10, %rax
addq $-8,%rax
test %rax,%rax
jz .ukr0_ok1_0
jmp .ukr0_try2
.ukr0_ok1_0:
vmovsd (%r9), %xmm4
vpxord %xmm5,%xmm5,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try2
jp .ukr0_try2
jmp .ukr0_case1
.ukr0_try2:
movq %r10, %rax
addq $-8,%rax
test %rax,%rax
jz .ukr0_ok2_0
jmp .ukr0_try3
.ukr0_ok2_0:
vmovsd (%r9), %xmm4
movq $4607182418800017408,%rax
vmovq %rax,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try3
jp .ukr0_try3
vmovsd (%r8), %xmm4
movq $4607182418800017408,%rax
vmovq %rax,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try3
jp .ukr0_try3
jmp .ukr0_case2
.ukr0_try3:
movq %r10, %rax
addq $-8,%rax
test %rax,%rax
jz .ukr0_ok3_0
jmp .ukr0_try4
.ukr0_ok3_0:
vmovsd (%r9), %xmm4
movq $4607182418800017408,%rax
vmovq %rax,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try4
jp .ukr0_try4
jmp .ukr0_case3
.ukr0_try4:
movq %r10, %rax
addq $-8,%rax
test %rax,%rax
jz .ukr0_ok4_0
jmp .ukr0_try5
.ukr0_ok4_0:
vmovsd (%r8), %xmm4
movq $4607182418800017408,%rax
vmovq %rax,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try5
jp .ukr0_try5
jmp .ukr0_case4
.ukr0_try5:
movq %r10, %rax
addq $-8,%rax
test %rax,%rax
jz .ukr0_ok5_0
jmp .ukr0_try6
.ukr0_ok5_0:
jmp .ukr0_case5
.ukr0_try6:
vmovsd (%r9), %xmm4
vpxord %xmm5,%xmm5,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try7
jp .ukr0_try7
vmovsd (%r8), %xmm4
movq $4607182418800017408,%rax
vmovq %rax,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try7
jp .ukr0_try7
jmp .ukr0_case6
.ukr0_try7:
vmovsd (%r9), %xmm4
vpxord %xmm5,%xmm5,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try8
jp .ukr0_try8
jmp .ukr0_case7
.ukr0_try8:
vmovsd (%r9), %xmm4
movq $4607182418800017408,%rax
vmovq %rax,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try9
jp .ukr0_try9
vmovsd (%r8), %xmm4
movq $4607182418800017408,%rax
vmovq %rax,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try9
jp .ukr0_try9
jmp .ukr0_case8
.ukr0_try9:
vmovsd (%r9), %xmm4
movq $4607182418800017408,%rax
vmovq %rax,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try10
jp .ukr0_try10
jmp .ukr0_case9
.ukr0_try10:
vmovsd (%r8), %xmm4
movq $4607182418800017408,%rax
vmovq %rax,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try11
jp .ukr0_try11
jmp .ukr0_case10
.ukr0_try11:
jmp .ukr0_case11
.ukr0_try12:
jmp .ukr0_cases_end
.ukr0_case0:
movq %rcx, %rax
movq %rcx, %rdx
vmovupd %zmm0, (%rax)
vmovupd %zmm1, (%rax,%r11,1)
vmovupd %zmm2, (%rax,%r11,2)
addq %r11,%rax
leaq (%rax,%r11,2),%rax
vmovupd %zmm3, (%rax)
jmp .ukr0_cases_end
.ukr0_case1:
movq %rcx, %rax
movq %rcx, %rdx
vbroadcastsd (%r8), %zmm4
vmulpd %zmm0,%zmm4,%zmm5
vmulpd %zmm1,%zmm4,%zmm0
vmulpd %zmm2,%zmm4,%zmm1
vmulpd %zmm3,%zmm4,%zmm2
vmovupd %zmm5, (%rax)
vmovupd %zmm0, (%rax,%r11,1)
vmovupd %zmm1, (%rax,%r11,2)
addq %r11,%rax
leaq (%rax,%r11,2),%rax
vmovupd %zmm2, (%rax)
jmp .ukr0_cases_end
.ukr0_case2:
movq %rcx, %rax
movq %rcx, %rdx
vmovupd (%rax), %zmm4
vmovupd (%rax,%r11,1), %zmm5
vmovupd (%rax,%r11,2), %zmm6
addq %r11,%rax
leaq (%rax,%r11,2),%rax
vmovupd (%rax), %zmm7
vaddpd %zmm0,%zmm4,%zmm4
vaddpd %zmm1,%zmm5,%zmm5
vaddpd %zmm2,%zmm6,%zmm6
vaddpd %zmm3,%zmm7,%zmm7
vmovupd %zmm4, (%rdx)
vmovupd %zmm5, (%rdx,%r11,1)
vmovupd %zmm6, (%rdx,%r11,2)
movq %rax, %rdx
vmovupd %zmm7, (%rdx)
jmp .ukr0_cases_end
.ukr0_case3:
movq %rcx, %rax
movq %rcx, %rdx
vmovupd (%rax), %zmm4
vmovupd (%rax,%r11,1), %zmm5
vmovupd (%rax,%r11,2), %zmm6
vbroadcastsd (%r8), %zmm7
addq %r11,%rax
leaq (%rax,%r11,2),%rax
vmovupd (%rax), %zmm8
vfmadd231pd %zmm0,%zmm7,%zmm4
vfmadd231pd %zmm1,%zmm7,%zmm5
vfmadd231pd %zmm2,%zmm7,%zmm6
vfmadd231pd %zmm3,%zmm7,%zmm8
vmovupd %zmm4, (%rdx)
vmovupd %zmm5, (%rdx,%r11,1)
vmovupd %zmm6, (%rdx,%r11,2)
movq %rax, %rdx
vmovupd %zmm8, (%rdx)
jmp .ukr0_cases_end
.ukr0_case4:
movq %rcx, %rax
movq %rcx, %rdx
vmovupd (%rax), %zmm4
vmovupd (%rax,%r11,1), %zmm5
vmovupd (%rax,%r11,2), %zmm6
vbroadcastsd (%r9), %zmm7
addq %r11,%rax
leaq (%rax,%r11,2),%rax
vmovupd (%rax), %zmm8
vfmadd231pd %zmm4,%zmm7,%zmm0
vfmadd231pd %zmm5,%zmm7,%zmm1
vfmadd231pd %zmm6,%zmm7,%zmm2
vfmadd231pd %zmm8,%zmm7,%zmm3
vmovupd %zmm0, (%rdx)
vmovupd %zmm1, (%rdx,%r11,1)
vmovupd %zmm2, (%rdx,%r11,2)
movq %rax, %rdx
vmovupd %zmm3, (%rdx)
jmp .ukr0_cases_end
.ukr0_case5:
movq %rcx, %rax
movq %rcx, %rdx
vmovupd (%rax), %zmm4
vmovupd (%rax,%r11,1), %zmm5
vmovupd (%rax,%r11,2), %zmm6
vbroadcastsd (%r9), %zmm7
addq %r11,%rax
leaq (%rax,%r11,2),%rax
vmovupd (%rax), %zmm8
vmulpd %zmm4,%zmm7,%zmm4
vbroadcastsd (%r8), %zmm9
vmulpd %zmm5,%zmm7,%zmm5
vmulpd %zmm6,%zmm7,%zmm6
vmulpd %zmm8,%zmm7,%zmm8
vfmadd231pd %zmm0,%zmm9,%zmm4
vfmadd231pd %zmm1,%zmm9,%zmm5
vfmadd231pd %zmm2,%zmm9,%zmm6
vfmadd231pd %zmm3,%zmm9,%zmm8
vmovupd %zmm4, (%rdx)
vmovupd %zmm5, (%rdx,%r11,1)
vmovupd %zmm6, (%rdx,%r11,2)
movq %rax, %rdx
vmovupd %zmm8, (%rdx)
jmp .ukr0_cases_end
.ukr0_case6:
movq %rcx, %rax
vextractf32x4 $0,%zmm0,%xmm4
vextractf32x4 $0,%zmm1,%xmm5
vextractf32x4 $0,%zmm2,%xmm6
vextractf32x4 $0,%zmm3,%xmm7
vmovsd %xmm4,(%rax)
vmovhpd %xmm4,(%rax,%r10,1)
vextractf32x4 $1,%zmm0,%xmm4
vmovsd %xmm4,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm4,(%rax)
vextractf32x4 $2,%zmm0,%xmm4
vmovsd %xmm4,(%rax,%r10,1)
vmovhpd %xmm4,(%rax,%r10,2)
vextractf32x4 $3,%zmm0,%xmm4
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovsd %xmm4,(%rax)
vmovhpd %xmm4,(%rax,%r10,1)
leaq (%rcx,%r11,1),%rax
vmovsd %xmm5,(%rax)
vmovhpd %xmm5,(%rax,%r10,1)
vextractf32x4 $1,%zmm1,%xmm0
vmovsd %xmm0,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm0,(%rax)
vextractf32x4 $2,%zmm1,%xmm0
vmovsd %xmm0,(%rax,%r10,1)
vmovhpd %xmm0,(%rax,%r10,2)
vextractf32x4 $3,%zmm1,%xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovsd %xmm0,(%rax)
vmovhpd %xmm0,(%rax,%r10,1)
leaq (%rcx,%r11,2),%rax
vmovsd %xmm6,(%rax)
vmovhpd %xmm6,(%rax,%r10,1)
vextractf32x4 $1,%zmm2,%xmm0
vmovsd %xmm0,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm0,(%rax)
vextractf32x4 $2,%zmm2,%xmm0
vmovsd %xmm0,(%rax,%r10,1)
vmovhpd %xmm0,(%rax,%r10,2)
vextractf32x4 $3,%zmm2,%xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovsd %xmm0,(%rax)
vmovhpd %xmm0,(%rax,%r10,1)
leaq (%rcx,%r11,1),%rax
leaq (%rax,%r11,2),%rax
vmovsd %xmm7,(%rax)
vmovhpd %xmm7,(%rax,%r10,1)
vextractf32x4 $1,%zmm3,%xmm0
vmovsd %xmm0,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm0,(%rax)
vextractf32x4 $2,%zmm3,%xmm0
vmovsd %xmm0,(%rax,%r10,1)
vmovhpd %xmm0,(%rax,%r10,2)
vextractf32x4 $3,%zmm3,%xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovsd %xmm0,(%rax)
vmovhpd %xmm0,(%rax,%r10,1)
jmp .ukr0_cases_end
.ukr0_case7:
movq %rcx, %rax
vbroadcastsd (%r8), %zmm4
vmulpd %zmm0,%zmm4,%zmm5
vmulpd %zmm1,%zmm4,%zmm0
vmulpd %zmm2,%zmm4,%zmm1
vmulpd %zmm3,%zmm4,%zmm2
vextractf32x4 $0,%zmm5,%xmm3
vextractf32x4 $0,%zmm0,%xmm4
vextractf32x4 $0,%zmm1,%xmm6
vextractf32x4 $0,%zmm2,%xmm7
vmovsd %xmm3,(%rax)
vmovhpd %xmm3,(%rax,%r10,1)
vextractf32x4 $1,%zmm5,%xmm3
vmovsd %xmm3,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm3,(%rax)
vextractf32x4 $2,%zmm5,%xmm3
vmovsd %xmm3,(%rax,%r10,1)
vmovhpd %xmm3,(%rax,%r10,2)
vextractf32x4 $3,%zmm5,%xmm3
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovsd %xmm3,(%rax)
vmovhpd %xmm3,(%rax,%r10,1)
leaq (%rcx,%r11,1),%rax
vmovsd %xmm4,(%rax)
vmovhpd %xmm4,(%rax,%r10,1)
vextractf32x4 $1,%zmm0,%xmm3
vmovsd %xmm3,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm3,(%rax)
vextractf32x4 $2,%zmm0,%xmm3
vmovsd %xmm3,(%rax,%r10,1)
vmovhpd %xmm3,(%rax,%r10,2)
vextractf32x4 $3,%zmm0,%xmm3
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovsd %xmm3,(%rax)
vmovhpd %xmm3,(%rax,%r10,1)
leaq (%rcx,%r11,2),%rax
vmovsd %xmm6,(%rax)
vmovhpd %xmm6,(%rax,%r10,1)
vextractf32x4 $1,%zmm1,%xmm0
vmovsd %xmm0,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm0,(%rax)
vextractf32x4 $2,%zmm1,%xmm0
vmovsd %xmm0,(%rax,%r10,1)
vmovhpd %xmm0,(%rax,%r10,2)
vextractf32x4 $3,%zmm1,%xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovsd %xmm0,(%rax)
vmovhpd %xmm0,(%rax,%r10,1)
leaq (%rcx,%r11,1),%rax
leaq (%rax,%r11,2),%rax
vmovsd %xmm7,(%rax)
vmovhpd %xmm7,(%rax,%r10,1)
vextractf32x4 $1,%zmm2,%xmm0
vmovsd %xmm0,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm0,(%rax)
vextractf32x4 $2,%zmm2,%xmm0
vmovsd %xmm0,(%rax,%r10,1)
vmovhpd %xmm0,(%rax,%r10,2)
vextractf32x4 $3,%zmm2,%xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovsd %xmm0,(%rax)
vmovhpd %xmm0,(%rax,%r10,1)
jmp .ukr0_cases_end
.ukr0_case8:
movq %rcx, %rax
vmovsd (%rax), %xmm4
vmovhpd (%rax,%r10,1), %xmm4, %xmm4
vinsertf32x4 $0,%xmm4,%zmm5,%zmm5
vmovsd (%rax,%r10,2), %xmm4
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm4, %xmm4
vinsertf32x4 $1,%xmm4,%zmm5,%zmm5
vmovsd (%rax,%r10,1), %xmm4
vmovhpd (%rax,%r10,2), %xmm4, %xmm4
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vinsertf32x4 $2,%xmm4,%zmm5,%zmm5
vmovsd (%rax), %xmm4
vmovhpd (%rax,%r10,1), %xmm4, %xmm4
vinsertf32x4 $3,%xmm4,%zmm5,%zmm5
vaddpd %zmm0,%zmm5,%zmm5
vextractf32x4 $0,%zmm5,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm5,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm5,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vextractf32x4 $3,%zmm5,%xmm4
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vmovsd %xmm4,(%rcx)
vmovhpd %xmm4,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm0,%zmm4,%zmm4
vmovsd (%rax,%r10,2), %xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm0, %xmm0
vinsertf32x4 $1,%xmm0,%zmm4,%zmm4
vmovsd (%rax,%r10,1), %xmm0
vmovhpd (%rax,%r10,2), %xmm0, %xmm0
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm0,%zmm4,%zmm4
vmovsd (%rax), %xmm0
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf32x4 $3,%xmm0,%zmm4,%zmm4
vaddpd %zmm1,%zmm4,%zmm4
vextractf32x4 $0,%zmm4,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm4,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm4,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vextractf32x4 $3,%zmm4,%xmm1
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vmovsd %xmm1,(%rcx)
vmovhpd %xmm1,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,2), %xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm0, %xmm0
vinsertf32x4 $1,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,1), %xmm0
vmovhpd (%rax,%r10,2), %xmm0, %xmm0
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm0,%zmm1,%zmm1
vmovsd (%rax), %xmm0
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf32x4 $3,%xmm0,%zmm1,%zmm1
vaddpd %zmm2,%zmm1,%zmm1
vextractf32x4 $0,%zmm1,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vextractf32x4 $3,%zmm1,%xmm2
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vmovsd %xmm2,(%rcx)
vmovhpd %xmm2,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,2), %xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm0, %xmm0
vinsertf32x4 $1,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,1), %xmm0
vmovhpd (%rax,%r10,2), %xmm0, %xmm0
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm0,%zmm1,%zmm1
vmovsd (%rax), %xmm0
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf32x4 $3,%xmm0,%zmm1,%zmm1
vaddpd %zmm3,%zmm1,%zmm1
vextractf32x4 $0,%zmm1,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
vextractf32x4 $3,%zmm1,%xmm0
movq %rax, %rcx
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
jmp .ukr0_cases_end
.ukr0_case9:
movq %rcx, %rax
vmovsd (%rax), %xmm4
vbroadcastsd (%r8), %zmm5
vmovhpd (%rax,%r10,1), %xmm4, %xmm4
vinsertf32x4 $0,%xmm4,%zmm6,%zmm6
vmovsd (%rax,%r10,2), %xmm4
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm4, %xmm4
vinsertf32x4 $1,%xmm4,%zmm6,%zmm6
vmovsd (%rax,%r10,1), %xmm4
vmovhpd (%rax,%r10,2), %xmm4, %xmm4
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vinsertf32x4 $2,%xmm4,%zmm6,%zmm6
vmovsd (%rax), %xmm4
vmovhpd (%rax,%r10,1), %xmm4, %xmm4
vinsertf32x4 $3,%xmm4,%zmm6,%zmm6
vfmadd231pd %zmm0,%zmm5,%zmm6
vextractf32x4 $0,%zmm6,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm6,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm6,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vextractf32x4 $3,%zmm6,%xmm4
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vmovsd %xmm4,(%rcx)
vmovhpd %xmm4,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm0,%zmm4,%zmm4
vmovsd (%rax,%r10,2), %xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm0, %xmm0
vinsertf32x4 $1,%xmm0,%zmm4,%zmm4
vmovsd (%rax,%r10,1), %xmm0
vmovhpd (%rax,%r10,2), %xmm0, %xmm0
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm0,%zmm4,%zmm4
vmovsd (%rax), %xmm0
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf32x4 $3,%xmm0,%zmm4,%zmm4
vfmadd231pd %zmm1,%zmm5,%zmm4
vextractf32x4 $0,%zmm4,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm4,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm4,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vextractf32x4 $3,%zmm4,%xmm1
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vmovsd %xmm1,(%rcx)
vmovhpd %xmm1,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,2), %xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm0, %xmm0
vinsertf32x4 $1,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,1), %xmm0
vmovhpd (%rax,%r10,2), %xmm0, %xmm0
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm0,%zmm1,%zmm1
vmovsd (%rax), %xmm0
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf32x4 $3,%xmm0,%zmm1,%zmm1
vfmadd231pd %zmm2,%zmm5,%zmm1
vextractf32x4 $0,%zmm1,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vextractf32x4 $3,%zmm1,%xmm2
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vmovsd %xmm2,(%rcx)
vmovhpd %xmm2,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,2), %xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm0, %xmm0
vinsertf32x4 $1,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,1), %xmm0
vmovhpd (%rax,%r10,2), %xmm0, %xmm0
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm0,%zmm1,%zmm1
vmovsd (%rax), %xmm0
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf32x4 $3,%xmm0,%zmm1,%zmm1
vfmadd231pd %zmm3,%zmm5,%zmm1
vextractf32x4 $0,%zmm1,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
vextractf32x4 $3,%zmm1,%xmm0
movq %rax, %rcx
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
jmp .ukr0_cases_end
.ukr0_case10:
movq %rcx, %rax
vmovsd (%rax), %xmm4
vbroadcastsd (%r9), %zmm5
vmovhpd (%rax,%r10,1), %xmm4, %xmm4
vinsertf32x4 $0,%xmm4,%zmm6,%zmm6
vmovsd (%rax,%r10,2), %xmm4
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm4, %xmm4
vinsertf32x4 $1,%xmm4,%zmm6,%zmm6
vmovsd (%rax,%r10,1), %xmm4
vmovhpd (%rax,%r10,2), %xmm4, %xmm4
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vinsertf32x4 $2,%xmm4,%zmm6,%zmm6
vmovsd (%rax), %xmm4
vmovhpd (%rax,%r10,1), %xmm4, %xmm4
vinsertf32x4 $3,%xmm4,%zmm6,%zmm6
vfmadd231pd %zmm6,%zmm5,%zmm0
vextractf32x4 $0,%zmm0,%xmm4
vmovsd %xmm4,(%rcx)
vmovhpd %xmm4,(%rcx,%r10,1)
vextractf32x4 $1,%zmm0,%xmm4
vmovsd %xmm4,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm4,(%rcx)
vextractf32x4 $2,%zmm0,%xmm4
vmovsd %xmm4,(%rcx,%r10,1)
vmovhpd %xmm4,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm4
vextractf32x4 $3,%zmm0,%xmm6
vmovhpd (%rax,%r10,1), %xmm4, %xmm4
vmovsd %xmm6,(%rcx)
vmovhpd %xmm6,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm4,%zmm0,%zmm0
vmovsd (%rax,%r10,2), %xmm4
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm4, %xmm4
vinsertf32x4 $1,%xmm4,%zmm0,%zmm0
vmovsd (%rax,%r10,1), %xmm4
vmovhpd (%rax,%r10,2), %xmm4, %xmm4
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm4,%zmm0,%zmm0
vmovsd (%rax), %xmm4
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm4, %xmm4
vinsertf32x4 $3,%xmm4,%zmm0,%zmm0
vfmadd231pd %zmm0,%zmm5,%zmm1
vextractf32x4 $0,%zmm1,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vextractf32x4 $3,%zmm1,%xmm4
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vmovsd %xmm4,(%rcx)
vmovhpd %xmm4,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,2), %xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm0, %xmm0
vinsertf32x4 $1,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,1), %xmm0
vmovhpd (%rax,%r10,2), %xmm0, %xmm0
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm0,%zmm1,%zmm1
vmovsd (%rax), %xmm0
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf32x4 $3,%xmm0,%zmm1,%zmm1
vfmadd231pd %zmm1,%zmm5,%zmm2
vextractf32x4 $0,%zmm2,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm2,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm2,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vextractf32x4 $3,%zmm2,%xmm1
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vmovsd %xmm1,(%rcx)
vmovhpd %xmm1,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,2), %xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm0, %xmm0
vinsertf32x4 $1,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,1), %xmm0
vmovhpd (%rax,%r10,2), %xmm0, %xmm0
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm0,%zmm1,%zmm1
vmovsd (%rax), %xmm0
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf32x4 $3,%xmm0,%zmm1,%zmm1
vfmadd231pd %zmm1,%zmm5,%zmm3
vextractf32x4 $0,%zmm3,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm3,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm3,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
vextractf32x4 $3,%zmm3,%xmm0
movq %rax, %rcx
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
jmp .ukr0_cases_end
.ukr0_case11:
movq %rcx, %rax
vmovsd (%rax), %xmm4
vbroadcastsd (%r9), %zmm5
vbroadcastsd (%r8), %zmm6
vmovhpd (%rax,%r10,1), %xmm4, %xmm4
vinsertf32x4 $0,%xmm4,%zmm7,%zmm7
vmovsd (%rax,%r10,2), %xmm4
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm4, %xmm4
vinsertf32x4 $1,%xmm4,%zmm7,%zmm7
vmovsd (%rax,%r10,1), %xmm4
vmovhpd (%rax,%r10,2), %xmm4, %xmm4
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vinsertf32x4 $2,%xmm4,%zmm7,%zmm7
vmovsd (%rax), %xmm4
vmovhpd (%rax,%r10,1), %xmm4, %xmm4
vinsertf32x4 $3,%xmm4,%zmm7,%zmm7
vmulpd %zmm7,%zmm5,%zmm7
vfmadd231pd %zmm0,%zmm6,%zmm7
vextractf32x4 $0,%zmm7,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm7,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm7,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vextractf32x4 $3,%zmm7,%xmm4
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vmovsd %xmm4,(%rcx)
vmovhpd %xmm4,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm0,%zmm4,%zmm4
vmovsd (%rax,%r10,2), %xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm0, %xmm0
vinsertf32x4 $1,%xmm0,%zmm4,%zmm4
vmovsd (%rax,%r10,1), %xmm0
vmovhpd (%rax,%r10,2), %xmm0, %xmm0
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm0,%zmm4,%zmm4
vmovsd (%rax), %xmm0
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf32x4 $3,%xmm0,%zmm4,%zmm4
vmulpd %zmm4,%zmm5,%zmm4
vfmadd231pd %zmm1,%zmm6,%zmm4
vextractf32x4 $0,%zmm4,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm4,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm4,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vextractf32x4 $3,%zmm4,%xmm1
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vmovsd %xmm1,(%rcx)
vmovhpd %xmm1,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,2), %xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm0, %xmm0
vinsertf32x4 $1,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,1), %xmm0
vmovhpd (%rax,%r10,2), %xmm0, %xmm0
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm0,%zmm1,%zmm1
vmovsd (%rax), %xmm0
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf32x4 $3,%xmm0,%zmm1,%zmm1
vmulpd %zmm1,%zmm5,%zmm1
vfmadd231pd %zmm2,%zmm6,%zmm1
vextractf32x4 $0,%zmm1,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
movq $6,%rdx
imulq %r10,%rdx
subq %rdx,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vextractf32x4 $3,%zmm1,%xmm2
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vmovsd %xmm2,(%rcx)
vmovhpd %xmm2,(%rcx,%r10,1)
vinsertf32x4 $0,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,2), %xmm0
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm0, %xmm0
vinsertf32x4 $1,%xmm0,%zmm1,%zmm1
vmovsd (%rax,%r10,1), %xmm0
vmovhpd (%rax,%r10,2), %xmm0, %xmm0
leaq (%rcx,%r11,1),%rax
movq $6,%rdx
imulq %r10,%rdx
vinsertf32x4 $2,%xmm0,%zmm1,%zmm1
vmovsd (%rax), %xmm0
subq %rdx,%rcx
addq %r11,%rcx
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf32x4 $3,%xmm0,%zmm1,%zmm1
vmulpd %zmm1,%zmm5,%zmm1
vfmadd231pd %zmm3,%zmm6,%zmm1
vextractf32x4 $0,%zmm1,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf32x4 $1,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
addq %r10,%rcx
leaq (%rcx,%r10,2),%rcx
vmovhpd %xmm0,(%rcx)
vextractf32x4 $2,%zmm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,1)
vmovhpd %xmm0,(%rcx,%r10,2)
vextractf32x4 $3,%zmm1,%xmm0
movq %rax, %rcx
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dgemm_ukrgen_avx512_vm_8x4_asm, .-bli_dgemm_ukrgen_avx512_vm_8x4_asm
.section .note.GNU-stack,"",%progbits
