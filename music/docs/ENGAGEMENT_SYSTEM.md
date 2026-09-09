# VibeNation Engagement System

## Table of Contents

* [1. Purpose](#1-purpose)
* [2. Engagement System Overview](#2-engagement-system-overview)
* [3. Core Principles](#3-core-principles)
* [4. Engagement Categories](#4-engagement-categories)
* [5. Likes](#5-likes)

  * [5.1 Community Post Likes](#51-community-post-likes)
  * [5.2 Community Comment Likes](#52-community-comment-likes)
  * [5.3 Editorial Article Likes](#53-editorial-article-likes)
  * [5.4 Editorial Comment Likes](#54-editorial-comment-likes)
  * [5.5 Like/Unlike Flow](#55-likeunlike-flow)
* [6. Ratings](#6-ratings)

  * [6.1 Song Ratings](#61-song-ratings)
  * [6.2 Album Ratings](#62-album-ratings)
  * [6.3 Rating Scale](#63-rating-scale)
  * [6.4 Updating Ratings](#64-updating-ratings)
  * [6.5 Average Rating](#65-average-rating)
* [7. Favorites](#7-favorites)

  * [7.1 Song Favorites](#71-song-favorites)
  * [7.2 Album Favorites](#72-album-favorites)
  * [7.3 Favorite Flow](#73-favorite-flow)
* [8. Following](#8-following)

  * [8.1 User Following](#81-user-following)
  * [8.2 Artist Following](#82-artist-following)
  * [8.3 Artist Accounts Do Not Exist](#83-artist-accounts-do-not-exist)
  * [8.4 Following Flow](#84-following-flow)
* [9. Views](#9-views)

  * [9.1 Community Post Views](#91-community-post-views)
  * [9.2 Community Comment Views](#92-community-comment-views)
  * [9.3 Editorial Article Views](#93-editorial-article-views)
  * [9.4 Editorial Comment Views](#94-editorial-comment-views)
  * [9.5 View Counting Strategy](#95-view-counting-strategy)
* [10. Cached Engagement Counters](#10-cached-engagement-counters)

  * [10.1 Why Counters Exist](#101-why-counters-exist)
  * [10.2 Source of Truth](#102-source-of-truth)
  * [10.3 Atomic Counter Updates](#103-atomic-counter-updates)
  * [10.4 Counter Repair](#104-counter-repair)
* [11. Engagement Uniqueness](#11-engagement-uniqueness)
* [12. Engagement Ownership](#12-engagement-ownership)
* [13. Engagement and Authentication](#13-engagement-and-authentication)
* [14. Engagement and Permissions](#14-engagement-and-permissions)
* [15. Engagement and Admin](#15-engagement-and-admin)
* [16. Engagement and API Design](#16-engagement-and-api-design)
* [17. Engagement and Database Design](#17-engagement-and-database-design)
* [18. Performance and Scalability](#18-performance-and-scalability)
* [19. Caching Strategy](#19-caching-strategy)
* [20. Analytics](#20-analytics)
* [21. Notifications](#21-notifications)
* [22. Trending and Ranking](#22-trending-and-ranking)
* [23. Future Engagement Features](#23-future-engagement-features)
* [24. Developer Workflow](#24-developer-workflow)
* [25. Golden Rules](#25-golden-rules)
* [26. Final Mental Model](#26-final-mental-model)

---

# 1. Purpose

The VibeNation Engagement System handles the actions users take when interacting with music, editorial content, community content, and other users.

Engagement includes:

* likes
* ratings
* favorites
* follows
* views

These actions are represented as separate database records or counters depending on their purpose.

The system is designed around an important principle:

> **Engagement is data about a relationship or interaction, not part of the identity of the content itself.**

For example:

```text
Song
```

is the music entity.

```text
SongRating
```

is a user's relationship with that song.

Likewise:

```text
CommunityPost
```

is the content.

```text
CommunityPostLike
```

is a user's interaction with that content.

---

# 2. Engagement System Overview

The engagement layer sits across several VibeNation systems.

```text
                         ENGAGEMENT
                             │
       ┌─────────────────────┼─────────────────────┐
       │                     │                     │
       ▼                     ▼                     ▼
    Content                Music                Social
       │                     │                     │
       │                     ├── Ratings           ├── UserFollow
       │                     └── Favorites         └── ArtistFollow
       │
   ┌───┴────┐
   │        │
   ▼        ▼
Editorial Community
   │        │
   ▼        ▼
 Likes     Likes
 Comments  Comments
 Views     Views
 Reports   Reports
```

The current engagement-related models include:

```text
EditorialArticleLike
CommunityPostLike

EditorialCommentLike
CommunityPostCommentLike

SongRating
AlbumRating

SongFavorite
AlbumFavorite

ArtistFollow
UserFollow
```

View counts are represented directly on the relevant content models.

---

# 3. Core Principles

## 3.1 Engagement is user-generated

Normal engagement records are created by users through the application.

Examples:

```text
Like
Rating
Favorite
Follow
```

Administrators should not normally fabricate these records.

---

## 3.2 Engagement records are the source of truth

The database rows representing engagement are authoritative.

For example:

```text
CommunityPostLike rows
```

are the source of truth for post likes.

The field:

```text
CommunityPost.likes_count
```

is a cached optimization.

---

## 3.3 Counters are optimizations

Cached counters exist to avoid expensive `COUNT(*)` queries on high-traffic pages.

They should never replace the underlying engagement records.

---

## 3.4 One relationship should not create duplicate engagement

Where the product defines an interaction as unique, the database should enforce that uniqueness.

Examples:

```text
one user + one post = one like
one user + one song = one rating
one user + one album = one rating
one user + one song = one favorite
one user + one album = one favorite
one follower + one followed user = one follow
one user + one artist = one artist follow
```

---

## 3.5 Business logic belongs outside the model

Engagement operations should normally be handled by the API/service layer.

Examples:

```text
like()
unlike()
rate()
favorite()
unfavorite()
follow()
unfollow()
record_view()
```

The model defines the data structure and database rules.

The service/API layer controls the operation.

---

# 4. Engagement Categories

VibeNation engagement can be grouped into five categories.

| Category  | Meaning                                | Examples      |
| --------- | -------------------------------------- | ------------- |
| Likes     | Lightweight positive interaction       | Post like     |
| Ratings   | Quantitative opinion                   | Song 4.5/5    |
| Favorites | Personal saved relationship            | Favorite song |
| Follows   | Persistent social/catalog relationship | Follow artist |
| Views     | Consumption/attention measurement      | Article view  |

These actions should not be treated as interchangeable.

For example:

```text
Like ≠ Favorite
Rating ≠ Like
Follow ≠ Favorite
View ≠ Like
```

Each communicates a different user intent.

---

# 5. Likes

Likes are lightweight positive interactions.

VibeNation uses separate like models for different content domains.

```text
CommunityPostLike
CommunityPostCommentLike

EditorialArticleLike
EditorialCommentLike
```

This separation is intentional.

---

## 5.1 Community Post Likes

Model:

```text
CommunityPostLike
```

Relationship:

```text
User
  │
  ▼
CommunityPostLike
  │
  ▼
CommunityPost
```

A user likes a community post.

The post's cached counter is:

```text
CommunityPost.likes_count
```

---

## 5.2 Community Comment Likes

Model:

```text
CommunityPostCommentLike
```

Relationship:

```text
User
  │
  ▼
CommunityPostCommentLike
  │
  ▼
CommunityPostComment
```

This works for:

* top-level comments
* replies
* deeply nested replies

because replies use the same comment model.

The cached counter is:

```text
CommunityPostComment.likes_count
```

---

## 5.3 Editorial Article Likes

Model:

```text
EditorialArticleLike
```

Relationship:

```text
User
  │
  ▼
EditorialArticleLike
  │
  ▼
EditorialArticle
```

The cached counter is:

```text
EditorialArticle.likes_count
```

---

## 5.4 Editorial Comment Likes

Model:

```text
EditorialCommentLike
```

Relationship:

```text
User
  │
  ▼
EditorialCommentLike
  │
  ▼
EditorialComment
```

The cached counter is:

```text
EditorialComment.likes_count
```

---

## 5.5 Like/Unlike Flow

The frontend can present a simple toggle:

```text
Not liked
    ↓
   Like
    ↓
Liked
    ↓
  Unlike
    ↓
Not liked
```

Backend flow:

```text
POST /like/
      ↓
Authenticate user
      ↓
Validate target
      ↓
Create like record
      ↓
Increment cached counter
```

Unlike:

```text
DELETE /like/
      ↓
Authenticate user
      ↓
Find user's like
      ↓
Delete like record
      ↓
Decrement cached counter
```

The exact endpoint structure may differ from this example.

The important rule is that the operation must be idempotent or protected against duplicate requests.

---

# 6. Ratings

Ratings represent a stronger and more quantitative opinion than likes.

VibeNation currently supports ratings for:

```text
Song
Album
```

through:

```text
SongRating
AlbumRating
```

---

## 6.1 Song Ratings

Relationship:

```text
User
  │
  ▼
SongRating
  │
  ▼
Song
```

A user can rate a song using the supported five-star scale.

---

## 6.2 Album Ratings

Relationship:

```text
User
  │
  ▼
AlbumRating
  │
  ▼
Album
```

A user can rate an album/EP.

---

## 6.3 Rating Scale

Community ratings use:

```text
0.5 – 5.0
```

in half-star increments.

Valid values include:

```text
0.5
1.0
1.5
2.0
2.5
3.0
3.5
4.0
4.5
5.0
```

The backend must validate the submitted value.

The frontend should also restrict the user interface to valid values, but frontend validation is not sufficient by itself.

---

## 6.4 Updating Ratings

A user should normally have one active rating for a particular song or album.

Example:

```text
User rates song:
4.0
```

Later:

```text
User changes rating:
4.5
```

The application should update the existing rating rather than creating:

```text
4.0
4.5
```

as two active ratings from the same user.

The rating count should therefore represent the number of users who have rated the object, not the number of rating edits.

---

## 6.5 Average Rating

Average ratings are deliberately not stored permanently on `Song` or `Album`.

For a song:

```text
SongRating
  5.0
  4.5
  4.0
  5.0
```

the average is calculated from the rating rows.

Conceptually:

```python
Avg("rating")
```

The API may return:

```json
{
    "average_rating": 4.63,
    "rating_count": 4
}
```

without storing:

```text
Song.average_rating
```

as another source of truth.

This avoids synchronization problems.

---

# 7. Favorites

Favorites represent a user's personal saved relationship with music.

Current models:

```text
SongFavorite
AlbumFavorite
```

Favorites are different from likes.

A like generally communicates:

> "I like this."

A favorite communicates more closely:

> "I want to keep/save this in my personal collection."

---

## 7.1 Song Favorites

Relationship:

```text
User
  │
  ▼
SongFavorite
  │
  ▼
Song
```

A user can add a song to their favorites.

---

## 7.2 Album Favorites

Relationship:

```text
User
  │
  ▼
AlbumFavorite
  │
  ▼
Album
```

A user can favorite an album/EP.

---

## 7.3 Favorite Flow

The normal flow is:

```text
Favorite
   ↓
Create favorite row
   ↓
Optional cached counter update
```

Removing:

```text
Unfavorite
   ↓
Delete favorite row
   ↓
Optional cached counter update
```

The exact visibility of favorite counts is a product decision.

Favorites themselves are primarily user-specific relationships.

---

# 8. Following

Following creates persistent relationships between users and other entities.

VibeNation currently supports:

```text
UserFollow
ArtistFollow
```

These represent two different types of social relationship.

---

## 8.1 User Following

Model:

```text
UserFollow
```

Relationship:

```text
Follower
   │
   ▼
UserFollow
   │
   ▼
Followed User
```

For example:

```text
User A → follows → User B
```

The relationship can later power:

* personalized feeds
* notifications
* social discovery
* activity timelines
* recommendations

A user must not be allowed to follow themselves.

This should be enforced at the database level as well as the API layer.

---

## 8.2 Artist Following

Model:

```text
ArtistFollow
```

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

This is a catalog/social relationship.

It does **not** mean the artist has a VibeNation account.

---

## 8.3 Artist Accounts Do Not Exist

This is an important VibeNation architectural rule.

```text
Artist ≠ User
```

An `Artist` is a catalog/editorial entity.

Artists do not need:

* Django user accounts
* passwords
* login sessions
* user profiles
* authentication identities

A VibeNation user simply follows an artist record.

For example:

```text
User
  │
  └── ArtistFollow
          │
          └── Artist
```

This distinction must be preserved throughout the codebase.

---

## 8.4 Following Flow

User follow:

```text
POST /follow/
      ↓
Authenticate
      ↓
Validate target
      ↓
Create UserFollow
```

Artist follow:

```text
POST /artists/<artist>/follow/
      ↓
Authenticate
      ↓
Validate artist
      ↓
Create ArtistFollow
```

Unfollow removes the relationship.

Uniqueness prevents duplicate follow records.

---

# 9. Views

Views measure attention rather than an explicit user action.

Current models contain view counters for relevant content.

Examples:

```text
CommunityPost.views_count
CommunityPostComment.views_count

EditorialArticle.views_count
EditorialComment.views_count
```

Views differ from likes because viewing does not require the user to express an opinion.

---

## 9.1 Community Post Views

A community post has:

```text
views_count
```

The counter can be incremented when the post is viewed according to VibeNation's view-counting policy.

---

## 9.2 Community Comment Views

Community comments/replies can also have:

```text
views_count
```

This allows the platform to measure attention to individual discussion contributions where required.

---

## 9.3 Editorial Article Views

Editorial articles have:

```text
EditorialArticle.views_count
```

This is particularly important for:

* popular stories
* trending articles
* traffic analytics
* editorial performance

---

## 9.4 Editorial Comment Views

Editorial comments have:

```text
EditorialComment.views_count
```

This can be used to measure attention to individual comments/replies.

---

## 9.5 View Counting Strategy

View counting should not simply mean:

```python
obj.views_count += 1
```

inside the model every time the object is fetched.

The API/service layer should decide when a view counts.

Possible strategies include:

### Authenticated users

Count one view per user within a defined time window.

```text
User + content + time window
```

### Anonymous users

Use a session or another privacy-conscious identifier where appropriate.

### High-volume traffic

Use Redis or another fast store to temporarily aggregate views before writing them to PostgreSQL.

The exact strategy can evolve as traffic increases.

---

# 10. Cached Engagement Counters

Several content models contain cached counters.

Examples include:

```text
CommunityPost.likes_count
CommunityPost.comments_count
CommunityPost.views_count

CommunityPostComment.likes_count
CommunityPostComment.replies_count
CommunityPostComment.views_count

EditorialArticle.likes_count
EditorialArticle.comments_count
EditorialArticle.views_count

EditorialComment.likes_count
EditorialComment.replies_count
EditorialComment.views_count

Artist.followers_count
```

Music entities may also maintain engagement-related counters such as:

```text
Song.favorites_count
Song.ratings_count

Album.favorites_count
Album.ratings_count
```

These fields are designed for efficient reads.

---

## 10.1 Why Counters Exist

Consider a popular community post with:

```text
500,000 likes
```

Counting all like rows every time someone opens the post would be unnecessary database work.

Instead:

```text
CommunityPost.likes_count
```

can be returned immediately.

The underlying like rows remain available when the system needs authoritative data.

---

## 10.2 Source of Truth

The relationship is:

```text
Engagement rows
       ↓
SOURCE OF TRUTH
       ↓
Cached counter
       ↓
Fast API response
```

Examples:

```text
CommunityPostLike
        ↓
COUNT(*)
        ↓
CommunityPost.likes_count
```

and:

```text
ArtistFollow
        ↓
COUNT(*)
        ↓
Artist.followers_count
```

The counter should never be treated as more authoritative than the underlying rows.

---

## 10.3 Atomic Counter Updates

Counters should be updated atomically.

For example:

```python
CommunityPost.objects.filter(
    pk=post_id
).update(
    likes_count=F("likes_count") + 1
)
```

For removal:

```python
CommunityPost.objects.filter(
    pk=post_id
).update(
    likes_count=F("likes_count") - 1
)
```

Atomic database expressions reduce the risk of lost updates when multiple users interact with the same object simultaneously.

The actual implementation should also ensure counters do not become negative.

---

## 10.4 Counter Repair

Because counters are cached, the system should eventually have a way to rebuild them.

For example:

```text
COUNT(CommunityPostLike)
        ↓
CommunityPost.likes_count
```

A maintenance command could recalculate counters periodically or after an incident.

This is another reason counters should never be treated as the primary source of truth.

---

# 11. Engagement Uniqueness

Database constraints are essential for engagement.

Examples:

```text
User + CommunityPostLike
        ↓
unique
```

```text
User + SongRating
        ↓
unique
```

```text
User + AlbumRating
        ↓
unique
```

```text
User + SongFavorite
        ↓
unique
```

```text
User + AlbumFavorite
        ↓
unique
```

```text
Follower + Followed User
        ↓
unique
```

```text
User + ArtistFollow
        ↓
unique
```

The API should check uniqueness before attempting the operation for good user experience.

The database must still enforce it for correctness.

This protects against:

* double-clicks
* retries
* race conditions
* malicious requests
* concurrent requests
* frontend bugs

---

# 12. Engagement Ownership

Most engagement records have an acting user.

For example:

```text
CommunityPostLike.user
SongRating.user
AlbumRating.user
SongFavorite.user
AlbumFavorite.user
ArtistFollow.user
UserFollow.follower
```

The backend should derive this user from authentication.

Do not trust:

```json
{
    "user_id": 123
}
```

from the client when the API already knows the authenticated user.

Instead:

```python
request.user
```

determines who performed the action.

---

# 13. Engagement and Authentication

Most engagement actions require authentication.

Typical requirements:

| Action          | Authentication |
| --------------- | -------------- |
| Like            | Required       |
| Unlike          | Required       |
| Rate            | Required       |
| Favorite        | Required       |
| Unfavorite      | Required       |
| Follow user     | Required       |
| Unfollow user   | Required       |
| Follow artist   | Required       |
| Unfollow artist | Required       |
| Comment         | Required       |
| Reply           | Required       |
| Report          | Required       |

Public visitors may still be able to:

* read content
* view public ratings
* see like counts
* see follower counts
* see comments

depending on the endpoint and privacy rules.

---

# 14. Engagement and Permissions

A user should only control their own engagement.

For example:

```text
User A likes Post 1
```

User A can remove their own like.

User B should not be able to send a request that deletes User A's like.

Likewise:

```text
User A rates Song 1 = 4.5
```

User A can change or delete their own rating.

User B cannot modify User A's rating.

The API must enforce ownership.

---

# 15. Engagement and Admin

Engagement records are platform-generated user activity.

Therefore, the admin interface should primarily allow staff to:

* inspect engagement
* search engagement
* filter engagement
* moderate where necessary
* investigate abuse
* audit activity

rather than manually generating normal user engagement.

This is why some engagement models intentionally have no normal admin `+ Add` button.

For example:

```text
SongRating
AlbumRating
```

represent actual user ratings.

An administrator should not normally create a fake rating just because the admin panel makes it technically possible.

---

## Admin exceptions

Administrative tooling may eventually require special operational actions, such as:

* correcting corrupted data
* removing fraudulent engagement
* resolving abuse
* performing migrations
* repairing counters

These are maintenance operations, not ordinary engagement creation.

---

# 16. Engagement and API Design

The API should expose engagement in a way that is convenient for the frontend without exposing unnecessary database complexity.

For example, a song response could eventually contain:

```json
{
    "id": 42,
    "title": "Example Song",
    "rating": {
        "average": 4.4,
        "count": 182
    },
    "favorites_count": 91,
    "viewer": {
        "has_rated": true,
        "rating": 4.5,
        "is_favorite": true
    }
}
```

This separates:

```text
Global engagement
```

from:

```text
Current user's engagement
```

The same pattern can be used for posts and articles.

---

## Global state

Examples:

```text
likes_count
comments_count
views_count
average_rating
rating_count
followers_count
```

## Viewer-specific state

Examples:

```text
liked_by_me
favorited_by_me
followed_by_me
my_rating
```

This distinction is extremely useful for frontend development.

---

# 17. Engagement and Database Design

Engagement tables should remain normalized.

For example:

```text
CommunityPost
       │
       │ 1:N
       ▼
CommunityPostLike
```

rather than storing:

```text
CommunityPost.liked_users = [...]
```

inside the post.

Likewise:

```text
Song
 │
 └── SongRating
```

instead of storing a list of user ratings directly inside `Song`.

Relational tables provide:

* uniqueness constraints
* foreign keys
* indexing
* efficient filtering
* ownership queries
* moderation
* auditing

---

# 18. Performance and Scalability

Engagement can become one of the highest-write areas of the platform.

A popular song may receive:

```text
thousands of ratings
thousands of favorites
thousands of views
```

A viral community post may receive:

```text
thousands of likes
thousands of comments
```

The architecture should therefore optimize both reads and writes.

---

## Database indexes

Common query patterns should have appropriate indexes.

Examples:

```text
likes by user
likes by post
ratings by song
ratings by album
favorites by user
favorites by song
favorites by album
follows by follower
follows by followed user
artist follows by artist
```

Composite uniqueness constraints often provide useful indexes automatically.

---

## Pagination

Never load all engagement records for a popular object at once.

Use pagination for:

* comments
* replies
* ratings
* followers
* following
* user activity

---

# 19. Caching Strategy

Caching can eventually be introduced around high-read engagement data.

Potential cache targets:

```text
Song rating summary
Album rating summary
Popular artists
Trending posts
Popular articles
Follower counts
High-traffic comment threads
```

However, caching should not replace PostgreSQL.

A good architecture is:

```text
PostgreSQL
    ↓
Source of truth

Redis/cache
    ↓
Fast temporary representation

API
    ↓
Frontend
```

Cache invalidation should happen when the underlying engagement changes where appropriate.

---

# 20. Analytics

Engagement records provide the foundation for analytics.

The platform can derive metrics such as:

### Content engagement

```text
likes
comments
views
```

### Music popularity

```text
ratings
favorites
artist follows
community discussion volume
```

### User activity

```text
posts created
comments created
likes given
ratings submitted
artists followed
```

### Engagement rate

A future analytics layer could calculate:

```text
engagement rate =
(total meaningful engagements / views) × 100
```

The exact formula should be defined separately for each content type.

---

# 21. Notifications

Engagement can eventually trigger notifications.

Examples:

```text
Someone liked your post.
Someone replied to your comment.
Someone followed you.
Someone mentioned you.
Your post reached a milestone.
```

Artist following can also become the basis for future notifications such as:

```text
A followed artist has a new release.
A new article about a followed artist was published.
```

However, these notifications should be implemented as a separate notification system.

Engagement models should not become responsible for delivering notifications directly.

Conceptually:

```text
Engagement Event
       ↓
Event/Service Layer
       ↓
Notification
       ↓
User
```

---

# 22. Trending and Ranking

Engagement data can power VibeNation's future ranking systems.

Potential signals include:

```text
views
likes
comments
ratings
favorites
follows
recency
engagement velocity
```

For example:

```text
A post with 500 likes over 2 days
```

may be more interesting than:

```text
A post with 600 likes over 6 months
```

Therefore, future ranking systems should consider time rather than simply sorting by total engagement.

---

## Example conceptual score

A future trending algorithm might consider:

```text
score =
    recent_views
  + recent_likes
  + recent_comments
  + rating_activity
  + recency_weight
```

This is only an architectural example.

The exact ranking formula should be developed independently from the database models.

---

# 23. Future Engagement Features

The current architecture can support additional engagement features later.

## Reactions

Instead of only:

```text
Like
```

the platform could support:

```text
Like
Love
Fire
Laugh
```

If introduced, reactions should be modeled intentionally rather than forcing multiple unrelated boolean fields into content models.

---

## Shares

Future share tracking could record:

```text
User
Content
Platform
Timestamp
```

Possible platforms:

```text
WhatsApp
X
Facebook
Copy Link
```

Share counts could then be used as additional engagement signals.

---

## Bookmarks

Bookmarks could be introduced for editorial articles or community posts.

These should remain distinct from music favorites.

```text
Bookmark ≠ Favorite
```

---

## Saves

A broader save system could eventually allow users to save:

* articles
* posts
* songs
* albums

If introduced, it should be carefully separated from the existing music-specific favorite models unless there is a strong reason to consolidate them.

---

## Reposts and Quote Posts

Social sharing features can eventually build on `CommunityPost`.

They should not misuse:

```text
CommunityPostComment
```

as a substitute for a repost.

---

# 24. Developer Workflow

When implementing an engagement feature, follow these steps.

## Step 1 — Define the meaning

Ask:

```text
Is this a like?
A rating?
A favorite?
A follow?
A view?
A share?
A bookmark?
```

Do not create vague "engagement" records that attempt to represent everything.

---

## Step 2 — Identify the target

Determine what the user is interacting with:

```text
Song
Album
Artist
CommunityPost
CommunityPostComment
EditorialArticle
EditorialComment
User
```

---

## Step 3 — Determine whether the relationship is unique

Ask:

```text
Can one user perform this action more than once on the same target?
```

If not, enforce uniqueness at the database level.

---

## Step 4 — Identify the owner

Determine which authenticated user performed the action.

Use:

```python
request.user
```

rather than trusting a client-provided user ID.

---

## Step 5 — Update counters

If the target has a cached counter:

```text
create engagement
      ↓
atomic increment
```

and:

```text
delete engagement
      ↓
atomic decrement
```

---

## Step 6 — Handle race conditions

The API should be safe against:

* double clicks
* retries
* simultaneous requests
* duplicate submissions

Database constraints and atomic updates are critical here.

---

## Step 7 — Add tests

At minimum test:

```text
authenticated user can engage
anonymous user is rejected where required
duplicate engagement is rejected/prevented
user can remove own engagement
user cannot remove another user's engagement
counter increments correctly
counter decrements correctly
counter cannot become negative
rating validation works
self-follow is rejected
```

---

# 25. Golden Rules

### Rule 1 — Engagement records are the source of truth

```text
Like row
Rating row
Favorite row
Follow row
```

are authoritative.

Counters are cached values.

---

### Rule 2 — Do not store average ratings

Calculate averages from:

```text
SongRating
AlbumRating
```

rather than maintaining another permanent average field.

---

### Rule 3 — Enforce uniqueness in the database

Do not rely only on frontend or API checks.

---

### Rule 4 — Authentication determines the acting user

Use:

```python
request.user
```

for user-owned engagement.

---

### Rule 5 — Artist following does not create artist accounts

```text
Artist ≠ User
```

`ArtistFollow` connects a VibeNation user to a catalog artist.

---

### Rule 6 — Likes, favorites, ratings, and follows mean different things

Do not collapse them into one generic interaction system simply for convenience.

---

### Rule 7 — Counters are optimizations

If:

```text
likes_count = 500
```

but the actual like rows say:

```text
497
```

the rows are authoritative.

The counter can be repaired.

---

### Rule 8 — View counting belongs in the service/API layer

Retrieving a model object must not automatically mean:

```text
views_count += 1
```

---

### Rule 9 — Admins moderate engagement

They should not normally fabricate user activity.

---

### Rule 10 — Keep engagement separate from content

For example:

```text
CommunityPost
CommunityPostLike
```

is preferable to stuffing user IDs into the post itself.

---

### Rule 11 — Use atomic operations for counters

Concurrent engagement must not cause lost updates.

---

### Rule 12 — Keep the API frontend-friendly

Expose both:

```text
global engagement
```

and, where authenticated:

```text
current user's engagement
```

without forcing the frontend to reconstruct everything from raw database relationships.

---

### Rule 13 — Optimize only where necessary

Start with:

```text
PostgreSQL
indexes
constraints
pagination
atomic updates
```

Introduce Redis, queues, workers, or separate services when actual traffic justifies them.

---

# 26. Final Mental Model

The VibeNation Engagement System can be remembered as five questions:

```text
                         USER
                           │
        ┌──────────────────┼───────────────────┐
        │                  │                   │
        ▼                  ▼                   ▼
      CONTENT            MUSIC               PEOPLE
        │                  │                   │
        │                  │                   ├── UserFollow
        │                  │                   └── ArtistFollow
        │                  │
        │                  ├── SongRating
        │                  ├── AlbumRating
        │                  ├── SongFavorite
        │                  └── AlbumFavorite
        │
        ├── Like
        ├── Comment
        └── View
```

Or, more simply:

```text
LIKE
"What do I think of this?"

RATING
"How highly do I score this?"

FAVORITE
"Do I want to keep this in my collection?"

FOLLOW
"Do I want an ongoing relationship with this user/artist?"

VIEW
"Did I consume or look at this content?"
```

The database then represents those relationships explicitly:

```text
User
 │
 ├── CommunityPostLike ─────── CommunityPost
 │
 ├── EditorialArticleLike ─── EditorialArticle
 │
 ├── SongRating ────────────── Song
 │
 ├── AlbumRating ───────────── Album
 │
 ├── SongFavorite ──────────── Song
 │
 ├── AlbumFavorite ─────────── Album
 │
 ├── ArtistFollow ──────────── Artist
 │
 └── UserFollow ────────────── User
```

While views and cached counters sit on the content side:

```text
CommunityPost
├── likes_count
├── comments_count
└── views_count

CommunityPostComment
├── likes_count
├── replies_count
└── views_count

EditorialArticle
├── likes_count
├── comments_count
└── views_count

EditorialComment
├── likes_count
├── replies_count
└── views_count
```

The complete architectural principle is:

```text
USER ACTION
    ↓
ENGAGEMENT RECORD
    ↓
DATABASE CONSTRAINTS
    ↓
ATOMIC COUNTER UPDATE
    ↓
API RESPONSE
    ↓
FRONTEND EXPERIENCE
```

The engagement system should remain a **separate layer from the content itself**.

Music, editorial articles, community posts, artists, albums, and users are the entities.

Likes, ratings, favorites, follows, and views describe what users do with those entities.

That separation keeps VibeNation's data model clean, makes moderation easier, protects against duplicate activity, and gives the platform a strong foundation for feeds, notifications, analytics, recommendations, and future high-traffic scaling.
