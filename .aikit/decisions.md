# Decisions

Why this project is built the way it is, oldest first. One entry per decision that changes a
contract, a dependency, a data format or the architecture; IDs are consecutive and never reused.

<!-- Entry format:
### ADR-NNN: <decision in one line>
- **Date**: YYYY-MM-DD
- **Status**: Accepted
- **Context**: <what forced the decision>
- **Decision**: <what was decided>
- **Consequences**: <what follows, including what it costs>
-->

## Licensing migration (mit-final)

- New versions use the Aegean License 1.1 (AL-1.1); versions up to and including `mit-final` remain under the MIT License.
- Rights holder: AegeanWorks; commercial use under ACL-1.0.
- Counsel review of the 1.1 texts remains pending.

## License notice cleanup (2026-10-26)

- The license-history notes and the old-license boundary tag were removed: the project is offered only under the Aegean License 1.1 (AL-1.1), with commercial use under ACL-1.0.

### ADR-001: Push-window audit 1->End and clinical-safety corrections
- **Date**: 2026-11-07
- **Status**: Accepted
- **Context**: The goal asks for cumulative push-to-push verification, starting at the 1->3 window and expanding through 1->6, 1->9 and onward until the first commit is covered. Reforge run-1 had already recorded windows 3 through 45 (newest first); the five pushes added after that run and several current-content gaps were still unaudited.
- **Decision**: Complete the audit at the 1->50 window, treating the reforge stage windows as the cumulative evidence trail. Apply the findings that survive at HEAD rather than editing historical commits: the LP note no longer prescribes routine prolonged supine rest or caffeine as primary therapy, the optic-neuritis text no longer calls a central scotoma atypical, the IIH text no longer links CN VI palsy to permanent vision loss, headache red-flag and autonomic claims are evidence-bounded, routine-test and follow-up fields are made indication-based, every explanation file carries key sources, and the README distinguishes template use from the Python test runtime. Add failing-first-style regression pins for each corrected surface.
- **Consequences**: All 50 commits now have a recorded review window; the clinical wording is more cautious and better sourced; 14 project tests and all four AIKit gates pass before the push. Historical commits remain untouched, so the audit is reproducible from the window ledger rather than a rewrite.
