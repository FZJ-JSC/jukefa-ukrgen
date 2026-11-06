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
# r10 = stride(C,m)
# r11 = stride(C,n)
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
movq 16(%rsp), %r11
movq %r10, %rax
addq $-8,%rax
test %rax,%rax
jz .ukr0_ok1
jmp .ukr0_try0
.ukr0_ok1:
vmovsd (%r9), %xmm2
vpxor %xmm3,%xmm3,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try2
jp .ukr0_try2
vmovsd (%r8), %xmm2
movq $4607182418800017408,%rax
vmovq %rax,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try3
jp .ukr0_try3
jmp .ukr0_case0
.ukr0_try3:
jmp .ukr0_case1
.ukr0_try2:
vmovsd (%r9), %xmm2
movq $4607182418800017408,%rax
vmovq %rax,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try4
jp .ukr0_try4
vmovsd (%r8), %xmm2
movq $4607182418800017408,%rax
vmovq %rax,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try5
jp .ukr0_try5
jmp .ukr0_case2
.ukr0_try5:
jmp .ukr0_case3
.ukr0_try4:
vmovsd (%r8), %xmm2
movq $4607182418800017408,%rax
vmovq %rax,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try6
jp .ukr0_try6
jmp .ukr0_case4
.ukr0_try6:
jmp .ukr0_case5
.ukr0_try0:
vmovsd (%r9), %xmm2
vpxor %xmm3,%xmm3,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try7
jp .ukr0_try7
vmovsd (%r8), %xmm2
movq $4607182418800017408,%rax
vmovq %rax,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try8
jp .ukr0_try8
jmp .ukr0_case6
.ukr0_try8:
jmp .ukr0_case7
.ukr0_try7:
vmovsd (%r9), %xmm2
movq $4607182418800017408,%rax
vmovq %rax,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try9
jp .ukr0_try9
vmovsd (%r8), %xmm2
movq $4607182418800017408,%rax
vmovq %rax,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try10
jp .ukr0_try10
jmp .ukr0_case8
.ukr0_try10:
jmp .ukr0_case9
.ukr0_try9:
vmovsd (%r8), %xmm2
movq $4607182418800017408,%rax
vmovq %rax,%xmm3
vucomisd %xmm3,%xmm2
jne .ukr0_try11
jp .ukr0_try11
jmp .ukr0_case10
.ukr0_try11:
jmp .ukr0_case11
jmp .ukr0_cases_end
.ukr0_case0:
movq %rcx, %rax
movq %rcx, %rdx
vmovupd %ymm0, (%rax)
vmovupd %ymm1, (%rax,%r11,1)
jmp .ukr0_cases_end
.ukr0_case1:
movq %rcx, %rax
movq %rcx, %rdx
vbroadcastsd (%r8), %ymm2
vmulpd %ymm0,%ymm2,%ymm3
vmulpd %ymm1,%ymm2,%ymm0
vmovupd %ymm3, (%rax)
vmovupd %ymm0, (%rax,%r11,1)
jmp .ukr0_cases_end
.ukr0_case2:
movq %rcx, %rax
movq %rcx, %rdx
vmovupd (%rax), %ymm2
vmovupd (%rax,%r11,1), %ymm3
vaddpd %ymm0,%ymm2,%ymm2
vaddpd %ymm1,%ymm3,%ymm3
vmovupd %ymm2, (%rdx)
vmovupd %ymm3, (%rdx,%r11,1)
jmp .ukr0_cases_end
.ukr0_case3:
movq %rcx, %rax
movq %rcx, %rdx
vbroadcastsd (%r8), %ymm2
vmovupd (%rax), %ymm3
vmovupd (%rax,%r11,1), %ymm4
vfmadd231pd %ymm0,%ymm2,%ymm3
vfmadd231pd %ymm1,%ymm2,%ymm4
vmovupd %ymm3, (%rdx)
vmovupd %ymm4, (%rdx,%r11,1)
jmp .ukr0_cases_end
.ukr0_case4:
movq %rcx, %rax
movq %rcx, %rdx
vbroadcastsd (%r9), %ymm2
vmovupd (%rax), %ymm3
vmovupd (%rax,%r11,1), %ymm4
vfmadd231pd %ymm3,%ymm2,%ymm0
vfmadd231pd %ymm4,%ymm2,%ymm1
vmovupd %ymm0, (%rdx)
vmovupd %ymm1, (%rdx,%r11,1)
jmp .ukr0_cases_end
.ukr0_case5:
movq %rcx, %rax
movq %rcx, %rdx
vbroadcastsd (%r9), %ymm2
vmovupd (%rax), %ymm3
vmovupd (%rax,%r11,1), %ymm4
vbroadcastsd (%r8), %ymm5
vmulpd %ymm3,%ymm2,%ymm3
vmulpd %ymm4,%ymm2,%ymm4
vfmadd231pd %ymm0,%ymm5,%ymm3
vfmadd231pd %ymm1,%ymm5,%ymm4
vmovupd %ymm3, (%rdx)
vmovupd %ymm4, (%rdx,%r11,1)
jmp .ukr0_cases_end
.ukr0_case6:
movq %rcx, %rax
vextractf128 $0,%ymm0,%xmm2
vextractf128 $0,%ymm1,%xmm3
vmovsd %xmm2,(%rax)
vmovhpd %xmm2,(%rax,%r10,1)
vextractf128 $1,%ymm0,%xmm2
vmovsd %xmm2,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm2,(%rax)
leaq (%rcx,%r11,1),%rax
vmovsd %xmm3,(%rax)
vmovhpd %xmm3,(%rax,%r10,1)
vextractf128 $1,%ymm1,%xmm0
vmovsd %xmm0,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm0,(%rax)
jmp .ukr0_cases_end
.ukr0_case7:
movq %rcx, %rax
vbroadcastsd (%r8), %ymm2
vmulpd %ymm0,%ymm2,%ymm3
vmulpd %ymm1,%ymm2,%ymm0
vextractf128 $0,%ymm3,%xmm1
vextractf128 $0,%ymm0,%xmm2
vmovsd %xmm1,(%rax)
vmovhpd %xmm1,(%rax,%r10,1)
vextractf128 $1,%ymm3,%xmm1
vmovsd %xmm1,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm1,(%rax)
leaq (%rcx,%r11,1),%rax
vmovsd %xmm2,(%rax)
vmovhpd %xmm2,(%rax,%r10,1)
vextractf128 $1,%ymm0,%xmm1
vmovsd %xmm1,(%rax,%r10,2)
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd %xmm1,(%rax)
jmp .ukr0_cases_end
.ukr0_case8:
movq %rcx, %rax
vmovsd (%rax), %xmm2
vmovhpd (%rax,%r10,1), %xmm2, %xmm2
vinsertf128 $0,%xmm2,%ymm3,%ymm3
vmovsd (%rax,%r10,2), %xmm2
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm2, %xmm2
vinsertf128 $1,%xmm2,%ymm3,%ymm3
vaddpd %ymm0,%ymm3,%ymm3
vextractf128 $0,%ymm3,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf128 $1,%ymm3,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
subq %r10,%rax
subq %r10,%rax
subq %r10,%rax
addq %r11,%rax
vmovsd (%rax), %xmm2
vmovhpd %xmm0,(%rcx)
vmovhpd (%rax,%r10,1), %xmm2, %xmm2
vinsertf128 $0,%xmm2,%ymm0,%ymm0
vmovsd (%rax,%r10,2), %xmm2
leaq (%rcx,%r11,1),%rax
subq %r10,%rcx
subq %r10,%rcx
vmovhpd (%rax), %xmm2, %xmm2
subq %r10,%rcx
addq %r11,%rcx
vinsertf128 $1,%xmm2,%ymm0,%ymm0
vaddpd %ymm1,%ymm0,%ymm0
vextractf128 $0,%ymm0,%xmm1
vmovsd %xmm1,(%rcx)
vmovhpd %xmm1,(%rcx,%r10,1)
vextractf128 $1,%ymm0,%xmm1
vmovsd %xmm1,(%rcx,%r10,2)
movq %rax, %rcx
vmovhpd %xmm1,(%rcx)
jmp .ukr0_cases_end
.ukr0_case9:
movq %rcx, %rax
vmovsd (%rax), %xmm2
vbroadcastsd (%r8), %ymm3
vmovhpd (%rax,%r10,1), %xmm2, %xmm2
vinsertf128 $0,%xmm2,%ymm4,%ymm4
vmovsd (%rax,%r10,2), %xmm2
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm2, %xmm2
vinsertf128 $1,%xmm2,%ymm4,%ymm4
vfmadd231pd %ymm0,%ymm3,%ymm4
vextractf128 $0,%ymm4,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf128 $1,%ymm4,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
subq %r10,%rax
subq %r10,%rax
subq %r10,%rax
addq %r11,%rax
vmovsd (%rax), %xmm2
vmovhpd %xmm0,(%rcx)
vmovhpd (%rax,%r10,1), %xmm2, %xmm2
vinsertf128 $0,%xmm2,%ymm0,%ymm0
vmovsd (%rax,%r10,2), %xmm2
leaq (%rcx,%r11,1),%rax
subq %r10,%rcx
subq %r10,%rcx
vmovhpd (%rax), %xmm2, %xmm2
subq %r10,%rcx
addq %r11,%rcx
vinsertf128 $1,%xmm2,%ymm0,%ymm0
vfmadd231pd %ymm1,%ymm3,%ymm0
vextractf128 $0,%ymm0,%xmm1
vmovsd %xmm1,(%rcx)
vmovhpd %xmm1,(%rcx,%r10,1)
vextractf128 $1,%ymm0,%xmm1
vmovsd %xmm1,(%rcx,%r10,2)
movq %rax, %rcx
vmovhpd %xmm1,(%rcx)
jmp .ukr0_cases_end
.ukr0_case10:
movq %rcx, %rax
vmovsd (%rax), %xmm2
vbroadcastsd (%r9), %ymm3
vmovhpd (%rax,%r10,1), %xmm2, %xmm2
vinsertf128 $0,%xmm2,%ymm4,%ymm4
vmovsd (%rax,%r10,2), %xmm2
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm2, %xmm2
vinsertf128 $1,%xmm2,%ymm4,%ymm4
vfmadd231pd %ymm4,%ymm3,%ymm0
vextractf128 $0,%ymm0,%xmm2
vmovsd %xmm2,(%rcx)
vmovhpd %xmm2,(%rcx,%r10,1)
vextractf128 $1,%ymm0,%xmm2
vmovsd %xmm2,(%rcx,%r10,2)
movq %rax, %rcx
subq %r10,%rax
subq %r10,%rax
subq %r10,%rax
addq %r11,%rax
vmovsd (%rax), %xmm0
vmovhpd %xmm2,(%rcx)
vmovhpd (%rax,%r10,1), %xmm0, %xmm0
vinsertf128 $0,%xmm0,%ymm2,%ymm2
vmovsd (%rax,%r10,2), %xmm0
leaq (%rcx,%r11,1),%rax
subq %r10,%rcx
subq %r10,%rcx
vmovhpd (%rax), %xmm0, %xmm0
subq %r10,%rcx
addq %r11,%rcx
vinsertf128 $1,%xmm0,%ymm2,%ymm2
vfmadd231pd %ymm2,%ymm3,%ymm1
vextractf128 $0,%ymm1,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf128 $1,%ymm1,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
vmovhpd %xmm0,(%rcx)
jmp .ukr0_cases_end
.ukr0_case11:
movq %rcx, %rax
vmovsd (%rax), %xmm2
vbroadcastsd (%r9), %ymm3
vbroadcastsd (%r8), %ymm4
vmovhpd (%rax,%r10,1), %xmm2, %xmm2
vinsertf128 $0,%xmm2,%ymm5,%ymm5
vmovsd (%rax,%r10,2), %xmm2
addq %r10,%rax
leaq (%rax,%r10,2),%rax
vmovhpd (%rax), %xmm2, %xmm2
vinsertf128 $1,%xmm2,%ymm5,%ymm5
vmulpd %ymm5,%ymm3,%ymm5
vfmadd231pd %ymm0,%ymm4,%ymm5
vextractf128 $0,%ymm5,%xmm0
vmovsd %xmm0,(%rcx)
vmovhpd %xmm0,(%rcx,%r10,1)
vextractf128 $1,%ymm5,%xmm0
vmovsd %xmm0,(%rcx,%r10,2)
movq %rax, %rcx
subq %r10,%rax
subq %r10,%rax
subq %r10,%rax
addq %r11,%rax
vmovsd (%rax), %xmm2
vmovhpd %xmm0,(%rcx)
vmovhpd (%rax,%r10,1), %xmm2, %xmm2
vinsertf128 $0,%xmm2,%ymm0,%ymm0
vmovsd (%rax,%r10,2), %xmm2
leaq (%rcx,%r11,1),%rax
subq %r10,%rcx
subq %r10,%rcx
vmovhpd (%rax), %xmm2, %xmm2
subq %r10,%rcx
addq %r11,%rcx
vinsertf128 $1,%xmm2,%ymm0,%ymm0
vmulpd %ymm0,%ymm3,%ymm0
vfmadd231pd %ymm1,%ymm4,%ymm0
vextractf128 $0,%ymm0,%xmm1
vmovsd %xmm1,(%rcx)
vmovhpd %xmm1,(%rcx,%r10,1)
vextractf128 $1,%ymm0,%xmm1
vmovsd %xmm1,(%rcx,%r10,2)
movq %rax, %rcx
vmovhpd %xmm1,(%rcx)
.ukr0_cases_end:
ret
.cfi_endproc
.size bli_dgemm_ukrgen_avx256_vm_4x2_asm, .-bli_dgemm_ukrgen_avx256_vm_4x2_asm
.section .note.GNU-stack,"",%progbits
