---
date: 2026-04-21
tags:
  - ai
  - homelab
  - blog
title: 我的第一個真正 OpenClaw 工作流程：打造一個 GitHub 基礎設施 PR Review Agent
---
> 本文由 AI 翻譯。

OpenClaw，或 Clawbot，或不管它最近又把自己叫成什麼，算是少數幾個真的會讓我興奮的 AI 工具之一。

> 簡單講就是：它是一個可以跑在你自己機器上的 AI agent，而且真的能幫你做事。像是讀信並整理每日更新、掃描股市找可能被低估的股票，甚至處理一些生活雜事，例如規劃採買清單。

但這也是可怕的地方。一個能在你機器上行動的 agent 很有用，但如果你什麼都沒想清楚就把它接進所有東西裡，它也可以瞬間變成安全惡夢。

所以我問自己：*有沒有什麼既真實又有用、而且交給它做也不至於在安全上太愚蠢的任務？*

答案是 **基礎設施相依套件更新的初步判斷**。

因為我的 homelab 大多採用 GitOps 風格，基礎設施幾乎都用程式碼定義並放在公開 repo 裡。這讓這類任務比較適合委派：沒有機密，agent 只需要讀 repo 和 release notes，輸出也被限制在 GitHub comment 或我之後仍會審查的 PR。

管理基礎設施的 Renovate PR 很快就會變得很煩，尤其當同時有 20 多個開著的 PR，而且其中一些還提到可能有 breaking changes。大部分 PR 還是需要有人去讀 release notes、搞懂實際改了什麼，並判斷這些變更到底會不會影響這個 repo。

換句話說，這是一個 **高訊號、低風險的任務**：

- 高訊號，因為它真的需要閱讀 release notes 並理解變更內容
- 低風險，因為就算 agent 判斷錯，最糟也只是留下一則爛 comment，或開一個我可以忽略的 PR

這個組合很適合交給 agent：重複、有點花時間，但仍然夠結構化，讓我可以把範圍縮小、降低影響半徑。

下面是我目前 [homelab 架構](https://github.com/ysonC/super-homelab#architecture-overview) 的快速總覽。你可以看得出來，如果每個 dependency 都要手動一個一個管理，真的會很痛苦。

![585803381 acfd7ea4 0e29 4214 9965 78da89e783d5](/images/585803381-acfd7ea4-0e29-4214-9965-78da89e783d5.png)

## 目標

我想替自己的 homelab repo `ysonC/super-homelab` 做一個範圍很窄的工作流程。

任務很簡單：

1. 掃描開著的 Renovate PR
2. 閱讀 PR 內容和上游 release notes
3. 判斷 breaking change 是否真的影響我的基礎設施
4. 如果不需要修改 repo，就留下一則有用的 review comment
5. 如果需要修改 repo，就建立修正 branch 和對應的 companion PR

重點是它不做什麼。它 **不會 merge 任何東西**。它 **不會取得寬泛的 GitHub 權限**。它 **不會像一般用途的 coding agent 一樣到處亂逛**。

它只負責做無聊的初步篩選，最後決定權仍然留給我。

## 設定概覽

在進入檔案和設定細節之前，這張圖最值得先看。它展示了存取、委派與行動之間的邊界。我透過 **Tailscale** 存取 OpenClaw，OpenClaw 跑在 **Proxmox LXC** 裡，而實際的 GitHub 工作則被下放到一個任務非常明確的小 agent。

![ChatGPT Image Apr 30, 2026, 01 58 22 PM](/images/ChatGPT%20Image%20Apr%2030%2C%202026%2C%2001_58_22%20PM.png)

用白話來說，流程大概是這樣：

> 我透過 Tailscale 連到 OpenClaw，OpenClaw 跑在 Proxmox LXC 裡，gateway 把請求交給 Bob，而 Bob 再把基礎設施 PR review 的工作委派給 Popeye。接著 Popeye 會 review GitHub PR，然後不是留 comment，就是開一個包含修正的 companion PR。

## 為什麼我另外建立一個 Agent

Popeye 是我主要助理 Bob 底下的一個專用 agent。

原因是責任分離。Bob 仍維持一般用途助理的角色，而 Popeye 只處理基礎設施 PR 審查。這讓整個設定現在更容易理解，之後如果我要加入其他負責不同工作的 agent，也比較容易擴充。

這也對安全模型有幫助。Popeye 的工作越明確，我就越容易寫出有用的指令、定義邊界，並在它偏離預期路徑時察覺。

## 定義護欄

第一個階段主要是在定義行為和護欄，避免 Popeye 跑去做一些莫名其妙的事情。

Bob 和我最後整理出一小組檔案，讓整個流程變得可預期：

- `popeye-agent.md`：政策與範圍
- `popeye-agent-prompt.md`：執行時指令
- `popeye-agent-config.yaml`：repo、labels、paths 與行為設定
- `popeye-report.md`：報告輸出
- `analyzed-open-items.json`：追蹤已處理過的 open PR

這部分比我一開始想的還重要。邊界和指令寫得越清楚，實際跑起來就越不像在跟一個又笨又過度自由的東西搏鬥。

我也想避免 spam。如果 Popeye 今天已經看過某個 open PR，我不希望它明天在沒有任何變化的情況下又送一模一樣的東西給我。

*目標不是讓 Popeye 變成某種模糊意義上的「聰明」。目標是讓它無聊、可重複，而且受限制。*

## 設定 GitHub 存取

行為定義好之後，下一步就是給 Popeye 它真正需要的能力。最重要的是 [GitHub](https://clawhub.ai/steipete/github) 技能。

我只會從我信任的來源安裝技能。讓 AI agent 存取 GitHub 本來就已經有點毛了，如果再隨便裝來路不明的第三方技能，感覺就像是在自找麻煩。這次的技能來自 *Peter Steinberger*，也就是 OpenClaw 的作者，所以我覺得算是合理可接受。

我也不想直接把自己的 GitHub 個人帳號交出去。那看起來是完全不必要的風險。所以我另外建立了一個專門給 agent 用的帳號：`wyson-clawdy-botty`。

這可以把影響範圍縮小。機器人可以在既有的 Renovate PR 上留言，也可以開 follow-up PR，但它不能到處用我的身分亂跑。這不會完全消除 AI 產出廢話或錯誤內容的風險，但會讓整個 workflow 更容易接受。

這也是我在 agent workflow 裡最在意的事情：**給它有用的權限，而不是最大的權限**。

## 排程執行

cron job 老實說是最簡單的部分。

我請 Bob 建立一個每天中午執行的排程，然後這部分就完成了。

每天中午，Popeye 會檢查開著的 PR，判斷是否需要後續處理，並把狀態報告送到 Slack。我也把 Popeye 接上 Slack，讓它在審查 PR 之後可以傳更新給我。

## 最終結果

最後得到的是一個能安靜處理 homelab 維護中某個小但煩人的部分的 workflow。你可以在這裡看到，agent 掃描了五個由我的 n8n workflow 預先標記為可能有 breaking changes 的 open PR，並找出其中一個真的需要手動更新。

![Pasted image 20260421151509](/images/Pasted%20image%2020260421151509.png)

當 Popeye 發現某個 Renovate PR 可能包含 breaking change 時，它會檢查 release notes，並把變更和我的 repo 做比較。如果該變更不影響我，它會留下一則留言，說明為什麼不需要更新 repo。

如果該變更會影響我的基礎設施，它就會建立一個 companion PR，裡面包含摘要和建議修正。

![Pasted image 20260421151822](/images/Pasted%20image%2020260421151822.png)
![Pasted image 20260421151835](/images/Pasted%20image%2020260421151835.png)

這裡是一個需要使用者在更新前，先從 Redis 切換到 Valkey 的例子。

之後，我會 **手動審查** 這個變更提案。如果看起來沒問題，我才會把更新和修正 merge 進 repo。

## 我喜歡這個 Workflow 的地方

我喜歡這個 workflow 的地方，是它的範圍很窄。

我不是要一個 agent 來管理我的人生。我只是要它處理一個重複的基礎設施任務，而且這個任務本來就有清楚的模式：

1. 讀 PR
2. 讀 release notes
3. 判斷 breaking change 是否重要
4. 要嘛解釋為什麼安全，要嘛準備一個修正

以目前來說，這感覺是剛剛好的信任程度。
