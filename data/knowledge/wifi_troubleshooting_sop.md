# Corporate Wi-Fi Troubleshooting SOP

**Document ID:** SOP-NET-001
**Version:** 1.0
**Status:** Approved for POC demonstration
**Domain:** End-User Computing
**Scenario:** Employee laptop cannot connect to corporate Wi-Fi

## 1. Purpose

Provide a consistent initial troubleshooting procedure for Service Desk engineers handling corporate Wi-Fi connectivity incidents.

## 2. Initial Information Gathering

Before changing any settings, record:

* Employee's reported problem.
* Laptop asset identifier.
* Employee's location.
* Whether the issue affects one employee or multiple employees.
* When the issue started.
* Any recent password changes or laptop configuration changes.

## 3. Troubleshooting Procedure

### Step 1: Check Basic Connectivity Settings

1. Confirm that Airplane Mode is turned off.
2. Confirm that Wi-Fi is enabled.
3. Check whether the corporate Wi-Fi network name is visible.
4. Record the results before proceeding.

### Step 2: Determine the Scope

1. Ask whether other employees in the same location are experiencing the same problem.
2. If multiple employees are affected, record the affected location and number of users.
3. Escalate suspected widespread connectivity issues according to the organization's network incident procedure.
4. Do not independently declare a network outage without sufficient evidence.

### Step 3: Check Authentication

1. Ask whether the employee recently changed their password.
2. Record any authentication error displayed by the laptop.
3. Do not ask the employee to disclose their password.
4. Do not bypass corporate authentication or device security controls.
5. Escalate authentication failures that require privileged investigation.

### Step 4: Check Network Configuration

1. If permitted by the organization's endpoint troubleshooting policy, inspect the laptop's IP configuration.
2. Record the IP address and any relevant error messages.
3. If the device has an unexpected network configuration, follow the approved endpoint troubleshooting procedure.
4. Do not make changes to network infrastructure.

### Step 5: Record Findings

Document:

* Checks performed.
* Results of each check.
* Error messages observed.
* Actions taken.
* Whether connectivity was restored.

## 4. Escalation Criteria

Escalate the incident when:

* Multiple employees appear to be affected.
* Authentication requires privileged investigation.
* Device security or compliance controls may be involved.
* The issue persists after the approved initial checks.
* The next action requires permissions the Service Desk engineer does not have.

Include the troubleshooting evidence in the escalation.

## 5. Security Restrictions

Service Desk engineers must not:

* Request or record user passwords.
* Bypass authentication or device compliance controls.
* Modify network infrastructure without authorization.
* Claim that an issue is resolved without verifying connectivity.

## 6. Completion Criteria

The incident can be considered resolved when the employee confirms that the laptop connects to the corporate Wi-Fi and the engineer records the verification result.

If connectivity cannot be restored, document the evidence and follow the escalation procedure.
