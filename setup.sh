pip install hachoir-metadata
pip install hachoir-core
pip install hachoir-parser

mkdir -p /usr/local/bin/TBFS/

cp tag /usr/local/bin/
chmod +x /usr/local/bin/tag

cp tagfs /usr/local/bin/
chmod +x /usr/local/bin/tagfs 

cp config.json /usr/local/bin/TBFS/
cp pythonInterface.py /usr/local/bin/TBFS/
cp fuse_start.py /usr/local/bin/TBFS/
