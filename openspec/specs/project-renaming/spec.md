# project-renaming Specification

## Purpose
TBD - created by archiving change rename-project-to-aiput. Update Purpose after archive.
## Requirements
### Requirement: Project Name Configuration
The project configuration MUST use the new project name "aiput" across all configuration files and package metadata.
#### Scenario: When users view the project name in pyproject.toml
- The project name MUST be "aiput" instead of "qaa-airtype"
- The project SHOULD maintain the same version and metadata structure
- The package name MUST reflect the new identity

### Requirement: Application Branding Display
The application MUST display the new brand name "AIPut" in all user-visible locations including window titles and system tray.
#### Scenario: When users run the application
- The window title MUST display "AIPut" instead of "QAA AirType"
- The system tray icon MUST show "AIPut" as the tooltip/name
- All user-facing text MUST reference "AIPut" as the application name

### Requirement: Documentation Branding
All project documentation MUST reference the new project name "AIPut" instead of "QAA AirType".
#### Scenario: When developers read project documentation
- The project description and context MUST reference "AIPut"
- The purpose statement MUST be updated to reflect the new name
- All historical references SHOULD acknowledge the name change

### Requirement: Repository URL Updates
All repository links in project configuration MUST point to the new repository location.
#### Scenario: When users access repository links
- Homepage URL MUST point to https://github.com/newbe36524/AIPut
- Repository URL MUST point to https://github.com/newbe36524/AIPut
- Issues URL MUST point to https://github.com/newbe36524/AIPut/issues

