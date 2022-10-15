#!/usr/bin/env python3

import asyncio
import xml.etree.ElementTree as ET

from configparser import ConfigParser

import pytak
from os.path import exists


class MySerializer(pytak.QueueWorker):
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
            data = tak_pong3()
            if data:
                print("sent_cnt=%i" %(sent_cnt))
                await self.handle_data(data)
            await asyncio.sleep(20)


def tak_pong():
    """
    Generates a simple takPong COT Event.
    """
    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", "t-x-d-d")
    root.set("uid", "takPong")
    root.set("how", "m-g")
    root.set("time", pytak.cot_time())
    root.set("start", pytak.cot_time())
    root.set("stale", pytak.cot_time(3600))
    return ET.tostring(root)

def tak_pong2():
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

def tak_pong3():
    #msg="""<event version='2.0' uid='a9e3bb10-17f8-4715-bc50-323063e587fa' type='a-u-A' time='2022-10-12T15:08:22.209Z' start='2022-10-12T15:08:22.209Z' stale='2023-10-12T15:08:22.209Z' how='h-g-i-g-o'><point lat='24.7946371' lon='121.0261352' hae='70.542' ce='9999999.0' le='9999999.0' /><detail><status readiness='true'/><archive/><archive/><contact callsign='airman 1'/><precisionlocation altsrc='DTED0'/><remarks></remarks><usericon iconsetpath='34ae1613-9645-4222-a9d2-e5f243dea2865/Military/airman.png'/><link uid='ANDROID-0d335e9f05caaf2a' production_time='2022-10-12T15:03:49.328Z' type='a-f-G-U-C' parent_callsign='wuulong' relation='p-p'/><color argb='-1'/></detail></event>"""
    if exists("msg.cot"):
        with open("msg.cot") as f:
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
    config["mycottool"] = {"COT_URL": "tcp://34.80.169.66:8087"}
    config = config["mycottool"]

    # Initializes worker queues and tasks.
    clitool = pytak.CLITool(config)
    await clitool.setup()

    # Add your serializer to the asyncio task list.
    clitool.add_tasks(set([MySerializer(clitool.tx_queue, config)]))

    # Start all tasks.
    await clitool.run()

if __name__ == "__main__":
    asyncio.run(main())
