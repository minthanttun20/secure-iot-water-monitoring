import argparse
import json
import random
import ssl
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import paho.mqtt.client as mqtt

from paho.mqtt.client import CallbackAPIVersion

DEFAULT_HOST = "localhost"
PORT_INSECURE = 1883
PORT_TLS = 8883

TOPIC = "grandmarina/sensors/test/telemetry"


def banner(title, tls, extra=""):
    print("=" * 50)
    print(f"  {title}")
    print(f"  TLS: {'ON' if tls else 'OFF'}")
    if extra:
        print(f"  {extra}")
    print("=" * 50)
    print()


class Runner:
    def __init__(self, tls_enabled: bool, host: str, ca_path: str | None):
        self.tls_enabled = tls_enabled
        self.host = host
        self.port = PORT_TLS if tls_enabled else PORT_INSECURE
        self.ca_path = ca_path

        self.client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
        self.client.on_message = self._on_message
        self._messages = []
        self._connected = False

        if self.tls_enabled:
            if self.ca_path:
                self.client.tls_set(
                    ca_certs=self.ca_path,
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLS,
                )
            else:
                # Danger mode (no verification) for the "no-ca" scenario
                self.client.tls_set(
                    cert_reqs=ssl.CERT_NONE,
                    tls_version=ssl.PROTOCOL_TLS,
                )
                self.client.tls_insecure_set(True)

        self.client.on_connect = self._on_connect

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        self._connected = (reason_code == 0)

    def _on_message(self, client, userdata, msg):
        self._messages.append((time.time(), msg.payload))

    def connect(self):
        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop_start()
        time.sleep(0.5)

    def disconnect(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass

    def publish_messages(self, count: int):
        for i in range(count):
            payload = {
                "device_id": "test-sensor-001",
                "pressure_psi": round(80 + random.uniform(-3, 3), 1),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "counter": i + 1,
            }
            self.client.publish(TOPIC, json.dumps(payload))
            time.sleep(0.2)

    def latency_test(self, count: int):
        # subscribe to same topic to measure time-to-receive
        self.client.subscribe(TOPIC)
        time.sleep(0.2)

        latencies_ms = []

        for i in range(count):
            sent = time.time()
            payload = {"counter": i + 1, "sent": sent}
            self.client.publish(TOPIC, json.dumps(payload))

            # wait for message echo back
            start_wait = time.time()
            while time.time() - start_wait < 2:
                if self._messages:
                    recv_time, raw = self._messages.pop(0)
                    try:
                        data = json.loads(raw.decode())
                        if data.get("counter") == i + 1:
                            latencies_ms.append((recv_time - sent) * 1000)
                            break
                    except Exception:
                        pass
                time.sleep(0.005)

            if (i + 1) % 10 == 0:
                print(f"  Sent {i+1}/{count} messages...")

        return latencies_ms

    def stress_test(self, rate: int, duration: int):
        # rate messages/sec for duration sec
        total = rate * duration
        delay = 1.0 / rate if rate > 0 else 0
        errors = 0

        start = time.time()
        for i in range(total):
            payload = {"counter": i + 1, "ts": datetime.now(timezone.utc).isoformat()}
            info = self.client.publish(TOPIC, json.dumps(payload))
            if info.rc != 0:
                errors += 1
            time.sleep(delay)

        elapsed = time.time() - start
        actual_rate = total / elapsed if elapsed > 0 else 0
        success_rate = 100.0 * (1 - errors / total) if total > 0 else 0
        return total, errors, actual_rate, success_rate


def generate_wrong_ca(path="certs/wrong-ca.pem"):
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Wrong CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Wrong Root CA"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )

    Path("certs").mkdir(exist_ok=True)
    Path(path).write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    print(f"Saved wrong CA cert to: {path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True,
                   choices=["publish", "connect", "latency", "stress",
                            "generate-wrong-ca", "test-wrong-ca"])
    p.add_argument("--tls", choices=["on", "off"], default="off")
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--rate", type=int, default=25)
    p.add_argument("--duration", type=int, default=30)
    p.add_argument("--no-ca", action="store_true")
    p.add_argument("--host", default=DEFAULT_HOST)
    args = p.parse_args()

    tls_enabled = (args.tls == "on")
    ca_path = None if args.no_ca else "certs/ca.pem"

    if args.mode == "generate-wrong-ca":
        banner("Generate Wrong CA", tls=False)
        generate_wrong_ca()
        return

    if args.mode == "test-wrong-ca":
        banner("Connection Test (Wrong CA)", tls=True, extra="CA Certificate: certs/wrong-ca.pem")
        runner = Runner(True, args.host, "certs/wrong-ca.pem")
        try:
            runner.connect()
            print("SUCCESS: Connected to broker! (This would be BAD in real life!)")
        except Exception as e:
            print(f"FAILED: {e}")
        finally:
            runner.disconnect()
        return

    if args.mode == "connect":
        banner("Connection Test", tls=tls_enabled, extra=f"CA Certificate: {'NONE' if args.no_ca else 'certs/ca.pem'}")
        runner = Runner(tls_enabled, args.host, ca_path)
        try:
            runner.connect()
            if runner._connected:
                print("SUCCESS: Connected to broker!")
            else:
                print("FAILED: Could not connect (check broker).")
        except Exception as e:
            print(f"FAILED: {e}")
        finally:
            runner.disconnect()
        return

    if args.mode == "publish":
        banner("Publish Test Messages", tls=tls_enabled, extra=f"Messages: {args.count}")
        runner = Runner(tls_enabled, args.host, ca_path)
        try:
            runner.connect()
            runner.publish_messages(args.count)
            print("Done.")
        except Exception as e:
            print(f"FAILED: {e}")
        finally:
            runner.disconnect()
        return

    if args.mode == "latency":
        banner("Latency Test", tls=tls_enabled, extra=f"Messages: {args.count}")
        runner = Runner(tls_enabled, args.host, ca_path)
        try:
            runner.connect()
            lat = runner.latency_test(args.count)
            if not lat:
                print("No latency samples collected (check topic/broker).")
                return
            avg = sum(lat) / len(lat)
            mn = min(lat)
            mx = max(lat)
            # std dev
            var = sum((x - avg) ** 2 for x in lat) / len(lat)
            std = var ** 0.5
            print("\n" + "=" * 50)
            print(f"  Latency Results (TLS {'ON' if tls_enabled else 'OFF'})")
            print("=" * 50)
            print(f"  Messages sent: {len(lat)}")
            print(f"  Average latency: {avg:.2f} ms")
            print(f"  Min latency: {mn:.2f} ms")
            print(f"  Max latency: {mx:.2f} ms")
            print(f"  Std deviation: {std:.2f} ms")
            print("=" * 50)
        except Exception as e:
            print(f"FAILED: {e}")
        finally:
            runner.disconnect()
        return

    if args.mode == "stress":
        banner("Stress Test", tls=tls_enabled, extra=f"Rate: {args.rate} msg/sec | Duration: {args.duration}s")
        runner = Runner(tls_enabled, args.host, ca_path)
        try:
            runner.connect()
            total, errors, actual, success = runner.stress_test(args.rate, args.duration)
            print("\n" + "=" * 50)
            print(f"  Stress Test Results (TLS {'ON' if tls_enabled else 'OFF'})")
            print("=" * 50)
            print(f"  Target rate: {args.rate} msg/sec")
            print(f"  Actual rate: {actual:.2f} msg/sec")
            print(f"  Messages sent: {total}")
            print(f"  Errors: {errors}")
            print(f"  Success rate: {success:.1f}%")
            status = "SUCCESS" if actual >= 0.95 * args.rate else "DEGRADED"
            print(f"  Status: {status}")
            print("=" * 50)
        except Exception as e:
            print(f"FAILED: {e}")
        finally:
            runner.disconnect()
        return


if __name__ == "__main__":
    main()
