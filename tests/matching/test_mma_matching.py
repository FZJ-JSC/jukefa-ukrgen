# ------------------------------------------------------------------------------
# SPDX-License-Identifier: MIT OR GPL-3.0-or-later
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@fz-juelich.de>
# Copyright (C) 2021 Stepan Nassyr <s.nassyr@xcpp.org>
# ------------------------------------------------------------------------------

"""
Testsuite for matching arithmetic instruction to a matrix-multiply-accumulate
"""

import logging
import unittest
from typing import Any

from ukrgen.matching.math import (
    HW_FADD_AST,
    HW_FDOTA_AST,
    HW_FMA_AST,
    HW_FMUL_AST,
    HW_FOPA_AST,
    HW_MMA_AST,
    ast_node,
    decimate_index,
    expression_node,
    extract_deepest_operation,
    generate_variants,
    get_operand_io,
    get_operands,
    map_and_match,
    operand_ref,
    operation,
    simplify_ast,
    solve_requirement,
    transform_ast,
    transform_operand,
    transformation as tf,
    req_solution_step as rsstep
)

# uncomment this for debugging
#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def print_solution(solutions : list[list[rsstep]]):
    
    for i,s in enumerate(solutions):
        print(f"Solution {i}:")
        for j,op in enumerate(s):
            print(f"  Operation {j}")
            print(f"    AST: {op.hw_ast}")
            print( "    Transformations:")
            for opd, tfs in op.transformations.items():
                print(f"      {opd}:{'->'.join(t.name for t in tfs)}")
            print( "    Name mapping:")
            for hw_name, req_name in op.name_mapping.items():
                print(f"      {hw_name}->{req_name}")
            print( "    Index mapping:")
            for hw_idx, req_idx in op.index_mapping.items():
                print(f"      {hw_idx}->{req_idx}")


class test_mm_matching(unittest.TestCase):
    """
    Test math matching, mostly revolving around matching matmul intent/requirement
    """

    def setUp(self):
        self.mm_req = expression_node(
            op=operation.MOVE,
            left=operand_ref(name="C", indices=('m', 'n')),
            right=expression_node(
                op=operation.ADD,
                left=operand_ref(name="C", indices=('m', 'n')),
                right=expression_node(
                    op=operation.REDUCE_SUM,
                    left=expression_node(
                        op=operation.MUL,
                        left=operand_ref(name="A", indices=('m', 'k')),
                        right=operand_ref(name="B", indices=('k', 'n'))),
                    reduce_dim='k')
            )
        )

    def extract_tfs(self, solutions: list[list[dict[str, Any]]]) -> set[tuple]:
        """
        Helper method to extract transformations from a list of solutions into a 
        comparable set of tuples. Order inside the tuple is (adreg, bdreg, cdreg).
        """
        res = set()
        for sol in solutions:
            sol_tfs = []
            for op in sol:
                tfs = op.transformations
                sol_tfs.append((
                    tfs.get('adreg', [tf.NONE])[0],
                    tfs.get('bdreg', [tf.NONE])[0],
                    tfs.get('cdreg', [tf.NONE])[0]
                ))
            res.add(tuple(sol_tfs))
        return res

    # --- MATCHING TESTS ---

    def test_match_fma(self):
        solutions = solve_requirement(self.mm_req, [HW_FMA_AST])
        print_solution(solutions)
        # Vectors are rank 1, so the orientation is the index binding (i=m with B
        # broadcast, i=n with A broadcast), not a transposition
        self.assertEqual(6, len(solutions))
        
        expected_tfs = {
            ((tf.NONE, tf.SCALAR_REDUCE, tf.NONE),),
            ((tf.SCALAR_REDUCE, tf.NONE, tf.NONE),),
            ((tf.SCALAR_REDUCE, tf.SCALAR_REDUCE, tf.SCALAR_REDUCE),),
        }
        self.assertEqual(expected_tfs, self.extract_tfs(solutions))


    def test_match_fdota(self):
        solutions = solve_requirement(self.mm_req, [HW_FDOTA_AST])
        print_solution(solutions)
        # The reduced index r is not the output index: A and B run along k, the
        # result is one element
        self.assertEqual(4, len(solutions))

        expected_tfs = {
            ((tf.NONE, tf.NONE, tf.SCALAR_REDUCE),),
            ((tf.SCALAR_REDUCE, tf.SCALAR_REDUCE, tf.SCALAR_REDUCE),),
        }
        self.assertEqual(expected_tfs, self.extract_tfs(solutions))


    def test_match_fopa(self):
        solutions = solve_requirement(self.mm_req, [HW_FOPA_AST])
        print_solution(solutions)
        # bdreg (j,) binds to B's n directly; transposing is only needed with the
        # operand slots swapped
        self.assertEqual(4, len(solutions))

        expected_tfs = {
            ((tf.NONE, tf.NONE, tf.NONE),),
            ((tf.NONE, tf.NONE, tf.TRANSPOSE),),
            ((tf.NONE, tf.SCALAR_REDUCE, tf.ROW_REDUCE),),
            ((tf.SCALAR_REDUCE, tf.NONE, tf.COL_REDUCE),),
        }
        self.assertEqual(expected_tfs, self.extract_tfs(solutions))

    def test_match_mma(self):
        solutions = solve_requirement(self.mm_req, [HW_MMA_AST])
        print_solution(solutions)
        self.assertEqual(5, len(solutions))

        expected_tfs = {
            ((tf.NONE, tf.NONE, tf.NONE),),             # normal
            ((tf.COL_REDUCE, tf.NONE, tf.COL_REDUCE),), # column times matrix
            ((tf.NONE, tf.ROW_REDUCE, tf.ROW_REDUCE),), # matrix times row
            ((tf.ROW_REDUCE, tf.COL_REDUCE, tf.NONE),), # outer product
            ((tf.TRANSPOSE, tf.TRANSPOSE, tf.TRANSPOSE),),             # normal
        }
        self.assertEqual(expected_tfs, self.extract_tfs(solutions))

    def test_match_fmulfadd(self):
        solutions = solve_requirement(self.mm_req, [HW_FMUL_AST, HW_FADD_AST])
        print_solution(solutions)

        # Many solutions, most degenerate or redundant
        # The temporary between fmul and fadd must be laid out the same way in
        # both: no chain vectorizes it along n in one and along m in the other
        self.assertEqual(12, len(solutions))

        # only 5 actual solutions (RVV examples in comments)
        expected_tfs = {
            ((tf.NONE, tf.SCALAR_REDUCE, tf.NONE), (tf.NONE, tf.NONE, tf.NONE)),
            ((tf.SCALAR_REDUCE, tf.NONE, tf.NONE), (tf.NONE, tf.NONE, tf.NONE)),
            ((tf.SCALAR_REDUCE, tf.SCALAR_REDUCE, tf.SCALAR_REDUCE), (tf.SCALAR_REDUCE, tf.SCALAR_REDUCE, tf.SCALAR_REDUCE)),
        }
        self.assertEqual(expected_tfs, self.extract_tfs(solutions))


    def test_match_fmulfadd_to_addtemp(self):
        req = expression_node(
            operation.MOVE,
            operand_ref(name="C", indices=('m', 'n')),
            expression_node(
                operation.ADD, 
                operand_ref(name="C", indices=('m', 'n')),
                operand_ref(name="T0", indices=('m', 'n'))))

        solutions = solve_requirement(req, [HW_FMUL_AST, HW_FADD_AST])
        # Both orientations bind without transposing
        self.assertEqual(6, len(solutions))
        
        expected_tfs = {
            ((tf.NONE, tf.NONE, tf.NONE),),
            ((tf.SCALAR_REDUCE, tf.SCALAR_REDUCE, tf.SCALAR_REDUCE),),
        }
        self.assertEqual(expected_tfs, self.extract_tfs(solutions))

    def test_match_fmulfadd_to_matmul(self):
        req = expression_node(
            operation.MOVE, 
            operand_ref(name="C", indices=('m', 'n')),
            expression_node(
                operation.REDUCE_SUM, 
                expression_node(
                    operation.MUL, 
                    operand_ref(name="A", indices=('m', 'k')),
                    operand_ref(name="B", indices=('k', 'n'))),
                reduce_dim='k'))

        solutions = solve_requirement(req, [HW_FMUL_AST, HW_FADD_AST])
        print_solution(solutions)
        # Both orientations bind without transposing
        self.assertEqual(6, len(solutions))

        expected_tfs = {
            ((tf.NONE, tf.SCALAR_REDUCE, tf.NONE),),
            ((tf.SCALAR_REDUCE, tf.NONE, tf.NONE),),
            ((tf.SCALAR_REDUCE, tf.SCALAR_REDUCE, tf.SCALAR_REDUCE),),
        }
        self.assertEqual(expected_tfs, self.extract_tfs(solutions))

    def test_direct_match_reduced_to_scalar(self):
        req = expression_node(
            operation.MOVE, 
            operand_ref(name="C", indices=('m', 'n')),
            expression_node(
                operation.REDUCE_SUM, 
                expression_node(
                    operation.MUL, 
                    operand_ref(name="A", indices=('m', 'k')),
                    operand_ref(name="B", indices=('k', 'n'))),
                reduce_dim='k'))

        fmul = transform_ast(HW_FMUL_AST, 
            {'adreg': [tf.NONE],
             'bdreg': [tf.SCALAR_REDUCE],
             'cdreg': [tf.NONE]})

        match_count = 0
        for v in generate_variants(req):
            name_mapping = {}
            index_mapping = {}
            if map_and_match(v, fmul, name_mapping, index_mapping):
                match_count += 1
                
        # one per orientation: A*B binding i=m with B broadcast, and the
        # commuted B*A binding i=n with A broadcast
        self.assertEqual(2, match_count, "Expected one match per orientation")

    def test_extract_deepest(self):
        split_ast, dependencies = extract_deepest_operation(
            self.mm_req,
            temp_counter=0)

        self.assertEqual("MOVE(C[m,n],ADD(C[m,n],REDUCE_SUM(T0[m,k,n],k)))", 
                         str(split_ast))
        self.assertEqual(1, len(dependencies))
        self.assertEqual("MOVE(T0[m,k,n],MUL(A[m,k],B[k,n]))", 
                         str(dependencies[0]))

        split_ast, dependencies = extract_deepest_operation(
            split_ast,
            temp_counter=0)

        self.assertEqual("MOVE(C[m,n],ADD(C[m,n],T0[m,n]))", 
                         str(split_ast))
        self.assertEqual(1, len(dependencies))
        self.assertEqual("MOVE(T0[m,n],REDUCE_SUM(T0[m,k,n],k))", 
                         str(dependencies[0]))

        # No more dependencies expected after this point
        split_ast, dependencies = extract_deepest_operation(
            split_ast,
            temp_counter=0)
        self.assertEqual("MOVE(C[m,n],ADD(C[m,n],T0[m,n]))", str(split_ast))
        self.assertEqual(0, len(dependencies))

        split_ast, dependencies = extract_deepest_operation(
            split_ast,
            temp_counter=0)
        self.assertEqual("MOVE(C[m,n],ADD(C[m,n],T0[m,n]))", str(split_ast))
        self.assertEqual(0, len(dependencies))

    # --- AST UTILITY TESTS (Coverage increase) ---

    def test_simplify_ast_removes_dead_reductions(self):
        req = expression_node(
            operation.REDUCE_SUM,
            operand_ref(name="A", indices=('m', 'n')),
            reduce_dim='k' # 'k' does not exist in children
        )
        simplified = simplify_ast(req)
        self.assertTrue(isinstance(simplified, operand_ref))
        self.assertEqual("A[m,n]", str(simplified))

    def test_transform_operand_variations(self):
        op = operand_ref(name="A", indices=('i', 'j'))

        # Transpose
        trans_op = transform_operand(op, tf.TRANSPOSE)
        self.assertEqual(('j', 'i'), trans_op.indices)

        # Col Reduce
        col_op = transform_operand(op, tf.COL_REDUCE)
        self.assertEqual((None, 'j'), col_op.indices)

        # Row Reduce
        row_op = transform_operand(op, tf.ROW_REDUCE)
        self.assertEqual(('i', None), row_op.indices)

        # Scalar Reduce from valid 2D
        scalar_op_1 = transform_operand(col_op, tf.SCALAR_REDUCE)
        self.assertEqual((None, None), scalar_op_1.indices)

        scalar_op_2 = transform_operand(row_op, tf.SCALAR_REDUCE)
        self.assertEqual((None, None), scalar_op_2.indices)

    def test_get_operands(self):
        operands = get_operands(self.mm_req)
        self.assertEqual({"A", "B", "C"}, operands)

    def test_decimate_index_middle(self):
        op = operand_ref(name="T", indices=('m', 'k', 'n'))
        decimated = decimate_index(op, 'k')
        
        # T[m, None, n] should be pruned to T[m, n]
        self.assertEqual(('m', 'n'), decimated.indices)

    def test_no_solution_for_incompatible_math(self):
        # A purely ADD based requirement should not match FMUL hardware
        add_req = expression_node(
            operation.MOVE,
            operand_ref(name="C", indices=('m', 'n')),
            expression_node(
                operation.ADD,
                operand_ref(name="A", indices=('m', 'n')),
                operand_ref(name="B", indices=('m', 'n'))
            )
        )
        solutions = solve_requirement(add_req, [HW_FMUL_AST])
        self.assertEqual(0, len(solutions))

    def test_operand_io(self):

        self.assertEqual((True,False), get_operand_io(self.mm_req, "A"))
        self.assertEqual((True,False), get_operand_io(self.mm_req, "B"))
        self.assertEqual((True,True), get_operand_io(self.mm_req, "C"))

    def test_operand_io_pure_output(self):
        """
        A MOVE destination that is never read is an output only - otherwise the
        data movement solver demands a load of a register that is about to be
        overwritten.
        """
        self.assertEqual((False,True), get_operand_io(HW_FMUL_AST, "cdreg"))
        self.assertEqual((True,False), get_operand_io(HW_FMUL_AST, "adreg"))
        # an accumulator is read by the ADD, so it stays both
        self.assertEqual((True,True), get_operand_io(HW_FMA_AST, "cdreg"))

        pack = expression_node(
            operation.MOVE, operand_ref(name="Y", indices=('m','n')),
            expression_node(operation.MUL,
                            operand_ref(name="X", indices=('m','n')),
                            operand_ref(name="kappa", indices=(None,None))))
        self.assertEqual((False,True), get_operand_io(pack, "Y"))
        self.assertEqual((True,False), get_operand_io(pack, "X"))

