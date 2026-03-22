# Quick Start Guide - Running Against Kagenti Cluster

## Prerequisites

✅ kubectl configured with `kind-kagenti` context
✅ Kagenti cluster running with:
- Kagenti backend in `kagenti-system` namespace
- Keycloak in `keycloak` namespace
- `team1` namespace for deployments

## Option 1: Deploy Your Own Benchmark and Agent

If you want to deploy a fresh benchmark and agent:

### Step 1: Deploy the Benchmark (MCP Server)

Deploy an Exgentic benchmark (e.g., GSM8K):

```bash
cd exgentic_a2a_runner
./deploy-benchmark.sh gsm8k admin admin
```

This will:
- Check for the benchmark image locally
- Sync the image to the kind cluster if needed
- Deploy the MCP server via Kagenti API
- Wait for the deployment to be ready

**Note:** You need to build the benchmark image first. Use 
agent-examples/mcp/exgentic_benchmarks/build.sh to build the image locally.

### Step 2: Deploy the Agent

Deploy a generic A2A agent that will use the benchmark:

```bash
./deploy-agent.sh gsm8k admin admin
```

This will:
- Deploy the generic agent via Kagenti API
- Configure it to connect to the MCP server
- Build the agent image from source
- Wait for the deployment to be ready

### Step 3: Update Configuration

Update your `.env` file to use the deployed services:

```bash
# Update these values in .env
AGENT_SERVICE=generic-agent-internal-gsm8k
BENCHMARK_SERVICE=exgentic-mcp-gsm8k-mcp
```

### Step 4: Run the Harness

Now run the harness with the deployed services:

```bash
./run-with-port-forward.sh
```

## Option 2: Use Existing Services

If services are already deployed in the team1 namespace, you can use them directly.

### Quick Run

The easiest way to run the harness is using the provided script:

```bash
cd exgentic_a2a_runner
./run-with-port-forward.sh
```

This script will:
1. Set up port forwarding to both services
2. Test connectivity
3. Run the harness with verbose logging
4. Clean up port forwards on exit


## Configuration

The `.env` file should be configured for your deployed services:

```bash
# Service names in Kubernetes
AGENT_SERVICE=generic-agent-internal-gsm8k
BENCHMARK_SERVICE=exgentic-mcp-gsm8k-mcp

# Local endpoints (via port-forward)
EXGENTIC_MCP_SERVER_URL=http://localhost:8000/mcp
A2A_BASE_URL=http://localhost:8081

# Test configuration
MAX_TASKS=10  # Number of tasks to run
MAX_PARALLEL_SESSIONS=10  # Parallel execution
LOG_PROMPT=1  # Enable prompt logging
LOG_RESPONSE=1  # Enable response logging
```

**Important:** Note that the A2A agent now uses port 8081 (not 8080) to avoid conflicts with the kagenti-ui service.

## What to Expect

The harness will:
1. Connect to the MCP server and create a session
2. Get a task from the Tau-Bench benchmark
3. Build a prompt with the session_id
4. Send the prompt to the generic-agent2 via A2A
5. Wait for the agent to complete the task
6. Evaluate the session via MCP
7. Close the session
8. Print statistics

### Expected Output

```
2026-03-17 18:52:00 - INFO - Initializing runner components
2026-03-17 18:52:00 - INFO - Initializing OpenTelemetry instrumentation
2026-03-17 18:52:00 - INFO - Initializing Exgentic adapter
2026-03-17 18:52:01 - INFO - Creating new session
2026-03-17 18:52:01 - INFO - Processing session: session_abc123
2026-03-17 18:52:05 - INFO - Session session_abc123 completed in 4523.45ms (evaluation: success)
...
============================================================
RUN SUMMARY
============================================================
Sessions Attempted:   3
Sessions Succeeded:   3
Sessions Failed:      0
Evaluation Success:   100.0%
Total Wall Time:      15.23s
Average Latency:      5076.67ms
P50 Latency:          5000.00ms
P95 Latency:          5500.00ms
============================================================
```

## Troubleshooting

### Port Forward Issues

If port forwarding fails:
```bash
# Kill existing port forwards
pkill -f "port-forward"

# Check if ports are in use
lsof -i :8000
lsof -i :8080

# Restart port forwards
kubectl port-forward -n team1 svc/exgentic-mcp-tau2-mcp 8000:8000 &
kubectl port-forward -n team1 svc/generic-agent2 8080:8080 &
```

### MCP Connection Issues

If you see "MCP client initialization failed":
- Verify the MCP server is running: `kubectl get pods -n team1 | grep exgentic`
- Check MCP server logs: `kubectl logs -n team1 -l app=exgentic-mcp-tau2-mcp`
- Test connectivity: `curl http://localhost:8000/health` (if health endpoint exists)

### A2A Connection Issues

If you see "A2A request failed":
- Verify the agent is running: `kubectl get pods -n team1 | grep generic-agent2`
- Check agent logs: `kubectl logs -n team1 -l app=generic-agent2`
- Test agent card: `curl http://localhost:8080/.well-known/agent-card.json`

### Session Evaluation Failures

If sessions complete but evaluation fails:
- Check if the agent is using the session_id correctly in its tool calls
- Review agent logs to see what tools it's calling
- Verify the agent has access to the MCP server for tool execution

## Deployment Scripts Reference

### deploy-benchmark.sh

Deploys an Exgentic MCP benchmark server:

```bash
./deploy-benchmark.sh <benchmark-name> [keycloak-username] [keycloak-password]
```

**Arguments:**
- `benchmark-name`: Name of the benchmark (e.g., gsm8k, tau2)
- `keycloak-username`: Keycloak admin username (default: admin)
- `keycloak-password`: Keycloak admin password (default: admin)

**What it does:**
1. Checks for local benchmark image
2. Syncs image to kind cluster if needed
3. Authenticates with Keycloak
4. Deploys MCP server via Kagenti API
5. Waits for deployment to be ready

### deploy-agent.sh

Deploys a generic A2A agent:

```bash
./deploy-agent.sh <benchmark-name> [keycloak-username] [keycloak-password]
```

**Arguments:**
- `benchmark-name`: Name of the benchmark the agent will use
- `keycloak-username`: Keycloak admin username (default: admin)
- `keycloak-password`: Keycloak admin password (default: admin)

**What it does:**
1. Authenticates with Keycloak
2. Fetches agent environment configuration
3. Configures agent to connect to the MCP server
4. Deploys agent via Kagenti API (builds from source)
5. Waits for build and deployment to complete

## Next Steps

After successful test run:
1. Increase `MAX_TASKS` in `.env` for longer runs
2. Enable OTLP exporter for telemetry collection
3. Deploy different benchmarks and test with various agents
4. Analyze results and agent performance
5. Access kagenti-ui at http://kagenti-ui.localtest.me:8080/ to monitor deployments

## Support

For issues:
- Check logs with `--verbose` flag
- Review agent and MCP server logs in Kubernetes
- See main README.md for detailed documentation