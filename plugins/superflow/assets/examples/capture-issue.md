<!-- superflow:issue v1 -->

Source: inline
Confidence: low
Route: inbox_only
Phase budget: capture
Local package: none

# PRD: Ideia de onboarding

## Problem

Ideia solta para melhorar onboarding depois.

## Goal

Registrar sem transformar em trabalho local ainda.

## Users / Actors

- Marco or the backlog operator.

## Story de Usuario

As the operator, I want to save the idea without creating local execution work
so it can be revisited later.

## Story Tecnica

As Superflow, keep this in GitHub inbox form until promotion creates a local
PRD package.

## Current Behavior / Bug

The idea is not yet committed to local work.

## Desired Behavior

The issue captures the idea with enough shape to promote later.

## System Pattern / Contract

GitHub is the inbox. Local `specs/NNN-*` folders are created only on promotion.

## Acceptance Criteria

- [ ] A ideia fica capturada em issue.
- [ ] Nenhuma pasta `specs/NNN-*` e criada.

## Definition of Complete

- [ ] Issue body is saved with Superflow metadata.

## Next Phase

Promote when mature.
