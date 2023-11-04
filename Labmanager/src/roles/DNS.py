

def init_role(cls):
    cls.update_all_DNS = update_all_DNS()

def update_all_DNS():
    # Modify /etc/hosts and reboot dnsmasq
    pass