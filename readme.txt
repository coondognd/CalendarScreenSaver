) Install python and pip
) Install Dropbox downloader: https://github.com/andreafabrizi/Dropbox-Uploader

) Install libraries
python -m venv calendar
calendar/bin/pip install google-api-code google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib googleapis-common-protos

Every day:
) ~/Dropbox-Uploader/dropbox_uploader.sh download /Photos/Frame ~/Pictures/Dropbox/
) ~/Dropbox-Uploader/dropbox_uploader.sh download /Photos/Frame ~/Pictures/Dropbox/
) cp ~/Pictures/Dropbox/Frame/Kevin/* ./app_images/
) cp ~/Pictures/Dropbox/Frame/Amy/* ./app_images/
) calendar/bin/python ./get_calendar_events.py
) python ./metadata_builder.py
) python ./image_selector.py
) python ./create_calendar_images.py

TODO:
- Support subfolders so we don't have to treat the Kevin and Amy folders separately