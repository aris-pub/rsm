// braiid.typ — RSM's design language for Typst PDF export
// Mirrors braiid.css: same fonts, sizes, colors, spacing

// Colors (from braiid.css :root)
#let gray-900 = rgb("#3C4952")
#let gray-800 = rgb("#51636F")
#let gray-700 = rgb("#5F7186")
#let gray-100 = rgb("#EDF0F2")
#let gray-75 = rgb("#F5F7F8")
#let blue-300 = rgb("#7DCDFC")
#let blue-500 = rgb("#0E9AE9")

// Template entry point
#let braiid(
  title: none,
  authors: (),
  emails: (:),
  abstract: none,
  doc,
) = {
  // Page setup
  set page(
    paper: "a4",
    margin: (top: 30mm, bottom: 30mm, left: 25mm, right: 25mm),
    header: context {
      let pg = counter(page).get().first()
      if pg > 1 {
        set text(size: 9pt, fill: gray-800)
        if calc.odd(pg) {
          // Odd pages: title
          if title != none { title }
        } else {
          // Even pages: author
          if authors.len() > 0 { authors.join(", ") }
        }
        h(1fr)
        counter(page).display()
      }
    },
    footer: context {
      if counter(page).get().first() == 1 {
        align(center, text(size: 9pt, fill: gray-800, counter(page).display()))
      }
    },
  )

  // Body text: Source Sans 3 if available, fallback to system sans
  set text(
    font: ("Source Sans 3", "Source Sans Pro", "Noto Sans"),
    size: 11pt,
    fill: gray-900,
  )
  set par(
    leading: 0.65em,   // ~1.5 line-height
    justify: true,
    first-line-indent: 0pt,
  )

  // Section numbering
  set heading(numbering: "1.")

  // Headings: Montserrat, matching braiid.css scale
  show heading.where(level: 1): it => {
    set text(font: ("Montserrat", "Source Sans 3", "Source Sans Pro", "Noto Sans"), size: 22pt, weight: "bold")
    v(1.5em)
    if it.numbering != none { counter(heading).display(it.numbering) + [ ] }
    it.body
    v(0.5em)
  }
  show heading.where(level: 2): it => {
    set text(font: ("Montserrat", "Source Sans 3", "Source Sans Pro", "Noto Sans"), size: 19.25pt, weight: "semibold")
    v(1.2em)
    if it.numbering != none { counter(heading).display(it.numbering) + [ ] }
    it.body
    v(0.4em)
  }
  show heading.where(level: 3): it => {
    set text(font: ("Montserrat", "Source Sans 3", "Source Sans Pro", "Noto Sans"), size: 16.5pt, weight: "medium")
    v(1em)
    if it.numbering != none { counter(heading).display(it.numbering) + [ ] }
    it.body
    v(0.3em)
  }
  show heading.where(level: 4): it => {
    set text(font: ("Montserrat", "Source Sans 3", "Source Sans Pro", "Noto Sans"), size: 15.125pt, weight: "medium")
    v(0.8em)
    if it.numbering != none { counter(heading).display(it.numbering) + [ ] }
    it.body
    v(0.3em)
  }

  // Code blocks
  show raw.where(block: true): it => {
    set text(font: "Source Code Pro", size: 9.5pt)
    block(
      fill: gray-75,
      inset: 10pt,
      radius: 4pt,
      width: 100%,
      it,
    )
  }
  show raw.where(block: false): set text(font: "Source Code Pro", size: 10pt)

  // Block quotes (used for theorem/proof divs from Pandoc)
  show quote: it => {
    block(
      stroke: (left: 3pt + blue-300),
      inset: (left: 12pt, top: 4pt, bottom: 4pt),
      it.body,
    )
  }

  // Links
  show link: set text(fill: blue-500)

  // Title block
  if title != none {
    set par(justify: false)
    text(font: ("Montserrat", "Source Sans 3", "Source Sans Pro", "Noto Sans"), size: 24pt, weight: "bold", title)
    v(0.8em)
  }

  if authors.len() > 0 {
    for author in authors {
      text(size: 12pt, weight: "semibold", author)
      if author in emails {
        text(size: 10.5pt, fill: gray-800, [ — #link("mailto:" + emails.at(author))[#emails.at(author)]])
      }
      linebreak()
    }
    v(0.5em)
  }

  if abstract != none {
    v(0.5em)
    text(font: ("Montserrat", "Source Sans 3", "Source Sans Pro", "Noto Sans"), size: 11pt, weight: "semibold", "Abstract")
    v(0.3em)
    block(
      inset: (left: 16pt, right: 16pt),
      text(size: 10.5pt, abstract),
    )
    v(1em)
  }

  doc
}
