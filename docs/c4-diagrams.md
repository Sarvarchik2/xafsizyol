# C4 Diagrams: Xafsizyol

## Level 1: System Context Diagram
Shows how the Xafsizyol system interacts with users and external systems.

```mermaid
C4Context
    title System Context diagram for Xafsizyol
    Person(user, "Commuter", "A person who reports potholes and road hazards.")
    System(system, "Xafsizyol Platform", "Allows users to report and track road hazards.")
    System_Ext(map, "Map Provider", "Provides map tiles and geocoding services.")
    System_Ext(storage, "Cloud Storage", "Stores uploaded photos of hazards.")
    
    Rel(user, system, "Uses", "HTTPS")
    Rel(system, map, "Fetches maps from", "API")
    Rel(system, storage, "Uploads photos to", "API")
```

## Level 2: Container Diagram
Shows the high-level technical building blocks of the system.

```mermaid
C4Container
    title Container diagram for Xafsizyol
    Person(user, "Commuter", "A person who reports hazards.")
    System_Boundary(c1, "Xafsizyol") {
        Container(app, "Web Application", "Nuxt.js / Vue", "Provides the UI and user experience.")
        Container(api, "API Layer", "Nuxt Server Engine", "Handles business logic and data processing.")
        ContainerDb(db, "Database", "PostgreSQL/MongoDB", "Stores records of reports and users.")
    }
    System_Ext(map, "Map Provider", "External Map Service")
    
    Rel(user, app, "Interacts with", "HTTPS")
    Rel(app, api, "Makes API calls to", "JSON/HTTPS")
    Rel(api, db, "Reads from/Writes to", "SQL/Driver")
    Rel(app, map, "Loads map tiles", "HTTPS")
```

## Level 3: Component Diagram (API Layer)
Shows the internal components of the API Layer.

```mermaid
C4Component
    title Component diagram for API Layer
    Container(app, "Web Application", "Vue.js", "Frontend UI")
    Container_Boundary(api, "API Layer") {
        Component(auth, "Auth Controller", "Nuxt Server", "Handles user login and registration.")
        Component(report, "Report Handler", "Nuxt Server", "Processes pothole report submissions.")
        Component(map_proxy, "Map Proxy", "Nuxt Server", "Proxies map requests if needed.")
    }
    ContainerDb(db, "Database", "Relational Database", "Data Storage")
    
    Rel(app, auth, "Uses", "JSON/HTTPS")
    Rel(app, report, "Uses", "JSON/HTTPS")
    Rel(report, db, "Stores reports in", "SQL")
    Rel(auth, db, "Manages users in", "SQL")
```
