---
title: "How I Fell Into the Homelab Rabbit Hole"
date: "2025-10-23T00:00:00Z"
tags: ["homelab", "kubernetes", "security", "raspberry-pi"]
---

It started with a professor saying: “use a password manager… but don’t fully trust it.” That kicked off a curiosity spiral. I wanted something secure that I could actually understand and control. Enter Vaultwarden, a spare Raspberry Pi from my bachelor’s project, and a dream — I began my homelab journey.

## Why homelab?

Freedom with a side of ~pain and suffering~ fun. I get to control how my data is stored, backed up, and secured — and when things break, I learn fast (and occasionally nuke something by accident).

- Learn by doing: build → break → fix → harden → repeat
- Own it end‑to‑end: no black‑box SaaS, no surprise paywalls (no more corporate giants slurping your data to train their “AI”)
- Automate the boring stuff: GitOps/IaC, repeatable setups across boxes (no AI touching the infrastructure, just plain old CI/CD)
- Privacy and reliability on my terms: my rules, my threat model, my backups, my responsibilities

Also: no monthly cloud‑storage tax.

## From `docker-compose up` to Kubernetes chaos

Honestly, too many homelab YouTube videos pulled me into this rabbit hole.  
After getting my password manager (Vaultwarden) up and running, the next problem was _secure access_. Living in a dorm with strict network policies meant port forwarding wasn’t an option (and it’s not great security anyway).

That’s when I discovered **Tailscale** — a mesh VPN built on WireGuard that creates a private, encrypted network between my devices. With single-sign-on and MagicDNS, I can now reach my services by name from anywhere without exposing ports to the internet. My tiny Pi suddenly became a globally accessible, self-hosted vault.

### Then came availability

SD cards aren’t built for long-term writes; a Raspberry Pi booting from one can just _poof_ out of existence. And since I’d rotated most of my important passwords (Google, banking, etc.) to 20-character random strings stored in Vaultwarden, losing that server would be a nightmare.

I _could’ve_ added an M.2 HAT or a USB SSD and called it a day — but, of course, I didn’t. Instead, I bought **three Raspberry Pi 5s** and built a **Kubernetes (K3s)** cluster to chase high availability. Cue the YAML hell.

It wasn’t as simple as “more nodes = more uptime.” Suddenly, I had to think about storage replication, backups, persistent volumes, and what happens when the node hosting my database just… vanishes.

That’s when I stumbled upon **Longhorn**, a distributed storage system that solved most of that — but that’s a story for another blog.  
(Also, fun fact: I only found out _after_ setting everything up that Vaultwarden isn’t designed for multi-replica deployments. So the “HA” I was chasing? Not really possible from the start.)

---

Not within two months, it’s not just a homelab anymore — it’s my own little cloud, powered by curiosity, caffeine, and way too much YAML.
