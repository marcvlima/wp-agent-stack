#!/usr/bin/env python3
"""Seed the Trae IDE local SQLite cache with RiseGen gateway models.

Best-effort. Trae's server sync may overwrite.
Does not kill Trae. Does not call coresg-normal.trae.ai.
"""

import json
import os
import shutil
import sqlite3
import sys
import time
import urllib.request
import urllib.error


def main():
    # 1. Read credentials
    creds_path = os.path.expanduser("~/.risegen/credentials.json")
    if not os.path.isfile(creds_path):
        print("credentials.json not found", file=sys.stderr)
        sys.exit(1)
    with open(creds_path) as f:
        creds = json.load(f)
    api_key = creds.get("gateway_api_key", "")
    gateway_url = creds.get("gateway_url", "")
    if not api_key or not gateway_url:
        print("gateway_api_key or gateway_url missing", file=sys.stderr)
        sys.exit(1)

    # 2. Fetch models
    base = gateway_url.rstrip("/")
    models_url = f"{base}/models"
    req = urllib.request.Request(
        models_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "RiseGenProviderSetup/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            if resp.status != 200:
                print(resp.status)
                sys.exit(1)
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(e.code)
        sys.exit(1)
    except Exception as e:
        print(f"fetch error: {e}", file=sys.stderr)
        sys.exit(1)

    models_data = json.loads(body)
    model_list = models_data.get("data", [])
    models_fetched = len(model_list)

    # 3. Backup database
    db_path = os.path.expanduser(
        "/home/marcus/.config/Trae/User/globalStorage/state.vscdb"
    )
    backup_path = os.path.expanduser(
        "/home/marcus/.config/Trae/User/globalStorage/state.vscdb.bak-risegen-20261024"
    )
    backup_created = "no"
    if not os.path.isfile(backup_path):
        shutil.copy2(db_path, backup_path)
        backup_created = "yes"

    # 4. Connect and seed
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("BEGIN IMMEDIATE")

    cursor = conn.execute(
        "SELECT key, value FROM ItemTable WHERE key LIKE '%AI.agent.model.model_list_map'"
    )
    rows = list(cursor.fetchall())

    keys_updated = 0
    rows_inserted = 0

    for key, value_json in rows:
        try:
            data = json.loads(value_json)
        except json.JSONDecodeError:
            continue

        modified = False
        for func_name, models in data.items():
            if not isinstance(models, list) or len(models) == 0:
                continue

            template = dict(models[0])
            existing_ids = {
                (m.get("name"), m.get("provider"))
                for m in models
                if isinstance(m, dict)
            }

            for model in model_list:
                mid = model.get("id", "")
                if not mid:
                    continue
                if (mid, "custom_openai_compatible") in existing_ids:
                    continue

                entry = dict(template)
                entry["name"] = mid
                entry["display_name"] = f"RiseGen · {mid}"
                entry["provider"] = "custom_openai_compatible"
                entry["base_url"] = "https://nex-global.risegen.ai/v1"
                entry["is_custom_base_url"] = True
                entry["ak"] = api_key
                entry["sk"] = ""
                entry["auth_type"] = 0
                entry["config_source"] = 3
                entry["is_preset"] = False
                entry["selectable"] = True
                entry["status"] = True
                entry["config_name"] = "risegen"
                entry["custom_model_id"] = mid
                entry["use_remote_service"] = False

                models.append(entry)
                rows_inserted += 1
                modified = True

        if modified:
            new_value = json.dumps(data, ensure_ascii=False)
            conn.execute(
                "UPDATE ItemTable SET value = ? WHERE key = ?",
                (new_value, key),
            )
            keys_updated += 1

    conn.commit()

    # 5. Print counts
    print(f"models_fetched={models_fetched}")
    print(f"keys_updated={keys_updated}")
    print(f"rows_inserted={rows_inserted}")
    print(f"backup_created={backup_created}")

    # 6. Count custom rows immediately after commit
    count_cursor = conn.execute(
        "SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%AI.agent.model.model_list_map'"
    )
    before_count = 0
    for row in count_cursor.fetchall():
        try:
            data = json.loads(row[0]) if len(row) > 1 else None
        except Exception:
            continue
    # Count from the in-memory data we just wrote
    before_count = rows_inserted

    conn.close()

    # 7. Sleep 20s, re-open read-only, count again
    time.sleep(20)

    conn_ro = sqlite3.connect(
        f"file:{db_path}?mode=ro", uri=True, timeout=30
    )
    after_count = 0
    ro_cursor = conn_ro.execute(
        "SELECT value FROM ItemTable WHERE key LIKE '%AI.agent.model.model_list_map'"
    )
    for (value_json,) in ro_cursor.fetchall():
        try:
            data = json.loads(value_json)
        except json.JSONDecodeError:
            continue
        for func_name, models in data.items():
            if isinstance(models, list):
                for m in models:
                    if isinstance(m, dict) and m.get("provider") == "custom_openai_compatible":
                        after_count += 1
    conn_ro.close()

    print(f"custom_rows_after_20s={after_count}")
    if after_count < before_count:
        print(
            f"trae_cache_overwritten before={before_count} after={after_count}"
        )


if __name__ == "__main__":
    main()