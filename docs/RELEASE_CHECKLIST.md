# Release and submission checklist

The student demo is published at [NextStep Scholarships](https://nextstep-scholarships.replit.app/) and the public repository uses `main`. See [build status](BUILD_STATUS.md) for recorded validation; this checklist does not claim that the course submission has been sent.

## Before submitting

- Open the published app and confirm it loads without student sign-in.
- Confirm the repository and Google submission document are accessible to instructors.
- Add the recorded video link to the submission document and check its sharing permissions.
- Describe evaluation results with their corpus, test-set size, and limitations; do not present tuning results as independent accuracy.
- Keep provider keys in server-side secrets. Hosted admin remains disabled; evaluations run locally.

## Future code releases

Run the checks in the [README](../README.md), review the diff, and verify the active corpus before publication. After publishing, check matching, chat citations, and printing. Documentation-only updates do not require republishing Replit.

Corpus rollback uses `uv run python -m nextstep.ingest.cli rollback --version PREVIOUS_READY_VERSION` with the intended database selected and a retained, query-ready version. Do not delete the previous namespace as part of a release.
