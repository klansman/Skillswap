# Skillswap

🔥 Project Idea: “SkillSwap” – A Peer-to-Peer Skill Trading Platform
Concept:
A platform where users can offer a skill (e.g. guitar lessons, coding help, graphic design) and request a skill in return — no money involved, just fair trades.

Core Features (API-Heavy):

1. User System
   Register/Login with JWT

Profile with skill tags, location (optional), and availability

2. Skill Listings
   Users create skills they can offer and describe them

CRUD via APIs

Search/filter by category or keywords

3. Trade Requests
   User A sends a trade request to User B

B can accept, reject, or propose a counter-offer

Real-time status updates

4. Messaging (Bonus with Channels or API-only)
   lightweight messaging system between users once matched

5. Rating System
   After a trade, users can rate each other and leave feedback

Helps build trust and credibility

6. Admin Panel
   Admin moderation of flagged content

View overall system analytics

Tech Stack
Backend: Django + Django REST Framework (JWT auth, viewsets, permissions, etc.)

Frontend: — React or simple HTML templates, or just Postman testing

Database: SQLite

Deployment: Render, Heroku, or Railway

'''
Enhancement features:

1.  ✅ Next Feature: Swap History & Threads
    🔍 Goal:
    Allow users to view:

    All related swaps and counter offers

    Which was accepted/rejected

    What skill was offered and countered

    🧩 Implementation Plan:
    Threaded View

    Create an endpoint that returns a list of:

    The original swap request

    Any counter offers referencing it

    Their statuses and timestamps

    Model Updates — Already done (counter_to relationship).

    New API View

    GET /api/swaps/{id}/thread/ — return the original + all related counter offers.

    Optional Enhancements

    Allow filtering swaps by status (accepted, pending, etc.)

    Add flags like "is_counter_offer": true

'''
