# VibeNation Music System

The `music` app is the core music discovery, editorial, community, and social interaction system of **VibeNationHQ**.

It is designed to support music-related content without hosting or distributing copyrighted audio files.

The system allows VibeNation to:

* Maintain its own curated catalog of artists, albums, songs, genres, and tracks.
* Publish editorial articles about music.
* Allow users to create community posts containing opinions, reviews, ratings, and discussions about music.
* Allow users to rate songs and albums.
* Allow users to favorite songs and albums.
* Allow users to follow artists.
* Allow users to follow other users.
* Support comments, nested replies, likes, reports, and view counts.
* Connect community posts to songs, albums, artists, or external music-provider metadata.
* Integrate with third-party music catalog providers for music discovery and metadata.
* Provide official listening destinations rather than hosting downloadable audio.
* Provide a foundation for personalized feeds, recommendations, notifications, analytics, and future high-scale services.

---

# Table of Contents

1. [Overview](#overview)
2. [Core Architecture](#core-architecture)
3. [Music System Philosophy](#music-system-philosophy)
4. [Application Structure](#application-structure)
5. [Domain Areas](#domain-areas)

   * [Music Catalog](#music-catalog)
   * [Editorial System](#editorial-system)
   * [Community System](#community-system)
   * [Engagement System](#engagement-system)
   * [Social Graph](#social-graph)
6. [Core Models](#core-models)
7. [Important Relationships](#important-relationships)
8. [Community Posts](#community-posts)
9. [Comments and Replies](#comments-and-replies)
10. [Ratings](#ratings)
11. [Likes, Favorites and Follows](#likes-favorites-and-follows)
12. [View Counts](#view-counts)
13. [Artist Architecture](#artist-architecture)
14. [Third-Party Music Metadata](#third-party-music-metadata)
15. [Audio Hosting Policy](#audio-hosting-policy)
16. [Editorial vs Community Content](#editorial-vs-community-content)
17. [Engagement Counters](#engagement-counters)
18. [Database and PostgreSQL](#database-and-postgresql)
19. [API Architecture](#api-architecture)
20. [Admin Architecture](#admin-architecture)
21. [Caching and Performance](#caching-and-performance)
22. [Future Scalability](#future-scalability)
23. [Development Rules](#development-rules)
24. [Migration Rules](#migration-rules)
25. [Documentation](#documentation)
26. [Developer Checklist](#developer-checklist)
27. [Golden Rules](#golden-rules)
28. [Final Mental Model](#final-mental-model)

---

# Overview

The VibeNation music system is **not a music file-hosting platform**.

Its purpose is to build a structured music knowledge and social layer around songs, albums, artists, and music-related conversations.

A simplified representation of the system is:

```text
                         VIBENATION MUSIC SYSTEM
                                  │
          ┌───────────────────────┼────────────────────────┐
          │                       │                        │
          ▼                       ▼                        ▼
   MUSIC CATALOG             EDITORIAL               COMMUNITY
          │                       │                        │
          │                       │                        │
   Artists / Albums         Articles / Comments     Posts / Comments
   Songs / Genres           Likes / Reports         Replies / Likes
   Tracks / Metadata        Views                   Ratings
          │                       │                        │
          └───────────────────────┼────────────────────────┘
                                  │
                                  ▼
                             ENGAGEMENT
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
           Ratings            Favorites            Follows
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                                  ▼
                         SOCIAL / DISCOVERY
```

The application is designed around clear separation of responsibilities.

For example:

* An `Artist` represents a music artist.
* An `Album` represents an album or EP.
* A `Song` represents a song.
* An `EditorialArticle` represents content written by VibeNation's editorial team.
* A `CommunityPost` represents a post created by a VibeNation user.
* A `CommunityPostComment` represents a comment on a community post.
* A `SongRating` represents a user's rating of a song.
* An `ArtistFollow` represents a user's relationship with an artist.

These concepts should not be mixed together.

---

# Core Architecture

The music application is divided into several conceptual layers.

```text
┌─────────────────────────────────────────────┐
│                USER INTERFACE               │
│              Next.js Frontend               │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                    API                      │
│               Django REST API               │
└──────────────────────┬──────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────────┐   ┌──────────────────┐
│   Music Application  │   │ External Catalog │
│      PostgreSQL      │   │    Providers     │
└──────────────────────┘   └──────────────────┘
```

The VibeNation database remains the **canonical source of truth for VibeNation-owned data**.

Third-party music services may provide:

* Search results
* Artist metadata
* Song metadata
* Album metadata
* Artwork references
* Provider IDs
* Preview information
* Official listening URLs

However, external providers do not become the VibeNation database.

---

# Music System Philosophy

The system follows several important principles.

## 1. Separate catalog data from user activity

Music metadata and user engagement are different domains.

For example:

```text
Song
 ├── title
 ├── artists
 ├── album
 ├── genres
 └── metadata

SongRating
 ├── user
 ├── song
 └── rating
```

A song should not contain a list of individual user ratings inside the song record.

Instead, ratings are stored independently.

---

## 2. Separate editorial content from community content

VibeNation staff publish editorial articles.

Users publish community posts.

They are intentionally separate systems.

```text
EditorialArticle
        │
        ├── EditorialComment
        ├── EditorialArticleLike
        └── EditorialArticleReport


CommunityPost
        │
        ├── CommunityPostComment
        ├── CommunityPostLike
        └── CommunityPostReport
```

This separation makes moderation, permissions, analytics, APIs, and future features easier to manage.

---

## 3. Comments are not posts

A comment belongs to a post or article.

It cannot independently become a community post.

For example:

```text
CommunityPost
    │
    └── Comment
          │
          ├── Reply
          │    └── Reply
          │         └── Reply
          │
          └── Reply
```

A comment always has a parent content object.

---

## 4. Artists are catalog entities

Artists are **not Django users**.

An artist record represents the artist as a music/catalog entity.

Users can follow artists:

```text
User ───────────────► Artist
       ArtistFollow
```

But an artist does not log into VibeNation through the `Artist` model.

---

## 5. Store relationships as database records

User interactions such as:

* Likes
* Ratings
* Favorites
* Follows
* Reports

are represented by their own database models.

This provides better integrity, querying, moderation, analytics, and scalability.

---

# Application Structure

The recommended structure for the music application is:

```text
music/
│
├── README.md
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   ├── COMMUNITY_SYSTEM.md
│   ├── EDITORIAL_SYSTEM.md
│   ├── ENGAGEMENT_SYSTEM.md
│   ├── MUSIC_CATALOG.md
│   ├── ADMIN.md
│   └── API.md
│
├── migrations/
│
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── services.py
└── tests/
```

The exact structure may evolve as the application becomes larger.

The important principle is that the codebase should remain separated by responsibility.

---

# Domain Areas

The music application contains five major domains.

```text
┌─────────────────────────────────────────┐
│              MUSIC CATALOG              │
│ Artist / Album / Song / Genre / Track   │
└────────────────────┬────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌─────────────────────┐ ┌──────────────────┐
│     EDITORIAL       │ │    COMMUNITY     │
│      Articles       │ │      Posts       │
└──────────┬──────────┘ └────────┬─────────┘
           │                     │
           └──────────┬──────────┘
                      ▼
             ┌─────────────────┐
             │   ENGAGEMENT    │
             │ Likes / Ratings │
             │ Favorites / etc│
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │   SOCIAL GRAPH  │
             │ Follows / Feed  │
             └─────────────────┘
```

---

# Music Catalog

The music catalog contains the core music entities.

## Main catalog models

* `Genre`
* `Artist`
* `Album`
* `AlbumTrack`
* `Song`

These models describe music itself rather than user activity.

### Genre

Represents a music genre.

Examples:

```text
Afrobeats
Hip-Hop
R&B
Pop
Amapiano
Gospel
```

A genre may be associated with multiple songs and editorial articles.

---

### Artist

Represents a music artist.

Important:

> `Artist` is not a Django `User`.

An artist may be associated with:

* Songs
* Albums
* Editorial articles
* Community post targets
* User follows

The model also contains a cached `followers_count` value for efficient display and ranking.

---

### Album

Represents an album, EP, mixtape, or similar collection.

An album can contain:

* Multiple artists
* Multiple tracks
* Ratings
* Favorites
* Editorial articles

---

### AlbumTrack

Represents the relationship between an album and a song while preserving track order.

For example:

```text
Album: Example EP

1. Intro
2. Song A
3. Song B
4. Song C
5. Outro
```

`AlbumTrack` allows the same song to exist independently while appearing in different album contexts.

---

### Song

Represents an individual music recording.

A song may be associated with:

* One or more artists
* Featured artists
* An album
* Genres
* Ratings
* Favorites
* Community posts
* Editorial articles

The model should contain music metadata, not individual user interactions.

---

# Editorial System

The editorial system contains content created by VibeNation's staff.

The primary model is:

```text
EditorialArticle
```

An editorial article can discuss:

* A song
* An artist
* An album
* A music event
* A music-related topic

Editorial articles can have:

* Genres
* Related music entities
* Likes
* Comments
* Replies
* Views
* Reports

Editorial content is controlled by the VibeNation editorial/admin team.

Users interact with it, but they do not create the article itself.

---

# Community System

The community system allows registered users to create music-related posts.

The primary model is:

```text
CommunityPost
```

A community post may contain:

* User-written content
* A rating
* A selected music target
* Likes
* Comments
* Replies
* Views
* Reports

The post may target:

```text
Song
Album
Artist
External Music Provider Item
```

This is handled through:

```text
CommunityPostTarget
```

---

# Engagement System

The engagement system stores user interactions.

Examples include:

```text
SongRating
AlbumRating

SongFavorite
AlbumFavorite

CommunityPostLike
EditorialArticleLike

CommunityPostCommentLike
EditorialCommentLike
```

These should remain separate from the main catalog models.

---

# Social Graph

The social graph contains relationships between users and other users or music entities.

There are two major follow systems.

### User following

```text
User ───────► User
       UserFollow
```

### Artist following

```text
User ───────► Artist
      ArtistFollow
```

These relationships can later power:

* Personalized feeds
* Notifications
* Recommendations
* Following pages
* Trending systems
* User discovery

---

# Core Models

The application currently contains the following major models:

```text
TimeStampedModel

Genre

Artist
Album
AlbumTrack
Song

SongRating
AlbumRating

EditorialArticle
EditorialComment
EditorialArticleLike
EditorialCommentLike
EditorialArticleReport
EditorialCommentReport

CommunityPost
CommunityPostTarget
CommunityPostComment
CommunityPostLike
CommunityPostCommentLike
CommunityPostReport
CommunityPostCommentReport

SongFavorite
AlbumFavorite

ArtistFollow
UserFollow
```

The detailed field-by-field explanation of these models belongs in:

`docs/DATA_MODEL.md`

---

# Important Relationships

A simplified relationship map looks like this:

```text
Artist
  │
  ├──────────────► Song
  │                  │
  │                  ├── SongRating
  │                  ├── SongFavorite
  │                  └── CommunityPostTarget
  │
  ├──────────────► Album
  │                  │
  │                  ├── AlbumTrack ─────► Song
  │                  ├── AlbumRating
  │                  └── AlbumFavorite
  │
  └──────────────► ArtistFollow
```

Community:

```text
CommunityPost
     │
     ├── CommunityPostTarget
     │
     ├── CommunityPostLike
     │
     ├── CommunityPostComment
     │        │
     │        ├── Reply
     │        └── Reply
     │
     └── CommunityPostReport
```

Editorial:

```text
EditorialArticle
      │
      ├── EditorialArticleLike
      ├── EditorialComment
      │       │
      │       └── Reply
      └── EditorialArticleReport
```

---

# Community Posts

A community post is a standalone piece of user-generated content.

The typical creation flow is:

```text
User
  │
  ▼
Search for music
  │
  ▼
Third-party music catalog
  │
  ▼
Search results
  │
  ▼
User selects music
  │
  ▼
CommunityPostTarget
  │
  ▼
User writes opinion/review
  │
  ▼
CommunityPost
```

The user should not have to manually type information such as:

```text
Song title
Artist name
Album name
Artwork
Provider ID
```

when the platform already has that information from a selected catalog result.

This reduces:

* Duplicate records
* Spelling inconsistencies
* Incorrect metadata
* Fake music entries
* Poor search quality

---

# CommunityPostTarget

`CommunityPostTarget` provides an abstraction between a community post and the music item being discussed.

A post can target an internal VibeNation entity:

```text
Song
Album
Artist
```

or an external music-provider item.

Conceptually:

```text
CommunityPost
       │
       ▼
CommunityPostTarget
       │
       ├── Internal Song
       ├── Internal Album
       ├── Internal Artist
       │
       └── External Provider Item
```

This abstraction allows the external music catalog integration to evolve without redesigning the community post system.

---

# Comments and Replies

Comments are separate from posts.

A comment belongs to:

```text
CommunityPost
```

or:

```text
EditorialArticle
```

Replies use a self-referencing parent relationship.

For example:

```text
Comment A
   │
   ├── Reply B
   │      │
   │      └── Reply C
   │
   └── Reply D
          │
          └── Reply E
```

This allows deeply nested discussions.

A reply is still a comment record.

It does **not** become a `CommunityPost`.

This distinction is extremely important.

---

# Ratings

The platform uses two different rating systems.

## Community ratings

Community users rate music using:

```text
0.5 → 5.0
```

Examples:

```text
0.5
1.0
1.5
2.0
...
4.5
5.0
```

Community ratings are represented through:

```text
SongRating
AlbumRating
```

---

## Editorial ratings

Editorial content can use a:

```text
0 → 10
```

editorial score.

This allows VibeNation staff to provide a professional/editorial assessment without mixing it with community ratings.

---

# Average Ratings

Average ratings should **not initially be stored as a permanent field on the Song or Album model**.

For example, avoid:

```text
average_rating = 4.73
```

as a source-of-truth field.

Instead, calculate the average from the underlying rating records.

Conceptually:

```text
Song
 │
 ├── Rating: 5.0
 ├── Rating: 4.5
 ├── Rating: 4.0
 └── Rating: 5.0

Average = calculated from rating records
```

This prevents synchronization problems.

The database records remain the source of truth.

If performance eventually requires caching the calculated average, that should be introduced deliberately as a read optimization with clearly defined update rules.

---

# Likes, Favorites and Follows

These are different concepts and should never be treated as the same interaction.

## Like

A user likes content.

Examples:

```text
CommunityPostLike
EditorialArticleLike
CommunityPostCommentLike
EditorialCommentLike
```

---

## Favorite

A user saves music for personal access.

Examples:

```text
SongFavorite
AlbumFavorite
```

A favorite is not automatically a like.

---

## Follow

A user subscribes to another entity's activity.

Examples:

```text
ArtistFollow
UserFollow
```

A follow is not a favorite.

---

# View Counts

The system tracks views independently for relevant content.

Examples:

```text
EditorialArticle.views_count
CommunityPost.views_count
EditorialComment.views_count
CommunityPostComment.views_count
```

Views should be incremented through the API/service layer rather than through arbitrary model behavior.

Conceptually:

```text
Request
   │
   ▼
API / Service
   │
   ▼
Validate view
   │
   ▼
Increment counter
```

This gives the application control over:

* Duplicate-view prevention
* Authentication requirements
* Rate limiting
* Analytics
* Abuse prevention
* Future view-event tracking

---

# Artist Architecture

Artists are catalog entities.

They are not user accounts.

This means:

```text
Artist ≠ User
```

There should be no assumption that an artist can:

* Log into VibeNation through the Artist model
* Publish directly as an Artist model
* Have authentication credentials
* Own a Django user account

Instead:

```text
User
  │
  │ follows
  ▼
Artist
```

The relationship is represented by:

```text
ArtistFollow
```

The `followers_count` field on `Artist` is a cached count used for efficient display and ranking.

Example:

```text
Tems
48K followers
```

The actual user-to-artist relationships remain stored in `ArtistFollow`.

---

# Third-Party Music Metadata

VibeNation does not need to manually maintain every piece of music metadata entered by users.

When a user wants to create a review or opinion post, the frontend can provide a music search experience.

Conceptually:

```text
User types:

"Essence"

        ↓

VibeNation API

        ↓

Music Catalog Provider

        ↓

Results

┌──────────────────────────────┐
│ Cover                        │
│ Song title                   │
│ Artist                       │
│ Album                        │
│ Preview                      │
│ Official listening link      │
└──────────────────────────────┘

        ↓

User selects result

        ↓

VibeNation creates target

        ↓

User writes post
```

The external provider should be treated as a **metadata/discovery source**, not VibeNation's primary database.

VibeNation's PostgreSQL database remains the source of truth for data that VibeNation owns and curates.

---

# External Provider Architecture

The integration should be designed behind VibeNation's API.

The browser should not become tightly coupled to a specific provider.

Preferred architecture:

```text
Next.js
   │
   ▼
VibeNation API
   │
   ▼
Music Catalog Service
   │
   ├── Apple Music / Apple catalog
   │
   ├── Optional secondary provider
   │
   └── Optional metadata enrichment
```

This means the frontend does not need to know every provider's API format.

Instead, VibeNation normalizes provider responses into its own structure.

For example:

```json
{
  "provider": "apple_music",
  "provider_id": "123456",
  "type": "song",
  "title": "Example Song",
  "artists": [
    {
      "name": "Example Artist"
    }
  ],
  "album": {
    "name": "Example Album"
  },
  "artwork_url": "...",
  "preview_url": "...",
  "external_url": "..."
}
```

The exact API response format may evolve.

---

# Audio Hosting Policy

VibeNation does not host downloadable music files.

The music system is designed around:

* Music discovery
* Music metadata
* Editorial analysis
* Community reviews
* Ratings
* Official listening destinations
* Approved previews where provider terms permit

The platform should not store third-party audio files simply to provide playback.

Do not introduce an `audio_file` field into the new architecture merely because an external provider exposes a preview URL.

A provider's preview URL is still controlled by that provider and its terms.

---

# Editorial vs Community Content

These two systems have different purposes.

## Editorial

Created by:

```text
VibeNation staff
```

Used for:

* Reviews
* News
* Analysis
* Features
* Interviews
* Music stories
* Editorial recommendations

Primary model:

```text
EditorialArticle
```

---

## Community

Created by:

```text
VibeNation users
```

Used for:

* Opinions
* Personal reviews
* Reactions
* Discussions
* Community ratings
* Music conversations

Primary model:

```text
CommunityPost
```

---

## Why they remain separate

Combining them would create problems with:

* Permissions
* Moderation
* Publishing workflows
* Analytics
* APIs
* Search
* Content ownership
* Trust levels

Therefore:

```text
EditorialArticle ≠ CommunityPost
```

---

# Engagement Counters

Several models contain cached counters.

Examples:

```text
likes_count
comments_count
replies_count
views_count
favorites_count
ratings_count
followers_count
```

These are **read-performance optimizations**.

They are not the primary source of truth.

For example:

```text
CommunityPostLike
```

contains the actual like relationship.

While:

```text
CommunityPost.likes_count
```

is a cached number used for fast display.

Conceptually:

```text
Database rows
     │
     ▼
Source of truth
     │
     ▼
Cached counter
     │
     ▼
Fast frontend display
```

Counters should be updated atomically through API/service logic.

---

# Database and PostgreSQL

PostgreSQL is the intended production database.

The application should be designed so that its data can be queried cleanly by:

* Django
* Django REST Framework
* Future services
* Background workers
* Analytics systems
* Potential Go services

The schema should therefore avoid unnecessary framework-specific coupling.

Important principles:

* Use relational database constraints.
* Use foreign keys for relationships.
* Use unique constraints where required.
* Use indexes for common query patterns.
* Keep source-of-truth data normalized.
* Avoid unnecessary denormalization.
* Use transactions where multiple related writes must succeed together.

---

# API Architecture

The frontend communicates with the music application through the API.

Preferred architecture:

```text
Next.js
   │
   ▼
Django REST Framework
   │
   ├── Serializers
   ├── Views
   ├── Services
   └── Models
        │
        ▼
    PostgreSQL
```

The API should expose resources rather than leaking internal database implementation details.

For example:

```text
GET /api/v1/music/songs/
GET /api/v1/music/songs/<id>/

GET /api/v1/music/albums/
GET /api/v1/music/albums/<id>/

GET /api/v1/music/artists/
GET /api/v1/music/artists/<id>/

GET /api/v1/music/community-posts/
POST /api/v1/music/community-posts/

GET /api/v1/music/community-posts/<id>/comments/
POST /api/v1/music/community-posts/<id>/comments/
```

Exact endpoints are documented separately in:

`docs/API.md`

---

# Admin Architecture

The admin system is intended primarily for:

* Music catalog management
* Editorial content management
* Moderation
* Reports
* Reviewing platform-generated engagement
* Managing genres and catalog metadata

Staff should not manually fabricate normal user activity.

For example, administrators should generally not use the admin panel to manually create:

```text
SongRating
AlbumRating
SongFavorite
AlbumFavorite
ArtistFollow
UserFollow
```

These are normally generated by the user-facing application.

The admin interface can inspect and moderate these records.

---

# Caching and Performance

Caching should be introduced where it provides a measurable benefit.

Good candidates may include:

* Popular songs
* Trending songs
* Popular artists
* Frequently requested albums
* Public catalog pages
* Editorial homepage sections
* Community feed fragments

However, caching should not replace the database as the source of truth.

General principle:

```text
PostgreSQL
    │
    │ source of truth
    ▼
Application
    │
    │ cache where useful
    ▼
Redis / Cache
    │
    ▼
Fast API responses
```

Do not add caching merely because a feature can be cached.

Measure first.

---

# Future Scalability

The current architecture is intentionally suitable for Django/DRF while leaving room for future high-concurrency services.

A future architecture could look like:

```text
                    ┌──────────────────┐
                    │    Next.js       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    API Gateway   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Django/DRF        Go Service     Workers
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                       PostgreSQL
```

Go or another high-performance service may eventually be useful for extremely high-concurrency workloads such as:

* Feed generation
* Realtime interactions
* High-volume counters
* Recommendation workloads
* Analytics ingestion

But these services should only be introduced when actual scale justifies them.

The initial Django architecture should remain clean and maintainable.

---

# Development Rules

Developers working on this application should follow these rules.

## Rule 1 — Do not mix domains unnecessarily

Do not turn a music catalog model into a social interaction model.

Bad:

```text
Song
 ├── users_who_liked
 ├── users_who_rated
 ├── users_who_favorited
 └── users_who_followed
```

Prefer separate relationship models.

---

## Rule 2 — Do not make artists users

```text
Artist ≠ User
```

Artists are catalog entities.

---

## Rule 3 — Comments cannot become posts

A comment is always attached to an article or community post.

---

## Rule 4 — Do not store average ratings as the primary source of truth

Calculate them from rating records unless a deliberate caching strategy is introduced later.

---

## Rule 5 — Do not host copyrighted music files

The music system is not an MP3 download service.

Use metadata, official listening destinations, and provider-approved previews where permitted.

---

## Rule 6 — Do not expose third-party provider architecture directly to the frontend

Normalize provider responses through the VibeNation backend.

---

## Rule 7 — Use database constraints

Important business rules should be enforced at the database/model level whenever possible.

---

## Rule 8 — Update counters atomically

Counters such as:

```text
likes_count
comments_count
ratings_count
followers_count
```

should be updated safely to prevent race conditions.

---

## Rule 9 — Keep migrations under version control

Never casually delete or modify production migration history.

---

## Rule 10 — Prefer source-of-truth records

Cached counters can be rebuilt.

Relationship records cannot simply be guessed.

---

# Migration Rules

Django migrations are part of the application's schema history.

Before changing models:

```bash
python manage.py makemigrations music
```

Review the generated migration.

Then apply it:

```bash
python manage.py migrate
```

Check migration state:

```bash
python manage.py showmigrations music
```

Generate SQL when necessary:

```bash
python manage.py sqlmigrate music <migration_number>
```

Never manually edit migration history just to make Django think a schema exists.

If a database becomes inconsistent, investigate:

1. Migration state
2. Existing database tables
3. Migration SQL
4. Whether data exists
5. Whether the migration can safely be reversed

Destructive database operations should only be performed when data loss is understood and explicitly acceptable.

---

# Documentation

The `README.md` is the entry point.

Detailed documentation should be separated into focused files.

Recommended documentation:

```text
docs/
│
├── ARCHITECTURE.md
│
├── DATA_MODEL.md
│
├── COMMUNITY_SYSTEM.md
│
├── EDITORIAL_SYSTEM.md
│
├── ENGAGEMENT_SYSTEM.md
│
├── MUSIC_CATALOG.md
│
├── ADMIN.md
│
└── API.md
```

### `ARCHITECTURE.md`

Explains:

* System architecture
* Application boundaries
* Data flow
* Service boundaries
* Future scalability

### `DATA_MODEL.md`

Explains:

* Every model
* Every important field
* Relationships
* Constraints
* Why each model exists

This should be the canonical explanation of `models.py`.

### `COMMUNITY_SYSTEM.md`

Explains:

* Community posts
* Post targets
* Ratings
* Comments
* Replies
* Likes
* Reports
* Feed architecture

### `EDITORIAL_SYSTEM.md`

Explains:

* Editorial articles
* Publishing
* Featuring
* Editorial comments
* Moderation
* Editorial engagement

### `ENGAGEMENT_SYSTEM.md`

Explains:

* Likes
* Favorites
* Ratings
* Follows
* Views
* Counters

### `MUSIC_CATALOG.md`

Explains:

* Artists
* Albums
* Songs
* Tracks
* Genres
* External music providers
* Metadata synchronization

### `ADMIN.md`

Explains:

* Master admin
* Staff admin
* Permissions
* Moderation
* Catalog management

### `API.md`

Explains:

* API endpoints
* Authentication
* Request/response formats
* Pagination
* Filtering
* Search
* Errors

---

# Developer Checklist

Before adding a new music feature, ask:

### Data

* Does this need a new model?
* Does an existing model already represent this concept?
* Is this catalog data or user activity?
* Should this be a relationship table?

### Relationships

* What owns this relationship?
* Should it use a foreign key?
* Should it have a unique constraint?
* Can the relationship be deleted independently?

### User activity

* Is this a like?
* Rating?
* Favorite?
* Follow?
* Report?
* View?

If so, consider whether it belongs in its own model.

### API

* Does the frontend actually need this field?
* Should the endpoint be public or authenticated?
* Does the endpoint require pagination?
* Could the query cause N+1 problems?

### Performance

* Does this query need an index?
* Should the result be cached?
* Is a counter actually necessary?
* Can `select_related()` or `prefetch_related()` improve the query?

### Security

* Can a user modify another user's record?
* Can users fabricate engagement?
* Can users submit invalid provider IDs?
* Can users spam comments or ratings?

### Moderation

* Can this content be reported?
* Can staff remove or review it?
* Does the admin interface expose the necessary information?

---

# Golden Rules

These are the rules that should remain true even if the implementation changes.

> **1. Artists are catalog entities, not users.**

> **2. Music metadata and user activity are separate domains.**

> **3. Comments are not community posts.**

> **4. Replies remain comments using a self-referencing relationship.**

> **5. Community ratings and editorial scores are different systems.**

> **6. Database relationship records are the source of truth for engagement.**

> **7. Cached counters are optimizations, not sources of truth.**

> **8. Average ratings should not be unnecessarily denormalized.**

> **9. VibeNation does not host downloadable copyrighted music.**

> **10. External music providers supply discovery/metadata; VibeNation owns its internal catalog and community data.**

> **11. The frontend should communicate through the VibeNation API rather than becoming tightly coupled to external providers.**

> **12. Django/DRF is the current core backend; future high-performance services should be introduced only when justified by scale.**

---

# Final Mental Model

If a new developer remembers nothing else, they should understand this:

```text
                         VIBENATION
                             │
                             ▼
                      MUSIC CATALOG
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
        Artist             Album              Song
          │                  │                  │
          │                  ▼                  │
          │              AlbumTrack             │
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
        EDITORIAL                       COMMUNITY
              │                             │
              ▼                             ▼
      EditorialArticle              CommunityPost
              │                             │
              ▼                             ▼
      EditorialComment              CommunityComment
              │                             │
              └──────────────┬──────────────┘
                             ▼
                         ENGAGEMENT
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
        Likes             Ratings           Favorites
                             │
                             ▼
                          Follows
                             │
                             ▼
                       SOCIAL GRAPH
```

The entire system can therefore be understood as:

```text
Music entities
     +
Editorial content
     +
Community content
     +
User engagement
     +
Social relationships
     =
VibeNation Music Platform
```

The system should remain modular, relational, API-first, and ready to scale without sacrificing clarity.
