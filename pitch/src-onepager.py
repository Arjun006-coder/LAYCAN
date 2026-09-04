#!/usr/bin/env python3
"""LAYCAN investor one-pager. Two pages: the pitch, and the asterisks."""
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph

D = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DJ",   D + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DJ-B", D + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DJ-I", D + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("MO",   D + "DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("MO-B", D + "DejaVuSansMono-Bold.ttf"))
pdfmetrics.registerFontFamily("DJ", normal="DJ", bold="DJ-B", italic="DJ-I")

INK   = HexColor("#1C2530")
MUTE  = HexColor("#5C6D7A")
DIM   = HexColor("#8A9BA8")
AMBER = HexColor("#C25E12")
TEAL  = HexColor("#0E7C6B")
RED   = HexColor("#B3282D")
DARK  = HexColor("#0E1419")
RULE  = HexColor("#D8E0E6")
WASH  = HexColor("#F4F6F8")

W, H = A4
MG = 38.0
CW = W - 2 * MG

body = ParagraphStyle("body", fontName="DJ", fontSize=8.3, leading=11.6,
                      textColor=INK, alignment=TA_LEFT, spaceAfter=0)
bodyM = ParagraphStyle("bodyM", parent=body, textColor=MUTE)
tiny = ParagraphStyle("tiny", parent=body, fontSize=7.3, leading=10.0, textColor=MUTE)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=10, bulletIndent=0,
                        spaceAfter=3.2)
bulletM = ParagraphStyle("bulletM", parent=bullet, textColor=MUTE)
b2 = ParagraphStyle("b2", parent=body, fontSize=7.9, leading=10.6)
b2M = ParagraphStyle("b2M", parent=b2, textColor=MUTE)
bul2 = ParagraphStyle("bul2", parent=b2, leftIndent=10, bulletIndent=0, spaceAfter=2.6)

c = canvas.Canvas(sys.argv[1] if len(sys.argv) > 1 else "onepager.pdf", pagesize=A4)
c.setTitle("LAYCAN — freight decision engine for bulk cargo importers")
c.setAuthor("Team LAYCAN")


def para(text, style, x, y, w):
    """Draw a paragraph with its top edge at y. Returns the new y (below it)."""
    p = Paragraph(text, style)
    _, h = p.wrapOn(c, w, 2000)
    p.drawOn(c, x, y - h)
    return y - h


def bullets(items, style, x, y, w, glyph="–"):
    for it in items:
        p = Paragraph(it, style, bulletText=glyph)
        _, h = p.wrapOn(c, w, 2000)
        p.drawOn(c, x, y - h)
        y -= h + style.spaceAfter
    return y


def kicker(text, x, y, w, color=AMBER, size=7.4):
    c.setFont("MO-B", size)
    c.setFillColor(color)
    c.drawString(x, y - size, text.upper())
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(x, y - size - 5.5, x + w, y - size - 5.5)
    return y - size - 13.0


def footer(page, total):
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(MG, 46, W - MG, 46)
    c.setFont("MO", 6.6)
    c.setFillColor(DIM)
    c.drawString(MG, 36, "LAYCAN  ·  PRE-SEED  ·  SIH 2026 PS 26006, MINISTRY OF STEEL / SAIL")
    c.drawRightString(W - MG, 36, f"PAGE {page} OF {total}")


# ══════════════════════════════════════════════════════════ PAGE 1
BAND = 96
c.setFillColor(DARK)
c.rect(0, H - BAND, W, BAND, stroke=0, fill=1)

c.setFont("DJ-B", 30)
c.setFillColor(HexColor("#F2F5F7"))
c.drawString(MG, H - 46, "LAYCAN")
c.setFont("MO", 7)
c.setFillColor(HexColor("#8A9BA8"))
c.drawRightString(W - MG, H - 40, "PRE-SEED  ·  DRY BULK, INDIA-BOUND  ·  SEPTEMBER 2026")
c.setFont("DJ", 11.5)
c.setFillColor(HexColor("#FF8A3D"))
c.drawString(MG, H - 66, "A freight decision engine for bulk cargo importers.")
c.setFont("DJ-I", 9)
c.setFillColor(HexColor("#8A9BA8"))
c.drawString(MG, H - 82, "Freight stops being a daily purchase and becomes a managed position.")

GAP = 20
LW = 322.0                     # left column width
RW = CW - LW - GAP             # right column width
RX = MG + LW + GAP

y = H - BAND - 22
yl = y

# ── THE PROBLEM
yl = kicker("The problem", MG, yl, LW)
yl = para(
    "Indian steel, power and cement producers import coal and ore by the shipload and buy the ocean "
    "freight one voyage at a time, on the day the plant asks for it. Four things are missing, and each "
    "of them costs money. There is no threshold that tells a buyer whether today's offer is good "
    "relative to waiting, so the decision defaults to <i>the plant needs coal, fix it</i>. The vessel "
    "class is chosen by habit rather than by computing what the discharge port's draft limit actually "
    "allows a ship to load. Nothing is compared afterwards against what could have been paid, so there "
    "is no institutional memory. And the freight price risk is carried entirely unhedged — by buyers "
    "whose counterparty across every negotiation hedges routinely.",
    body, MG, yl, LW) - 15

# ── WHAT WE SELL
yl = kicker("What we sell", MG, yl, LW)
yl = para("One page a day, per cargo: a decision memo that commits to an action.",
          ParagraphStyle("lead", parent=body, fontName="DJ-B", fontSize=9, leading=12.4),
          MG, yl, LW) - 7
yl = bullets([
    "<b>Fix or wait</b>, expressed as a reservation rate — a number today's offer is measured "
    "against, not an arrow on a chart",
    "<b>Which vessel class, to which port</b>, with draft-limited cargo intake computed from trim and "
    "density, not read off a table",
    "<b>Spot, trip charter or contract of affreightment</b>, chosen on an expected-cost versus "
    "tail-risk frontier and capped by what the buyer can actually lift",
    "<b>How many FFA lots to sell</b>, with hedge effectiveness and residual basis risk both stated",
], bullet, MG, yl, LW) - 8
yl = para(
    "We do not claim to forecast the market, and we say so on stage. Dry bulk rates are close to a "
    "random walk and a liquid forward market already prices them better than we could. The value sits "
    "in the stopping rule, the physical feasibility constraints and the hedge — none of which "
    "require forecast superiority. We prove it the only way that counts: by backtesting <i>decisions</i> "
    "in dollars per tonne against a naive buyer and against perfect hindsight, and publishing the worst "
    "quarter next to the average.",
    bodyM, MG, yl, LW) - 15

# ── DEFENSIBILITY
yl = kicker("Why it is defensible", MG, yl, LW)
yl = para(
    "Two assets compound, and neither of them is software. The first is the <b>decision-outcome "
    "record</b>: every recommendation stored with its model version and joined to what actually "
    "happened — the rate fixed, the days waited, the demurrage paid. Nobody holds this for "
    "India-bound bulk, because nobody else is in the decision loop. The second is the <b>benchmark</b>. "
    "Authoritative daily assessments exist for the world's liquid routes; they do not exist for "
    "Newcastle to Paradip. A platform sitting inside enough Indian importers' fixture flow can "
    "construct the reference nobody publishes, and index businesses become infrastructure.",
    body, MG, yl, LW) - 8
yl = para(
    "There is also a structural reason the incumbents are unlikely to follow us here: their customers "
    "are shipowners, operators and brokers. A product whose job is to tell a charterer to wait is "
    "adversarial to the other side of their book.",
    bodyM, MG, yl, LW)

# ── RIGHT COLUMN
yr = y

def panel(x, top, w, h, fill=WASH):
    c.setFillColor(fill)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.rect(x, top - h, w, h, stroke=1, fill=1)

panel(RX, yr, RW, 96)
yi = kicker("Status", RX + 10, yr - 9, RW - 20, color=TEAL)
yi = para(
    "Pre-product. A six-person team on a five-week build for SIH 2026 — two ML, two full-stack, "
    "one data, one design. Design-partner access to a national steel producer's live procurement "
    "problem through the sponsoring ministry.",
    tiny, RX + 10, yi, RW - 20)
yr = yr - 96 - 18

yr = kicker("Market", RX, yr, RW)
yr = bullets([
    "India is among the world's largest importers of both coking and thermal coal, at a scale of tens "
    "of millions of tonnes of coking coal a year",
    "Global seaborne dry bulk trade is of the order of five billion tonnes a year",
    "Ocean freight is commonly a material double-digit percentage of the delivered cost of imported "
    "coal, and it swings with the rate cycle",
    "Our wedge: Indian importers moving roughly 0.5 to 10 Mtpa with no chartering desk — big "
    "enough for the savings to matter, small enough never to have built the capability",
], bulletM, RX, yr, RW) - 4
yr = para("<i>All four figures are order-of-magnitude estimates and are flagged for verification "
          "before any of them is quoted to a counterparty.</i>", tiny, RX, yr, RW) - 14

yr = kicker("Business model", RX, yr, RW)
yr = para(
    "An annual enterprise subscription, tiered by covered tonnage and anchored to measured savings on "
    "that tonnage rather than to seats. We are deliberately not asserting a price yet: it should be set "
    "against the first shadow-mode result, not against a spreadsheet.",
    body, RX, yr, RW) - 14

yr = kicker("The ask", RX, yr, RW)
yr = para(
    "Indicatively <b>$600K to $1M for eighteen months</b>. The largest single line item is a licensed "
    "freight index feed and satellite AIS coverage — the one purchase that converts our biggest "
    "acknowledged weakness into an operating advantage. Then two quantitative hires and two paid "
    "shadow-mode deployments. The final number should be set from real licence quotes, not from a "
    "market multiple.",
    body, RX, yr, RW)

c.setFillColor(HexColor("#FCF3EC"))
c.setStrokeColor(HexColor("#E8C4A8"))
c.setLineWidth(0.6)
c.rect(MG, 58, CW, 30, stroke=1, fill=1)
c.setFont("MO-B", 6.8)
c.setFillColor(AMBER)
c.drawString(MG + 9, 74, "READ PAGE 2 BEFORE YOU QUOTE ANY NUMBER ON PAGE 1.")
c.setFont("DJ", 7.3)
c.setFillColor(MUTE)
c.drawString(MG + 9, 64, "Written without live data access. Page 2 states which claims are verified, "
                         "which are estimates, and how to falsify us.")
footer(1, 2)
c.showPage()

# ══════════════════════════════════════════════════════════ PAGE 2
c.setFillColor(DARK)
c.rect(0, H - 54, W, 54, stroke=0, fill=1)
c.setFont("DJ-B", 15)
c.setFillColor(HexColor("#F2F5F7"))
c.drawString(MG, H - 34, "Page 2 — the asterisks")
c.setFont("DJ", 8.6)
c.setFillColor(HexColor("#8A9BA8"))
c.drawRightString(W - MG, H - 33, "Every startup one-pager has these. Most leave them off.")

y2 = H - 54 - 20

y2 = kicker("What is verified, and what is not", MG, y2, CW, color=RED)
y2 = para(
    "This material was produced without live internet access, so <b>every quantitative and competitive "
    "claim in it is an estimate from domain knowledge, not a sourced figure</b> — port drafts, handling "
    "rates, import volumes, freight share of landed cost, competitor pricing, market size. The "
    "engineering design does not depend on any of them; the credibility of the pitch does. The "
    "repository therefore carries a blocking checklist of sixteen verification items to be closed "
    "against primary sources before the deck is shown or a customer approached — about two days of "
    "work, and the highest-value two days on the project. An investor who catches one wrong port draft "
    "is entitled to discount everything else we say. In that checklist, <i>unknown</i> is an acceptable "
    "answer and a guess is not.",
    b2, MG, y2, CW) - 13

y2 = kicker("Competitive landscape — and the claim we most need to disprove", MG, y2, CW)
y2 = para(
    "The maritime software market is not empty and it would be dishonest to imply otherwise. It divides "
    "roughly four ways. <b>Vessel-tracking and commodity-flow analytics</b> sell AIS-derived positions, "
    "port calls and trade-flow estimates to trading desks, owners and analysts. <b>Chartering "
    "intelligence platforms</b> sell market data, fixture history and cargo matching to people who "
    "charter professionally. <b>Voyage and commercial management systems</b> are the system of record "
    "for owners running fleets. <b>Risk and compliance</b> products sell sanctions and behavioural "
    "screening to governments, insurers and banks. Alongside them sit performance-optimisation vendors, "
    "broking-desk email tools, port cost specialists, and the index provider the derivatives settle "
    "against.",
    b2, MG, y2, CW) - 6
y2 = para(
    "Our central commercial hypothesis is that <b>none of them sells a prescriptive, dated fix-or-wait "
    "threshold combined with a port-feasible vessel choice, an instrument mix and a hedge size, to an "
    "industrial importer with no chartering desk</b>. They sell data and workflow, by the seat, to "
    "people who already know what the market is worth. Different product, different buyer. It is also "
    "exactly the kind of claim founders talk themselves into, so it sits in the checklist as an item to "
    "be attacked rather than confirmed — including a search for Indian freight-tech entrants and for "
    "any FFA broker shipping software to physical buyers rather than broking to them.",
    b2M, MG, y2, CW) - 13

y2 = kicker("Risks, and what we actually do about them", MG, y2, CW)
risks = [
    ("The timing edge may not survive a real backtest.",
     "Then we say so, and the pitch changes rather than the honesty. The feasibility and hedging layers "
     "create value with no forecasting content at all: a vessel that cannot berth is a hard error "
     "regardless of the rate, and an unhedged position is an exposure regardless of direction."),
    ("The best rate data is licensed, and we will not scrape it.",
     "Until a licence exists the daily series is a calibrated stochastic process, every simulated figure "
     "carries a visible badge, and the simulator is validated against free observables. A licence is a "
     "config change and a funding line, not a rewrite."),
    ("Public sector procurement is slow and price-led.",
     "So the sponsoring relationship is design partnership and credibility, not first revenue. Initial "
     "paid deployments target private importers, where the cycle is shorter."),
    ("An incumbent could add a recommendation module.",
     "They would need the decision-outcome dataset and the India-specific port physics — and they would "
     "be selling advice against the interests of the owners and brokers who pay them today."),
    ("A confident wrong number destroys trust faster than a missing one.",
     "The language models are forbidden from emitting a numeral at all, enforced by a schema validator "
     "and a build check rather than by convention. Every figure originates in a versioned, unit-tested "
     "solver and carries provenance to its source, licence and timestamp. A critic agent attacks each "
     "recommendation before it ships and escalates to a human when it cannot get comfortable."),
]
for h, b in risks:
    y2 = para(f"<b>{h}</b>", b2, MG, y2, CW)
    y2 = para(b, b2M, MG + 12, y2 - 1, CW - 12) - 4.5
y2 -= 7

y2 = kicker("The next ninety days", MG, y2, CW, color=TEAL)
y2 = bullets([
    "<b>Days 1–14.</b> Close the verification checklist against primary sources, publish the citation "
    "index, and correct or delete every figure that does not survive it.",
    "<b>Days 15–45.</b> Ship the deterministic core — port physics, voyage economics, stopping policy, "
    "assignment program — with the decision backtest and a leakage test running in CI.",
    "<b>Days 46–70.</b> Complete the agent layer, the critic, and the provenanced decision memo. Freeze "
    "a demo snapshot so nothing depends on venue wifi.",
    "<b>Days 71–90.</b> Take the measured result, whatever it says, to three importers and ask one to "
    "run us in shadow mode for a quarter.",
], bul2, MG, y2, CW) - 9

y2 = kicker("How to falsify us", MG, y2, CW)
para("Ask for the capture ratio — the share of theoretically available timing value the policy actually "
     "captured, measured walk-forward and net of commissions and frictions. Then ask for the worst "
     "quarter in the sample, and for the result against the forward curve rather than against a naive "
     "buyer. If we cannot produce all three, we have not earned the meeting.",
     b2, MG, y2, CW)

footer(2, 2)
c.save()
print("ok")
