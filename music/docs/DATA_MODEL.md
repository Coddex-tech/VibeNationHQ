# VibeNation Music System — Data Model

This document is the canonical documentation for the database model layer of the VibeNation `music` application.

It explains what each model represents, why it exists, how models relate to one another, what the important fields mean, and which architectural rules developers must preserve when modifying the database schema.

The implementation is defined in:

```text
music/models.py
```

This document explains the **design and intent** behind that implementation.

If the code and this document ever disagree, the code and database migration history are the immediate technical source of truth, and this document should be updated to reflect the corrected architecture.

---

# Table of Contents

1. [Purpose](#purpose)
2. [Data Model Philosophy](#data-model-philosophy)
3. [Architecture Overview](#architecture-overview)
4. [Domain Classification](#domain-classification)
5. [Model Inventory](#model-inventory)
6. [Shared Base Model](#shared-base-model)

   * [TimeStampedModel](#timestampedmodel)
7. [Music Catalog Models](#music-catalog-models)

   * [Genre](#genre)
   * [Artist](#artist)
   * [Album](#album)
   * [AlbumTrack](#albumtrack)
   * [Song](#song)
8. [Rating Models](#rating-models)

   * [SongRating](#songrating)
   * [AlbumRating](#albumrating)
9. [Editorial Models](#editorial-models)

   * [EditorialArticle](#editorialarticle)
   * [EditorialComment](#editorialcomment)
   * [EditorialArticleLike](#editorialarticlelike)
   * [EditorialCommentLike](#editorialcommentlike)
   * [EditorialArticleReport](#editorialarticlereport)
   * [EditorialCommentReport](#editorialcommentreport)
10. [Community Models](#community-models)

    * [CommunityPost](#communitypost)
    * [CommunityPostTarget](#communityposttarget)
    * [CommunityPostComment](#communitypostcomment)
    * [CommunityPostLike](#communitypostlike)
    * [CommunityPostCommentLike](#communitypostcommentlike)
    * [CommunityPostReport](#communitypostreport)
    * [CommunityPostCommentReport](#communitypostcommentreport)
11. [Favorite Models](#favorite-models)

    * [SongFavorite](#songfavorite)
    * [AlbumFavorite](#albumfavorite)
12. [Social Graph Models](#social-graph-models)

    * [ArtistFollow](#artistfollow)
    * [UserFollow](#userfollow)
13. [Relationship Map](#relationship-map)
14. [Community Post Architecture](#community-post-architecture)
15. [Comment and Reply Architecture](#comment-and-reply-architecture)
16. [Rating Architecture](#rating-architecture)
17. [Like Architecture](#like-architecture)
18. [Favorite Architecture](#favorite-architecture)
19. [Follow Architecture](#follow-architecture)
20. [Artist Architecture](#artist-architecture)
21. [Editorial Architecture](#editorial-architecture)
22. [Cached Counters](#cached-counters)
23. [Source of Truth](#source-of-truth)
24. [Database Constraints](#database-constraints)
25. [Indexes and Query Performance](#indexes-and-query-performance)
26. [Deletion and Cascade Behavior](#deletion-and-cascade-behavior)
27. [Authentication and User Relationships](#authentication-and-user-relationships)
28. [Third-Party Music Metadata](#third-party-music-metadata)
29. [Audio and Media Storage](#audio-and-media-storage)
30. [API Implications](#api-implications)
31. [Admin Implications](#admin-implications)
32. [Migration Strategy](#migration-strategy)
33. [Future Scalability](#future-scalability)
34. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
35. [Adding a New Model](#adding-a-new-model)
36. [Developer Checklist](#developer-checklist)
37. [Golden Rules](#golden-rules)
38. [Final Mental Model](#final-mental-model)

---

# Purpose

The VibeNation music database is designed to represent five major categories of information:

```text
1. Music Catalog
2. Editorial Content
3. Community Content
4. User Engagement
5. Social Relationships
```

These categories are deliberately separated.

The database should represent music entities independently from the actions users perform on those entities.

For example:

```text
Song
```

represents a song.

While:

```text
SongRating
SongFavorite
```

represent actions performed by users on that song.

This distinction is one of the most important architectural decisions in the application.

---

# Data Model Philosophy

The data model follows several principles.

## 1. Normalize important relationships

Relationships such as:

* ratings
* likes
* favorites
* follows
* reports

are represented by dedicated models.

This prevents large amounts of user activity from being embedded directly into catalog records.

---

## 2. Separate content ownership

There are two different content owners:

```text
VibeNation Editorial Team
```

and:

```text
VibeNation Users
```

Therefore:

```text
EditorialArticle
```

and:

```text
CommunityPost
```

are separate models.

---

## 3. Keep the catalog independent

Music catalog entities should not depend on community activity.

A song must still exist even if:

* nobody has rated it
* nobody has favorited it
* nobody has reviewed it
* nobody has commented on it

---

## 4. User activity belongs in relationship models

Instead of:

```text
Song
 └── users_who_liked
```

use:

```text
Song
  ▲
  │
SongFavorite
  │
  ▼
User
```

This makes the relationship queryable, constrainable, and scalable.

---

## 5. Cached counters are optimizations

Fields such as:

```text
likes_count
comments_count
followers_count
ratings_count
views_count
```

are cached values for efficient reads.

They are not the underlying source of truth.

---

# Architecture Overview

The data model can be divided into layers.

```text
┌────────────────────────────────────────────┐
│                 MUSIC CATALOG              │
│                                            │
│ Genre / Artist / Album / AlbumTrack / Song │
└──────────────────────┬─────────────────────┘
                       │
          ┌────────────┴─────────────┐
          │                          │
          ▼                          ▼
┌──────────────────────┐   ┌─────────────────────┐
│      EDITORIAL       │   │      COMMUNITY      │
│                      │   │                     │
│ EditorialArticle     │   │ CommunityPost       │
│ EditorialComment     │   │ CommunityComment    │
└──────────┬───────────┘   └──────────┬──────────┘
           │                          │
           └─────────────┬────────────┘
                         │
                         ▼
               ┌────────────────────┐
               │     ENGAGEMENT     │
               │                    │
               │ Likes              │
               │ Ratings            │
               │ Favorites          │
               │ Views              │
               │ Reports            │
               └─────────┬──────────┘
                         │
                         ▼
               ┌────────────────────┐
               │    SOCIAL GRAPH    │
               │                    │
               │ UserFollow         │
               │ ArtistFollow       │
               └────────────────────┘
```

---

# Domain Classification

| Model                        | Domain     | Purpose                     |
| ---------------------------- | ---------- | --------------------------- |
| `Genre`                      | Catalog    | Music genre                 |
| `Artist`                     | Catalog    | Music artist                |
| `Album`                      | Catalog    | Album/EP                    |
| `AlbumTrack`                 | Catalog    | Song position inside album  |
| `Song`                       | Catalog    | Individual song             |
| `SongRating`                 | Engagement | User song rating            |
| `AlbumRating`                | Engagement | User album rating           |
| `EditorialArticle`           | Editorial  | Staff-created article       |
| `EditorialComment`           | Editorial  | Comment/reply on article    |
| `EditorialArticleLike`       | Engagement | Like on article             |
| `EditorialCommentLike`       | Engagement | Like on article comment     |
| `EditorialArticleReport`     | Moderation | Report on article           |
| `EditorialCommentReport`     | Moderation | Report on article comment   |
| `CommunityPost`              | Community  | User-created post           |
| `CommunityPostTarget`        | Community  | Music item attached to post |
| `CommunityPostComment`       | Community  | Comment/reply on post       |
| `CommunityPostLike`          | Engagement | Like on community post      |
| `CommunityPostCommentLike`   | Engagement | Like on post comment        |
| `CommunityPostReport`        | Moderation | Report on community post    |
| `CommunityPostCommentReport` | Moderation | Report on post comment      |
| `SongFavorite`               | Engagement | User favorite song          |
| `AlbumFavorite`              | Engagement | User favorite album         |
| `ArtistFollow`               | Social     | User follows artist         |
| `UserFollow`                 | Social     | User follows user           |

---

# Model Inventory

The current model structure is:

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

The models are intentionally grouped by responsibility rather than by how frequently they are queried.

---

# Shared Base Model

## TimeStampedModel

`TimeStampedModel` is the common abstract base model for models that need creation and modification timestamps.

Conceptually:

```text
TimeStampedModel
 ├── created_at
 └── updated_at
```

Because it is abstract, Django does not create a separate database table for it.

Instead, its fields are inherited by concrete models.

For example:

```text
Song
 ├── created_at
 └── updated_at
```

and:

```text
CommunityPost
 ├── created_at
 └── updated_at
```

This avoids duplicating timestamp definitions throughout the application.

---

# Music Catalog Models

The catalog layer represents music itself.

```text
Genre
Artist
Album
AlbumTrack
Song
```

These models should not depend on user activity.

---

# Genre

`Genre` represents a musical genre.

Examples:

```text
Afrobeats
Amapiano
Hip-Hop
R&B
Pop
Gospel
Dancehall
```

A genre may be associated with multiple songs.

Genres may also be associated with editorial articles where relevant.

### Responsibilities

`Genre` should contain information that describes the genre itself.

It should not contain:

* User ratings
* User favorites
* User follows
* Likes

Those belong to separate models.

### Relationship

```text
Genre
  │
  ├────────► Song
  │
  └────────► EditorialArticle
```

---

# Artist

`Artist` represents a music artist in VibeNation's catalog.

Examples:

```text
Tems
Burna Boy
Davido
Wizkid
Ayra Starr
```

## Critical architectural rule

> An `Artist` is not a Django `User`.

An artist is a catalog/editorial entity.

Artists do not automatically have:

* Login credentials
* Passwords
* User sessions
* Django authentication identities

A user may follow an artist through:

```text
ArtistFollow
```

### Artist relationships

```text
Artist
 │
 ├── Songs
 │
 ├── Albums
 │
 ├── Editorial Articles
 │
 ├── Community Post Targets
 │
 └── Artist Follows
```

### followers_count

`followers_count` is a cached count representing how many VibeNation users currently follow the artist.

The actual relationships are stored in:

```text
ArtistFollow
```

Therefore:

```text
Artist.followers_count
```

is an optimization.

It should not be treated as the source of truth.

---

# Album

`Album` represents an album, EP, mixtape, or other music collection.

An album can contain:

* Artists
* Tracks
* Ratings
* Favorites
* Editorial references

Conceptually:

```text
Album
 │
 ├── Artists
 │
 ├── AlbumTrack
 │       │
 │       └── Song
 │
 ├── AlbumRating
 │
 └── AlbumFavorite
```

### Album counters

The model contains cached counters such as:

```text
favorites_count
ratings_count
```

These should be updated when the corresponding relationship records are created or deleted.

The individual relationship records remain the source of truth.

---

# AlbumTrack

`AlbumTrack` represents the membership and ordering of a song within an album.

It exists because an album-to-song relationship contains information that belongs to the relationship itself.

Most importantly:

```text
track_number
```

Example:

```text
Album
 │
 ├── Track 1 → Song A
 ├── Track 2 → Song B
 ├── Track 3 → Song C
 └── Track 4 → Song D
```

This should not be represented merely as a simple many-to-many relationship because the relationship has additional data.

### Why AlbumTrack exists

Without `AlbumTrack`, the application would not have a clean place to store:

```text
track_number
```

It also provides a future location for album-specific track metadata if required.

---

# Song

`Song` represents an individual song.

A song may have:

* One or more primary artists
* Featured artists
* One or more genres
* An album relationship
* Publication metadata
* Ratings
* Favorites
* Community references
* Editorial references

### Important distinction

A `Song` is catalog data.

The following are **not** stored directly as lists inside the song:

```text
Users who rated it
Users who favorited it
Users who reviewed it
Users who liked it
```

Those interactions have dedicated models.

### Song counters

The model contains cached counters such as:

```text
favorites_count
ratings_count
```

The actual records remain the source of truth.

---

# Rating Models

Ratings represent explicit user scores.

There are two separate rating models:

```text
SongRating
AlbumRating
```

They are intentionally separate because songs and albums are different catalog entities.

---

# SongRating

`SongRating` represents a user's rating of a song.

The rating uses a five-star scale:

```text
0.5
1.0
1.5
2.0
...
4.5
5.0
```

A rating belongs to:

```text
User + Song
```

Conceptually:

```text
User
  │
  ▼
SongRating
  │
  ▼
Song
```

A user should not be able to create multiple active ratings for the same song.

Therefore the database should enforce uniqueness on the user/song relationship.

### Rating count

When a new rating is created:

```text
Song.ratings_count += 1
```

When a rating is deleted:

```text
Song.ratings_count -= 1
```

Editing an existing rating does not create another rating count.

---

# AlbumRating

`AlbumRating` is the album equivalent of `SongRating`.

Relationship:

```text
User + Album
```

The rating uses the same five-star scale.

A user should have at most one active rating for a particular album.

### Why it is separate

Do not attempt to create one generic rating model for songs and albums unless there is a compelling architectural reason.

Keeping them separate provides:

* Strong foreign keys
* Better database integrity
* Easier querying
* Easier API design
* Easier admin management
* Clearer business rules

---

# Editorial Models

The editorial layer contains content created by VibeNation staff.

Primary content model:

```text
EditorialArticle
```

Supporting models:

```text
EditorialComment
EditorialArticleLike
EditorialCommentLike
EditorialArticleReport
EditorialCommentReport
```

---

# EditorialArticle

`EditorialArticle` represents a staff-created article.

Examples:

* Music reviews
* Artist features
* Album reviews
* Song analysis
* Interviews
* Music news
* Editorial features

An article may be related to:

* Songs
* Artists
* Albums
* Genres

### Engagement

An article supports:

```text
likes_count
comments_count
views_count
```

These are cached counters.

Actual likes and comments are represented by their respective models.

---

# EditorialComment

`EditorialComment` represents a comment attached to an editorial article.

It also represents replies.

The model uses a self-referencing relationship.

Therefore:

```text
parent = NULL
```

means the comment is a top-level comment.

While:

```text
parent = another EditorialComment
```

means it is a reply.

Example:

```text
EditorialArticle
       │
       ▼
Comment A
   │
   ├── Reply B
   │     │
   │     └── Reply C
   │
   └── Reply D
```

### Counters

Editorial comments can contain cached:

```text
likes_count
replies_count
views_count
```

---

# EditorialArticleLike

Represents a user's like on an editorial article.

Relationship:

```text
User + EditorialArticle
```

The relationship should be unique so a user cannot like the same article multiple times simultaneously.

---

# EditorialCommentLike

Represents a user's like on an editorial comment.

Relationship:

```text
User + EditorialComment
```

Again, uniqueness prevents duplicate likes.

---

# EditorialArticleReport

Represents a report submitted against an editorial article.

Reports allow the moderation team to investigate problematic content.

Typical report information may include:

* Reporting user
* Article
* Reason
* Status
* Moderation metadata
* Timestamps

Reports are moderation records rather than engagement records.

---

# EditorialCommentReport

Represents a report submitted against an editorial comment.

Relationship:

```text
User
  │
  ▼
EditorialCommentReport
  │
  ▼
EditorialComment
```

It exists separately from article reports because comments require their own moderation lifecycle.

---

# Community Models

The community layer contains user-generated music discussions.

Primary model:

```text
CommunityPost
```

Supporting models:

```text
CommunityPostTarget
CommunityPostComment
CommunityPostLike
CommunityPostCommentLike
CommunityPostReport
CommunityPostCommentReport
```

---

# CommunityPost

`CommunityPost` represents standalone user-generated content.

A user may create a post such as:

```text
"I think this album is one of the strongest Afrobeats projects this year."
```

The post can be connected to a music item.

A community post may also contain a community rating.

### Engagement

Community posts support:

```text
likes_count
comments_count
views_count
```

### Important distinction

A community post is not a comment.

It exists independently in the community feed.

---

# CommunityPostTarget

`CommunityPostTarget` identifies the music entity that a community post is discussing.

A post may target:

```text
Song
Album
Artist
External music-provider item
```

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
      └── External Provider Metadata
```

This abstraction is important because users may discover music through an external catalog provider before the item exists in VibeNation's own curated catalog.

---

# Why CommunityPostTarget Exists

Without a target abstraction, the community post would need complicated logic such as:

```text
song_id
album_id
artist_id
spotify_id
apple_music_id
musicbrainz_id
...
```

all directly inside `CommunityPost`.

That approach becomes difficult to maintain as more providers are added.

Instead:

```text
CommunityPost
       │
       ▼
CommunityPostTarget
       │
       └── Provider abstraction
```

This allows the provider integration to evolve independently.

---

# CommunityPostComment

`CommunityPostComment` represents comments and replies attached to community posts.

It uses the same parent/self-reference concept as editorial comments.

Example:

```text
CommunityPost
      │
      ▼
Comment A
   │
   ├── Reply B
   │     │
   │     └── Reply C
   │
   └── Reply D
```

A comment cannot become a standalone community post.

---

# CommunityPostLike

Represents a user's like on a community post.

Relationship:

```text
User + CommunityPost
```

The combination should be unique.

---

# CommunityPostCommentLike

Represents a user's like on a community post comment.

Relationship:

```text
User + CommunityPostComment
```

The combination should be unique.

---

# CommunityPostReport

Represents a report against a community post.

Reports are handled by the moderation/admin system.

The reporting user does not directly delete the post.

Instead:

```text
User
  │
  ▼
Report
  │
  ▼
Moderation
  │
  ├── Review
  ├── Resolve
  ├── Dismiss
  └── Take action
```

---

# CommunityPostCommentReport

Represents a report against a community post comment.

It exists separately from post reports because comments may violate rules independently of the post itself.

---

# Favorite Models

Favorites allow users to save music for later.

Current favorite models:

```text
SongFavorite
AlbumFavorite
```

Favorites are different from likes.

---

# SongFavorite

Represents a user's saved/favorited song.

Relationship:

```text
User + Song
```

A user should only have one active favorite relationship with a song.

When created:

```text
Song.favorites_count += 1
```

When deleted:

```text
Song.favorites_count -= 1
```

---

# AlbumFavorite

Represents a user's saved/favorited album.

Relationship:

```text
User + Album
```

A user should only have one active favorite relationship with an album.

The album's cached:

```text
favorites_count
```

is updated when favorites are created or deleted.

---

# Social Graph Models

The social graph represents relationships between users and other entities.

There are two important relationship types:

```text
User → Artist
User → User
```

---

# ArtistFollow

`ArtistFollow` represents a VibeNation user's decision to follow an artist.

Relationship:

```text
User
  │
  ▼
ArtistFollow
  │
  ▼
Artist
```

This does not mean the artist has a VibeNation account.

The artist remains a catalog entity.

### followers_count

When a new follow is created:

```text
Artist.followers_count += 1
```

When a follow is removed:

```text
Artist.followers_count -= 1
```

The `ArtistFollow` records remain the source of truth.

---

# UserFollow

`UserFollow` represents one VibeNation user following another VibeNation user.

Relationship:

```text
Follower User
      │
      ▼
 UserFollow
      │
      ▼
Followed User
```

A user should not be allowed to follow themselves.

The database/model layer should enforce this rule.

User follower counts are not currently extended onto the base Django user model by this system.

---

# Relationship Map

A simplified entity relationship map:

```text
                         ┌───────────┐
                         │   Genre   │
                         └─────┬─────┘
                               │
                               ▼
┌───────────┐            ┌───────────┐
│  Artist   │───────────►│   Song    │
└─────┬─────┘            └─────┬─────┘
      │                         │
      │                         ├────► SongRating
      │                         │
      │                         └────► SongFavorite
      │
      ▼
┌───────────┐
│   Album   │
└─────┬─────┘
      │
      ▼
┌──────────────┐
│  AlbumTrack  │
└──────┬───────┘
       │
       ▼
     Song
```

Community:

```text
CommunityPost
      │
      ▼
CommunityPostTarget
      │
      ├────► Song
      ├────► Album
      ├────► Artist
      └────► External Provider Item
      │
      ├────► CommunityPostLike
      ├────► CommunityPostComment
      │           │
      │           └────► nested replies
      │
      └────► CommunityPostReport
```

Editorial:

```text
EditorialArticle
      │
      ├────► EditorialArticleLike
      ├────► EditorialComment
      │           │
      │           └────► nested replies
      │
      └────► EditorialArticleReport
```

Social:

```text
User ─────► Artist
      ArtistFollow

User ─────► User
      UserFollow
```

---

# Community Post Architecture

The community posting system is designed around a music-selection workflow.

## User flow

```text
1. User opens "Create Post"

2. User searches for music

3. VibeNation requests metadata
   from an external music catalog

4. Search results are displayed

5. User selects a result

6. VibeNation creates/uses
   CommunityPostTarget

7. User writes their opinion/review

8. User optionally provides
   a community rating

9. CommunityPost is created
```

The user should not have to manually type:

```text
Song title
Artist
Album
Artwork
Provider identifier
```

when these values are already available from the selected music result.

---

# Comment and Reply Architecture

Comments are represented using a self-referencing relationship.

The conceptual structure is:

```text
Comment
  │
  ├── parent = NULL
  │
  │   Top-level comment
  │
  └── parent = another comment
      │
      Reply
```

This permits arbitrary nesting.

Example:

```text
Comment A
│
├── Reply B
│   │
│   └── Reply C
│       │
│       └── Reply D
│
└── Reply E
```

All of these remain comment records.

There is no separate `Reply` model.

This reduces duplication and gives the API a consistent representation for comments and replies.

---

# Rating Architecture

Ratings are user-to-content relationships.

```text
User
 │
 ├──── SongRating ────► Song
 │
 └──── AlbumRating ───► Album
```

A user can rate many songs:

```text
User
 ├── Song A → 4.5
 ├── Song B → 3.0
 ├── Song C → 5.0
 └── Song D → 4.0
```

But should only have one current rating per song.

The same principle applies to albums.

---

# Rating Count Management

The catalog model contains:

```text
ratings_count
```

The rating relationship contains the actual rating.

For example:

```text
Song
 └── ratings_count = 4

SongRating
 ├── User A → 5.0
 ├── User B → 4.0
 ├── User C → 4.5
 └── User D → 3.5
```

If User E rates the song:

```text
ratings_count = 5
```

If User B edits their rating:

```text
ratings_count remains 5
```

If User B deletes their rating:

```text
ratings_count = 4
```

---

# Average Rating Strategy

Average ratings are derived from rating records.

For example:

```text
5.0
4.5
4.0
5.0
```

Average:

```text
(5.0 + 4.5 + 4.0 + 5.0) / 4
= 4.625
```

The system does not need to permanently store:

```text
average_rating = 4.625
```

on the song as its initial source of truth.

This prevents stale averages.

If the application later requires an aggressively optimized rating system, a cached average can be introduced with explicit consistency rules.

---

# Like Architecture

Likes are separate relationship records.

Example:

```text
User A ───► CommunityPost 1
User B ───► CommunityPost 1
User C ───► CommunityPost 1
```

These become:

```text
CommunityPostLike
```

records.

The post may also have:

```text
likes_count = 3
```

but the count is derived from the underlying relationships.

---

# Favorite Architecture

Favorites represent saved music.

They are intentionally separate from likes.

```text
Like
```

usually represents lightweight social appreciation.

```text
Favorite
```

represents saving something for personal access.

Therefore:

```text
SongLike
```

and:

```text
SongFavorite
```

should not be treated as interchangeable concepts.

---

# Follow Architecture

There are two follow relationships.

## Artist follow

```text
User
 │
 └── ArtistFollow ──► Artist
```

## User follow

```text
User
 │
 └── UserFollow ──► User
```

These should remain separate because their business meanings differ.

Artist following can support:

* Artist pages
* Personalized discovery
* Notifications
* Feed ranking
* Artist popularity

User following can support:

* Social feeds
* User discovery
* Activity feeds
* Notifications

---

# Artist Architecture

The distinction between `Artist` and `User` must be preserved.

```text
Artist
```

is a music entity.

```text
User
```

is an authenticated platform account.

Therefore:

```text
Artist
      ≠
Django User
```

An artist may be followed by thousands of users without having a VibeNation login account.

This architecture also means the catalog can represent artists independently of whether they have any relationship with VibeNation.

---

# Editorial Architecture

Editorial content is owned and controlled by VibeNation.

The primary relationship is:

```text
EditorialArticle
```

with supporting engagement and moderation models.

```text
EditorialArticle
 │
 ├── Likes
 ├── Comments
 ├── Replies
 ├── Views
 └── Reports
```

Users can interact with editorial content without gaining editorial publishing privileges.

---

# Cached Counters

The following types of counters may exist:

```text
likes_count
comments_count
replies_count
views_count
favorites_count
ratings_count
followers_count
```

These counters exist primarily to make common reads fast.

For example, displaying:

```text
12,481 likes
```

does not require counting thousands of relationship rows every time the post is loaded.

Instead:

```text
CommunityPost.likes_count
```

can be read directly.

---

# Counter Source of Truth

The general pattern is:

```text
                    SOURCE OF TRUTH
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
         Like rows     Rating rows    Follow rows
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    Cached counters
                           │
                           ▼
                     Fast frontend
```

For example:

```text
CommunityPostLike
```

is the source of truth.

```text
CommunityPost.likes_count
```

is the cached representation.

---

# Counter Updates

Counters should be updated in the API/service layer using safe database operations.

For example:

```text
Create Like
    ↓
Create relationship
    ↓
Increment counter atomically
```

Deletion:

```text
Delete Like
    ↓
Delete relationship
    ↓
Decrement counter atomically
```

Avoid naive read-modify-write logic such as:

```python
post.likes_count += 1
post.save()
```

when concurrent requests can modify the same counter.

Prefer atomic database expressions where appropriate.

---

# Source of Truth

The following table summarizes the intended source of truth.

| Data                   | Source of Truth            |
| ---------------------- | -------------------------- |
| Song metadata          | `Song`                     |
| Album metadata         | `Album`                    |
| Artist metadata        | `Artist`                   |
| Genre metadata         | `Genre`                    |
| Album track order      | `AlbumTrack`               |
| User song ratings      | `SongRating`               |
| User album ratings     | `AlbumRating`              |
| Article content        | `EditorialArticle`         |
| Community post content | `CommunityPost`            |
| Article likes          | `EditorialArticleLike`     |
| Community post likes   | `CommunityPostLike`        |
| Article comments       | `EditorialComment`         |
| Community comments     | `CommunityPostComment`     |
| Song favorites         | `SongFavorite`             |
| Album favorites        | `AlbumFavorite`            |
| Artist follows         | `ArtistFollow`             |
| User follows           | `UserFollow`               |
| Reports                | Corresponding report model |
| Like counters          | Cached                     |
| Comment counters       | Cached                     |
| Rating counters        | Cached                     |
| Favorite counters      | Cached                     |
| Follower counters      | Cached                     |
| View counters          | Cached                     |

---

# Database Constraints

Business rules should be enforced as close to the database as practical.

Important constraints include:

## Unique relationships

A user should not be able to create duplicate:

```text
SongRating
AlbumRating
SongFavorite
AlbumFavorite
ArtistFollow
UserFollow
CommunityPostLike
EditorialArticleLike
CommunityPostCommentLike
EditorialCommentLike
```

for the same relationship.

---

## Self-follow prevention

A user cannot follow themselves.

Conceptually:

```text
follower != following
```

---

## Valid ratings

Community ratings must remain within:

```text
0.5 → 5.0
```

and should only allow the intended increments.

---

## Valid track numbers

Album track numbers must be positive.

```text
track_number >= 1
```

---

# Indexes and Query Performance

Indexes should be created for fields frequently used in:

* Filtering
* Searching
* Sorting
* Foreign-key lookups
* Feed generation

Examples of useful query patterns include:

```text
songs by artist
songs by album
albums by artist
posts by user
comments by post
replies by parent comment
ratings by song
ratings by user
favorites by user
artist follows by artist
user follows by follower
```

Do not add indexes blindly.

An index should exist because it supports an actual query pattern.

Too many indexes can increase:

* Storage usage
* Write cost
* Migration complexity

---

# Deletion and Cascade Behavior

Relationships must define intentional deletion behavior.

For example:

```text
User
  │
  └── UserFollow
```

If a user is deleted, their relationship records may need to be deleted or otherwise handled according to the application's user-retention policy.

Similarly:

```text
CommunityPost
   │
   ├── Comments
   ├── Likes
   └── Reports
```

Deleting a post should have explicitly defined behavior for these dependent records.

Developers must not assume that every relationship should use `CASCADE`.

The deletion behavior should reflect the business meaning of the data.

---

# Authentication and User Relationships

The music app uses Django's user system as the base authentication identity.

The music models reference users for user-generated activity.

Examples:

```text
SongRating.user
AlbumRating.user

CommunityPost.author
CommunityPostComment.author

ArtistFollow.user

UserFollow.follower
UserFollow.following
```

The music application should not create duplicate authentication models unless there is a strong architectural requirement.

A future custom profile model can be introduced separately if the product requires profile-specific data.

---

# Third-Party Music Metadata

External music services may provide metadata when users search for music.

Typical information may include:

```text
Provider
Provider ID
Title
Artist
Album
Artwork
Preview information
Official listening URL
Duration
Genre
```

The external provider is not the VibeNation database.

The flow is:

```text
User
  │
  ▼
VibeNation API
  │
  ▼
External Music Provider
  │
  ▼
Normalized Search Result
  │
  ▼
User Selection
  │
  ▼
CommunityPostTarget
```

---

# Provider Abstraction

The application should not hard-code provider-specific assumptions throughout the community system.

Instead, provider-specific logic should live behind a service/adapter layer.

Conceptually:

```text
MusicCatalogProvider
       │
       ├── AppleMusicProvider
       ├── OptionalSecondaryProvider
       └── OptionalMetadataProvider
```

The rest of the application should work with a normalized representation.

This makes it easier to:

* Change providers
* Add providers
* Handle provider outages
* Normalize different metadata formats
* Test provider integrations

---

# Internal vs External Music Records

A selected community target may correspond to a VibeNation catalog object.

For example:

```text
External result
      │
      ▼
Matched VibeNation Song
      │
      ▼
CommunityPostTarget
```

Or the result may remain external:

```text
External result
      │
      ▼
CommunityPostTarget
      │
      └── provider metadata
```

This prevents the platform from being forced to create a permanent catalog record for every song a user searches for.

---

# Audio and Media Storage

The new music architecture does not use VibeNation as a downloadable audio host.

The database should therefore not be redesigned around storing third-party music files.

External previews should remain external.

The platform may store metadata necessary to display or reference the music, subject to the provider's terms.

Do not assume that because a provider returns a preview URL, VibeNation is permitted to:

* Download the audio
* Store the audio
* Cache the audio indefinitely
* Modify the audio
* Redistribute the audio

Provider-specific terms must be respected.

---

# API Implications

The database structure is designed to support a clean REST API.

For example:

```text
GET /songs/
GET /songs/<id>/

GET /albums/
GET /albums/<id>/

GET /artists/
GET /artists/<id>/

GET /community-posts/
POST /community-posts/

GET /community-posts/<id>/comments/
POST /community-posts/<id>/comments/
```

The API should not expose internal implementation details unnecessarily.

For example, an external provider's raw API response should not automatically become VibeNation's public API response.

Instead:

```text
External Provider
       │
       ▼
Provider Adapter
       │
       ▼
Normalized VibeNation Data
       │
       ▼
DRF Serializer
       │
       ▼
Frontend
```

---

# Admin Implications

The admin panel is primarily for:

* Catalog management
* Editorial publishing
* Moderation
* Reports
* Reviewing engagement
* Maintaining metadata

User-generated engagement should normally be created by the application rather than fabricated manually by administrators.

Therefore models such as:

```text
SongRating
AlbumRating
SongFavorite
AlbumFavorite
ArtistFollow
UserFollow
```

may intentionally not expose normal `Add` functionality in the admin.

The admin can still inspect and moderate these records.

---

# Migration Strategy

The Django migration system represents the schema history.

Whenever a model changes:

```bash
python manage.py makemigrations music
```

Review the generated migration before applying it.

Then:

```bash
python manage.py migrate
```

Check status:

```bash
python manage.py showmigrations music
```

Inspect SQL when debugging:

```bash
python manage.py sqlmigrate music <migration_number>
```

---

# Migration Safety

Never treat migrations as disposable files in a production environment.

A migration may already have been applied to a database containing real data.

Before performing destructive operations, determine:

```text
Does data exist?
Which migrations have been applied?
What tables exist?
What does Django think exists?
What will the migration actually execute?
```

Development databases can sometimes be rebuilt when no valuable data exists.

Production databases should be handled much more carefully.

---

# Future Scalability

The relational model is intentionally designed so other services can interact with PostgreSQL later.

Possible future components include:

```text
Django / DRF
      │
      ├── Core API
      ├── Admin
      └── Business logic
             │
             ▼
         PostgreSQL
             ▲
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
   Go Service    Workers
```

Potential future Go services might handle:

* High-volume feed generation
* Realtime systems
* Recommendation workloads
* Analytics ingestion
* High-concurrency workloads

However, introducing another language or service should be based on actual requirements.

The database model should not be made unnecessarily complicated merely because future scale is possible.

---

# Common Mistakes to Avoid

## Mistake 1 — Making artists users

Wrong:

```text
Artist → User
```

unless a completely separate artist-account architecture is deliberately introduced later.

Current architecture:

```text
Artist = catalog entity
User = platform account
```

---

## Mistake 2 — Putting ratings directly on songs

Avoid:

```text
Song
 └── user_ratings = [...]
```

Use:

```text
SongRating
```

---

## Mistake 3 — Storing average rating as the source of truth

Avoid making:

```text
average_rating
```

the authoritative value.

Calculate from rating records.

---

## Mistake 4 — Making replies separate posts

A reply is a comment.

```text
Comment
  └── parent
```

not:

```text
CommunityPost
```

---

## Mistake 5 — Combining editorial and community content

Avoid:

```text
Content
 ├── article
 ├── community post
 └── everything else
```

unless there is a compelling future architectural reason.

The current system deliberately separates:

```text
EditorialArticle
CommunityPost
```

---

## Mistake 6 — Storing third-party audio

A preview URL is not permission to download and host the audio.

---

## Mistake 7 — Updating counters unsafely

Avoid race-prone counter updates.

Use atomic operations where appropriate.

---

## Mistake 8 — Creating a database record for every search

A user searching for a song does not necessarily mean VibeNation should permanently create a `Song`.

Search results may remain external until the application has a reason to persist them.

---

## Mistake 9 — Using generic relationships everywhere

Avoid reaching for generic foreign keys simply because several models appear similar.

Strong relational relationships are preferred when the domain is known.

---

## Mistake 10 — Premature denormalization

Do not add fields simply because they might make something faster.

First establish:

```text
What query is slow?
Why is it slow?
Can indexing solve it?
Can query optimization solve it?
Would caching solve it?
```

Then denormalize only when justified.

---

# Adding a New Model

Before creating a new model, ask:

## Question 1

What real-world concept does this model represent?

If the answer is unclear, the model may not be necessary.

---

## Question 2

Is this:

```text
Catalog data?
Editorial data?
Community data?
Engagement?
Moderation?
Social relationship?
```

Classify it first.

---

## Question 3

Can an existing model represent it?

Avoid duplicate concepts.

---

## Question 4

Is it actually a relationship?

For example:

```text
User ↔ Song
```

may require a relationship model such as:

```text
SongFavorite
SongRating
```

rather than adding fields directly to `Song`.

---

## Question 5

What happens when it is deleted?

Define:

```text
CASCADE
SET_NULL
PROTECT
RESTRICT
```

or another appropriate behavior intentionally.

---

## Question 6

Does it need constraints?

Consider:

* Unique constraints
* Check constraints
* Validators
* Nullability
* Required fields

---

## Question 7

Does it need indexes?

Only add indexes that support meaningful query patterns.

---

# Developer Checklist

Before changing `models.py`, verify:

### Architecture

* [ ] Does the change fit an existing domain?
* [ ] Is the responsibility clearly defined?
* [ ] Does it preserve separation between catalog and engagement?

### Relationships

* [ ] Is a relationship model more appropriate than a direct field?
* [ ] Is uniqueness enforced?
* [ ] Is deletion behavior intentional?
* [ ] Are foreign keys appropriate?

### User activity

* [ ] Is this a like?
* [ ] Rating?
* [ ] Favorite?
* [ ] Follow?
* [ ] Report?
* [ ] View?

If yes, determine whether it belongs in a dedicated model.

### Performance

* [ ] Is an index needed?
* [ ] Is a cached counter justified?
* [ ] Can the query be optimized instead?
* [ ] Are `select_related()` / `prefetch_related()` appropriate?

### API

* [ ] Does the API need this field?
* [ ] Is the field safe to expose?
* [ ] Does pagination apply?
* [ ] Does the serializer create unnecessary queries?

### Security

* [ ] Can users modify another user's relationship?
* [ ] Can duplicate engagement be created?
* [ ] Can users manipulate counters?
* [ ] Can provider metadata be spoofed?

### Migration

* [ ] Have migrations been generated?
* [ ] Has the migration been reviewed?
* [ ] Is the migration safe for existing data?
* [ ] Has the migration been tested?

---

# Golden Rules

These rules should remain true unless the architecture is intentionally redesigned.

> **1. `Artist` is a catalog entity, not a Django user.**

> **2. Music catalog data is separate from user activity.**

> **3. Ratings are separate relationship records.**

> **4. Likes are separate relationship records.**

> **5. Favorites are separate relationship records.**

> **6. Follows are separate relationship records.**

> **7. Comments are not community posts.**

> **8. Replies are comments with a parent comment.**

> **9. Editorial content and community content are separate domains.**

> **10. Cached counters are optimizations, not the source of truth.**

> **11. Average ratings should initially be calculated from rating records.**

> **12. Database constraints should enforce important business rules.**

> **13. VibeNation does not host downloadable copyrighted music.**

> **14. External music providers provide discovery/metadata; they do not replace VibeNation's database.**

> **15. Provider-specific logic belongs behind an abstraction/service layer.**

> **16. Do not create permanent catalog records simply because a user performed a search.**

> **17. Do not introduce denormalization without a measurable reason.**

> **18. Migration history must be treated as part of the production database contract.**

---

# Final Mental Model

The easiest way to understand the entire data model is to think in layers.

```text
                         VIBENATION MUSIC
                                │
                                ▼
                       ┌─────────────────┐
                       │  MUSIC CATALOG  │
                       └────────┬────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
       Artist                 Album                 Song
          │                     │                     │
          │                     ▼                     │
          │                AlbumTrack                 │
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
          ┌──────────────┐              ┌──────────────┐
          │  EDITORIAL   │              │  COMMUNITY   │
          └──────┬───────┘              └──────┬───────┘
                 │                             │
                 ▼                             ▼
        EditorialArticle                CommunityPost
                 │                             │
                 ▼                             ▼
        EditorialComment              CommunityPostComment
                 │                             │
                 └──────────────┬──────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   ENGAGEMENT    │
                       └────────┬────────┘
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
           Likes             Ratings           Favorites
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  SOCIAL GRAPH   │
                       └────────┬────────┘
                                │
                         ┌──────┴──────┐
                         ▼             ▼
                    ArtistFollow   UserFollow
```

In one sentence:

> **The VibeNation music database separates music entities, editorial content, community content, user engagement, and social relationships into clear relational models while keeping PostgreSQL as the source of truth and cached counters as performance optimizations.**

That separation is what makes the system easier to maintain today and much easier to scale tomorrow.
