#!/usr/bin/env bash
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../fixtures/scaffold.sh" vue-basico pendientes-sum
