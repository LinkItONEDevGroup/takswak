#!/usr/bin/env python3

import asyncio
import xml.etree.ElementTree as ET
import os

from configparser import ConfigParser

import pytak
from os.path import exists

VERSION="0.0.3"

class MyTx(pytak.QueueWorker):
    """
    Defines how you process or generate your Cursor-On-Target Events.
    From there it adds the COT Events to a queue for TX to a COT_URL.
    """

    async def handle_data(self, data):
        """
        Handles pre-COT data and serializes to COT Events, then puts on queue.
        """
        print(data)
        event = data
        await self.put_queue(event)

    async def run(self, number_of_iterations=-1):
        """
        Runs the loop for processing or generating pre-COT data.
        """
        sent_cnt=0
        while 1:
            data = cot_from_file() #send msg.cot
            if data:
                print("sent_cnt=%i" %(sent_cnt))
                sent_cnt+=1
                await self.handle_data(data)
                await asyncio.sleep(1)
            #send directory

            search_dir = "send"
            for dirpath, dirnames, filenames in os.walk(search_dir):
                #print("dirpath=%s\ndirnames=%s\nfilenames=%s" %(dirpath, dirnames, filenames))
                filenames = [f for f in filenames if f.endswith(".cot")]
                for filename in sorted(filenames):
                    pathname = "%s/%s" %(search_dir,filename)
                    data = cot_from_file(pathname)
                    if data:
                        print("sent_cnt=%i" %(sent_cnt))
                        sent_cnt+=1
                        await self.handle_data(data)
                        os.rename(pathname, "%s/%s" %("sent",filename))
                        await asyncio.sleep(1)
            await asyncio.sleep(20)

class MyRx(pytak.QueueWorker):
    """
    Defines how you process or generate your Cursor-On-Target Events.
    From there it adds the COT Events to a queue for TX to a COT_URL.
    """


    async def run(self, number_of_iterations=-1):
        """
        Runs the loop for processing or generating pre-COT data.
        """
        rec_cnt=0
        while 1:
            if not self.queue.empty():
                data = self.queue.get_nowait()
                if data:
                    print("rec_cnt=%i" %(rec_cnt))
                    print(data)
                    rec_cnt+=1
                    pathname ="%s/%s.cot" %('rec', pytak.cot_time(60*60*8))
                    with open(pathname,"wb") as f:
                        f.write(data)
                        #lines = f.readlines()
                    #msg="".join(lines).strip()
            else:
                await asyncio.sleep(1)



def cot_example():
    """
    Generates a simple takPong COT Event.
    """
    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", "a-h-G-E-V-A-T-t")
    root.set("uid", "auto")
    root.set("how", "m-g")
    root.set("time", pytak.cot_time())
    root.set("start", pytak.cot_time())
    root.set("stale", pytak.cot_time(3600))
    point = ET.SubElement(root, 'point')
    point.set("lat","24.7995259")
    point.set("lon","120.9960658")
    point.set("ce","70.1")
    point.set("hae","9999999.0")
    point.set("le","9999999.0")
    return ET.tostring(root)

def cot_from_file(pathname="msg.cot"):
    #msg="""<event version='2.0' uid='a9e3bb10-17f8-4715-bc50-323063e587fa' type='a-u-A' time='2022-10-12T15:08:22.209Z' start='2022-10-12T15:08:22.209Z' stale='2023-10-12T15:08:22.209Z' how='h-g-i-g-o'><point lat='24.7946371' lon='121.0261352' hae='70.542' ce='9999999.0' le='9999999.0' /><detail><status readiness='true'/><archive/><archive/><contact callsign='airman 1'/><precisionlocation altsrc='DTED0'/><remarks></remarks><usericon iconsetpath='34ae1613-9645-4222-a9d2-e5f243dea2865/Military/airman.png'/><link uid='ANDROID-0d335e9f05caaf2a' production_time='2022-10-12T15:03:49.328Z' type='a-f-G-U-C' parent_callsign='wuulong' relation='p-p'/><color argb='-1'/></detail></event>"""
    if exists(pathname):
        with open(pathname) as f:
            lines = f.readlines()
        msg="".join(lines).strip()
        return bytes(msg,'utf-8')
    return None

async def main():
    """
    The main definition of your program, sets config params and
    adds your serializer to the asyncio task list.
    """
    config = ConfigParser()

    #config["mycottool"] = {"COT_URL": "tcp://127.0.0.1:8087"}
    config["mycottool"] = {"COT_URL": "tcp://34.80.169.66:8087"}
    config = config["mycottool"]

    # Initializes worker queues and tasks.
    clitool = pytak.CLITool(config)
    await clitool.setup()

    # Add your serializer to the asyncio task list.
    clitool.add_tasks(set([MyTx(clitool.tx_queue, config),MyRx(clitool.rx_queue, config)]))

    # Start all tasks.
    await clitool.run()

if __name__ == "__main__":
    asyncio.run(main())
