) Install python and pip
) Install Dropbox downloader: https://github.com/andreafabrizi/Dropbox-Uploader

) Install libraries
python -m venv calendar
calendar/bin/pip install google-api-code google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib googleapis-common-protos

Every day:
0 0 * * * ~/Dropbox-Uploader/dropbox_uploader.sh download /Photos/Frame ~/Pictures/Dropbox/
10 0 * * * cp -n ~/Pictures/Dropbox/Frame/Kevin/* ~/CalendarScreenSaver/all_images/
10 0 * * * cp -n ~/Pictures/Dropbox/Frame/Amy/* ~/CalendarScreenSaver/all_images/
15 0 * * * cd ~/CalendarScreenSaver && . ./.env && ./calendar/bin/python ./get_calendar_events.py
16 0 * * * cd ~/CalendarScreenSaver && . ./.env && ./calendar/bin/python ./metadata_builder.py
17 0 * * * cd ~/CalendarScreenSaver && . ./.env && ./calendar/bin/python ./image_selector.py
18 0,3 * * * cd ~/CalendarScreenSaver && . ./.env && ./calendar/bin/python ./create_calendar_images.py


TODO:
- Support subfolders so we don't have to treat the Kevin and Amy folders separately