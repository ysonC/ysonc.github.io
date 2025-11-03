---
title: "How I Fell Into the Homelab Rabbit Hole"
date: "2025-11-03T00:00:00Z"
draft: false
tags: ["homelab", "kubernetes", "security", "tailscale", "raspberry-pi"]
---

It started with a simple lecture note: “use a password manager… but don’t fully trust it.” That kicked off a curiosity spiral. I wanted something secure that I could actually understand and control. Enter Vaultwarden, a spare Raspberry Pi from my bachelor’s project, and the beginning of the homelab rabbit hole.

## Why homelab?

Freedom with a side of ~pain and suffering~ fun. I get to control how my data is stored, backed up, and secured — and when things break, I learn fast (and occasionally nuke something by accident).

- Own it end‑to‑end: no black‑box SaaS, no surprise paywalls
- Learn by doing: build → break → fix → harden → repeat
- Automate the boring stuff: GitOps/IaC, repeatable setups across boxes (no AI touching the infrastructure, just plain old CI/CD)
- Privacy and reliability on my terms: my rules, my threat model, my backups

Also: no monthly cloud‑storage tax.

## How did I get from simple `docker-compose up` to a Kubernetes cluster?

Honestly, too many homelab YouTube videos got me into this rabbit hole. After getting my password manager (Vaultwarden) up and running, securely accessing it was the next problem. Living in a dorm with strict network security management meant port forwarding wasn’t an option (and it’s not great security anyway). I found Tailscale—a mesh VPN built on WireGuard that creates a private, encrypted network between my devices. With single‑sign‑on (via an identity provider) and MagicDNS, I can reach my services by name from anywhere without exposing ports to the internet.
