#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  ATTACK ENGINE                ║
║                    engine.py  |  v5.0                        ║
╚══════════════════════════════════════════════════════════════╝
"""

import time
import hmac
import queue
import hashlib
import threading


# ─── WPA2 PMK HASHER ────────────────────────────────────
class Hasher:
    ITERATIONS = 4096
    KEYLEN     = 32

    def __init__(self, ssid):
        self.ssid_bytes = ssid.encode("utf-8")

    def pmk(self, password):
        return hashlib.pbkdf2_hmac(
            "sha1",
            password.encode("utf-8"),
            self.ssid_bytes,
            self.ITERATIONS,
            dklen=self.KEYLEN,
        )


# ─── ATTACK STATE ───────────────────────────────────────
class AttackState:
    def __init__(self):
        self.lock     = threading.Lock()
        self.attempts = 0
        self.found    = None
        self.stop     = threading.Event()
        self.start    = 0.0


# ─── WORKER ─────────────────────────────────────────────
def _worker(hasher, target_mic, q, st, timeout):
    while not st.stop.is_set():
        try:
            pwd = q.get(timeout=0.25)
        except queue.Empty:
            return
        if pwd is None:
            return
        if time.time() - st.start > timeout:
            st.stop.set()
            return
        with st.lock:
            st.attempts += 1
        try:
            pmk = hasher.pmk(pwd)
            mic = hmac.new(pmk, b"AWAIS-TEST-PACKET",
                           hashlib.sha1).digest()[:16]
        except Exception:
            continue
        if hmac.compare_digest(mic, target_mic):
            with st.lock:
                if st.found is None:
                    st.found = pwd
            st.stop.set()
            return


# ─── PRODUCER ───────────────────────────────────────────
def _producer(path, q, st):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if st.stop.is_set():
                    return
                w = line.strip()
                if w:
                    try:
                        q.put(w, timeout=1.0)
                    except queue.Full:
                        continue
    except Exception:
        pass
    finally:
        for _ in range(128):
            try:
                q.put(None, timeout=0.05)
            except queue.Full:
                break


# ─── SIMULATION ─────────────────────────────────────────
def run_simulation(ssid, target_mic, wordlist_path, threads, timeout,
                   progress_cb=None):
    """
    Simulated WPA2 attack against a known MIC.
    progress_cb(attempts, elapsed, rate) is called ~6 times/sec.
    Returns (AttackState, elapsed_seconds).
    """
    threads = max(1, min(int(threads), 256))
    hasher  = Hasher(ssid)
    st      = AttackState()
    st.start = time.time()
    q       = queue.Queue(maxsize=100000)

    pt = threading.Thread(target=_producer,
                          args=(wordlist_path, q, st), daemon=True)
    pt.start()

    workers = [
        threading.Thread(target=_worker,
                         args=(hasher, target_mic, q, st, timeout),
                         daemon=True)
        for _ in range(threads)
    ]
    for w in workers:
        w.start()

    try:
        while any(w.is_alive() for w in workers):
            elapsed = time.time() - st.start
            if elapsed > timeout:
                st.stop.set()
                break
            rate = st.attempts / elapsed if elapsed > 0 else 0
            if progress_cb:
                progress_cb(st.attempts, elapsed, rate)
            time.sleep(0.15)
    except KeyboardInterrupt:
        st.stop.set()
        raise

    for w in workers:
        w.join(timeout=1.0)

    elapsed = max(time.time() - st.start, 1e-9)
    return st, elapsed


# ─── TARGET MIC ─────────────────────────────────────────
def make_target_mic(ssid, password):
    h   = Hasher(ssid)
    pmk = h.pmk(password)
    return hmac.new(pmk, b"AWAIS-TEST-PACKET", hashlib.sha1).digest()[:16]