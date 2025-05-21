
import asyncio
import configparser



config = configparser.ConfigParser()
config.read('config.ini')


from ndt7_download import download_test
from ndt7_upload import upload_test
from utils import getserverdetails,displaysc





if __name__ == "__main__":
    server, downloaduri, uploaduri = getserverdetails(config)    

    
 
    print("\nStarting NDT7 tests ...\n")
    displaysc(server)
    
    asyncio.run(download_test(downloaduri))
    asyncio.run(upload_test(uploaduri))
    print("\nFinshed NDT7 tests\n") 


