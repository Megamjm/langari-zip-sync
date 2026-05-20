import streamlit as st
import os
from pathlib import Path
import hashlib
import shutil

st.title('Langari ZIP Sync Tool')

st.write('''Web app for checking source folder for ZIPs, comparing to target, and syncing with hard links or copies. Designed for western web comic / torrent management.''')

source_dir = st.text_input('Source Folder (e.g. new torrents)', '/path/to/source')
target_dir = st.text_input('Target Folder (e.g. library)', '/path/to/target')

operation = st.radio('Operation', ['Hard Link', 'Copy'])

if st.button('Scan and Sync'):
    if not os.path.exists(source_dir) or not os.path.exists(target_dir):
        st.error('Invalid paths')
    else:
        st.info('Scanning...')
        # TODO: implement logic
        st.success('Done!')