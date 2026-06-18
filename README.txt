GymTracker
==========

A simple personal gym workout tracker built for my own use.
Written with Claude Code (claude.ai/code) to track my workouts.
Not feature-rich — just what I personally needed.


WHAT IT DOES
------------
- Track workouts by category (Chest, Shoulders, Arms, Core & Back, Legs, Cardio, Calisthenics)
- Log weight, reps and sets for strength exercises
- Log distance, duration and auto-calculates speed for cardio exercises
- See your last entry when you open an exercise so you know where you left off
- Analytics page with weekly volume chart and weight progress chart
- Works offline — logs sync when you're back online
- 11 visual themes to pick from
- Upload a banner image and set a motivation quote on the home page
- Export and import your settings and workout logs as CSV (for backup)
- Reset everything back to defaults if needed


SETUP
-----

Requirements: Python 3.11+

1. Create a virtual environment and install dependencies:

   python -m venv .venv
   .venv\Scripts\python.exe -m pip install django pillow

2. Set up the database:

   .venv\Scripts\python.exe manage.py migrate

3. Run the app:

   .venv\Scripts\python.exe manage.py runserver

4. Open your browser and go to:

   http://127.0.0.1:8000


That's it. No accounts, no login, single user only.


NOTES
-----
- All data is stored locally in db.sqlite3
- Uploaded images (banner, category photos) are stored in the media/ folder
- To back up your data: export CSV from Settings > Data / Backup
- To start fresh: Settings > Reset / Danger Zone > Reset to Default Settings
