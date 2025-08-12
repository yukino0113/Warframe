(function () {
    // Token format: b2:idmask: Base64URL of repeated entries [varint(id), 1-byte mask]
    const TOKEN_PREFIX = "b2:idmask:";

    // State
    let sets = []; // [{id, name, type, component_type, vaulted}]
    let idToSet = new Map();
    let selection = new Map(); // id -> mask (number 0..255)
    let showVaulted = (localStorage.getItem('wf.showVaulted') === 'true');

    // Elements
    const container = document.getElementById('setsContainer');
    const bitmapOutEl = document.getElementById('bitmapOut');
    const copyBtn = document.getElementById('copyBtn');
    const clearBtn = document.getElementById('clearBtn');
    const toggleVaultedEl = document.getElementById('toggleVaulted');
    const saveBtn = document.getElementById('saveBtn');

    // Init toggle state
    toggleVaultedEl.checked = showVaulted;
    toggleVaultedEl.addEventListener('change', () => {
        showVaulted = toggleVaultedEl.checked;
        localStorage.setItem('wf.showVaulted', String(showVaulted));
        if (!showVaulted) {
            // Clear selections for vaulted sets when hiding
            for (const s of sets) {
                if (s.vaulted) selection.delete(s.id);
            }
        }
        renderAll();
    });

    copyBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(location.href);
            copyBtn.textContent = 'Copied';
            setTimeout(() => copyBtn.textContent = 'Copy', 1500);
        } catch (e) {
        }
    });
    clearBtn.addEventListener('click', () => {
        selection.clear();
        renderAll();
    });
    saveBtn.addEventListener('click', async () => {
        persistUrl();
        try {
            await navigator.clipboard.writeText(location.href);
            saveBtn.textContent = 'Saved';
            setTimeout(() => saveBtn.textContent = 'Save link', 1500);
        } catch (e) {
        }
    });

    // ---- Encoding helpers ----
    function base64UrlEncode(bytes) {
        let s = '';
        for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
        let b = btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
        return b;
    }

    function base64UrlDecode(s) {
        s = s.replace(/-/g, '+').replace(/_/g, '/');
        const pad = s.length % 4;
        if (pad) s += '='.repeat(4 - pad);
        const bin = atob(s);
        const out = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
        return out;
    }

    function writeVarint(num, arr) {
        // unsigned LEB128
        let n = num >>> 0;
        while (n >= 0x80) {
            arr.push((n & 0x7f) | 0x80);
            n >>>= 7;
        }
        arr.push(n);
    }

    function readVarint(bytes, idx) {
        let shift = 0, result = 0, b = 0, i = idx;
        do {
            if (i >= bytes.length) return {value: null, next: i};
            b = bytes[i++];
            result |= (b & 0x7f) << shift;
            shift += 7;
        } while (b & 0x80);
        return {value: result >>> 0, next: i};
    }

    function encodeSelection() {
        const entries = Array.from(selection.entries()).filter(([id, mask]) => mask > 0);
        const bytes = [];
        for (const [id, mask] of entries) {
            // Drop vaulted when hidden
            const s = idToSet.get(id);
            if (!s) continue;
            if (!showVaulted && s.vaulted) continue;
            // Clamp mask to number of parts
            const parts = s.component_type || [];
            const bitCount = Math.min(8, parts.length);
            const clipped = mask & ((1 << bitCount) - 1);
            if (clipped === 0) continue;
            writeVarint(id, bytes);
            bytes.push(clipped & 0xFF);
        }
        const token = TOKEN_PREFIX + base64UrlEncode(Uint8Array.from(bytes));
        bitmapOutEl.value = token;
        return token;
    }

    function decodeToken(token) {
        selection.clear();
        if (!token || !token.startsWith(TOKEN_PREFIX)) return;
        const payload = token.slice(TOKEN_PREFIX.length);
        const bytes = base64UrlDecode(payload);
        let i = 0;
        while (i < bytes.length) {
            const {value: id, next} = readVarint(bytes, i);
            if (id == null) break;
            i = next;
            if (i >= bytes.length) break;
            const mask = bytes[i++];
            // Store; later rendering will clip mask to parts length
            selection.set(id, mask);
        }
    }

    function persistUrl() {
        const token = encodeSelection();
        const path = '/' + token;
        history.replaceState(null, '', path);
    }

    function restoreFromPath() {
        const seg = location.pathname.split('/').filter(Boolean)[0] || '';
        if (!seg) return; // homepage => empty selection
        decodeToken(seg);
    }

    // ---- Rendering ----
    function renderAll() {
        // Build DOM
        container.innerHTML = '';
        const visibleSets = sets.filter(s => showVaulted || !s.vaulted);
        // Sort by name
        visibleSets.sort((a, b) => a.name.localeCompare(b.name));

        for (const s of visibleSets) {
            const card = document.createElement('div');
            card.className = 'card';
            const h3 = document.createElement('h3');
            h3.textContent = s.name + (s.vaulted ? ' (Vaulted)' : '');
            card.appendChild(h3);
            const parts = s.component_type || [];

            // All toggle
            const allRow = document.createElement('div');
            allRow.className = 'part';
            const allCb = document.createElement('input');
            allCb.type = 'checkbox';
            const currentMask = selection.get(s.id) || 0;
            const allMask = parts.length >= 8 ? 0xFF : ((1 << parts.length) - 1);
            allCb.checked = (currentMask & allMask) === allMask && allMask !== 0;
            const allLabel = document.createElement('label');
            allLabel.textContent = 'All';
            allCb.addEventListener('change', () => {
                if (allCb.checked) {
                    selection.set(s.id, allMask);
                } else {
                    selection.set(s.id, 0);
                }
                renderAll(); // re-render for consistency of child checkboxes and token
            });
            allRow.appendChild(allCb);
            allRow.appendChild(allLabel);

            const partsDiv = document.createElement('div');
            partsDiv.className = 'parts';
            partsDiv.appendChild(allRow);

            parts.forEach((p, idx) => {
                const row = document.createElement('div');
                row.className = 'part';
                const cb = document.createElement('input');
                cb.type = 'checkbox';
                const mask = selection.get(s.id) || 0;
                const bit = 1 << idx;
                cb.checked = !!(mask & bit);
                cb.addEventListener('change', () => {
                    let m = selection.get(s.id) || 0;
                    if (cb.checked) m = (m | bit); else m = (m & (~bit));
                    selection.set(s.id, m);
                    persistUrl(); // update URL token
                });
                const label = document.createElement('label');
                label.textContent = p;
                // optional sources link
                const a = document.createElement('a');
                a.href = `/v1/items/source/${encodeURIComponent(s.name + ' ' + p)}`;
                a.target = '_blank';
                a.textContent = 'sources';
                row.appendChild(cb);
                row.appendChild(label);
                row.appendChild(a);
                partsDiv.appendChild(row);
            });

            card.appendChild(partsDiv);
            container.appendChild(card);
        }

        // Update token field and URL
        persistUrl();
    }

    async function loadSets() {
        const res = await fetch('/v1/prime/status');
        if (!res.ok) throw new Error('Failed to load /v1/prime/status');
        sets = await res.json();
        idToSet.clear();
        for (const s of sets) idToSet.set(s.id, s);
        // Decode from path after we know sets
        restoreFromPath();
        // If showVaulted is off, drop vaulted selections immediately per spec
        if (!showVaulted) {
            for (const s of sets) {
                if (s.vaulted) selection.delete(s.id);
            }
        }
        renderAll();
    }

    // Init
    loadSets().catch(e => {
        container.innerHTML = `<div class="card">Failed to initialize: ${e.message}</div>`;
    });
})();
