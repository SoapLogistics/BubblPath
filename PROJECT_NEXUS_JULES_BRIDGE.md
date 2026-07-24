# PROJECT_NEXUS_JULES_BRIDGE

## Overview
**Project Nexus** is the architectural bridge between **Solomon** (the cognitive, browser-based Observer and Planner) and **Jules** (the autonomous Builder and Executor).

Through the Solomon Browser Companion, Solomon can read webpages, review GitHub PRs, or identify bugs in the DOM. With Project Nexus, Solomon can now dynamically spin up Jules sessions, delegate writing/fixing code, automatically approve Jules's changes, and trigger deployments.

## The Pipeline (Writing -> Approving -> Deploying)

1. **Context Acquisition:** Solomon's browser companion (`content.js`) reads a GitHub issue, a PR diff, or a broken webpage.
2. **Delegation (`[DELEGATE_JULES]`)**: Solomon determines a code change is needed. He outputs `[DELEGATE_JULES: instructions]`. The sidepanel intercepts this and hits the Flask backend `/api/jules/delegate`.
3. **Execution (Writing):** Jules wakes up in the backend sandbox, creates a plan, and writes the code.
4. **Approval (`[APPROVE_JULES]`)**: Once Jules finishes a draft, Solomon can review the output. If acceptable, Solomon issues `[APPROVE_JULES: branch_name]`.
5. **Deployment (`[DEPLOY_JULES]`)**: Solomon finalizes the workflow by issuing `[DEPLOY_JULES: branch_name]`, prompting Jules (or the backend CI/CD) to merge and deploy.

## UI Implementation (The Nexus Dashboard)
The sidepanel features a dedicated "Nexus Uplink" UI. It visually tracks the state of the delegated task:
- 🟢 **IDLE**
- ⚡ **JULES WRITING...** (Pulsing animation)
- ⏳ **AWAITING APPROVAL**
- 🚀 **DEPLOYING...**

## Safety Boundaries
While Solomon can instruct Jules to write and deploy code, **Strict Manual Approval** by the human user is still required to initiate the `[DELEGATE_JULES]` command via the sidepanel UI, ensuring autonomous runaway loops do not occur without human oversight.