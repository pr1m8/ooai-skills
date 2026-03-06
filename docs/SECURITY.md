# Security notes

Skill packs are executable **instructions** for an agent.

- Treat third-party skill repos like untrusted code.
- Prefer mirroring a small allowlist first.
- Avoid enabling powerful tools (shell/network/write) unless needed.
- If you run agents in shared environments, consider separate registries or prefixes.

ooai-skills itself never executes downloaded skill content; it only copies/upload/downloads files.
