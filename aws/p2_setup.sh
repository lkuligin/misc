#!/bin/bash
set -e -u

sudo apt-get update
sudo apt-get --assume-yes upgrade
sudo apt-get --assume-yes install tmux build-essential gcc g++ make binutils
sudo apt-get --assume-yes install software-properties-common

mkdir downloads
cd downloads

#install cuda
wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_8.0.44-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1604_8.0.44-1_amd64.deb
sudo apt-get update
sudo apt-get -y install cuda
sudo modprobe nvidia
nvidia-smi

#install conda and launch ipython notebook
echo "installing dependecies"
CONDA_HOME=/mnt/conda
CONDA_BIN=${CONDA_HOME}/bin
echo export PATH="${CONDA_BIN}:\$PATH" >> ~/.bashrc
export PATH="$CONDA_BIN:$PATH"
mkdir ~/log
export NOTEBOOK_LOG=~/log/jupyter.log

wget https://repo.continuum.io/miniconda/Miniconda2-4.2.12-Linux-x86_64.sh
sudo bash Miniconda2-4.2.12-Linux-x86_64.sh -b -p ${CONDA_HOME}

req_path=/home/ubuntu/install/req.txt
sudo ${CONDA_BIN}/conda install --yes --file $req_path

mkdir /home/ubuntu/notebooks/
ln -s /mnt/notebooks /home/ubuntu/notebooks
mkdir /var/log/

JUPYTER_CONFIG=~/.jupyter/jupyter_notebook_config.py

if [ ! -e $JUPYTER_CONFIG ] ; then
    ${CONDA_BIN}/jupyter-notebook --generate-config
    echo 'c = get_config()
c.NotebookApp.ip = "*"
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8889
c.NotebookApp.notebook_dir = u"/home/ubuntu/notebooks"
c.NotebookApp.base_url = u"/jupyter"
' > $JUPYTER_CONFIG
else
    echo "profile already exists"
fi

sudo ${CONDA_BIN}/ipython kernel install

#theano config
echo "[global]
device = gpu
floatX = float32" > ~/.theanorc

sudo ${CONDA_BIN}/pip install keras
mkdir ~/.keras
echo '{
    "image_dim_ordering": "th",
    "epsilon": 1e-07,
    "floatx": "float32",
    "backend": "theano"
}' > ~/.keras/keras.json

${CONDA_BIN}/jupyter-notebook > $NOTEBOOK_LOG 2>&1 &
${CONDA_BIN}/jupyter-notebook list
