# Requirements Document

## Introduction

A web-based Poisson calculator using a browser/server (B/S) architecture. A FastAPI backend exposes REST API endpoints for validation and computation. A separate static frontend (plain HTML/CSS/JS) calls those endpoints and presents results. Users specify a time range (with timezone support), a window duration, and an observed probability. The calculator computes how many times per year an equivalent event occurs using the Poisson distribution, returning intermediate calculation steps for transparency. The architecture should accommodate additional calculation modes in the future.

## Glossary

- **Backend**: The FastAPI server application that exposes REST API endpoints for input validation and Poisson computation.
- **Frontend**: The static HTML/CSS/JS client served as a single page that communicates with the Backend via REST API calls.
- **API**: The set of REST endpoints exposed by the Backend for performing calculations and validations.
- **Calculator**: The combined system of Frontend and Backend that performs all user-facing computations and interactions.
- **Time_Range**: A pair of timestamps (start and end) that defines the observation period over which event data is considered.
- **Timestamp_Selector**: A UI control in the Frontend that allows the user to pick a specific date and time, including timezone selection and a "Now" shortcut.
- **Window**: A duration specified in days and/or hours that represents the size of a sliding observation window within the Time_Range.
- **Probability**: A user-provided percentage (0–100 exclusive) representing the observed likelihood of at least one event occurring within the given Window.
- **Annualized_Frequency**: The computed number of times per year an event is expected to occur, derived from the Poisson distribution using the provided Probability and Window.
- **Poisson_Distribution**: A discrete probability distribution expressing the probability of a given number of events occurring in a fixed interval, assuming events occur independently at a constant average rate. The key relationship used is: P(at least 1 event in window) = 1 − e^(−λ), where λ is the expected number of events in the window.
- **Lambda (λ)**: The expected number of events in a given Window, derived by inverting the Poisson CDF: λ = −ln(1 − Probability).
- **Calculation_Steps**: The intermediate results returned by the API for each computation, including Lambda, Window in hours, and the scaling factor used to annualize.
- **Mode_Selector**: A UI control that allows the user to choose between different calculation modes (only Poisson mode is supported initially).
- **Auth_Token**: A UUID (Universally Unique Identifier) string assigned to each user, used to authenticate API requests to the Backend.
- **Token_Store**: A plain-text flat file on the server that contains all valid Auth_Tokens, one per line.

## Requirements

### Requirement 1: Time Range Input

**User Story:** As a user, I want to specify an observation time range using two timestamp selectors with timezone support, so that I can define the period over which event data is considered.

#### Acceptance Criteria

1. THE Frontend SHALL display two Timestamp_Selectors labeled "Start" and "End" for defining the Time_Range.
2. WHEN a user interacts with a Timestamp_Selector, THE Frontend SHALL allow selection of a date, time, and timezone.
3. WHEN the user selects the "Now" option on the Start Timestamp_Selector, THE Frontend SHALL set the Start value to the current date and time in the browser's local timezone.
4. THE Frontend SHALL default the Start Timestamp_Selector value to "Now" in the browser's local timezone.
5. THE Frontend SHALL default the End Timestamp_Selector timezone to US Eastern (EST/EDT).
6. IF the user sets the Start timestamp to a value equal to or later than the End timestamp, THEN THE Backend SHALL return a validation error indicating that the Start must be before the End.

### Requirement 2: Window Duration Input

**User Story:** As a user, I want to specify a window duration in days and hours, so that I can define the observation window size for the Poisson calculation.

#### Acceptance Criteria

1. THE Frontend SHALL display input fields for specifying the Window in days and hours.
2. THE Frontend SHALL accept non-negative integer values for days and non-negative integer values for hours (0–23) in the Window input fields.
3. IF the user enters a Window with a total duration of zero, THEN THE Backend SHALL return a validation error indicating that the Window must be greater than zero.
4. IF the user enters a non-numeric or negative value in a Window input field, THEN THE Backend SHALL return a validation error indicating that the value must be a non-negative integer.

### Requirement 3: Probability Input

**User Story:** As a user, I want to enter a probability percentage, so that the calculator can determine the corresponding event frequency.

#### Acceptance Criteria

1. THE Frontend SHALL display an input field for specifying the Probability as a percentage.
2. IF the user enters a Probability value less than or equal to 0 or greater than or equal to 100, THEN THE Backend SHALL return a validation error indicating that the Probability must be between 0 and 100 exclusive.
3. IF the user enters a non-numeric value in the Probability input field, THEN THE Backend SHALL return a validation error indicating that a numeric value is required.

### Requirement 4: Annualized Frequency Calculation with Steps

**User Story:** As a user, I want the calculator to compute how many times per year the event is expected to occur and show me the intermediate steps, so that I can understand and verify the annualized impact of the observed probability.

#### Acceptance Criteria

1. WHEN a valid calculation request is received, THE Backend SHALL compute Lambda (λ) using the formula λ = −ln(1 − Probability / 100) and include it in the Calculation_Steps.
2. WHEN Lambda (λ) is computed, THE Backend SHALL compute Window_in_hours using the formula Window_in_hours = (days × 24) + hours and include it in the Calculation_Steps.
3. WHEN Window_in_hours is computed, THE Backend SHALL derive the Annualized_Frequency by scaling Lambda from the Window duration to a one-year period using the formula: Annualized_Frequency = λ × (hours_in_year / Window_in_hours), where hours_in_year = 8766 (average accounting for leap years), and include the scaling factor in the Calculation_Steps.
4. THE Backend SHALL return the Annualized_Frequency result with up to two decimal places.
5. THE Backend SHALL return all Calculation_Steps (Lambda, Window_in_hours, scaling_factor, Annualized_Frequency) as part of the API response.
6. THE Frontend SHALL display the Calculation_Steps alongside the final Annualized_Frequency result.

### Requirement 5: Input Validation and Error Display

**User Story:** As a user, I want clear validation feedback on all inputs, so that I can correct mistakes before relying on the calculation result.

#### Acceptance Criteria

1. WHEN the Backend receives a calculation request with invalid inputs, THE Backend SHALL return structured error responses identifying each invalid field and its validation message.
2. WHEN the Frontend receives validation errors from the API, THE Frontend SHALL display specific error messages adjacent to the corresponding input fields.
3. WHILE any input validation error is present, THE Frontend SHALL hide the Annualized_Frequency result display.
4. WHEN all validation errors are resolved and a successful API response is received, THE Frontend SHALL immediately display the computed Annualized_Frequency and Calculation_Steps.

### Requirement 6: Mode Selection for Future Extensibility

**User Story:** As a user, I want a mode selector in the interface, so that additional calculation modes can be added in the future without redesigning the layout.

#### Acceptance Criteria

1. THE Frontend SHALL display a Mode_Selector control with "Poisson" as the default and only available option.
2. WHEN a mode is selected in the Mode_Selector, THE Frontend SHALL display the input fields and results relevant to the selected mode.
3. THE Frontend SHALL maintain separate input state for each mode so that switching modes preserves previously entered values.

### Requirement 7: Responsive and Minimal Frontend

**User Story:** As a user, I want the calculator to be usable on both desktop and mobile browsers with a simple interface, so that I can access it from any device without needing complex frontend tooling.

#### Acceptance Criteria

1. THE Frontend SHALL be implemented as a single static HTML file with inline or linked CSS and JavaScript, requiring no build tools or frontend frameworks.
2. THE Frontend SHALL render all input fields and results within a single-page layout without requiring page navigation.
3. THE Frontend SHALL adapt its layout to screen widths from 320px to 1920px without horizontal scrolling.
4. THE Frontend SHALL use a classless or minimal CSS approach to achieve a clean, readable design without heavy framework dependencies.
5. THE Frontend SHALL ensure all interactive controls are accessible via keyboard navigation and are compatible with screen readers.

### Requirement 8: FastAPI Backend with REST API

**User Story:** As a developer, I want the backend built with FastAPI exposing REST API endpoints, so that the system benefits from built-in Pydantic validation, async support, and auto-generated API documentation.

#### Acceptance Criteria

1. THE Backend SHALL be implemented using the FastAPI framework.
2. THE Backend SHALL expose a POST endpoint for submitting calculation requests with Time_Range, Window, and Probability inputs.
3. THE Backend SHALL validate all incoming request data using Pydantic models and return structured error responses for invalid inputs.
4. THE Backend SHALL serve auto-generated API documentation at a standard documentation path (e.g., /docs).
5. THE Backend SHALL serve the static Frontend files so that the entire application is accessible from a single server.
6. THE Backend SHALL include CORS configuration to allow the Frontend to communicate with the API during development.

### Requirement 9: Timezone Handling

**User Story:** As a user, I want the calculator to handle timezone conversions correctly, so that my time range inputs are interpreted accurately regardless of timezone differences.

#### Acceptance Criteria

1. THE Frontend SHALL send all timestamps to the Backend as ISO 8601 strings with timezone offset information.
2. WHEN the Backend receives timestamps with timezone information, THE Backend SHALL convert all timestamps to UTC for internal computation.
3. WHEN the Backend returns timestamps in API responses, THE Backend SHALL include UTC representations of all time values.
4. THE Frontend SHALL default the Start Timestamp_Selector to "Now" in the browser's local timezone.
5. THE Frontend SHALL default the End Timestamp_Selector timezone to US Eastern (EST/EDT).

### Requirement 10: Token-based Authentication

**User Story:** As an operator, I want all API endpoints protected by token-based authentication, so that only authorized users can access the calculator's computation and validation services.

#### Acceptance Criteria

1. THE Backend SHALL assign each authorized user a unique Auth_Token in UUID format.
2. THE Backend SHALL store all valid Auth_Tokens in a Token_Store implemented as a plain-text flat file on the server, with one Auth_Token per line.
3. WHEN a request is received on any API endpoint, THE Backend SHALL require the Auth_Token to be provided in the `Authorization` HTTP header.
4. IF a request does not include an Auth_Token in the `Authorization` header, THEN THE Backend SHALL return an HTTP 401 Unauthorized response with a structured error message indicating that an Auth_Token is required.
5. IF a request includes an Auth_Token that does not exist in the Token_Store, THEN THE Backend SHALL return an HTTP 401 Unauthorized response with a structured error message indicating that the Auth_Token is invalid.
6. WHEN a request includes a valid Auth_Token found in the Token_Store, THE Backend SHALL proceed with normal request processing.
7. WHEN the Backend starts, THE Backend SHALL load Auth_Tokens from the Token_Store file and reload the Token_Store when the file is modified.
8. IF the Token_Store file is missing or unreadable at startup, THEN THE Backend SHALL log an error and reject all authenticated requests until a valid Token_Store is available.
