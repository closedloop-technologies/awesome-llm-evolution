# Awesome LLM Evolution [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

A curated list of frameworks that combine **Large Language Models (LLMs)** with **evolutionary algorithms** or **search-based optimization techniques** (e.g. genetic algorithms, reinforcement learning, MCTS). Categorized by application domain.

---

## Contents

- [🧠 Code & Algorithm Discovery](#-code--algorithm-discovery)
- [🎮 Game Strategy & Planning](#-game-strategy--planning)
- [🧠 Neural Architecture Search & AI Design](#-neural-architecture-search--ai-design)
- [🧪 Molecule & Material Discovery](#-molecule--material-discovery)
- [🧩 Prompt & Policy Optimization](#-prompt--policy-optimization)

---

## 🧠 Code & Algorithm Discovery

- [FunSearch (DeepMind, 2024)](https://deepmind.google/discover/blog/funsearch-making-new-discoveries-in-mathematical-sciences-using-large-language-models/) - Pairs an LLM with an evaluator to evolve code for open math and algorithm problems. Achieved new records in combinatorics and discovered high-performance heuristics.

- [AlphaEvolve (DeepMind, 2025)](https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) - Gemini-based LLM agent that evolves entire programs, outperforming previous algorithm benchmarks, including a breakthrough in matrix multiplication.

- [OpenEvolve](https://github.com/codelion/openevolve) - Open-source version of AlphaEvolve. Modular LLM+EA framework with support for multi-language generation, ensemble agents, and custom evaluation loops.

- [Evolution of Heuristics (EoH)](https://github.com/FeiLiu36/EoH) - Evolves natural-language 'thoughts' and corresponding heuristics with an LLM loop. Beats previous methods on combinatorial optimization problems.

- [ReEvo](https://arxiv.org/abs/2402.01145v3) - Reflective evolution loop where the LLM both mutates and critiques heuristic strategies, leading to general-purpose solvers.

- [LLaMEA](https://github.com/XAI-liacs/LLaMEA) - Uses GPT-4 to iteratively evolve optimization algorithm code; beats classic optimizers on benchmark suites.

- [MPaGE](https://arxiv.org/abs/2507.20923v1) - Evolves diverse multi-objective heuristics guided by a Pareto grid. Achieves strong performance across several domains.

- [SOAR](https://github.com/flowersteam/SOAR) - Self-improving LLM that fine-tunes itself from successful generations. Dominates ARC symbolic reasoning benchmark.

- [LAEA](https://github.com/hhyqhh/LAEA) - Zero-shot LLMs act as surrogate models to rank solutions, replacing learned predictors in classic EA.

### A roundup of lots of other papers

- [LLM4EC](https://github.com/wuxingyu-ai/LLM4EC) - Community-sourced list of all papers at the intersection of LLMs and Evolutionary Computation.

---

## 🎮 Game Strategy & Planning

- [LLM-MCTS](https://github.com/1989Ryan/llm-mcts) - GPT-4 guides Monte Carlo Tree Search for high-level planning in robotics and games.

- [MC-DML](https://textgamer.github.io/mc-dml/) - Dynamic memory + GPT integrated into MCTS for interactive fiction. Significantly boosts single-shot win rates.

- [LERO](https://arxiv.org/abs/2503.21807v1) - Evolves reward shaping functions and partial observation strategies in multi-agent RL with GPT assistance.

- [Voyager](https://github.com/MineDojo/Voyager) - GPT-4 powered autonomous Minecraft agent that iteratively improves its own skills and codebase.

- [Tree-of-Thoughts](https://arxiv.org/abs/2305.10601) - Search-based reasoning framework that treats LLM generations as a search tree of "thoughts".

---

## 🧠 Neural Architecture Search & AI Design

- [ASI-Arch](https://arxiv.org/abs/2506.13131) - Gemini-based autonomous AI researcher that discovered 100+ transformer architectures outperforming human designs.

- [LLMatic](https://github.com/umair-nasir14/LLMatic) - GPT-4 powered neural architecture mutation guided by quality-diversity search. Efficient CIFAR and NAS-Bench exploration.

- [DesignGPT](https://arxiv.org/abs/2404.09777) - Framework where GPT-4 recommends network architecture improvements iteratively. Early-stage AutoML system.

---

## 🧪 Molecule & Material Discovery

- [MOLLEO](https://github.com/zoom-wang112358/MOLLEO) - GPT-4 proposes chemical modifications as evolutionary mutations. Strong results on drug design and property optimization.

- [MOLLM](https://arxiv.org/abs/2502.12845v2) - LLM framework for multi-objective molecule generation using in-context experience replay.

- [MultiMol](https://github.com/jiajunyu1999/LLM4Drug) - Two-agent LLM architecture: one learns from data, one reads literature to guide mutation of drug candidates.

- [LLM-Evolver for Polymers](https://www.youtube.com/watch?v=_owRHzenX-8) - Claude-3.5 driven optimizer outperforms traditional Bayesian methods for designing polymer sequences.

- [ChemLatica](https://openreview.net/forum?id=jC9D4cKhfu) - Family of small chemistry LLMs trained on 100M property-labeled molecules. Combines with evolutionary prompts.

- [VALID-Mol](https://arxiv.org/abs/2507.18074) - Incorporates chemical validation filtering into LLM-driven evolutionary molecular design.

---

## 🧩 Prompt & Policy Optimization

- [EvoPrompt](https://openreview.net/forum?id=ZG3RaNIsO8) - Uses evolutionary search with LLM-informed mutation to discover superior prompts for >30 NLP tasks.

- [Promptbreeder](https://arxiv.org/abs/2309.11319) - Self-mutating prompt generation. LLM breeds new prompts using self-descriptive meta prompts.

- [Vision-Language EvoPrompt](https://arxiv.org/abs/2503.23503) - GA optimized prompts induced emergent tool-use behavior in multimodal LLMs.

- [Bayesian Prompt Optimization](https://arxiv.org/abs/2401.10778) - BO in prompt space, using embeddings + surrogate models for search.
