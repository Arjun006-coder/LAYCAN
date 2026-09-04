# LAYCAN — the whole project in plain language

For the team. Read this before you write code. Twenty minutes.

No shipping jargon in this document except where the word is unavoidable, and those are explained. The technical version is `MASTER-PLAN.md`; the shipping version is `DOMAIN-PRIMER.md`. This is the version you use to explain the project to your parents, a judge, or a teammate who joined yesterday.

---

## 1. The problem, told as a story

A steel plant in Odisha needs coking coal. India doesn't have enough good coking coal, so it comes from Australia by ship — not in containers, just poured into the hold of a bulk carrier. Seventy-five thousand tonnes at a time. Sometimes a hundred and eighty thousand.

Somebody has to hire that ship.

Here is how it works today. The plant says "we need coal by mid-October." A person in procurement emails three or four shipbrokers. Offers come back over a day or two. They pick one. The ship sails. Six weeks later the coal arrives. Then they do it again. And again. Forty, sixty, a hundred times a year.

Now notice what is missing from that story.

**Nobody ever asks whether today's price is a good price.** There is no number to compare the offer against. So the decision defaults to: *the plant needs coal, fix it.* You would never buy anything else this way. You check prices on a phone before buying a ₹2,000 pair of shoes. This is a ₹15 crore purchase made without a reference price.

**Nobody checks afterwards.** Nobody sits down in January and says "last year we paid an average of $24 a tonne; if we had waited three days on these eleven cargoes we would have paid $22." The information exists. Nobody looks. So the organisation never learns.

**The ship is chosen by habit.** More on this below, because it's the most interesting part and the part that wins us the room.

**And the price risk is carried completely naked.** Freight prices swing violently — they can double in six months. There is a financial market for insuring against exactly that, and professional trading houses use it constantly. The Indian steel plant, generally, does not. Which means in every negotiation, the person on the other side of the table has hedged and you haven't.

That's the problem. Not "we can't predict freight prices." **The problem is that a very large, very repetitive purchase is being made with no price discipline, no physics check, no memory, and no insurance.**

---

## 2. How big is this actually

India imported about 268 million tonnes of coal in FY 2023-24, of which roughly 57 million tonnes was coking coal for steelmaking. That's thousands of shiploads a year into the East Coast alone.

Ocean freight is a meaningful slice of what that coal costs by the time it reaches the plant gate — not a rounding error, a double-digit percentage that moves with the shipping cycle. So a few percent off the freight bill on a few crore tonnes is a large number.

**But here is the discipline I want from everyone on this team.** We do not yet know what we save. We have not measured it. Until the backtest runs, any savings figure we say out loud is invented, and inventing it is how we lose. The honest sentence is: *"this is the size of the spend, our measured saving is the number we will show you, and we are not going to guess it in advance."*

Also: be careful which SAIL number you quote. "Freight outward" in their annual report is the cost of shipping *finished steel out to customers*. That is not the same as ocean freight on *imported raw material coming in*, which is what we address. Get the right line item or don't use one.

---

## 3. The one idea that everything else depends on

Read this section twice.

The problem statement is called "freight forecasting." The obvious project is a model that predicts freight prices. **We are deliberately not building that, and understanding why is the difference between winning and losing.**

Freight prices behave a lot like a stock price. They wander. Tomorrow's price is roughly today's price plus a random shove. Decades of academic work says beating a simple "tomorrow equals today" guess is genuinely hard at the horizons that matter.

Worse: there is already a financial market where professionals trade the future price of freight. Those prices are public-ish and they aggregate the opinion of everyone who has money on the line. **A six-person student team in five weeks is not going to out-predict that market.** Anyone who tells you otherwise is selling you something.

So if we stand on stage and say "our AI predicts freight rates with 92% accuracy," one judge who knows this field asks one question — *"how do you do against the forward curve?"* — and the project is over. That is a real risk, not a hypothetical.

**So we changed the question.**

Instead of *"what will the price be?"* we ask *"given the price in front of me today, should I commit now or wait — and what exactly is my cutoff?"*

That is a completely different kind of problem, and it is solvable even when prediction isn't.

### The analogy that makes it click

You are selling your house. Offers arrive over the next thirty days. You cannot predict tomorrow's offer. But you can absolutely work out a rule: *"today, with 22 days left, I accept anything above ₹80 lakh."* Tomorrow the number is slightly different. On day 29, with a deadline looming, you accept almost anything.

That threshold is computable. You need to know how offers typically vary, and how many days you have left. You do **not** need to know what tomorrow's offer will be.

We are doing exactly that, upside down, because we're buying instead of selling. Every morning, for every cargo, we compute: **"fix today if the offer is at or below $X per tonne."** As the loading window closes, X rises, because your ability to walk away is disappearing. That number — the **reservation rate** — is the core of the product.

It requires no forecasting superiority. It requires knowing how volatile the market is and how much time you have. Both of those we can get.

---

## 4. The bit that makes shipping people take us seriously

This is my favourite part and it should be yours.

A ship floats lower in the water the more you load into it. Every port has a depth limit — the channel, the berth. So **a port's depth limit is really a cargo limit.**

Which means the obvious instinct — *bigger ship, lower cost per tonne, always better* — is frequently wrong.

Real numbers from our verified port data:

- **Haldia** is limited to about **8.5 metres** of draft, because it's up a tidal river. A big Capesize ship needs roughly **18 metres** when loaded. It physically cannot go there. Cargo for Haldia gets partly unloaded at an anchorage offshore into smaller vessels first — extra ships, extra days, extra cost.
- **Visakhapatnam is two different ports wearing one name.** The Outer Harbour takes about **18.1 m** and handles Capesize vessels. The Inner Harbour takes about **14.5 m** and caps out around 240 m in length. Treat "Vizag" as one number and every recommendation you make is wrong half the time. A maritime judge knows this. It is a trap and we've stepped around it.
- **Paradip** isn't one number either — the coal berths run around **16.0 m** while other bulk berths are shallower. Model it per berth type.
- **Gangavaram**, right next door to Vizag, goes to about **17.7 m**, which makes it one of the few genuinely Capesize-capable options on the East Coast.
- And the load end bites too: **Newcastle** in Australia has a maximum sailing draft around **16.1 m**. A fully-loaded Capesize draws about 18. So it *cannot leave Newcastle full* regardless of where it's going.

Put it together and you get the demo moment: somebody says "just use the biggest ship, it's cheapest per tonne," and we show the arithmetic where the big ship arrives at a shallow port, can only fill two-thirds of its hold, needs lightering and waits for a tide — and ends up costing more than the smaller ship that simply fit.

**None of that is a prediction. It is arithmetic and geometry.** It is right or wrong, testable, and it does not depend on any model being clever. That's why it's our credibility layer.

---

## 5. What we are actually building

**One page a day, for each cargo, that commits to an action.** Not a dashboard. Not charts for someone else to interpret. A recommendation with a number attached, so that if we're wrong you can prove it.

The features, in plain terms:

**Fix or wait.** The reservation rate from section 3. "Fix today if you're offered $23.40/t or better. Otherwise wait — recheck tomorrow." Plus what waiting costs you if you're wrong.

**Which ship, to which port.** Given the cargo, the ports that can physically take it, and how much each ship class can actually load there after the depth limit bites. This is where the section 4 arithmetic lives. Hard constraints, not preferences — if a ship can't berth, it isn't an option at any price.

**Which kind of contract.** You can buy one voyage at a time (flexible, no price certainty), or commit to six voyages over a year (cheaper, price certainty, but if your plant slows down you pay for ships you don't use — that penalty is called deadfreight). We work out how much to commit versus leave flexible, based on how confident you are in your own volume. **This is the specific thing the problem statement asks for** — moving from many one-off purchases to sensible term contracts.

**How much to hedge.** There is a financial contract that pays out if freight prices rise. We size it. Honestly, though — see the reliability section, because this one comes with a real asterisk.

**What to do when things go wrong.** Ship is going to arrive early, or the port is congested, or a cyclone is coming. Wait at anchorage? Slow the ship down to burn less fuel and arrive later? Divert to a different port? Unload part of the cargo offshore? Each of these has a cost. We compare them.

**A paper trail.** Every recommendation stored permanently with the exact data and code version that produced it, and every single number clickable through to where it came from. This sounds boring. It is the reason a government-owned company could actually use this, because procurement decisions have to be defensible to auditors. It's also the reason we can prove afterwards whether we were right.

---

## 6. How the AI part works — and the one rule that matters most

We use Gemini agents. Five of them, plus one that exists purely to attack the others.

There is a supervisor that reads the request. A market agent that explains what the rate model is saying. A port agent that checks physical feasibility. A risk agent that watches weather, cyclones and news. And then **the Critic**, whose only job is to try to destroy the recommendation before a human sees it — is this vessel actually feasible at both ends, has our accuracy degraded recently, are we betting against the market and if so why. If the Critic can't get comfortable, the product says "confidence low, escalate to a human broker" instead of pretending.

**And now the rule. The language models are not allowed to produce a number. Not one digit.**

Every figure — every rate, tonnage, day count, cost — comes out of ordinary Python code that we wrote and unit-tested. The AI's job is to gather information, reason about context, argue, and write clear English. The arithmetic is never its job.

Why this matters so much: language models generate plausible text, and a plausible-sounding wrong number is the single most dangerous output this product could produce. In procurement, one confident wrong number and nobody trusts the tool again. So we don't rely on the model behaving well — we make it structurally impossible. There's an automated check that fails the build if any model output contains a digit.

This is good engineering, it's our honest answer when a judge asks "how do we know the AI didn't hallucinate this," and it's a slide. Do not disable that check to make a test pass.

---

## 7. How we prove it works — the only number that counts

Not accuracy. Not R². **Money.**

Take real history. Run three buyers through it:

1. **The naive buyer** — fixes on the day the plant asks. This is roughly what happens today.
2. **Us** — follows the reservation rate.
3. **The oracle** — has perfect hindsight and always picks the cheapest day in the window. Impossible, but it tells you the maximum available prize.

Then: what share of the gap between naive and oracle did we capture? That's the **capture ratio**. "We captured about half of the timing value that was theoretically on the table" is a sentence a CFO can act on and a judge can't wave away, because it openly admits perfection is unreachable.

Two rules around it, non-negotiable. Test on data the model has never seen, moving forward through time the way real life does — never let the model peek at the future, even accidentally, and we have an automated test that fails the build if it does. And **always show the worst quarter next to the average.** An average saving that hides one catastrophic quarter is a lie.

---

## 8. How reliable is this, honestly

Four tiers. Know which tier you're standing on when you speak.

**Rock solid — the physics and the voyage arithmetic.** Whether a ship fits, how much it can load at a given depth, what a voyage costs, how demurrage accrues. This is arithmetic with unit tests. If a Capesize can't enter Haldia, that's a fact about the world, not a forecast. We can defend every digit. *This is where most of our real value lives, and it's why it's built first.*

**Sound method, unproven result — the timing policy.** The mathematical technique is standard and respected, used widely in finance for exactly this kind of "act now or wait" problem. Applying it to freight buying is a legitimate contribution. **But whether it makes money in this particular market is an open question until our backtest answers it.** It might come back weak. Plan for that now: if the timing edge is small, the physics and the hedging still create value on their own, and we say so rather than massaging the number. A team that reports a disappointing result honestly looks far better than one caught inflating a good one.

**Approximate, and it's our biggest weakness — the rate data itself.** The authoritative daily price for a specific route like Australia-to-Paradip is sold by subscription for tens of thousands of dollars a year. We don't have it and we will not steal it. So we build the rate series from free public signals plus a calibrated statistical model, anchor the levels to real quarterly earnings figures that shipowners publish in their filings, and **badge every simulated number visibly in the interface.** When asked, the answer is: "that series is modelled, here's what it's calibrated against, and a licensed feed is a line item in our funding plan — it's a purchase, not a rebuild." Never let a simulated number be presented as observed. That's the one mistake we can't recover from.

**Being fixed right now — some facts.** Port depths, handling rates, cost conventions. Several are now verified from primary sources with URLs recorded; the rest are in a blocking checklist. Rule: **"unknown" is an acceptable answer, a guess is not.** If you need a number that isn't verified, leave it as `unknown` and let the code refuse to compute rather than quietly inventing something.

### Four things we have decided in advance never to claim

Written down now so nobody improvises under pressure on stage:

We will not claim to beat the forward market at long horizons. We will not quote a saving without its worst case beside it. We will not show a simulated number as if it were observed. We will not state a confidence percentage we haven't actually measured for accuracy.

Pre-committed answers to the four hardest questions are worth more than any extra feature.

---

## 9. The one thing each of you must not get wrong

**ML pair** — you are not building a price predictor, you are building a decision policy and honest uncertainty bands. If you find yourself optimising forecast accuracy, stop and reread section 3. And guard the leakage test like your life depends on it; a backtest with a peek at the future is worse than no backtest, because it's confidently wrong.

**Backend pair** — the provenance object and the no-numerals check are features, not plumbing. Build them in week one. Retrofitting an audit trail is a rewrite. Also: the system must produce a complete decision memo with the AI switched off entirely. Test that path.

**Data** — you own the verification checklist, and disproving one of our assumptions is a win, not a setback. A wrong port depth found by you in week one costs nothing; found by a judge in week five it costs everything.

**Design and pitch** — the interface must make the difference between an observed number and a modelled one obvious at a glance, without anyone explaining it. That visual distinction is the most important design decision in the project.

**Everyone** — rehearse the demo offline, from a frozen copy of the data, with the wifi switched off. Venue wifi has ended more good projects than bad code has.

---

## 10. Three sentences to memorise

Someone will corner you next to a poster and ask. Have these ready.

> **"Freight prices are near-random and a real futures market already prices them better than we could — so we don't forecast. We tell a buyer whether today's offer beats waiting, which ship can physically load full at their port, and how much of the price risk to insure."**

> **"The AI in our system is not allowed to produce a single number. Every figure comes from tested code and traces back to its source, licence and timestamp. Our build fails if a model emits a digit."**

> **"We don't measure ourselves on accuracy, we measure in dollars per tonne against what a normal buyer would have paid — and we show you our worst quarter, not just the average."**
