"""Create the final FireGUARD pdf output"""

import os
import math
import subprocess

import PyPDF2
from PyPDF2 import PdfFileMerger
from fpdf import FPDF

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import TABLOID
from reportlab.pdfbase import pdfform
import reportlab.lib.colors as colors
from reportlab.lib.units import inch
from reportlab.platypus.tables import Table
from reportlab.platypus.tables import TableStyle

from log import *

from Settings import Settings
from util import find_line
from util import find_lines

## Directory containing program to compress outputs
BINARY_DIR = os.path.join(Settings.HOME_DIR, "pdfsizeopt")
## Binary for compressing output pdf
BINARY = os.path.join(BINARY_DIR, "pdfsizeopt.exe")

## Basic font to use
NORMAL = "Helvetica"
## Bold font to use
BOLD = "Helvetica-Bold"
## Width of page
PAGE_WIDTH = TABLOID[1]
## Height of page
PAGE_HEIGHT = TABLOID[0]
## Margin to use on edge of page
MARGIN = 0.2 * inch
## Width of map thumbnails
IMAGE_WIDTH = (PAGE_WIDTH - 2 * MARGIN) / 3.0
## Height of map thumbnails
IMAGE_HEIGHT = (PAGE_HEIGHT - 2 * MARGIN) / 3.0
## Width of logo
LOGO_WIDTH = IMAGE_WIDTH / 4
## Height of logo
LOGO_HEIGHT = LOGO_WIDTH * (4929.0 / 5258.0)
## Landscape 11x17 page dimensions
LANDSCAPE = tuple([PAGE_WIDTH, PAGE_HEIGHT])
## question we are on (defines position on page)
question = 1

## @param in_file PDF to compress
## @param out_file Path to save compressed file to
## @return None
def compressPdf(in_file, out_file):
    """Call program to compress pdf"""
    logging.info("Compressing {}...".format(in_file))
    CREATE_NO_WINDOW            = 0x08000000
    ABOVE_NORMAL_PRIORITY_CLASS = 0x00008000
    CREATION_FLAGS = CREATE_NO_WINDOW | ABOVE_NORMAL_PRIORITY_CLASS
    process = subprocess.Popen([BINARY, "--use-pngout=no", "--quiet", in_file, out_file],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           cwd=BINARY_DIR,
                           creationflags=CREATION_FLAGS)
    stdout, stderr = process.communicate()

def makeCover(fire, days, dates, maps, sim_output, scores):
    """!
    Make cover page pdf summarizing FireSTARR results
    @param fire Fire name to use
    @param days Array of days simulation created output for
    @param dates Array of dates simulation created output for
    @param maps List of maps to use for cover page thumbnails
    @param sim_output Array of simulation output, by line
    @param scores Array of scores for simulation output dates
    @return Path of cover page PDF
    """
    size = float(find_line(sim_output, 'Fire starting with size', 'size ')[:-2])
    sizes = find_lines(sim_output, ' size at end of day')
    confirmed = find_line(sim_output, 'Initialized WxShield with date')[-16:]
    numSims = int(find_line(sim_output, 'simulations', 'Ran ').split(' ')[0])
    showSims = "{:,}".format(numSims)
    score = scores[-1]
    showScore = score
    lat_find = "Using ignition point ("
    lat_long = find_line(sim_output, lat_find, lat_find)[:-1].split(',')
    lat = float(lat_long[0].strip())
    lon = float(lat_long[1].strip())
    loc_find = 'UTM coordinates are: '
    location = find_line(sim_output, loc_find, loc_find)
    runTime  = sim_output[1][1:20]
    startup = find_lines(sim_output, 'Startup indices ')
    startup = startup[0] if (len(startup) > 0) else "Startup indices are not valid"
    txtStartup = startup[startup.find("Startup indices "):]
    cover = os.path.join(os.path.dirname(maps[0]), fire + "_cover.pdf")
    title = "{} - {}".format(fire, dates[0])
    #
    c = canvas.Canvas(cover, LANDSCAPE)
    c.rect(MARGIN / 3, MARGIN / 3, PAGE_WIDTH - 2 * MARGIN / 3, PAGE_HEIGHT - 2 * MARGIN / 3, fill=0)
    c.setFillColor(colors.white)
    c.rect(MARGIN / 2, PAGE_HEIGHT - MARGIN, 220, 20, fill=1)
    c.setFillColor(colors.black)
    c.setFont(NORMAL, 20)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN, 'Part 1: Burn Probability')
    c.setFont(BOLD, 36)
    c.drawCentredString(IMAGE_WIDTH / 2, PAGE_HEIGHT - 3 * MARGIN, title)
    c.drawInlineImage(r'C:\FireGUARD\mapping\logo_all.png', MARGIN / 2, PAGE_HEIGHT - (3.5 * MARGIN + LOGO_HEIGHT), LOGO_WIDTH, LOGO_HEIGHT)
    c.setFont(BOLD, 20)
    c.drawCentredString(MARGIN + 1.4 * LOGO_WIDTH, PAGE_HEIGHT - (5 * MARGIN), 'Total Risk')
    c.setFont(BOLD, 12)
    c.drawCentredString(MARGIN + 1.4 * LOGO_WIDTH, PAGE_HEIGHT - (6 * MARGIN), '(on day 14)')
    c.setFont(BOLD, 36)
    c.drawCentredString(MARGIN + 1.4 * LOGO_WIDTH, PAGE_HEIGHT - (9 * MARGIN), showScore)
    #
    c.setFont(BOLD, 12)
    t = Table([['Simulation Start', confirmed],
              ['Location', location],
              ['Initial size (ha)', "{:,}".format(size)],
              ['Model run', runTime],
              ['Simulations', showSims]])
    t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                             ]))
    #
    w, h = t.wrapOn(c, 0, 0)
    t.drawOn(c, 2 * LOGO_WIDTH + MARGIN, PAGE_HEIGHT - (9.7 * MARGIN))
    c.drawInlineImage(maps[1], MARGIN + IMAGE_WIDTH, MARGIN + 2 * IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT)
    c.drawInlineImage(maps[0], MARGIN + 2 * IMAGE_WIDTH, MARGIN + 2 * IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT)
    c.drawInlineImage(maps[2], MARGIN + IMAGE_WIDTH, MARGIN + IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT)
    c.drawInlineImage(maps[4], MARGIN + 2 * IMAGE_WIDTH, MARGIN + IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT)
    c.drawInlineImage(maps[3], MARGIN + IMAGE_WIDTH, MARGIN, IMAGE_WIDTH, IMAGE_HEIGHT)
    c.drawInlineImage(maps[5], MARGIN + 2 * IMAGE_WIDTH, MARGIN, IMAGE_WIDTH, IMAGE_HEIGHT)
    #
    c.setFont(BOLD, 10)
    c.drawCentredString(MARGIN + IMAGE_WIDTH / 2 , 630, txtStartup)
    data = [['Simulated fire statistics', '', '', '', '', '', ''],
              ['', 'Date', 'Size (ha)', '', '', '', 'Total Risk'],
              ['Day*', '(23:59 local)', 'Min', 'Average', 'Median**', 'Max', '(Avg Loss)']]
    for i in xrange(len(days)):
        sizeline = 'size at end of day ' + str(days[i]) + ': '
        size = [x for x in sizes if -1 != x.find(sizeline)]
        size_split = size[0][(size[0].find(sizeline) + len(sizeline)):].split(' ')
        size_min = "{:,}".format(int(round(float(size_split[0]))))
        size_max = "{:,}".format(int(round(float(size_split[3]))))
        size_median = "{:,}".format(int(round(float(size_split[9]))))
        size_mean = "{:,}".format(int(round(float(size_split[6]))))
        risk = scores[i]
        data.append([str(days[i]), dates[i], size_min, size_mean, size_median, size_max, risk])
    t = Table(data, colWidths=[40, 65, 55, 55, 55, 55, 55])
    t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('FONTNAME', (0,0), (-1, 2), BOLD),
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('SPAN',(2,1),(-2,1)),
                            ('SPAN',(0,0),(-1,0)),
                             ]))
    #
    w, h = t.wrapOn(c, 0, 0)
    t.drawOn(c, MARGIN, 470)
    c.setFont(NORMAL, 10)
    c.drawString(MARGIN, 460, '* Day 1 is the simulation start date')
    c.drawString(MARGIN, 450, '** Half of the fires are smaller than and larger than the median size')
    #
    form = c.acroForm
    #
    c.setFont(NORMAL, 12)
    def addQuestion(q, y):
        global question
        c.drawString(MARGIN, y + 8, q)
        group = 'radio' + str(question)
        form.radio(name=group, tooltip='Field radio1',
                   value='yes', selected=False,
                   x=170, y=y, buttonStyle='circle',
                   borderStyle='solid', shape='circle')
        form.radio(name=group, tooltip='Field radio1',
                   value='no', selected=False,
                   x=195, y=y, buttonStyle='circle',
                   borderStyle='solid', shape='circle')
        form.textfield(name='reason' + str(question), tooltip='Explanation',
                   x=225, y=y, borderStyle='inset',
                   borderColor=colors.black, fillColor=colors.white, 
                   width=180, height=20,
                   textColor=colors.black, forceBorder=True)
        question = question + 1
    c.drawString(170, 425, 'Yes  No')
    addQuestion('Start location accurate', 400)
    addQuestion('Start size correct', 380)
    addQuestion('Perimeter most recent', 360)
    addQuestion('Fuel map accurate', 340)
    addQuestion('Startup indices appropriate', 320)
    addQuestion('Spread matches weather', 300)
    addQuestion('Projection is reasonable', 280)
    c.drawString(MARGIN, 260, 'If no to any question, explain why this is still operationally useful:')
    form.textfield(name='notes', tooltip='Notes',
                   x=MARGIN, y=235, borderStyle='inset',
                   borderColor=colors.black, fillColor=colors.white, 
                   width=405 - MARGIN, height=20,
                   textColor=colors.black, forceBorder=True)
    #
    c.setFont(BOLD, 20)
    c.drawString(MARGIN, 215, 'Reviewed by:')
    form.textfield(name='reviewer', tooltip='Reviewed by',
                   x=145, y=213, borderStyle='inset',
                   borderColor=colors.black, fillColor=colors.white, 
                   width=260, height=20,
                   textColor=colors.black, forceBorder=True)
    #
    c.setFont(BOLD, 13)
    c.drawString(MARGIN, 195, 'Interpreting the burn probability maps:')
    c.setFont(NORMAL, 12)
    c.drawString(MARGIN, 180, 'Fire growth is simulated for thousands of individual weather and fire')
    c.drawString(MARGIN, 164, 'behaviour scenarios. The burn probability is the fraction of scenarios in')
    c.drawString(MARGIN, 148, 'which each cell burned. It is extremely unlikely that the whole coloured')
    c.drawString(MARGIN, 132, 'area burned in a single scenario.')
    #
    c.setFont(BOLD, 13)
    c.drawString(MARGIN, 116, 'Warning - Experimental Model')
    c.setFont(NORMAL, 12)
    c.drawString(MARGIN, 100, 'Any operational use should only be done with caution and awareness of')
    c.drawString(MARGIN, 84, 'the assumptions and simplifications. The model spreads over a virtual grid')
    c.drawString(MARGIN, 68, 'of 1 ha cells derived from Ontario\'s FBP Fuel Model. Assumes no')
    c.drawString(MARGIN, 52, 'suppression. Does not represent fine scale barriers (small creeks, etc.) or')
    c.drawString(MARGIN, 36, 'long-range spotting. This model is under continuous development, and can')
    c.drawString(MARGIN, 20, 'change at any time.')
    c.setFont(BOLD, 10)
    c.drawCentredString(PAGE_WIDTH / 2 , 5, Settings.ACTIVE_OFFER)
    c.save()
    return cover

def makeRampart(fire, days, dates, maps, sim_output, scores):
    """!
    Make summary page for RamPART and risk
    @param fire Fire name to use
    @param days Array of days simulation created output for
    @param dates Array of dates simulation created output for
    @param maps List of maps to use for cover page thumbnails
    @param sim_output Array of simulation output, by line
    @param scores Array of scores for simulation output dates
    @return Path of RamPART summary page PDF
    """
    size = float(find_line(sim_output, 'Fire starting with size', 'size ')[:-2])
    sizes = find_lines(sim_output, ' size at end of day')
    confirmed = find_line(sim_output, 'Initialized WxShield with date')[-16:]
    numSims = int(find_line(sim_output, 'simulations', 'Ran ').split(' ')[0])
    showSims = "{:,}".format(numSims)
    score = scores[-1]
    showScore = score
    lat_find = "Using ignition point ("
    lat_long = find_line(sim_output, lat_find, lat_find)[:-1].split(',')
    lat = float(lat_long[0].strip())
    lon = float(lat_long[1].strip())
    loc_find = 'UTM coordinates are: '
    location = find_line(sim_output, loc_find, loc_find)
    runTime  = sim_output[1][1:20]
    startup = find_lines(sim_output, 'Startup indices ')
    startup = startup[0] if (len(startup) > 0) else "Startup indices are not valid"
    txtStartup = startup[startup.find("Startup indices "):]
    rampart = os.path.join(os.path.dirname(maps[0]), fire + "_rampart.pdf")
    title = "{} - {}".format(fire, dates[0])
    #
    c = canvas.Canvas(rampart, LANDSCAPE)
    c.rect(MARGIN / 3, MARGIN / 3, PAGE_WIDTH - 2 * MARGIN / 3, PAGE_HEIGHT - 2 * MARGIN / 3, fill=0)
    c.setFillColor(colors.white)
    c.rect(MARGIN / 2, PAGE_HEIGHT - MARGIN, 220, 20, fill=1)
    c.setFillColor(colors.black)
    c.setFont(NORMAL, 20)
    c.drawString(MARGIN, PAGE_HEIGHT - MARGIN, 'Part 2: Impact & Risk')
    c.setFont(BOLD, 36)
    c.drawCentredString(IMAGE_WIDTH / 2, PAGE_HEIGHT - 3 * MARGIN, title)
    c.drawInlineImage(r'C:\FireGUARD\mapping\logo_all.png', MARGIN / 2, PAGE_HEIGHT - (3.5 * MARGIN + LOGO_HEIGHT), LOGO_WIDTH, LOGO_HEIGHT)
    c.setFont(BOLD, 20)
    c.drawCentredString(MARGIN + 1.4 * LOGO_WIDTH, PAGE_HEIGHT - (5 * MARGIN), 'Total Risk')
    c.setFont(BOLD, 12)
    c.drawCentredString(MARGIN + 1.4 * LOGO_WIDTH, PAGE_HEIGHT - (6 * MARGIN), '(on day 14)')
    c.setFont(BOLD, 36)
    c.drawCentredString(MARGIN + 1.4 * LOGO_WIDTH, PAGE_HEIGHT - (9 * MARGIN), showScore)
    #
    c.setFont(BOLD, 12)
    t = Table([['Simulation Start', confirmed],
              ['Location', location],
              ['Initial size (ha)', "{:,}".format(size)],
              ['Model run', runTime],
              ['Simulations', showSims]])
    t.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                             ]))
    #
    w, h = t.wrapOn(c, 0, 0)
    t.drawOn(c, 2 * LOGO_WIDTH + MARGIN, PAGE_HEIGHT - (9.7 * MARGIN))
    c.drawInlineImage(maps[1], MARGIN + IMAGE_WIDTH, MARGIN + 2 * IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT)
    c.drawInlineImage(maps[0], MARGIN + 2 * IMAGE_WIDTH, MARGIN + 2 * IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT)
    c.drawInlineImage(maps[2], MARGIN + IMAGE_WIDTH, MARGIN + IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT)
    c.drawInlineImage(maps[4], MARGIN + 2 * IMAGE_WIDTH, MARGIN + IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT)
    c.drawInlineImage(maps[3], MARGIN + IMAGE_WIDTH, MARGIN, IMAGE_WIDTH, IMAGE_HEIGHT)
    c.drawInlineImage(maps[5], MARGIN + 2 * IMAGE_WIDTH, MARGIN, IMAGE_WIDTH, IMAGE_HEIGHT)
    #
    c.setFont(BOLD, 20)
    c.drawString(MARGIN, 630, 'Check:')
    def mkPoint(title, text, y):
        c.setFont(BOLD, 10)
        c.drawString(MARGIN, y, "- " + title)
        c.setFont(NORMAL, 10)
        c.drawString(110, y, text)
    mkPoint("Burn Probability", "Is it accurate? Does it make sense? What were the assumptions?", 615)
    mkPoint("ARs", 'Can they be burnt? Are they located in areas of "non-fuel"?', 600)
    c.setFont(BOLD, 20)
    c.drawString(MARGIN, 580, "Product Description:")
    mkPoint("Potential Impact", "What would happen if the entire area were to burn with 100%", 565)
    c.drawString(110, 550, "certainty at a high fire intensity?")
    mkPoint("Total Risk", "The sum of the risk per cell for the entire area.", 535)
    mkPoint("Risk Map", "The impact (adjusted for different fire intensities) times the likelihood", 520)
    c.drawString(110, 505, "that a cell is burnt, giving the risk per cell.")
    c.setFont(BOLD, 20)
    c.drawString(MARGIN, 485, "Terminology:")
    #
    mkPoint("Risk", 'Is impact times likelihood, literally the "average" loss, as if the', 470)
    c.drawString(110, 455, "situation was repeated many times.")
    mkPoint("ARs", 'Assests and Resources (ARs) are physical things on the landscape.', 440)
    mkPoint("Resources", 'Are biological and other natural elements.', 425)
    mkPoint("Assets", 'Are objects built by people.', 410)
    mkPoint("Fire Effects", 'Are the physical, biological, and ecological changes to ARs and their', 395)
    c.drawString(110, 380, 'functioning caused by fire. Only "direct" effects happening')
    c.drawString(110, 365, 'immediately or soon after the passage of fire are considered.')
    mkPoint("Fire Impacts", 'Are the changes in worth, as judged by people, that are caused by', 350)
    c.drawString(110, 335, 'fire effects. Impact represents loss and positive impacts are not')
    c.drawString(110, 320, 'considered. There are three impact types that make up total impact:')
    c.drawString(110, 305, 'Social, Economic, and Emergency Response.')
    c.drawInlineImage(r'C:\FireGUARD\mapping\impact_flow.png', MARGIN, 200, IMAGE_WIDTH, 366.0 / 1435 * IMAGE_WIDTH)
    c.drawString(MARGIN, 185, 'Q: What is the impact and risk scale?')
    c.drawString(MARGIN, 170, 'A: Staff scored impacts on a 1-10 scale for each of 52 different ARs.')
    data = [['', 'Total Potential Impact', 'Risk (average loss)', ''],
              ['', '(HFI 4000+ kW/m)', '50% prob', '90% prob'],
              ['1 structure', '6.6', '3.3', '5.9'],
              ['100 ha of timber', '5.9', '3.0', '5.3'],
              ['1 km of hydro line', '7.0', '3.5', '6.3'],
              ['Example sum in 1 ha (3 structures,\n50 m of hydro line, 1 ha of timber)', '20.2', '10.1', '18.2']]
    t = Table(data, colWidths=[170, 105, 60, 60])
    t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('FONTNAME', (0,0), (-1, 1), BOLD),
                            ('FONTSIZE', (0,0), (-1, -1), 10),
                            ('ALIGN', (1,0), (-1,1), 'CENTER'),
                            ('SPAN',(-2,0),(-1,0)),
                             ]))
    #
    w, h = t.wrapOn(c, 0, 0)
    t.drawOn(c, MARGIN, 45)
    c.setFont(BOLD, 10)
    c.drawString(MARGIN, 30, 'Interpretation:')
    c.setFont(NORMAL, 10)
    c.drawString(MARGIN, 15, 'A risk of 10 is "like" the loss of 200 ha of timber, or worse than the loss of a structure.')
    c.drawCentredString(PAGE_WIDTH / 2 , 5, Settings.ACTIVE_OFFER)
    c.save()
    return rampart

def makePDF(fire, days, dates, mxd_names, wxshield, risk_maps, sim_output, out_file, scores):
    """!
    Create summary pdfs and merge everything together before compressing
    @param fire Fire name to use
    @param days Array of days simulation created output for
    @param dates Array of dates simulation created output for
    @param mxd_names List of mxds to use for cover page thumbnails and full page exports
    @param wxshield WeatherSHIELD PDF export
    @param risk_maps List of mxds to use for RamPART page thumbnails and full page exports
    @param sim_output Array of simulation output, by line
    @param out_file File to save final output to
    @param scores Array of scores for simulation output dates
    @return None
    """
    cover = makeCover(fire, days, dates, mxd_names, sim_output, scores)
    rampart = makeRampart(fire, days, dates, risk_maps, sim_output, scores)
    logging.info("Merging...")
    merged = os.path.join(os.path.dirname(mxd_names[0]), fire + "_merged.pdf")
    merger = PdfFileMerger()
    pdfs = map(lambda _: os.path.splitext(_)[0] + ".pdf", mxd_names)
    pdfs = [x for x in pdfs if os.path.exists(x)]
    merger.append(cover, 'rb')
    for pdf in pdfs:
        merger.append(pdf, 'rb')
    merger.append(wxshield, 'rb')
    merger.append(rampart, 'rb')
    risk_pdfs = map(lambda _: os.path.splitext(_)[0] + ".pdf", risk_maps)
    risk_pdfs = [x for x in risk_pdfs if os.path.exists(x)]
    for pdf in risk_pdfs:
        merger.append(pdf, 'rb')
    with open(merged, 'wb') as fout:
        merger.write(fout)
    merger.close()
    del merger
    compressPdf(merged, out_file)
