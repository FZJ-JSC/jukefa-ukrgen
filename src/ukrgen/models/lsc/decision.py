"""
One decision: a branch of one question the allocator answers
(docs/REGISTER_ALLOCATION.md: decisions)

An operation carries the decision its presence depends on. The specializer
generates every branch and tags them; the allocation takes one branch of each
question; the pruning pass keeps the operations of the branches taken. A
question is its family and its subject - an offset's polynomial and component,
a tail's index, a loop's name, a file's tag - and it has exactly two answers.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class decision:
    """
    One branch of one question: kept or dropped whole, and hashable so that a
    set of them is an answer

    :param family: what kind of choice it is - "offset", "tail", "loop", "cap"
    :param subject: what it is about - an offset's (polynomial, component), a
        tail's index, a loop's name, a file's tag
    :param branch: this answer, "taken" by default; `alternative` the other
    """
    family : str
    subject : tuple
    branch : str = "taken"

    @property
    def alternative(self) -> "decision":
        """
        The same question's other answer
        :return: the branch not taken
        """
        return decision(self.family, self.subject,
                        "plain" if "plain" != self.branch else "taken")

    def question(self) -> tuple[str, tuple]:
        """
        What this is a branch of, without the branch: two decisions with one
        question are alternatives
        :return: the family and the subject
        """
        return (self.family, self.subject)

    def __str__(self) -> str:
        """Its name in a message: the family, what it is about, the answer"""
        return ":".join([self.family] + [str(part) for part in self.subject] + [self.branch])
