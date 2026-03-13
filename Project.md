**Project:** A Neuro-Symbolic Framework for Automated Code Verification: Bridging Large
Language Models and SMT Solvers

#### 1. Introduction

The rapid adoption of Large Language Models (LLMs) for automated code generation and
review has introduced significant risks regarding subtle logical flaws and hallucinated
correctness. Standard neural models lack the deterministic reasoning required to
mathematically guarantee code safety. This project proposes a Neuro-Symbolic Judge that
combines the semantic understanding of LLMs with the rigorous formal verification of the Z
SMT (Satisfiability Modulo Theories) solver. By utilizing Compositional Verification, the
system extracts programmatic intents via an LLM and mathematically proves them using Z3,
effectively identifying edge-case vulnerabilities that evade both human experts and standard
neural models.

#### 2. Problem Statement and Objectives

While LLMs excel at syntactic analysis and pattern recognition, they struggle with deep
symbolic execution and boundary condition validation. A neural model may approve code
that appears structurally sound but contains hidden state-space pollution or integer
overflows.
**Primary Objectives:**
● Design a hybrid pipeline that limits state-space explosion when verifying single-file
codebases.
● Automate the translation of Python source code and natural language intent into
formal mathematical constraints.
● Establish a deterministic benchmark (a Turing Test for code review) to compare the
Neuro-Symbolic Judge against human developers and standalone LLMs.

#### 3. Mathematical Foundation

The core mechanism relies on finding counter-examples to intended behavior. We consider
the defined preconditions of a function, and the postconditions. For a given program
operation, we must prove that valid inputs always lead to valid outputs.
Instead of proving this directly, the system uses Z3 to test the negation. We instruct the
solver to evaluate the constraint space.
If the Z3 solver returns unsat (unsatisfiable), it is mathematically proven that no inputs can
violate the expected behavior, guaranteeing the code's structural correctness. If it returns sat
(satisfiable), the solver generates a concrete model (counter-example) that demonstrates the
bug.


#### 4. System Architecture

The framework employs a Divide and Conquer architectural pattern to ensure scalability and
prevent solver timeouts.
● **Abstract Syntax Tree (AST) Ingestion Module:** Parses the raw source code into a
hierarchical dependency graph, isolating leaf nodes (helper functions) from parent
functions to enable bottom-up analysis.
● **Semantic Translation Engine (LLM):** Acts as the bridge. It receives isolated code
chunks and generates a structured JSON contract containing preconditions,
postconditions, and the corresponding Z3 logic.
● **Constraint Execution Sandbox:** A secure Python subprocess that executes the
LLM-generated Z3 scripts.
● **Compositional Roll-up Layer:** Replaces mathematically verified child functions with
their logical contracts. When evaluating a parent function, the solver evaluates the
contract rather than the underlying execution path, preventing state-space explosion.
#### 5. Technology Stack

```
Component Technology Purpose
Core Orchestration Python 3.12, ast
module
Code parsing, dependency mapping,
and overall control flow.
Neural Engine Gemini 3 Semantic intent extraction and
constraint generation.
Symbolic Engine z3-solver
(Microsoft)
SMT constraint solving and
counter-example generation.
Data Structuring Pydantic Enforcing strict JSON schemas for
LLM outputs.
```

#### 6. Implementation Plan

The development lifecycle is divided into four iterative phases:

###### Phase 1: Ingestion and Parsing

```
● Develop the AST parsing script to read standard Python files.
● Map function dependencies to establish the bottom-up verification order.
```
###### Phase 2: The Translation Bridge

```
● Engineer the prompt structure utilizing the Negation Strategy to force the LLM to
write constraints looking for failure states.
● Implement Pydantic schemas to ensure the LLM outputs exact Z3 Python syntax
rather than conversational text.
● Build a self-refinement loop: if the generated Z3 script throws a Python SyntaxError,
the traceback is fed back to the LLM for autonomous correction.
```
###### Phase 3: Execution and Composition

```
● Construct the isolated execution sandbox to safely run z3.prove() or
z3.Solver().check().
● Implement the logic to abstract proven functions into constraints for higher-level
parent functions.
```
###### Phase 4: Benchmarking (The Turing Test)

```
● Create a dataset of 15-20 Python files containing deliberate, subtle logical errors
(e.g., off-by-one errors, negative integer unhandled exceptions, hidden resource
leaks).
● Record the defect-detection rates of a control group (human reviewers) and a
baseline LLM.
● Evaluate the Neuro-Symbolic framework against the dataset, measuring exact
counter-example generation and false-positive reduction.
```

