import time, subprocess, re

def Host_Batt_check(self)-> int:
    processR= subprocess.run(['apcaccess -p BCHARGE'],shell=True, check=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
    time.sleep(5)
    x = re.findall('\d{1,3}',processR)
    y = int(x[0])
    self.Batt_Stat=y
    


    