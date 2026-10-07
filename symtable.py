from typing import Optional

from parser import Assignment, BinOp, Declaration, Number, Program, Variable


class SemanticError(Exception):
    pass


class Environment:
    def __init__(self, parent: Optional["Environment"] = None) -> None:
        self.parent = parent
        self._names: dict = {}  # name -> declaration line, THIS scope only

    def define(self, name: str, line: int) -> None:
        if name in self._names:
            original_line = self._names[name]
            raise SemanticError(
                f"Duplicate declaration of '{name}' (line {line}; originally declared line {original_line})."
            )
        self._names[name] = line

    def resolve(self, name: str) -> int:
        if name in self._names:
            return self._names[name]

        if self.parent is not None:
            return self.parent.resolve(name)

        raise SemanticError(f"Undeclared variable '{name}'.")

def check_expr(expr, env):
    if isinstance(expr, Number):
        return

    if isinstance(expr, Variable):
        try:    
            env.resolve(expr.name)
        except SemanticError:
            raise SemanticError(f"Undeclared variable '{expr.name}' on line {expr.line}.")
        return

    if isinstance(expr, BinOp):
        check_expr(expr.left, env)
        check_expr(expr.right, env)
        return

def check_program(ast: Program) -> Environment:
    env = Environment()

    for statement in ast.statements:
        if isinstance(statement, Declaration):
            check_expr(statement.expr, env)
            env.define(statement.name, statement.line)

        elif isinstance(statement, Assignment):
            try:    
                env.resolve(statement.name)
            except SemanticError:
                raise SemanticError(f"Undeclared variable '{statement.name}' on line {statement.line}.")
            check_expr(statement.expr, env)

    return env