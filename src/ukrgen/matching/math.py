"""
Matching of mathematical operations
"""
from __future__ import annotations

import logging
import functools
import itertools
from copy import deepcopy,copy
from typing import Optional,Iterator
from dataclasses import dataclass
from enum import Enum,auto

class operation(Enum):
    """
    Mathematical operations
    """
    ADD = auto()
    MUL = auto()
    REDUCE_SUM = auto()
    MOVE = auto()


class transformation(Enum):
    """
    Tile transformations
    """
    NONE          = auto()
    TRANSPOSE     = auto() # (i,j)    -> (j,i)
    COL_REDUCE    = auto() # (i,j)    -> (None,j)
    ROW_REDUCE    = auto() # (i,j)    -> (i,None)
    SCALAR_REDUCE = auto() # (i,None)/(None,j) -> (None,None) [BCAST/VF/IDX/LANE]

debug = logging.getLogger("MATCHING").debug

@dataclass(frozen=True)
class operand_ref:
    """
    Reference to an operand
    """
    name: str
    indices: tuple[str,...]

    def get_shape(self) -> list[str]:
        """
        Return the set of active dimensions
        """
        # Indices are names, so a shape is which of them the operand varies
        # along - not which slot they sit in. A rank-1 vector (i,) and a matrix
        # column (i,None) have the same shape.
        return [idx for idx in self.indices if idx is not None]

    def is_dimensionally_valid(self) -> bool:
        """
        Operands are always valid
        """
        return True

    def __str__(self):
        idx_str = ','.join(i if i is not None else '1'
                           for i in self.indices )
        return f"{self.name}[{idx_str}]"

    def __repr__(self):
        return str(self)

@dataclass(frozen=True)
class expression_node:
    """
    Node representing an expression on mathematical operands
    """
    op: operation
    left: expression_node|operand_ref
    right: Optional[expression_node|operand_ref] = None
    reduce_dim: Optional[str] = None

    def get_shape(self) -> list[str]:
        """
        Return the output shape of the expression
        """

        # Potential OOP rework required if more ops are added in the future
        if self.op in (operation.ADD, operation.MUL):
            left_indices = self.left.get_shape()
            if self.right is None:
                return left_indices

            right_indices = self.right.get_shape()

            # the indices either side varies along: an outer product of a(i)
            # and b(j) varies along both
            return left_indices + [i for i in right_indices if i not in left_indices]

        elif self.op == operation.REDUCE_SUM:

            return [i for i in self.left.get_shape() if i != self.reduce_dim]
        elif self.op == operation.MOVE:
            return self.left.get_shape()
        return []

    def is_dimensionally_valid(self) -> bool:
        """
        Checks if all assignments inside the AST are valid
        """

        if not self.left.is_dimensionally_valid():
            return False

        if self.right is not None:
            if not self.right.is_dimensionally_valid():
                return False


        # Forbid vector->scalar: whatever the right side varies along, the
        # destination must vary along too. Allow scalar->vector.
        if self.op == operation.MOVE:
            left_shape = self.left.get_shape()
            # right is not None for a MOVE
            right_shape = self.right.get_shape()
            if any(i not in left_shape for i in right_shape):
                return False
                # index mismatch
                if i_out is not None and i_in is not None:
                    if i_out != i_in:
                        return False
        return True

    def __str__(self):
        maybe_right = ""
        if self.right is not None:
            maybe_right = f",{self.right}"

        if operation.REDUCE_SUM == self.op:
            maybe_right += f",{self.reduce_dim}"
        return f"{self.op.name}({self.left}{maybe_right})"

    def __repr__(self):
        return str(self)


type ast_node = expression_node | operand_ref

def recurse_indices(n : ast_node) -> list[str,...]:
    """
    Gathers all indices of an AST node and it's children, preserving order

    :param n: expression node or a leaf operand reference
    :return: set of all indices in the node and all it's children
    """
    if isinstance(n, operand_ref):
        return [idx for idx in n.indices if idx is not None]

    indices = recurse_indices(n.left)
    if n.right is not None:
        for idx in recurse_indices(n.right):
            if idx not in indices:
                indices.append(idx)

    # remove reduction index if this op is a reduction
    if operation.REDUCE_SUM == n.op:
        indices = [idx for idx in indices if idx != n.reduce_dim]

    return indices

def simplify_ast(n : ast_node) \
        -> ast_node:
    """
    Simplify AST

    :param n: starting node of the AST
    :return: simplified AST
    """

    if isinstance(n, operand_ref):
        return n

    new_left = simplify_ast(n.left)
    new_right = None
    if n.right is not None:
        new_right = simplify_ast(n.right)

    # For now only a reducing sum is relevant
    # FMA (VF transform) -> already scalar
    # FDOTA,FOPA,MMA -> k reduced
    if operation.REDUCE_SUM == n.op:
        child_indices = recurse_indices(new_left)
        if new_right is not None:
            child_indices |= recurse_indices(new_right)

        # If the index isn't present in the children, REDUCE_SUM
        # doesn't do anything
        if n.reduce_dim not in child_indices:
            return new_left

    return expression_node(
            op=n.op,
            left=new_left, right=new_right,
            reduce_dim=n.reduce_dim)

def bind_indices(req_indices : tuple[str|None, ...],
                 hw_indices : tuple[str|None, ...],
                 index_mapping : dict[str, str|None]) -> Iterator[dict[str, str|None]]:
    """
    Every way to bind the indices of a hardware operand to those of a
    requirement operand, consistent with the bindings so far.

    Operands of equal rank bind slot by slot - a tile's rows to the
    requirement's rows. A hardware operand of lower rank binds its indices to
    any of the requirement operand's: a vector (i,) against A[m,k] runs along
    m or along k, which is how both orientations of an FMA come out of one
    hardware AST without transposing it. Requirement indices left unbound are
    covered one element at a time.

    :param req_indices: indices of the requirement operand
    :param hw_indices: indices of the hardware operand
    :param index_mapping: hardware index -> requirement index, so far
    :return: each consistent extension of index_mapping
    """
    if len(req_indices) == len(hw_indices):
        mapping = dict(index_mapping)
        for r_idx, h_idx in zip(req_indices, hw_indices):
            if h_idx is None:
                continue
            if mapping.setdefault(h_idx, r_idx) != r_idx:
                return
        yield mapping
        return

    hw_live = [h for h in hw_indices if h is not None]
    req_live = [r for r in req_indices if r is not None]
    if len(hw_live) > len(req_live):
        return
    seen = set()
    for chosen in itertools.permutations(req_live, len(hw_live)):
        mapping = dict(index_mapping)
        if all(mapping.setdefault(h, r) == r for h, r in zip(hw_live, chosen)):
            key = tuple(sorted(mapping.items(), key=str))
            if key not in seen:
                seen.add(key)
                yield mapping


def iter_matches(requirement : ast_node,
                 hardware : ast_node,
                 name_mapping : dict[str,str],
                 index_mapping : dict[str,str|None]) \
        -> Iterator[tuple[dict[str,str], dict[str,str|None]]]:
    """
    Every way the hardware AST matches the requirement: consistent pairs of
    operand name and index bindings. Several exist when a lower-rank hardware
    operand can bind to more than one requirement index.

    :return: (hardware name -> requirement name, hardware index -> requirement
             index) per match
    """
    if type(requirement) != type(hardware):
        return
    if isinstance(requirement, operand_ref):
        names = dict(name_mapping)
        if names.setdefault(hardware.name, requirement.name) != requirement.name:
            return
        for indices in bind_indices(requirement.indices, hardware.indices, index_mapping):
            yield names, indices
        return

    if requirement.op != hardware.op:
        return
    indices = dict(index_mapping)
    if requirement.reduce_dim is not None and hardware.reduce_dim is not None:
        if indices.setdefault(hardware.reduce_dim, requirement.reduce_dim) \
                != requirement.reduce_dim:
            return
    elif requirement.reduce_dim is not None or hardware.reduce_dim is not None:
        return

    for names_l, indices_l in iter_matches(requirement.left, hardware.left, name_mapping, indices):
        if requirement.right is None and hardware.right is None:
            yield names_l, indices_l
        elif requirement.right is not None and hardware.right is not None:
            yield from iter_matches(requirement.right, hardware.right, names_l, indices_l)


def map_and_match(requirement : ast_node,
                  hardware : ast_node,
                  name_mapping : dict[str,str],
                  index_mapping : dict[str,str]) -> bool:
    """
    Whether the hardware AST matches the requirement; fills in the first match's
    name and index mappings. See iter_matches for all of them.
    """
    debug(f"Trying to match {requirement} and {hardware}")
    for names, indices in iter_matches(requirement, hardware, name_mapping, index_mapping):
        name_mapping.update(names)
        index_mapping.update(indices)
        return True
    return False


def extract_operand_pairs(req: ast_node, hw: ast_node) \
        -> list[tuple[operand_ref, operand_ref]]:
    """
    Helper to extract corresponding operand leaves from two structurally matched ASTs.
    """
    if isinstance(req, operand_ref) and isinstance(hw, operand_ref):
        return [(req, hw)]
    pairs = []
    if isinstance(req, expression_node) and isinstance(hw, expression_node):
        pairs.extend(extract_operand_pairs(req.left, hw.left))
        if req.right and hw.right:
            pairs.extend(extract_operand_pairs(req.right, hw.right))
    return pairs

def extract_deepest_operation(ast : ast_node,
                              temp_counter: int) -> \
                                      tuple[ast_node,list[ast_node]]:
    """
    Finds the deepest operation in the AST and replaces it with a MOVE AST on a temporary

    :param ast: AST to extract from
    :param temp_counter: Now many temporaries were already substituted
    :return: tuple consisting of a modified AST including the substitution and a list of new requirements
    """

    if isinstance(ast, operand_ref):
        return ast,[]

    if operation.MOVE == ast.op:

        right_node = ast.right

        # MOVE(C, T0)
        if isinstance(right_node, operand_ref):
            return ast, []

        left_is_leaf = isinstance(right_node.left, operand_ref)
        right_is_leaf = right_node.right is None or \
                isinstance(right_node.right, operand_ref)

        # MOVE(C, OP(A,B))
        if left_is_leaf and right_is_leaf:
            return ast, []

        new_right, deps = extract_deepest_operation(ast.right, temp_counter)


        return expression_node(
                  op=operation.MOVE,
                  left=ast.left,
                  right=new_right
               ), deps

    left_is_leaf = isinstance(ast.left, operand_ref)
    right_is_leaf = ast.right is None or isinstance(ast.right, operand_ref)

    if left_is_leaf and right_is_leaf:
        temp_indices = recurse_indices(ast)
        temp_ref = operand_ref(name=f"T{temp_counter}",
                               indices=tuple(temp_indices))


        new_req = expression_node(operation.MOVE, left=temp_ref, right=ast)
        
        debug(f"temporary {temp_ref} created as substitute for {ast} with {new_req} as dependency")

        return temp_ref, [new_req]

    if not right_is_leaf:
        new_right, deps = extract_deepest_operation(ast.right, temp_counter)
        return expression_node(
                op=ast.op,
                left=ast.left,
                right=new_right,
                reduce_dim=ast.reduce_dim
            ), deps

    if not left_is_leaf:
        new_left, deps = extract_deepest_operation(ast.left, temp_counter)
        return expression_node(
                op=ast.op,
                left=new_left,
                right=ast.right,
                reduce_dim=ast.reduce_dim
            ), deps

    raise RuntimeError("This shouldn't be reachable")


def transform_operand(operand : operand_ref, tf : transformation) -> operand_ref:
    """
    Returns a new operand resulting from transforming an input operand
    
    :param operand: Operand to transform
    :param tf: Transformaiton to apply
    :return: New transformed operand
    """
    new_operand = copy(operand)

    idx = list(operand.indices)

    if transformation.TRANSPOSE == tf and len(idx) == 2:
        idx = [idx[1],idx[0]]
    if transformation.SCALAR_REDUCE == tf:
        # a vector becomes one element, whatever its rank: (i,) -> (None,),
        # (i,None) -> (None,None). An operand varying along two indices is
        # reduced by COL_REDUCE or ROW_REDUCE instead.
        live = [n for n, i in enumerate(idx) if i is not None]
        if 1 == len(live):
            idx[live[0]] = None
    if transformation.COL_REDUCE == tf:
        if len(idx) == 2:
            if idx[0] is not None:
                idx[0] = None
            else:
                pass
    if transformation.ROW_REDUCE == tf:
        if len(idx) == 2:
            if idx[1] is not None:
                idx[1] = None
            else:
                pass

    return operand_ref(name=operand.name, indices=tuple(idx))

def transform_ast(ast : ast_node,
                  trans_dict : dict[str,list[transformation]]) -> ast_node:
    """
    Returns a new AST resulting from walking the input AST and transforming all
    its operands

    :param ast: Original AST
    :param trans_dict: Map of operands to a list of transformations to apply to them
    :return: New transformed AST
    """

    if isinstance(ast, operand_ref):
        new_op = ast
        for tf in trans_dict.get(ast.name, [transformation.NONE]):
            new_op = transform_operand(new_op, tf)
        return new_op

    new_left = transform_ast(ast.left, trans_dict)
    new_right = None
    if ast.right is not None:
        new_right = transform_ast(ast.right, trans_dict)

    return expression_node(
            op=ast.op,
            left=new_left, right=new_right,
            reduce_dim=ast.reduce_dim)


def get_operands(n: ast_node) -> set[str]:
    """
    Recursively collect all operands in an AST.
    :param n: root node of the AST
    :return: set of operand names
    """
    if isinstance(n,operand_ref):
        return {n.name}

    operands = get_operands(n.left)
    if n.right is not None:
        operands |= get_operands(n.right)
    return operands

def for_each_operand(n: ast_node, 
                     func : Callable[[ast_node],Any]) -> Iterator[Any]:
    """
    Recursively iterate through all operands and apply a function to all of them,
    yielding the return values.
    :param n: root node of the AST
    :param func: function to apply to operands
    :return: Iterator through return values of the supplied
             function applied to operands of the AST
    """
    if isinstance(n,operand_ref):
        yield func(n)

    # yield is NOT return, code picks up from after the yield so need to
    # check if node is an expression explicitly
    if isinstance(n,expression_node):
        yield from for_each_operand(n.left, func)
        if n.right is not None:
            yield from for_each_operand(n.right, func)

def for_each_expression(n: ast_node, func : Callable[[ast_node],Any]) -> Iterator[Any]:
    """
    Recursively iterate through all expressions and apply a function to all of them,
    yielding the return values.
    :param n: root node of the AST
    :param func: function to apply to expressions
    :return: Iterator through return values of the supplied
             function applied to expressions of the AST
    """
    if isinstance(n,expression_node):
        yield func(n)
        
        yield from for_each_expression(n.left, func)
        if n.right is not None:
            yield from for_each_expression(n.right, func)


def get_operand_io(n: ast_node, opd : str) -> tuple[bool,bool]:
    """
    Find out if the operator is used as input,output or both in the AST
    :param n: root node of the AST
    :param opd: name of the operand to search for
    :return: first value is True if the operand is used as input, 
             second value if it is used as output
    """

    io = [False,False]

    def mark_io(n: ast_node):
        if isinstance(n, expression_node):
            if isinstance(n.left, operand_ref) and n.left.name == opd:
                # The destination of a MOVE is written, not read. An operand that
                # is also read (an accumulator) shows up as an input elsewhere,
                # e.g. as the left side of the ADD below the MOVE.
                if operation.MOVE == n.op:
                    io[1] = True
                else:
                    io[0] = True
            if n.right is not None:
                if isinstance(n.right, operand_ref):
                    if n.right.name == opd:
                        io[0] = True

    for _ in for_each_expression(n, mark_io):
        pass

    return tuple(io)

TF_DEGENERACIES = {
    transformation.ROW_REDUCE : {transformation.SCALAR_REDUCE,
                                 transformation.NONE},
    transformation.COL_REDUCE : {transformation.SCALAR_REDUCE,
                                 transformation.NONE},
    transformation.SCALAR_REDUCE : {transformation.NONE},
    transformation.TRANSPOSE : {transformation.NONE},
}

@functools.lru_cache(maxsize=None)
def is_transformation_weak(opd : operand_ref,
                           tf : transformation) -> bool:
    """
    Check if a transformation is "weak" (either doesn't do anything or
    is equivalent to a "stronger" transformation)
    """
    
    if transformation.NONE == tf:
        return False
    # one that changes nothing - transposing a vector, reducing a scalar
    if transform_operand(opd, tf) == opd:
        return True

    if tf not in TF_DEGENERACIES:
        return False
    for stf in TF_DEGENERACIES[tf]:
        if transform_operand(opd,tf) == transform_operand(opd,stf):
            return True

    return False


def has_weak_transformations(ast : ast_node, 
                             trans_dict : dict[str,list[transformation]]) -> bool:
    """
    Checks if any of the transformations in trans_dict is "weak"/redundant

    :param ast: AST to check
    :param trans_dict: Operand transformations to check
    :return: True if any weak transformations are present, False otherwise
    """

    return any(for_each_operand(
                ast,
                lambda opd : any(
                    is_transformation_weak(
                        opd, tf)
                    for tf in trans_dict[opd.name])))


def decimate_index(node : ast_node, idx : str) -> ast_node:
    
    if isinstance(node, operand_ref):

        new_indices = [i if i != idx else None for i in node.indices]
        if len(new_indices) > 2:
            pruned_indices = [new_indices[0]]
            for i in new_indices[1:-1]:
                if i is not None:
                    pruned_indices.append(i)
            pruned_indices.append(new_indices[-1])

            new_indices = pruned_indices

        return operand_ref(
                name=node.name,
                indices=tuple(new_indices)
                )
    
    l = decimate_index(node.left, idx)
    r = None
    if node.right is not None:
        r = decimate_index(node.right, idx)

    return expression_node(
            op = node.op, 
            left = l,
            right = r,
            reduce_dim= node.reduce_dim)

def generate_variants(node: ast_node) -> list[ast_node]:
    """
    Generates the original AST, ASTs where reductions are applied and
    Commutative variants with swapped operands for MUL/ADD

    :param node: original AST
    :return: list of original AST and generated variants
    """

    debug(f"Making variants of {node}")

    if isinstance(node, operand_ref):
        return [node]
        
    left_vars = generate_variants(node.left)
    right_vars = generate_variants(node.right) if node.right else [None]
    
    variants = []
    for l in left_vars:
        for r in right_vars:
            # 1. Standard structural variant
            variants.append(expression_node(node.op, l, r, node.reduce_dim))

            # 2. Commutative variants
            if r is not None and node.op in (operation.ADD, operation.MUL):
                variants.append(expression_node(node.op,
                                                left=r, right=l,
                                                reduce_dim=node.reduce_dim))

            
            # 3. If this is a reduction, ALSO append the operand of the reduction
            #    with decimated reduction dimension
            if node.op == operation.REDUCE_SUM:
                variants.append(decimate_index(l, node.reduce_dim))

    debug(f"Generated variants: {variants}")
    return variants

def validate_variance(req: ast_node, hw: ast_node,
                      index_mapping: dict[str, str]) -> bool:
    """
    Check the following condition: 
    If the math requires an operand to vary along dimension R, and the hardware 
    vectorizes along dimension H (where H maps to R),
    the hardware operand MUST contain H.
    """
    pairs = extract_operand_pairs(req, hw)
    for req_op, hw_op in pairs:
        req_shape = req_op.get_shape()
        hw_shape = hw_op.get_shape()
        
        for h_idx, r_idx in index_mapping.items():
            if r_idx in req_shape and h_idx not in hw_shape:
                debug(f"hw shape of {hw_op}: {hw_shape}")
                debug(f"Variance failure: {r_idx} in req, but {h_idx} not in hw")
                return False
    return True

@dataclass
class req_solution_step:
    """
    One step of a solution to an AST requirement

    :param hw_ast: untransformed hardware AST. Contains information about the
                   physical operands
    :param logical_ast: hardware AST after transformation and simplification.
    :param transformations: transformations applied to each operand
    :param name_mapping: map of hardware opd names to requirement opd names
    :param index_mapping: map of hardware indices to requirement index.
                          unmapped requirement indices have extent 1
    """
    hw_ast : ast_node
    logical_ast : ast_node
    transformations : dict[str, list[transformation]]
    name_mapping : dict[str,str]
    index_mapping : dict[str,str]

@functools.lru_cache(maxsize=None)
def _hw_transforms(hw_ast: ast_node) -> tuple:
    """
    The transformations of an HW AST worth matching - none weak, the result
    dimensionally valid - in the order transform_and_match tries them, each
    with its simplified logical AST. A property of the HW operation alone:
    computed once however many requirements it's matched against (it was
    each time - 1.2M weak checks a family's build)

    :return: ((operand name, transformation) pairs, simplified AST) per
             transformation worth matching
    """
    tf_options = list(transformation)
    all_operands = get_operands(hw_ast)
    out = []
    for perm in itertools.product(tf_options, repeat=len(all_operands)):
        trans_dict = {op_name: [tf] for op_name, tf in zip(all_operands, perm)}

        if has_weak_transformations(hw_ast, trans_dict):
            continue

        logical_hw = transform_ast(hw_ast, trans_dict)
        simplified_hw = simplify_ast(logical_hw)

        # 2. SHAPE VALIDATION: Reject impossible HW physics (Fake DOTA)
        if not simplified_hw.is_dimensionally_valid():
            continue
        out.append((tuple(zip(all_operands, perm)), simplified_hw))
    return tuple(out)


def transform_and_match(req: ast_node, hw_ast: ast_node) -> Iterator[req_solution_step]:
    """
    Generator that transforms an HW AST and yields the transformed ast if
    it matches the requirement

    :param req: Mathematical requirement
    :param hw_ast: Single AST representing HW operation
    :return: solution steps containing matching transformed HW ASTs
    """
    if hw_ast.op != operation.MOVE:
        raise ValueError(
                f"HW AST root op must be MOVE, instead it's {hw_ast.op.name}")

    for items, simplified_hw in _hw_transforms(hw_ast):
        # each step its own dict: the cached transformations are shared
        trans_dict = {op_name: [tf] for op_name, tf in items}

        seen = set()
        for name_mapping, index_mapping in iter_matches(req, simplified_hw, {}, {}):
            key = (tuple(sorted(name_mapping.items())),
                   tuple(sorted(index_mapping.items(), key=str)))
            if key in seen:
                continue
            seen.add(key)
            debug(f"success: {req} and {simplified_hw} match, validating variance")
            # reject fake scalars: an index the requirement varies along must
            # be one the hardware operand varies along
            if validate_variance(req, simplified_hw, index_mapping):
                yield req_solution_step(
                    hw_ast=hw_ast,
                    logical_ast=simplified_hw,
                    transformations=trans_dict,
                    name_mapping=name_mapping,
                    index_mapping=index_mapping
                )
            else:
                debug(f"variance validation failed")


def reduction_dims(ast: ast_node) -> set[str]:
    """
    Returns all dimension names that were reduced over in the AST

    :param ast: AST to query for reductions
    :return: set of dimension names that were reduced
    """
    def get_rdim(expr) -> str:
        return expr.reduce_dim if expr.op == operation.REDUCE_SUM else None

    return { 
        dim for dim in for_each_expression(ast, get_rdim)
        if dim is not None
    }

def index_axes(step: req_solution_step) -> dict[str, list[tuple[str,int]]]:
    """
    For each requirement index, list of operand names and dimension this index
    occupies, 
    
    example: A[m,k] * B[k,n] -> C[m,n]:
      m: [(A,0),(C,0)]
      k: [(A,1),(B,0)]
      n: [(B,1),(C,1)]

    :param step: solution step to inspect
    :return: list of (hw opd name, occupied dimension) mapped onto 
             dimension names as used in the requirement
    """

    axes : dict[str, list[tuple[str,int]]] = {}

    ast = step.logical_ast if step.logical_ast is not None else step.hw_ast

    for opd in for_each_operand(ast,lambda x:x):
        for axis,hw_idx in enumerate(opd.indices):
            if hw_idx is None:
                continue
            req_idx = step.index_mapping.get(hw_idx)
            if req_idx is None:
                continue

            axes.setdefault(req_idx, []).append((opd.name, axis))


    return axes


def solution_step_key(step: req_solution_step) -> tuple:
    """
    Structural key identifying one solution step.

    :param step: solution step
    :return: hashable key, equal for steps describing the same implementation
    """

    return (
        str(step.hw_ast),
        tuple(sorted((opd, tuple(t.name for t in tfs))
                     for opd, tfs in step.transformations.items())),
        tuple(sorted(step.name_mapping.items())),
        tuple(sorted(step.index_mapping.items()))
    )


def chain_key(chain : list[req_solution_step]) -> tuple:
    """
    Structural key identifying a whole solution chain

    :param chain: list of solution steps
    :return: hashable key, equal for chaoins describing the same implementation
    """

    return tuple(solution_step_key(step) for step in chain)


def dedup_chains(
        chains: list[list[req_solution_step]]
        ) -> list[list[req_solution_step]]:
    """
    Remove identical solutions

    :param chains: unfiltered chains
    :return: deduplicated chains
    """

    seen = set()
    out = []
    for chain in chains:
        key = chain_key(chain)
        if key in seen:
            continue
        seen.add(key)
        out.append(chain)
    
    return out


def dedup_variants(variants : list[ast_node]) -> list[ast_node]:
    """
    Remove duplicate variants

    :param variants: unfiltered variants
    :return: deduplicated variants
    """

    seen_variants = set()
    unique_variants = []

    for variant in variants:
        vkey = str(variant)
        if vkey in seen_variants:
            continue
        seen_variants.add(vkey)
        unique_variants.append(variant)

    return unique_variants

def operand_coverage(step: req_solution_step, math_name: str) -> frozenset[str]:
    """
    Requirement indices a step's hardware operand for math_name runs along -
    after its transformations, so a scalar-reduced operand covers none

    :param step: a solution step
    :param math_name: requirement operand, e.g. a temporary of a chain
    :return: the requirement indices bound to the operand's hardware indices
    """
    covered = set()
    for ref in for_each_operand(step.logical_ast, lambda x: x):
        if step.name_mapping.get(ref.name) != math_name:
            continue
        for idx in ref.indices:
            if idx is not None and step.index_mapping.get(idx) is not None:
                covered.add(step.index_mapping[idx])
    return frozenset(covered)


def solve_requirement(req: ast_node, hw_asts: list[ast_node],
                      temp_counter=0) \
        -> list[list[req_solution_step]]:
    """
    Generates a list of hw ASTs that solve the mathematical requirement

    :param req: Mathematical requirement to solve for
    :param hw_asts: List of hardware ASTs available for the solution
    :param temp_counter: Starting index for temporary name generation 
                         (used for recursion)
    :return: list of valid instruction chains, like [[FMA],[FMUL,FADD],[FDOTA]]
    """

    all_valid_chains = []

    req_variants = dedup_variants(generate_variants(req))

    for variant in req_variants:

        direct_matches = [
            [match]
            for hw_ast in hw_asts
            for match in transform_and_match(variant, hw_ast)
        ]
        all_valid_chains.extend(direct_matches)

        if isinstance(variant, operand_ref):
            continue

        split_ast, dependencies = extract_deepest_operation(
                variant,
                temp_counter=temp_counter)

        if not dependencies:
            continue

        # a plain move (an operand on its right) solves a requirement that
        # is one; inside a chain it would only copy a temporary
        chain_asts = [hw_ast for hw_ast in hw_asts
                      if not isinstance(hw_ast.right, operand_ref)]
        dep_solutions = solve_requirement(dependencies[0], chain_asts,
                                          temp_counter=temp_counter+1)
        remainder_solutions = solve_requirement(split_ast, chain_asts,
                                                temp_counter=temp_counter+1)


        for dep_chain in dep_solutions:
            for rem_chain in remainder_solutions:

                # This must be a temporary
                output_opd = dep_chain[-1].hw_ast.left 
                dep_tfs = dep_chain[-1].transformations[output_opd.name]

                invalid_change = False
                for opd in for_each_operand(rem_chain[0].hw_ast, lambda x : x):
                    if opd.name == output_opd.name:
                        rem_tfs = rem_chain[0].transformations[opd.name]
                        if transform_ast(output_opd, {opd.name:rem_tfs}) != \
                                transform_ast(opd, {opd.name:dep_tfs}):
                            invalid_change = True
                            break


                # The temporary between the two must be laid out the same way on
                # both sides: an fmul leaving it vectorized along n cannot feed
                # an fadd reading it as a vector along m. Each step binds its
                # indices independently, so nothing else guarantees this.
                producer = dep_chain[-1]
                temp = producer.name_mapping.get(producer.hw_ast.left.name)
                consumer = next((st for st in rem_chain
                                 if temp in st.name_mapping.values()), None)
                if consumer is not None and \
                        operand_coverage(consumer, temp) != operand_coverage(producer, temp):
                    invalid_change = True
                if not invalid_change:
                    all_valid_chains.append(dep_chain+rem_chain)

    return dedup_chains(all_valid_chains)

# A plain move: asmgen's move names its source adreg and its destination
# bdreg
HW_MOVE_AST = expression_node(
        op=operation.MOVE,
        left=operand_ref(name="bdreg", indices=('i',)),
        right=operand_ref(name="adreg", indices=('i',))
        )

# A tile's plain move: no instruction does it (SME has none from a tile to
# another), so the copy is never emitted - its tile is renamed to its source's
HW_MOVE_TILE_AST = expression_node(
        op=operation.MOVE,
        left=operand_ref(name="bdreg", indices=('i', 'j')),
        right=operand_ref(name="adreg", indices=('i', 'j'))
        )

HW_FADD_AST = expression_node(
        op=operation.MOVE,
        left=operand_ref(name="cdreg", indices=('i',)),
        right=expression_node(
            op=operation.ADD,
            left=operand_ref(name="adreg", indices=('i',)),
            right=operand_ref(name="bdreg", indices=('i',)))
        )

HW_FMUL_AST = expression_node(
        op=operation.MOVE,
        left=operand_ref(name="cdreg", indices=('i',)),
        right=expression_node(
            op=operation.MUL,
            left=operand_ref(name="adreg", indices=('i',)),
            right=operand_ref(name="bdreg", indices=('i',)))
        )

HW_FMA_AST = expression_node(
        op=operation.MOVE,
        left=operand_ref(name="cdreg", indices=('i',)),
        right=expression_node(
            op=operation.ADD,
            left=operand_ref(name="cdreg", indices=('i',)),
            right=expression_node(
                op=operation.MUL,
                left=operand_ref(name="adreg", indices=('i',)),
                right=operand_ref(name="bdreg", indices=('i',))
                )
            )
        )

# Dot product into each lane: the reduced index is not the output's
HW_FDOTA_AST = expression_node(
        op=operation.MOVE,
        left=operand_ref(name="cdreg", indices=('i',)),
        right=expression_node(
            op=operation.ADD,
            left=operand_ref(name="cdreg", indices=('i',)),
            right=expression_node(
                op=operation.REDUCE_SUM,
                left=expression_node(
                    op=operation.MUL,
                    left=operand_ref(name="adreg", indices=('r',)),
                    right=operand_ref(name="bdreg", indices=('r',))),
                reduce_dim='r')
            )
        )

HW_FOPA_AST = expression_node(
        op=operation.MOVE,
        left=operand_ref(name="cdreg", indices=('i','j')),
        right=expression_node(
            op=operation.ADD,
            left=operand_ref(name="cdreg", indices=('i','j')),
            right=expression_node(
                op=operation.MUL,
                left=operand_ref(name="adreg", indices=('i',)),
                right=operand_ref(name="bdreg", indices=('j',)))
            )
        )

HW_MMA_AST = expression_node(
        op=operation.MOVE,
        left=operand_ref(name="cdreg", indices=('i', 'j')),
        right=expression_node(
            op=operation.ADD,
            left=operand_ref(name="cdreg", indices=('i','j')),
            right=expression_node(
                op=operation.REDUCE_SUM,
                left=expression_node(
                    op=operation.MUL,
                    left=operand_ref(name="adreg", indices=('i','k')),
                    right=operand_ref(name="bdreg", indices=('k','j'))),
                reduce_dim='k')
            )
        )
