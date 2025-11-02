---
date: "2025-11-02T15:46:33Z"
draft: false
title: "About"
---

Hi there, I’m Wyson Cheng, a security‑minded developer who fell down the homelab rabbit hole while studying Cyber Security at the University of Edinburgh for my master’s. It started in a lecture when the professor said we should all use a password manager—then quickly added we shouldn’t fully trust it either. That got me thinking about how to build the most secure setup for me. I dusted off my old Raspberry Pi 4 from my bachelor’s dissertation at the University of Nottingham, where I built a facial recognition system. That’s when I first got into Docker—the first time I did anything beyond a PHP server, lol. These days I run a K3s cluster on 3 Raspberry Pi 5 devices, provisioned with Ansible and managed GitOps‑style with Flux + Kustomize; Traefik handles ingress, Longhorn provides storage, CloudNativePG powers PostgreSQL, and Prometheus/Grafana monitor the stack—apps like Vaultwarden, Immich, and n8n included. I also have a ZimaBlade running TrueNAS for storage and an N150 machine running Proxmox for networking (here is my project: https://github.com/ysonC/super-homelab).

So how did I get from Docker to Kubernetes? Honestly, too many homelab YouTube videos. After getting my password manager (Vaultwarden) up and running, securely accessing it was the next problem. Living in a dorm with strict network security management meant port forwarding wasn’t an option (and it’s not great security anyway). I found Tailscale—a mesh VPN built on WireGuard that creates a private, encrypted network between my devices. With single‑sign‑on and MagicDNS, I can reach my services by name from anywhere without exposing ports to the internet.

## Experience

### Intern - Deloitte

Taipei, Taiwan
Jul. 2023 - Sep. 2023

- Engaged in a dynamic internship focusing on software development and agile management.
- API Development and Maintenance: Developed and maintained APIs using MuleSoft. Managed tasks and deadlines efficiently using JIRA. Addressed evolving client requirements and change requests, maintaining high-quality solutions.
- Testing and Debugging: Collaborated with team members to replicate client-identified bugs and diagnose possible solutions. In charge of communicating with the development team.
- UI Design and Adaptability: Created new UI designs in response to client requirements and developed reusable templates. Enhanced design efficiency and project scalability.

## Projects

### Home Lab (Individual Project)

Jan. 2025 - Present

- Built a cluster on three Raspberry Pi 5 devices, leveraging K3s for lightweight Kubernetes orchestration.
- Employed Ansible to provision and configure the cluster and used Kustomize for environment-specific configurations.
- Implemented Flux for GitOps continuous delivery, ensuring seamless rollouts and version control across the entire setup.
- Deployed Longhorn for container-native distributed storage, integrated CloudNativePG for a robust PostgreSQL operator in Kubernetes, and configured Traefik as the Ingress Controller.
- Utilised Tailscale for secure remote access and set up a Prometheus & Grafana monitoring stack to capture real-time metrics and performance insights.
- Continually refining the environment to adopt new tools, improve automation pipelines, and enhance system resilience.

### Memory Safety Execution in C (Master Dissertation)

Mar. 2025 - Sep. 2025

- Conducted a master’s dissertation comparing Checked C, Fail-Safe C, and Rust in retrofitting memory safety to legacy C software.
- Developed and benchmarked Zlib 1.3.1 and micro-benchmarks to evaluate performance, safety coverage, and developer effort.
- Implemented automated build and profiling pipelines across legacy toolchains and modern compilers.
- Quantified spatial and temporal protection trade-offs through runtime analysis and code-conversion metrics.
- Produced a comprehensive evaluation informing practical paths toward safer systems programming in C ecosystems.

### Face Recognition with Raspberry Pi (Bachelor Dissertation)

Dec. 2023 - May. 2024

- Designed and implemented a low-cost home security system using Python, Flask, OpenCV, and TensorFlow on a Raspberry Pi, featuring real-time face recognition and motion detection.
- Trained a Siamese neural network in Google Colab to perform one-shot face recognition, optimised for single-user accuracy (~85%) and efficient on-device inference.
- Developed a secure, user-friendly web interface for access control and remote monitoring.
- Ensured ethical and privacy-conscious use by employing diverse training samples, bias-aware evaluation, and local, privacy-preserving data storage.

## Additional

**Language Skills:** Chinese and English (Fluent Speaking/Writing); Japanese (Passed N2 Language Proficiency Test)
**Technical Skills:** C++, C, Python, Java, Golang, SQL, Unix/Bash
**Volunteer Experience:** Volunteered as an English and Science teacher at rural schools to help underprivileged students gain access to better education and learning opportunities.
**Interests/Hobbies:** Certified Shi/Sake Sommelier by Sake Service Institute (SSI): International Kikisake-Shi/Sake Sommelier (Mar. 2022)
