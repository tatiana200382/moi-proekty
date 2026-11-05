#!/bin/sh
# Добавляет папку agent-marketolog в рабочие области DeepSeek Harness.
# Запускать в терминале: ./dobavit-v-rabotu.sh
# После добавления перезапустить приложение (Cmd+Q и открыть снова).
set -e
DIR=$(cd "$(dirname "$0")" && pwd)
python3 - "$DIR" <<'PY'
import json, os, sys, uuid, datetime

target = os.path.normpath(sys.argv[1])
reg = os.path.expanduser('~/.dsh/storages/workspace.json')
if not os.path.exists(reg):
    sys.exit('Реестр не найден: %s' % reg)

with open(reg, encoding='utf-8') as f:
    doc = json.load(f)

for wid, w in doc['tables']['workspaces'].items():
    if os.path.normpath(w['path']) == os.path.normpath(target):
        print('Уже есть: %s' % wid)
        sys.exit(0)

now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
wid = str(uuid.uuid4())
doc['tables']['workspaces'][wid] = {
    'path': target,
    'title': 'agent-marketolog',
    'sessionIds': [],
    'createdAt': now,
    'updatedAt': now,
}
doc['global']['workspaceIds'].append(wid)

tmp = reg + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write('\n')
os.replace(tmp, reg)
print('Добавлено: %s' % wid)
print('Теперь перезапустите DeepSeek Harness — папка появится в списке рабочих областей.')
PY
