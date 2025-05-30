#!/usr/bin/env python3
import subprocess
import logging
import os
import time
from datetime import datetime

# === CONFIGURATION ===
PKCS11_TOOL = "pkcs11-tool"

SLOTS_TO_SCAN = range(0, 5)  # You can update this based on token setup
WORDLIST = ["0000", "1234", "123456", "1111", "admin", "test"]  # Sample weak PINs
TEEC_LOG_NAME = "teec.log"

# === LOGGING SETUP ===
LOG_FILE = f"pkcs11_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_command(cmd, capture_output=True):
    try:
        logging.debug(f"Executing command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=capture_output, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout
        else:
            logging.warning(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
            return None
    except Exception as e:
        logging.error(f"Exception running command: {cmd} - {str(e)}")
        return None

def list_slots():
    output = run_command([PKCS11_TOOL, "--list-slots"])
    if output:
        logging.info("Slot listing successful:\n" + output)
    return output

def test_pin(slot, pin):
    output = run_command([PKCS11_TOOL, "--login", "--pin", pin, "--slot", str(slot), "--list-objects"])
    if output:
        logging.info(f"Successful login with PIN '{pin}' on slot {slot}")
        return True
    return False

def brute_force_pin(slot):
    logging.info(f"Starting brute-force on slot {slot}")
    for pin in WORDLIST:
        if test_pin(slot, pin):
            logging.info(f"Weak PIN found on slot {slot}: {pin}")
            break
        time.sleep(1)  # Avoid lockout

def list_objects(slot, pin):
    logging.info(f"Listing objects in slot {slot} with PIN: {pin}")
    output = run_command([PKCS11_TOOL, "--login", "--pin", pin, "--slot", str(slot), "--list-objects"])
    if output:
        logging.info("Object Listing:\n" + output)

def check_keygen(slot, pin):
    logging.info(f"Attempting RSA keypair generation in slot {slot}")
    run_command([PKCS11_TOOL, "--keypairgen", "--key-type", "rsa:2048", "--login", "--pin", pin, "--slot", str(slot)])

def extract_cert(slot, pin):
    cert_path = f"cert_{slot}.der"
    logging.info(f"Trying to extract cert from slot {slot} to {cert_path}")
    result = run_command([PKCS11_TOOL, "--read-object", "--type", "cert", "--login", "--pin", pin, "--slot", str(slot), "--output-file", cert_path])
    if result:
        logging.info(f"Certificate extracted to {cert_path}")

def search_teec_log():
    logging.info("Searching for teec.log files across accessible directories...")
    for root, dirs, files in os.walk("/", topdown=True):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        try:
            if TEEC_LOG_NAME in files:
                log_path = os.path.join(root, TEEC_LOG_NAME)
                logging.info(f"Found {TEEC_LOG_NAME} at: {log_path}")
        except PermissionError:
            continue

def audit_slot(slot):
    logging.info(f"\n=== Auditing Slot {slot} ===")
    brute_force_pin(slot)
    for pin in WORDLIST:
        if test_pin(slot, pin):
            list_objects(slot, pin)
            check_keygen(slot, pin)
            extract_cert(slot, pin)
            break

def main():
    logging.info("Starting PKCS#11 Security Audit Tool")
    list_slots()
    for slot in SLOTS_TO_SCAN:
        audit_slot(slot)
    search_teec_log()
    logging.info("Audit completed. Log saved to " + LOG_FILE)

if __name__ == "__main__":
    main()
