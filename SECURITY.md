# Security Policy

## Scope

This repository is a research and engineering prototype. It is not currently represented as a production security control, safety filter, or certified security product.

Security reports are welcome for vulnerabilities affecting:
- executable code in the repository;
- dependency and build configuration;
- CI workflows and repository automation;
- handling of interaction traces or evidence;
- candidate generation, testing, or review boundaries.

## Reporting

Please do not publish credentials, access tokens, private interaction traces, or exploitable details in a public issue.

Use GitHub's private vulnerability reporting feature for this repository when it is enabled. If private reporting is unavailable, contact the repository owner through the contact method published on the GitHub profile and provide:
- affected version or commit;
- affected file/component;
- reproduction steps;
- impact and realistic attack conditions;
- any suggested mitigation.

Do not include secrets or personal data in the report.

## Response expectations

This is an independently maintained research project. A response or remediation timeline is not guaranteed. Reports will be triaged according to reproducibility, severity, affected scope, and available maintainer capacity.

## Security limitations

Until separately implemented and assessed, do not assume the project provides:
- sandboxing for generated candidate code;
- durable or tamper-evident storage of all evidence;
- distributed access control;
- production-grade secrets management;
- provider-side isolation;
- a security certification or compliance attestation.

Security findings and mitigations must be documented without implying that a research prototype is production-hardened.
