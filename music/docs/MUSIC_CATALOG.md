# VibeNation Music Catalog

## Table of Contents

* [1. Purpose](#1-purpose)
* [2. Music Catalog Overview](#2-music-catalog-overview)
* [3. Core Principle](#3-core-principle)
* [4. Catalog Entities](#4-catalog-entities)

  * [4.1 Genre](#41-genre)
  * [4.2 Artist](#42-artist)
  * [4.3 Album](#43-album)
  * [4.4 Album Track](#44-album-track)
  * [4.5 Song](#45-song)
* [5. Artist Identity](#5-artist-identity)
* [6. Album and Track Relationships](#6-album-and-track-relationships)
* [7. Music Metadata](#7-music-metadata)
* [8. External Music Providers](#8-external-music-providers)

  * [8.1 Apple Music / iTunes Search](#81-apple-music--itunes-search)
  * [8.2 Spotify](#82-spotify)
  * [8.3 MusicBrainz](#83-musicbrainz)
* [9. External Search Flow](#9-external-search-flow)
* [10. Selecting Music for Community Posts](#10-selecting-music-for-community-posts)
* [11. CommunityPostTarget](#11-communityposttarget)
* [12. Internal vs External Music Records](#12-internal-vs-external-music-records)
* [13. Audio Policy](#13-audio-policy)
* [14. Preview Audio](#14-preview-audio)
* [15. Official Listening Links](#15-official-listening-links)
* [16. Artwork and Images](#16-artwork-and-images)
* [17. Metadata Ownership](#17-metadata-ownership)
* [18. Metadata Synchronization](#18-metadata-synchronization)
* [19. Catalog Quality and Deduplication](#19-catalog-quality-and-deduplication)
* [20. Ratings and Catalog Entities](#20-ratings-and-catalog-entities)
* [21. Favorites and Catalog Entities](#21-favorites-and-catalog-entities)
* [22. Editorial Content and the Catalog](#22-editorial-content-and-the-catalog)
* [23. Search and Discovery](#23-search-and-discovery)
* [24. API Responsibilities](#24-api-responsibilities)
* [25. Caching](#25-caching)
* [26. Performance and Scalability](#26-performance-and-scalability)
* [27. PostgreSQL Considerations](#27-postgresql-considerations)
* [28. Future Catalog Expansion](#28-future-catalog-expansion)
* [29. Developer Workflow](#29-developer-workflow)
* [30. Golden Rules](#30-golden-rules)
* [31. Final Mental Model](#31-final-mental-model)

---

# 1. Purpose

The VibeNation music catalog is the foundation of the platform's music-related features.

It provides structured records for:

* Artists
* Albums
* Songs
* Album tracks
* Genres

The catalog is used by:

* Community posts
* Editorial articles
* Ratings
* Favorites
* Artist following
* Music discovery
* Search
* Recommendations
* Music reviews
* Statistics and analytics

VibeNation is **not a music-download platform**.

The catalog stores and organizes music information while directing users toward legitimate external listening platforms.

---

# 2. Music Catalog Overview

The catalog has two related responsibilities.

### Internal catalog

VibeNation maintains its own structured records for music that becomes important to the platform.

For example:

```text
Artist
   │
   ├── Album
   │      │
   │      ├── AlbumTrack → Song
   │      ├── AlbumTrack → Song
   │      └── AlbumTrack → Song
   │
   └── Song
```

These records become the stable internal references used by VibeNation's database.

### External discovery

Users may discover music that does not yet exist in VibeNation's database.

Instead of forcing administrators to manually create every song first, VibeNation can search external music catalogs.

```text
User
  ↓
VibeNation search
  ↓
External music catalog
  ↓
Search results
  ↓
User selects music
  ↓
VibeNation creates/uses internal catalog reference
```

This makes the community posting experience much faster.

---

# 3. Core Principle

The most important catalog principle is:

> **VibeNation owns the organization of its platform catalog, not the underlying copyrighted music.**

The platform should store metadata and references required for its own functionality.

It should not become an unauthorized music-hosting service.

Therefore:

```text
Metadata        → VibeNation
Community data  → VibeNation
Editorial data  → VibeNation
Ratings         → VibeNation
Favorites       → VibeNation
Social graph    → VibeNation

Full audio      → External licensed platform
```

---

# 4. Catalog Entities

## 4.1 Genre

`Genre` represents a music genre used by VibeNation.

Genres can be attached to songs and editorial content.

Examples:

```text
Afrobeats
Hip-Hop
R&B
Pop
Amapiano
Highlife
```

Genres are VibeNation catalog records.

They allow the platform to:

* Categorize music
* Filter searches
* Build genre pages
* Support discovery
* Relate editorial content to musical styles

---

## 4.2 Artist

`Artist` represents a music artist in the VibeNation catalog.

An artist is a **catalog/editorial entity**.

An artist is **not a Django user**.

This distinction is critical.

```text
Artist
  ├── name
  ├── metadata
  ├── followers_count
  └── catalog relationships
```

There is no requirement for an artist to:

* Register
* Log in
* Have a password
* Own a VibeNation account
* Create community posts
* Moderate content

VibeNation users can follow artist records.

```text
User ────── ArtistFollow ────── Artist
```

The `followers_count` field on Artist is a cached count of VibeNation users following that artist.

---

## 4.3 Album

`Album` represents an album or other release grouping maintained by the catalog.

An album can contain:

* Album metadata
* Artists
* Tracks
* Publication information
* Favorites
* Ratings

Conceptually:

```text
Album
 ├── Artists
 ├── AlbumTracks
 ├── Favorites
 └── Ratings
```

Albums may also be referenced by editorial articles and community content.

---

## 4.4 Album Track

`AlbumTrack` represents the relationship between an album and a song.

It answers:

> "Which song appears on this album, and where?"

For example:

```text
Album: African Sunrise

Track 1 → Song A
Track 2 → Song B
Track 3 → Song C
```

The track number determines the song's position within the album.

This relationship is separated from `Song` because a song and its placement within an album are conceptually different things.

---

## 4.5 Song

`Song` represents a track in the VibeNation music catalog.

A song can have relationships with:

* Artists
* Featured artists
* Genres
* Albums through `AlbumTrack`
* Ratings
* Favorites
* Editorial content
* Community content

Conceptually:

```text
Song
 ├── Artists
 ├── Featured Artists
 ├── Genres
 ├── AlbumTrack
 ├── Ratings
 └── Favorites
```

A song is the primary catalog entity for song-specific discussion and reviews.

---

# 5. Artist Identity

Artist identity must remain separate from platform user identity.

The system should never assume:

```text
Artist = User
```

Instead:

```text
User
  ↓
ArtistFollow
  ↓
Artist
```

This allows a user to follow an artist without requiring the artist to have a VibeNation account.

It also allows VibeNation to represent artists who have never interacted with the platform.

This architecture is important for:

* Artist discovery
* Artist pages
* Follower counts
* Editorial content
* Song metadata
* Recommendations
* Music search

---

# 6. Album and Track Relationships

Albums and songs use `AlbumTrack` to establish their relationship.

The conceptual structure is:

```text
Album
   │
   ├── AlbumTrack #1 ── Song A
   ├── AlbumTrack #2 ── Song B
   ├── AlbumTrack #3 ── Song C
   └── AlbumTrack #4 ── Song D
```

This provides an explicit track ordering.

The same song may theoretically appear in more than one release context, so the album-track relationship should not assume that a Song belongs to exactly one Album.

---

# 7. Music Metadata

Typical catalog metadata can include information such as:

* Title
* Artist name
* Featured artists
* Album
* Genre
* Cover artwork
* Release date
* Track number
* Duration
* External identifiers
* External listening links

Metadata received from an external provider should not automatically be treated as permanent VibeNation truth.

External metadata is an input.

VibeNation's internal catalog becomes the platform's canonical representation once a record is adopted into the database.

---

# 8. External Music Providers

External music providers are used primarily for **discovery and enrichment**.

The architecture should avoid tightly coupling the entire application to one provider.

A provider may change:

* API rules
* response structures
* authentication requirements
* available metadata
* preview availability
* commercial usage restrictions

Therefore external providers should sit behind VibeNation's own catalog/search layer.

---

## 8.1 Apple Music / iTunes Search

Apple's music catalog is a strong candidate for VibeNation's primary discovery source.

Apple's ecosystem can provide information such as:

* Song title
* Artist
* Album
* Artwork
* Genre
* Duration
* External store/listening URL
* Preview information where available

The older iTunes Search API is particularly useful for straightforward catalog search.

The current Apple Music API can also provide catalog resources and preview information.

The application should treat Apple's terms and usage requirements as part of the integration design.

---

## 8.2 Spotify

Spotify can be used as another music provider and official listening destination.

Spotify is particularly useful for:

* Official track links
* Album links
* Artist links
* Music discovery

However, Spotify's Web API preview behavior and availability can change, and preview URLs are not guaranteed for every track.

Therefore Spotify should not be treated as the sole preview source.

The system should also avoid assuming that every Spotify track has a playable preview.

---

## 8.3 MusicBrainz

MusicBrainz can be used as a metadata and identity enrichment source.

It is useful for information such as:

* Artists
* Recordings
* Releases
* Release groups
* Relationships
* ISRC-related metadata

MusicBrainz is better viewed as a metadata/identity resource than as VibeNation's user-facing music player.

---

# 9. External Search Flow

The preferred architecture is:

```text
User searches for a song
        ↓
VibeNation API
        ↓
Music catalog provider
        ↓
Provider response
        ↓
VibeNation normalizes result
        ↓
Frontend displays result
```

The frontend should not directly depend on provider-specific response formats.

For example, the frontend should not have to know that one provider calls a field:

```text
trackName
```

while another calls it:

```text
name
```

Instead VibeNation should normalize provider responses into a consistent internal structure.

Example:

```json
{
  "title": "Example Song",
  "artist_name": "Example Artist",
  "album_name": "Example Album",
  "artwork_url": "...",
  "preview_url": "...",
  "apple_music_url": "...",
  "spotify_url": "..."
}
```

The exact API response structure may evolve independently of the external provider.

---

# 10. Selecting Music for Community Posts

When a user creates a community post about music, they should not manually type the music metadata.

The intended experience is:

```text
Create Post
    ↓
Search music
    ↓
Select result
    ↓
Write opinion/review
    ↓
Add rating
    ↓
Publish
```

For example:

```text
User searches:

"Tems Me & U"
```

The application searches the configured music catalog provider.

The user sees something like:

```text
[Cover]

Me & U
Tems

▶ Preview

Apple Music
Spotify
```

The user selects the result.

The selected music becomes the target of the community post.

This prevents problems such as:

```text
User enters:
Title = "Me and You"
Artist = "TEMS"
Album = "..."
```

when the canonical metadata should actually be different.

---

# 11. CommunityPostTarget

`CommunityPostTarget` is the abstraction connecting a community post to the music it discusses.

A community post should be about a selected music entity rather than requiring the author to manually type music metadata.

The target can represent internal VibeNation catalog entities or external provider metadata where appropriate.

Conceptually:

```text
CommunityPost
      │
      ↓
CommunityPostTarget
      │
      ├── Song
      ├── Album
      ├── Artist
      │
      └── External provider metadata
```

This gives the community system flexibility without forcing every possible external search result to become a fully populated internal catalog record immediately.

The target abstraction also prevents the community-post model from becoming tightly coupled to one music provider.

---

# 12. Internal vs External Music Records

There are two different concepts:

### External result

A result returned by an external music provider.

```text
Apple Music result
Spotify result
MusicBrainz result
```

It may only exist temporarily during search.

### Internal catalog record

A VibeNation database entity.

```text
Song
Album
Artist
Genre
```

It is used by the platform's own features.

The system should not blindly import every external search result into PostgreSQL.

A user searching for a song does not necessarily mean VibeNation needs a permanent catalog record for every result returned.

The application should import or associate data when there is a meaningful reason to do so.

---

# 13. Audio Policy

VibeNation does **not** host downloadable music files.

The catalog should therefore not be designed around:

```text
Song.audio_file
```

as a requirement for music playback.

The platform's music experience is based on:

* Metadata
* Discovery
* Reviews
* Ratings
* Community discussion
* Official listening links
* Permitted previews/embeds

The architecture deliberately separates music metadata from music ownership.

---

# 14. Preview Audio

Preview audio is different from hosting a full song.

Where an external provider makes a preview available and its terms permit VibeNation's intended use, the platform may expose that preview appropriately.

However:

> **The system must never assume that every song has a preview URL.**

A preview may be:

* unavailable
* region restricted
* provider restricted
* subject to commercial-use conditions
* changed or removed by the provider

The application should gracefully handle:

```text
preview_url = null
```

For example:

```text
No preview available

[Listen on Apple Music]
[Listen on Spotify]
```

VibeNation should not download, permanently store, or independently redistribute provider preview audio unless its licensing terms explicitly permit the intended behavior.

The platform should also not attempt to manufacture arbitrary 10-second clips from full copyrighted recordings.

---

# 15. Official Listening Links

The preferred approach for full-track listening is to send users to legitimate music services.

Examples include:

```text
Listen on Apple Music
Listen on Spotify
Listen on YouTube Music
```

These should be represented as external destinations rather than as VibeNation-hosted audio.

The exact providers exposed to users can evolve over time.

---

# 16. Artwork and Images

Music artwork is metadata associated with external catalog resources and/or VibeNation's internal catalog.

Artwork handling must respect the terms of the provider supplying it.

The architecture should therefore distinguish between:

```text
Artwork URL
```

and:

```text
VibeNation-hosted image
```

An external artwork URL does not automatically mean VibeNation has unrestricted rights to download, transform, permanently cache, or redistribute that image.

Where VibeNation stores artwork itself, the storage and usage must comply with the applicable rights and provider terms.

---

# 17. Metadata Ownership

VibeNation should maintain a clear distinction between:

### Provider metadata

Data received from Apple, Spotify, MusicBrainz, or another provider.

### VibeNation metadata

Data created or curated by VibeNation.

Examples of VibeNation-owned content include:

* Editorial reviews
* Editorial scores
* Community ratings
* Community posts
* Favorites
* Follows
* Comments
* Engagement statistics

For example:

```text
External provider:
    Song title
    Artist
    Album
    Artwork

VibeNation:
    Editorial review
    Editorial score
    Community rating
    Community posts
    Comments
    Favorites
```

External metadata is the foundation for discovery.

VibeNation's editorial and community layer is the platform's original value.

---

# 18. Metadata Synchronization

External metadata may change.

For example:

* Artwork may change.
* A release may receive updated metadata.
* Provider links may change.
* An artist name may be updated.

VibeNation should not continuously overwrite curated internal information simply because an external provider changed something.

Synchronization should therefore be deliberate.

The system can distinguish between:

```text
Provider-sourced fields
```

and:

```text
VibeNation-curated fields
```

Curated editorial data should never be destroyed by an automated metadata refresh.

---

# 19. Catalog Quality and Deduplication

The catalog should avoid duplicate records for the same musical entity.

A search may return:

```text
Song A
Song A (Deluxe)
Song A - Remastered
Song A - Radio Edit
```

These are not necessarily duplicates.

The system must consider identifiers and release context when deciding whether two results represent the same entity.

Useful external identifiers may include:

* Provider IDs
* ISRC
* External album/release IDs
* Other stable catalog identifiers

Deduplication should be based on identifiers and meaningful metadata rather than title matching alone.

For example:

```text
"Essence"
```

is not sufficient to identify a unique song.

---

# 20. Ratings and Catalog Entities

Ratings belong to VibeNation's internal catalog entities.

Users can rate:

* Songs
* Albums

Ratings are separate from external provider ratings.

A provider's popularity or rating value should never be confused with VibeNation's community rating.

VibeNation's rating scale is:

```text
0.5
1.0
1.5
2.0
...
4.5
5.0
```

The average is calculated from VibeNation's own rating records.

It is not copied from Apple Music, Spotify, or another external provider.

---

# 21. Favorites and Catalog Entities

Users can favorite internal catalog entities.

Currently:

```text
SongFavorite
AlbumFavorite
```

are supported.

Favorites represent the user's relationship with VibeNation's catalog.

They do not imply that VibeNation owns or hosts the underlying music.

---

# 22. Editorial Content and the Catalog

Editorial content can reference catalog entities.

An editorial article may be associated with:

* Songs
* Artists
* Albums
* Genres

For example:

```text
Editorial Article
      │
      ├── Song
      ├── Artist
      ├── Album
      └── Genres
```

This allows VibeNation to publish content such as:

* Song reviews
* Album reviews
* Artist features
* Music news
* Release analysis
* Rankings
* Recommendations

The editorial layer adds human/contextual value on top of the structured catalog.

---

# 23. Search and Discovery

The music catalog should support several search experiences.

### Music search

Used when a user wants to find a song, album, or artist.

### Catalog search

Used to find music already represented internally by VibeNation.

### Editorial search

Used to discover articles related to music.

### Community discovery

Used to find community discussions surrounding music.

Eventually these can be combined into a broader discovery system:

```text
Search
  │
  ├── Songs
  ├── Albums
  ├── Artists
  ├── Genres
  ├── Editorial
  └── Community
```

---

# 24. API Responsibilities

The backend should act as the boundary between the frontend and external music providers.

The frontend should communicate with VibeNation:

```text
Next.js
   ↓
VibeNation API
   ↓
Music provider
```

rather than:

```text
Next.js
   ↓
Apple API
```

for core application behavior.

This provides several advantages:

* Provider credentials remain server-side.
* Provider-specific response formats stay inside the backend.
* Rate limiting can be controlled.
* Search results can be normalized.
* Caching can be added.
* Providers can be replaced later.
* Abuse can be monitored.
* Business logic stays centralized.

---

# 25. Caching

External music searches can be expensive in terms of latency and provider limits.

VibeNation can cache appropriate search results.

For example:

```text
User searches "Davido"
        ↓
Check cache
        ↓
Cache hit → return results
        │
        └── Cache miss
                ↓
          External provider
                ↓
              Cache
                ↓
          Return results
```

Caching should respect provider terms and should not be used to circumvent restrictions on storing or redistributing provider content.

The cache strategy should be based on what the provider permits.

---

# 26. Performance and Scalability

The catalog architecture should remain simple enough to scale naturally.

The primary database remains PostgreSQL in production.

Common high-read operations include:

* Song pages
* Artist pages
* Album pages
* Genre pages
* Search
* Community post targets
* Editorial relationships

These can later benefit from:

* Database indexes
* Query optimization
* Redis caching
* API caching
* CDN delivery for permitted media
* Search infrastructure

The application should not introduce a separate microservice merely because music search exists.

Django/DRF can own the catalog integration initially.

---

# 27. PostgreSQL Considerations

PostgreSQL is the intended production database.

Catalog tables should use appropriate indexes for common queries.

Potential indexing areas include:

```text
Artist.name
Album.title
Song.title
Genre.name
AlbumTrack.track_number
External provider identifiers
```

The exact indexes should be determined from actual query patterns and production profiling rather than added indiscriminately.

Database constraints should protect catalog integrity.

For example:

* Required relationships should not silently accept invalid data.
* Track numbers should remain valid.
* Duplicate relationships should be prevented where appropriate.
* External identifiers should be handled carefully.

---

# 28. Future Catalog Expansion

The catalog can eventually support additional concepts without redesigning the entire system.

Possible future additions include:

* EPs
* Singles
* Compilations
* Mixtapes
* Music videos
* Lyrics metadata
* Producer credits
* Songwriters
* Labels
* ISRC identifiers
* UPC/EAN identifiers
* Release groups
* Regional availability
* Multiple streaming providers
* Charts
* Trending music
* Personalized recommendations

These should be introduced only when there is a real product requirement.

The current architecture should not be overloaded with speculative tables.

---

# 29. Developer Workflow

When adding a new music feature:

### Step 1 — Determine the catalog entity

Ask:

```text
Is this about a Song?
Album?
Artist?
Genre?
Release/track relationship?
```

### Step 2 — Determine ownership

Ask:

```text
Is this external provider metadata?
Or VibeNation-owned data?
```

### Step 3 — Determine the relationship

Ask:

```text
Does this belong to the catalog?
Editorial?
Community?
Engagement?
Social graph?
```

### Step 4 — Determine whether an external provider is needed

Do not add a provider dependency if VibeNation already has the required data.

### Step 5 — Keep provider logic behind the API

Do not expose provider-specific implementation details unnecessarily to the frontend.

### Step 6 — Respect provider terms

Before storing, displaying, caching, previewing, or transforming external content, verify that the intended use is permitted.

### Step 7 — Test edge cases

Test:

* Missing artwork
* Missing preview
* Missing album
* Multiple artists
* Featured artists
* Duplicate search results
* Provider errors
* Rate limits
* Deleted/unavailable external content
* Slow provider responses

---

# 30. Golden Rules

1. **VibeNation is not an MP3 hosting platform.**
2. **Songs, albums, artists, and genres are catalog entities.**
3. **Artists are not Django users.**
4. **External providers are discovery/enrichment sources, not VibeNation's database.**
5. **VibeNation's PostgreSQL database is the canonical source for VibeNation-owned catalog relationships and engagement.**
6. **Never require users to manually type music metadata when it can be selected from a catalog search.**
7. **Community posts should reference selected music through `CommunityPostTarget`.**
8. **Do not assume every song has a preview.**
9. **Do not manufacture or host unauthorized full-track audio.**
10. **Use official listening destinations for full music playback.**
11. **External metadata must not overwrite VibeNation's curated editorial content.**
12. **Do not blindly import every external search result into the database.**
13. **Use stable external identifiers when available.**
14. **Keep provider-specific logic behind VibeNation's API.**
15. **Respect every provider's API and content-usage terms.**
16. **Do not prematurely introduce microservices for catalog functionality.**
17. **Optimize with indexes and caching when actual usage requires it.**
18. **Keep the catalog layer independent from the community and editorial engagement systems.**

---

# 31. Final Mental Model

The VibeNation music catalog should be understood as the bridge between **music discovery** and **VibeNation's original content/community experience**.

```text
                 EXTERNAL MUSIC WORLD
                         │
          ┌──────────────┼──────────────┐
          │              │              │
     Apple Music      Spotify       MusicBrainz
          │              │              │
          └──────────────┼──────────────┘
                         ↓
                  VibeNation API
                         │
                 Normalize / Match
                         ↓
              ┌─────────────────────┐
              │ VibeNation Catalog  │
              │                     │
              │ Artist              │
              │ Album               │
              │ Song                │
              │ AlbumTrack          │
              │ Genre               │
              └──────────┬──────────┘
                         │
          ┌──────────────┼─────────────────┐
          ↓              ↓                 ↓
     Editorial       Community         Engagement
      Articles          Posts          Ratings
                                      Favorites
                                      Follows
                                      Likes
                                      Views
                         │
                         ↓
                User Experience
                         │
             ┌───────────┴───────────┐
             ↓                       ↓
       VibeNation content      Official listening
                                  platforms
```

The key idea is simple:

> **External providers help VibeNation find and identify music. VibeNation owns the community, editorial, engagement, and discovery experience built around that music.**

This separation keeps the platform flexible, scalable, and much safer than building the product around hosted copyrighted audio.
