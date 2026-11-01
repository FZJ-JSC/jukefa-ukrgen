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
# r10 = stride(C,n)
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
vmovsd (%r9), %xmm4
vpxord %xmm5,%xmm5,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try1
jp .ukr0_try1
vmovsd (%r8), %xmm4
movq $4607182418800017408,%r11
vmovq %r11,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try1
jp .ukr0_try1
jmp .ukr0_case0
.ukr0_try1:
vmovsd (%r9), %xmm4
vpxord %xmm5,%xmm5,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try2
jp .ukr0_try2
jmp .ukr0_case1
.ukr0_try2:
vmovsd (%r9), %xmm4
movq $4607182418800017408,%r11
vmovq %r11,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try3
jp .ukr0_try3
vmovsd (%r8), %xmm4
movq $4607182418800017408,%r11
vmovq %r11,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try3
jp .ukr0_try3
jmp .ukr0_case2
.ukr0_try3:
vmovsd (%r9), %xmm4
movq $4607182418800017408,%r11
vmovq %r11,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try4
jp .ukr0_try4
jmp .ukr0_case3
.ukr0_try4:
vmovsd (%r8), %xmm4
movq $4607182418800017408,%r11
vmovq %r11,%xmm5
vucomisd %xmm5,%xmm4
jne .ukr0_try5
jp .ukr0_try5
jmp .ukr0_case4
.ukr0_try5:
jmp .ukr0_case5
.ukr0_try6:
jmp .ukr0_cases_end
.ukr0_case0:
movq %rcx, %r11
vmovupd %zmm0, (%r11)
vmovupd %zmm1, (%r11,%r10,1)
vmovupd %zmm2, (%r11,%r10,2)
addq %r10,%r11
leaq (%r11,%r10,2),%r11
vmovupd %zmm3, (%r11)
jmp .ukr0_cases_end
.ukr0_case1:
movq %rcx, %r11
vbroadcastsd (%r8), %zmm4
vmulpd %zmm0,%zmm4,%zmm5
vmulpd %zmm1,%zmm4,%zmm0
vmulpd %zmm2,%zmm4,%zmm1
vmulpd %zmm3,%zmm4,%zmm2
vmovupd %zmm5, (%r11)
vmovupd %zmm0, (%r11,%r10,1)
vmovupd %zmm1, (%r11,%r10,2)
addq %r10,%r11
leaq (%r11,%r10,2),%r11
vmovupd %zmm2, (%r11)
jmp .ukr0_cases_end
.ukr0_case2:
movq %rcx, %r11
vmovupd (%r11), %zmm4
vmovupd (%r11,%r10,1), %zmm5
vmovupd (%r11,%r10,2), %zmm6
addq %r10,%r11
leaq (%r11,%r10,2),%r11
vmovupd (%r11), %zmm7
vaddpd %zmm0,%zmm4,%zmm4
vaddpd %zmm1,%zmm5,%zmm5
vaddpd %zmm2,%zmm6,%zmm6
vaddpd %zmm3,%zmm7,%zmm7
vmovupd %zmm4, (%rcx)
vmovupd %zmm5, (%rcx,%r10,1)
vmovupd %zmm6, (%rcx,%r10,2)
movq %r11, %rcx
vmovupd %zmm7, (%rcx)
jmp .ukr0_cases_end
.ukr0_case3:
movq %rcx, %r11
vmovupd (%r11), %zmm4
vmovupd (%r11,%r10,1), %zmm5
vmovupd (%r11,%r10,2), %zmm6
vbroadcastsd (%r8), %zmm7
addq %r10,%r11
leaq (%r11,%r10,2),%r11
vmovupd (%r11), %zmm8
vfmadd231pd %zmm0,%zmm7,%zmm4
vfmadd231pd %zmm1,%zmm7,%zmm5
vfmadd231pd %zmm2,%zmm7,%zmm6
vfmadd231pd %zmm3,%zmm7,%zmm8
vmovupd %zmm4, (%rcx)
vmovupd %zmm5, (%rcx,%r10,1)
vmovupd %zmm6, (%rcx,%r10,2)
movq %r11, %rcx
vmovupd %zmm8, (%rcx)
jmp .ukr0_cases_end
.ukr0_case4:
movq %rcx, %r11
vmovupd (%r11), %zmm4
vmovupd (%r11,%r10,1), %zmm5
vmovupd (%r11,%r10,2), %zmm6
vbroadcastsd (%r9), %zmm7
addq %r10,%r11
leaq (%r11,%r10,2),%r11
vmovupd (%r11), %zmm8
vfmadd231pd %zmm4,%zmm7,%zmm0
vfmadd231pd %zmm5,%zmm7,%zmm1
vfmadd231pd %zmm6,%zmm7,%zmm2
vfmadd231pd %zmm8,%zmm7,%zmm3
vmovupd %zmm0, (%rcx)
vmovupd %zmm1, (%rcx,%r10,1)
vmovupd %zmm2, (%rcx,%r10,2)
movq %r11, %rcx
vmovupd %zmm3, (%rcx)
jmp .ukr0_cases_end
.ukr0_case5:
movq %rcx, %r11
vmovupd (%r11), %zmm4
vmovupd (%r11,%r10,1), %zmm5
vmovupd (%r11,%r10,2), %zmm6
vbroadcastsd (%r9), %zmm7
vbroadcastsd (%r8), %zmm8
vmulpd %zmm4,%zmm7,%zmm4
addq %r10,%r11
leaq (%r11,%r10,2),%r11
vmulpd %zmm5,%zmm7,%zmm5
vmulpd %zmm6,%zmm7,%zmm6
vfmadd231pd %zmm0,%zmm8,%zmm4
vmovupd (%r11), %zmm0
vfmadd231pd %zmm1,%zmm8,%zmm5
vfmadd231pd %zmm2,%zmm8,%zmm6
vmovupd %zmm4, (%rcx)
vmulpd %zmm0,%zmm7,%zmm0
vmovupd %zmm5, (%rcx,%r10,1)
vmovupd %zmm6, (%rcx,%r10,2)
movq %r11, %rcx
vfmadd231pd %zmm3,%zmm8,%zmm0
vmovupd %zmm0, (%rcx)
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dgemm_ukrgen_avx512_vm_8x4_asm, .-bli_dgemm_ukrgen_avx512_vm_8x4_asm
.section .note.GNU-stack,"",%progbits
