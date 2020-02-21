#!/usr/bin/env python
"""
* Modifies a Fusion 360 thread profile to contain classes of
* threads that are shifted larger by steps, to aid in calibration.
"""

from lxml import etree
from io import open

#threadlibpath = "./testdata.xml"
threadlibpath = "./ISOMetricprofile.xml"
outfile = "./ISOMetricprofileCalibration.xml"

with open(threadlibpath, "br") as f:
    threadlib = etree.parse(f)

name = threadlib.getroot().find(".//Name")
name.text = name.text + " Calibration"

threads = threadlib.getroot().iterfind(".//ThreadSize")
for ts in threads:
    size = float(ts.find(".//Size").text)
    for designation in ts.iterfind(".//Designation"):
        adjthreads = []  # Buffer additions to the designation to avoid reprocessing
        for thread in designation.iterfind(".//Thread"):
            if thread.find(".//Gender").text == "external":  # Don't adjust external threads
                continue
            # x is [0.1, 0.2, 0.3 etc.]
            for adjustment in [x/100 for x in range(10, 100+1, 10)]:
                tclass = thread.find(".//Class").text + \
                    "{:+.2f}".format(adjustment)
                majordia = round(
                    float(thread.find(".//MajorDia").text) + adjustment, 3)
                pitchdia = round(
                    float(thread.find(".//PitchDia").text) + adjustment, 3)
                minordia = round(
                    float(thread.find(".//MinorDia").text) + adjustment, 3)

                adjthread = \
                    etree.XML(
                        "<Thread>\n"
                        "   <Gender>internal</Gender>\n"
                        "   <Class>{}</Class>\n"
                        "   <MajorDia>{}</MajorDia>\n"
                        "   <PitchDia>{}</PitchDia>\n"
                        "   <MinorDia>{}</MinorDia>\n"
                        "</Thread>\n".format(tclass, majordia, pitchdia, minordia))
                adjthreads.append(adjthread)
        for t in adjthreads:
            designation.append(t)

etree.indent(threadlib)
with open(outfile, "wb") as f:
    threadlib.write(f, pretty_print=True)
