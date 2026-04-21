---
date: 2026-04-21
title: My First Real OpenClaw Workflow, Building a GitHub PR Review Agent for Infrastructure
tags:
  - ai
  - github
  - infrastructure
  - homelab
---

> [!info] TL;DR
> I built an OpenClaw workflow to deal with annoying Renovate PRs in my homelab repo. It checks whether a breaking change actually matters to my infrastructure, then either leaves a review comment or opens a follow-up fix PR, all without giving the bot full access to everything.

OpenClaw, or Clawbot, or whatever it is calling itself these days, is one of the few AI tools that actually gets me excited.

The short version is simple: it is an AI agent that can run on your own machine and do real stuff for you. That could mean reading email and sending daily updates, scanning the stock market for undervalued stocks, or even doing grocery shopping. All of that also sounds like a security nightmare, but it is still pretty damn cool that you can have an AI assistant helping with actual tasks.

That got me thinking: what is a task I can hand over to it without doing something stupid security-wise?

For me, the answer was infrastructure dependency updates.

Managing Renovate PRs for infrastructure gets annoying really fast, especially when you suddenly have 20+ open PRs and a bunch of them mention possible breaking changes. Most of those PRs still need someone to read the release notes, figure out what actually changed, and decide whether it matters for the repo or not.

## The Goal

The core workflow was straightforward in principle:

- Scan open PRs
- Focus on Renovate PRs tagged with `ai-breaking-change`
- Check whether the reported breaking change actually affects my infrastructure
- If it does not, leave a useful review comment explaining why no change is needed
- If it does, prepare a fix and open a companion PR

So basically, let the bot handle the boring triage part without giving it the keys to the kingdom.

## Why I Created a Separate Agent

So I created a dedicated agent under my main assistant, Bob, and named it Popeye.

The reason was pretty simple. I wanted better separation of responsibilities. Popeye handles infrastructure PR review work only, for now. That makes the setup easier to manage now and easier to expand later if I end up adding more agents with different jobs.

## What I Wanted Popeye To Do

I wanted Popeye to do one thing only: handle infrastructure-related PR review work for my homelab repo.

More specifically, I wanted it to:

1. Scan open PRs in `ysonC/super-homelab`
2. Focus on PRs labeled `ai-breaking-change`
3. Read the PR body and upstream release notes
4. Identify the real breaking change, not just the version bump
5. Check whether that breaking change affects the infrastructure definitions in my repo
6. If it does affect the repo, create a follow-up fix branch and a companion PR
7. If it does not affect the repo, leave a useful review comment explaining what changed and why no repo update is needed

I also wanted to avoid spam. If Popeye already looked at an open PR today, I did not want it sending me the exact same thing again tomorrow unless something actually changed.

## Defining the Agent

The first stage was mostly about defining behavior and guardrails so Popeye would not go off and do random nonsense.

Bob and I ended up with a small set of files to make the workflow predictable:

- `popeye-agent.md` for the policy and scope
- `popeye-agent-prompt.md` for the runtime instructions
- `popeye-agent-config.yaml` for repo, labels, paths, and behavior settings
- `popeye-report.md` for reporting output
- `analyzed-open-items.json` for tracking already processed open PRs

This part mattered more than I expected. The better the boundaries and instructions were, the less dumb the workflow felt in practice.

## Setting Up GitHub Access

Once the behavior was defined, the next step was giving Popeye the skills it actually needed. The most important one was the [GitHub](https://clawhub.ai/steipete/github) skill.

I would only install skills from sources I trust. Giving an AI agent GitHub access is already sketchy enough, so pulling in random third-party skills feels like asking for trouble. In this case, the skill came from Peter Steinberger, who also builds OpenClaw, so that felt reasonable enough.

I also did not want to hand over my personal GitHub account. That just seemed stupid. So I created a separate account just for the agent: `wyson-clawdy-botty`.

That way, even if the setup blows up, the blast radius stays small. The bot can comment on existing Renovate PRs and open follow-up PRs, but it cannot just run around as me everywhere. That does not remove the risk of AI-generated slop, but it does make the whole thing easier to live with.

## Scheduling the Run

The cron job was honestly the easiest part.

I asked Bob to create a daily run at noon, and that part was done.

## The Final Result

Every day at noon, Popeye gets prompted to check open PRs and see if any changes are needed, then send the report to Slack. I also wired Popeye into Slack so it could send me status messages when it reviewed PRs.

![Pasted image 20260421151509](/images/Pasted%20image%2020260421151509.png)

If it finds an actual breaking change that needs my attention, it will create a PR with a summary and proposed change.

![Pasted image 20260421151822](/images/Pasted%20image%2020260421151822.png)
![Pasted image 20260421151835](/images/Pasted%20image%2020260421151835.png)
(here is an example of an update that requires users to switch from redis to valkey before updating)

Then after I manually review it, I can merge the update and fix into my repo.

## What I Like About This Workflow

What I like about this workflow is that it is narrow.

I am not asking an agent to run my life. I am asking it to do one repetitive infrastructure task that already follows a pretty clear pattern:

- Read the PR
- Read the release notes
- Figure out whether the breaking change matters
- Either explain why it is safe or prepare a fix

That feels like the right level of trust for now.

It saves me time on repetitive triage, keeps access limited, and still leaves the final merge decision to me.
