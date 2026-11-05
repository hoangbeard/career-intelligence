# Job report: Globex Cloud / Application Security Lead

> **Job ID:** JOB-2026-001 · **Job Name:** `globex-cloud/2026-10-application-security-lead`

## Decision Card

**Apply** · Overall Match 82/100 (Strong fit) · Career Acceleration 88/100 (Strong career value)

Application Security Lead · Ho Chi Minh City, hybrid (two office days) · Lead, hands-on programme owner · Role mix 85/15 vs 70/30

Main reason: direct evidence in CI/CD security gates and threat modeling, with broader AppSec ownership and a published range above the floor.

### Company (fictional, details in `jobs/globex-cloud/company.md`)

| Item | Summary | Source · confidence |
|---|---|---|
| Overview | API management SaaS, about 600 staff, HQ Singapore, hubs in Ho Chi Minh City and Warsaw | Company file · low (fictional) |
| Finance and business | Series C; no revenue or profit figures | Company file · low (fictional) |
| Employee reviews | `not checked`: the company is fictional | — |
| Hiring activity | `not checked`: the company is fictional | — |
| Pay range | USD 5,500–7,000 monthly gross plus 13th month; midpoint meets the USD 72,000 target | JD · high |
| Interview process | `not checked`: the company is fictional | — |
| Leadership | `not checked`: the company is fictional | — |
| Controversies | `not checked`: the company is fictional | — |

### Job fit

| Area | Matches | Gaps |
|---|---|---|
| Technical must-haves | CI/CD security gates, threat modeling (STRIDE) | AppSec tenure, code review languages and ASVS depth are partial |
| Technical nice-to-haves | AWS security | Kubernetes partial; bug bounty and SOC 2 missing |
| Soft skills | Technical leadership through a champions group | Formal mentoring or line management not documented |

**Direction:** serves Application Security Lead best (9/10) and also Security Architect (8/10). Compliance at 15% is within the user's preference.

**Growth in 2–3 years:** threat modeling at scale and cross-team guardrails; realistic exits are AppSec Lead or Senior Cloud Security, and Security Architect if design authority is real.

### Decision

**Why chase:** strong match to the cloud security and DevSecOps direction; broader AppSec ownership across 12 teams; pay above the USD 60,000 floor.

**Risks:** authority across teams is unclear; AppSec tenure and review languages are not fully evidenced; company facts cannot be verified.

**Next:** ask about languages, who owns security gates, and whether the 13th month is guaranteed · study ASVS mapping, secure code review for the main stack, Kubernetes supply chain security · lead the CV with CI/CD gates and AWS guardrails

---

## Evidence

### Requirement Match Matrix

| Requirement | Must/Nice | Evidence (company, year) | Match | Action |
|---|---|---|---|---|
| 6+ years in software engineering or security; 3+ in AppSec | Must | Vandelay, 2018–2022; Initech, 2022–2026; relevant security work spans roughly 4.5 years, but 3 years specifically in AppSec is not established | Partial | Present the security and secure development timeline accurately; clarify how Globex defines AppSec experience |
| Hands-on threat modeling (STRIDE or similar) | Must | Initech, 2026: STRIDE used in service/change reviews | Strong | Include STRIDE work; prepare a concise method example without confidential details |
| Build security gates in CI/CD | Must | Initech, 2022–2026: SAST, dependency and container scans with severity gates across 60 repos | Strong | Lead with this result |
| OWASP Top 10 and ASVS | Must | Vandelay, 2022: ASVS checklist in web feature reviews | Partial | Review current ASVS and Top 10 before interview; do not imply broad mastery beyond evidence |
| Secure code review in Go, Java or TypeScript | Must | Vandelay, 2022: web feature security reviews; language not documented | Partial | Clarify languages reviewed; do not list a language without confirming evidence |
| Lead or mentor engineers | Must | Initech, 2022–2026: ran champions group of 8 engineers | Partial | Emphasize technical leadership and peer enablement; be clear that formal line management is not documented |
| AWS and Kubernetes security | Nice | Initech, 2022–2026: AWS security across 40 accounts; Kubernetes security familiar, last used 2025 | Strong (AWS); Partial (Kubernetes) | Highlight AWS; refresh Kubernetes security fundamentals |
| Bug bounty programme management | Nice | No evidence in work history | Missing | Ask about existing programme and prepare a triage approach; do not claim ownership |
| SOC 2 experience | Nice | Vandelay, 2021: technical evidence support for ISO 27001; no SOC 2 evidence | Missing | Position adjacent evidence accurately; ask how much of the stated 15% is evidence collection |

### Soft skills

| Skill | Signal in JD | Evidence (company, year) | Match |
|---|---|---|---|
| Mentoring | Mentor two AppSec engineers | Initech, 2022–2026: ran champions group of 8 engineers; no formal line management | Partial |
| Cross-team influence | Programme across 12 product teams | Initech, 2022–2026: champions group and security gates across 60 repositories | Strong |

### CV positioning

- Headline: Senior Cloud Security Engineer | Application Security & DevSecOps
- Emphasise (recent work): CI/CD scanning gates across 60 repositories, AWS guardrails across 40 accounts, STRIDE reviews, champions group of eight.
- Do not claim: Formal management of engineers, SOC 2 ownership, bug bounty ownership, or specific Go/Java/TypeScript code review absent confirmation.
- CV file: `artifacts/cv.md`.

### Pay

| Component | Value | Quality |
|---|---|---|
| Base salary | USD 5,500–7,000/month gross (USD 66,000–84,000/year if paid for 12 months) | Stated in JD |
| Bonus | 13th-month salary; estimated total cash USD 71,500–91,000 if it is one additional full monthly salary | Stated, but guarantee and calculation basis need confirmation |
| Equity | Not stated | Unknown |
| Insurance | Private health insurance | Stated in JD |
| Learning support | USD 1,000 yearly budget | Stated in JD |
| Flexibility | Hybrid, two days in office | Stated in JD |
| Total package (yearly) | USD 71,500–91,000 including assumed 13th month; excludes unpriced benefits | Conditional estimate based on JD |

Negotiation notes: The user's stated floor is USD 60,000/year and target is USD 72,000/year. A reasonable target is USD 6,000–7,000 monthly gross plus a guaranteed 13th-month salary, given the lead scope. Confirm whether base is paid for 12 or 13 months, the guarantee and eligibility rules, and whether benefits are additional. Ask about additional annual leave, certification support, and remote flexibility.

### Career

| Target role | Contribution /10 | Reason |
|---|---:|---|
| Senior Cloud Security Engineer | 8 | AWS guardrails and pipeline controls remain core, with wider application scope. |
| Application Security Lead | 9 | Direct programme ownership, threat modeling, code review, champions, and mentoring align closely. |
| Security Architect | 8 | Cross-team guardrails and threat modeling build architecture influence; decision rights need confirmation. |

Skill capital: Threat modeling at scale—high growth; Kubernetes security—moderate growth; security architecture—high growth, conditional on meaningful design authority.

| Area | Score /10 | Notes |
|---|---:|---|
| Resume value | 8 | Multi-team AppSec programme ownership would broaden current cloud security profile. |
| Industry reputation | 6 | Fictional company; cannot verify market reputation. |
| Recruiter demand | 8 | AppSec, cloud security, and DevSecOps leadership combine relevant skills. |
| Pay growth potential | 8 | Range exceeds current package and stated floor; 13th-month details need confirmation. |

Exit options after 2–3 years: Application Security Lead (high likelihood); Senior/Lead Cloud Security Engineer (high); Security Architect (medium-high if design ownership is real).

Opportunity cost: Could shift time from hands-on engineering to programme coordination; compliance is stated at 15%, within the user's preference, but scope may expand. Formal management expectations may exceed documented experience.

### Risks

| Risk | Level | Why it matters | Mitigation |
|---|---|---|---|
| Authority unclear across 12 teams | Medium | Programme ownership without release or design influence can become advisory-only | Ask who owns security gates and how exceptions are decided |
| Mentor expectation exceeds documented management | Medium | Role includes mentoring two engineers; work history only supports champions leadership | Explain leadership scope honestly and ask whether direct reports are involved |
| AppSec depth/language mismatch | Medium | 3+ years AppSec and one named language are not fully evidenced | Clarify language and quantify relevant work accurately |
| Compliance scope creep | Low-Medium | SOC 2 evidence could expand beyond the stated 15% | Ask for expected deliverables and time split |
| Company information cannot be verified | Medium | Existing records identify Globex as fictional | Treat employer and market ratings as provisional |

### Sources and assumptions

- Work history verified: true
- JD: `source.md`, supplied example; found on the Globex careers page on 2026-10-15 per user.
- Career profile: `profile/career-profile.md`; work evidence: `profile/work-history/initech.md` and `profile/work-history/vandelay.md`.
- Role mix estimate: 85% security engineering/programme delivery and 15% compliance, inferred from listed responsibilities.
- Match scoring uses the profile weights: requirement match 40%, role mix 20%, seniority 15%, company quality 15%, pay 10%. The role mix passes the user's governance threshold; overall match is reduced for language-specific code review and AppSec tenure uncertainty.
- Career acceleration reflects target role contribution, skill growth, ownership potential, resume value, pay, and uncertainty about company facts.
