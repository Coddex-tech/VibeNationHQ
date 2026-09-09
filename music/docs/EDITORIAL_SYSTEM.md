# VibeNation Editorial System

## Table of Contents

* [1. Purpose](#1-purpose)
* [2. Editorial System Overview](#2-editorial-system-overview)
* [3. Editorial vs Community Content](#3-editorial-vs-community-content)
* [4. Editorial Content Model](#4-editorial-content-model)
* [5. Editorial Articles](#5-editorial-articles)

  * [5.1 What an Editorial Article Is](#51-what-an-editorial-article-is)
  * [5.2 Article Ownership](#52-article-ownership)
  * [5.3 Article Title and Slug](#53-article-title-and-slug)
  * [5.4 Article Body](#54-article-body)
  * [5.5 Article Status](#55-article-status)
  * [5.6 Featured Articles](#56-featured-articles)
  * [5.7 Sponsored Content](#57-sponsored-content)
  * [5.8 Article Views](#58-article-views)
* [6. Connecting Editorial Content to Music](#6-connecting-editorial-content-to-music)

  * [6.1 Related Songs](#61-related-songs)
  * [6.2 Related Artists](#62-related-artists)
  * [6.3 Related Albums](#63-related-albums)
  * [6.4 Related Genres](#64-related-genres)
* [7. Editorial Publishing Workflow](#7-editorial-publishing-workflow)
* [8. Drafts](#8-drafts)
* [9. Publishing](#9-publishing)
* [10. Featured and Homepage Content](#10-featured-and-homepage-content)
* [11. Editorial Comments](#11-editorial-comments)

  * [11.1 Comments](#111-comments)
  * [11.2 Replies](#112-replies)
  * [11.3 Comment Likes](#113-comment-likes)
  * [11.4 Comment Views](#114-comment-views)
* [12. Editorial Engagement](#12-editorial-engagement)

  * [12.1 Article Likes](#121-article-likes)
  * [12.2 Article Comments](#122-article-comments)
  * [12.3 Article Views](#123-article-views)
* [13. Editorial Reports and Moderation](#13-editorial-reports-and-moderation)
* [14. Editorial Music Reviews](#14-editorial-music-reviews)
* [15. Editorial and Community Ratings](#15-editorial-and-community-ratings)
* [16. Editorial Content and the Music Catalog](#16-editorial-content-and-the-music-catalog)
* [17. SEO and Discoverability](#17-seo-and-discoverability)
* [18. Media and Images](#18-media-and-images)
* [19. Admin Responsibilities](#19-admin-responsibilities)
* [20. API Responsibilities](#20-api-responsibilities)
* [21. Performance and Scalability](#21-performance-and-scalability)
* [22. Future Extensions](#22-future-extensions)
* [23. Developer Workflow](#23-developer-workflow)
* [24. Golden Rules](#24-golden-rules)

---

# 1. Purpose

The VibeNation Editorial System is responsible for professionally produced content published by the VibeNation editorial team.

This includes content such as:

* music reviews
* song analysis
* album reviews
* EP reviews
* artist stories
* music news
* interviews
* features
* opinion pieces
* entertainment stories
* sponsored/editorial partnership content

Editorial content is controlled by VibeNation staff rather than ordinary community users.

The editorial system exists alongside the community system but has different ownership, permissions, publishing rules, and responsibilities.

---

# 2. Editorial System Overview

The primary editorial model is:

```text
EditorialArticle
```

An editorial article can be associated with VibeNation's music catalog.

Conceptually:

```text
                         EditorialArticle
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
           Songs             Artists            Albums
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                                ▼
                            Genres
```

An article can then have its own engagement layer:

```text
EditorialArticle
       │
       ├── Likes
       │
       ├── Comments
       │      └── Replies
       │
       ├── Views
       │
       └── Reports
```

This gives editorial content its own complete interaction system without turning it into community content.

---

# 3. Editorial vs Community Content

This distinction is one of the most important architectural rules in VibeNation.

## Editorial content

Created and controlled by:

```text
VibeNation staff/admin
```

Primary model:

```text
EditorialArticle
```

Examples:

```text
"Why This New Burna Boy Album Matters"

"5 Things You Should Know About the New Wave of Afrobeats"

"Album Review: ..."

"Artist Spotlight: ..."
```

## Community content

Created by:

```text
VibeNation users
```

Primary model:

```text
CommunityPost
```

Examples:

```text
"I think this album is underrated."

"That second track is insane."

"What do you guys think about this song?"
```

The two systems may discuss the same music but serve different purposes.

```text
                    MUSIC
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
   EditorialArticle        CommunityPost
          │                       │
          ▼                       ▼
 Professional content       User-generated
```

---

# 4. Editorial Content Model

The editorial system is built around several responsibilities:

```text
Content
  ↓
Music relationships
  ↓
Publishing
  ↓
Discovery
  ↓
Engagement
  ↓
Moderation
```

The `EditorialArticle` model represents the published or draft article.

Additional models handle:

```text
EditorialArticleLike
EditorialComment
EditorialCommentLike
EditorialCommentReport
EditorialArticleReport
```

This separation keeps editorial content and editorial engagement independently manageable.

---

# 5. Editorial Articles

## 5.1 What an Editorial Article Is

An `EditorialArticle` is a professionally created piece of VibeNation content.

It may be short-form or long-form depending on the content category.

Examples include:

### Music news

```text
A new single has been released.
An artist announced an upcoming album.
A festival lineup has been announced.
```

### Reviews

```text
Song review
Album review
EP review
```

### Features

```text
Artist spotlight
Music industry analysis
Genre analysis
```

### Opinion/editorial

```text
Editorial perspective
Cultural commentary
Music trends
```

The article should contain enough structured metadata for VibeNation's frontend to present it correctly.

---

## 5.2 Article Ownership

Editorial articles are created by authorized staff.

The backend should determine the author from the authenticated administrative user where applicable.

A frontend/client must never be allowed to impersonate another staff member by submitting an arbitrary author ID.

The general rule is:

```text
Authenticated staff member
        ↓
creates/edits article
        ↓
article author/editor information
```

The exact authorship fields must remain consistent with the finalized `EditorialArticle` model.

---

## 5.3 Article Title and Slug

The title is the primary human-readable identifier.

For example:

```text
Why Afrobeats Continues to Dominate Global Music
```

The article should also have a URL-friendly slug:

```text
why-afrobeats-continues-to-dominate-global-music
```

The slug provides stable and readable URLs.

Example:

```text
/news/why-afrobeats-continues-to-dominate-global-music/
```

Slugs should be unique where required.

If an article title changes after publication, slug changes should be handled carefully because changing URLs can break:

* search-engine indexing
* bookmarks
* social links
* internal links
* external backlinks

URL changes should therefore be deliberate rather than automatic whenever an article is edited.

---

## 5.4 Article Body

The body contains the actual editorial content.

Depending on the editor implementation, the body may support:

* paragraphs
* headings
* links
* images
* quotations
* lists
* embedded media
* emphasis
* structured formatting

The API should sanitize or safely process user-editable rich content before exposing it to the frontend.

Editorial HTML must never be blindly rendered if the content can contain unsafe markup.

---

## 5.5 Article Status

Editorial articles have a publishing lifecycle.

The conceptual lifecycle is:

```text
Draft
  ↓
Review
  ↓
Published
  ↓
Archived
```

The exact statuses must match the finalized model implementation.

### Draft

The article is being prepared.

It should not appear as public editorial content.

### Published

The article is publicly available.

It can appear in:

* article pages
* category pages
* search results
* homepage sections
* related-content sections
* feeds where applicable

### Archived

The article is retained but is no longer part of normal active publishing.

Archived content may remain accessible depending on VibeNation's content policy.

---

## 5.6 Featured Articles

Featured content is editorially selected content that deserves additional visibility.

Examples:

* major breaking news
* important album reviews
* exclusive interviews
* major artist stories
* high-priority features

A featured article may appear in:

```text
Homepage hero
Featured section
Top stories
Category highlights
```

Being featured should not automatically mean the article is published.

The publication state remains authoritative.

Conceptually:

```text
is_published = True
is_featured = True
```

is valid.

But:

```text
is_published = False
is_featured = True
```

should not make the article publicly visible.

Publication state always takes precedence.

---

## 5.7 Sponsored Content

VibeNation can support sponsored/editorial partnership content.

Sponsored content must remain distinguishable from ordinary editorial content.

The existing system includes sponsored state handling for news/editorial content.

For example:

```text
is_sponsored = True
```

may indicate that an article is sponsored.

The frontend should clearly identify sponsored material according to VibeNation's publishing policy and applicable advertising requirements.

Sponsored status should never silently transform ordinary editorial content into advertising.

---

## 5.8 Article Views

Editorial articles have their own:

```text
views_count
```

Views are tracked separately from community posts.

The article's view count belongs to the editorial engagement system.

View increment logic belongs in the API/service layer.

The model should not automatically increment its own counter every time the object is retrieved.

---

# 6. Connecting Editorial Content to Music

Editorial articles often discuss specific music entities.

The article model therefore supports relationships with VibeNation's music catalog.

These relationships provide structured connections between editorial content and music.

---

## 6.1 Related Songs

An article may be associated with one or more songs.

Example:

```text
EditorialArticle
      │
      └── Song
```

This allows VibeNation to display:

```text
Related Song
```

on the article page.

It also makes it possible to build future features such as:

* related articles on song pages
* song-specific editorial feeds
* search filtering
* recommendations

---

## 6.2 Related Artists

Articles can be connected to artists.

Example:

```text
EditorialArticle
      │
      └── Artist
```

An artist page can therefore eventually show:

```text
Latest News
Reviews
Features
Interviews
```

related to that artist.

Remember:

```text
Artist ≠ User
```

The artist relationship is to the music catalog entity, not a user account.

---

## 6.3 Related Albums

Articles can also reference albums or EPs.

Example:

```text
EditorialArticle
      │
      └── Album
```

This is especially useful for:

* album reviews
* EP reviews
* release announcements
* album analysis
* track-by-track features

An album page can later surface relevant editorial content.

---

## 6.4 Related Genres

Editorial articles can also be associated with genres.

Examples:

```text
Afrobeats
Afropop
Amapiano
Hip-Hop
R&B
```

Genre relationships help with:

* category discovery
* filtering
* recommendations
* SEO
* related-content systems

The article's genre relationship should not replace the article's actual editorial category if those concepts are modeled separately.

---

# 7. Editorial Publishing Workflow

The normal editorial workflow is:

```text
                    ┌──────────────┐
                    │ Create Draft │
                    └──────┬───────┘
                           │
                           ▼
                 Write/Edit Content
                           │
                           ▼
                Add Music Relationships
                           │
                           ▼
                  Add Featured Image
                           │
                           ▼
                    Editorial Review
                           │
                           ▼
                       Publish
                           │
                           ▼
                 Public VibeNation Page
```

After publication:

```text
Published
   │
   ├── Receive views
   ├── Receive likes
   ├── Receive comments
   ├── Receive reports
   └── Appear in discovery surfaces
```

The editorial team remains responsible for the content itself.

---

# 8. Drafts

Drafts allow staff to prepare content before publication.

A draft can contain:

* title
* body
* related music
* genres
* images
* metadata
* SEO information
* publication configuration

without being publicly accessible.

Drafts are particularly important for scheduled editorial workflows.

The frontend must ensure that unpublished content is not accidentally exposed through public API endpoints.

---

# 9. Publishing

Publishing is a deliberate state transition.

The API/admin workflow should validate required information before allowing publication.

For example:

```text
Title
Body
Slug
Required metadata
Publication state
```

Depending on the article type, additional information may be required.

Once published, the article becomes eligible for public API queries.

Public endpoints should generally filter out unpublished content.

Conceptually:

```python
EditorialArticle.objects.filter(
    is_published=True
)
```

The exact query should follow the finalized model fields.

---

# 10. Featured and Homepage Content

Featured editorial content is part of VibeNation's content-discovery strategy.

The homepage may contain sections such as:

```text
Featured Story
Latest News
Trending Stories
Music Reviews
Artist Features
Latest Articles
```

The backend should expose these through purpose-specific API endpoints or optimized querysets rather than forcing the frontend to download the entire editorial database.

Example:

```text
GET /api/v1/news/layout/
```

or equivalent finalized endpoints.

Homepage ordering can later incorporate:

* publication time
* featured status
* editorial priority
* engagement
* category
* manually selected content

The exact ranking algorithm should remain independent from the database model wherever possible.

---

# 11. Editorial Comments

Editorial articles have their own comment system.

The model is:

```text
EditorialComment
```

This is intentionally separate from:

```text
CommunityPostComment
```

because an editorial article and a community post are different content domains.

---

## 11.1 Comments

A top-level editorial comment belongs to an editorial article.

Conceptually:

```text
EditorialArticle
      │
      ├── EditorialComment
      ├── EditorialComment
      └── EditorialComment
```

---

## 11.2 Replies

Replies use the same `EditorialComment` model through its self-referential parent relationship.

Conceptually:

```text
EditorialComment
    parent = NULL
        ↓
    Top-level comment
```

and:

```text
EditorialComment
    parent = another EditorialComment
        ↓
    Reply
```

This allows deeply nested conversations.

Example:

```text
Comment
├── Reply
│   ├── Reply
│   └── Reply
└── Reply
```

---

## 11.3 Comment Likes

Editorial comment likes use:

```text
EditorialCommentLike
```

This is separate from:

```text
CommunityPostCommentLike
```

The separation keeps editorial and community engagement independent.

---

## 11.4 Comment Views

Editorial comments contain their own view count where defined by the model.

This makes it possible to measure interaction with individual discussion contributions.

As with article views, view counting belongs in the service/API layer.

---

# 12. Editorial Engagement

Editorial content has its own engagement system.

```text
EditorialArticle
       │
       ├── EditorialArticleLike
       ├── EditorialComment
       │       └── EditorialCommentLike
       ├── views_count
       └── Reports
```

This is intentionally separate from community engagement.

---

## 12.1 Article Likes

Likes on editorial articles use:

```text
EditorialArticleLike
```

A user should normally have one active like per article.

The database should enforce the appropriate uniqueness rule.

---

## 12.2 Article Comments

Comments are represented by:

```text
EditorialComment
```

Replies use the same model through its parent relationship.

This means the article can support full discussion without creating a separate reply table.

---

## 12.3 Article Views

Views use:

```text
EditorialArticle.views_count
```

The counter is a cached/read-optimized value.

The underlying view-counting strategy should be implemented outside the model.

---

# 13. Editorial Reports and Moderation

Even though editorial articles are created by staff, their public comment sections are user-generated.

Therefore, both articles and comments can participate in the moderation system.

Current report models include:

```text
EditorialArticleReport
EditorialCommentReport
```

Reports are moderation records.

A report should not itself modify the article.

Typical flow:

```text
User reports content
        ↓
Report created
        ↓
Staff reviews
        ↓
Action taken if necessary
```

Possible actions include:

* dismiss report
* remove problematic comment
* restrict user
* edit/remove content where appropriate
* escalate moderation issue

The precise moderation policy should be defined separately from the database architecture.

---

# 14. Editorial Music Reviews

Music reviews are a major use case for the editorial system.

A review can be associated with:

```text
Song
Artist
Album
Genre
```

depending on what the article is reviewing.

For an album review:

```text
EditorialArticle
       │
       ├── Album
       ├── Artist
       └── Genres
```

For a song review:

```text
EditorialArticle
       │
       ├── Song
       ├── Artist
       └── Genres
```

This gives the frontend enough structured information to display relevant music context.

The actual review remains editorial content.

---

# 15. Editorial and Community Ratings

VibeNation has two distinct rating concepts.

## Community rating

Users can rate songs/albums using:

```text
0.5 → 5.0 stars
```

These ratings are represented by:

```text
SongRating
AlbumRating
```

## Editorial score

Editorial reviews can use a professional editorial score:

```text
0 → 10
```

The editorial score represents VibeNation's own critical assessment.

These values must never be treated as the same metric.

For example:

```text
Community rating:
4.6 / 5

Editorial score:
8.5 / 10
```

Both can appear on a music page while communicating different things.

```text
Community = audience opinion

Editorial = VibeNation's critical opinion
```

---

# 16. Editorial Content and the Music Catalog

The editorial system depends heavily on the music catalog.

The relationship should generally flow from editorial content toward canonical music entities.

```text
EditorialArticle
       │
       ├── Song
       ├── Album
       ├── Artist
       └── Genre
```

The music catalog remains responsible for representing the underlying music entity.

The editorial system is responsible for writing about it.

This separation prevents duplicated music metadata.

For example, an article should not create its own independent copy of:

```text
Artist name
Album name
Song title
Genre
```

when the canonical music records already exist.

Instead:

```text
EditorialArticle → Artist
EditorialArticle → Album
EditorialArticle → Song
```

---

# 17. SEO and Discoverability

Editorial content is one of the primary SEO assets of VibeNation.

Every publicly accessible article should be designed with search discoverability in mind.

Important elements include:

* stable URL
* descriptive title
* readable slug
* appropriate metadata
* structured relationships
* publication date
* featured image
* relevant categories/genres
* internal links
* related music entities

Example URL:

```text
/articles/album-review-example/
```

The exact route depends on the frontend routing architecture.

---

## Internal linking

Editorial articles should link naturally to related VibeNation pages.

For example:

```text
Article
  ↓
Artist page
  ↓
Album page
  ↓
Song page
  ↓
Related articles
```

This creates a connected content graph.

```text
                   Artist
                  /      \
                 /        \
          Album ---------- Article
            |
            |
          Song
```

This structure benefits both users and search engines.

---

# 18. Media and Images

Editorial articles may use images such as:

* featured images
* article body images
* artist images
* album artwork
* promotional graphics

Media files should be handled through VibeNation's configured media-storage architecture.

In production, the project may use:

```text
django-storages
boto3
object storage/CDN
```

The database should store references to media rather than unnecessarily storing large binary files inside PostgreSQL.

---

## Image optimization

The frontend should use appropriately sized images.

Possible optimizations include:

* responsive image sizes
* WebP/AVIF where supported
* lazy loading
* CDN delivery
* image compression

Large original uploads should not automatically be served to every visitor.

---

# 19. Admin Responsibilities

The admin system is the primary management interface for editorial content.

Staff should be able to:

* create articles
* edit articles
* manage publication state
* manage featured content
* manage related music
* manage genres
* manage sponsored status
* review reports
* moderate comments
* inspect engagement
* manage editorial metadata

The admin system should reduce repetitive manual work.

---

## Staff should not manually manage user engagement

The editorial team should not normally create:

```text
EditorialArticleLike
EditorialCommentLike
SongRating
AlbumRating
ArtistFollow
UserFollow
```

on behalf of users.

These records represent real user activity.

Admin can inspect or moderate them when necessary.

---

# 20. API Responsibilities

The editorial API should expose only content appropriate for the requesting user.

## Public API

Public users should generally be able to retrieve:

* published articles
* article details
* related music
* article comments
* article engagement
* public metadata

Unpublished drafts should not be exposed through public endpoints.

---

## Authenticated API

Authenticated users may be able to:

* like articles
* unlike articles
* create comments
* reply to comments
* like comments
* report content

depending on the implemented permissions.

---

## Staff API/Admin

Authorized staff may:

* create articles
* edit articles
* publish articles
* archive articles
* manage editorial relationships
* moderate comments
* review reports

Permissions must be enforced server-side.

---

# 21. Performance and Scalability

Editorial pages are likely to receive high read traffic compared with write traffic.

Therefore, editorial APIs should be optimized primarily for reads.

Important strategies include:

### Pagination

Use pagination for:

* article lists
* comments
* replies
* reports
* related content

### Select-related/prefetch-related

Use appropriate ORM optimization when retrieving:

```text
Artist
Album
Song
Genre
```

alongside articles.

### Caching

Frequently requested content can be cached.

Potential cache targets include:

```text
Homepage articles
Featured articles
Popular articles
Article detail responses
Related articles
```

### CDN

Static/media assets should be served through appropriate CDN/object-storage infrastructure in production.

---

# 22. Future Extensions

The editorial architecture leaves room for future features.

## Scheduled Publishing

Articles can eventually be published automatically at a specified time.

Conceptually:

```text
Draft
  ↓
Scheduled
  ↓
Published
```

This is especially useful for:

* midnight releases
* embargoed announcements
* campaign content
* planned editorial calendars

---

## Editorial Authors

A future version may provide dedicated editorial author profiles.

This could allow:

```text
Written by Victor
Senior Music Editor
```

without changing the underlying content architecture.

---

## Content Series

Articles could eventually belong to series.

Example:

```text
Afrobeats Explained
   ├── Part 1
   ├── Part 2
   └── Part 3
```

---

## Related Content

The system can eventually support explicit relationships such as:

```text
Related articles
Recommended articles
Previous article
Next article
```

---

## Editorial Analytics

Future analytics could track:

```text
Views
Unique visitors
Reading time
Scroll depth
Likes
Comments
Shares
Traffic sources
Search traffic
```

These analytics should be introduced independently from the core article model where possible.

---

# 23. Developer Workflow

When creating or modifying an editorial feature, follow this process.

## Step 1 — Identify the editorial object

Determine whether the feature concerns:

```text
Article
Song
Album
Artist
Genre
Comment
Report
Engagement
```

---

## Step 2 — Preserve ownership boundaries

Ask:

```text
Is this staff content?
Is this user-generated content?
Is this engagement?
Is this moderation data?
```

Do not mix these responsibilities.

---

## Step 3 — Connect to canonical music records

If an article discusses existing music:

```text
Article → Song
Article → Album
Article → Artist
Article → Genre
```

Avoid duplicating catalog metadata.

---

## Step 4 — Protect unpublished content

Verify that public endpoints cannot expose:

```text
Drafts
Archived private content
Unpublished scheduled content
```

unless explicitly intended.

---

## Step 5 — Test engagement separately

Test:

```text
Article like
Article unlike
Comment creation
Reply creation
Comment like
Report creation
View counting
```

---

## Step 6 — Test permissions

At minimum:

```text
Public user can read published article
Public user cannot access protected draft
Authenticated user can comment
Authenticated user can like
User cannot edit staff article
Unauthorized user cannot publish
Staff can manage editorial content
```

---

# 24. Golden Rules

### Rule 1 — Editorial content belongs to VibeNation

```text
EditorialArticle = staff-created content
```

It is not equivalent to a community post.

---

### Rule 2 — Community and editorial systems remain separate

```text
EditorialArticle
        ≠
CommunityPost
```

Even though both can have comments, likes, views, and reports.

---

### Rule 3 — Music entities remain canonical

Articles should reference:

```text
Song
Album
Artist
Genre
```

rather than duplicating their metadata.

---

### Rule 4 — Artists are catalog entities

An artist relationship does not mean the artist has a VibeNation account.

```text
Artist ≠ Django User
```

---

### Rule 5 — Publication state controls visibility

A featured article that is not published must not accidentally become publicly visible.

```text
Featured ≠ Published
```

---

### Rule 6 — Editorial scores and community ratings are different

```text
Editorial:
0–10

Community:
0.5–5 stars
```

Do not combine them into one rating system.

---

### Rule 7 — User engagement remains user-generated

Admins moderate engagement but should not fabricate normal user activity.

---

### Rule 8 — Views are handled outside the model

View counting belongs in the API/service layer.

---

### Rule 9 — Public APIs must protect drafts

Never expose unpublished editorial content through normal public endpoints.

---

### Rule 10 — Editorial content should be SEO-friendly

Stable URLs, structured relationships, useful metadata, internal linking, and optimized media are important parts of the editorial system.

---

### Rule 11 — Editorial comments remain separate

```text
EditorialComment
        ≠
CommunityPostComment
```

They serve different content domains.

---

### Rule 12 — Keep the editorial layer scalable

Use:

```text
PostgreSQL
efficient ORM queries
pagination
caching
CDN/media optimization
```

before introducing unnecessary microservices.

---

# Final Mental Model

The VibeNation Editorial System can be understood as:

```text
                         VIBENATION EDITORIAL
                                  │
                                  ▼
                         EditorialArticle
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
           Song                Album                Artist
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
                                Genre
                                  │
                                  ▼
                          Published Article
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
                 ▼                ▼                ▼
               Views            Likes          Comments
                                                   │
                                                   ▼
                                                Replies
                                                   │
                                                   ▼
                                                 Likes
                                                   │
                                                   ▼
                                                Reports
```

The simplest way to remember the architecture is:

```text
Music catalog
    ↓
provides the canonical music entities

EditorialArticle
    ↓
provides VibeNation's professional voice

CommunityPost
    ↓
provides the audience's voice

Editorial engagement
    ↓
lets readers interact with professional content

Community engagement
    ↓
lets users interact with one another

Admin
    ↓
controls publishing and moderation

API
    ↓
enforces permissions, visibility, validation, and business rules
```

The editorial system is therefore **not just a blog system**.

It is VibeNation's professional content layer, tightly connected to the music catalog while remaining independent from user-generated community content.
