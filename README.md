# OSS License Kit: AGPL-3.0 + Commercial dual license

A drop-in kit for publishing code openly while keeping commercial rights and keeping private assets out of git.

## What's in `template/`

| File | Purpose |
|---|---|
| `LICENSE` | Full AGPL-3.0 text (SPDX `AGPL-3.0-only`) |
| `COMMERCIAL.md` | When a paid license is required, and how to get one |
| `CLA.md` | Contributor License Agreement: contributors grant relicensing rights, so dual licensing keeps working |
| `NOTICE` | Copyright plus a trademark reservation (forks must rename) |
| `CONTRIBUTING.md`, `SECURITY.md`, PR template | CLA checkbox, header rules, disclosure policy |
| `.gitignore` | Weights, datasets, secrets, experiment logs |
| `scripts/commitguard.py` | Pre-commit guard, stdlib-only Python 3.9+ |
| `scripts/install-hooks.sh` / `.ps1` | Plain git hook install, no dependencies |
| `.pre-commit-config.yaml` | commitguard + gitleaks + standard hygiene hooks |
| `.github/workflows/commitguard.yml` | Runs the same checks in CI, so `--no-verify` doesn't get past it |

## What commitguard blocks

- **Weights and serialized models:** `.pt .pth .ckpt .safetensors .onnx .h5 .pkl .joblib .gguf .tflite .engine` and similar
- **Datasets:** `.parquet .npy .npz .arrow .tfrecord .sqlite .db`, plus anything under `data/ datasets/ weights/ checkpoints/ private/ secrets/ runs/ wandb/ mlruns/`
- **Media outside `docs/ assets/ examples/`**, to catch raw training clips
- **Credentials:** `.env*` (except `.env.example`), keys (`.pem .key .p12 .pfx`), SSH keys, `credentials.json`, `*.tfvars`, `.tfstate`, `.npmrc`, `.pypirc`
- **Secrets in content:** AWS, GitHub, Anthropic, OpenAI, Hugging Face, Slack, Google, Stripe and Discord tokens, private keys, and hardcoded `password=`/`api_key=` values
- **Files over 5 MB**
- **Source files missing the SPDX header.** `--fix-headers` adds it.

To make a reviewed exception, add a glob to `.commitguard-allow`.

## Usage

```bash
# New or existing repo
python apply_template.py --target D:\Work\mcp-opcua --project mcp-opcua \
    --owner "USTechService Corporation" --contact "licensing@ustechservice.com"

# In the target repo
python scripts/commitguard.py --fix-headers   # add headers to staged files
python scripts/commitguard.py --all           # audit the whole repo
pip install pre-commit && pre-commit install  # optional: adds gitleaks
```

Add this to each project README:

```markdown
## License
Dual-licensed under [AGPL-3.0](LICENSE) or a [commercial license](COMMERCIAL.md).
Contributions require agreeing to the [CLA](CLA.md).
```

## Notes

- Use `AGPL-3.0-only` rather than `-or-later`, so a future GPL version can't change your terms.
- Have an IP attorney review `COMMERCIAL.md` and `CLA.md` before the first paid deal. The CLA is modeled on Apache's ICLA, with explicit proprietary relicensing.
- Run `gitleaks detect` on the full history before flipping an existing private repo to public. commitguard only checks new commits.
