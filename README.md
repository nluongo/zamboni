# zamboni

![Logo](zamboni_logo.png)
*<p style="text-align: center;">This AI-generated (DALL-E) image of a zamboni is obviously inacurrate, reminding us to pursue our objective cautiously.</p>*

Download a comprehensive set of NHL game, player, and team data and load into a SQL database. Export in format for analysis and training of ML models.

## Installation

First setup up your environment as you prefer. Then:

` pip install . `

## Run

` python -m zamboni `

The program will proceed in several steps:

#### Download from NHL API

You may first wish to get some familiarity with the API's functionality. The notebook APIWalkthrough.ipynb gives various examples of API calls used by this package.

` jupyter lab notebooks/APIWalkthrough.ipynb `

Relevant data is placed into text files in CSV format. Games are placed into a file containing all historical games and another for the current day's games. Team information is placed into a separate file.

#### Load into SQL database

The data will be loaded from the text files into a SQLite database, which will contain several tables including game and team tables. Several views will be created which will facilitate the preparation of data for export. Status tables will hold the last successful dates of various program functions for failure tolerance and efficient incremental updating.

After data is loaded into the DB, it can be explored using the notebook DataExploration.ipynb.

` jupyter lab notebooks/DataExploration.ipynb `

#### Export to ML-friendly format

Game data is formatted for input to ML training and exported to parquet files. Separate files are again created for games before the current day and games on the current day.

#### Training

The ML model is trained from scratch if running for the first time, or incrementally if an existing model is found. Training is performed over games after the last training date stored in the DB and before the current day. After a successful training, the last training date is set to today.

#### Reporting

After the model is updated to have been trained on all days before the current date, the model is evaluated on today's games. It is assumed that this is done before any outcomes for today's games are known. A log file is created with the predictions for each of today's games.
