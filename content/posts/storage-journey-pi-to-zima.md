---
title: "My NAS solution: From a Not-So-Ok setup to a Kinda-OK setup"
date: "2025-10-27T00:30:00Z"
draft: false
tags:
  ["storage", "nas", "truenas", "openmediavault", "raspberry-pi", "zimablade"]
---

I started simple: a Raspberry Pi 4, a USB SSD, and OpenMediaVault.
It worked… until it didn’t.

This is how I went from a barely acceptable “good enough” NAS to something I can actually trust (well, kinda): **TrueNAS running on a ZimaBlade**.

## Why I Needed a NAS

My NAS journey began when I installed **Immich** on my Raspberry Pi 4 using Docker.
Then it hit me: if the SD card failed, every single backed-up photo would vanish instantly. If I wanted to ditch iCloud completely, I needed reliable storage — not a time bomb on an SD card.

I had a spare SSD from an old PC, so with a cheap USB adapter I thought I had solved storage forever.
Spoiler: I had not.

Another reason I wanted a NAS: I am too cheap to pay for **Obsidian Sync**. I use Obsidian on both my desktop and laptop, and my old “Git push/pull” syncing ritual constantly caused merge conflicts whenever edits collided. With a NAS, I could just store the vault centrally and avoid cloud subscriptions and sync failures entirely.

At the time, **OpenMediaVault** was the fastest way to get something working, so I went with it.

## When "Good Enough" Starts Feeling Risky

Even after upgrading to an SSD, I kept worrying about data loss. So I started looking into what a **proper** storage setup should look like: secure, redundant, and recoverable.

Everyone talks about the **3-2-1 backup rule** by photographer **Peter Krogh**:

> 3 copies of data, on 2 different types of media, with 1 copy stored off-site.

A great rule — and one I absolutely failed to follow (still failing, honestly).

The real problem was **cost**. The 3-2-1 strategy sounds responsible until you calculate the price on a student budget.

Example: a basic **RAID-Z1** with 3× 4TB drives:

- ~8TB usable storage with 4TB parity
- ~£90 per drive → **£270** just for disks
- Add a Synology NAS (~**£450**) → total already **£700+**

And that still doesn’t include off-site backups or cloud storage. For a student wallet… no thanks.

I needed something between “cheap but risky” and “proper but expensive” — something reliable **and** affordable.

Enter the **ZimaBlade**.

## To the Glory of ZimaBlade

After weeks of price comparisons and binge-watching NAS reviews on YouTube, I landed on the **ZimaBlade 7700 NAS Kit** — a compact single-board server built for DIY storage nerds, and ideal for cramped student housing.

The kit includes:

- ZimaBlade 7700 board (Intel Celeron)
- 16GB DDR3L RAM
- 12V/5A 60W USB-C power adapter
- 2-bay HDD rack
- SATA Y-cable

All for about **$160 (£121)** — dramatically cheaper than a prebuilt NAS.

Since the kit supports **two** HDDs, I needed two 4TB drives. So I did the logical thing for a broke student: I went hunting on eBay for refurbished drives. I scored **2 × 4TB HDD for £100** total.

Final build cost:

| Component          | Price    |
| ------------------ | -------- |
| ZimaBlade 7700 Kit | £121     |
| 2 × 4TB HDD        | £100     |
| **Total**          | **£221** |

For £221, I finally have a NAS that doesn’t feel like a time bomb. (more like a slowly ticking bomb now)
