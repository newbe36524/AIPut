# AI Processing Capability Specification

## Requirements

## ADDED Requirements

### Requirement: AI Processing Mode Selection
The mobile interface SHALL provide a mode selector in the header that allows users to choose between different text processing modes, including a default "Normal" mode that applies no processing.

#### Scenario: Mode selector visibility
- **WHEN** user loads the mobile interface
- **THEN** a mode selector dropdown SHALL be visible in the header between the title and action buttons
- **AND** SHALL default to "Normal" mode
- **AND** SHALL display the current mode name

#### Scenario: Mode selection
- **WHEN** user taps on the mode selector
- **THEN** a dropdown list SHALL appear with available processing modes
- **AND** each mode SHALL display its name and description
- **AND** selecting a mode SHALL immediately update the selector and close the dropdown

### Requirement: Configurable Processing Prompts
The frontend SHALL load processing mode configurations from a JSON file that defines available modes, their display names, descriptions, and associated prompts.

#### Scenario: Prompt configuration loading
- **WHEN** the mobile interface loads
- **THEN** the frontend SHALL load mode configurations from `site/config/prompts.json`
- **AND** SHALL populate the mode selector with available options
- **AND** SHALL gracefully handle missing or invalid configuration files

#### Scenario: Dynamic mode updates
- **WHEN** the prompts.json file is updated
- **THEN** the frontend SHALL make new modes available without backend changes
- **AND** SHALL support adding new processing modes by adding entries to the JSON

### Requirement: AI Text Processing Service
The backend SHALL provide an AI text processing service that applies selected prompts to user text using configurable AI providers.

#### Scenario: Text processing request
- **WHEN** user sends text with a processing mode selected
- **THEN** the frontend SHALL include the prompt directly in the request
- **THEN** the backend SHALL use the received prompt to process the user's text
- **AND** SHALL send the combined content to the configured AI provider
- **AND** SHALL log the mode for analytics purposes only
- **AND** SHALL return the processed text to replace the original input

#### Scenario: Processing failure handling
- **WHEN** AI processing fails due to API errors or timeouts
- **THEN** the system SHALL display a clear error message to the user
- **AND** SHALL offer options to retry or send the original unprocessed text
- **AND** SHALL maintain the original text in the input field

## MODIFIED Requirements

### Requirement: Header Action Buttons (from mobile-ui spec)
Send and Clear action buttons SHALL be prominently displayed in the header area for immediate access, with space for the mode selector.

#### Scenario: Header element arrangement
- **WHEN** viewing the interface on mobile devices
- **THEN** the header SHALL contain: hamburger menu (left), title (center-left), mode selector (center-right), and action buttons (right)
- **AND** all elements SHALL remain accessible and properly spaced
- **AND** SHALL maintain responsive design for different screen sizes

### Requirement: AI Provider Abstraction
The backend SHALL implement an abstract AI processor interface that allows multiple AI providers to be supported with a common API.

#### Scenario: Provider configuration
- **WHEN** configuring the system
- **THEN** administrators SHALL be able to select from available AI providers
- **AND** SHALL configure provider-specific settings (API keys, models, etc.)
- **AND** SHALL set a default provider for processing requests

#### Scenario: Provider extensibility
- **WHEN** adding support for a new AI provider
- **THEN** developers SHALL implement the AIProcessor interface
- **AND** SHALL register the provider with the ProcessingService
- **AND** SHALL not require changes to the frontend or API contracts

### Requirement: Enhanced Type Endpoint
The system SHALL enhance the existing `/type` endpoint to accept optional AI processing parameters while maintaining backward compatibility.

#### Scenario: Standard text input
- **WHEN** frontend sends text with "Normal" mode
- **THEN** it SHALL send a POST request to `/type` with text only
- **AND** the backend SHALL send text directly to desktop
- **AND** SHALL return success status

#### Scenario: AI-processed text input
- **WHEN** frontend sends text with AI mode selected
- **THEN** it SHALL send a POST request to `/type` with text, prompt, and mode
- **AND** the backend SHALL use the prompt to process the text
- **AND** SHALL send the processed text to desktop
- **AND** SHALL return success status

#### Scenario: API security
- **WHEN** processing requests are made
- **THEN** API keys SHALL never be exposed to the frontend
- **AND** requests SHALL be rate-limited to prevent abuse
- **AND** sensitive content SHALL not be logged in plain text
- **AND** prompts SHALL be validated to prevent injection attacks