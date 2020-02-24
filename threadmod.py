#!/usr/bin/env python
from lxml import etree
from os import path
from io import open
import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
import functools


# todo: locate fusion360 installation

#threadlibpath = "./testdata.xml"
threadlibpath = "./ISOMetricprofile.xml"
outfile = "./ISOMetricProfileAdjusted.xml"

classprefix = "UM2 "

with open(threadlibpath, "br") as f:
    threadlib = etree.parse(f)


threadsizes = list(map(lambda e: float(e.text),
                       threadlib.getroot().findall(".//ThreadSize/Size")))
print(threadsizes)

datapoints = [(3.0, 0.58), (5.0, 0.55), (8.0, 0.5), (12.0, 0.4)]
xs = np.linspace(min(threadsizes), max(threadsizes))


def sigmoid(p, x):
    x0, y0, c, k = p
    y = c / (1 + np.exp(-k*(x-x0))) + y0
    return y


def residuals(p, x, y):
    return y - sigmoid(p, x)


x, y = zip(*datapoints)
p_guess = (np.median(x), np.median(y), 1.0, 1.0)
p, cov, infodict, mesg, ier = scipy.optimize.leastsq(
    residuals, p_guess, args=(x, y), full_output=True
)

xp = np.linspace(0, 50, 500)
pxp = np.maximum(0, sigmoid(p, xp))


plt.plot(x, y, '.', xp, pxp, '-')
plt.show()

adjfun = np.maximum(0, functools.partial(sigmoid, p))

threads = threadlib.getroot().iterfind(".//ThreadSize")
for ts in threads:
    size = float(ts.find(".//Size").text)
    adjustment = round(adjfun(size), 3)
    print(adjustment)
    for designation in ts.iterfind(".//Designation"):
        print(designation.find(".//ThreadDesignation").text)
        adjthreads = []
        for thread in designation.iterfind(".//Thread"):
            print(thread.find(".//Class").text)
            if thread.find(".//Gender").text == "external":  # Don't adjust external threads
                continue

            tclass = classprefix + thread.find(".//Class").text
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
        print(adjthreads)
        for t in adjthreads:
            print(designation.find(".//ThreadDesignation").text, end=" ")
            print(t.find(".//Class").text)
            designation.append(t)

etree.indent(threadlib)
with open(outfile, "wb") as f:
    threadlib.write(f, pretty_print=True)
