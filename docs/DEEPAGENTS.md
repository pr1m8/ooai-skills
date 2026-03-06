# Deep Agents integration

Deep Agents discovers skills from local directories (it does not read from MinIO directly).

ooai-skills bridges that gap by pulling from MinIO into:

- `~/.agents/skills/` (flattened view)

## Verify Deep Agents sees the skills
```bash
deepagents skills list
```

## If Deep Agents does not see skills
1) Make sure you ran `ooai-skills pull --all`
2) Verify `~/.agents/skills` contains folders with `SKILL.md`
3) If symlinks are blocked (common on Windows), use:
   ```bash
   ooai-skills pull --all --copy
   ```
