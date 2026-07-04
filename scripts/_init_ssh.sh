#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSH_DIR="$ROOT/.ssh"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

generate_ansible_key() {
    local key_dir="$SSH_DIR/ansible"
    local key_file="$key_dir/id_ed25519"

    if [[ -f "$key_file" ]]; then
        log_info "Ansible key already exists: $key_file"
        return 0
    fi

    log_info "Generating Ansible key..."
    mkdir -p "$key_dir"
    ssh-keygen \
        -t ed25519 \
        -N "" \
        -f "$key_file" \
        -C "ansible@$(hostname)"
    log_info "Ansible key generated successfully."
}

generate_host_keys() {
    local hosts=("host01" "host02" "host03")
    for host in "${hosts[@]}"; do
        local host_dir="$SSH_DIR/$host"
        local key_file="$host_dir/ssh_host_ed25519_key"

        if [[ -f "$key_file" ]]; then
            log_info "Host key for $host already exists: $key_file"
            continue
        fi

        log_info "Generating host key for $host..."
        mkdir -p "$host_dir"
        ssh-keygen \
            -t ed25519 \
            -N "" \
            -f "$key_file" \
            -C "$host@$(hostname)"
        log_info "Host key for $host generated successfully."
    done
}

main() {
    mkdir -p "$SSH_DIR"
    generate_ansible_key
    generate_host_keys
    log_info "All SSH keys are ready."
}

main
