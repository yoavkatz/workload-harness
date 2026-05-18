# Kagenti Workload Harness

This repository contains workload harnesses for driving test and evaluation traffic to Kagenti agents.

## Current Scope

- **AppWorld harness** (`appworld_a2a_runner/`) — the first supported workload driver.
- **Exgentic harness** (`exgentic_a2a_runner/`) — drives Exgentic benchmarks (tau2, gsm8k, appworld) against Kagenti agents via A2A protocol.
- Designed to expand to additional workload drivers over time.

## Purpose

The workload harness exists to robustly exercise agents and validate that the Kagenti platform is:

- Reliable
- Scalable
- Observable

## Observability

Tracing is powered by **MLflow** via an OpenTelemetry Collector that forwards OTLP traces to the MLflow `/v1/traces` endpoint. This replaces the previous Phoenix-based tracing setup.

- The runner emits OpenTelemetry spans and metrics over gRPC.
- An OTEL Collector in the cluster routes traces to MLflow with the appropriate experiment ID and OAuth2 authentication headers.
- Pass `--mlflow` to `evaluate-benchmark.sh` or `deploy-and-evaluate.sh` to enable tracing with automatic port-forwarding.
- Prometheus metrics are collected for infrastructure-level pod resource usage.

See [`exgentic_a2a_runner/README.md`](exgentic_a2a_runner/README.md) for detailed configuration.
