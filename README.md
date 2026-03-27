# Collaborative Editing Proof of Concept

A proof of concept that demonstrates why Last-Write-Wins (LWW) fails in distributed collaborative editing, and how Operational Transformation (OT) fixes it by removing the dependency on timestamps entirely.

## Author's Note

I've been reading _Designing Data-Intensive Applications_ whilst simultaneously going through an [engineering lab](https://irreplaceable.engineer/lab/) that walks through the concepts in the book from first principles using systems thinking.
This POC was inspired by question 6 in the second assessment:

> Your team runs a collaborative document editor deployed globally (US, EU, Sydney). To handle concurrent edits, you implement last-write-wins (LWW) using server timestamps. Users in Sydney report that their edits sometimes "disappear" when US users edit the same document around the same time. The Sydney users swear they saved AFTER seeing the US user's changes.
>
> **Question:** What's causing the disappearing edits, and why is LWW with timestamps fundamentally broken for this use case?

My first instinct was that timezones were the culprit, but I realized quickly that's not the root cause. Even with all servers using UTC, clock skew can still occur when distributed server clocks drift out of sync with each other. Timezones are an offset problem; clock skew is a synchronization problem. Both are distinct.

This is the first time I've approached a problem like this. I found it fascinating enough to read further, which is where I encountered Operational Transformation (OT) and decided to build an experiment around it.

This experiment demonstrates two things:

1. How LWW silently discards real user data under clock skew.
2. And how OT resolves concurrent edits correctly by transforming operations against each other rather than relying on timestamps at all.

## Prerequisites

- Python 3.10+
- No external dependencies

## Getting Started

1. Clone the repository:

    ```bash
    git clone git@github.com:aybruhm/collaborative-editing-poc.git && cd collaborative-editing-poc
    ```

2. Run the experiment:

    ```bash
    python -m src.main
    ```

## What to Expect

The script runs two simulations and prints annotated output for each.

**Part 1: LWW (what was wrong)**
Two users edit the same document concurrently. Sydney's server clock is skewed behind real time. Despite Sydney writing physically after the US user, LWW rejects Sydney's edit because its server timestamp appears older. The final document is wrong, and no error is surfaced.

**Part 2: Operational Transformation (the fix)**
The same concurrent edits are replayed. The OT server detects that Sydney's operation is concurrent with the US operation and transforms Sydney's insert position to account for the characters the US user already inserted. Both edits are applied correctly and the document converges to the right state.
