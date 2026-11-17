---
title: "Why Rules Change on the Ground: Frontline Workers and Real Policy"
date: 2026-11-17T00:00:00Z
draft: true
translationKey: why-rules-change-on-the-ground
description: "How frontline discretion, resources and feedback change formal rules in practice."
tags: [governance, institutions, feedback]
---

> Source note: the examples and diagrams illustrate possible mechanisms, not measured universal effects. Simon's lecture and Lewis and Aligica's article were checked against available texts; Lipsky and Brehm and Gates were checked against publishers' descriptions, Taylor and Kelly against the authors' abstract. Applying conclusions across government, companies and platforms requires separate testing.

> By the end, you should be able to distinguish a rule on paper from a frontline worker's decision, understand why a government, company or platform cannot govern solely through orders from above, and use a simple card to examine the gap between goal, instruction, action and result.

The practical point: no one can specify every situation in advance, but boundaries for departures can be set. A local decision is useful when it draws on available information, has a recorded reason and can be reviewed; hidden discretion without appeal raises the risk of arbitrary action.

## Map of the article

A manager can make a good decision and write clear instructions yet obtain a different result. Several transitions stand between the centre and the person facing a client, patient, pupil, driver or employee:

```text
goal from above
→ formal rule
→ resources, queue and workload
→ local interpretation
→ frontline decision
→ actual service or sanction
→ complaint, data and rule change
```

A short guard against confusion:

```text
rule ≠ instruction ≠ decision ≠ implementation ≠ outcome
```

## Why the centre cannot decide everything in advance

An organisation encounters more cases than one document can describe. Information is distributed: a doctor sees a patient's condition, an inspector the particular situation, a shift manager the queue, and a moderator a message's context. The centre can set goals and limits but cannot see every detail at the moment of action.

Herbert Simon described bounded rationality: people and organisations cannot collect all information, calculate every option and find a globally best answer. They divide decisions among specialists, create subgoals and build structures of communication and authority to cope with complexity and uncertainty ([Simon, Nobel lecture *Rational Decision-Making in Business Organizations*](https://www.nobelprize.org/uploads/2018/06/simon-lecture.pdf)). The lecture presents a general decision theory, not a quantitative assessment of a particular service.

The practical question is not how to eliminate local decisions. It is where they are permitted, what limits them, how reasons are recorded and who can review an error.

## Frontline workers are part of the governance system

Michael Lipsky called workers who interact directly with people and have substantial discretion street-level bureaucrats: social workers, police officers, teachers, doctors and other public-policy implementers. Demand often exceeds resources, agency goals can be unclear and cases differ. These workers do more than “implement” policy: their everyday decisions shape how citizens experience it ([Lipsky, *Street-Level Bureaucracy*](https://www.russellsage.org/publications/book/street-level-bureaucracy)).

A similar mechanism exists outside government:

| Where | Formal rule | Where discretion appears |
|---|---|---|
| Public service | eligibility criteria for assistance | interpreting incomplete documents, urgency and exceptions |
| Hospital | protocol and queue order | whom to see first, when to call an expert |
| Corporation | KPI, instructions and budget | which cases are complex, who receives resources and time |
| Platform | moderation rules | interpreting context, irony, threats and repeat violations |
| Closed group | doctrine, ritual and routine | who receives an exception, how doubt and sanctions are interpreted |

Discretion is not necessarily arbitrariness; it can use local knowledge. Risk arises when decision authority is hidden, unequally distributed, unrecorded and lacks independent appeal.

## Where the gap between plan and practice comes from

### Resource shortages

If applicants outnumber places, a worker must allocate scarcity. They may accelerate simple cases, defer difficult ones, shorten conversations or create informal criteria. Even a conscientious person may begin using rules absent from the central document.

### Unclear or conflicting goals

“Help everyone,” “cut costs,” “avoid risk” and “prevent queues” may be impossible to achieve simultaneously. The worker chooses a priority; a report may show one indicator even though the job involved several conflicting tasks.

### The signal does not reach the top

A worker knows what failed but may not report it if bad news invites a sanction. The centre sees formal compliance and mistakes it for actual performance: a bureaucratic mirage in which documents look uniform while people's local experiences differ.

### Professional norms and social pressure

Decisions depend on more than the supervisor. Colleagues, clients, professional ethics, fear of conflict and local reputation also influence behaviour. One study of bureaucratic behaviour combines models, surveys, observations and administrative records. According to the publisher's description, job characteristics and the influence of colleagues and clients are among the reasons for employee effort, while the authors give supervisors' coercive capacity a smaller role. This is the publisher's account; the full book was not read ([Brehm and Gates, *Working, Shirking, and Sabotage*](https://press.umich.edu/Books/W/Working-Shirking-and-Sabotage)).

This does not make control useless; it means “add supervision” is not a diagnosis. A queue needs resources and priorities; conflicting goals need a changed mandate; deliberate appropriation calls for audit and sanctions; a weak signal needs safe feedback.

## Governance is a loop, not an order

A systems view asks what happens after a rule is applied. Action changes the situation, the result becomes a new signal, and the next step should take it into account. If the centre receives it too late, sees only convenient indicators or lacks authority to change the rule, the loop breaks. This does not mean every local level is better than the centre: several levels may add flexibility or merely add delays and shift responsibility.

```text
FeedbackLoop = (goal, observation, delay, authority to change,
                correction, memory)
```

Check six links: whether the goal is clear, the real outcome observed, how long the signal takes to return, who can change action, whether the reason for correction is retained and whether the rule itself changes. Research on the Ostroms' self-governance and cybernetics is useful as a language for nested rules and feedback, not proof that polycentricity is universally superior ([The Ostroms on self-governance and cybernetics](https://doi.org/10.1017/S1744137424000079)).

## An everyday example: benefits, a clinic and a call centre

Imagine three organisations told to “process requests quickly and fairly.”

At an agency, a worker seeing incomplete documents decides whether to allow time for correction or refuse. At a clinic, a receptionist judges whether a complaint is urgent. At a call centre, an operator chooses between closing a ticket with a template and escalating it to an engineer. The centre may measure speed, share of cases closed and instructions followed, but local decisions determine who gets help, who waits and which problem becomes visible.

If rewards depend only on speed, one possible response is to process easy cases first, lose difficult ones, leave exceptions unrecorded and improve the metric. This illustrates a possible mechanism, not a measurement in a particular organisation. A complete ban on deviations may produce more uniform decisions but serve unusual cases worse.

The useful question:

```text
what should be the same for everyone
and where should an explainable departure be allowed?
```

## A formal implementation card

To analyse an institution, write:

```text
Implementation = (
  goal,
  formal rule,
  available resources,
  workload and queue,
  local information,
  authority to depart,
  professional norm,
  pressure from colleagues and clients,
  monitoring,
  reason for decision,
  appeal,
  exit,
  observed outcome
)
```

Useful metrics:

```text
ImplementationGap = distance(formal rule, observed practice)
DiscretionRate = share of cases with several permissible actions
ReasonCoverage = share of decisions with a recorded, verifiable reason
AppealCorrection = corrected decisions / appeals considered
EquityGap = difference in outcomes between comparable groups
QueuePressure = demand / available capacity
```

For `ImplementationGap`, first code rule and practice on one common, predefined compliance scale. Otherwise it is a useful name for a gap, not a numerical metric.

This is not one rating of a worker. The metrics answer different questions. High `ReasonCoverage` does not guarantee a fair reason; low `DiscretionRate` may mean a clear rule or fear of departure; high `AppealCorrection` may show a good correction channel or poor initial decisions.

## Design implementation, not just the order

### 1. Separate boundaries from room for judgment

Write down what cannot be violated: a ban on violence, minimum response time, necessary conflict-of-interest controls and a basic right to an explanation. Alongside, state where departures are permitted and which facts justify them. “Act according to the situation” is too vague; “never depart” often breaks the work.

### 2. Give local decisions resources

Discretion without time, data and access to an expert becomes a lottery. A worker needs clear escalation, access to context, realistic workload and the ability to pause a dangerous action.

### 3. Record the reason, not just the result code

“Refused” does not show what happened. A minimum record should say which fact was seen, which rule applied, why an exception was chosen and who reviews a disputed case. This protects both participant and worker.

### 4. Separate help, monitoring and sanctions

One person should not simultaneously allocate resources, assess their own work, punish dissent and hear a complaint. Separating roles reduces the risk of a worker hiding an error to preserve status.

### 5. Measure outcomes on the ground

Check not only procedure but the recipient's experience, repeat contact, delay, exceptions, distribution of errors between groups and share of decisions corrected. Otherwise the centre rewards attractive reporting.

## Who owns real policy?

Formal power may sit with a ministry, board or platform owner. Real power partly belongs to whoever:

```text
sees a case → interprets a rule → chooses an exception
→ starts a sanction or service → explains the decision
```

But the worker is not always free: resources, career evaluation, queues, colleagues and clients constrain them. Draw a map of constraints as well as an organisation chart: who can refuse, hide a signal, check a record and review a decision?

This links street-level bureaucracy to earlier themes: in government, the gap between capacity and service quality; in a firm, KPI and actual outcomes; on a platform, moderation rules and context; in a closed group, doctrine and exceptions for a leader.

## Counterexample: a uniform rule can be better than discretion

Suppose an organisation allocates scarce resources and workers are biased or sell exceptions. More freedom for them would worsen equality. A standard criterion, random queue, external audit and equal appeal may outperform local judgment, even while losing some context.

The conclusion is not “always trust the worker.” Compare two costs:

```text
cost of a blind rule
vs.
cost of a hidden and unequal exception
```

Where error is costly, independent review, a second decision, a temporary mandate and authority to stop action are useful. Where small errors are reversible, more autonomy and learning from outcomes may be appropriate.

## Conclusion

Governing a large group does not end when an order is written. It ends in the particular decision by a person or system facing a real case. A good institution combines:

```text
clear boundary
+ local knowledge
+ resources for implementation
+ explainable discretion
+ independent appeal
+ outcome measurement
+ safe exit
```

A complete ban on discretion may reduce the ability to respond to unusual cases. Leaving it invisible gives power to whoever interprets the rule on the ground and denies others a way to check the decision.

## Evidence notes

| Claim | Source / evidence | Confidence | Qualification |
|---|---|---|---|
| Organisations decide with limited information and computational capacity, dividing work among specialists and communication structures | [Simon, Nobel lecture](https://www.nobelprize.org/uploads/2018/06/simon-lecture.pdf) | theoretical framework; lecture section on bounded rationality | Not a quantitative assessment of any particular hierarchy |
| Frontline workers shape public policy through everyday discretion | [Lipsky, *Street-Level Bureaucracy*](https://www.russellsage.org/publications/book/street-level-bureaucracy) | classic organisational and political theory and book | Discretion varies by profession, reform and control arrangements |
| Nested levels of rules and feedback help describe self-governance in complex settings | [Lewis and Aligica, *The Ostroms on self-governance and cybernetics*](https://doi.org/10.1017/S1744137424000079) | conceptual bridge between cybernetics, polycentricity and Ostromian self-governance | Theoretical reconstruction, not a causal test that more levels always improve outcomes |
| Discretion is not explained only by supervision: publisher's description identifies job nature, colleagues and clients among influences on effort and gives supervisor coercion a smaller role | [Brehm and Gates, *Working, Shirking, and Sabotage*](https://press.umich.edu/Books/W/Working-Shirking-and-Sabotage) | models, surveys, observations and administrative records according to publisher; full book unread | Studies US public employees; transfer requires testing |
| More managerial control does not necessarily eliminate frontline dilemmas involving ambiguous goals and varied cases | [Taylor and Kelly, revisiting Lipsky](https://doi.org/10.1108/09513550610704662) | authors' abstract: critical analysis of reforms and professional literature; full text unread | Main examples are British teachers and social workers |
