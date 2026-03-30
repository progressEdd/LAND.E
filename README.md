# LAND.E

## Presentation
This branch is for my notes and presentation materials

## Preparing for a demo
These instructions assume that you already have bun and uv installed, and you haven't added the branches as worktrees
1. Have the webapp-ui branch in the worktree
   1. Initialze the worktree with  `git worktree add 02-worktrees/webapp-ui webapp-ui`
2. Build the demo environments:
   1. ```bash
      cd 02-worktrees/webapp-ui
      uv sync
      ```
   2. ```bash
      cd 02-worktrees/webapp-ui/frontend
      bun install
      ```
3. Running the demo (from a new terminal)
   1. ```bash
      cd 02-worktrees/webapp-ui/backend
      uv run uvicorn app.main:app --reload --port 8000
      ```
   2. ```bash
      cd 02-worktrees/webapp-ui/frontend
      bun run dev
      ```
4. If you want to show the marimo:
   1. Initialize the workree with `git worktree add 02-worktrees/webapp-ui webapp-ui`
   2. Build the demo environment `uv sync`
   3. start the server `uv run marimo run app.py`
5. open the ports in vscode's integrated browser