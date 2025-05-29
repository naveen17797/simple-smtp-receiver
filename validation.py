import ipaddress
import pydig

def get_spf_records(domain):
    """Recursively resolves SPF includes and returns a list of IP ranges."""
    records = pydig.query(domain, 'TXT')

    spf_ips = []

    for record in records:
        record = record.replace('"', '')
        if record.startswith('v=spf1'):
            parts = record.split()
            for part in parts:
                if part.startswith('ip4:'):
                    ip = part.split(':')[1]
                    spf_ips.append(ip)
                elif part.startswith('include:'):
                    included_domain = part.split(':')[1]
                    spf_ips += get_spf_records(included_domain)
                elif part.startswith('redirect='):
                    redirected_domain = part.split('=')[1]
                    spf_ips += get_spf_records(redirected_domain)

    return spf_ips

def is_ip_authorized(domain, ip):
    """Validates if the sender IP is authorized via SPF to send emails for the domain."""
    try:
        sender_ip = ipaddress.ip_address(ip)
        spf_ranges = get_spf_records(domain)
        print(sender_ip, spf_ranges)
        for spf_range in spf_ranges:
            if sender_ip in ipaddress.ip_network(spf_range):
                return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False