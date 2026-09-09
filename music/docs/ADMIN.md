# VibeNation Music System — Admin Architecture

This document explains how the VibeNation `music` application's administrative system is structured.

It covers:

* The purpose of the admin system
* Master admin and staff admin portals
* Music catalog management
* Editorial management
* Community moderation
* User-generated engagement
* Reports
* Permissions
* Admin registration
* Read-only engagement records
* Moderation workflows
* Administrative responsibilities
* Security principles
* Common mistakes

The implementation of the admin configuration currently lives primarily in:

```text
music/admin.py
```

and the custom admin sites are defined in the project's administrative site configuration.

---

# Table of Contents

1. [Purpose](#purpose)
2. [Admin Philosophy](#admin-philosophy)
3. [Administrative Architecture](#administrative-architecture)
4. [Admin Portals](#admin-portals)

   * [Master Admin](#master-admin)
   * [Staff Admin](#staff-admin)
   * [Default Django Admin](#default-django-admin)
5. [Master Admin Responsibilities](#master-admin-responsibilities)
6. [Staff Admin Responsibilities](#staff-admin-responsibilities)
7. [Permission Philosophy](#permission-philosophy)
8. [Music Catalog Management](#music-catalog-management)

   * [Genres](#genres)
   * [Artists](#artists)
   * [Albums](#albums)
   * [Album Tracks](#album-tracks)
   * [Songs](#songs)
9. [Editorial Management](#editorial-management)
10. [Community Management](#community-management)
11. [Community Post Moderation](#community-post-moderation)
12. [Comment Moderation](#comment-moderation)
13. [Reports and Moderation](#reports-and-moderation)

* [Community Post Reports](#community-post-reports)
* [Community Comment Reports](#community-comment-reports)
* [Editorial Reports](#editorial-reports)

14. [User Engagement Records](#user-engagement-records)
15. [Why Some Models Have No Add Button](#why-some-models-have-no-add-button)
16. [Ratings in Admin](#ratings-in-admin)
17. [Likes in Admin](#likes-in-admin)
18. [Favorites in Admin](#favorites-in-admin)
19. [Follows in Admin](#follows-in-admin)
20. [Cached Counters](#cached-counters)
21. [Admin Search and List Views](#admin-search-and-list-views)
22. [Admin Filters](#admin-filters)
23. [Admin Read-Only Fields](#admin-read-only-fields)
24. [CommunityPostTarget Administration](#communityposttarget-administration)
25. [User and Group Management](#user-and-group-management)
26. [Authentication and Admin Security](#authentication-and-admin-security)
27. [Admin Audit Logs](#admin-audit-logs)
28. [Admin Workflow](#admin-workflow)
29. [Typical Editorial Workflow](#typical-editorial-workflow)
30. [Typical Moderation Workflow](#typical-moderation-workflow)
31. [What Admins Should Not Do](#what-admins-should-not-do)
32. [Adding a New Admin Model](#adding-a-new-admin-model)
33. [Testing Admin Changes](#testing-admin-changes)
34. [Common Admin Mistakes](#common-admin-mistakes)
35. [Security Rules](#security-rules)
36. [Developer Checklist](#developer-checklist)
37. [Golden Rules](#golden-rules)
38. [Final Mental Model](#final-mental-model)

---

# Purpose

The VibeNation admin system exists to allow authorized staff to manage the platform without directly manipulating the database.

The admin interface provides controlled access to:

```text
Music Catalog
      +
Editorial Content
      +
Community Moderation
      +
Reports
      +
Users
      +
Platform Configuration
```

The admin panel is **not** the primary interface through which normal user activity is created.

For example, a normal user should rate a song through the frontend.

The administrator should generally inspect that rating through the admin panel rather than manually creating it.

---

# Admin Philosophy

The administrative system follows one major principle:

> **Admins manage the platform; users generate normal engagement.**

This means administrators are responsible for:

* Maintaining catalog information
* Publishing editorial content
* Moderating user-generated content
* Reviewing reports
* Managing users and permissions
* Correcting legitimate catalog errors

Users are responsible for generating:

* Likes
* Ratings
* Favorites
* Follows
* Community posts
* Comments
* Replies

The admin system should not blur these responsibilities.

---

# Administrative Architecture

VibeNation uses custom Django admin sites.

The architecture currently includes:

```text
┌────────────────────────────────────────────┐
│               VIBENATION ADMIN             │
├────────────────────────────────────────────┤
│                                            │
│  Master Admin                              │
│  /vibenation-admin-1999/                   │
│                                            │
│  Staff Admin                               │
│  /vibe-crew-login-2026/                   │
│                                            │
│  Default Django Admin                      │
│  /admin/                                   │
│                                            │
└────────────────────────────────────────────┘
```

The exact URLs are implementation details and should be changed if the project's security strategy changes.

The important architectural distinction is the separation between:

```text
Master Administration
```

and:

```text
Staff Administration
```

---

# Admin Portals

## Master Admin

The master administrative portal is:

```text
/vibenation-admin-1999/
```

Its admin site name is:

```text
boss_admin
```

The master portal represents the highest administrative level of the VibeNation platform.

It has control over the complete administrative environment.

---

# Staff Admin

The staff portal is:

```text
/vibe-crew-login-2026/
```

Its admin site name is:

```text
staff_admin
```

The staff portal is designed for authorized members of the VibeNation team who need to perform operational tasks without necessarily having unrestricted control over the entire platform.

Typical staff responsibilities include:

* Editorial publishing
* Music catalog management
* Community moderation
* Report review

---

# Default Django Admin

The project may also retain Django's default admin site:

```text
/admin/
```

This should not automatically be treated as the primary production administration portal.

Custom VibeNation admin sites exist so the platform can control:

* Branding
* Permissions
* Dashboard behavior
* Available models
* Staff workflows
* Security boundaries

---

# Master Admin Responsibilities

The master admin has the broadest administrative authority.

Typical responsibilities include:

### Platform

* Full administrative control
* User management
* Group/permission management
* Configuration
* Security settings

### Music

* Artists
* Albums
* Songs
* Genres
* Album tracks
* Music metadata

### Editorial

* Articles
* Publishing
* Featuring
* Archiving
* Moderation

### Community

* Posts
* Comments
* Reports
* User moderation

### Engagement

* Inspecting ratings
* Inspecting likes
* Inspecting favorites
* Inspecting follows

The master admin should still avoid fabricating normal user activity unless there is an explicit administrative reason to do so.

---

# Staff Admin Responsibilities

Staff administrators should have access based on their job responsibilities.

Typical staff workflows include:

```text
Catalog Team
     │
     ├── Artists
     ├── Albums
     ├── Songs
     └── Genres

Editorial Team
     │
     ├── Articles
     └── Editorial moderation

Community Team
     │
     ├── Community Posts
     ├── Comments
     └── Reports
```

Staff permissions should follow the principle of least privilege.

A staff member should receive the minimum access required to perform their role.

---

# Permission Philosophy

Administrative permissions should be based on responsibility.

Avoid giving every staff member:

```text
superuser
```

access.

Instead, use:

```text
Groups
+
Model permissions
+
Custom admin restrictions
```

where appropriate.

Django provides the standard model permissions:

```text
add
change
delete
view
```

The application may also implement custom restrictions where business rules require them.

---

# Music Catalog Management

The admin system is responsible for maintaining VibeNation's internal music catalog.

The core catalog consists of:

```text
Genre
Artist
Album
AlbumTrack
Song
```

---

# Genres

Administrators can create and manage music genres.

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

Genres should have clean names and should not be duplicated unnecessarily.

Before creating a new genre, administrators should search for an existing equivalent.

For example, avoid having:

```text
Afro Beats
Afrobeats
Afro-beats
```

as separate genres unless there is a deliberate catalog reason.

---

# Artists

Administrators manage artist catalog records.

An artist record may contain:

* Name
* Slug
* Biography
* Image
* External identifiers
* Followers count
* Related catalog information

The exact fields depend on the current `Artist` model.

## Important

Artists are not platform users.

Do not create a Django user account merely because an artist exists in the catalog.

```text
Artist ≠ User
```

---

# Albums

Administrators manage album metadata.

An album may include:

* Title
* Artists
* Release information
* Cover artwork
* Tracks
* Publication metadata
* Favorite count
* Rating count

Album track ordering should be maintained through:

```text
AlbumTrack
```

rather than manually encoding track positions into arbitrary text.

---

# Album Tracks

`AlbumTrack` controls which songs appear in an album and in what order.

Example:

```text
Album
│
├── 1 → Song A
├── 2 → Song B
├── 3 → Song C
└── 4 → Song D
```

Administrators should ensure that:

* Track numbers are valid
* Songs exist
* The album relationship is correct
* Duplicate track positions are avoided where the model's constraints require uniqueness

---

# Songs

Administrators manage the internal song catalog.

A song may contain:

* Title
* Artists
* Featured artists
* Album
* Genres
* Cover information
* Publication information
* Favorites count
* Ratings count

Administrators should not manually maintain user ratings or favorites inside the song record.

Those are generated by the platform's engagement system.

---

# Editorial Management

Editorial articles are created and managed by authorized staff.

The main model is:

```text
EditorialArticle
```

Typical workflow:

```text
Draft
  │
  ▼
Review
  │
  ▼
Publish
  │
  ├── Feature
  │
  └── Archive
```

Editorial articles may reference:

* Songs
* Albums
* Artists
* Genres

This allows editorial content to become part of the broader music discovery system.

---

# Community Management

Community content is user-generated.

The main model is:

```text
CommunityPost
```

Administrators should primarily use the admin interface to:

* Review posts
* Investigate reports
* Remove violating content
* Manage moderation states where available
* Investigate abuse

Administrators should not routinely rewrite user content simply to make it look editorial.

Community content and editorial content serve different purposes.

---

# Community Post Moderation

A community post can receive a report.

The workflow is:

```text
User
 │
 ▼
Reports Community Post
 │
 ▼
CommunityPostReport
 │
 ▼
Moderator Reviews
 │
 ├── Dismiss
 │
 ├── Take action
 │
 └── Escalate
```

The report record should provide moderators with enough information to understand:

* What was reported
* Who reported it
* Why it was reported
* When it was reported
* Whether it has already been reviewed

---

# Comment Moderation

Comments and replies can also be moderated.

The same concept applies:

```text
CommunityPostComment
        │
        ▼
CommunityPostCommentReport
        │
        ▼
Moderator
```

A reported reply should be treated as a comment record.

Moderators should not convert replies into posts during moderation.

---

# Reports and Moderation

Reports are moderation records.

They are not likes.

They are not comments.

They are not user posts.

Their purpose is to notify authorized staff that content may require review.

The system currently separates reports by content type.

---

# Community Post Reports

```text
CommunityPostReport
```

represents a report against a community post.

Relationship:

```text
User
  │
  ▼
CommunityPostReport
  │
  ▼
CommunityPost
```

---

# Community Comment Reports

```text
CommunityPostCommentReport
```

represents a report against a community comment or reply.

Relationship:

```text
User
  │
  ▼
CommunityPostCommentReport
  │
  ▼
CommunityPostComment
```

---

# Editorial Reports

Editorial content also has dedicated report models.

```text
EditorialArticleReport
EditorialCommentReport
```

This allows the moderation system to distinguish:

```text
Reported article
```

from:

```text
Reported editorial comment
```

and apply appropriate moderation actions.

---

# User Engagement Records

The following models represent platform-generated user activity:

```text
SongRating
AlbumRating

SongFavorite
AlbumFavorite

ArtistFollow
UserFollow

CommunityPostLike
CommunityPostCommentLike

EditorialArticleLike
EditorialCommentLike
```

These models are normally created by the user-facing application.

The admin interface primarily provides:

```text
View
Inspect
Filter
Moderate
```

rather than:

```text
Fabricate
```

---

# Why Some Models Have No Add Button

Some engagement models intentionally disable the normal admin **Add** action.

For example:

```text
AlbumRating
SongRating
SongFavorite
ArtistFollow
UserFollow
```

may be configured so administrators cannot casually create new records from the admin interface.

This is intentional.

Consider:

```text
User A rated Album X = 5 stars
```

That relationship should normally be created because User A actually performed the action.

It should not be fabricated by an administrator simply because the admin happens to have access to the database.

Therefore:

```text
User action
     │
     ▼
Frontend/API
     │
     ▼
Database relationship
```

is the normal path.

The admin is primarily:

```text
Database relationship
     │
     ▼
Admin inspection/moderation
```

---

# Ratings in Admin

Administrators can inspect:

```text
SongRating
AlbumRating
```

records.

Useful information includes:

* User
* Song or album
* Rating value
* Created date
* Updated date

Ratings should normally be generated through the API.

If an administrator needs to correct an abusive or invalid rating, the appropriate moderation action should be taken according to platform policy.

---

# Likes in Admin

Administrators can inspect like records such as:

```text
CommunityPostLike
CommunityPostCommentLike
EditorialArticleLike
EditorialCommentLike
```

Likes are user activity.

The admin should not routinely create likes manually.

If a like is fraudulent or abusive, moderation can remove the relationship record where appropriate.

---

# Favorites in Admin

Favorites include:

```text
SongFavorite
AlbumFavorite
```

Favorites are user-specific relationships.

The admin can inspect them for:

* User activity
* Debugging
* Moderation
* Analytics support

They should normally be created through the user-facing application.

---

# Follows in Admin

There are two follow systems:

```text
ArtistFollow
UserFollow
```

Administrators can inspect these relationships.

An artist follow means:

```text
User → Artist
```

A user follow means:

```text
User → User
```

They are not interchangeable.

---

# Cached Counters

Several catalog/content models contain cached counters.

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

Administrators should generally **not manually edit these fields**.

For example:

```text
Song.ratings_count
```

should be updated when `SongRating` records are created or deleted.

Similarly:

```text
Artist.followers_count
```

should reflect `ArtistFollow` relationships.

---

# Why Counters Are Read-Only

Counters are derived optimizations.

The actual records are the source of truth.

For example:

```text
ArtistFollow
   │
   ├── User A → Artist
   ├── User B → Artist
   └── User C → Artist
```

The cached value:

```text
Artist.followers_count = 3
```

exists for fast reads.

Allowing arbitrary manual edits could create:

```text
Artist.followers_count = 9000
```

while only three actual follow records exist.

That would create inconsistency.

Therefore counters should normally be read-only in the admin.

---

# Admin Search and List Views

Admin list views should make large datasets manageable.

Good `list_display` fields generally include:

* Human-readable name
* Relevant owner
* Status
* Important relationship
* Created date
* Updated date

Avoid putting every field into the list display.

The list page should provide enough information to identify a record quickly.

---

# Admin Search

Search fields should focus on values administrators are likely to search for.

Examples:

### Artist

```text
name
```

### Album

```text
title
```

### Song

```text
title
artist names
album
```

### CommunityPost

```text
content
author
```

### Comments

```text
content
author
```

Search configuration should be optimized for actual moderation and catalog workflows.

---

# Admin Filters

Filters should be used for fields that are commonly grouped or reviewed.

Potential filters include:

```text
publication status
created date
updated date
genre
artist
album
report status
```

Do not create unnecessary filters simply because a model contains a field.

---

# Admin Read-Only Fields

Certain fields should generally be read-only.

Examples:

```text
created_at
updated_at
likes_count
comments_count
replies_count
views_count
favorites_count
ratings_count
followers_count
```

These values are either automatically managed or derived from application activity.

The admin can inspect them without being able to accidentally break their consistency.

---

# CommunityPostTarget Administration

`CommunityPostTarget` is an implementation detail supporting community posts.

It should generally not be treated as an independent piece of content.

Conceptually:

```text
CommunityPost
      │
      ▼
CommunityPostTarget
```

The target exists to connect the post to:

```text
Song
Album
Artist
External music-provider metadata
```

For this reason, it does not need to appear as a standalone top-level admin model in the same way that `CommunityPost` does.

The target is managed through the community-post workflow.

---

# User and Group Management

The admin system also exposes Django's user/group system where appropriate.

Users represent authenticated platform accounts.

Groups can be used to organize administrative permissions.

Possible groups include:

```text
Super Administrators
Editorial Staff
Music Editors
Community Moderators
```

The exact group structure should reflect the actual VibeNation organization.

Do not create unnecessary permission groups before there is a real operational need.

---

# Authentication and Admin Security

The admin system is security-sensitive because it provides direct access to important platform data.

The project uses additional administrative security mechanisms, including two-factor authentication components.

Administrators should use strong authentication practices.

The admin URLs should not be treated as a substitute for authentication.

Changing or obscuring an admin URL does not replace:

* Strong passwords
* 2FA
* Permission controls
* Session security
* Monitoring
* Audit logs

---

# Admin Audit Logs

Administrative actions should be auditable.

Django's `LogEntry` system records important admin actions.

Typical actions include:

```text
ADD
CHANGE
DELETION
```

This allows authorized administrators to investigate:

* Who changed a record
* What type of object was changed
* When the change happened
* What administrative action occurred

Audit logs should generally not be casually deleted.

They are valuable for troubleshooting and security investigations.

---

# Admin Workflow

A good administrative workflow follows:

```text
Identify
   │
   ▼
Inspect
   │
   ▼
Verify
   │
   ▼
Modify / Moderate
   │
   ▼
Save
   │
   ▼
Audit
```

Administrators should avoid making destructive changes before understanding the affected relationships.

---

# Typical Editorial Workflow

A typical editorial process:

```text
Research
   │
   ▼
Create Editorial Article
   │
   ▼
Assign Music Relationships
   │
   ├── Artist
   ├── Album
   ├── Song
   └── Genre
   │
   ▼
Review
   │
   ▼
Publish
   │
   ▼
Feature if appropriate
   │
   ▼
Monitor engagement
```

User comments, likes, and views are generated independently by the frontend/API.

---

# Typical Moderation Workflow

A typical moderation process:

```text
User submits report
        │
        ▼
Report record created
        │
        ▼
Moderator reviews content
        │
        ├──────────────┐
        ▼              ▼
   No violation     Violation
        │              │
        ▼              ▼
    Dismiss       Take action
                       │
                ┌──────┴──────┐
                ▼             ▼
             Remove        Escalate
```

The exact moderation states and actions may evolve as the platform develops.

---

# What Admins Should Not Do

## 1. Do not fabricate user activity

Do not manually create fake:

```text
Likes
Ratings
Favorites
Follows
```

just to increase engagement numbers.

---

## 2. Do not manually edit cached counters

Avoid changing:

```text
likes_count
ratings_count
favorites_count
followers_count
```

unless performing a deliberate data-repair operation.

---

## 3. Do not create artists as users

An artist record does not require a Django account.

```text
Artist ≠ User
```

---

## 4. Do not turn comments into posts

A comment remains a comment.

---

## 5. Do not use the admin as the normal user interface

The admin is for administration.

User interactions should normally go through the public application/API.

---

## 6. Do not manually copy third-party music data without understanding its source

External provider metadata should flow through the catalog/provider architecture.

---

## 7. Do not upload copyrighted audio simply because an admin interface allows file uploads elsewhere

The music architecture does not make VibeNation an MP3 hosting service.

---

## 8. Do not delete catalog entities without checking relationships

Deleting a song, album, or artist may affect:

* Community posts
* Editorial articles
* Favorites
* Ratings
* Album tracks
* Search results
* External references

Deletion behavior must be understood before taking action.

---

# Adding a New Admin Model

When introducing a new model, determine whether it actually needs admin exposure.

Ask:

### Question 1

Does an administrator need to manage this object?

If no, it may not need an admin registration.

### Question 2

Is it user-generated activity?

If yes, consider whether it should be:

```text
View only
```

rather than fully editable.

### Question 3

Can editing the object break a cached counter or relationship?

If yes, make sensitive fields read-only.

### Question 4

Does the model need moderation?

If yes, provide:

* Search
* Filters
* Status
* Relevant timestamps
* Relationship information

### Question 5

Which admin sites should expose it?

Consider:

```text
Master admin
Staff admin
Default admin
```

Do not automatically expose every model to every portal.

---

# Admin Registration Pattern

The project uses custom admin sites.

Conceptually:

```python
admin_site = MasterAdminSite(name="boss_admin")
staff_admin_site = StaffAdminSite(name="staff_admin")
```

Music models can then be registered with the appropriate sites.

The project also uses a safe registration approach to avoid duplicate-registration errors.

The important architectural rule is:

```text
Model
  │
  ├── Master Admin
  │
  └── Staff Admin
```

with permissions and admin classes controlling what each portal can do.

---

# Testing Admin Changes

After changing `music/admin.py` or the custom admin site configuration, test:

## 1. Django system checks

```bash
python manage.py check
```

---

## 2. Migration state

If models were changed:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 3. Admin loading

Verify:

```text
Master Admin
Staff Admin
```

load without errors.

---

## 4. Model registration

Verify expected models appear.

Check that models that should be hidden remain hidden.

---

## 5. Permissions

Test using accounts representing:

```text
Master administrator
Staff administrator
Regular user
```

Make sure staff cannot access functionality outside their intended permissions.

---

## 6. Engagement models

Verify that models intentionally configured without add permission do not display the normal:

```text
+ Add
```

action.

---

## 7. Audit logging

Make a test change and verify the administrative action is recorded correctly.

---

# Common Admin Mistakes

## Mistake 1 — Registering every model blindly

Not every model needs the same admin behavior.

---

## Mistake 2 — Giving staff superuser access

Use least privilege.

---

## Mistake 3 — Making counters editable

Counters should normally be read-only.

---

## Mistake 4 — Allowing manual creation of engagement

User activity should normally originate from the application.

---

## Mistake 5 — Exposing internal relationship models unnecessarily

Some relationship models are useful for inspection but do not need to become prominent administrative workflows.

---

## Mistake 6 — Hard-coding admin URLs

Admin URLs and namespaces should be derived from the actual admin site configuration.

---

## Mistake 7 — Ignoring audit logs

Administrative changes should remain traceable.

---

## Mistake 8 — Deleting catalog data without checking dependencies

Always understand the relationship graph first.

---

# Security Rules

The following rules apply to all administrative development.

### Rule 1

Use least privilege.

### Rule 2

Require strong authentication.

### Rule 3

Use 2FA for privileged administration.

### Rule 4

Do not expose sensitive models unnecessarily.

### Rule 5

Keep audit logging enabled.

### Rule 6

Do not trust an obscured admin URL as a security mechanism.

### Rule 7

Do not allow normal users to access admin functionality.

### Rule 8

Validate permissions on the server.

### Rule 9

Never rely solely on frontend permission hiding.

### Rule 10

Treat database-changing operations as privileged operations.

---

# Developer Checklist

Before adding or changing an admin class:

### Model

* [ ] Does this model need admin access?
* [ ] Is it catalog data, editorial content, engagement, or moderation?
* [ ] Does it contain sensitive information?

### Permissions

* [ ] Should master admins access it?
* [ ] Should staff access it?
* [ ] Should staff be able to add records?
* [ ] Should staff be able to edit records?
* [ ] Should staff be able to delete records?

### Display

* [ ] Is `list_display` useful?
* [ ] Are search fields appropriate?
* [ ] Are filters useful?
* [ ] Are important fields read-only?

### Relationships

* [ ] Are foreign-key relationships easy to inspect?
* [ ] Could deletion cause unexpected cascades?
* [ ] Are counters protected?

### Security

* [ ] Does the model expose sensitive data?
* [ ] Are permissions enforced server-side?
* [ ] Is the action auditable?

### Testing

* [ ] Run `python manage.py check`
* [ ] Test master admin
* [ ] Test staff admin
* [ ] Test permissions
* [ ] Test add/change/delete behavior
* [ ] Test audit logging

---

# Golden Rules

> **1. The admin panel manages the platform; it does not replace the user-facing application.**

> **2. Master admins have broad control; staff should receive only the permissions they need.**

> **3. User engagement should normally be generated by users through the API.**

> **4. Ratings, likes, favorites, and follows should not be fabricated through normal admin workflows.**

> **5. Cached counters should normally be read-only.**

> **6. Artists are catalog entities, not Django users.**

> **7. Comments remain comments and should never be treated as standalone community posts.**

> **8. Reports are moderation records and should be handled through an explicit moderation workflow.**

> **9. Administrative actions should remain auditable.**

> **10. Strong authentication and least privilege are more important than hiding the admin URL.**

> **11. Do not expose every internal model as a full CRUD workflow.**

> **12. Always understand relationship and deletion consequences before removing catalog data.**

---

# Final Mental Model

The easiest way to understand the VibeNation music admin system is:

```text
                         ADMIN SYSTEM
                              │
               ┌──────────────┴──────────────┐
               │                             │
               ▼                             ▼
        MASTER ADMIN                    STAFF ADMIN
               │                             │
               ├──────────────┐              │
               │              │              │
               ▼              ▼              ▼
           Full Control   User/Groups    Operational Work
               │                         │
               │             ┌───────────┼───────────┐
               │             ▼           ▼           ▼
               │          Catalog     Editorial   Moderation
               │
               └─────────────────────────────────────┐
                                                     │
                                                     ▼
                                            MUSIC PLATFORM
                                                     │
                         ┌───────────────────────────┼─────────────────────────┐
                         │                           │                         │
                         ▼                           ▼                         ▼
                      Catalog                    Content                  Engagement
                         │                           │                         │
                    Artist/Album                 Articles/Posts          Likes/Ratings
                    Song/Genre                   Comments                Favorites/Follows
                                                     │
                                                     ▼
                                                  Reports
                                                     │
                                                     ▼
                                                Moderation
```

The fundamental rule is:

```text
ADMIN
  │
  ├── Manage catalog
  ├── Publish editorial content
  ├── Moderate community content
  ├── Review reports
  ├── Manage permissions
  └── Inspect platform activity
```

while:

```text
USER
  │
  ├── Create community posts
  ├── Comment
  ├── Reply
  ├── Like
  ├── Rate
  ├── Favorite
  ├── Follow artists
  └── Follow users
```

The admin system should provide the tools necessary to **operate and protect VibeNation without becoming the mechanism through which normal user activity is fabricated**.
