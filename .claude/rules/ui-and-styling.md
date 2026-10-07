# UI and Styling

## Styling engine
`frontend/` uses one stylesheet, `frontend/styles.css`, with CSS variables. Do not add a CSS
framework or a build step, and do not use inline styles except for computed values
(gauge offset, metric bar widths).

## Design tokens
- Colors are tokens on `:root`, redefined under `@media (prefers-color-scheme: dark)`.
- Severity colors are fixed: `--critical`, `--high`, `--medium`, `--low`, `--info`, each with
  a `-bg` pair. Reuse them for every severity indicator (pills, finding borders, line tints).

## Layout
- Works from 375px to wide desktop with no horizontal page scroll.
- The code viewer may scroll horizontally inside its own box.

## Safety
- Report data is untrusted model output: render it with `textContent`, never `innerHTML`.
