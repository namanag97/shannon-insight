"""Layer definitions for spec generation."""

LAYERS = {
    "business": {
        "name": "Business Layer",
        "order": 1,
        "focus_areas": [
            "What problem does this solve?",
            "Who are the users?",
            "What value does it provide?",
            "What are the constraints (budget, time, regulations)?",
            "What's the success metric?"
        ],
        "output_template": """
## Business Layer

### Problem Statement
[What problem are we solving?]

### Target Users
[Who will use this?]

### Value Proposition
[Why should users care?]

### Constraints
[Budget, time, regulatory, etc.]

### Success Metrics
[How do we measure success?]
"""
    },
    "product": {
        "name": "Product Layer",
        "order": 2,
        "focus_areas": [
            "What are the core features?",
            "What are the key user flows?",
            "What data needs to be captured/displayed?",
            "What integrations are needed?",
            "What's the MVP vs. nice-to-have?"
        ],
        "output_template": """
## Product Layer

### Core Features
[List of essential features]

### User Flows
[Key user journeys]

### Data Model (Conceptual)
[What entities and relationships exist?]

### Integrations
[Third-party services needed]

### MVP Scope
[What's in v1?]
"""
    },
    "technical": {
        "name": "Technical Layer",
        "order": 3,
        "focus_areas": [
            "What's the architecture (client/server, microservices, etc.)?",
            "What's the tech stack (languages, frameworks)?",
            "What are the scale requirements?",
            "What are the security requirements?",
            "What's the deployment model?"
        ],
        "output_template": """
## Technical Layer

### Architecture
[High-level system design]

### Tech Stack
[Languages, frameworks, tools]

### Scale Requirements
[Expected load, growth]

### Security Requirements
[Auth, data protection, compliance]

### Deployment
[Cloud provider, CI/CD, environments]
"""
    },
    "implementation": {
        "name": "Implementation Layer",
        "order": 4,
        "focus_areas": [
            "What's the project structure?",
            "What are the API endpoints?",
            "What's the database schema?",
            "What's the deployment process?",
            "What are the first implementation steps?"
        ],
        "output_template": """
## Implementation Layer

### Project Structure
[Folder/file organization]

### API Design
[Endpoints, contracts]

### Database Schema
[Tables, indexes, relationships]

### Deployment Process
[Build, test, deploy steps]

### First Steps
[Recommended order of implementation]
"""
    }
}

def get_layer_order():
    """Return layers in correct order."""
    return sorted(LAYERS.keys(), key=lambda k: LAYERS[k]["order"])

def get_layer_info(layer_name: str):
    """Get information about a specific layer."""
    return LAYERS.get(layer_name)
