
# 🔐 PKCS#11 (in OPTEE) Security Audit Tool

This Python-based script is designed for offensive auditing of PKCS#11-compatible cryptographic tokens or HSMs. It automates key security checks like weak PIN brute-force attempts, object enumeration, certificate extraction, and checks for sensitive file artifacts like `teec.log`.

---

## 🚀 Features

- Brute-force testing for weak/common PINs
- Object enumeration (certificates, keys, etc.)
- RSA keypair generation attempts
- Certificate extraction from token
- System-wide scan for `teec.log` files
- Detailed logging for all actions

---

## 🛠️ Requirements

- Python 3.x
- `pkcs11-tool` installed and accessible in your system's PATH

Install `pkcs11-tool` via:

```bash
sudo apt install opensc
