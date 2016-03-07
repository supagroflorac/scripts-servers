#!/usr/bin/env python
#-*- coding: utf-8 -*-
# Need 'pip install Fabric'
"""Configuration des serveurs de SupAgro Florac"""

from __future__ import print_function, with_statement
from fabric.api import run, env, put, sudo, local
from fabric.contrib.files import sed

import yaml
import os

CONFIG = yaml.load(open('config.yml', 'r'))
env.hosts = CONFIG['hosts']

def install():
    '''Configuration complete'''
    # Copy la clé ssh
    # local('ssh-copy-id ' + env.host_string)
    update()
    install_ntp_client()
    install_vim()
    install_bash()
    install_ssmtp()
    install_logwatch()
    install_apticron()

def update():
    '''Mise a jour du système'''
    sudo('apt-get update')
    sudo('apt-get -y dist-upgrade')
    sudo('apt-get -y autoremove')

def install_software():
    '''Install les outils necessaires'''
    sudo('apt-get install -y vim-nox aptitude')

def install_ntp_client():
    '''Installation du service NTP comme client '''
    sudo('apt-get -y purge openntpd ntp ntpdate')
    sudo('apt-get -y install ntp')
    sudo_put('conf/ntp.conf', '/etc/ntp.conf')
    sudo('service ntp restart')

def install_vim():
    '''Installation et configuration de vim'''
    put('conf/vimrc', '~/.vimrc')
    run('mkdir -p ~/.vim/colors')
    put('conf/monokai.vim', '~/.vim/colors/monokai.vim')
    sudo_put('conf/vimrc', '/root/.vimrc')
    sudo('mkdir -p /root/.vim/colors')
    sudo_put('conf/monokai.vim', '/root/.vim/colors/monokai.vim')

def install_bash():
    '''Installation et configuration de bashrc'''
    put('conf/bashrc.user', '~/.bashrc')
    sudo_put('conf/bashrc.root', '~/.bashrc')

def install_software():
    '''Installation des outils de bases'''
    sudo('apt-get -y install vim tmux')

def install_ssmtp():
    '''Configure le systeme pour envoyer des mails'''
    # TODO : Ajouter une gestion des mots de passe.
    sudo('apt-get -y install ssmtp')
    sudo_put('conf/ssmtp.conf', '/etc/ssmtp/ssmtp.conf')
    sudo_put('conf/revaliases', '/etc/ssmtp/revaliases')
    sudo('chfn -f "no-reply" www-data')
    sed('/etc/ssmtp/ssmtp.conf', 'HOSTNAME', str(env.host), use_sudo=True, backup='')
    sed('/etc/ssmtp/revaliases', 'HOSTNAME', str(env.host), use_sudo=True, backup='')

def install_logwatch():
    '''Install et configure logwatch'''
    sudo('apt-get -y install logwatch')
    sudo_put('conf/logwatch.conf', '/usr/share/logwatch/default.conf/logwatch.conf')

def install_apticron():
    '''Install est configure apticron : envoi mail avec liste des mises a jour'''
    sudo('DEBIAN_FRONTEND="noninteractive" apt-get -y install apticron')
    sudo_put('conf/apticron.conf', '/etc/apticron/apticron.conf')

def ssh_copy_id():
    '''Copy la clé ssh publique sur les serveur distant.'''
    local('ssh-copy-id ' + env.host)

def ping():
    '''Ping les serveurs'''
    local('ping -c 3 ' + env.host)

##############################################################################
# toolbox

def sudo_put(src, dest):
    '''Copy des fichier accessible uniquement via root'''
    put(src, '/tmp/file_to_put')
    sudo('mv /tmp/file_to_put ' + dest)
