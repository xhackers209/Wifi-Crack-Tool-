#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  SELF TEST                    ║
║                    selftest.py  |  v6.2 ULTIMATE             ║
║                                                              ║
║   Builds a REAL synthetic WPA2 capture and cracks it.        ║
║   Proves the engine works on THIS device.                    ║
║   Run:  python3 main.py --selftest                           ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import hmac
import struct
import random
import hashlib

from banner import R, B, GRN, RED, YEL, CYN, D
from handshake import (extract_from_capture, resolve_ssid,
                       pmk_from_password)
from engine import run_real_crack

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) or "."


def run_selftest():
    print(f"\n  {B}{CYN}AWAIS X HACKER TEAM — ENGINE SELF TEST{R}\n")

    SSID = "SelfTestNet"
    PW = "selftest2024"
    AA = bytes.fromhex("112233445566")
    SA = bytes.fromhex("665544332211")
    AN = bytes(random.randrange(256) for _ in range(32))
    SN = bytes(random.randrange(256) for _ in range(32))

    # derive real keys (same math as the attack)
    pmk = pmk_from_password(PW, SSID)
    am, sm = min(AA, SA), max(AA, SA)
    an, sn = min(AN, SN), max(AN, SN)

    def prf(k, lb, d, n=64):
        out, i = b"", 0
        while len(out) < n:
            out += hmac.new(k, lb + b"\x00" + d + bytes([i]),
                            hashlib.sha1).digest()
            i += 1
        return out[:n]

    ptk = prf(pmk, b"Pairwise key expansion", am + sm + an + sn, 64)

    def eapol(ki, replay, nonce, mic=b"\x00" * 16):
        body = struct.pack(">B", 2) + struct.pack(">H", ki) + struct.pack(">H", 16)
        body += struct.pack(">Q", replay) + nonce + b"\x00" * 32
        body += mic + struct.pack(">H", 0)
        return b"\x02\x03" + struct.pack(">H", len(body)) + body

    m1 = eapol(0x0082, 1, AN)
    m2z = eapol(0x0102, 1, SN)
    m2 = eapol(0x0102, 1, SN,
               hmac.new(ptk[:16], m2z, hashlib.sha1).digest()[:16])

    rt = b"\x00\x00\x08\x00\x00\x00\x00\x00"
    llc = b"\xaa\xaa\x03\x00\x00\x00\x88\x8e"

    def df(fc, a1, a2, a3, pl):
        return rt + struct.pack("<H", fc) + b"\x00\x00" + a1 + a2 + a3 \
               + b"\x10\x00" + pl

    bc = rt + b"\x80\x00" + b"\x00\x00" + b"\xff" * 6 + AA + AA + b"\x10\x00" \
         + b"\x00" * 8 + b"\x64\x00\x31\x04" \
         + b"\x00" + bytes([len(SSID)]) + SSID.encode()

    pkts = [bc, df(0x0208, SA, AA, AA, llc + m1), df(0x0108, AA, SA, AA, llc + m2)]

    os.makedirs(os.path.join(BASE_DIR, "lab"), exist_ok=True)
    cap = os.path.join(BASE_DIR, "lab", "selftest.cap")
    pcap = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 127)
    for p in pkts:
        pcap += struct.pack("<IIII", 0, 0, len(p), len(p)) + p
    open(cap, "wb").write(pcap)

    words = [f"wrong{i}" for i in range(50)] + [PW]
    random.shuffle(words)
    wl = os.path.join(BASE_DIR, "lab", "selftest.txt")
    open(wl, "w").write("\n".join(words))

    # TEST 1: capture parsing
    info = extract_from_capture(cap)
    ssid = resolve_ssid(info)
    t1 = ssid == SSID and len(info["handshakes"]) == 1
    print(f"  [{'OK' if t1 else 'FAIL'}] Capture parsing  (ssid={ssid!r}, "
          f"handshakes={len(info['handshakes'])})")

    # TEST 2: real crack
    st, elapsed = run_real_crack(info, ssid, wl, threads=8, timeout=120)
    t2 = st.found == PW
    print(f"  [{'OK' if t2 else 'FAIL'}] Real crack       "
          f"(found={st.found!r}, attempts={st.attempts})")

    # TEST 3: engine benchmark
    from engine import benchmark
    a, e, r = benchmark(seconds=1.0)
    t3 = r > 0
    print(f"  [{'OK' if t3 else 'FAIL'}] Benchmark        ({r:,.0f} PMK/s)")

    for f in (cap, wl):
        try:
            os.remove(f)
        except OSError:
            pass

    ok = t1 and t2 and t3
    print(f"\n  {B}{GRN if ok else RED}"
          f"{'✅ SELFTEST PASS — engine 100% working on this device' if ok else '❌ SELFTEST FAIL'}"
          f"{R}\n")
    return ok


if __name__ == "__main__":
    sys.exit(0 if run_selftest() else 1)
