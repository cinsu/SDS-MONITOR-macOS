# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 J. Lynch. See LICENSE in the program folder.
"""Rdio Scanner (v1.1.63): recorded calls sent to /api/call-upload, kept when the server can't be reached."""
import email.parser
import email.policy
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from support import mon, monitor

TRUNK = ["2026-11-03 00:11:13", "2026-11-03 00:11:17", "4.3", "Palmetto 800", "Greer PD",
         "Greer PD Dispatch", "853.862500MHz", "TGID:44381", "Greenville County Simulcast",
         "UID:3235401, UID:3235438", "P25", "-55", "4.0", "001113_Greer PD Dispatch.mp3"]
CONV = ["2026-11-03 01:00:00", "2026-11-03 01:00:05", "5.0", "Greenville", "Greenville County - EMS",
        "EMS Backup", "155.340000MHz", "", "", "", "FM", "-60", "5.0", "010000_EMS Backup.mp3"]


def parse_form(body, ctype):
    msg = email.parser.BytesParser(policy=email.policy.HTTP).parsebytes(
        b"Content-Type: " + ctype.encode() + b"\r\n\r\n" + body)
    fields, files = {}, {}
    for part in msg.iter_parts():
        name = part.get_param("name", header="content-disposition")
        if part.get_filename():
            files[name] = (part.get_filename(), part.get_content_type(), part.get_payload(decode=True))
        else:
            fields[name] = part.get_payload(decode=True).decode()
    return fields, files


class RdioTests(unittest.TestCase):
    def setUp(self):
        self.w = monitor(fresh=True)
        s = self.w.settings
        s.setValue("rdio/enabled", "true")
        s.setValue("rdio/url", "127.0.0.1:3000")
        s.setValue("rdio/key", "secret-key")
        s.setValue("rdio/systems", "{}")
        mon.RDIO_QUEUE_FILE.unlink(missing_ok=True)
        self.posts = []
        self.reply = (200, "Call imported successfully.")
        self.r = mon.RdioUploader(self.w, post=self.fake_post)
        self.r.kick = lambda: None                     # tests send synchronously
        folder = mon.DATA_DIR / "audio" / "2026-11-03"
        folder.mkdir(parents=True, exist_ok=True)
        self.mp3 = folder / TRUNK[13]
        self.mp3.write_bytes(b"ID3fake-mp3-data")
        self.conv_mp3 = folder / CONV[13]
        self.conv_mp3.write_bytes(b"ID3other")

    def fake_post(self, url, body, ctype):
        self.posts.append((url, *parse_form(body, ctype)))
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply

    def test_fields_for_a_talkgroup_call(self):
        f = mon.rdio_fields(TRUNK, "k", 1)
        self.assertEqual(f["talkgroup"], "44381")
        self.assertEqual(f["talkgroupLabel"], "Greer PD Dispatch")
        self.assertEqual(f["talkgroupGroup"], "Greer PD")
        self.assertEqual(f["systemLabel"], "Palmetto 800")
        self.assertEqual(f["frequency"], "853862500")
        self.assertEqual(f["unit"], "3235401")
        self.assertEqual(json.loads(f["units"]), [{"id": 3235401, "offset": 0}, {"id": 3235438, "offset": 0}])
        self.assertTrue(f["dateTime"].startswith("2026-11-03T00:11:13"))
        self.assertRegex(f["dateTime"], r"[+-]\d\d:\d\d$")          # RFC 3339 with the time zone

    def test_conventional_channel_uses_its_frequency(self):
        self.assertEqual(mon.rdio_talkgroup(CONV), 155340)
        self.assertNotIn("unit", mon.rdio_fields(CONV, "k", 2))

    def test_upload_url(self):
        self.assertEqual(mon.rdio_upload_url("127.0.0.1:3000/"), "http://127.0.0.1:3000/api/call-upload")
        self.assertEqual(mon.rdio_upload_url("https://pc.tail1234.ts.net"),
                         "https://pc.tail1234.ts.net/api/call-upload")

    def test_a_call_is_sent_with_its_audio(self):
        self.r.call_saved(self.mp3, TRUNK)
        self.r.send_pending()
        url, fields, files = self.posts[0]
        self.assertEqual(url, "http://127.0.0.1:3000/api/call-upload")
        self.assertEqual(fields["key"], "secret-key")
        self.assertEqual(fields["system"], "1")
        self.assertEqual(files["audio"], (TRUNK[13], "audio/mpeg", b"ID3fake-mp3-data"))
        self.assertEqual(self.r.queue, [])
        self.assertEqual(self.r.sent_today, 1)
        self.assertFalse(mon.RDIO_QUEUE_FILE.exists())

    def test_systems_get_lasting_numbers(self):
        self.assertEqual(self.r.system_id("Palmetto 800"), 1)
        self.assertEqual(self.r.system_id("Greenville"), 2)
        self.assertEqual(self.r.system_id("Palmetto 800"), 1)
        self.assertEqual(mon.RdioUploader(self.w, post=self.fake_post).system_id("Greenville"), 2)

    def test_unreachable_server_keeps_calls_for_later_and_after_a_restart(self):
        self.reply = OSError("Connection refused")
        self.r.call_saved(self.mp3, TRUNK)
        self.r.call_saved(self.conv_mp3, CONV)
        self.r.send_pending()
        self.assertEqual(len(self.r.queue), 2)
        self.assertEqual(len(self.posts), 1)              # stops at the first failure
        again = mon.RdioUploader(self.w, post=self.fake_post)
        self.assertEqual(len(again.queue), 2)
        self.reply = (200, "Call imported successfully.")
        again.send_pending()
        self.assertEqual(again.queue, [])
        self.assertEqual([p[1]["talkgroup"] for p in self.posts[1:]], ["44381", "155340"])

    def test_a_refused_key_pauses_until_settings_change(self):
        self.reply = (401, "Invalid API key")
        self.r.call_saved(self.mp3, TRUNK)
        self.r.send_pending()
        self.assertTrue(self.r.paused)
        self.assertEqual(len(self.r.queue), 1)
        self.r.settings_changed()
        self.assertFalse(self.r.paused)

    def test_duplicates_and_missing_files_leave_the_queue(self):
        self.reply = (417, "duplicate call rejected")
        self.r.call_saved(self.mp3, TRUNK)
        self.r.call_saved(self.mp3.with_name("gone.mp3"), TRUNK)
        self.r.send_pending()
        self.assertEqual(self.r.queue, [])
        self.assertEqual(len(self.posts), 1)

    def test_nothing_is_queued_when_switched_off(self):
        self.w.settings.setValue("rdio/enabled", "false")
        self.r.call_saved(self.mp3, TRUNK)
        self.assertEqual(self.r.queue, [])

    def test_a_real_http_upload(self):
        received = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                received.append((self.path, parse_form(body, self.headers["Content-Type"])))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Call imported successfully.")

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            self.w.settings.setValue("rdio/url", f"http://127.0.0.1:{server.server_port}")
            r = mon.RdioUploader(self.w)                  # the real rdio_post
            r.kick = lambda: None
            r.call_saved(self.mp3, TRUNK)
            r.send_pending()
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(received[0][0], "/api/call-upload")
        fields, files = received[0][1]
        self.assertEqual(fields["talkgroup"], "44381")
        self.assertEqual(files["audio"][2], b"ID3fake-mp3-data")
        self.assertEqual(r.queue, [])

    def test_monitor_sends_each_saved_recording(self):
        self.assertTrue(hasattr(self.w, "rdio"))
        import inspect
        self.assertIn("self.rdio.call_saved(path, row)", inspect.getsource(mon.Monitor.audio_saved))


if __name__ == "__main__":
    unittest.main()
