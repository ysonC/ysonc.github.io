---
date: 2026-04-21
tags:
  - ai
  - homelab
  - blog
title: My First Real OpenClaw Workflow, Building a GitHub PR Review Agent for Infrastructure
---
OpenClaw, or Clawbot, or whatever it is calling itself these days, is one of the few AI tools that actually gets me excited.

> The short version is simple: it is an AI agent that can run on your own machine and do real stuff for you. That could mean reading email and sending daily updates, scanning the stock market for undervalued stocks, or even helping with chores like grocery planning.

That is also where it gets scary. An agent that can act on your machine is useful, but it can also become a security nightmare if you wire it into everything without thinking.

So the question for me was: *what is a real task I can hand over without doing something stupid security-wise?*

The answer was **infrastructure dependency update triage**.

Managing Renovate PRs for infrastructure gets annoying really fast, especially when there are 20+ open PRs and some of them mention possible breaking changes. Most of those PRs still need someone to read the release notes, figure out what actually changed, and decide whether the change matters for the repo.

Here's a quick overview of my current [homelab structure](https://github.com/ysonC/super-homelab#architecture-overview), as you can see, individually managing each dependency would be a nightmare.

![585803381 acfd7ea4 0e29 4214 9965 78da89e783d5](/images/585803381-acfd7ea4-0e29-4214-9965-78da89e783d5.png)

That is repetitive work, but it is not work I want fully automated all the way to merge.

## The Goal

I wanted a narrow workflow for my homelab repo, `ysonC/super-homelab`.

The job was simple:

1. Scan open Renovate PRs
2. Focus on PRs labeled `ai-breaking-change`
3. Read the PR body and upstream release notes
4. Decide whether the breaking change actually affects my infrastructure
5. Leave a useful review comment if no repo change is needed
6. Create a fix branch and companion PR if a repo change is needed

The important part is what it **does not do**. It **does not merge anything.** It **does not get broad GitHub access**. It **does not act like a general-purpose coding agent** with permission to wander around.

It handles the boring triage step, then leaves the final decision to me.

## Workflow Overview

Before getting into the files and setup, this diagram is the part worth looking at first. It shows the boundary between access, delegation, and action. I access OpenClaw through **Tailscale**, OpenClaw runs inside a **Proxmox LXC**, and the actual GitHub work is pushed down into a smaller agent with a very specific job.

![ChatGPT Image Apr 30, 2026, 01 58 22 PM](/images/ChatGPT%20Image%20Apr%2030%2C%202026%2C%2001_58_22%20PM.png)

In plain language, the flow looks like this: 

> I reach OpenClaw through Tailscale, OpenClaw runs in a Proxmox LXC, the gateway hands the request to Bob, and Bob delegates infrastructure PR review work to Popeye. Popeye then reviews the GitHub PR and either leaves a comment or opens a companion PR with the fix.

That diagram became the bridge between the idea and the implementation. I did not want one big assistant with vague instructions and broad access. I wanted a small workflow where each layer had a clear reason to exist.

## Why I Created a Separate Agent

Popeye is a dedicated agent under my main assistant, Bob.

The reason is separation of responsibilities. Bob can remain the general assistant, while Popeye only handles infrastructure PR review work. That makes the setup easier to reason about now, and easier to expand later if I add more agents with different jobs.

This also helped with the security model. The more specific Popeye's job is, the easier it is to write useful instructions, define boundaries, and notice when it is doing something outside the expected path.

## Defining the Guardrails

The first stage was mostly about defining behavior and guardrails so Popeye would not go off and do random nonsense.

Bob and I ended up with a small set of files to make the workflow predictable:

- `popeye-agent.md` for the policy and scope
- `popeye-agent-prompt.md` for the runtime instructions
- `popeye-agent-config.yaml` for repo, labels, paths, and behavior settings
- `popeye-report.md` for reporting output
- `analyzed-open-items.json` for tracking already processed open PRs

This part mattered more than I expected. The better the boundaries and instructions were, the less dumb the workflow felt in practice.

I also wanted to avoid spam. If Popeye already looked at an open PR today, I did not want it sending me the exact same thing again tomorrow unless something actually changed.

*The goal was not to make Popeye clever in a vague way. The goal was to make it boring, repeatable, and constrained.*

## Setting Up GitHub Access

Once the behavior was defined, the next step was giving Popeye the skills it actually needed. The most important one was the [GitHub](https://clawhub.ai/steipete/github) skill.

I would only install skills from sources I trust. Giving an AI agent GitHub access is already sketchy enough, so pulling in random third-party skills feels like asking for trouble. In this case, the skill came from *Peter Steinberger*, who also builds OpenClaw, so that felt reasonable enough.

I also did not want to hand over my personal GitHub account. That seemed like an unnecessary risk. So I created a separate account just for the agent: `wyson-clawdy-botty`.

That keeps the blast radius smaller. The bot can comment on existing Renovate PRs and open follow-up PRs, but it cannot run around as me everywhere. That does not remove the risk of AI-generated slop, but it makes the workflow easier to live with.

This is the part I care about most with agent workflows: **useful access, not maximum access**.

## Scheduling the Run

The cron job was honestly the easiest part.

I asked Bob to create a daily run at noon, and that part was done.

Every day at noon, Popeye checks open PRs, decides whether any follow-up work is needed, and sends a status report to Slack. I also wired Popeye into Slack so it could send me updates when it reviewed PRs.

## The Final Result

The end result is a workflow that quietly handles a small but annoying part of homelab maintenance.

![Pasted image 20260421151509](/images/Pasted%20image%2020260421151509.png)

When Popeye finds a Renovate PR with a possible breaking change, it checks the release notes and compares the change against my repo. If the change does not affect me, it leaves a comment explaining why no repo update is needed.

If the change does affect my infrastructure, it creates a companion PR with a summary and proposed fix.

![Pasted image 20260421151822](/images/Pasted%20image%2020260421151822.png)
![Pasted image 20260421151835](/images/Pasted%20image%2020260421151835.png)

Here is an example of an update that requires users to switch from Redis to Valkey before updating.

After that, I **manually review** the proposed change. If it looks right, I merge the update and the fix into my repo.

## What I Like About This Workflow

What I like about this workflow is that it is narrow.

I am not asking an agent to run my life. I am asking it to do one repetitive infrastructure task that already follows a clear pattern:

1. Read the PR
2. Read the release notes
3. Figure out whether the breaking change matters
4. Either explain why it is safe or prepare a fix

That feels like the right level of trust for now.

