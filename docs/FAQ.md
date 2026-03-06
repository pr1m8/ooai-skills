# FAQ

## Does Deep Agents read from MinIO directly?
No. Deep Agents reads skills from local folders. ooai-skills pulls from MinIO into those folders.

## Why is there an index?
The index (`index/skills.json`) makes pulling deterministic and avoids listing the entire bucket.

## Can I store multiple “bundles”?
Yes. Use different `--pack` names with `push-local`, or ingest different curated categories. Everything merges into the index.
If you want strict separation, use different buckets or add a second install of ooai-skills with different env vars.

## Windows symlinks?
Symlink creation may be restricted. ooai-skills auto-falls-back to copying when symlinks fail, or use `--copy`.
