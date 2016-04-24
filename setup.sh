if [ $# -eq 0 ]; then
    setupPath="/home/aniket/bin"
else
    setupPath=$1
fi

pip install hachoir-metadata
pip install hachoir-core
pip install hachoir-parser
pip install docx2txt
sudo -H pip install nltk

export PATH="/opt/local/bin:/opt/local/sbin:$PATH"
# Finished adapting your PATH environment variable for use with MacPorts.
python createConfig.py ${setupPath}

mkdir -p ${setupPath}/TBFS/

cp tag ${setupPath}/
chmod +x ${setupPath}/tag

cp tagfs ${setupPath}/
chmod +x ${setupPath}/tagfs

cp tagr ${setupPath}/
chmod +x ${setupPath}/tagr

cp getfiles ${setupPath}/
chmod +x ${setupPath}/getfiles 

cp lstag ${setupPath}/
chmod +x ${setupPath}/lstag 

cp tagrel ${setupPath}/
chmod +x ${setupPath}/tagrel

cp config.json ${setupPath}/TBFS/
cp pythonInterface.py ${setupPath}/TBFS/
cp fuse_start.py ${setupPath}/TBFS/
cp results.py ${setupPath}/TBFS/
cp database.py ${setupPath}/TBFS/
cp graph.py ${setupPath}/TBFS/
