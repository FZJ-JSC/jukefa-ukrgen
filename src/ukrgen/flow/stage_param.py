from dataclasses import dataclass

@dataclass
class stage_param:
    """
    A parameter a stage asks for.

    :param flag: a boolean switch taking no value, e.g. --list-to-candidates. Its
                 value is True when given and False otherwise.
    """
    value       : str|list[str]|bool
    description : str
    default     : str|list[str]|bool|None = None
    choices     : list[str]|None = None
    required    : bool = True
    multi       : bool = False
    flag        : bool = False
