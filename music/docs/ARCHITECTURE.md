# VibeNation Backend Architecture

## Table of Contents

* [1. Purpose](#1-purpose)
* [2. Architecture Philosophy](#2-architecture-philosophy)
* [3. High-Level System Architecture](#3-high-level-system-architecture)
* [4. Application Layers](#4-application-layers)

  * [4.1 Frontend Layer](#41-frontend-layer)
  * [4.2 API Layer](#42-api-layer)
  * [4.3 Business Logic Layer](#43-business-logic-layer)
  * [4.4 Data Layer](#44-data-layer)
  * [4.5 External Services Layer](#45-external-services-layer)
* [5. Django Application Structure](#5-django-application-structure)
* [6. Music Domain](#6-music-domain)
* [7. Editorial Domain](#7-editorial-domain)
* [8. Community Domain](#8-community-domain)
* [9. Engagement Domain](#9-engagement-domain)
* [10. Social Graph](#10-social-graph)
* [11. User and Identity Architecture](#11-user-and-identity-architecture)
* [12. Artist Identity Architecture](#12-artist-identity-architecture)
* [13. Request Flow](#13-request-flow)
* [14. Read Operations](#14-read-operations)
* [15. Write Operations](#15-write-operations)
* [16. Business Logic and Data Integrity](#16-business-logic-and-data-integrity)
* [17. Cached Counters](#17-cached-counters)
* [18. Views](#18-views)
* [19. Serializers](#19-serializers)
* [20. Authentication and Authorization](#20-authentication-and-authorization)
* [21. Admin Architecture](#21-admin-architecture)
* [22. External Music Catalog Integration](#22-external-music-catalog-integration)
* [23. Audio and Media Architecture](#23-audio-and-media-architecture)
* [24. Database Architecture](#24-database-architecture)
* [25. Caching Architecture](#25-caching-architecture)
* [26. Search Architecture](#26-search-architecture)
* [27. Performance Architecture](#27-performance-architecture)
* [28. Scalability Strategy](#28-scalability-strategy)
* [29. Future Go Services](#29-future-go-services)
* [30. Security Architecture](#30-security-architecture)
* [31. Error Handling](#31-error-handling)
* [32. Observability and Logging](#32-observability-and-logging)
* [33. Deployment Architecture](#33-deployment-architecture)
* [34. Development Principles](#34-development-principles)
* [35. Architectural Anti-Patterns](#35-architectural-anti-patterns)
* [36. Developer Workflow](#36-developer-workflow)
* [37. Golden Rules](#37-golden-rules)
* [38. Final Mental Model](#38-final-mental-model)

---

# 1. Purpose

This document describes the overall technical architecture of VibeNation.

It explains:

* How the frontend communicates with the backend
* How Django and Django REST Framework are organized
* How business logic is separated from database models
* How music, editorial, community, engagement, and social features interact
* How external music providers are integrated
* How PostgreSQL fits into the system
* How caching and performance are handled
* How the platform can scale in the future
* Where future specialized services such as Go services may fit

This document describes **architectural responsibilities and boundaries**.

It does not attempt to document every API endpoint.

The exact API contract belongs in:

```text
docs/API.md
```

`API.md` will be written after the backend API has been implemented and stabilized.

---

# 2. Architecture Philosophy

VibeNation should be built as a modular application with clear boundaries rather than as a collection of unrelated features.

The primary backend stack is:

```text
Django
Django REST Framework
PostgreSQL
```

The frontend is:

```text
Next.js
```

The architecture should prioritize:

1. Correctness
2. Maintainability
3. Clear ownership of data
4. Security
5. Performance
6. Scalability
7. Simplicity

The project should avoid premature microservices.

The initial system should be capable of serving the majority of VibeNation's workload from a well-structured Django/DRF application.

---

# 3. High-Level System Architecture

The overall system can be represented as:

```text
                         VIBENATION

                    ┌─────────────────┐
                    │    Next.js      │
                    │    Frontend     │
                    └────────┬────────┘
                             │
                             │ HTTPS / JSON
                             ↓
                    ┌─────────────────┐
                    │ Django + DRF    │
                    │    API Layer     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ↓              ↓              ↓
       Business Logic    Serializers     Auth/
       / Services                        Permissions
              │
              ↓
        ┌───────────────┐
        │   Django ORM  │
        └───────┬───────┘
                │
                ↓
        ┌───────────────┐
        │  PostgreSQL   │
        └───────────────┘

                │
       ┌────────┴─────────┐
       ↓                  ↓
 External Music       Media / CDN
 Providers
```

The architecture is intentionally centralized around Django initially.

---

# 4. Application Layers

## 4.1 Frontend Layer

The frontend is built with Next.js.

Its responsibilities include:

* Rendering pages
* User interaction
* Client-side state
* Form handling
* Calling the backend API
* Displaying API responses
* Authentication UI
* Music discovery UI
* Community UI
* Editorial UI

The frontend should not contain the application's authoritative business rules.

For example, the frontend may display:

```text
Like
```

but the backend determines whether the authenticated user is actually allowed to create that like.

---

## 4.2 API Layer

Django REST Framework provides the backend API boundary.

Its responsibilities include:

* Receiving HTTP requests
* Authentication
* Authorization
* Validation
* Calling application logic
* Serializing responses
* Returning appropriate HTTP responses

The API layer should not become a dumping ground for complex business logic.

---

## 4.3 Business Logic Layer

Business logic is responsible for operations that require more than simply saving a model.

Examples include:

* Incrementing/decrementing engagement counters
* Creating or deleting ratings
* Handling follows
* Processing external music search results
* Creating community-post targets
* Updating related records atomically
* Applying moderation rules
* Coordinating multi-model operations

Where appropriate, reusable logic can live in service/helper modules rather than being duplicated across views.

The goal is:

```text
View
  ↓
Business operation
  ↓
Models
```

rather than putting every rule directly into the view.

---

## 4.4 Data Layer

The data layer consists primarily of Django models and PostgreSQL.

It is responsible for:

* Persistent data
* Relationships
* Constraints
* Indexes
* Transactions
* Querying
* Data integrity

Models should represent domain data and database relationships.

They should not become giant containers for unrelated application workflows.

---

## 4.5 External Services Layer

External services may include:

* Music catalog providers
* Music streaming destinations
* Object/media storage
* CDN
* Email services
* Analytics systems
* Future search infrastructure
* Future specialized services

External services should be accessed through controlled backend integrations.

The frontend should not need to understand provider-specific implementation details.

---

# 5. Django Application Structure

The current backend is centered around Django applications.

The music application contains the core music-related domain.

Conceptually:

```text
music/
├── models.py
├── admin.py
├── serializers.py
├── views.py
├── urls.py
├── migrations/
└── docs/
```

As the application grows, internal modules can be separated where necessary.

For example:

```text
music/
├── services/
├── integrations/
├── selectors/
├── permissions/
└── utils/
```

These should be introduced when complexity justifies them.

The architecture should not create dozens of files merely for the sake of theoretical separation.

---

# 6. Music Domain

The music domain is the foundation of VibeNation's music features.

Core catalog entities include:

```text
Genre
Artist
Album
AlbumTrack
Song
```

Additional music-domain entities include:

```text
SongRating
AlbumRating
SongFavorite
AlbumFavorite
ArtistFollow
```

Community and editorial entities can reference music entities without becoming part of the catalog itself.

The music catalog provides the structured foundation for:

* Discovery
* Artist pages
* Album pages
* Song pages
* Reviews
* Ratings
* Favorites
* Community discussion
* Editorial content

---

# 7. Editorial Domain

The editorial domain manages VibeNation's professionally produced content.

The primary content entity is:

```text
EditorialArticle
```

Editorial articles can connect to:

* Songs
* Albums
* Artists
* Genres

Editorial content has its own engagement and moderation system.

Conceptually:

```text
EditorialArticle
      │
      ├── Music relationships
      │
      ├── Likes
      ├── Comments
      ├── Replies
      ├── Views
      └── Reports
```

Editorial content is controlled by VibeNation staff/admin workflows.

Users can interact with published editorial content but do not become editorial authors merely by commenting on it.

---

# 8. Community Domain

The community domain provides user-generated music discussion.

The primary entity is:

```text
CommunityPost
```

A community post can be associated with music through:

```text
CommunityPostTarget
```

Users can then:

* Publish posts
* Rate music
* Comment
* Reply
* Like content
* Report content
* View content

The community system is separate from editorial publishing.

```text
Editorial
    ↓
VibeNation-produced content

Community
    ↓
User-produced content
```

This separation is fundamental to the platform.

---

# 9. Engagement Domain

Engagement represents actions users perform around content and music.

It includes:

```text
Likes
Ratings
Favorites
Follows
Views
```

Different actions have different meanings.

For example:

```text
Like
→ I enjoyed this content.

Rating
→ I am scoring this music.

Favorite
→ I want to keep this music in my collection.

Follow
→ I want updates about this entity/user.

View
→ This content was viewed.
```

Engagement records are separate database entities rather than fields embedded directly inside users or content objects.

---

# 10. Social Graph

The social graph currently consists primarily of:

```text
UserFollow
ArtistFollow
```

`UserFollow` represents:

```text
User → User
```

`ArtistFollow` represents:

```text
User → Artist
```

These relationships can later power:

* Following feeds
* Artist updates
* Recommendations
* Notifications
* Social discovery
* Trending calculations

The social graph remains separate from the music catalog itself.

---

# 11. User and Identity Architecture

Django's user system is the identity foundation.

The system distinguishes between:

```text
Platform User
```

and:

```text
Music Artist
```

A platform user can:

* Log in
* Create community posts
* Comment
* Rate
* Like
* Favorite
* Follow users
* Follow artists

A catalog artist does not need a platform account.

This prevents the catalog from being artificially constrained by user authentication.

---

# 12. Artist Identity Architecture

Artists are catalog entities, not accounts.

The relationship is:

```text
User
  │
  │ follows
  ↓
Artist
```

not:

```text
User
  │
  └── Artist account
```

The `Artist.followers_count` field is a cached count of VibeNation users following that artist.

It exists to support efficient read operations such as:

```text
Artist page
    ↓
48K followers
```

It does not imply that artists have login identities.

---

# 13. Request Flow

A normal request follows this general path:

```text
Browser
   ↓
Next.js
   ↓
HTTP request
   ↓
Django URL routing
   ↓
DRF view
   ↓
Authentication / permissions
   ↓
Validation
   ↓
Business logic
   ↓
Django ORM
   ↓
PostgreSQL
   ↓
Serializer
   ↓
JSON response
   ↓
Next.js
   ↓
Browser
```

External-provider requests add another branch:

```text
DRF view
   ↓
Music integration
   ↓
External provider
   ↓
Normalized result
   ↓
DRF response
```

---

# 14. Read Operations

Read-heavy operations should be optimized differently from writes.

Typical read operations include:

* Homepage
* Song pages
* Album pages
* Artist pages
* Editorial pages
* Community feeds
* Comments
* Search

The system should use:

* Efficient ORM queries
* `select_related`
* `prefetch_related`
* Appropriate indexes
* Pagination
* Caching where useful

The goal is to prevent unnecessary database queries.

For example, an artist page should not execute one database query per song merely to retrieve artist relationships.

---

# 15. Write Operations

Write operations include:

* Creating community posts
* Creating comments
* Creating replies
* Creating ratings
* Creating likes
* Creating favorites
* Following users
* Following artists
* Publishing editorial content

Writes must enforce:

* Authentication
* Permissions
* Validation
* Database constraints
* Atomic counter updates where applicable

A successful write should leave related data in a consistent state.

---

# 16. Business Logic and Data Integrity

Some operations affect multiple records.

For example, creating an `ArtistFollow` may require:

```text
Create ArtistFollow
        +
Increment Artist.followers_count
```

These operations should be handled atomically.

Conceptually:

```text
transaction
    ├── create relationship
    └── update cached counter
```

If one part fails, the operation should not leave the database in an inconsistent state.

The same principle applies to:

* Likes
* Favorites
* Ratings
* Comment counters
* Reply counters
* View counters
* Follow counters

---

# 17. Cached Counters

VibeNation stores certain counters for read performance.

Examples include:

```text
Artist.followers_count
Album.favorites_count
Album.ratings_count
Song.favorites_count
Song.ratings_count
EditorialArticle.likes_count
EditorialArticle.comments_count
EditorialArticle.views_count
CommunityPost.likes_count
CommunityPost.comments_count
CommunityPost.views_count
EditorialComment.likes_count
EditorialComment.replies_count
EditorialComment.views_count
CommunityPostComment.likes_count
CommunityPostComment.replies_count
CommunityPostComment.views_count
```

These counters are **cached read optimizations**.

The underlying engagement rows remain the source of truth.

For example:

```text
CommunityPostLike rows
        ↓
source of truth

CommunityPost.likes_count
        ↓
cached counter
```

Counters should be updated atomically.

They should also be repairable if a bug or exceptional event causes drift.

---

# 18. Views

Views are treated as engagement metrics rather than as conventional relationships.

A view does not necessarily create a permanent user-to-content relationship.

View counting should therefore be handled at the API/service layer.

The exact anti-abuse strategy can evolve.

Possible future techniques include:

* Session-based deduplication
* Authenticated-user deduplication
* IP/rate controls
* Time windows
* Redis-based short-term tracking

The system should avoid unnecessarily creating a database row for every page impression unless analytics requirements justify it.

---

# 19. Serializers

Django REST Framework serializers provide the API representation layer.

They are responsible for:

* Converting model instances into API representations
* Validating incoming structured data
* Controlling exposed fields
* Representing relationships
* Handling nested API structures where appropriate

Serializers should not be treated as the database layer.

They should also avoid embedding excessive business logic.

Where a complex operation requires multiple database changes, the serializer can delegate to an application/service operation.

---

# 20. Authentication and Authorization

Authentication answers:

> Who is making this request?

Authorization answers:

> Is this user allowed to perform this action?

These are separate concerns.

For example:

```text
Authenticated user
    ↓
Can create CommunityPost
```

but:

```text
Anonymous visitor
    ↓
Cannot create CommunityPost
```

Similarly:

```text
Staff
    ↓
Can moderate reports

Master Admin
    ↓
Full administrative control
```

Permissions should be enforced server-side.

The frontend must never be trusted to enforce authorization by itself.

---

# 21. Admin Architecture

VibeNation has a dedicated administrative architecture.

The major portals are:

```text
Master Admin
Staff Admin
Default Django Admin
```

The master portal provides full platform control.

The staff portal is intended for operational workflows such as:

* Editorial management
* Music catalog management
* Moderation
* Reports
* Content management

User-generated engagement should generally not be manually fabricated through the admin.

For example, an administrator should not normally create:

```text
CommunityPostLike
SongRating
ArtistFollow
```

on behalf of users.

Admin exists primarily for:

```text
Manage
Moderate
Review
Correct
Publish
Configure
Audit
```

rather than simulate user activity.

---

# 22. External Music Catalog Integration

VibeNation can integrate external music catalogs for discovery.

The integration should be isolated from the rest of the application.

Conceptually:

```text
VibeNation API
      ↓
Music Provider Adapter
      ↓
Provider API
```

The rest of VibeNation should consume normalized data rather than provider-specific structures.

For example:

```text
Apple:
trackName

Spotify:
name

VibeNation:
title
```

The provider adapter handles the translation.

This makes it possible to replace or add providers later without rewriting the entire community system.

---

# 23. Audio and Media Architecture

VibeNation does not host full copyrighted music recordings.

The architecture therefore does not depend on storing MP3 files for normal music playback.

The platform instead uses:

* Music metadata
* External listening links
* Permitted previews
* Permitted embeds
* VibeNation-owned editorial media

For production media such as:

* News images
* Editorial images
* Advertisements
* Other platform-owned assets

VibeNation can use object storage and CDN infrastructure.

The media architecture should remain separate from the music catalog architecture.

---

# 24. Database Architecture

PostgreSQL is the intended production database.

Django ORM provides the application interface to the database.

```text
Application
    ↓
Django ORM
    ↓
PostgreSQL
```

The database remains the source of truth for persistent VibeNation data.

Important database responsibilities include:

* Relationships
* Constraints
* Unique constraints
* Foreign keys
* Indexes
* Transactions
* Data persistence

The application should rely on database constraints in addition to application-level validation.

---

# 25. Caching Architecture

Caching should be introduced where it solves a demonstrated performance problem.

Potential cache targets include:

* Homepage data
* Trending music
* Popular artists
* Music-provider search results
* Frequently accessed catalog pages
* Expensive aggregate queries

Redis can eventually serve as the primary application cache.

The architecture should not treat cache data as the authoritative source.

```text
PostgreSQL
    ↓
source of truth

Redis
    ↓
performance layer
```

If the cache disappears, the application should be able to rebuild the data from its authoritative sources.

---

# 26. Search Architecture

Search begins with database-backed querying.

For moderate scale, PostgreSQL can handle many search requirements using:

* Indexed fields
* Case-insensitive matching
* Full-text search
* Appropriate query optimization

External music-provider search remains separate from VibeNation's internal catalog search.

Eventually, if search requirements become sufficiently large or sophisticated, a dedicated search engine can be introduced.

Possible future technologies include:

* Elasticsearch
* OpenSearch
* PostgreSQL full-text search enhancements
* Other specialized search infrastructure

A dedicated search engine should only be introduced when actual scale or search requirements justify it.

---

# 27. Performance Architecture

Performance should be improved progressively.

### First layer

Use efficient Django ORM queries.

```text
select_related()
prefetch_related()
```

### Second layer

Use:

* Pagination
* Database indexes
* Cached counters
* Response caching

### Third layer

Introduce:

* Redis
* CDN
* Background workers
* Dedicated search infrastructure

### Fourth layer

Introduce specialized services only where justified.

The architecture should avoid solving imaginary scaling problems before they exist.

---

# 28. Scalability Strategy

The initial architecture is intentionally a modular monolith.

```text
             Django
        ┌──────┼──────┐
        │      │      │
     Music  Editorial Community
        │      │      │
        └──────┼──────┘
               │
          PostgreSQL
```

This does **not** mean the system cannot scale.

A well-designed Django application can handle substantial traffic when supported by:

* PostgreSQL
* Caching
* CDN
* Efficient queries
* Horizontal application scaling
* Background processing

The first goal is to build a strong modular core.

---

# 29. Future Go Services

Go may eventually be introduced for high-concurrency workloads.

However, Go is not required for the initial VibeNation backend.

Potential future Go workloads could include:

* High-volume feed generation
* Real-time activity streams
* Very high-throughput notifications
* Large-scale analytics ingestion
* Specialized recommendation processing
* Other workloads where Go provides a meaningful operational advantage

The intended architecture would become:

```text
                 ┌───────────────┐
                 │    Next.js    │
                 └───────┬───────┘
                         │
                ┌────────┴────────┐
                │                 │
                ↓                 ↓
           Django/DRF          Go Service
                │                 │
                └────────┬────────┘
                         ↓
                    Data Layer
```

Go should be introduced because a specific workload requires it—not simply because "large platforms use microservices."

Django remains the core application unless there is a concrete reason to split responsibilities.

---

# 30. Security Architecture

Security is enforced primarily at the backend boundary.

Important principles include:

* HTTPS in production
* Secure authentication
* Server-side authorization
* CSRF protection where applicable
* Input validation
* Rate limiting
* Secure secret management
* Database constraints
* Safe file handling
* Output escaping where appropriate
* Protection against abusive requests
* Audit logging for administrative activity

External provider credentials must never be exposed to the browser.

For example:

```text
Browser
   ↓
VibeNation API
   ↓
Provider API key/token
```

not:

```text
Browser
   ↓
Provider API key/token
```

---

# 31. Error Handling

The API should return predictable errors.

Errors can occur from:

* Invalid user input
* Authentication failure
* Permission failure
* Missing resources
* Database constraints
* External provider failure
* Rate limiting
* Temporary infrastructure problems

External provider failures should not necessarily bring down unrelated VibeNation features.

For example:

```text
Apple Music unavailable
        ↓
Music search temporarily unavailable

Community posts
Editorial
Comments
Ratings
        ↓
Continue functioning
```

The backend should isolate external failures wherever practical.

---

# 32. Observability and Logging

Production systems need visibility into what is happening.

Important areas include:

* Application errors
* API errors
* Slow requests
* Database performance
* External provider failures
* Authentication failures
* Administrative activity
* Background job failures
* Infrastructure health

Django's logging system can provide the initial foundation.

As the platform grows, external monitoring and error-tracking systems can be introduced.

---

# 33. Deployment Architecture

A typical production deployment can eventually look like:

```text
                    Internet
                       │
                       ↓
                  CDN / Proxy
                       │
                       ↓
                 Next.js App
                       │
                       │ HTTPS
                       ↓
              Django/DRF Application
                       │
            ┌──────────┼──────────┐
            ↓          ↓          ↓
        PostgreSQL   Redis    External APIs
            │          │
            ↓          ↓
        Persistent   Cache
          Data
```

Media can use separate object storage/CDN infrastructure:

```text
Django
   ↓
Object Storage
   ↓
CDN
   ↓
Browser
```

The exact hosting providers can change without changing the core application architecture.

---

# 34. Development Principles

Development should follow these principles.

### Build from the domain model

The database structure defines important relationships, but the API should expose domain operations rather than simply exposing every table blindly.

### Keep responsibilities clear

Each layer should have a reason to exist.

### Prefer simple solutions

Do not introduce:

* Microservices
* Message queues
* Search clusters
* Multiple databases
* Go services

until there is a real requirement.

### Protect data integrity

Use:

* Database constraints
* Transactions
* Validation
* Permissions

### Design for future growth without building future complexity

The architecture should be capable of evolving without requiring every future technology today.

---

# 35. Architectural Anti-Patterns

The following patterns should generally be avoided.

## 35.1 Frontend-only authorization

Never rely on:

```text
if (user.isAdmin) {
   showButton();
}
```

as the security boundary.

The backend must enforce authorization.

---

## 35.2 Giant views

Avoid putting:

* Validation
* Business logic
* Database manipulation
* External API calls
* Counter management

into one enormous view.

---

## 35.3 Giant serializers

Serializers should not become entire application services.

Complex workflows should be moved into appropriate application logic.

---

## 35.4 Model overloading

Do not put every possible workflow inside `models.py`.

Models represent data and domain relationships.

---

## 35.5 External provider coupling

Do not spread Apple/Spotify-specific fields and response structures throughout the application.

Use an integration/normalization boundary.

---

## 35.6 Premature microservices

Do not split:

```text
Music service
Community service
Rating service
Comment service
```

into independent services simply because the platform contains those features.

They can initially live inside one well-structured Django application.

---

## 35.7 Treating counters as truth

Never assume:

```text
Song.ratings_count
```

is more authoritative than the actual rating rows.

Counters are cached values.

---

## 35.8 Treating artists as users

Never create an artist account model simply because an artist has followers.

Artists are catalog entities.

---

## 35.9 Hosting copyrighted music unnecessarily

The architecture should not depend on VibeNation storing full commercial recordings.

---

# 36. Developer Workflow

When implementing a new feature, follow this sequence:

```text
1. Define the domain requirement
            ↓
2. Identify affected models
            ↓
3. Determine business rules
            ↓
4. Determine permissions
            ↓
5. Implement application logic
            ↓
6. Implement serializer
            ↓
7. Implement API view
            ↓
8. Add URL routing
            ↓
9. Test
            ↓
10. Optimize
            ↓
11. Document
```

Documentation should follow implementation closely enough that it describes the actual system.

For the API specifically:

```text
Build API
   ↓
Test API
   ↓
Stabilize API
   ↓
Document API.md
```

This prevents documentation from becoming disconnected from the implementation.

---

# 37. Golden Rules

1. **Django/DRF is the initial core backend.**
2. **PostgreSQL is the production source of truth.**
3. **Next.js communicates with the backend through the VibeNation API.**
4. **The backend owns authorization and business rules.**
5. **Models represent data and relationships.**
6. **Serializers represent API data and validation.**
7. **Complex workflows belong in appropriate application/business logic.**
8. **External provider integrations remain behind the backend.**
9. **Artists are catalog entities, not users.**
10. **Engagement records are the source of truth for engagement.**
11. **Cached counters are performance optimizations.**
12. **Views should not contain unnecessary business complexity.**
13. **Database constraints protect data integrity.**
14. **Caching is a performance layer, not a source of truth.**
15. **VibeNation does not need microservices at the beginning.**
16. **Go services should only be introduced for workloads that justify them.**
17. **VibeNation does not depend on hosting full copyrighted music.**
18. **External provider failures should be isolated where practical.**
19. **Security must be enforced server-side.**
20. **Optimize based on real bottlenecks rather than speculation.**

---

# 38. Final Mental Model

The VibeNation architecture can be reduced to this:

```text
                         USERS
                           │
                           ↓
                     Next.js Frontend
                           │
                           ↓
                    Django REST API
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ↓              ↓              ↓
         Catalog        Editorial      Community
            │              │              │
            └──────────────┼──────────────┘
                           │
                           ↓
                      Engagement
                           │
                           ↓
                      Social Graph
                           │
                           ↓
                     Django ORM
                           │
                           ↓
                       PostgreSQL


External Music Providers
          │
          ↓
   Music Integration
          │
          ↓
     Django/DRF


Redis / CDN / Background Workers / Go
          │
          ↓
    Added only when
    actually necessary
```

The architecture is therefore:

> **A modular Django/DRF monolith backed by PostgreSQL, with Next.js as the frontend, external music providers behind a controlled integration layer, and optional infrastructure/services added progressively as real scale requires them.**

The goal is not to make VibeNation complicated.

The goal is to make it **well-structured enough that it can become complicated later without becoming a mess.**
