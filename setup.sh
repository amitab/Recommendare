#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALLED_MONGO=false
INSTALLED_PIP=false
INSTALLED_PYMONGO=false
INSTALLED_PYPRIND=false

ARCHITECTURE=`getconf LONG_BIT`
DISTRO=`grep -ihs "buntu\|SUSE\|Fedora\|PCLinuxOS\|MEPIS\|Mandriva\|Debian\|Damn\|Sabayon\|Slackware\|KNOPPIX\|Gentoo\|Zenwalk\|Mint\|Kubuntu\|FreeBSD\|Puppy\|Freespire\|Vector\|Dreamlinux\|CentOS\|Arch\|Xandros\|Elive\|SLAX\|Red\|BSD\|KANOTIX\|Nexenta\|Foresight\|GeeXboX\|Frugalware\|64\|SystemRescue\|Novell\|Solaris\|BackTrack\|KateOS\|Pardus" /etc/{issue,*release,*version}` 

function remove_if_exists {
    cd "$DIR/data"
    sudo rm -rf ml-100k
    sudo rm -rf *.json
    cd "$1"
}

function remove_downloaded_files {
    cd "$DIR/data"
    sudo rm -rf ml*
    sudo rm -rf *.json
    cd "$DIR"
}

function remove_apps {
    
    if $INSTALLED_MONGO; then
        sudo apt-get remove mongodb* --purge
    fi
    
    if $INSTALLED_PYMONGO; then
        sudo pip uninstall pymongo
    fi
    
    if $INSTALLED_PYPRIND; then
        sudo pip uninstall pyprind
    fi
    
    if $INSTALLED_PIP; then    
        sudo apt-get purge python-pip
    fi
}

function error_exit {
    remove_downloaded_files
    remove_apps
    
    exit 1
}

trap error_exit SIGINT

{
    cd "$DIR/data"

    if [ ! -f ml-100k.zip ]; then
        wget "http://files.grouplens.org/datasets/movielens/ml-100k.zip";
    fi

    remove_if_exists "$DIR/data"

    unzip "ml-100k.zip"

    python extractor.py ml-100k

    if dpkg -s mongodb-org > /dev/null;
    then
        echo "MongoDB found"
    else
        read -p "MongoDB not found. Install?" yn
        case $yn in
            [Yy]* )
                INSTALLED_MONGO=true
                sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10;
                echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list;
                sudo apt-get update;
                sudo apt-get install -y mongodb-org;;
            [Nn]* ) exit;;
            * ) echo "Please answer y or n.";;
        esac
    fi

    if dpkg -s python-pip > /dev/null;
    then
        echo "python-pip found"
    else
        read -p "python-pip not found. Install?" yn
        case $yn in
            [Yy]* )
                INSTALLED_PIP=true
                sudo apt-get install python-pip;;
            [Nn]* ) exit;;
            * ) echo "Please answer y or n.";;
        esac
    fi

    if python -c 'import pymongo' 2>/dev/null; then
        echo "Found pymongo"
    else
        read -p "pymongo not found. Install?" yn
        case $yn in
            [Yy]* )
                INSTALLED_PYMONGO=true
                sudo pip install pymongo;;
            [Nn]* ) exit;;
            * ) echo "Please answer y or n.";;
        esac
    fi

    if python -c 'import pyprind' 2>/dev/null; then
        echo "Found pyprind"
    else
        read -p "pyprind not found. Install?" yn
        case $yn in
            [Yy]* )
                INSTALLED_PYPRIND=true
                sudo pip install pyprind;;
            [Nn]* ) exit;;
            * ) echo "Please answer y or n.";;
        esac
    fi

    sudo mongoimport --db hypertarget_ads --collection users --type json --file users.json --jsonArray
    sudo mongoimport --db hypertarget_ads --collection movies --type json --file movies.json --jsonArray
    sudo mongoimport --db hypertarget_ads --collection meta --type json --file meta.json --jsonArray

    echo "Precomputing Data ..."

    cd "$DIR"
    python precompute.py

    cd "$DIR/data"

    sudo mongoimport --db hypertarget_ads --collection deviations --type json --file deviation.json --jsonArray
    sudo mongoimport --db hypertarget_ads --collection user_similarity --type json --file user_similarity.json --jsonArray

    cd "$DIR"

    echo "Install Completed"
    
} || {
    
    error_exit
    
}