# Discovery map — open SoT, do not re-derive

**Repo:** https://github.com/lakenbeach/holding-shared-infra  
**Clone examples:** `~/risegen/holding-shared-infra`, sibling of product repos.

| Question | Path under SoT |
|---|---|
| Where do I start? | `docs/INDEX.md` |
| Full edge reapply after reboot | `docs/runbooks/edge-reapply.md` |
| Xiaomi SSH (Dropbear) | `docs/runbooks/xiaomi-ssh-dropbear.md` |
| Xiaomi admin API / PF | `docs/runbooks/xiaomi-admin-api.md` |
| LAN DNS alias custom_hosts | `docs/runbooks/xiaomi-lan-dns-aliases.md` |
| Modem VS_ppp0 DNAT | `docs/runbooks/modem-dnat-vs-ppp0.md` |
| Cloudflare DNS / origin | `docs/runbooks/cloudflare-dns-origin.md` |
| Double-NAT diagram | `docs/topology/residential-double-nat.md` |
| Secret **key names** | `docs/secrets-map.md` |
| Hostnames / routes / PF inventory | `inventory.yaml` |
| Edge replaces cloudflared (why) | `docs/decisions/0003-dns-portforward-edge-replaces-cloudflared.md` |
| SoT + anti-volatility ADRs | `docs/decisions/0001-…`, `0002-…` |
| Build CLI | `go build -o bin/rg-dev-host ./cmd/rg-dev-host` (SoT root) |

If the answer is not in the SoT, **probe live** and then **promote** into the SoT — do not leave it only in chat.
