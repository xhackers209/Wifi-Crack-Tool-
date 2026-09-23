#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║         AWAIS X HACKER TEAM  —  REAL WPA2 CAPTURE PARSER     ║
║                    handshake.py  |  v6.1 REAL EDITION        ║
║                                                              ║
║   Pure-Python WPA2 handshake + PMKID extractor/cracker.      ║
║   NO external tools required for the built-in engine.        ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import struct
import hashlib
import hmac


EAPOL_ETHERTYPE = 0x888E
LINKTYPE_IEEE802_11       = 105   # raw 802.11
LINKTYPE_IEEE802_11_RADIO = 127   # radiotap
LINKTYPE_PPI              = 192   # Per-Packet Information


# ══════════════════════════════════════════════════════════
#  PCAP / PCAPNG READING
# ══════════════════════════════════════════════════════════
def read_packets(path):
    """
    Read a .pcap or .pcapng file.
    Returns (linktype, [packet_bytes, ...]).
    Raises ValueError if the file is not a supported capture.
    """
    with open(path, "rb") as f:
        data = f.read()
    if len(data) < 4:
        raise ValueError("file too small to be a capture")

    magic = data[:4]
    if magic in (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1"):
        return _read_pcap(data, "<")
    if magic in (b"\xa1\xb2\xc3\xd4", b"\xa1\xb2\x3c\x4d"):
        return _read_pcap(data, ">")
    if magic == b"\x0a\x0d\x0d\x0a":
        return _read_pcapng(data)
    raise ValueError("not a pcap/pcapng file (bad magic bytes)")


def _read_pcap(data, en):
    if len(data) < 24:
        raise ValueError("truncated pcap global header")
    _, vmaj, vmin, _tz, _sig, _snap, linktype = struct.unpack(
        en + "IHHIIII", data[:24])
    pkts = []
    off = 24
    while off + 16 <= len(data):
        _ts, _us, incl, _orig = struct.unpack(en + "IIII", data[off:off + 16])
        off += 16
        if off + incl > len(data):
            break
        pkts.append(data[off:off + incl])
        off += incl
    return linktype, pkts


def _read_pcapng(data):
    if len(data) < 12:
        raise ValueError("truncated pcapng")
    bom = data[8:12]
    if bom == b"\x4d\x3c\x2b\x1a":
        en = "<"
    elif bom == b"\x1a\x2b\x3c\x4d":
        en = ">"
    else:
        raise ValueError("pcapng: bad byte-order magic")

    linktype = None
    pkts = []
    off = 0
    while off + 12 <= len(data):
        btype, blen = struct.unpack(en + "II", data[off:off + 8])
        if blen < 12 or off + blen > len(data):
            break
        body = data[off + 8: off + blen - 4]
        if btype == 0x00000001:                       # Interface Description
            if len(body) >= 8 and linktype is None:
                linktype = struct.unpack(en + "H", body[:2])[0]
        elif btype == 0x00000006:                     # Enhanced Packet Block
            if len(body) >= 20:
                _ifid, _tsh, _tsl, caplen, _orig = struct.unpack(
                    en + "IIIII", body[:20])
                pkts.append(body[20:20 + caplen])
        elif btype == 0x00000003:                     # Simple Packet Block
            if len(body) >= 4:
                orig = struct.unpack(en + "I", body[:4])[0]
                pkts.append(body[4:4 + min(orig, len(body) - 4)])
        off += blen
    if linktype is None:
        raise ValueError("pcapng: no interface description block")
    return linktype, pkts


# ══════════════════════════════════════════════════════════
#  802.11 FRAME PARSING
# ══════════════════════════════════════════════════════════
def strip_link_header(linktype, pkt):
    """Return the 802.11 frame payload (or None if unsupported)."""
    if linktype == LINKTYPE_IEEE802_11:
        return pkt
    if linktype == LINKTYPE_IEEE802_11_RADIO:      # radiotap
        if len(pkt) < 4:
            return None
        hlen = struct.unpack("<H", pkt[2:4])[0]
        if hlen >= len(pkt):
            return None
        return pkt[hlen:]
    if linktype == LINKTYPE_PPI:                   # PPI
        if len(pkt) < 8:
            return None
        hlen = struct.unpack("<H", pkt[4:6])[0]
        if hlen >= len(pkt):
            return None
        return pkt[hlen:]
    return None


def _mac(b):
    return ":".join(f"{x:02x}" for x in b)


def parse_80211(frame):
    """Parse an 802.11 frame header. Returns dict or None."""
    if len(frame) < 24:
        return None
    fc = struct.unpack("<H", frame[:2])[0]
    ftype    = (fc >> 2) & 0x3
    subtype  = (fc >> 4) & 0xF
    to_ds    = (fc >> 8) & 1
    from_ds  = (fc >> 9) & 1
    protected = (fc >> 14) & 1
    order    = (fc >> 15) & 1

    addr1, addr2, addr3 = frame[4:10], frame[10:16], frame[16:22]
    hdrlen = 24
    if ftype == 2:                                  # data frame
        if to_ds and from_ds:
            hdrlen = 30
        if subtype & 0x8:                           # QoS data subtypes
            hdrlen += 2
        if order:
            hdrlen += 4
        if protected:
            return None                            # encrypted payload
    payload = frame[hdrlen:]
    return {
        "type": ftype, "subtype": subtype,
        "to_ds": to_ds, "from_ds": from_ds,
        "addr1": addr1, "addr2": addr2, "addr3": addr3,
        "bssid": addr3, "payload": payload,
    }


def parse_beacon_ssid(f):
    """Extract SSID from a beacon / probe-response management frame."""
    if f["type"] != 0 or f["subtype"] not in (5, 8):
        return None
    body = f["payload"]
    if len(body) < 14:
        return None
    tags = body[12:]                                # skip fixed 12 bytes
    i = 0
    while i + 2 <= len(tags):
        tag_id, tag_len = tags[i], tags[i + 1]
        val = tags[i + 2: i + 2 + tag_len]
        if tag_id == 0 and 0 < tag_len <= 32:
            try:
                ssid = val.decode("utf-8", "ignore").strip()
            except Exception:
                return None
            if ssid and not ssid.startswith("\x00"):
                return ssid
        i += 2 + tag_len
    return None


def parse_eapol_from_data(f):
    """If this data frame carries EAPOL, return (eapol_bytes, aa_guess, sa_guess)."""
    if f["type"] != 2:
        return None
    p = f["payload"]
    if len(p) < 8:
        return None
    if p[0:3] != b"\xaa\xaa\x03":
        return None
    if struct.unpack(">H", p[6:8])[0] != EAPOL_ETHERTYPE:
        return None
    eapol = p[8:]
    if f["from_ds"] and not f["to_ds"]:
        aa, sa = f["addr2"], f["addr1"]
    elif f["to_ds"] and not f["from_ds"]:
        aa, sa = f["addr1"], f["addr2"]
    else:
        aa, sa = f["addr3"], f["addr2"]
    return eapol, aa, sa


def parse_eapol_key(eapol):
    """Parse an EAPOL-Key frame. Returns dict or None."""
    if len(eapol) < 99:
        return None
    if eapol[1] != 3:                               # EAPOL type: Key
        return None
    body_len = struct.unpack(">H", eapol[2:4])[0]
    total = min(4 + body_len, len(eapol))
    eapol = eapol[:total]

    descriptor = eapol[4]
    key_info   = struct.unpack(">H", eapol[5:7])[0]
    install = (key_info >> 6) & 1
    ack     = (key_info >> 7) & 1
    mic     = (key_info >> 8) & 1
    secure  = (key_info >> 9) & 1
    replay  = struct.unpack(">Q", eapol[9:17])[0]
    nonce   = eapol[17:49]
    mic_b   = eapol[81:97]
    kd_len  = struct.unpack(">H", eapol[97:99])[0]
    kd      = eapol[99:99 + kd_len]

    # frame with MIC zeroed — this is what the MIC actually signs
    z = bytearray(eapol[:total])
    z[81:97] = b"\x00" * 16
    return {
        "descriptor": descriptor, "key_info": key_info,
        "install": install, "ack": ack, "mic": mic, "secure": secure,
        "replay": replay, "nonce": nonce, "mic_bytes": mic_b,
        "frame": bytes(z), "key_data": kd,
    }


# ══════════════════════════════════════════════════════════
#  RSN IE / PMKID PARSING
# ══════════════════════════════════════════════════════════
def _parse_rsn_ie_for_pmkids(ie):
    """ie = RSN IE content (after id+len). Returns list of 16-byte PMKIDs."""
    pmkids = []
    try:
        off = 0
        off += 2                                   # version
        off += 4                                   # group cipher
        if off + 2 > len(ie):
            return []
        pc = struct.unpack("<H", ie[off:off + 2])[0]; off += 2 + 4 * pc
        if off + 2 > len(ie):
            return []
        ac = struct.unpack("<H", ie[off:off + 2])[0]; off += 2 + 4 * ac
        off += 2                                   # rsn capabilities
        if off + 2 > len(ie):
            return []
        n = struct.unpack("<H", ie[off:off + 2])[0]; off += 2
        for _ in range(n):
            if off + 16 <= len(ie):
                pmkids.append(ie[off:off + 16])
            off += 16
    except Exception:
        pass
    return pmkids


def scan_pmkids_in_tags(blob):
    """Defensively scan a tag blob for RSN IEs that contain PMKIDs."""
    found = []
    i = 0
    while i + 2 <= len(blob):
        if blob[i] == 48:                          # RSN IE
            ln = blob[i + 1]
            ie = blob[i + 2: i + 2 + ln]
            found.extend(_parse_rsn_ie_for_pmkids(ie))
        i += 2 + blob[i + 1]
    return found


# ══════════════════════════════════════════════════════════
#  CAPTURE ANALYSIS
# ══════════════════════════════════════════════════════════
def extract_from_capture(path):
    """
    Analyze a capture file and pull out everything crackable:
      - WPA2 4-way handshakes (EAPOL msg1 + msg2)
      - PMKIDs (from EAPOL msg1 key data or association requests)
      - SSID map from beacons
    Returns dict(ssid_map, handshakes, pmkids, packet_count).
    """
    linktype, pkts = read_packets(path)
    ssid_map  = {}
    anonces   = []
    smics     = []
    pmkids    = []

    for raw in pkts:
        frame = strip_link_header(linktype, raw)
        if not frame:
            continue
        f = parse_80211(frame)
        if not f:
            continue

        if f["type"] == 0 and f["subtype"] in (5, 8):
            ssid = parse_beacon_ssid(f)
            if ssid:
                ssid_map.setdefault(_mac(f["addr3"]), ssid)

        if f["type"] == 0 and f["subtype"] == 0:    # assoc request
            body = f["payload"]
            if len(body) >= 4:
                aa = f["addr3"] if f["addr3"] != b"\xff" * 6 else f["addr1"]
                for pmk in scan_pmkids_in_tags(body[4:]):
                    pmkids.append({"aa": aa, "spa": f["addr2"], "pmkid": pmk})

        got = parse_eapol_from_data(f)
        if not got:
            continue
        eapol, aa, sa = got
        ek = parse_eapol_key(eapol)
        if not ek:
            continue
        if ek["ack"] == 1 and ek["mic"] == 0:
            anonces.append({"aa": aa, "anonce": ek["nonce"],
                            "replay": ek["replay"]})
            for pmk in scan_pmkids_in_tags(ek["key_data"]):
                pmkids.append({"aa": aa, "spa": sa, "pmkid": pmk})
        elif ek["ack"] == 0 and ek["mic"] == 1 and ek["secure"] == 0:
            smics.append({
                "aa": aa, "sa": sa, "snonce": ek["nonce"],
                "mic": ek["mic_bytes"], "frame": ek["frame"],
                "replay": ek["replay"],
                "algo": hashlib.md5 if ek["descriptor"] == 0xFE
                        else hashlib.sha1,
            })

    # pair msg1 x msg2 (replay counters should match when both exist)
    handshakes = []
    used = set()
    for s in smics:
        partner = None
        for idx, a in enumerate(anonces):
            if idx in used:
                continue
            if a["aa"] == s["aa"] and a["replay"] == s["replay"]:
                partner = (idx, a)
                break
        if partner is None:
            for idx, a in enumerate(anonces):
                if idx not in used and a["aa"] == s["aa"]:
                    partner = (idx, a)
                    break
        if partner:
            idx, a = partner
            used.add(idx)
            handshakes.append({
                "aa": a["aa"], "sa": s["sa"],
                "anonce": a["anonce"], "snonce": s["snonce"],
                "mic": s["mic"], "frame": s["frame"], "algo": s["algo"],
            })

    return {
        "ssid_map": ssid_map,
        "handshakes": handshakes,
        "pmkids": pmkids,
        "packet_count": len(pkts),
    }


def resolve_ssid(info, aa_bytes=None, user_default=""):
    """Pick the best SSID for cracking."""
    smap = info["ssid_map"]
    if aa_bytes is not None:
        s = smap.get(_mac(aa_bytes))
        if s:
            return s
    if smap:
        return next(iter(smap.values()))
    return user_default


# ══════════════════════════════════════════════════════════
#  CRYPTO — REAL WPA2
# ══════════════════════════════════════════════════════════
def pmk_from_password(password, ssid):
    """PBKDF2-HMAC-SHA1 — the real WPA2 PMK derivation."""
    return hashlib.pbkdf2_hmac(
        "sha1", password.encode("utf-8"), ssid.encode("utf-8"),
        4096, dklen=32)


def _prf_sha1(key, label, data, length=64):
    out = b""
    i = 0
    while len(out) < length:
        out += hmac.new(key, label + b"\x00" + data + bytes([i]),
                        hashlib.sha1).digest()
        i += 1
    return out[:length]


def derive_ptk(pmk, aa, sa, anonce, snonce):
    """IEEE 802.11i PRF-512 -> PTK."""
    am, sm = min(aa, sa), max(aa, sa)
    an, sn = min(anonce, snonce), max(anonce, snonce)
    return _prf_sha1(pmk, b"Pairwise key expansion", am + sm + an + sn, 64)


def mic_from_ptk(ptk, frame, algo):
    """EAPOL-Key MIC: HMAC-MD5 (WPA/TKIP) or HMAC-SHA1[:16] (WPA2)."""
    return hmac.new(ptk[:16], frame, algo).digest()[:16]


def pmkid_from_pmk(pmk, aa, spa):
    """PMKID = HMAC-SHA1(PMK, 'PMK Name' || AA || SPA)[:16]  (hashcat -m 16800)"""
    return hmac.new(pmk, b"PMK Name" + aa + spa,
                    hashlib.sha1).digest()[:16]


def verify_password(password, ssid, info):
    """
    Test ONE password against everything crackable in the capture.
    Returns (matched_bool, detail_dict).
    """
    pmk = pmk_from_password(password, ssid)
    for p in info["pmkids"]:
        if hmac.compare_digest(pmkid_from_pmk(pmk, p["aa"], p["spa"]),
                               p["pmkid"]):
            return True, {"type": "PMKID"}
    for h in info["handshakes"]:
        ptk = derive_ptk(pmk, h["aa"], h["sa"], h["anonce"], h["snonce"])
        calc = mic_from_ptk(ptk, h["frame"], h["algo"])
        if hmac.compare_digest(calc, h["mic"]):
            return True, {"type": "4-way handshake"}
    return False, {}
