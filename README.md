# zamboni

Download a comprehensive set of NHL game, player, and team data and load into a SQL database. Export in format for analysis or training of ML models.

## Installation

First setup up your environment as you prefer. Then:

` pip install . `

## Database Setup

` python scripts/setup_db.py `

## Download from NHL API

` python scripts/download_all.py `

## Load into SQL database

` python scripts/load_to_sql.py `
