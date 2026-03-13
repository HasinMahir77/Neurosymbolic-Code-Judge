from __future__ import annotations

import ast
from collections import deque

from nsjudge.schemas import DependencyGraph, FunctionInfo


def parse_file(source_code: str) -> DependencyGraph:
    """Parse a Python source file and return its dependency graph.

    Extracts top-level functions, builds a call graph of internal dependencies,
    and returns a topologically sorted verification order (leaves first).
    """
    tree = ast.parse(source_code)
    functions = _extract_functions(tree, source_code)

    if "main" not in functions:
        raise ValueError("Source file must contain a top-level 'main' function.")

    call_graph = _build_call_graph(functions)
    verification_order = _topological_sort(call_graph, functions)

    global_code = _extract_global_code(tree, source_code, functions)

    return DependencyGraph(
        functions=functions,
        verification_order=verification_order,
        global_code=global_code,
    )


def _extract_functions(tree: ast.Module, source: str) -> dict[str, FunctionInfo]:
    """Extract all top-level function definitions from the AST."""
    functions: dict[str, FunctionInfo] = {}

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        func_source = ast.get_source_segment(source, node)
        if func_source is None:
            # Fallback: extract by line numbers
            lines = source.splitlines()
            func_source = "\n".join(lines[node.lineno - 1 : node.end_lineno])

        args = [arg.arg for arg in node.args.args]

        functions[node.name] = FunctionInfo(
            name=node.name,
            source=func_source,
            args=args,
            calls=[],  # Populated by _build_call_graph
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
        )

    return functions


def _build_call_graph(functions: dict[str, FunctionInfo]) -> dict[str, list[str]]:
    """For each function, find which other internal functions it calls."""
    func_names = set(functions.keys())
    graph: dict[str, list[str]] = {name: [] for name in func_names}

    for name, info in functions.items():
        func_tree = ast.parse(info.source)
        calls = set()
        for node in ast.walk(func_tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in func_names
                and node.func.id != name  # Exclude self-recursion from deps
            ):
                calls.add(node.func.id)
        deps = sorted(calls)
        graph[name] = deps
        info.calls = deps

    return graph


def _topological_sort(
    graph: dict[str, list[str]], functions: dict[str, FunctionInfo]
) -> list[str]:
    """Kahn's algorithm: returns functions in bottom-up order (leaves first).

    Raises ValueError if a cycle is detected.
    """
    # Build in-degree map (how many functions depend on each function)
    # Note: graph[A] = [B, C] means A calls B and C, so A depends on B and C.
    # For topo sort, we want to process B and C before A.
    # Reverse the edges: B is depended on by A.
    in_degree: dict[str, int] = {name: 0 for name in graph}
    reverse_graph: dict[str, list[str]] = {name: [] for name in graph}

    for caller, callees in graph.items():
        for callee in callees:
            if callee in in_degree:
                in_degree[caller] += 1
                reverse_graph[callee].append(caller)

    # Start with leaf functions (no internal dependencies)
    queue: deque[str] = deque()
    for name, degree in in_degree.items():
        if degree == 0:
            queue.append(name)

    order: list[str] = []
    while queue:
        # Sort the queue contents for deterministic ordering
        current = queue.popleft()
        order.append(current)

        for dependent in reverse_graph[current]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(graph):
        remaining = set(graph.keys()) - set(order)
        raise ValueError(
            f"Circular dependency detected among functions: {sorted(remaining)}"
        )

    return order


def _extract_global_code(
    tree: ast.Module, source: str, functions: dict[str, FunctionInfo]
) -> str:
    """Extract module-level code that isn't a function definition."""
    lines = source.splitlines()
    func_line_ranges: set[int] = set()

    for info in functions.values():
        for line_num in range(info.line_start, info.line_end + 1):
            func_line_ranges.add(line_num)

    global_lines = []
    for i, line in enumerate(lines, start=1):
        if i not in func_line_ranges:
            global_lines.append(line)

    return "\n".join(global_lines).strip()
