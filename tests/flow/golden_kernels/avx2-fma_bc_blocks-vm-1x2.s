.text
.global bli_dgemm_ukrgen_avx256_vm_4x2_asm
.type bli_dgemm_ukrgen_avx256_vm_4x2_asm, %function
bli_dgemm_ukrgen_avx256_vm_4x2_asm:
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
vpxor %ymm0,%ymm0,%ymm0
vpxor %ymm1,%ymm1,%ymm1
test %rdi,%rdi
jz .ukr1_done
vmovupd (%rsi), %ymm2
vbroadcastsd (%rdx), %ymm3
vbroadcastsd 8(%rdx), %ymm4
addq $32,%rsi
addq $16,%rdx
addq $-1,%rdi
test %rdi,%rdi
jz .ukr1_last
.ukr1_loop:
addq $-1,%rdi
vfmadd231pd %ymm2,%ymm3,%ymm0
vfmadd231pd %ymm2,%ymm4,%ymm1
vmovupd (%rsi), %ymm5
vbroadcastsd (%rdx), %ymm6
vbroadcastsd 8(%rdx), %ymm7
vmovupd 32(%rsi), %ymm8
vbroadcastsd 16(%rdx), %ymm9
vfmadd231pd %ymm5,%ymm6,%ymm0
vfmadd231pd %ymm5,%ymm7,%ymm1
vbroadcastsd 24(%rdx), %ymm10
vmovupd 64(%rsi), %ymm11
vfmadd231pd %ymm8,%ymm9,%ymm0
vbroadcastsd 32(%rdx), %ymm12
vfmadd231pd %ymm8,%ymm10,%ymm1
vbroadcastsd 40(%rdx), %ymm13
vmovupd 96(%rsi), %ymm2
vbroadcastsd 48(%rdx), %ymm3
vbroadcastsd 56(%rdx), %ymm4
vfmadd231pd %ymm11,%ymm12,%ymm0
vfmadd231pd %ymm11,%ymm13,%ymm1
addq $128,%rsi
addq $64,%rdx
test %rdi,%rdi
jnz .ukr1_loop
.ukr1_last:
vfmadd231pd %ymm2,%ymm3,%ymm0
vfmadd231pd %ymm2,%ymm4,%ymm1
vmovupd (%rsi), %ymm5
vbroadcastsd (%rdx), %ymm6
vbroadcastsd 8(%rdx), %ymm7
vmovupd 32(%rsi), %ymm8
vbroadcastsd 16(%rdx), %ymm9
vfmadd231pd %ymm5,%ymm6,%ymm0
vfmadd231pd %ymm5,%ymm7,%ymm1
vbroadcastsd 24(%rdx), %ymm10
vmovupd 64(%rsi), %ymm11
vfmadd231pd %ymm8,%ymm9,%ymm0
vbroadcastsd 32(%rdx), %ymm12
vfmadd231pd %ymm8,%ymm10,%ymm1
vbroadcastsd 40(%rdx), %ymm13
addq $96,%rsi
vfmadd231pd %ymm11,%ymm12,%ymm0
addq $48,%rdx
vfmadd231pd %ymm11,%ymm13,%ymm1
.ukr1_done:
test %r10,%r10
jz .ukr1_taildone
.ukr1_tail:
addq $-1,%r10
vmovupd (%rsi), %ymm2
vbroadcastsd (%rdx), %ymm3
vbroadcastsd 8(%rdx), %ymm4
vfmadd231pd %ymm2,%ymm3,%ymm0
vfmadd231pd %ymm2,%ymm4,%ymm1
addq $32,%rsi
addq $16,%rdx
test %r10,%r10
jnz .ukr1_tail
.ukr1_taildone:
movq 8(%rsp), %r10
vmovsd (%r9), %xmm2
vpxor %xmm3,%xmm3,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try1
jp .ukr0_try1
vmovsd (%r8), %xmm2
movq $4607182418800017408,%r11
vmovq %r11,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try1
jp .ukr0_try1
jmp .ukr0_case0
.ukr0_try1:
vmovsd (%r9), %xmm2
vpxor %xmm3,%xmm3,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try2
jp .ukr0_try2
jmp .ukr0_case1
.ukr0_try2:
vmovsd (%r9), %xmm2
movq $4607182418800017408,%r11
vmovq %r11,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try3
jp .ukr0_try3
vmovsd (%r8), %xmm2
movq $4607182418800017408,%r11
vmovq %r11,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try3
jp .ukr0_try3
jmp .ukr0_case2
.ukr0_try3:
vmovsd (%r9), %xmm2
movq $4607182418800017408,%r11
vmovq %r11,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try4
jp .ukr0_try4
jmp .ukr0_case3
.ukr0_try4:
vmovsd (%r8), %xmm2
movq $4607182418800017408,%r11
vmovq %r11,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try5
jp .ukr0_try5
jmp .ukr0_case4
.ukr0_try5:
jmp .ukr0_case5
.ukr0_try6:
jmp .ukr0_cases_end
.ukr0_case0:
movq %rcx, %r11
vmovupd %ymm0, (%r11)
vmovupd %ymm1, (%r11,%r10,1)
jmp .ukr0_cases_end
.ukr0_case1:
movq %rcx, %r11
vbroadcastsd (%r8), %ymm2
vmulpd %ymm0,%ymm2,%ymm3
vmulpd %ymm1,%ymm2,%ymm0
vmovupd %ymm3, (%r11)
vmovupd %ymm0, (%r11,%r10,1)
jmp .ukr0_cases_end
.ukr0_case2:
movq %rcx, %r11
vmovupd (%r11), %ymm2
vmovupd (%r11,%r10,1), %ymm3
vaddpd %ymm0,%ymm2,%ymm2
vaddpd %ymm1,%ymm3,%ymm3
vmovupd %ymm2, (%rcx)
vmovupd %ymm3, (%rcx,%r10,1)
jmp .ukr0_cases_end
.ukr0_case3:
movq %rcx, %r11
vmovupd (%r11), %ymm2
vbroadcastsd (%r8), %ymm3
vmovupd (%r11,%r10,1), %ymm4
vfmadd231pd %ymm0,%ymm3,%ymm2
vfmadd231pd %ymm1,%ymm3,%ymm4
vmovupd %ymm2, (%rcx)
vmovupd %ymm4, (%rcx,%r10,1)
jmp .ukr0_cases_end
.ukr0_case4:
movq %rcx, %r11
vmovupd (%r11), %ymm2
vbroadcastsd (%r9), %ymm3
vmovupd (%r11,%r10,1), %ymm4
vfmadd231pd %ymm2,%ymm3,%ymm0
vfmadd231pd %ymm4,%ymm3,%ymm1
vmovupd %ymm0, (%rcx)
vmovupd %ymm1, (%rcx,%r10,1)
jmp .ukr0_cases_end
.ukr0_case5:
movq %rcx, %r11
vmovupd (%r11), %ymm2
vbroadcastsd (%r9), %ymm3
vmovupd (%r11,%r10,1), %ymm4
vbroadcastsd (%r8), %ymm5
vmulpd %ymm2,%ymm3,%ymm2
vmulpd %ymm4,%ymm3,%ymm4
vfmadd231pd %ymm0,%ymm5,%ymm2
vfmadd231pd %ymm1,%ymm5,%ymm4
vmovupd %ymm2, (%rcx)
vmovupd %ymm4, (%rcx,%r10,1)
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dgemm_ukrgen_avx256_vm_4x2_asm, .-bli_dgemm_ukrgen_avx256_vm_4x2_asm
.section .note.GNU-stack,"",%progbits
