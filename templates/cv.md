---
# CV format for scripts/export_cv.py. Front matter is optional; without it the
# body starts with your own "# Name" heading.
name: YOUR NAME
header:
  # The first item is the title line under the name (HTML allowed).
  - text: <Target Title> | <Focus>
  # Contact items get an icon chosen from the text or link
  # (mail, phone, GitHub, LinkedIn, other links).
  - text: <City, Country>
    newLine: true      # start a new line before this item
  - text: you@example.com
    link: mailto:you@example.com
  - text: GitHub
    link: https://github.com/<user>
  - text: LinkedIn
    link: https://www.linkedin.com/in/<user>/
---

<!-- Notes for the agent stay in HTML comments; they are not printed. -->

## Summary

Two to four sentences: role, years, focus, and what you bring.

## Skills

- **Area:** tool, tool, practice
- **Area:** tool, tool, practice

## Experience

### <Company>

<Role Title>
: MM/YYYY - MM/YYYY

- What you did and the result, in general terms (no confidential details).
- One idea per bullet.

### <Earlier Company>

<Role Title>
: MM/YYYY - MM/YYYY

- ...

<!-- A line with only \newpage forces a page break here. Use it only when the
     automatic break looks wrong in the previews. -->

## Education

<Degree>, <School>
: YYYY

## Certifications

- <Certification>, <Year>
