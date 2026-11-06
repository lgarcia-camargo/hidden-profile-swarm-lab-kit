# Wire Beater monitor (BLS Nov 6 2026)

Polls `https://www.bls.gov/news.release/claims.nr0.htm` every 2s from Leon's Mac. On content change, parses SA initial claims, appends `docs/data/beat-log.jsonl`, and optionally posts Nostr (`NOSTR_MODE=wire-beat` via repo secret pattern).

## Dry-run (fixture)

```bash
cd "$(git rev-parse --show-toplevel)"
python3 scripts/watch_bls_release.py --dry-run --once
```

## Live loop (foreground)

```bash
export NOSTR_NSEC=...   # same as GitHub Actions nostr-feed workflow
python3 scripts/watch_bls_release.py --interval 2 --post-nostr
```

## launchd (persistent Mac worker)

```bash
REPO="$(cd "$(dirname "$0")/.." && pwd)"
sed "s|REPLACE_REPO|$REPO|g" scripts/com.lgarcia.wire-beater.plist > ~/Library/LaunchAgents/com.lgarcia.wire-beater.plist
launchctl unload ~/Library/LaunchAgents/com.lgarcia.wire-beater.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.lgarcia.wire-beater.plist
launchctl list | grep wire-beater
tail -f ~/Library/Logs/wire-beater.log
```

Unload after the release:

```bash
launchctl unload ~/Library/LaunchAgents/com.lgarcia.wire-beater.plist
```

## Pages

https://lgarcia-camargo.github.io/hidden-profile-swarm-lab-kit/wire-beater.html
