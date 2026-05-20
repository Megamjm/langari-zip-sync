import streamlit as st
import os
from pathlib import Path
import hashlib
import shutil
from collections import defaultdict

def get_file_hash(file_path):
    """Compute SHA256 hash of file."""
    hash_sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha.update(chunk)
    return hash_sha.hexdigest()

def scan_folder(folder):
    """Scan folder for .zip files and their hashes."""
    zips = {}
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith('.zip'):
                path = os.path.join(root, file)
                try:
                    h = get_file_hash(path)
                    zips[h] = path
                except Exception as e:
                    st.warning(f'Error hashing {path}: {e}')
    return zips

st.set_page_config(page_title="Langari ZIP Sync", layout="wide")
st.title("🗜️ Langari ZIP Sync Tool")
st.markdown("**For western web comics torrent management**")

col1, col2 = st.columns(2)
with col1:
    source_dir = st.text_input('Source Folder (new downloads/torrents)', value=os.path.expanduser('~/Downloads'))
with col2:
    target_dir = st.text_input('Target Folder (comic library)', value=os.path.expanduser('~/Comics'))

op_col1, op_col2 = st.columns(2)
with op_col1:
    operation = st.radio('Sync Method', ['Hard Link (recommended for space)', 'Copy'])
with op_col2:
    dry_run = st.checkbox('Dry Run (preview only)', value=True)

if st.button('🔍 Scan & Sync', type='primary'):
    if not source_dir or not target_dir:
        st.error('Please provide both folders.')
    elif not os.path.isdir(source_dir) or not os.path.isdir(target_dir):
        st.error('One or both paths are not valid directories.')
    else:
        with st.spinner('Scanning source...'):
            source_zips = scan_folder(source_dir)
        with st.spinner('Scanning target...'):
            target_zips = scan_folder(target_dir)
        
        st.success(f'Found {len(source_zips)} unique ZIPs in source, {len(target_zips)} in target.')
        
        to_sync = []
        for h, src_path in source_zips.items():
            if h not in target_zips:
                to_sync.append((src_path, h))
        
        st.info(f'{len(to_sync)} new ZIPs to sync.')
        
        if to_sync:
            if dry_run:
                st.write('**Preview of actions:**')
                for src, _ in to_sync[:10]:
                    st.write(f'- {os.path.basename(src)}')
                if len(to_sync) > 10:
                    st.write(f'... and {len(to_sync)-10} more')
            else:
                progress = st.progress(0)
                for i, (src_path, h) in enumerate(to_sync):
                    rel_path = os.path.relpath(src_path, source_dir)
                    dest_path = os.path.join(target_dir, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    try:
                        if operation == 'Hard Link':
                            os.link(src_path, dest_path)
                            st.write(f'✅ Hard linked: {os.path.basename(src_path)}')
                        else:
                            shutil.copy2(src_path, dest_path)
                            st.write(f'✅ Copied: {os.path.basename(src_path)}')
                    except Exception as e:
                        st.error(f'Failed for {src_path}: {e}')
                    progress.progress((i+1)/len(to_sync))
                st.success('Sync complete!')