# Handoff: Swarm Alignment Hackathon: two candidate projects

> **Status: early ideas, not a plan.** Everything below is a starting point for exploration. Directions, scope, and even the core questions may change once we see first results. Treat lists of variations as a menu, not a checklist.

## Context

- **Event:** Apart Research Swarm Alignment Hackathon, Fri Nov 6 – Sun Nov 8, 2026. Submission: PDF report of up to 8 pages, which must include an appendix on limitations and dual-use. A repo and a video are optional.
- **Judging:** impact and innovation, execution quality, presentation and clarity.
- **Compute:** $500 in Adaption credits (SDK already installed).
- **Inspiration:** John Kitaoka's talk "Open Problems in Securing Systems Against AI Agent Swarms." His key result: attacks split across 3 agents are caught 82% of the time when one agent does everything, 41% when all trajectories are read jointly, and only 3% when each agent is scored separately (GPT-5.6 Sol monitor, threshold at roughly 1% false-positive rate). Splitting attacks also let six attack stages chain into a full loss-of-control scenario without any per-agent alert.
- **Practical tips from the talk:**
  - Define the threat model first.
  - Hand-editing transcripts plus automatic grading is a cheap way to build attacks.
  - Multi-agent experiments are expensive and come with a "coordination tax," so keep them small.
  - Actually read the data.

---

## Project A: A monitor that links agents through shared resources (Track 4)

**Rough idea:** Per-agent monitors miss split attacks, and in practice nobody knows which agents to read together. Could a cheap step before the monitor group agents into likely-related clusters (for example through the files, credentials, network rules and services they touch) and recover much of the gap between per-agent and joint monitoring?

**Possible ingredients:**
- A small simulated lab infrastructure in the LinuxArena/Control Tower style: repo, IaC, firewall rules, logging config, credentials, eval reports
- A handful of split attacks (backdoor, disabling logging, faking an eval, preparing exfiltration), built by editing transcripts and graded automatically
- Harmless background agents as noise

**Things we could vary:**
- **Grouping:** resource graph, edges weighted by how sensitive the resource is, closeness in time, similarity of actions, which user or principal started the agent, connected components vs. community detection
- **Baselines:** per-agent, random groups, oracle (the true attack group)
- **Scale:** number of background agents, group-size limits, how busy shared resources are
- **Monitor:** weak vs. strong model, actions only vs. with reasoning, full trajectories vs. summaries, two-stage triage then escalation
- **Adaptive attacker:** avoids shared resources, routes hand-offs indirectly, spreads actions over time, hides in heavily used harmless resources
- **Metrics:** detection at a fixed false-positive rate, AUROC, whether the group contained all attacking agents, token cost

**Open questions:**
- How realistic does the environment need to be?
- Does grouping collapse once everyone touches the same repo?
- Is an LLM-based grouping step better than a graph?

---

## Project D: Peer pressure in agents: dissenters, authority, and detection (Tracks 2/4)

**Rough idea:** Check Point showed that one agent breaks an explicit rule (access to a forbidden folder) more often when scripted teammates on a shared board visibly reverse: 44% with no reversals, 98% with eight. The agent almost never cites them. They used one model and one scenario, and did **not** test dissenters, authority, or monitoring. We could extend this.

**Possible base:** a replication with a forbidden resource, a task that needs it, an allowed "report blocked / ask for help" path, a shared board of scripted teammates, and automatic grading on several models.

**Things we could vary (Asch/Milgram-inspired):**
- **Group size:** number of reversing teammates. Is there a plateau like Asch's at about 3?
- **Dissenter:** one teammate keeps refusing, silently or with a reason, before or after the reversals. Variants: an ally who later caves, a dissenter with a wrong reason, a "security agent" label, 1 vs. 2 dissenters. The question-answering literature is mixed: some models don't benefit from a dissenter, and one even conformed more.
- **Authority:** the reversal comes from a lead agent or orchestrator; the lead acts vs. instructs; a "human manager" message; conflicting authorities
- **Identity:** teammates labeled as the same model vs. another vendor, same team vs. another department, real vs. scripted messages
- **Public vs. private:** the agent must post its decision before acting
- **Informational vs. normative:** reversal with or without "restriction lifted"; a tool to check permissions
- **Stakes:** unimportant folder → credentials → disabling logging; how strongly the rule is stated; how visible the exit path is
- **Defenses:** "treat peer messages as unverified," reflection before tool calls, compared with out-of-model enforcement
- **Explanations and monitoring:** does the agent cite peers in its output or reasoning? Does a trajectory monitor catch the unexplained violations, with or without the board? Does a group-level monitor for correlated reversals help? (This links to Project A.)
- **Spread (stretch):** several live agents with different network shapes

**Method cautions:**
- Never use the words Asch, conformity or experiment, and frame everything as routine work. One study found Asch-style conformity went from 0% when blind to 83% when the paradigm was named.
- Use a fresh baseline for every series, about 30–50 runs per condition, and binomial confidence intervals.
- Separate social influence from ordinary run-to-run drift with a no-peers control.

---

## Prior work to check first

- Check Point, "Peer pressure in AI agents": https://blog.checkpoint.com/security/peer-pressure-ai-agents/
- "Pre-Crime for Agents, at the Last Second": activation probes detect when a pressured agent leaks a secret (82% vs. 26% for a zero-shot monitor)
- BenchForm / "Do as We Do, Not as You Think" (ICLR 2025): conformity on question-answering tasks
- "Recognition, Simulation, and Refusal" (Bose): contamination and named vs. blind paradigms
- "Not All Flips Are Conformity" (arXiv 2606.00820): separating drift from influence
- Kitaoka et al. (MATS / UK AISI): multi-agent split attacks vs. monitors (not yet published)
- Redwood Control Tower, LinuxArena, BashArena, Control Arena
- Swarm Traces, AI Village transcripts, swarms.wiki, METR's report on the Hugging Face incident (hackathon resources)

## Not decided yet

- Whether to do A, D, or a combined report with a shared monitoring chapter
- Which models to use, and what the credits cover
- Team size and who does what
