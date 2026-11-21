import ipaddress
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_ca_certificate():
    """Generate the Certificate Authority (CA) certificate"""

    # Step 1: Generate a private key for the CA
    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Step 2: Define the CA's identity
    ca_name = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Grand Marina Hotel"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Water Systems Security"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Grand Marina Root CA"),
    ])

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))  # 10 years
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(private_key=ca_key, algorithm=hashes.SHA256())
    )

    return ca_key, ca_cert

def generate_server_certificate(ca_key, ca_cert):
    """Generate the server certificate signed by the CA"""

    # The server gets its OWN key pair (separate from CA)
    server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
    )

        # Server's identity
    server_name = x509.Name([
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Grand Marina Hotel"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "MQTT Broker"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    server_cert = (
            x509.CertificateBuilder()
            .subject_name(server_name)
            .issuer_name(ca_cert.subject)  # CA is the issuer!
            .public_key(server_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            .sign(ca_key, hashes.SHA256())  # Signed by CA's key!
    )
    return server_key, server_cert

def save_certificates(ca_cert, server_cert, server_key, output_dir="certs"):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Save CA certificate (public)
    with open(output_path / "ca.pem", "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    # Save server certificate (public)
    with open(output_path / "server.pem", "wb") as f:
        f.write(server_cert.public_bytes(serialization.Encoding.PEM))

    # Save server private key (SECRET!)
    with open(output_path / "server-key.pem", "wb") as f:
        f.write(server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
        ))

def verify_chain(server_cert, ca_cert):
    ca_public_key = ca_cert.public_key()
    ca_public_key.verify(
        server_cert.signature,
        server_cert.tbs_certificate_bytes,
        # RSA signature uses PKCS1v15 with the hash algorithm in the cert
        padding=__import__("cryptography.hazmat.primitives.asymmetric.padding").hazmat.primitives.asymmetric.padding.PKCS1v15(),
        algorithm=server_cert.signature_hash_algorithm,
    )

def main():
    print("=======================================================")
    print("  Certificate Generation for Grand Marina Hotel")
    print("=======================================================\n")

    print("[1/3] Generating Certificate Authority (CA)...")
    print("      Generating CA private key (2048 bits)...")
    ca_key, ca_cert = generate_ca_certificate()
    print("      Creating CA certificate (valid for 10 years)...")
    print("      CA certificate created successfully!\n")

    print("[2/3] Generating Server Certificate...")
    print("      Generating server private key (2048 bits)...")
    server_key, server_cert = generate_server_certificate(ca_key, ca_cert)
    print("      Creating server certificate (valid for 1 year)...")
    print("      Server certificate created successfully!\n")

    print("[3/3] Saving certificates to certs/ folder...")
    save_certificates(ca_cert, server_cert, server_key, output_dir="certs")
    print("      Saved: certs/ca.pem")
    print("      Saved: certs/server.pem")
    print("      Saved: certs/server-key.pem\n")

    print("      Verifying certificates...")
    try:
        verify_chain(server_cert, ca_cert)
        print("      Chain verified: Server cert is signed by CA\n")
    except Exception:
        print("      Verification failed: server cert NOT signed by CA\n")
        raise

    print("=======================================================")
    print("  Certificates generated successfully!")
    print("=======================================================")


if __name__ == "__main__":
    main()