#!/usr/bin/env python3
# ScreenSense — UIAutomator Live Watcher
# Tool: ScreenSense (previously uiauto-watcher)
# Author / Channel: HasnainDarkNet
# Description: Watch visible UI text on a connected Android device using ADB + uiautomator dump,
#              print newly appeared lines. For educational / debugging use only.
# Usage: python3 live_uiauto_watch.py
#
# IMPORTANT: Use only on devices you own or have explicit permission to test.

import time, subprocess, os, xml.etree.ElementTree as ET

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout.decode(errors='ignore'), p.stderr.decode(errors='ignore')

def dump_ui(device, local='window_dump.xml'):
    rc, out, err = run(["adb","-s",device,"shell","uiautomator","dump","/sdcard/window_dump.xml"])
    # pull
    rc2, out2, err2 = run(["adb","-s",device,"pull","/sdcard/window_dump.xml", local])
    if rc2!=0:
        raise RuntimeError("Failed to pull dump: " + (err2 or err))
    return local

def parse_texts(xmlfile):
    texts=[]
    try:
        tree=ET.parse(xmlfile)
        for node in tree.iter():
            t = node.attrib.get('text') or node.attrib.get('content-desc') or node.attrib.get('hint')
            if t and t.strip():
                texts.append(t.strip())
    except Exception as e:
        # ignore parse errors silently (keeps watcher stable)
        pass
    return texts

def choose_device():
    rc,out,err = run(["adb","devices"])
    lines = out.splitlines()[1:]
    devs=[l.split()[0] for l in lines if l.strip() and 'device' in l]
    if not devs:
        raise RuntimeError("No adb devices")
    return devs[0]

if __name__ == "__main__":
    device = choose_device()
    seen=set()
    print("[*] ScreenSense (HasnainDarkNet👑) — Watching device:", device)
    try:
        while True:
            xml = dump_ui(device,"/tmp/window_dump.xml")
            texts = parse_texts(xml)
            new = [t for t in texts if t not in seen]
            for t in new:
                print("[NEW]", t)
                seen.add(t)
            # keep seen size sane
            if len(seen)>2000:
                seen = set(list(seen)[-1000:])
            time.sleep(0.6)
    except KeyboardInterrupt:
        print("\nStopped.")
