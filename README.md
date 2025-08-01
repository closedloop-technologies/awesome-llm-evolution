# Awesome-LLM-Evolution

A curated list of frameworks that combine Large Language Models (LLMs) with evolutionary algorithms or search-based optimization techniques (e.g. genetic algorithms, reinforcement learning, MCTS). Categorized by application domain.


---

🧠 Code & Algorithm Discovery

FunSearch (DeepMind, 2024) – Pairs an LLM with an evaluator to evolve code for open math and algorithm problems. Achieved new records in combinatorics and discovered high-performance heuristics.

AlphaEvolve (DeepMind, 2025) – Gemini-based LLM agent that evolves entire programs, outperforming previous algorithm benchmarks, including a breakthrough in matrix multiplication.

OpenEvolve – Open-source version of AlphaEvolve. Modular LLM+EA framework with support for multi-language generation, ensemble agents, and custom evaluation loops.

Evolution of Heuristics (EoH) – Evolves natural-language 'thoughts' and corresponding heuristics with an LLM loop. Beats previous methods on combinatorial optimization problems.

ReEvo – Reflective evolution loop where the LLM both mutates and critiques heuristic strategies, leading to general-purpose solvers.

LLaMEA – Uses GPT-4 to iteratively evolve optimization algorithm code; beats classic optimizers on benchmark suites.

MPaGE – Evolves diverse multi-objective heuristics guided by a Pareto grid. Achieves strong performance across several domains.

SOAR – Self-improving LLM that fine-tunes itself from successful generations. Dominates ARC symbolic reasoning benchmark.

LLM4EC – Community-sourced list of all papers at the intersection of LLMs and Evolutionary Computation.

LAEA – Zero-shot LLMs act as surrogate models to rank solutions, replacing learned predictors in classic EA.



---

🎮 Game Strategy & Planning

LLM-MCTS – GPT-4 guides Monte Carlo Tree Search for high-level planning in robotics and games.

MC-DML – Dynamic memory + GPT integrated into MCTS for interactive fiction. Significantly boosts single-shot win rates.

LERO – Evolves reward shaping functions and partial observation strategies in multi-agent RL with GPT assistance.

Voyager – GPT-4 powered autonomous Minecraft agent that iteratively improves its own skills and codebase.

Tree-of-Thoughts – Search-based reasoning framework that treats LLM generations as a search tree of "thoughts".



---

🧠 Neural Architecture Search & AI Design

ASI-Arch – Gemini-based autonomous AI researcher that discovered 100+ transformer architectures outperforming human designs.

LLMatic – GPT-4 powered neural architecture mutation guided by quality-diversity search. Efficient CIFAR and NAS-Bench exploration.

DesignGPT – Framework where GPT-4 recommends network architecture improvements iteratively. Early-stage AutoML system.



---

🧪 Molecule & Material Discovery

MOLLEO – GPT-4 proposes chemical modifications as evolutionary mutations. Strong results on drug design and property optimization.

MOLLM – LLM framework for multi-objective molecule generation using in-context experience replay.

MultiMol – Two-agent LLM architecture: one learns from data, one reads literature to guide mutation of drug candidates.

LLM-Evolver for Polymers – Claude-3.5 driven optimizer outperforms traditional Bayesian methods for designing polymer sequences.

ChemLatica – Family of small chemistry LLMs trained on 100M property-labeled molecules. Combines with evolutionary prompts.

VALID-Mol – Incorporates chemical validation filtering into LLM-driven evolutionary molecular design.



---

🧹 Prompt & Policy Optimization

EvoPrompt – Uses evolutionary search with LLM-informed mutation to discover superior prompts for >30 NLP tasks.

Promptbreeder – Self-mutating prompt generation. LLM breeds new prompts using self-descriptive meta prompts.

Vision-Language EvoPrompt – GA optimized prompts induced emergent tool-use behavior in multimodal LLMs.

Bayesian Prompt Optimization – BO in prompt space, using embeddings + surrogate models for search.

LLM Policy Evolvers (various) – Early-stage research into using LLMs to generate, mutate, or hybridize RL policies.



---

🔗 Related “Awesome” Repositories

wuxingyu-ai/LLM4EC — LLM + Evolutionary Computation survey and repo list.

turna1/Awesome-Multmodal_LLM — Multimodal LLM systems, datasets, and methods.

MLNLP-World/Awesome-LLM — LLM models, frameworks, fine-tuning, and downstream apps.

horseee/Awesome-Efficient-LLM — LLM compression, quantization, distillation.

sanjibnarzary/awesome-llm — General-purpose LLM awesome list.



---

Contributing

Have a framework to add? Submit a PR with the canonical link, a 1–3 sentence summary, and a domain tag.

License

MIT.
